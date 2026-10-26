---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import cv2
import numpy as np

img = cv2.imread("parts.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    if cv2.contourArea(cnt) < 100:
        continue
    # 1) 多边形逼近：epsilon 取周长的 2%
    eps = 0.02 * cv2.arcLength(cnt, True)
    poly = cv2.approxPolyDP(cnt, eps, True)

    # 2) 最小外接矩形（带旋转）
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect).astype(int)

    # 3) 椭圆拟合（需要 >=5 点）
    if len(cnt) >= 5:
        ellipse = cv2.fitEllipse(cnt)

    cv2.drawContours(img, [poly], -1, (0, 255, 0), 2)
    cv2.drawContours(img, [box], -1, (255, 0, 0), 1)
    if len(cnt) >= 5:
        cv2.ellipse(img, ellipse, (0, 0, 255), 2)

cv2.imwrite("fitted.png", img)
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
import numpy as np
import cv2


def rdp(points, epsilon):
    """手写 Douglas-Peucker 折线简化。points: (N,2) 数组。"""
    if len(points) < 3:
        return points
    p0, p1 = points[0], points[-1]
    line = p1 - p0
    norm = np.linalg.norm(line)
    if norm == 0:
        d = np.linalg.norm(points - p0, axis=1)
    else:
        d = np.abs(np.cross(line, points - p0)) / norm
    idx = np.argmax(d)
    if d[idx] > epsilon:
        left = rdp(points[:idx + 1], epsilon)
        right = rdp(points[idx:], epsilon)
        return np.vstack([left[:-1], right])
    return np.array([p0, p1])


cnt = cv2.findContours(cv2.Canny(cv2.imread("parts.jpg", 0), 50, 150),
                       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0][0]
pts = cnt.reshape(-1, 2).astype(np.float64)
simp = rdp(pts, epsilon=0.02 * cv2.arcLength(cnt, True))
print("原始点数:", len(pts), "-> 简化后:", len(simp))
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| epsilon | 多边形逼近精度（越大越简） | **0.01~0.02×周长** |
| closed | 轮廓是否闭合 | **True** |
| minAreaRect | 最小外接旋转矩形 | **(center, size, angle)** |
| fitEllipse | 最小二乘椭圆 | **需≥5点** |

::: tip 工程实现说明
approxPolyDP 要求输入为闭合曲线时 closed=True；fitEllipse 至少需要 5 个点，少于 5 点会抛异常。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **contour fitting** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="contours" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
