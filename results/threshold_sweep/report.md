# GPU Pending Threshold Sensitivity Study

This report contains seed-controlled discrete-event results, not hardware measurements.
The nominal GPU backlog is q0 times the workload's nominal GPU service time.
The normalized ratio divides that backlog by nominal preprocessing, submission, and postprocessing demand.

| Workload | q0 | Normalized backlog | Throughput (req/ms) | Mean (ms) | P95 (ms) | P99 (ms) | GPU idle (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|
| steady | 0 | 0.0000 | 1.2773 | 118.1097 | 221.1061 | 230.0937 | 1.6845 |
| steady | 1 | 0.9868 | 1.2781 | 117.6281 | 220.6044 | 229.5969 | 1.1965 |
| steady | 2 | 1.9737 | 1.2781 | 117.6273 | 220.6018 | 229.5955 | 1.1950 |
| steady | 4 | 3.9474 | 1.2781 | 117.6283 | 220.6018 | 229.5955 | 1.1950 |
| cpu_contention | 0 | 0.0000 | 1.8014 | 24.9687 | 38.6196 | 40.9835 | 14.1747 |
| cpu_contention | 1 | 0.6190 | 1.8238 | 19.6241 | 32.1078 | 34.7518 | 7.3628 |
| cpu_contention | 2 | 1.2381 | 1.8257 | 19.2147 | 31.4954 | 34.1059 | 6.7890 |
| cpu_contention | 4 | 2.4762 | 1.8258 | 19.2539 | 31.5198 | 34.2372 | 6.7773 |
| gpu_saturated | 0 | 0.0000 | 0.7106 | 494.7069 | 939.4402 | 977.9790 | 0.4568 |
| gpu_saturated | 1 | 3.0000 | 0.7106 | 494.7069 | 939.4402 | 977.9790 | 0.4568 |
| gpu_saturated | 2 | 6.0000 | 0.7106 | 494.7069 | 939.4402 | 977.9790 | 0.4568 |
| gpu_saturated | 4 | 12.0000 | 0.7106 | 494.7070 | 939.4402 | 977.9790 | 0.4568 |
| bursty | 0 | 0.0000 | 1.3429 | 329.3028 | 498.0476 | 517.2091 | 67.5841 |
| bursty | 1 | 0.8784 | 1.4728 | 292.2194 | 432.3627 | 451.5106 | 1.9126 |
| bursty | 2 | 1.7568 | 1.4748 | 291.8256 | 431.4357 | 450.6043 | 0.9789 |
| bursty | 4 | 3.5135 | 1.4748 | 291.8950 | 431.4297 | 450.5788 | 0.9826 |
