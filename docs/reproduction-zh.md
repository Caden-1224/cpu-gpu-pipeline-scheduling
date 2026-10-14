# 复现记录（论文数值证据）

本页是 `results/` 与 `docs/model.md` 之间的现场凭据：任何人都可以按照这里的命令，在约 75 秒内
把随仓库发布的全部数字复现出来。记录日期 **2026-10-14**。

## 1. 结论

仓库覆盖的每一个关键数值都**逐位可复现**，并且不需要任何第三方依赖，只运用 Python 标准库。
其中也包含两组值得留意的数值：突发工况下反馈策略的 P99 为 451.5106 ms，静态提交优先为
450.6234 ms；以及 `q0 = 2` 优于默认的 `q0 = 1`，即 34.1059 ms 对 34.7518 ms。

配套论文《Low-Latency Adaptive Scheduling for CPU-GPU Pipelines Using GPU Queue Feedback》
（2026.09 录用，ISPDS 2026，拟由 IEEE 出版并收录至 IEEE Xplore）§III / §IV 的数值与
本次实测对照如下，论文本身不随仓库分发。

## 2. 环境与耗时

| 项 | 值 |
|---|---|
| 解释器 | CPython 3.11.4（Windows）以及 CPython 3.10.12（Ubuntu 22.04 / WSL） |
| 第三方依赖 | 无（`argparse/csv/heapq/json/math/random/statistics/collections/dataclasses/pathlib` 均为标准库） |
| 主实验 | `python -m simulation.run_experiment --repetitions 30` → **360 次运行，Windows 约 28 s、Linux 约 32 s** |
| 阈值敏感性 | `python -m simulation.run_threshold_sweep --repetitions 30 --thresholds 0 1 2 4` → **480 次运行，Windows 约 45 s、Linux 约 48 s** |
| 单元测试 | `python -m unittest discover -s simulation -t .` → **9 passed，约 1.2 s** |
| 合计运行次数 | 360 + 480 = **840** |

两个平台产生的结果在印刷精度上完全一致。绘图需要 `matplotlib`，它只参与绘图而不参与仿真：
`python scripts/make_figures.py`。

## 3. 数字对照：论文终稿 vs 本仓库实测

| 指标（CPU 竞争工况，跨轮均值） | 论文 | 本次实测 | 一致 |
|---|---|---|---|
| P99 静态提交优先 | 36.7866 ms | **36.7866 ms** | 一致 |
| P99 队列反馈 | 34.7518 ms | **34.7518 ms** | 一致 |
| P99 降幅（相对静态） | 5.53% | **5.5315%**（绝对差 2.0348 ms） | 一致 |
| 吞吐 静态 / 反馈 | 1.8257 / 1.8238 req/ms | **1.8257 / 1.8238** | 一致 |
| 吞吐变化（相对静态） | −0.10% | **−0.1041%** | 一致 |
| FIFO 吞吐 | 1.3260 req/ms | **1.3260** | 一致 |
| 吞吐相对 FIFO（反馈） | +37.54% | **+37.5413%** | 一致 |
| 吞吐相对 FIFO（静态提交优先） | +37.68% | **+37.6850%**（1.3260→1.8257） | 一致 |
| P95 相对 FIFO | −89.63% | **−89.6242%** | 一致 |
| P99 相对 FIFO | −88.94% | **−88.9390%** | 一致 |
| GPU 忙比 FIFO → 反馈 | 0.7174 → 0.9867 | **0.7174 → 0.9867** | 一致 |
| P99 轮间标准差（反馈） | 12.1657 ms | **12.1657 ms** | 一致 |
| 突发 P99 反馈 vs 静态 | 451.5106 vs 450.6234 ms | **451.5106 vs 450.6234**（相差 +0.8872 ms） | 一致 |
| 突发平均延迟（论文：mean latency increases） | 未给数值，仅文字 | 反馈 **292.2194** vs FIFO **272.3634** ms（+7.29%） | 与论文文字一致 |
| q0=2 相对 q0=1 | 低约 1.86% | **1.8586%**（34.1059 vs 34.7518 ms） | 一致 |
| q0=0（CPU 竞争） | 供载不足 | P99 **40.9835** ms，GPU 空闲 **14.1747** ms | 一致 |
| GPU 饱和 | 各策略与各阈值结果几乎一致 | 977.97–977.99 ms（三策略相差不到 0.03 ms） | 一致 |

阈值敏感性（CPU 竞争，q0 = 0/1/2/4）：P99 = 40.9835 / 34.7518 / 34.1059 / 34.2372 ms，
与『q0 ≥ 1 构成窄平台、q0 = 0 供载不足』一致。逐位数值见 `results/threshold_sweep/`。

