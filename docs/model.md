# Model specification

This document is the normative description of the model implemented in
`simulation/run_experiment.py`. The code and this document are meant to be read
together; where they disagree, the code wins and the document is a bug.

## 1. Scope

The model is a **non-preemptive discrete-event simulation** of a four-stage
pipeline. All times are *model* milliseconds, and this document describes a
numerical simulation rather than a measurement of hardware, a driver, a kernel
scheduler or a CUDA runtime.

## 2. State

| symbol | meaning |
|---|---|
| `events` | min-heap of `(time, insertion_order, type, payload)` |
| `ready` | CPU-ready tasks, each with `(request_id, kind, duration_ms, ready_order)` |
| `cpu_free` | number of idle CPU cores (initialised to `profile.cpu_cores`) |
| `gpu_running` | whether the single GPU server is occupied |
| `gpu_queue` | FIFO of submitted request ids waiting for the GPU |
| `gpu_busy_ms` | accumulated GPU service time |
| `starts`, `completed` | per-request arrival and completion timestamps |

Event types: `arrival`, `background`, `cpu_done`, `gpu_done`.

## 3. Randomness

### 3.1 Stage durations

Every stage duration is drawn from a bounded log-normal distribution:

```
sample(mean) = clamp(lognormalvariate(log(mean), 0.28), 0.20 * mean, 3.00 * mean)
```

For request stages the generator is seeded *deterministically per stage*:

```
request_duration(seed, request_id, stage) =
    sample(profile.stage_ms) using random.Random(f"{seed}:{request_id}:{stage}")
```

This is the mechanism that makes policy comparisons **paired**: the same request
has the same preprocessing, submission and GPU service duration under every
policy, so a difference in the output can only come from the dispatch rule.
Background tasks draw from the single experiment RNG instead, because they carry
no request identity and are shared across policies through that same RNG sequence.

### 3.2 Arrivals

Interarrival times are exponential with mean `profile.interarrival_ms`; the arrival
times are generated once per `(workload, seed)` by `make_arrivals` and reused by
every policy. When `profile.burst_size > 1`, arrivals are grouped: the generator
advances the clock by one exponential gap and then emits `burst_size` requests
spaced `burst_gap_ms` apart.

### 3.3 Background load

When `background_rate > 0`, background tasks arrive as a Poisson process with the
given rate, up to `last_arrival + 25 ms`. They occupy CPU cores and never touch
the GPU. They exist to create CPU contention.

### 3.4 Seeds

Repetition `r` of workload index `w` uses `seed = 1000 + r + 10000 * w`, so the
30 seeds of a workload are 1000-1029 and each workload uses a disjoint seed block.

## 4. Event loop

```
while events or ready or gpu_queue or gpu_running:
    t = time of the earliest event
    batch = pop every event with timestamp t
    for each event in batch: apply its state transition
    if gpu idle and gpu_queue non-empty: dispatch head of gpu_queue to the GPU
    while cpu_free > 0 and ready non-empty:
        task = choose_task(ready, policy, gpu_pending = len(gpu_queue) + int(gpu_running))
        dispatch task onto a core, schedule its cpu_done at t + task.duration
```

Two details carry the fairness argument:

* **Simultaneous events are batched.** Every transition at timestamp `t` happens
  before the first scheduling decision at `t`, so the insertion order of the heap
  cannot change the outcome.
* **`gpu_pending` includes the request in service.** `q(t) = len(gpu_queue) + int(gpu_running)`.
  A policy that reads `q(t)` therefore sees the GPU as busy while it is actually
  serving, which is what makes `q0 = 0` a meaningful (too impatient) setting.

## 5. Policies

`choose_task` returns the ready task with the lowest `(priority, ready_order)` tuple:

| policy | priority map |
|---|---|
| `fifo` | no priority; strictly `ready_order` |
| `static_submit` | `submit:0, preprocess:1, postprocess:2, background:3` |
| `gpu_feedback` | if `q(t) <= q0`: `submit:0, preprocess:1, postprocess:2, background:3`; else `preprocess:0, postprocess:1, submit:2, background:3` |

The default threshold is `q0 = 1`; `q0 = 0` means the policy keeps submitting
unless the GPU is already occupied (including the running request).

The intended reading of `gpu_feedback` is: *keep the GPU fed when it is starving,
prepare the next wave when it is not.* Because the CPU stages are non-preemptive,
the policy can only reorder work that has not started yet; it cannot preempt a
running stage.

Two properties follow from the policy definitions and are shared by the code:

* The threshold changes **task order, not admission**, and the model places no bound on
  queue occupancy or on waiting inside a priority class.
* Both priority policies place background work last, so a comparison against FIFO
  carries the effect of **request prioritisation over background work**, and background
  response time is tracked apart from the request metrics.

## 6. Metrics

For request `i` let `a_i` be its arrival time and `c_i` its completion time
(after postprocessing). Latency is `L_i = c_i - a_i`.

| metric | definition |
|---|---|
| `throughput_req_per_ms` | `n / (max_i c_i - min_i a_i)` — a finite-batch completion span |
| `mean_latency_ms` | `fmean(L)` |
| `p50/p95/p99_latency_ms` | linear interpolation at position `(n - 1) * p / 100` |
| `gpu_busy_ratio` | `gpu_busy_ms / makespan` |
| `gpu_idle_ms` | `max(0, makespan - gpu_busy_ms)` |
| `mean_gpu_service_ms` | `gpu_busy_ms / n` |
| `cpu_dispatch_count` | number of CPU dispatches (a fairness cross-check: it should not depend on policy) |
| `makespan_ms` | `max_i c_i - min_i a_i` |

Percentiles use **interpolation**, not nearest-rank: for `n = 1000` requests and
`p = 99` the position is `(999) * 0.99 = 989.01`, i.e. the result interpolates
between the 989th and 990th ordered samples.

Aggregation is `mean_r(Q99(L_r))`: quantiles are computed inside each repetition
and then averaged across the 30 repetitions. Quantiles are **not** pooled across
repetitions, which would understate the run-to-run spread.

## 7. Workload profiles

See `results/configuration.json` for the frozen parameter set of the checked-in
results; the table in `README.md` is a transcription of it.

## 8. Abstraction level

The model spans the four pipeline stages, two non-preemptive CPU cores, one FIFO GPU
server and the background CPU load, with stage durations drawn from bounded log-normal
distributions that carry a fixed mean per profile. Batching, CUDA graphs, kernel launch
overhead, memory and PCIe bandwidth, multi-GPU and multi-tenant behaviour, CPU
frequency scaling, cache effects and NUMA placement sit outside that abstraction, so
the numbers describe how the three policies behave under the parameters listed above.
