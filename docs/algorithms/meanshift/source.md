# MeanShift 均值漂移 · 源码实现

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

## OpenCV 调用方法

MeanShift 均值漂移在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

img = cv2.imread("scene.jpg")
# MeanShift 滤波（颜色平滑+分割）
shifted = cv2.pyrMeanShiftFiltering(
    img,
    sp=15,      # 空间窗口半径
    sr=30,      # 颜色窗口半径
    maxLevel=1
)
# 再做一次连通域合并
gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
n, labels, stats, _ = cv2.connectedComponentsWithStats(thresh)
print(f"MeanShift 后共 {n-1} 个连通区域")
cv2.imwrite("meanshift.jpg", shifted)
```

### 关键参数说明

| 参数 | 含义 | 建议值 |
|---|---|---|
| （见各算法具体参数表） | — | — |

## NumPy 手写最小实现

下面写一个简化版的实现，帮助理解原理（性能远不如 OpenCV，仅用于教学）：

```python
import numpy as np
import cv2

def meanshift_vectorized(points, bandwidth, max_iter=20, tol=1e-3):
    """点集上的 MeanShift 聚类（演示用）"""
    X = points.astype(np.float32)
    for _ in range(max_iter):
        new_X = np.zeros_like(X)
        for i, x in enumerate(X):
            # 找带宽内的邻居
            dists = np.linalg.norm(X - x, axis=1)
            neighbors = X[dists < bandwidth]
            if len(neighbors) == 0:
                new_X[i] = x
                continue
            # 高斯核加权
            w = np.exp(-0.5 * (dists[dists<bandwidth]/bandwidth)**2)
            new_X[i] = (neighbors * w[:,None]).sum(0) / w.sum()
        if np.linalg.norm(new_X - X) < tol:
            break
        X = new_X
    return X
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

