"""CPU-GPU pipeline scheduling discrete-event model.

All times are model milliseconds and all pseudo-randomness is seed-controlled.
The model supports numerical policy comparisons; it is not evidence of a
deployed Linux scheduler or physical GPU measurement.
"""

from __future__ import annotations

import argparse
import csv
import heapq
import json
import math
import random
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path


POLICIES = ("fifo", "static_submit", "gpu_feedback")
WORKLOADS = ("steady", "cpu_contention", "gpu_saturated", "bursty")


@dataclass(frozen=True)
class Profile:
    request_count: int
    cpu_cores: int
    interarrival_ms: float
    preprocess_ms: float
    submit_ms: float
    gpu_ms: float
    postprocess_ms: float
    background_rate: float
    background_ms: float
    burst_size: int = 1
    burst_gap_ms: float = 0.0


PROFILES = {
    "steady": Profile(1000, 2, 0.55, 0.55, 0.06, 0.75, 0.15, 0.00, 0.0),
    "cpu_contention": Profile(1000, 2, 0.52, 0.62, 0.06, 0.52, 0.16, 1.65, 0.55),
    "gpu_saturated": Profile(1000, 2, 0.42, 0.30, 0.05, 1.35, 0.10, 0.20, 0.25),
    "bursty": Profile(1000, 2, 2.30, 0.52, 0.06, 0.65, 0.16, 0.80, 0.40, 10, 0.025),
}


@dataclass
class Task:
    request_id: int | None
    kind: str
    duration_ms: float
    ready_order: int


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * p / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def sample_duration(rng: random.Random, mean: float) -> float:
    # A bounded log-normal distribution adds repeatable task variability.
    return max(mean * 0.20, min(mean * 3.0, rng.lognormvariate(math.log(mean), 0.28)))


def request_duration(seed: int, request_id: int, kind: str, mean: float) -> float:
    """Keep a request-stage duration identical across policy comparisons."""
    return sample_duration(random.Random(f"{seed}:{request_id}:{kind}"), mean)


def make_arrivals(profile: Profile, rng: random.Random) -> list[float]:
    arrivals: list[float] = []
    now = 0.0
    while len(arrivals) < profile.request_count:
        if profile.burst_size > 1:
            now += rng.expovariate(1.0 / profile.interarrival_ms)
            for index in range(profile.burst_size):
                if len(arrivals) == profile.request_count:
                    break
                arrivals.append(now + index * profile.burst_gap_ms)
        else:
            now += rng.expovariate(1.0 / profile.interarrival_ms)
            arrivals.append(now)
    return arrivals


def choose_task(
    ready: list[Task],
    policy: str,
    gpu_pending: int,
    gpu_pending_threshold: int = 1,
) -> int:
    if policy == "fifo":
        return min(range(len(ready)), key=lambda index: ready[index].ready_order)

    if policy == "static_submit":
        priority = {"submit": 0, "preprocess": 1, "postprocess": 2, "background": 3}
    else:
        # GPU queue length is the only feedback signal in this model. When the
        # GPU is empty/near-empty, submit work prevents an idle bubble. When it
        # already has work, preprocessing prepares the next wave without growing
        # the GPU queue indefinitely.
        priority = (
            {"submit": 0, "preprocess": 1, "postprocess": 2, "background": 3}
            if gpu_pending <= gpu_pending_threshold
            else {"preprocess": 0, "postprocess": 1, "submit": 2, "background": 3}
        )
    return min(
        range(len(ready)),
        key=lambda index: (priority[ready[index].kind], ready[index].ready_order),
    )


