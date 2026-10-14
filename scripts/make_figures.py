"""Render the figures embedded in README.md from the checked-in results CSV files.

Usage:
    python scripts/make_figures.py

Reads results/run_metrics.csv and results/threshold_sweep/summary_metrics.csv and
writes three PNG files into figures/. Requires matplotlib (the simulation itself
needs the standard library only).
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

POLICIES = ("fifo", "static_submit", "gpu_feedback")
LABELS = {
    "fifo": "FIFO",
    "static_submit": "static submit",
    "gpu_feedback": "GPU-queue feedback",
}
COLORS = {"fifo": "#8c8c8c", "static_submit": "#2f6fb5", "gpu_feedback": "#c1440e"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def group_p99(run_rows: list[dict[str, str]], workload: str) -> dict[str, list[float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in run_rows:
        if row["workload"] != workload:
            continue
        grouped[row["policy"]].append(float(row["p99_latency_ms"]))
    return grouped


def figure_contention_latency(run_rows: list[dict[str, str]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for axis, workload in zip(axes, ("cpu_contention", "bursty")):
        grouped = group_p99(run_rows, workload)
        data = [grouped[policy] for policy in POLICIES]
        box = axis.boxplot(data, tick_labels=[LABELS[p] for p in POLICIES], patch_artist=True, widths=0.55)
        for patch, policy in zip(box["boxes"], POLICIES):
            patch.set_facecolor(COLORS[policy])
            patch.set_alpha(0.35)
        for median in box["medians"]:
            median.set_color("black")
        axis.set_title("P99 latency per repetition - " + workload)
        axis.set_ylabel("P99 latency (model ms)")
        axis.grid(axis="y", alpha=0.3)
        axis.tick_params(axis="x", labelsize=9)
    fig.suptitle("Policy comparison over 30 seed-controlled repetitions", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig1_policy_p99_box.png", dpi=160)
    plt.close(fig)


def figure_gpu_utilisation(run_rows: list[dict[str, str]]) -> None:
    workloads = ["steady", "cpu_contention", "gpu_saturated", "bursty"]
    fig, axis = plt.subplots(figsize=(9, 4.2))
    width = 0.26
    positions = range(len(workloads))
    for offset, policy in enumerate(POLICIES):
        means, errors = [], []
        for workload in workloads:
            values = [
                float(row["gpu_busy_ratio"])
                for row in run_rows
                if row["workload"] == workload and row["policy"] == policy
            ]
            means.append(sum(values) / len(values))
            errors.append(0.0)
        offsets = [p + (offset - 1) * width for p in positions]
        axis.bar(offsets, means, width=width, label=LABELS[policy], color=COLORS[policy], alpha=0.85)
    axis.set_xticks(list(positions))
    axis.set_xticklabels(workloads)
    axis.set_ylim(0.65, 1.02)
    axis.set_ylabel("GPU busy ratio")
    axis.set_title("GPU utilisation by policy and workload (model time)")
    axis.grid(axis="y", alpha=0.3)
    axis.legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig2_gpu_busy_ratio.png", dpi=160)
    plt.close(fig)


def figure_threshold_sensitivity() -> None:
    rows = read_csv(RESULTS / "threshold_sweep" / "summary_metrics.csv")
    workloads = ["steady", "cpu_contention", "gpu_saturated", "bursty"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.4), sharex=True)
    for axis, workload in zip(axes.ravel(), workloads):
        subset = sorted(
            (int(row["gpu_pending_threshold"]), float(row["p99_latency_ms_mean"]), float(row["gpu_idle_ms_mean"]))
            for row in rows
            if row["workload"] == workload
        )
        thresholds = [item[0] for item in subset]
        p99 = [item[1] for item in subset]
        idle = [item[2] for item in subset]
        axis.plot(thresholds, p99, marker="o", color="#c1440e", label="P99 latency")
        axis.set_title(workload, fontsize=10)
        axis.set_ylabel("P99 (ms)", color="#c1440e")
        axis.tick_params(axis="y", labelcolor="#c1440e")
        axis.grid(alpha=0.3)
        twin = axis.twinx()
        twin.plot(thresholds, idle, marker="s", linestyle="--", color="#2f6fb5", label="GPU idle")
        twin.set_ylabel("GPU idle (ms)", color="#2f6fb5")
        twin.tick_params(axis="y", labelcolor="#2f6fb5")
        axis.set_xticks(thresholds)
    for axis in axes[1]:
        axis.set_xlabel("GPU pending threshold q0")
    fig.suptitle("Threshold sensitivity of GPU-queue feedback scheduling (30 repetitions per point)", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig3_threshold_sensitivity.png", dpi=160)
    plt.close(fig)


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    run_rows = read_csv(RESULTS / "run_metrics.csv")
    figure_contention_latency(run_rows)
    figure_gpu_utilisation(run_rows)
    figure_threshold_sensitivity()
    for path in sorted(FIGURES.glob("*.png")):
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
