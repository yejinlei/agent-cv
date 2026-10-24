---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import cv2
import numpy as np

img1 = cv2.imread("a.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("b.jpg", cv2.IMREAD_GRAYSCALE)

sift = cv2.SIFT_create()
kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

# SIFT 是浮点描述子 -> KD-Tree 索引
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)         # 越大越准越慢

flann = cv2.FlannBasedMatcher(index_params, search_params)
knn = flann.knnMatch(des1, des2, k=2)

# Lowe 比率测试
good = []
for m, n in knn:
    if m.distance < 0.75 * n.distance:
        good.append(m)
print("原始匹配:", len(knn), "-> 优质匹配:", len(good))

# 用 RANSAC 进一步剔除几何外点
if len(good) >= 4:
    src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    print("内点数:", int(mask.sum()))
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
import cv2
import numpy as np

# ORB 是二进制描述子 -> 必须用 LSH 索引
img1 = cv2.imread("a.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("b.jpg", cv2.IMREAD_GRAYSCALE)

orb = cv2.ORB_create(2000)
kp1, des1 = orb.detectAndCompute(img1, None)
kp2, des2 = orb.detectAndCompute(img2, None)

FLANN_INDEX_LSH = 6
index_params = dict(
    algorithm=FLANN_INDEX_LSH,
    table_number=12,
    key_size=20,
    multi_probe_level=2,
)
search_params = dict(checks=50)

flann = cv2.FlannBasedMatcher(index_params, search_params)
knn = flann.knnMatch(des1, des2, k=2)
good = [m for m, n in knn if m.distance < 0.8 * n.distance]
print("ORB + LSH 优质匹配:", len(good))
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| trees | KD-Tree 数量 | **5** |
| checks | 搜索节点上限 | **50** |
| table_number | LSH 哈希表数 | **12** |
| k | knnMatch 的 k | **2（做比率测试）** |

::: tip 工程实现说明
浮点描述子（SIFT/SURF）用 FLANN_INDEX_KDTREE；二进制描述子（ORB/BRIEF/BRISK）必须用 FLANN_INDEX_LSH，否则匹配质量极差。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
