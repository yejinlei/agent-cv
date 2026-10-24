---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import cv2

img1 = cv2.imread("scene1.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("scene2.jpg", cv2.IMREAD_GRAYSCALE)

# 1) 先检测特征点（FREAK 只做描述，不做检测）
detector = cv2.FastFeatureDetector_create(threshold=30)
kp1 = detector.detect(img1, None)
kp2 = detector.detect(img2, None)

# 2) FREAK 描述子
freak = cv2.xfeatures2d.FREAK_create(
    orientationNormalized=True,
    scaleNormalized=True,
    patternScale=22.0,
    nOctaves=4,
)
kp1, des1 = freak.compute(img1, kp1)
kp2, des2 = freak.compute(img2, kp2)

# 3) 二进制描述子 -> 汉明距离匹配
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = sorted(bf.match(des1, des2), key=lambda m: m.distance)
print("匹配数:", len(matches))
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
import numpy as np
import cv2

# 手写：用 BRIEF 近似示意「采样对 + 二进制编码」的核心思想
img = cv2.imread("scene1.jpg", cv2.IMREAD_GRAYSCALE)
detector = cv2.FastFeatureDetector_create(30)
kp = detector.detect(img, None)

rng = np.random.default_rng(42)
pairs = rng.integers(-15, 15, size=(256, 2, 2))   # 256 对采样点
descriptors = []
for k in kp:
    x, y = int(k.pt[0]), int(k.pt[1])
    if x < 20 or y < 20 or x > img.shape[1] - 20 or y > img.shape[0] - 20:
        continue
    bits = []
    for (dx1, dy1), (dx2, dy2) in pairs:
        a = img[y + dy1, x + dx1]
        b = img[y + dy2, x + dx2]
        bits.append(1 if a > b else 0)
    descriptors.append(bits)

descriptors = np.array(descriptors, np.uint8)
print("描述子矩阵:", descriptors.shape)  # (N, 256)
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| patternScale | 采样模式缩放比例 | **22.0** |
| orientationNormalized | 是否做方向归一 | **True** |
| scaleNormalized | 是否做尺度归一 | **True** |
| nOctaves | 金字塔层数 | **4** |

::: tip 工程实现说明
FREAK 是描述子不是检测器，必须先用 FAST/AGAST/ORB 等检测关键点；匹配一律用 NORM_HAMMING。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
