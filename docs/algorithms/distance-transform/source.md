# 源码走读：距离变换

## OpenCV 最简调用

```python
import cv2, numpy as np
img = cv2.imread('binary.png', 0)
_, bw = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

# 距离变换（L2，5×5 mask）
dist = cv2.distanceTransform(bw, cv2.DIST_L2, 5)
cv2.normalize(dist, dist, 0, 1.0, cv2.NORM_MINMAX)

# 带标签（用于分水岭种子）
dist, labels = cv2.distanceTransform(bw, cv2.DIST_L2, 5, cv2.DIST_LABEL_CCOMP)

```

## 手写最小实现（理解原理）

```python
import numpy as np, cv2

def dt_l1(binary):
    """极简 L1 距离变换（两次扫描，教学用）"""
    h, w = binary.shape
    INF = w + h
    D = np.where(binary > 0, INF, 0).astype(np.int32)

    # Forward
    for y in range(1, h):
        for x in range(1, w):
            D[y, x] = min(D[y, x], D[y-1, x]+1, D[y, x-1]+1, D[y-1, x-1]+2)
    for y in range(1, h):
        for x in range(w-2, -1, -1):
            D[y, x] = min(D[y, x], D[y-1, x+1]+2)

    # Backward
    for y in range(h-2, -1, -1):
        for x in range(w-2, -1, -1):
            D[y, x] = min(D[y, x], D[y+1, x]+1, D[y, x+1]+1, D[y+1, x+1]+2)
    for y in range(h-2, -1, -1):
        for x in range(1, w):
            D[y, x] = min(D[y, x], D[y+1, x-1]+2)
    return D

```

## OpenCV 源码核心片段解读

OpenCV `distanceTransform` 在 `modules/imgproc/src/distransform.cpp`：

- `cv::distTransform()` 入口，先判断 distanceType / maskSize
- L1/L2/C 分别走不同的特化：
  - `DTL1Body`：8 邻域 L1，简单 int 版本
  - `DTOperator_3x3` / `DTOperator_5x5`：Chamfer 距离（模板权重数组）
  - `DistTransform::operator()`：Danielsson 8SED 精确欧氏距离，维护 (dx,dy) 向量而不是标量
- 全部用 `parallel_for_` 分块并行
- 一个有意思的细节：Danielsson 算法不是简单的"两次扫描就完事"，它对边角误差有 4 次扫描的修正版本（OpenCV 用了 8 扫描的更稳定实现）
