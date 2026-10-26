# MeanShift 均值漂移 · 核心概念

<AlgorithmCard
  name="MeanShift 均值漂移"
  enName="Mean-Shift Mode Seeking"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="1975/2002"
  author="K. Fukunaga / D. Comaniciu / P. Meer"
  paper="—"
  level="mid"
  tagline="每个点朝邻居最密的方向挪一步，最后聚成几坨——不用提前说有几坨"
  analogy="广场上站了一群人，每个人都往「周围人最密集的方向」走一步。走几步后大家会聚成几个紧密的小圈子，每个圈子就是一类"
  scene="图像平滑分割（pyrMeanShiftFiltering）、目标跟踪（CamShift）、聚类、运动目标分割"
  :pros='["无需指定聚类数", "同时考虑颜色+空间", "任意形状聚类", "对光照鲁棒"]'
  :cons='["速度很慢", "带宽 sp/sr 参数难调", "窗口大小固定", "高维不行"]'
/>

<div class="tip custom-block"><p>🧪 公式看不懂？去 <a href="/math-lab/">原理实验室</a> 拖动滑块直观体验卷积/梯度/高斯/霍夫/角点/RANSAC/光流等核心概念；看完原理再去本页底部 <a href="./source">源码/真机实验室</a> 亲手调参数。</p></div>


## MeanShift 均值漂移的核心思想

每个点朝邻居最密的方向挪一步，最后聚成几坨——不用提前说有几坨。广场上站了一群人，每个人都往「周围人最密集的方向」走一步。走几步后大家会聚成几个紧密的小圈子，每个圈子就是一类

**生活类比**：广场上站了一群人，每个人都往「周围人最密集的方向」走一步。走几步后大家会聚成几个紧密的小圈子，每个圈子就是一类

**典型应用**：图像平滑分割（pyrMeanShiftFiltering）、目标跟踪（CamShift）、聚类、运动目标分割

```mermaid
flowchart LR
  A["输入图像"] --> B["核心处理"]
  B --> C["输出结果"]
```

## 核心概念详解

### 概念1：密度梯度上升

MeanShift 的本质是**核密度估计的梯度上升**：对每个点，计算它周围窗口内所有点的加权平均位置（均值漂移向量），然后让这个点移动到均值位置——不断迭代直到收敛到局部密度峰值。所有收敛到同一峰值的点归为一类。

```mermaid
flowchart LR
  A["当前点 x"] --> B["算窗口内加权均值 m(x)"]
  B --> C["x ← m(x)"]
  C -->|"未收敛"| B
  C -->|"收敛"| D["到达密度峰值（模式）"]
```

### 概念2：空间-颜色联合空间

图像分割用的 MeanShift 在 5 维空间（x,y,L,a,b 或 x,y,R,G,B）里漂移，但空间维和颜色维的尺度不同，用两个带宽参数控制：sp 控制空间窗口半径，sr 控制颜色窗口半径。

### 概念3：金字塔加速

直接对原图像素做 MeanShift 太慢（O(N²)）。`pyrMeanShiftFiltering` 采用金字塔策略：先在小尺度图像上做漂移，然后上采样回大尺度做少量迭代精修——速度快很多。

### 概念4：MeanShift vs K-Means

K-Means 要预设 K，每个类形状倾向球状；MeanShift 不需要 K，能聚任意形状类，自动发现聚类数，但速度慢很多。

