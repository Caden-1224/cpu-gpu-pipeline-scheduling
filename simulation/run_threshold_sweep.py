"""Run a reproducible GPU-pending-threshold sensitivity study."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import statistics

if __package__:
    from .run_experiment import PROFILES, WORKLOADS, simulate
else:
    from run_experiment import PROFILES, WORKLOADS, simulate


METRICS = (
    "throughput_req_per_ms",
    "mean_latency_ms",
    "p50_latency_ms",
    "p95_latency_ms",
    "p99_latency_ms",
    "gpu_busy_ratio",
    "gpu_idle_ms",
)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize(
    run_rows: list[dict[str, object]], thresholds: list[int]
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for workload in WORKLOADS:
        profile = PROFILES[workload]
        cpu_stage_demand = (
            profile.preprocess_ms + profile.submit_ms + profile.postprocess_ms
        )
        for threshold in thresholds:
            group = [
                row
                for row in run_rows
                if row["workload"] == workload
                and row["gpu_pending_threshold"] == threshold
            ]
            result: dict[str, object] = {
                "workload": workload,
                "gpu_pending_threshold": threshold,
                "repetitions": len(group),
                "nominal_gpu_backlog_ms": threshold * profile.gpu_ms,
                "gpu_backlog_to_cpu_stage_demand": (
                    threshold * profile.gpu_ms / cpu_stage_demand
                ),
            }
            for metric in METRICS:
                values = [float(row[metric]) for row in group]
                result[f"{metric}_mean"] = statistics.fmean(values)
                result[f"{metric}_std"] = statistics.stdev(values)
            rows.append(result)
    return rows


def write_report(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# GPU Pending Threshold Sensitivity Study",
        "",
        "This report contains seed-controlled discrete-event results, not hardware measurements.",
        "The nominal GPU backlog is q0 times the workload's nominal GPU service time.",
        "The normalized ratio divides that backlog by nominal preprocessing, submission, and postprocessing demand.",
        "",
        "| Workload | q0 | Normalized backlog | Throughput (req/ms) | Mean (ms) | P95 (ms) | P99 (ms) | GPU idle (ms) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {workload} | {gpu_pending_threshold} | "
            "{gpu_backlog_to_cpu_stage_demand:.4f} | "
            "{throughput_req_per_ms_mean:.4f} | {mean_latency_ms_mean:.4f} | "
            "{p95_latency_ms_mean:.4f} | {p99_latency_ms_mean:.4f} | "
            "{gpu_idle_ms_mean:.4f} |".format(**row)
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=30)
    parser.add_argument("--thresholds", type=int, nargs="+", default=[0, 1, 2, 4])
    parser.add_argument(
        "--output", type=Path, default=Path("results") / "threshold_sweep"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="write into an existing output directory instead of refusing to overwrite it",
    )
    args = parser.parse_args()
    if args.repetitions < 2:
        raise SystemExit("repetitions must be at least 2")
    thresholds = sorted(set(args.thresholds))
    if not thresholds or thresholds[0] < 0:
        raise SystemExit("thresholds must be non-negative integers")
    # The default refuses to clobber an existing study so a result directory that
    # is already cited by a paper cannot be overwritten by accident.
    if args.output.exists() and not args.force:
        raise SystemExit(
            f"output directory {args.output} already exists; "
            "pass --force to overwrite it"
        )
    args.output.mkdir(parents=True, exist_ok=True)

    run_rows: list[dict[str, object]] = []
    for workload_index, workload in enumerate(WORKLOADS):
        for threshold in thresholds:
            for repetition in range(args.repetitions):
                seed = 1000 + repetition + workload_index * 10000
                _, summary = simulate(
                    workload,
                    "gpu_feedback",
                    seed,
                    gpu_pending_threshold=threshold,
                )
                run_rows.append(
                    {
                        "workload": workload,
                        "gpu_pending_threshold": threshold,
                        "seed": seed,
                        **summary,
                    }
                )

    summary_rows = summarize(run_rows, thresholds)
    write_csv(args.output / "run_metrics.csv", run_rows)
    write_csv(args.output / "summary_metrics.csv", summary_rows)
    configuration = {
        "model": "non-preemptive discrete-event CPU-GPU pipeline",
        "measurement_scope": "numerical model only; no physical hardware measurement",
        "time_unit": "model milliseconds",
        "policy": "gpu_feedback",
        "thresholds": thresholds,
        "repetitions": args.repetitions,
        "seeds": {
            workload: [
                1000 + index * 10000,
                999 + args.repetitions + index * 10000,
            ]
            for index, workload in enumerate(WORKLOADS)
        },
        "profiles": {name: profile.__dict__ for name, profile in PROFILES.items()},
    }
    (args.output / "configuration.json").write_text(
        json.dumps(configuration, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(args.output / "report.md", summary_rows)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "runs": len(run_rows),
                "summary_rows": len(summary_rows),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
