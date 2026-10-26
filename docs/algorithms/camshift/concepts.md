# CamShift 连续自适应 MeanShift · 核心概念

<AlgorithmCard
  name="CamShift 连续自适应 MeanShift"
  enName="Continuously Adaptive Mean-Shift"
  chapter="ch-11-object-detection"
  branch="detection"
  year="1998"
  author="Gary Bradski"
  paper="—"
  level="mid"
  tagline="MeanShift 的视频版——窗口大小自动跟着目标变，肤色跟踪的经典算法"
  analogy="MeanShift 像用放大镜盯跳蚤，大小不变；CamShift 像自适应聚光灯，跳蚤跳近光圈小、跳远光圈大，始终把跳蚤照亮在中间"
  scene="实时人脸/人手跟踪、肤色目标跟踪、视频会议人脸锁定、简单无模型跟踪、HCI 手势交互"
  :pros='["实现简单", "自适应窗口大小", "速度快", "非刚体变形容忍", "无需训练"]'
  :cons='["需初始化ROI", "同色背景易漂移", "光照敏感", "快速运动易丢", "只能跟踪颜色显著目标"]'
/>

<div class="tip custom-block"><p>🧪 公式看不懂？去 <a href="/math-lab/">原理实验室</a> 拖动滑块直观体验卷积/梯度/高斯/霍夫/角点/RANSAC/光流等核心概念；看完原理再去本页底部 <a href="./source">源码/真机实验室</a> 亲手调参数。</p></div>


## CamShift 连续自适应 MeanShift的核心思想

MeanShift 的视频版——窗口大小自动跟着目标变，肤色跟踪的经典算法。MeanShift 像用放大镜盯跳蚤，大小不变；CamShift 像自适应聚光灯，跳蚤跳近光圈小、跳远光圈大，始终把跳蚤照亮在中间

**生活类比**：MeanShift 像用放大镜盯跳蚤，大小不变；CamShift 像自适应聚光灯，跳蚤跳近光圈小、跳远光圈大，始终把跳蚤照亮在中间

**典型应用**：实时人脸/人手跟踪、肤色目标跟踪、视频会议人脸锁定、简单无模型跟踪、HCI 手势交互

```mermaid
flowchart LR
  A["输入图像"] --> B["核心处理"]
  B --> C["输出结果"]
```

## 核心概念详解

### 概念1：反向投影图 Back Projection

先算目标 ROI 的颜色直方图（通常在 HSV 的 H 通道，即色调直方图），然后把整张图的每个像素替换为「它的颜色在目标直方图中出现的概率」——得到的就是反向投影图（越亮的像素越像目标颜色）。

```mermaid
flowchart LR
  A["ROI 目标区域"] --> B["H 通道直方图"]
  C["全图"] --> D["反向投影<br/>像素=该颜色的概率"]
  B --> D
```

### 概念2：MeanShift 找峰值

在反向投影图上，从初始窗口位置开始：① 算窗口内质心（0阶矩+1阶矩）；② 把窗口中心移到质心；③ 重复直到中心移动 < ε，收敛到密度峰值。

### 概念3：CamShift 自适应

CamShift = 先跑 MeanShift 收敛，再根据窗口内 0/1/2 阶矩计算目标的新位置、大小和方向，把窗口更新为匹配目标的椭圆；然后下一帧用新窗口作为初始继续。

### 概念4：颜色空间选择

用 HSV 的 H 通道（色调）做直方图，能部分抵抗光照变化（V 亮度不影响 H）。但要注意排除低饱和度像素（S 太小 H 不稳定）。

