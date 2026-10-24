---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import cv2
import numpy as np

img = cv2.imread("coins.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 5)          # 去噪，霍夫圆对噪声敏感

circles = cv2.HoughCircles(
    gray,
    cv2.HOUGH_GRADIENT,
    dp=1.2,          # 累加器分辨率倒数
    minDist=30,      # 圆心最小间距
    param1=100,      # Canny 高阈值
    param2=30,       # 圆心累加阈值（越小越灵敏）
    minRadius=10,
    maxRadius=80,    # 一定要给上限，否则很慢
)

if circles is not None:
    circles = np.uint16(np.around(circles))
    for c in circles[0, :]:
        cv2.circle(img, (c[0], c[1]), c[2], (0, 255, 0), 2)
        cv2.circle(img, (c[0], c[1]), 2, (0, 0, 255), 3)

cv2.imwrite("circles.png", img)
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
import numpy as np
import cv2

# 手写「梯度方向投票」版霍夫圆（简化，仅示意）
img = cv2.imread("coins.jpg", cv2.IMREAD_GRAYSCALE)
edges = cv2.Canny(img, 100, 200)
gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)
ys, xs = np.nonzero(edges)
acc = np.zeros(img.shape, np.uint16)

r_min, r_max = 10, 80
for r in range(r_min, r_max, 2):
    for y, x in zip(ys, xs):
        n = np.hypot(gx[y, x], gy[y, x])
        if n < 1:
            continue
        a = int(x - r * gx[y, x] / n)   # 沿梯度方向走 r
        b = int(y - r * gy[y, x] / n)
        if 0 <= a < img.shape[1] and 0 <= b < img.shape[0]:
            acc[b, a] += 1

y0, x0 = np.unravel_index(np.argmax(acc), acc.shape)
print("投票最高的圆心:", (x0, y0), "票数:", acc[y0, x0])
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| dp | 累加器分辨率的倒数 | **1.2** |
| minDist | 圆心之间的最小距离 | **图高/8** |
| param1 | Canny 高阈值 | **100** |
| param2 | 圆心累加阈值 | **30（硬币）** |
| minRadius/maxRadius | 半径范围 | **按目标给定** |

::: tip 工程实现说明
OpenCV 的 HOUGH_GRADIENT 已用梯度信息做了降维，但 minRadius/maxRadius 必须限制，否则自增半径搜索会非常慢。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
