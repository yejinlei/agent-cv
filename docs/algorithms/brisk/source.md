# 源码走读：BRISK 二进制鲁棒不变可伸缩关键点

## OpenCV 最简调用

```python
import cv2
img = cv2.imread('scene.jpg', 0)

brisk = cv2.BRISK_create(thresh=30, octaves=4)
kps, des = brisk.detectAndCompute(img, None)

out = cv2.drawKeypoints(img, kps, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# 匹配
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)
matches = sorted(matches, key=lambda x: x.distance)

```

## 手写最小实现（理解原理）

```python
import numpy as np, cv2

def brisk_describe_naive(img, kp, pattern_radii, short_pairs, n_rots=36):
    """极简版 BRISK 描述子（教学用，不做亚像素插值、不做多尺度）"""
    x, y = int(kp.pt[0]), int(kp.pt[1])
    half = 25
    patch = img[max(0,y-half):y+half+1, max(0,x-half):x+half+1]
    if patch.shape[0] < 2*half+1 or patch.shape[1] < 2*half+1:
        return None

    # 简化：采样 60 个点沿 4 个圆
    pts = []
    for r in [4, 8, 13, 20]:
        for i in range(15):
            ang = i * 2 * np.pi / 15
            px = int(round(half + r * np.cos(ang)))
            py = int(round(half + r * np.sin(ang)))
            pts.append((px, py))

    # 用 dx,dy 简单估方向（跳过真正的长点对）
    gx = cv2.Sobel(patch, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(patch, cv2.CV_32F, 0, 1, ksize=3)
    ang = np.arctan2(gy[half, half], gx[half, half])
    cos_a, sin_a = np.cos(-ang), np.sin(-ang)

    # 旋转采样点
    rot_pts = []
    for (px, py) in pts:
        dx, dy = px - half, py - half
        rx = int(round(half + dx*cos_a - dy*sin_a))
        ry = int(round(half + dx*sin_a + dy*cos_a))
        rot_pts.append((rx, ry))

    # 比 512 个短点对（这里简化为前 512 对近邻）
    des = 0
    bit = 0
    for i in range(len(rot_pts)):
        for j in range(i+1, len(rot_pts)):
            if bit >= 256: break
            xi, yi = rot_pts[i]
            xj, yj = rot_pts[j]
            if 0 <= xi < patch.shape[1] and 0 <= yi < patch.shape[0] and 0 <= xj < patch.shape[1] and 0 <= yj < patch.shape[0]:
                if patch[yi, xi] < patch[yj, xj]:
                    des |= (1 << bit)
            bit += 1
    return des

```

## OpenCV 源码核心片段解读

OpenCV 的 BRISK 源码在 `modules/features2d/src/brisk.cpp`，关键结构：

- `BriskScaleSpace::constructPyramid()`：建 octave/intra-octave 金字塔
- `BriskScaleSpace::getKeypoints()`：每层跑 AGAST，通过 `AgastDetector9_16` 类
- `BriskLayer::getAgastPoints()`：调用 AGAST 决策树
- `BriskDescriptors::computeDescriptors()`：这是**核心**——它预先生成了所有 1770 对点对的采样 offset 列表（`shortPairs`/`longPairs`），方向估计和描述子生成都用同一个积分循环，非常快。

一个工程细节：OpenCV 的 BRISK 对采样点做了**整数坐标预计算**（因为旋转角度离散化为 1024 个方向，每个方向预存 60 个采样点的整数偏移），这样运行时只需要查表 + 加法就能定位像素，没有浮点插值开销。
