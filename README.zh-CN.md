# CPU-GPU 流水线调度仿真器

[English README](README.md) | 简体中文

本仓库是论文 **Low-Latency Adaptive Scheduling for CPU-GPU Pipelines Using GPU Queue
Feedback**的代码仓库，其中运用一个种子可控的**离散事件模型**，来开展流水线
推理服务中 **CPU 侧任务选择策略**的研究工作：每个请求依次经过 CPU 预处理、CPU 提交、
单 GPU 服务以及 CPU 后处理。仓库在四种合成负载下对三种调度策略进行比较，同时把每一个数字
背后的固化配置、逐次运行指标与绘图脚本一并公开。

本仓库属于**纯数值模型**，并不涉及对 GPU、CUDA、驱动以及 Linux `sched_ext` / eBPF 程序所
开展的测量工作，所有结论都只对**本模型在文档化参数下**成立。复现不需要任何第三方依赖，
模型只运用 Python 标准库。

## 核心结果

在 CPU 竞争工况下，也就是两个非抢占核心被请求各阶段以及后台任务共同占用时，一个比特的
反馈信号即 GPU 待处理深度，就可以在几乎不损失吞吐的前提下把尾延迟压低：


| 负载           | 策略         | 吞吐 (req/ms) | P95 (ms) | P99 (ms) | GPU 忙碌比 |
| -------------- | ------------ | ------------: | -------: | -------: | ---------: |
| cpu_contention | FIFO         |        1.3260 | 309.4488 | 314.1820 |     0.7174 |
| cpu_contention | 静态提交优先 |        1.8257 |  32.9830 |  36.7866 |     0.9877 |
| cpu_contention | GPU 队列反馈 |        1.8238 |  32.1078 |  34.7518 |     0.9867 |

* **P99 延迟** 从 36.7866 ms 降到 34.7518 ms：相对静态提交优先为 **−5.53%**，相对 FIFO 则为 **−88.94%**。
* **吞吐** 1.8238 req/ms：相对静态提交优先为 **−0.10%**，相对 FIFO 为 **+37.54%**。需要注意的是，
  **静态提交优先单独就拿回了 +37.68%**，也就是 1.8257 req/ms，因此吞吐的恢复主要来自提交优先，
  反馈比特真正贡献的是尾延迟。
* **GPU 忙碌比** 从 0.7174 升到 0.9867：相对 FIFO 的收益主要来自消除 CPU 所造成的 GPU 空转，
  而不是让 GPU 本身更快。

![逐次运行的 P99 分布](figures/fig1_policy_p99_box.png)

同一组数字也呈现出该策略在各负载下的差异：


| 负载          | 现象                                                                               | 解读                                                                                |
| ------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| bursty        | P99 反馈 451.5106 ms，静态 450.6234 ms；平均延迟反馈 292.2194 ms，FIFO 272.3634 ms | 相对静态提交优先，尾延迟高出 0.89 ms；相对 FIFO，P99 压低 1.10%，平均延迟上升 7.29% |
| gpu_saturated | 三种策略互相相差不到 0.03 ms                                                       | 瓶颈位于 GPU 服务时间，CPU 侧的排序几乎不影响结果                                   |
| steady        | 差异不到 0.1%                                                                      | GPU 已接近饱和，可供调度腾挪的空间很小                                              |

## 模型定义

```
到达 -> [CPU 预处理] -> [CPU 提交] -> GPU 队列 -> [GPU 服务] -> [CPU 后处理] -> 完成
```

* CPU：两个非抢占核心，工作保持，也就是 work-conserving；只要核心空闲并且存在就绪任务，马上进行决策。
* GPU：单服务台，按照 GPU 队列的 FIFO 顺序来取任务，同样不可抢占。
* 后台任务会与请求各阶段争抢同一批 CPU 核心，但始终不会进入 GPU。

四种负载以及三种策略的具体参数见 [README.md](README.md) 的 Workloads / Policies 两节，
完整的形式化定义见 [docs/model.md](docs/model.md)。

## 可复现性设计

1. **配对种子**：每个阶段的时长按 `(seed, request_id, stage)` 生成一次，三种策略复用同一份
   时长样本，这样策略比较只改变选择规则，不会改变输入流。
2. **共享到达流**：请求到达以及后台任务到达按 `(负载, 种子)` 生成一次，跨策略共享。
3. **同刻事件批量处理**：同一时间戳的事件先全部更新状态，再做调度决策，堆序不会渗入结果。
4. **固定种子**：负载 `w` 的第 `r` 次重复运用种子 `1000 + r + 10000 * index(w)`。

## 快速开始

需要 Python 3.10 以上版本，不使用 `enum.StrEnum`，Ubuntu 22.04 的默认解释器即可，且无需第三方包。

