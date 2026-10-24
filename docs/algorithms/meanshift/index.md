# MeanShift 均值漂移

<AlgorithmCard
  name="MeanShift 均值漂移"
  enName="Mean-Shift Mode Seeking"
  chapter="第5章 · 目标分割"  chapterLink="/chapters/ch05-segmentation"
  branch="segmentation"
  year="1975 (Fukunaga) / 2002 (Comaniciu 应用到视觉)"
  author="K. Fukunaga / L. Hostetler / Dorin Comaniciu / Peter Meer"
  paper="https://ieeexplore.ieee.org/document/1000236"
  level="mid"
  tagline="每个点朝邻居最密的方向挪一步，最后聚成几坨——不用提前说有几坨"
  analogy="广场上站了一群人，每个人都往「周围人最密集的方向」走一步。走几步后大家会聚成几个紧密的小圈子，每个圈子就是一类。你不需要提前告诉大家「分成几队」，人自己会扎堆"
  scene="图像平滑分割（pyrMeanShiftFiltering）、目标跟踪（CamShift）、聚类、视频中运动目标分割"
  :pros='["不需要指定聚类数", "同时考虑颜色+空间", "任意形状聚类", "对光照渐变鲁棒", "理论优雅"]'
  :cons='["速度很慢（1080p 几秒）", "带宽 sp/sr 参数难调", "窗口大小固定", "对高维数据不行", "OpenCV 只提供滤波版"]'
/>

## 一句话理解

每个点朝邻居最密的方向挪一步，最后聚成几坨——不用提前说有几坨。广场上站了一群人，每个人都往「周围人最密集的方向」走一步。走几步后大家会聚成几个紧密的小圈子，每个圈子就是一类。你不需要提前告诉大家「分成几队」，人自己会扎堆。

```mermaid
flowchart LR
  A["输入图像"] --> B["MeanShift 均值漂移"]
  B --> C["输出结果"]
```

## 生活类比

广场上站了一群人，每个人都往「周围人最密集的方向」走一步。走几步后大家会聚成几个紧密的小圈子，每个圈子就是一类。你不需要提前告诉大家「分成几队」，人自己会扎堆

## 它解决什么问题

图像平滑分割（pyrMeanShiftFiltering）、目标跟踪（CamShift）、聚类、视频中运动目标分割。

在传统 CV 的六分支体系中，MeanShift 均值漂移 属于 **segmentation** 分支，主要解决的是该分支中每个点朝邻居最密的方向挪一步，最后聚成几坨——不用提前说有几坨的问题。

## 核心优点

- ✅ **不需要指定聚类数**
- ✅ **同时考虑颜色+空间**
- ✅ **任意形状聚类**
- ✅ **对光照渐变鲁棒**
- ✅ **理论优雅**

## 它的短板

- ⚠️ 速度很慢（1080p 几秒）
- ⚠️ 带宽 sp/sr 参数难调
- ⚠️ 窗口大小固定
- ⚠️ 对高维数据不行
- ⚠️ OpenCV 只提供滤波版

## 本算法档案包含 7 个页面

| 页面 | 内容 |
|---|---|
| [论文故事](/algorithms/meanshift/paper) | 作者、发表时间、核心贡献、为什么它会被提出 |
| [核心概念](/algorithms/meanshift/concepts) | 用生活比方讲清它依赖的关键概念 |
| [算法流程](/algorithms/meanshift/architecture) | 一步步走通算法全流程，配 mermaid 图 |
| [源码实现](/algorithms/meanshift/source) | OpenCV 调用 + NumPy 手写最小实现 |
| [踩坑清单](/algorithms/meanshift/painpoints) | 新手最常犯的 N 个错误 |
| [调参口诀](/algorithms/meanshift/tricks) | 参数怎么选、实战技巧、性能优化 |

## 相关链接

- 返回 [六大分支总览](/branches/)
- [MeanShift 均值漂移所在分支](/branches/segmentation/)
- [算法档案总览](/algorithms/)