## 4. 文件 → 论文章节映射

| 文件 | 作用 | 对应论文 |
|---|---|---|
| `simulation/run_experiment.py` | 四阶段离散事件模型、三种策略、主实验与汇总及报告 | §II-A/B（模型与策略）、§III-A/B、§IV |
| `simulation/run_threshold_sweep.py` | q0 敏感性（0/1/2/4），另外计算归一化积压比 | §III-B 阈值敏感性 |
| `simulation/test_experiment.py` | 完整性、可重复性、策略产出、阈值默认与可配置、负阈值拒绝 | §III-A 复现性 |
| `simulation/adaptive_scheduler.py` 与配套测试 | **本仓库扩展**的评分原型，**未接入主实验** | 与论文数值无关 |
| `results/` | 请求级、逐次运行级、汇总级数据，固化配置以及自动生成的报告 | §III 数据表 |

## 5. 关键实现细节（用于回答追问）

1. **配对种子**：阶段时长由 `request_duration(seed, request_id, kind, mean)` 生成，随机源为
   `random.Random(f"{seed}:{request_id}:{kind}")`，也就是按（种子，请求号，阶段）索引预先生成，
   跨策略复用；到达流由 `make_arrivals` 生成之后共享。
2. **q(t) 定义**：`len(gpu_queue) + int(gpu_running)`，**包含运行中的那一项**（`model.md` §4）。
3. **策略与阈值**：`q(t) <= q0` 时按 `submit > preprocess > postprocess > background` 排序；
   否则按 `preprocess > postprocess > submit > background` 排序；默认 `q0 = 1`。
4. **同刻事件**：同一时间戳的事件先全部弹出并批量更新状态，**再**做调度决策，避免堆序影响结果。
5. **分位算法**：线性插值，位置为 `(n−1)·p/100`；1000 请求的 P99 对应位置 **989.01**，
   取第 989 个与第 990 个样本进行插值，而不是 nearest-rank 取第 990 个。
6. **吞吐定义**：`requests / (最后完成 − 首个到达)`，属于有限批次的完成跨度，不是无限稳态服务率。
7. **统计口径**：每次运行内部先算分位，再跨 30 次运行取均值，即 `mean_r(Q99(L_r))`，不是池化分位。
8. **种子**：`1000 + repetition (+ workload_index × 10000)`，每个工况取 1000–1029。
9. **阶段时长分布**：有界对数正态，`max(0.2·mean, min(3·mean, lognormvariate(log mean, 0.28)))`。
10. **归一化标称积压**：取值为 `q0 × gpu_ms / (preprocess_ms + submit_ms + postprocess_ms)`，
    见 `run_threshold_sweep.py` 以及 `results/threshold_sweep/report.md`。

## 6. 三步复现

```bash
python -m simulation.run_experiment --repetitions 30           # 约 28 s，360 次运行
python -m unittest discover -s simulation -t .                 # 约 1.2 s，9 项通过
python scripts/make_figures.py                                 # 重建 README 中的全部图
```

随后对照 `results/summary_metrics.csv` 当中 `cpu_contention` 行的 `p99_latency_ms_mean`
两列，即可确认 36.7866 → 34.7518。

## 7. 论文全文逐条对照（脚本化）

`scripts/check_paper_numbers.py` 把论文终稿全文印出的每个数值写成断言，并且随 CI 执行：

```bash
python scripts/check_paper_numbers.py --check     # 任何数值漂移即非零退出
python scripts/check_paper_numbers.py --write     # 重新生成 docs/paper-number-check.md
```

| 项 | 数量 | 结果 |
|---|---:|---|
| 绝对值（Table I 的 60 个表格值、Fig. 3 的 12 个两位小数标注、正文逐一列举值、阈值元组、区间上下界） | 169 | **169/169 四位小数一致** |
| 派生百分比（相对 FIFO 与静态的吞吐、P95、P99 变化，q0=2 对 q0=1） | 10 | **9/10 两位小数一致** |
| 标记项（不计为不一致） | 2 | ①论文把相对 FIFO 的 P95 降幅印作 89.63%，而 `32.1078/309.4488−1 = −89.6242%` 两位四舍五入为 **89.62%**，两个绝对值本身完全一致；②论文写作 approximately 494.7069 的 GPU 饱和平均延迟，`q0=4` 实测为 **494.7070**，按 1e-3 容差标为 APPROX |
| 不一致 | **0** | — |

完整对照表（逐行 manuscript / results / PASS）见 [paper-number-check.md](paper-number-check.md)。
