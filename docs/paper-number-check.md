# Manuscript number check

Every value the accompanying manuscript reports, compared with the CSVs in
`results/`. Regenerate with `python scripts/check_paper_numbers.py --write`;
`--check` exits non-zero as soon as a value drifts.

Absolute values checked: 169; derived percentages: 10; mismatches: 0.

## Values reported in the manuscript

| quantity | manuscript | results/ | status |
|---|---:|---:|---|
| `cpu_contention / fifo / throughput_req_per_ms_mean` | 1.3260 | 1.3260 | PASS |
| `cpu_contention / static_submit / throughput_req_per_ms_mean` | 1.8257 | 1.8257 | PASS |
| `cpu_contention / gpu_feedback / throughput_req_per_ms_mean` | 1.8238 | 1.8238 | PASS |
| `cpu_contention / fifo / p95_latency_ms_mean` | 309.4488 | 309.4488 | PASS |
| `cpu_contention / gpu_feedback / p95_latency_ms_mean` | 32.1078 | 32.1078 | PASS |
| `cpu_contention / static_submit / p95_latency_ms_mean` | 32.9830 | 32.9830 | PASS |
| `cpu_contention / fifo / p99_latency_ms_mean` | 314.1820 | 314.1820 | PASS |
| `cpu_contention / gpu_feedback / p99_latency_ms_mean` | 34.7518 | 34.7518 | PASS |
| `cpu_contention / static_submit / p99_latency_ms_mean` | 36.7866 | 36.7866 | PASS |
| `cpu_contention / fifo / mean_latency_ms_mean` | 195.2205 | 195.2205 | PASS |
| `cpu_contention / gpu_feedback / mean_latency_ms_mean` | 19.6241 | 19.6241 | PASS |
| `cpu_contention / static_submit / mean_latency_ms_mean` | 20.1235 | 20.1235 | PASS |
| `cpu_contention / fifo / gpu_busy_ratio_mean` | 0.7174 | 0.7174 | PASS |
| `cpu_contention / gpu_feedback / gpu_busy_ratio_mean` | 0.9867 | 0.9867 | PASS |
| `cpu_contention / fifo / gpu_idle_ms_mean` | 213.3647 | 213.3647 | PASS |
| `cpu_contention / gpu_feedback / gpu_idle_ms_mean` | 7.3628 | 7.3628 | PASS |
| `cpu_contention / gpu_feedback / p99_latency_ms_std` | 12.1657 | 12.1657 | PASS |
| `bursty / fifo / p99_latency_ms_mean` | 456.5480 | 456.5480 | PASS |
| `bursty / fifo / mean_latency_ms_mean` | 272.3634 | 272.3634 | PASS |
| `bursty / gpu_feedback / p99_latency_ms_mean` | 451.5106 | 451.5106 | PASS |
| `bursty / static_submit / p99_latency_ms_mean` | 450.6234 | 450.6234 | PASS |
| `bursty / gpu_feedback / mean_latency_ms_mean` | 292.2194 | 292.2194 | PASS |
| `bursty / static_submit / mean_latency_ms_mean` | 300.7754 | 300.7754 | PASS |
| `steady / gpu_feedback / throughput_req_per_ms_mean` | 1.2781 | 1.2781 | PASS |
| `steady / gpu_feedback / gpu_busy_ratio_mean` | 0.9985 | 0.9985 | PASS |
| `gpu_saturated / gpu_feedback / throughput_req_per_ms_mean` | 0.7106 | 0.7106 | PASS |
| `gpu_saturated / gpu_feedback / p99_latency_ms_mean` | 977.9790 | 977.9790 | PASS |
| `bursty / q0=0 / throughput_req_per_ms_mean` | 1.3429 | 1.3429 | PASS |
| `bursty / q0=0 / mean_latency_ms_mean` | 329.3028 | 329.3028 | PASS |
| `bursty / q0=0 / p95_latency_ms_mean` | 498.0476 | 498.0476 | PASS |
| `bursty / q0=0 / p99_latency_ms_mean` | 517.2091 | 517.2091 | PASS |
| `bursty / q0=0 / gpu_idle_ms_mean` | 67.5841 | 67.5841 | PASS |
| `bursty / q0=1 / throughput_req_per_ms_mean` | 1.4728 | 1.4728 | PASS |
| `bursty / q0=1 / mean_latency_ms_mean` | 292.2194 | 292.2194 | PASS |
| `bursty / q0=1 / p95_latency_ms_mean` | 432.3627 | 432.3627 | PASS |
| `bursty / q0=1 / p99_latency_ms_mean` | 451.5106 | 451.5106 | PASS |
| `bursty / q0=1 / gpu_idle_ms_mean` | 1.9126 | 1.9126 | PASS |
| `bursty / q0=2 / throughput_req_per_ms_mean` | 1.4748 | 1.4748 | PASS |
| `bursty / q0=2 / mean_latency_ms_mean` | 291.8256 | 291.8256 | PASS |
| `bursty / q0=2 / p95_latency_ms_mean` | 431.4357 | 431.4357 | PASS |
| `bursty / q0=2 / p99_latency_ms_mean` | 450.6043 | 450.6043 | PASS |
| `bursty / q0=2 / gpu_idle_ms_mean` | 0.9789 | 0.9789 | PASS |
| `bursty / q0=4 / throughput_req_per_ms_mean` | 1.4748 | 1.4748 | PASS |
| `bursty / q0=4 / mean_latency_ms_mean` | 291.8950 | 291.8950 | PASS |
| `bursty / q0=4 / p95_latency_ms_mean` | 431.4297 | 431.4297 | PASS |
| `bursty / q0=4 / p99_latency_ms_mean` | 450.5788 | 450.5788 | PASS |
| `bursty / q0=4 / gpu_idle_ms_mean` | 0.9826 | 0.9826 | PASS |
| `cpu_contention / q0=0 / throughput_req_per_ms_mean` | 1.8014 | 1.8014 | PASS |
| `cpu_contention / q0=0 / mean_latency_ms_mean` | 24.9687 | 24.9687 | PASS |
| `cpu_contention / q0=0 / p95_latency_ms_mean` | 38.6196 | 38.6196 | PASS |
| `cpu_contention / q0=0 / p99_latency_ms_mean` | 40.9835 | 40.9835 | PASS |
| `cpu_contention / q0=0 / gpu_idle_ms_mean` | 14.1747 | 14.1747 | PASS |
| `cpu_contention / q0=1 / throughput_req_per_ms_mean` | 1.8238 | 1.8238 | PASS |
| `cpu_contention / q0=1 / mean_latency_ms_mean` | 19.6241 | 19.6241 | PASS |
| `cpu_contention / q0=1 / p95_latency_ms_mean` | 32.1078 | 32.1078 | PASS |
| `cpu_contention / q0=1 / p99_latency_ms_mean` | 34.7518 | 34.7518 | PASS |
| `cpu_contention / q0=1 / gpu_idle_ms_mean` | 7.3628 | 7.3628 | PASS |
| `cpu_contention / q0=2 / throughput_req_per_ms_mean` | 1.8257 | 1.8257 | PASS |
| `cpu_contention / q0=2 / mean_latency_ms_mean` | 19.2147 | 19.2147 | PASS |
| `cpu_contention / q0=2 / p95_latency_ms_mean` | 31.4954 | 31.4954 | PASS |
| `cpu_contention / q0=2 / p99_latency_ms_mean` | 34.1059 | 34.1059 | PASS |
| `cpu_contention / q0=2 / gpu_idle_ms_mean` | 6.7890 | 6.7890 | PASS |
| `cpu_contention / q0=4 / throughput_req_per_ms_mean` | 1.8258 | 1.8258 | PASS |
| `cpu_contention / q0=4 / mean_latency_ms_mean` | 19.2539 | 19.2539 | PASS |
| `cpu_contention / q0=4 / p95_latency_ms_mean` | 31.5198 | 31.5198 | PASS |
| `cpu_contention / q0=4 / p99_latency_ms_mean` | 34.2372 | 34.2372 | PASS |
| `cpu_contention / q0=4 / gpu_idle_ms_mean` | 6.7773 | 6.7773 | PASS |
| `gpu_saturated / q0=0 / throughput_req_per_ms_mean` | 0.7106 | 0.7106 | PASS |
| `gpu_saturated / q0=0 / mean_latency_ms_mean` | 494.7069 | 494.7069 | PASS |
| `gpu_saturated / q0=0 / p95_latency_ms_mean` | 939.4402 | 939.4402 | PASS |
| `gpu_saturated / q0=0 / p99_latency_ms_mean` | 977.9790 | 977.9790 | PASS |
| `gpu_saturated / q0=0 / gpu_idle_ms_mean` | 0.4568 | 0.4568 | PASS |
| `gpu_saturated / q0=1 / throughput_req_per_ms_mean` | 0.7106 | 0.7106 | PASS |
| `gpu_saturated / q0=1 / mean_latency_ms_mean` | 494.7069 | 494.7069 | PASS |
| `gpu_saturated / q0=1 / p95_latency_ms_mean` | 939.4402 | 939.4402 | PASS |
| `gpu_saturated / q0=1 / p99_latency_ms_mean` | 977.9790 | 977.9790 | PASS |
| `gpu_saturated / q0=1 / gpu_idle_ms_mean` | 0.4568 | 0.4568 | PASS |
| `gpu_saturated / q0=2 / throughput_req_per_ms_mean` | 0.7106 | 0.7106 | PASS |
| `gpu_saturated / q0=2 / mean_latency_ms_mean` | 494.7069 | 494.7069 | PASS |
| `gpu_saturated / q0=2 / p95_latency_ms_mean` | 939.4402 | 939.4402 | PASS |
| `gpu_saturated / q0=2 / p99_latency_ms_mean` | 977.9790 | 977.9790 | PASS |
| `gpu_saturated / q0=2 / gpu_idle_ms_mean` | 0.4568 | 0.4568 | PASS |
| `gpu_saturated / q0=4 / throughput_req_per_ms_mean` | 0.7106 | 0.7106 | PASS |
| `gpu_saturated / q0=4 / mean_latency_ms_mean` | 494.7069 | 494.7070 | APPROX |
| `gpu_saturated / q0=4 / p95_latency_ms_mean` | 939.4402 | 939.4402 | PASS |
| `gpu_saturated / q0=4 / p99_latency_ms_mean` | 977.9790 | 977.9790 | PASS |
| `gpu_saturated / q0=4 / gpu_idle_ms_mean` | 0.4568 | 0.4568 | PASS |
| `steady / q0=0 / throughput_req_per_ms_mean` | 1.2773 | 1.2773 | PASS |
| `steady / q0=0 / mean_latency_ms_mean` | 118.1097 | 118.1097 | PASS |
| `steady / q0=0 / p95_latency_ms_mean` | 221.1061 | 221.1061 | PASS |
| `steady / q0=0 / p99_latency_ms_mean` | 230.0937 | 230.0937 | PASS |
| `steady / q0=0 / gpu_idle_ms_mean` | 1.6845 | 1.6845 | PASS |
| `steady / q0>=1 range / throughput_req_per_ms_mean` | 1.2781-1.2781 | 1.2781 | PASS |
| `steady / q0>=1 range / mean_latency_ms_mean` | 117.6273-117.6283 | 117.6273 | PASS |
| `steady / q0>=1 range / p95_latency_ms_mean` | 220.6018-220.6044 | 220.6018 | PASS |
| `steady / q0>=1 range / p99_latency_ms_mean` | 229.5955-229.5969 | 229.5955 | PASS |
| `steady / q0>=1 range / gpu_idle_ms_mean` | 1.1950-1.1965 | 1.1950 | PASS |
| `Table I / steady / fifo / throughput_req_per_ms_mean` | 1.2778 | 1.2778 | PASS |
| `Table I / steady / fifo / p95_latency_ms_mean` | 220.8328 | 220.8328 | PASS |
| `Table I / steady / fifo / p99_latency_ms_mean` | 229.7633 | 229.7633 | PASS |
| `Table I / steady / fifo / gpu_busy_ratio_mean` | 0.9982 | 0.9982 | PASS |
| `Table I / steady / fifo / gpu_idle_ms_mean` | 1.4192 | 1.4192 | PASS |
| `Table I / steady / static_submit / throughput_req_per_ms_mean` | 1.2781 | 1.2781 | PASS |
| `Table I / steady / static_submit / p95_latency_ms_mean` | 220.5986 | 220.5986 | PASS |
| `Table I / steady / static_submit / p99_latency_ms_mean` | 229.5519 | 229.5519 | PASS |
| `Table I / steady / static_submit / gpu_busy_ratio_mean` | 0.9985 | 0.9985 | PASS |
| `Table I / steady / static_submit / gpu_idle_ms_mean` | 1.2017 | 1.2017 | PASS |
| `Table I / steady / gpu_feedback / throughput_req_per_ms_mean` | 1.2781 | 1.2781 | PASS |
| `Table I / steady / gpu_feedback / p95_latency_ms_mean` | 220.6044 | 220.6044 | PASS |
| `Table I / steady / gpu_feedback / p99_latency_ms_mean` | 229.5969 | 229.5969 | PASS |
| `Table I / steady / gpu_feedback / gpu_busy_ratio_mean` | 0.9985 | 0.9985 | PASS |
| `Table I / steady / gpu_feedback / gpu_idle_ms_mean` | 1.1965 | 1.1965 | PASS |
| `Table I / cpu_contention / fifo / throughput_req_per_ms_mean` | 1.3260 | 1.3260 | PASS |
| `Table I / cpu_contention / fifo / p95_latency_ms_mean` | 309.4488 | 309.4488 | PASS |
| `Table I / cpu_contention / fifo / p99_latency_ms_mean` | 314.1820 | 314.1820 | PASS |
| `Table I / cpu_contention / fifo / gpu_busy_ratio_mean` | 0.7174 | 0.7174 | PASS |
| `Table I / cpu_contention / fifo / gpu_idle_ms_mean` | 213.3647 | 213.3647 | PASS |
| `Table I / cpu_contention / static_submit / throughput_req_per_ms_mean` | 1.8257 | 1.8257 | PASS |
| `Table I / cpu_contention / static_submit / p95_latency_ms_mean` | 32.9830 | 32.9830 | PASS |
| `Table I / cpu_contention / static_submit / p99_latency_ms_mean` | 36.7866 | 36.7866 | PASS |
| `Table I / cpu_contention / static_submit / gpu_busy_ratio_mean` | 0.9877 | 0.9877 | PASS |
| `Table I / cpu_contention / static_submit / gpu_idle_ms_mean` | 6.7921 | 6.7921 | PASS |
| `Table I / cpu_contention / gpu_feedback / throughput_req_per_ms_mean` | 1.8238 | 1.8238 | PASS |
| `Table I / cpu_contention / gpu_feedback / p95_latency_ms_mean` | 32.1078 | 32.1078 | PASS |
| `Table I / cpu_contention / gpu_feedback / p99_latency_ms_mean` | 34.7518 | 34.7518 | PASS |
| `Table I / cpu_contention / gpu_feedback / gpu_busy_ratio_mean` | 0.9867 | 0.9867 | PASS |
| `Table I / cpu_contention / gpu_feedback / gpu_idle_ms_mean` | 7.3628 | 7.3628 | PASS |
| `Table I / gpu_saturated / fifo / throughput_req_per_ms_mean` | 0.7106 | 0.7106 | PASS |
| `Table I / gpu_saturated / fifo / p95_latency_ms_mean` | 939.4630 | 939.4630 | PASS |
| `Table I / gpu_saturated / fifo / p99_latency_ms_mean` | 977.9945 | 977.9945 | PASS |
| `Table I / gpu_saturated / fifo / gpu_busy_ratio_mean` | 0.9997 | 0.9997 | PASS |
| `Table I / gpu_saturated / fifo / gpu_idle_ms_mean` | 0.4771 | 0.4771 | PASS |
| `Table I / gpu_saturated / static_submit / throughput_req_per_ms_mean` | 0.7106 | 0.7106 | PASS |
| `Table I / gpu_saturated / static_submit / p95_latency_ms_mean` | 939.4073 | 939.4073 | PASS |
| `Table I / gpu_saturated / static_submit / p99_latency_ms_mean` | 977.9742 | 977.9742 | PASS |
| `Table I / gpu_saturated / static_submit / gpu_busy_ratio_mean` | 0.9997 | 0.9997 | PASS |
| `Table I / gpu_saturated / static_submit / gpu_idle_ms_mean` | 0.4568 | 0.4568 | PASS |
| `Table I / gpu_saturated / gpu_feedback / throughput_req_per_ms_mean` | 0.7106 | 0.7106 | PASS |
| `Table I / gpu_saturated / gpu_feedback / p95_latency_ms_mean` | 939.4402 | 939.4402 | PASS |
| `Table I / gpu_saturated / gpu_feedback / p99_latency_ms_mean` | 977.9790 | 977.9790 | PASS |
| `Table I / gpu_saturated / gpu_feedback / gpu_busy_ratio_mean` | 0.9997 | 0.9997 | PASS |
| `Table I / gpu_saturated / gpu_feedback / gpu_idle_ms_mean` | 0.4568 | 0.4568 | PASS |
| `Table I / bursty / fifo / throughput_req_per_ms_mean` | 1.4621 | 1.4621 | PASS |
| `Table I / bursty / fifo / p95_latency_ms_mean` | 437.3239 | 437.3239 | PASS |
| `Table I / bursty / fifo / p99_latency_ms_mean` | 456.5480 | 456.5480 | PASS |
| `Table I / bursty / fifo / gpu_busy_ratio_mean` | 0.9900 | 0.9900 | PASS |
| `Table I / bursty / fifo / gpu_idle_ms_mean` | 6.8830 | 6.8830 | PASS |
| `Table I / bursty / static_submit / throughput_req_per_ms_mean` | 1.4748 | 1.4748 | PASS |
| `Table I / bursty / static_submit / p95_latency_ms_mean` | 431.4126 | 431.4126 | PASS |
| `Table I / bursty / static_submit / p99_latency_ms_mean` | 450.6234 | 450.6234 | PASS |
| `Table I / bursty / static_submit / gpu_busy_ratio_mean` | 0.9986 | 0.9986 | PASS |
| `Table I / bursty / static_submit / gpu_idle_ms_mean` | 0.9776 | 0.9776 | PASS |
| `Table I / bursty / gpu_feedback / throughput_req_per_ms_mean` | 1.4728 | 1.4728 | PASS |
| `Table I / bursty / gpu_feedback / p95_latency_ms_mean` | 432.3627 | 432.3627 | PASS |
| `Table I / bursty / gpu_feedback / p99_latency_ms_mean` | 451.5106 | 451.5106 | PASS |
| `Table I / bursty / gpu_feedback / gpu_busy_ratio_mean` | 0.9972 | 0.9972 | PASS |
| `Table I / bursty / gpu_feedback / gpu_idle_ms_mean` | 1.9126 | 1.9126 | PASS |
| `Fig. 3 / steady / fifo` | 229.76 | 229.76 | PASS |
| `Fig. 3 / steady / static_submit` | 229.55 | 229.55 | PASS |
| `Fig. 3 / steady / gpu_feedback` | 229.60 | 229.60 | PASS |
| `Fig. 3 / cpu_contention / fifo` | 314.18 | 314.18 | PASS |
| `Fig. 3 / cpu_contention / static_submit` | 36.79 | 36.79 | PASS |
| `Fig. 3 / cpu_contention / gpu_feedback` | 34.75 | 34.75 | PASS |
| `Fig. 3 / gpu_saturated / fifo` | 977.99 | 977.99 | PASS |
| `Fig. 3 / gpu_saturated / static_submit` | 977.97 | 977.97 | PASS |
| `Fig. 3 / gpu_saturated / gpu_feedback` | 977.98 | 977.98 | PASS |
| `Fig. 3 / bursty / fifo` | 456.55 | 456.55 | PASS |
| `Fig. 3 / bursty / static_submit` | 450.62 | 450.62 | PASS |
| `Fig. 3 / bursty / gpu_feedback` | 451.51 | 451.51 | PASS |

