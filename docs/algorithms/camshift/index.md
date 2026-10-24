# CamShift 连续自适应 MeanShift

<AlgorithmCard
  name="CamShift 连续自适应 MeanShift"
  enName="Continuously Adaptive Mean-Shift"
  chapter="第11章 · 运动分析"  chapterLink="/chapters/ch11-motion"
  branch="detection"
  year="1998"
  author="Gary Bradski"
  paper="https://www.researchgate.net/publication/2454644_Computer_Face_Perception_for_Perceptual_User_Interfaces"
  level="mid"
  tagline="MeanShift 的视频版——窗口大小自动跟着目标变，肤色跟踪的经典算法"
  analogy="MeanShift 像用放大镜盯着一个跳蚤看，跳蚤挪一点你挪一点放大镜，但放大镜大小不变；CamShift 像个自适应的聚光灯，跳蚤跳近你就把光圈缩小、跳蚤跳远你就放大，始终把跳蚤照亮在中间"
  scene="实时人脸/人手跟踪、肤色目标跟踪、视频会议人脸锁定、简单无模型目标跟踪、HCI 手势交互"
  :pros='["实现简单", "自动适应窗口大小和方向", "速度快", "对非刚体变形容忍", "无需训练模型"]'
  :cons='["需要初始化（ROI 框）", "背景有同色物体易漂移", "对光照敏感", "快速运动容易跟丢", "只能跟踪颜色分布显著的目标"]'
/>

## 一句话理解

MeanShift 的视频版——窗口大小自动跟着目标变，肤色跟踪的经典算法。MeanShift 像用放大镜盯着一个跳蚤看，跳蚤挪一点你挪一点放大镜，但放大镜大小不变；CamShift 像个自适应的聚光灯，跳蚤跳近你就把光圈缩小、跳蚤跳远你就放大，始终把跳蚤照亮在中间。

```mermaid
flowchart LR
  A["输入图像"] --> B["CamShift 连续自适应 MeanShift"]
  B --> C["输出结果"]
```

## 生活类比

MeanShift 像用放大镜盯着一个跳蚤看，跳蚤挪一点你挪一点放大镜，但放大镜大小不变；CamShift 像个自适应的聚光灯，跳蚤跳近你就把光圈缩小、跳蚤跳远你就放大，始终把跳蚤照亮在中间

## 它解决什么问题

实时人脸/人手跟踪、肤色目标跟踪、视频会议人脸锁定、简单无模型目标跟踪、HCI 手势交互。

在传统 CV 的六分支体系中，CamShift 连续自适应 MeanShift 属于 **detection** 分支，主要解决的是该分支中MeanShift 的视频版——窗口大小自动跟着目标变，肤色跟踪的经典算法的问题。

## 核心优点

- ✅ **实现简单**
- ✅ **自动适应窗口大小和方向**
- ✅ **速度快**
- ✅ **对非刚体变形容忍**
- ✅ **无需训练模型**

## 它的短板

- ⚠️ 需要初始化（ROI 框）
- ⚠️ 背景有同色物体易漂移
- ⚠️ 对光照敏感
- ⚠️ 快速运动容易跟丢
- ⚠️ 只能跟踪颜色分布显著的目标

## 本算法档案包含 7 个页面

| 页面 | 内容 |
|---|---|
| [论文故事](/algorithms/camshift/paper) | 作者、发表时间、核心贡献、为什么它会被提出 |
| [核心概念](/algorithms/camshift/concepts) | 用生活比方讲清它依赖的关键概念 |
| [算法流程](/algorithms/camshift/architecture) | 一步步走通算法全流程，配 mermaid 图 |
| [源码实现](/algorithms/camshift/source) | OpenCV 调用 + NumPy 手写最小实现 |
| [踩坑清单](/algorithms/camshift/painpoints) | 新手最常犯的 N 个错误 |
| [调参口诀](/algorithms/camshift/tricks) | 参数怎么选、实战技巧、性能优化 |

## 相关链接

- 返回 [六大分支总览](/branches/)
- [CamShift 连续自适应 MeanShift所在分支](/branches/detection/)
- [算法档案总览](/algorithms/)
