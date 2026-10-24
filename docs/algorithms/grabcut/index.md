# GrabCut 抠图

<AlgorithmCard
  name="GrabCut 抠图"
  enName="GrabCut Interactive Foreground Extraction"
  chapter="第5章 · 目标分割"  chapterLink="/chapters/ch05-segmentation"
  branch="segmentation"
  year="2004"
  author="Carsten Rother / Vladimir Kolmogorov / Andrew Blake"
  paper="https://dl.acm.org/doi/10.1145/1015706.1015720"
  level="mid"
  tagline="画一个框就能把目标抠出来，GMM+GraphCut 迭代优化，Photoshop 快速选择的灵魂"
  analogy="你用笔在目标周围画个圈，对算法说「圈外肯定是背景，圈内有前景也有背景」。GrabCut 就像一个聪明的学徒，先猜哪些颜色像前景、哪些像背景，然后用 GraphCut 切一刀，再根据结果重新学颜色模型，反复 5 次就抠得干干净净"
  scene="照片抠图换背景、数据集快速标注、医学影像交互式分割、人像美颜前景提取"
  :pros='["用户只需画一个框即可", "边缘细节比 GraphCut 好", "支持笔刷精修", "GMM 建模多峰颜色分布", "迭代自动优化"]'
  :cons='["高分辨率慢（1080p 约 5s）", "前景背景颜色接近时效果差", "矩形外永远是背景", "边缘毛发处理需 alpha matting", "bgdModel/fgdModel 容易填错"]'
/>

## 一句话理解

画一个框就能把目标抠出来，GMM+GraphCut 迭代优化，Photoshop 快速选择的灵魂。你用笔在目标周围画个圈，对算法说「圈外肯定是背景，圈内有前景也有背景」。GrabCut 就像一个聪明的学徒，先猜哪些颜色像前景、哪些像背景，然后用 GraphCut 切一刀，再根据结果重新学颜色模型，反复 5 次就抠得干干净净。

```mermaid
flowchart LR
  A["输入图像"] --> B["GrabCut 抠图"]
  B --> C["输出结果"]
```

## 生活类比

你用笔在目标周围画个圈，对算法说「圈外肯定是背景，圈内有前景也有背景」。GrabCut 就像一个聪明的学徒，先猜哪些颜色像前景、哪些像背景，然后用 GraphCut 切一刀，再根据结果重新学颜色模型，反复 5 次就抠得干干净净

## 它解决什么问题

照片抠图换背景、数据集快速标注、医学影像交互式分割、人像美颜前景提取。

在传统 CV 的六分支体系中，GrabCut 抠图 属于 **segmentation** 分支，主要解决的是该分支中画一个框就能把目标抠出来，GMM+GraphCut 迭代优化，Photoshop 快速选择的灵魂的问题。

## 核心优点

- ✅ **用户只需画一个框即可**
- ✅ **边缘细节比 GraphCut 好**
- ✅ **支持笔刷精修**
- ✅ **GMM 建模多峰颜色分布**
- ✅ **迭代自动优化**

## 它的短板

- ⚠️ 高分辨率慢（1080p 约 5s）
- ⚠️ 前景背景颜色接近时效果差
- ⚠️ 矩形外永远是背景
- ⚠️ 边缘毛发处理需 alpha matting
- ⚠️ bgdModel/fgdModel 容易填错

## 本算法档案包含 7 个页面

| 页面 | 内容 |
|---|---|
| [论文故事](/algorithms/grabcut/paper) | 作者、发表时间、核心贡献、为什么它会被提出 |
| [核心概念](/algorithms/grabcut/concepts) | 用生活比方讲清它依赖的关键概念 |
| [算法流程](/algorithms/grabcut/architecture) | 一步步走通算法全流程，配 mermaid 图 |
| [源码实现](/algorithms/grabcut/source) | OpenCV 调用 + NumPy 手写最小实现 |
| [踩坑清单](/algorithms/grabcut/painpoints) | 新手最常犯的 N 个错误 |
| [调参口诀](/algorithms/grabcut/tricks) | 参数怎么选、实战技巧、性能优化 |

## 相关链接

- 返回 [六大分支总览](/branches/)
- [GrabCut 抠图所在分支](/branches/segmentation/)
- [算法档案总览](/algorithms/)
