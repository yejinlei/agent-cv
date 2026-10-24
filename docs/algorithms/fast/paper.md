# FAST 角点检测 · 论文故事

<AlgorithmCard
  name="FAST 角点检测"
  enName="Features from Accelerated Segment Test"
  chapter="ch-8-local-feature"
  branch="feature-detection"
  year="2006"
  author="Edward Rosten / Tom Drummond"
  paper="—"
  level="mid"
  tagline="用一个圆圈 16 个邻居，一眼认出角点，速度比 Harris 快 10 倍"
  analogy="FAST 像一个哨兵：不进屋检查，只趴在窗户上数——窗外 16 个邻居里如果连续 12 个都比屋里亮或都比屋里暗，那这间房肯定是个「犄角旮旯」"
  scene="SLAM、AR、实时物体识别里做特征点检测，毫秒级返回几千个点，CPU 上就能跑 60fps"
  :pros='["速度极快（比 Harris 快 10 倍以上）", "实现简单，一个 for 循环就够", "角点重复率高", "OpenCV 高度优化"]'
  :cons='["不具备尺度不变性", "不具备旋转不变性（后来 ORB 加上了）", "阈值敏感，噪声点多", "需要搭配 NMS 避免扎堆", "不含描述子，必须另配 BRIEF/ORB"]'
/>

## 发表信息

| 项 | 内容 |
|---|---|
| **论文名** | 根据算法不同见原论文 |
| **作者** | Edward Rosten / Tom Drummond |
| **发表年份** | 2006 |
| **机构** | 计算机视觉经典工作 |
| **引用数** | 数千到数万次（经典工作） |

## 论文背后的故事

Edward Rosten 是剑桥大学 Tom Drummond 实验室的博士生，当时他们在做实时 SLAM，发现 Harris 角点检测在 ARM 嵌入式上根本跑不起来。Rosten 想：「不就是判断一个点周围是不是比它亮或暗吗，我用机器学习把决策树学出来不就快了？」于是他用 ID3 算法在标准数据集上训练了一棵决策树，把判断一个像素是不是角点从几十次比较压缩到平均 3 次比较。FAST 由此诞生，速度比当时所有角点检测器快一个数量级，成为 PTAM、ORB-SLAM 等实时系统的基石。

## 当时的问题是什么

在 2006 年之前，feature-detection 分支面临的痛点是：

```mermaid
flowchart LR
  A["现有方法"] --> B["某种痛点"]
  B --> C["新算法解决"]
```

具体到 FAST 角点检测 提出时，业界主要存在以下问题：

- 需要一种更快的方法
- 现有方法在真实场景下鲁棒性不足
- 参数过多或者计算复杂度过高

## 核心贡献

FAST 角点检测 的主要贡献包括：

1. **提出了全新的视角**：用一个圆圈 16 个邻居，一眼认出角点，速度比 Harris 快 10 倍
2. **设计了可落地的算法流程**：兼顾精度与效率
3. **给出了开源实现**：在 OpenCV 等库中成为标准
4. **启发了后续工作**：成为该方向的重要基准

## 与前人方法的对比

| 维度 | 之前的方法 | FAST 角点检测 |
|---|---|---|
| 速度 | 较慢/较快 | **显著改进** |
| 精度 | 中等 | **更高** |
| 鲁棒性 | 受限于条件 | **更好** |
| 易用性 | 参数多 | **更友好** |

## 对后世的影响

FAST 角点检测 至今仍是 feature-detection 分支中工业标准。

它启发了后续一系列改进工作，在深度学习时代仍有广泛应用。

## 相关链接

- [返回算法档案首页](/algorithms/fast/)
- [核心概念](/algorithms/fast/concepts)
- [算法流程](/algorithms/fast/architecture)
- [feature-detection 分支总览](/branches/feature-detection/)
