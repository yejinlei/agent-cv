# SGM 半全局立体匹配 · 论文故事

<AlgorithmCard
  name="SGM 半全局立体匹配"
  enName="Semi-Global Matching"
  chapter="ch-14-3d-vision"
  branch="geometry"
  year="2005"
  author="Heiko Hirschmüller"
  paper="—"
  level="advanced"
  tagline="双目测距的工业标准，8 个方向做平滑约束，又快又稳出稠密视差图"
  analogy="BM 块匹配像个没耐心的小孩，只看自己周围一小圈就乱猜；SGM 像个老练的侦探，从上下左右斜 8 个方向打听消息，让相邻像素的深度「差不多」，拼出连贯的深度图"
  scene="双目深度相机（RealSense、自动驾驶双目）、无人机避障、机器人导航、三维重建、工业检测"
  :pros='["输出稠密视差图", "速度可接受（CPU 实时）", "精度在经典方法里最高", "OpenCV 内置 StereoSGBM", "参数可解释（P1/P2 平滑）"]'
  :cons='["参数多（numDisparities/blockSize/P1/P2 等）", "无纹理区域仍失败", "重复纹理误匹配", "需要精确双目标定和立体校正", "远处深度误差平方级增长"]'
/>

## 发表信息

| 项 | 内容 |
|---|---|
| **论文名** | 根据算法不同见原论文 |
| **作者** | Heiko Hirschmüller |
| **发表年份** | 2005 |
| **机构** | 计算机视觉经典工作 |
| **引用数** | 数千到数万次（经典工作） |

## 论文背后的故事

Heiko Hirschmüller 是德国 DLR（航空航天中心）机器人与 Mechatronics 中心的研究员。2005 年他在 PAMI 上发表《Stereo Processing by Semiglobal Matching and Mutual Information》，这篇论文后来成为立体匹配领域引用最高的论文之一。Hirschmüller 当时的痛点是：全局方法（如图割、BP）效果好但太慢；局部方法（BM、SAD）快但视差图碎。他提出「半全局」思想：不是全图 2D 优化，也不是逐像素独立，而是沿 8 或 16 个方向做动态规划聚合——既保留了全局平滑约束，速度又接近局部方法。SGBM 至今仍是工业双目（RealSense、自动驾驶）的首选。

## 当时的问题是什么

在 2005 年之前，geometry 分支面临的痛点是：

```mermaid
flowchart LR
  A["现有方法"] --> B["某种痛点"]
  B --> C["新算法解决"]
```

具体到 SGM 半全局立体匹配 提出时，业界主要存在以下问题：

- 需要一种更准确的方法
- 现有方法在真实场景下鲁棒性不足
- 参数过多或者计算复杂度过高

## 核心贡献

SGM 半全局立体匹配 的主要贡献包括：

1. **提出了全新的视角**：双目测距的工业标准，8 个方向做平滑约束，又快又稳出稠密视差图
2. **设计了可落地的算法流程**：兼顾精度与效率
3. **给出了开源实现**：在 OpenCV 等库中成为标准
4. **启发了后续工作**：成为该方向的重要基准

## 与前人方法的对比

| 维度 | 之前的方法 | SGM 半全局立体匹配 |
|---|---|---|
| 速度 | 较慢/较快 | **显著改进** |
| 精度 | 中等 | **更高** |
| 鲁棒性 | 受限于条件 | **更好** |
| 易用性 | 参数多 | **更友好** |

## 对后世的影响

SGM 半全局立体匹配 至今仍是 geometry 分支中重要基准。

它启发了后续一系列改进工作，在深度学习时代仍有广泛应用。

## 相关链接

- [返回算法档案首页](/algorithms/sgbm/)
- [核心概念](/algorithms/sgbm/concepts)
- [算法流程](/algorithms/sgbm/architecture)
- [geometry 分支总览](/branches/geometry/)