def simulate(
    profile_name: str,
    policy: str,
    seed: int,
    gpu_pending_threshold: int = 1,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    if gpu_pending_threshold < 0:
        raise ValueError("gpu_pending_threshold must be non-negative")
    profile = PROFILES[profile_name]
    rng = random.Random(seed)
    events: list[tuple[float, int, str, object]] = []
    event_order = 0
    ready_order = 0
    ready: list[Task] = []
    cpu_free = profile.cpu_cores
    gpu_running = False
    gpu_queue: deque[int] = deque()
    gpu_busy_ms = 0.0
    cpu_dispatch_count = 0
    first_arrival = 0.0
    last_completion = 0.0
    starts: dict[int, float] = {}
    completed: dict[int, float] = {}
    arrival_times = make_arrivals(profile, rng)

    def push(when: float, event_type: str, payload: object) -> None:
        nonlocal event_order
        heapq.heappush(events, (when, event_order, event_type, payload))
        event_order += 1

    def add_ready(request_id: int | None, kind: str, mean_duration: float) -> None:
        nonlocal ready_order
        duration = (
            request_duration(seed, request_id, kind, mean_duration)
            if request_id is not None
            else sample_duration(rng, mean_duration)
        )
        ready.append(Task(request_id, kind, duration, ready_order))
        ready_order += 1

    for request_id, when in enumerate(arrival_times):
        push(when, "arrival", request_id)
    if profile.background_rate:
        background_time = rng.expovariate(profile.background_rate)
        horizon = arrival_times[-1] + 25.0
        while background_time < horizon:
            push(background_time, "background", None)
            background_time += rng.expovariate(profile.background_rate)

    now = 0.0
    while events or ready or gpu_queue or gpu_running:
        if events:
            now = events[0][0]
            batch: list[tuple[str, object]] = []
            while events and events[0][0] == now:
                _, _, event_type, payload = heapq.heappop(events)
                batch.append((event_type, payload))
            for event_type, payload in batch:
                if event_type == "arrival":
                    request_id = int(payload)
                    starts[request_id] = now
                    if request_id == 0:
                        first_arrival = now
                    add_ready(request_id, "preprocess", profile.preprocess_ms)
                elif event_type == "background":
                    add_ready(None, "background", profile.background_ms)
                elif event_type == "cpu_done":
                    cpu_free += 1
                    task = payload
                    assert isinstance(task, Task)
                    if task.kind == "preprocess":
                        add_ready(task.request_id, "submit", profile.submit_ms)
                    elif task.kind == "submit":
                        assert task.request_id is not None
                        gpu_queue.append(task.request_id)
                    elif task.kind == "postprocess":
                        assert task.request_id is not None
                        completed[task.request_id] = now
                        last_completion = max(last_completion, now)
                elif event_type == "gpu_done":
                    gpu_running = False
                    request_id = int(payload)
                    add_ready(request_id, "postprocess", profile.postprocess_ms)

        if not gpu_running and gpu_queue:
            request_id = gpu_queue.popleft()
            gpu_duration = request_duration(seed, request_id, "gpu", profile.gpu_ms)
            gpu_busy_ms += gpu_duration
            gpu_running = True
            push(now + gpu_duration, "gpu_done", request_id)

        while cpu_free and ready:
            index = choose_task(
                ready,
                policy,
                len(gpu_queue) + int(gpu_running),
                gpu_pending_threshold,
            )
            task = ready.pop(index)
            cpu_free -= 1
            cpu_dispatch_count += 1
            push(now + task.duration_ms, "cpu_done", task)

        # The loop always consumes a future event after all simultaneous state
        # transitions and scheduling decisions are complete.

    rows: list[dict[str, object]] = []
    latencies: list[float] = []
    for request_id in range(profile.request_count):
        latency = completed[request_id] - starts[request_id]
        latencies.append(latency)
        rows.append(
            {
                "workload": profile_name,
                "policy": policy,
                "seed": seed,
                "request_id": request_id,
                "arrival_ms": round(starts[request_id], 6),
                "completion_ms": round(completed[request_id], 6),
                "latency_ms": round(latency, 6),
            }
        )
    makespan = last_completion - first_arrival
    summary = {
        "workload": profile_name,
        "policy": policy,
        "seed": seed,
        "requests": profile.request_count,
        "throughput_req_per_ms": profile.request_count / makespan,
        "mean_latency_ms": statistics.fmean(latencies),
        "p50_latency_ms": percentile(latencies, 50),
        "p95_latency_ms": percentile(latencies, 95),
        "p99_latency_ms": percentile(latencies, 99),
        "gpu_busy_ratio": gpu_busy_ms / makespan,
        "gpu_idle_ms": max(0.0, makespan - gpu_busy_ms),
        "mean_gpu_service_ms": gpu_busy_ms / profile.request_count,
        "cpu_dispatch_count": cpu_dispatch_count,
        "makespan_ms": makespan,
    }
    return rows, summary


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def aggregate(run_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    metrics = (
        "throughput_req_per_ms", "mean_latency_ms", "p50_latency_ms",
        "p95_latency_ms", "p99_latency_ms", "gpu_busy_ratio", "gpu_idle_ms",
        "mean_gpu_service_ms", "cpu_dispatch_count", "makespan_ms",
    )
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in run_rows:
        groups[(str(row["workload"]), str(row["policy"]))].append(row)
    output: list[dict[str, object]] = []
    for workload, policy in sorted(groups):
        group = groups[(workload, policy)]
        row: dict[str, object] = {"workload": workload, "policy": policy, "repetitions": len(group)}
        for metric in metrics:
            values = [float(item[metric]) for item in group]
            row[f"{metric}_mean"] = statistics.fmean(values)
            row[f"{metric}_std"] = statistics.stdev(values) if len(values) > 1 else 0.0
        output.append(row)
    return output


def write_report(path: Path, summary_rows: list[dict[str, object]], repetitions: int) -> None:
    by_key = {(str(row["workload"]), str(row["policy"])): row for row in summary_rows}
    lines = [
        "# CPU-GPU 调度离散事件模型：结果报告",
        "",
        "## 证据边界",
        "",
        "本报告来自离散事件模型，时间单位为毫秒。它不测量 Linux `sched_ext`、eBPF 程序、GPU 驱动或真实硬件，因此不能用于声称实际部署性能。模型仅验证：在定义的流水线、资源和随机负载参数下，CPU 侧调度策略对端到端结果的影响。",
        "",
        "## 方法",
        "",
        "每个请求依次经过 CPU 预处理、CPU 提交、单 GPU 服务和 CPU 后处理。CPU 有两个非抢占式核心，GPU 为单服务台。比较 FIFO、静态提交优先和 GPU 队列反馈调度。后者在 GPU 队列长度不超过 1 时优先执行提交任务，其他时候优先准备后续任务。每个组合重复 %d 次，种子为 1000 至 %d。" % (repetitions, 999 + repetitions),
        "",
        "## 汇总结果",
        "",
        "| 负载 | 策略 | 吞吐 (req/ms) | P95 延迟 (ms) | P99 延迟 (ms) | GPU 忙碌比例 | GPU 空闲 (ms) |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| {workload} | {policy} | {throughput_req_per_ms_mean:.4f} | "
            "{p95_latency_ms_mean:.4f} | {p99_latency_ms_mean:.4f} | "
            "{gpu_busy_ratio_mean:.4f} | {gpu_idle_ms_mean:.4f} |".format(**row)
        )
    lines.extend(["", "## 受限结论", ""])
    for workload in WORKLOADS:
        fifo = by_key[(workload, "fifo")]
        feedback = by_key[(workload, "gpu_feedback")]
        static = by_key[(workload, "static_submit")]
        p99_delta = (float(feedback["p99_latency_ms_mean"]) / float(fifo["p99_latency_ms_mean"]) - 1.0) * 100
        throughput_delta = (float(feedback["throughput_req_per_ms_mean"]) / float(fifo["throughput_req_per_ms_mean"]) - 1.0) * 100
        static_p99_delta = (float(feedback["p99_latency_ms_mean"]) / float(static["p99_latency_ms_mean"]) - 1.0) * 100
        lines.append(
            "- `%s`：相对 FIFO，GPU 反馈策略的 P99 延迟变化 %.2f%%，吞吐变化 %.2f%%。"
            "相对静态提交优先，P99 延迟变化 %.2f%%。该观察仅适用于本模型参数。"
            % (workload, p99_delta, throughput_delta, static_p99_delta)
        )
    lines.extend([
        "",
        "## 复现",
        "",
        "运行 `python -m simulation.run_experiment --repetitions 30`。原始请求级数据见 `results/request_metrics.csv`，每次重复的指标见 `results/run_metrics.csv`，均值和标准差见 `results/summary_metrics.csv`。",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=30)
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    if args.repetitions < 2:
        raise SystemExit("repetitions must be at least 2")

    request_rows: list[dict[str, object]] = []
    run_rows: list[dict[str, object]] = []
    for workload_index, workload in enumerate(WORKLOADS):
        for policy_index, policy in enumerate(POLICIES):
            for repetition in range(args.repetitions):
                seed = 1000 + repetition
                # Use common random seeds within each workload repetition so
                # scheduling policy, rather than a changed input stream, is compared.
                rows, summary = simulate(workload, policy, seed + workload_index * 10000)
                request_rows.extend(rows)
                run_rows.append(summary)
    summary_rows = aggregate(run_rows)
    write_csv(args.output / "request_metrics.csv", request_rows)
    write_csv(args.output / "run_metrics.csv", run_rows)
    write_csv(args.output / "summary_metrics.csv", summary_rows)
    configuration = {
        "model": "non-preemptive discrete-event CPU-GPU pipeline",
        "time_unit": "milliseconds",
        "repetitions": args.repetitions,
        "request_duration_pairing": "fixed by seed, request id, and stage across policies",
        "policies": {
            "fifo": "ready-order FIFO",
            "static_submit": "submit > preprocess > postprocess > background",
            "gpu_feedback": "submit > preprocess when GPU pending <= 1; preprocess > postprocess > submit otherwise",
        },
        "profiles": {name: profile.__dict__ for name, profile in PROFILES.items()},
    }
    (args.output / "configuration.json").write_text(
        json.dumps(configuration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_report(args.output / "report.md", summary_rows, args.repetitions)


if __name__ == "__main__":
    main()
