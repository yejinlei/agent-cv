# PnP 位姿估计 · 论文故事

<AlgorithmCard
  name="PnP 位姿估计"
  enName="Perspective-n-Point"
  chapter="ch-14-3d-vision"
  branch="geometry"
  year="1841 (Grunert P3P) / 2009 (EPnP)"
  author="Grunert / Fischler / Quan&Lan / Vincent Lepetit (EPnP)"
  paper="—"
  level="advanced"
  tagline="已知几个 3D 点和它们在图上的位置，反推出相机在哪里看——AR 和机器人抓取的基石"
  analogy="你站在房间里，认出了墙上的钟、桌子上的杯子、书架顶上的花盆——这三个东西真实位置你知道（比如钟挂在门正上方 2.2 米），你就能反推出你自己站在房间的什么地方、朝什么方向看。PnP 就是这个「看几个地标定位自己」的算法"
  scene="AR 标记跟踪、机械臂抓取、视觉伺服、无人机着陆、增强现实虚拟物体叠加、SLAM 位姿求解"
  :pros='["最少 3 个点就能解（P3P）", "一次 solvePnP 毫秒级", "RANSAC 版本鲁棒", "OpenCV 内置（P3P/EPnP/ITERATIVE/DLS）", "精度高"]'
  :cons='["需要已知内参 K", "3D 点精度要高（依赖标定）", "点共面/共线时退化", "对匹配外点敏感（需 RANSAC）", "输出的 t 与 3D 点单位一致，易出错"]'
/>

## 发表信息

| 项 | 内容 |
|---|---|
| **论文名** | 根据算法不同见原论文 |
| **作者** | Grunert / Fischler / Quan&Lan / Vincent Lepetit (EPnP) |
| **发表年份** | 1841 (Grunert P3P) / 2009 (EPnP) |
| **机构** | 计算机视觉经典工作 |
| **引用数** | 数千到数万次（经典工作） |

## 论文背后的故事

PnP 是摄影测量学的经典问题，最早可以追溯到 1841 年德国数学家 Grunert 提出的 P3P 解法（3 点 4 解）。1981 年 Fischler 和 Bolles（就是 RANSAC 那两位）在《Random Sample Consensus》一文中重新系统总结了 P3P。2009 年 Vincent Lepetit（后来 BRIEF 那位）提出 EPnP——把 3D 点表示为 4 个虚拟控制点的加权组合，把复杂度降到 O(n)，成为现代最常用的 PnP 解法。PnP 是 AR 和机器人的几何基石：你看到标记上的 4 个角点，就能立刻算出「相机相对于标记的 6DoF 位姿」。

## 当时的问题是什么

在 1841 (Grunert P3P) / 2009 (EPnP) 年之前，geometry 分支面临的痛点是：

```mermaid
flowchart LR
  A["现有方法"] --> B["某种痛点"]
  B --> C["新算法解决"]
```

具体到 PnP 位姿估计 提出时，业界主要存在以下问题：

- 需要一种更准确的方法
- 现有方法在真实场景下鲁棒性不足
- 参数过多或者计算复杂度过高

## 核心贡献

PnP 位姿估计 的主要贡献包括：

1. **提出了全新的视角**：已知几个 3D 点和它们在图上的位置，反推出相机在哪里看——AR 和机器人抓取的基石
2. **设计了可落地的算法流程**：兼顾精度与效率
3. **给出了开源实现**：在 OpenCV 等库中成为标准
4. **启发了后续工作**：成为该方向的重要基准

## 与前人方法的对比

| 维度 | 之前的方法 | PnP 位姿估计 |
|---|---|---|
| 速度 | 较慢/较快 | **显著改进** |
| 精度 | 中等 | **更高** |
| 鲁棒性 | 受限于条件 | **更好** |
| 易用性 | 参数多 | **更友好** |

## 对后世的影响

PnP 位姿估计 至今仍是 geometry 分支中重要基准。

它启发了后续一系列改进工作，在深度学习时代仍有广泛应用。

## 相关链接

- [返回算法档案首页](/algorithms/pnpsolver/)
- [核心概念](/algorithms/pnpsolver/concepts)
- [算法流程](/algorithms/pnpsolver/architecture)
- [geometry 分支总览](/branches/geometry/)
