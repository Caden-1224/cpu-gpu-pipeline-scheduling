# Adaptive scoring prototype

`simulation/adaptive_scheduler.py` is a **design prototype** for a richer CPU
dispatch rule than the three policies in `run_experiment.py`. It is unit-tested,
self-contained, and **deliberately not wired into the main study**: every number
in `results/` comes from `run_experiment.py` alone.

> **Provenance.** The accompanying manuscript specifies the two-mode rule of equation
> (4), which switches on `q(t) > q0`. The scoring policy below is an **extension
> developed for this repository**, and its numbers stay outside `results/`.

The prototype answers one question: *if the scheduler could read several signals
(GPU in-flight depth, its own target depth, per-task waiting time, task class), how
would it combine them without starving any class?*

## 1. Signals and symbols

| symbol | meaning |
|---|---|
| `TaskType` | `PREPROCESS`, `SUBMIT`, `POSTPROCESS`, `BACKGROUND` |
| `ReadyTask` | `(task_type, ready_time_ms, ready_order)` — `ready_order` breaks ties |
| `gpu_pending` | observed GPU pending depth (same definition as the model: queue + in service) |
| `target_gpu_pending` | desired in-flight depth, adapted online |
| `gpu_service_ema_ms` | exponential moving average of measured GPU service time |
| `weights` | `(gpu, wait, stage, age)` |
| `limits` | `(min_target_pending, max_target_pending, starvation_limit_ms)` |

## 2. Target-depth adaptation

```
update_target_pending(ema, reference_gpu_ms, previous, limits):
    if ema is None or ema <= 0:  return clamp(previous, min, max)
    return clamp(round(reference_gpu_ms / ema), min, max)
```

`update_ema(previous, observation, alpha)` is the usual `alpha * x + (1 - alpha) * p`
form with `alpha in (0, 1]` and the first observation seeded directly.

Reading: the target in-flight depth is the ratio of a *reference* GPU service time
to the *measured* one. If the GPU becomes slower than the reference the target
shrinks, and the scheduler stops queueing ahead; if it becomes faster, the target
grows up to `max_target_pending`. Both bounds are enforced on every update, and an
absent measurement preserves the previous target rather than guessing.

## 3. Scoring function

```
waiting_ms  = max(0, now_ms - task.ready_time_ms)
wait_score  = clamp(waiting_ms / starvation_limit_ms, 0, 1)

SUBMIT:      gpu_urgency = clamp((target - pending) / target, 0, 1)   stage = 1.0
PREPROCESS:  gpu_urgency = clamp((pending - target) / target, 0, 1)   stage = 0.8
POSTPROCESS: gpu_urgency = 0                                          stage = 0.6
BACKGROUND:  gpu_urgency = 0                                          stage = 0.2

age_bonus   = 1 if waiting_ms >= starvation_limit_ms else 0

score = w_gpu * gpu_urgency
      + w_wait * wait_score
      + w_stage * stage
      + w_age  * age_bonus
```

`select_adaptive_task` returns the maximum-score task and breaks ties by
`-ready_order`, i.e. the earliest-ready task wins a tie — the same tie-break the
main model uses.

### Why two opposite GPU terms
`SUBMIT` is urgent when the GPU is **underfilled** (`target - pending > 0`);
`PREPROCESS` is urgent when the GPU is **overfilled** (`pending - target > 0`). The
two terms are never both positive for the same `pending`, so the policy always has
a clear direction; this is the continuous generalisation of the binary
`gpu_feedback` rule, where the switch is the single comparison `q(t) <= q0`.

### Anti-starvation
`wait_score` grows linearly to 1 at the starvation limit, and `age_bonus` adds a
step on top. With `age` weighted 3.0 in the unit tests, an aged `BACKGROUND` task
outranks a fresh `SUBMIT` — verified by
`test_adaptive_scheduler.AdaptiveSchedulerTests.test_aged_background_task_is_not_starved`.

## 4. Parameters

The module defines no default weights; every caller passes `SchedulerWeights` and
`SchedulerLimits` explicitly. The unit tests use

```
SchedulerLimits(min_target_pending=1, max_target_pending=4, starvation_limit_ms=10.0)
SchedulerWeights(gpu=2.0, wait=0.4, stage=0.2, age=3.0)
```

These values exercise the code paths, and calibration is left to the caller.
Validation rejects `min_target_pending < 1`,
`max_target_pending < min_target_pending`, `reference_gpu_ms <= 0`, `alpha` outside
`(0, 1]`, non-positive observations, negative `gpu_pending`, `target_gpu_pending < 1`
and an empty ready list.

## 5. Calibration path

1. **Parameter provenance** records where each weight comes from, whether measurement,
   search or a stated heuristic, and travels with the policy.
2. **Ablation** removes `gpu`, `wait`, `stage` and `age` one at a time, so each term can
   be shown to earn its place.
3. **Head-to-head** runs the prototype against `gpu_feedback` on the *same paired seeds*,
   which leaves the dispatch rule as the only difference.
4. **Adaptation dynamics** record `target_gpu_pending` over time and show how the EMA
   settles after a workload switch.
5. **Sensitivity** sweeps `alpha`, `starvation_limit_ms` and the weight vector, and
   reports the plateau rather than a single point.
6. **A starvation bound** asserts `BACKGROUND` completion inside a bounded window, which
   backs the aging term with a test.

## 6. Scope

The module is a pure-Python scoring function over a ready list, and it runs inside the
simulation rather than inside the kernel. It covers preemption-free dispatch, while CPU
migration, NUMA placement and per-core load sit outside it. The unit tests confirm that
the function returns what this document specifies; latency, throughput and fairness are
measured in the main model.
