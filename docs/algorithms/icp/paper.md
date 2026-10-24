# ICP 迭代最近点 · 论文故事

<AlgorithmCard
  name="ICP 迭代最近点"
  enName="Iterative Closest Point"
  chapter="ch-14-3d-vision"
  branch="geometry"
  year="1992"
  author="Paul Besl / Neil McKay (同时 Chen&Medioni 独立提出)"
  paper="—"
  level="advanced"
  tagline="两片点云拼起来的经典算法：找最近点配对，算刚体变换，反复迭代到对齐"
  analogy="你拿着两张被撕碎的地图碎片，每次都把一片上每个点在另一片上找最近的对应点，计算平移旋转让它们靠近一点，再重新找对应点……反复几十次，两片就严丝合缝地拼在一起了"
  scene="激光雷达点云配准、三维重建、机器人定位（LiDAR SLAM）、多视角点云融合、医学影像配准"
  :pros='["思想简单直观", "任何维度都适用（2D/3D）", "无需特征提取（直接用点坐标）", "Open3D/PCL 都有高效实现", "收敛保证（局部）"]'
  :cons='["需要初始位姿（否则容易局部最优）", "对动态物体/离群点敏感", "原始 O(N²) 慢（要 KD-Tree 加速）", "两片点云重叠率要够", "点到点版本精度不如点到面"]'
/>

## 发表信息

| 项 | 内容 |
|---|---|
| **论文名** | 根据算法不同见原论文 |
| **作者** | Paul Besl / Neil McKay (同时 Chen&Medioni 独立提出) |
| **发表年份** | 1992 |
| **机构** | 计算机视觉经典工作 |
| **引用数** | 数千到数万次（经典工作） |

## 论文背后的故事

1992 年是点云配准的元年——两个研究组独立提出了几乎一样的算法：IBM TJ Watson 研究中心的 Paul Besl 和 Neil McKay 在 PAMI 上发表了《A Method for Registration of 3-D Shapes》；USC 的 Yang Chen 和 Gérard Medioni 在图像理解研讨会上发表了类似的工作。Besl 的版本被引用最多，命名为 ICP（Iterative Closest Point）。当时 3D 扫描设备开始普及，如何把不同视角的扫描数据自动拼起来是个刚需。ICP 虽然简单，却意外地有效——至今仍是 LiDAR SLAM（如 LOAM）和 KinectFusion 的核心模块。

## 当时的问题是什么

在 1992 年之前，geometry 分支面临的痛点是：

```mermaid
flowchart LR
  A["现有方法"] --> B["某种痛点"]
  B --> C["新算法解决"]
```

具体到 ICP 迭代最近点 提出时，业界主要存在以下问题：

- 需要一种更准确的方法
- 现有方法在真实场景下鲁棒性不足
- 参数过多或者计算复杂度过高

## 核心贡献

ICP 迭代最近点 的主要贡献包括：

1. **提出了全新的视角**：两片点云拼起来的经典算法：找最近点配对，算刚体变换，反复迭代到对齐
2. **设计了可落地的算法流程**：兼顾精度与效率
3. **给出了开源实现**：在 OpenCV 等库中成为标准
4. **启发了后续工作**：成为该方向的重要基准

## 与前人方法的对比

| 维度 | 之前的方法 | ICP 迭代最近点 |
|---|---|---|
| 速度 | 较慢/较快 | **显著改进** |
| 精度 | 中等 | **更高** |
| 鲁棒性 | 受限于条件 | **更好** |
| 易用性 | 参数多 | **更友好** |

## 对后世的影响

ICP 迭代最近点 至今仍是 geometry 分支中重要基准。

它启发了后续一系列改进工作，在深度学习时代仍有广泛应用。

## 相关链接

- [返回算法档案首页](/algorithms/icp/)
- [核心概念](/algorithms/icp/concepts)
- [算法流程](/algorithms/icp/architecture)
- [geometry 分支总览](/branches/geometry/)
