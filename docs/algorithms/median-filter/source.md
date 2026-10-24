---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import cv2

img = cv2.imread("noisy.jpg")

# ksize 必须是大于 1 的奇数
clean = cv2.medianBlur(img, 3)      # 3x3，轻度
strong = cv2.medianBlur(img, 5)     # 5x5，重度椒盐

cv2.imwrite("median3.png", clean)
cv2.imwrite("median5.png", strong)
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
import numpy as np
import cv2


def my_median_blur(img, ksize):
    """手写中值滤波（灰度图）。"""
    pad = ksize // 2
    padded = np.pad(img, pad, mode="edge")
    h, w = img.shape
    out = np.zeros_like(img)
    for y in range(h):
        for x in range(w):
            window = padded[y:y + ksize, x:x + ksize]
            out[y, x] = np.median(window)
    return out.astype(np.uint8)


img = cv2.imread("noisy.jpg", cv2.IMREAD_GRAYSCALE)
clean = my_median_blur(img, 3)
print(clean.shape)
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| ksize | 邻域窗口边长（奇数>1） | **3** |
| img | 输入图像 | **8 位单通道或三通道** |

::: tip 工程实现说明
彩色图建议先在合适色彩空间处理，或确认对三通道分别中值是否可接受；对椒盐噪声 ksize=3 通常已足够。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