## Percentages quoted in prose

| comparison | manuscript | results/ | status |
|---|---:|---:|---|
| static vs FIFO throughput | +37.68% | +37.68% | PASS |
| feedback vs FIFO throughput | +37.54% | +37.54% | PASS |
| feedback vs FIFO P95 | -89.63% | -89.62% | ROUNDING |
| feedback vs FIFO P99 | -88.94% | -88.94% | PASS |
| feedback vs static throughput | -0.10% | -0.10% | PASS |
| feedback vs static P99 | -5.53% | -5.53% | PASS |
| bursty feedback vs FIFO P99 | -1.10% | -1.10% | PASS |
| bursty feedback vs FIFO mean latency | +7.29% | +7.29% | PASS |
| cpu_contention q0=2 vs q0=1 P99 | -1.86% | -1.86% | PASS |
| bursty q0=2 vs q0=1 P99 | -0.20% | -0.20% | PASS |

The bursty rows make explicit the tradeoff the manuscript states in words:
under bursty arrivals the feedback policy lowers P99 while raising mean latency.
Both percentages are computed relative to FIFO from `results/summary_metrics.csv`.

## Known rounding and approximation differences

One printed percentage does not follow from two-decimal rounding of the
reproduced value: the manuscript reports the FIFO-relative P95 reduction as
89.63%, while `32.1078 / 309.4488 - 1` is -89.6242%, which rounds to 89.62%.
The two absolute P95 values agree exactly, so the discrepancy is confined to
the printed percentage and is listed here rather than treated as a match.

A second, smaller case: the GPU-saturated mean latency is printed as
*approximately* 494.7069, while the q0 = 4 run reproduces as 494.7070, so that
row is marked APPROX under a 0.001 tolerance rather than counted as a mismatch.