```bash
python -m simulation.run_experiment --repetitions 30
python -m simulation.run_threshold_sweep --repetitions 30 --thresholds 0 1 2 4
python -m unittest discover -s simulation -t .
```

主实验为 4 负载 × 3 策略 × 30 次，即 **360 次运行**，约 28 s；阈值敏感性为 4 × 4 × 30，
即 **480 次运行**，约 45 s，合计 840 次。输出落在 `results/`，其中包含请求级、逐次运行级、
汇总级 CSV，固化配置以及自动生成的 `report.md`。`run_threshold_sweep.py` 默认拒绝覆盖已有
结果目录，需要覆盖时显式加上 `--force`。

## GPU 利用率

![各策略的 GPU 忙碌比](figures/fig2_gpu_busy_ratio.png)

FIFO 与两种优先级策略之间的差距主要来自 **GPU 空转**，而不是调度技巧。在 CPU 竞争工况下，
FIFO 于 754.40 ms 的 makespan 当中让 GPU 空转 213.36 ms，忙碌比为 0.7174；静态提交优先以及
GPU 反馈则把空转压到 6.79 ms 与 7.36 ms，忙碌比分别为 0.9877 与 0.9867。GPU 被喂饱之后，
反馈策略在 P99 上还剩下 2.03 ms 的收益，这部分来自**什么时候**提交，而不是是否提交。

## 论文数值对照

[`scripts/check_paper_numbers.py`](scripts/check_paper_numbers.py) 把论文当中印出的**每一个数字**写成断言，
共计 169 个绝对值以及 10 个派生百分比，并且由 CI 来执行：

```bash
python scripts/check_paper_numbers.py --check
```

结果为 **169/169** 个绝对值在四位小数上完全一致，**9/10** 个派生百分比在两位小数上一致。
另有 1 项标记而未计为一致：论文把相对 FIFO 的 P95 降幅写作 89.63%，而
`32.1078 / 309.4488 − 1 = −89.6242%` 四舍五入应为 89.62%，两个 P95 绝对值本身完全一致。
还有 1 项标为 APPROX：GPU 饱和工况的平均延迟论文写作 **approximately** 494.7069，而 `q0 = 4`
实测为 494.7070。完整的对照表见 [docs/paper-number-check.md](docs/paper-number-check.md)。

## 阈值敏感性

![q0 敏感性](figures/fig3_threshold_sensitivity.png)


| 负载                    |   q0 = 0 |   q0 = 1 |       q0 = 2 |   q0 = 4 |
| ----------------------- | -------: | -------: | -----------: | -------: |
| cpu_contention P99 (ms) |  40.9835 |  34.7518 |  **34.1059** |  34.2372 |
| bursty P99 (ms)         | 517.2091 | 451.5106 | **450.6043** | 450.5788 |
| steady P99 (ms)         | 230.0937 | 229.5969 |     229.5955 | 229.5955 |
| gpu_saturated P99 (ms)  | 977.9790 | 977.9790 |     977.9790 | 977.9790 |

* `q0 = 0` 在 CPU 竞争工况下供载不足：P99 升高 17.9%，GPU 空转 14.17 ms。
* `q0 ≥ 1` 构成一个窄平台：调阈值的收益最多也只有约 1.86%，即 q0=2 相对 q0=1，远小于
  『有没有反馈』本身的差别。
* `gpu_saturated` 对阈值不敏感：队列不会被 CPU 速度清空。

## 自适应策略原型

`simulation/adaptive_scheduler.py` 拥有更完整的评分策略，涵盖 GPU 在途量 EMA、等待时间反馈
以及防饥饿老化，并且配有单元测试。它属于**设计原型**，刻意**未接入** `run_experiment.py`。
评分函数、参数以及参数标定的路径见
[docs/adaptive_gpu_feedback_scheduler.md](docs/adaptive_gpu_feedback_scheduler.md)。

## 复现记录（中文）

环境、耗时以及逐位数字对照见 [docs/reproduction-zh.md](docs/reproduction-zh.md)。

## 引用

本仓库对应论文 **Low-Latency Adaptive Scheduling for CPU-GPU Pipelines Using GPU Queue
Feedback**（Linkai Liu、Muchenang Wen），该论文于 2026.09 录用，会议为 ISPDS 2026，
也就是第七届信息科学与并行、分布式处理国际学术会议；拟由 IEEE 出版并收录至 IEEE Xplore。
论文本身不随仓库分发，其中印出的每个数值都由
[`scripts/check_paper_numbers.py`](scripts/check_paper_numbers.py) 对照 `results/` 进行断言，
[CITATION.cff](CITATION.cff) 中保存了同样的记录，供工具读取。

## 许可

MIT，见 [LICENSE](LICENSE)。
