# Horn-Schunck 稠密光流 · 论文故事

<AlgorithmCard
  name="Horn-Schunck 稠密光流"
  enName="Horn-Schunck Optical Flow"
  chapter="ch-13-motion-analysis"
  branch="geometry"
  year="1981"
  author="Berthold K.P. Horn / Brian G. Schunck"
  paper="paper-horn-schunck-1981"
  level="advanced"
  tagline="给光流加上全局平滑约束，用变分法求每个像素的运动，开创稠密光流学派"
  analogy="LK 光流像一个独立办案的刑警，每个小窗口自己算自己的；Horn-Schunck 像一个总指挥，要求所有像素的运动方向「差不多」，不能突然跳变，然后全局求解出一幅密密麻麻的运动箭头图"
  scene="稠密运动场估计、流体运动分析、医学影像序列分析、变分光流研究基准、视频慢动作插帧（传统方法）"
  :pros='["输出稠密光流（每像素都有）", "全局一致，平滑无噪", "开创变分光流学派", "理论优美（能量最小化）", "作为基准方法"]'
  :cons='["迭代求解较慢", "对大运动不适用（需金字塔）", "运动边界处过度平滑", "亮度恒定假设苛刻", "工程上 Farnebäck/DIS 更常用"]'
/>

## 发表信息

| 项 | 内容 |
|---|---|
| **论文名** | 根据算法不同见原论文 |
| **作者** | Berthold K.P. Horn / Brian G. Schunck |
| **发表年份** | 1981 |
| **机构** | 计算机视觉经典工作 |
| **引用数** | 数千到数万次（经典工作） |

## 论文背后的故事

Berthold Horn 是 MIT CSAIL 的教授（MIT 开放式课程《Machine Vision》的作者），Brian Schunck 是他的博士生。1981 年两人在《Determining Optical Flow》一文中首次给光流问题建立了严谨的变分框架：定义一个能量函数 = 亮度恒定误差 + 流场平滑正则项，然后用欧拉-拉格朗日方程迭代求解。这篇论文开创了「变分光流」学派，后来的 TV-L1、Classic+NL 甚至深度学习前最好的光流算法，都沿用了 H-S 开创的「数据项+正则项」框架。

## 当时的问题是什么

在 1981 年之前，geometry 分支面临的痛点是：

```mermaid
flowchart LR
  A["现有方法"] --> B["某种痛点"]
  B --> C["新算法解决"]
```

具体到 Horn-Schunck 稠密光流 提出时，业界主要存在以下问题：

- 需要一种更准确的方法
- 现有方法在真实场景下鲁棒性不足
- 参数过多或者计算复杂度过高

## 核心贡献

Horn-Schunck 稠密光流 的主要贡献包括：

1. **提出了全新的视角**：给光流加上全局平滑约束，用变分法求每个像素的运动，开创稠密光流学派
2. **设计了可落地的算法流程**：兼顾精度与效率
3. **给出了开源实现**：在 OpenCV 等库中成为标准
4. **启发了后续工作**：成为该方向的重要基准

## 与前人方法的对比

| 维度 | 之前的方法 | Horn-Schunck 稠密光流 |
|---|---|---|
| 速度 | 较慢/较快 | **显著改进** |
| 精度 | 中等 | **更高** |
| 鲁棒性 | 受限于条件 | **更好** |
| 易用性 | 参数多 | **更友好** |

## 对后世的影响

Horn-Schunck 稠密光流 至今仍是 geometry 分支中重要基准。

它启发了后续一系列改进工作，在深度学习时代仍有广泛应用。

## 相关链接

- [返回算法档案首页](/algorithms/horn-schunck/)
- [核心概念](/algorithms/horn-schunck/concepts)
- [算法流程](/algorithms/horn-schunck/architecture)
- [geometry 分支总览](/branches/geometry/)
