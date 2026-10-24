---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import cv2

cap = cv2.VideoCapture("street.mp4")
knn = cv2.createBackgroundSubtractorKNN(
    history=500,
    dist2Threshold=400.0,
    detectShadows=True,
)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

while True:
    ok, frame = cap.read()
    if not ok:
        break
    fg = knn.apply(frame)
    # 去掉阴影（阴影被标为 127），只保留确定前景（255）
    _, fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
    # 形态学去噪
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel)
    fg = cv2.dilate(fg, kernel, iterations=2)

    cv2.imshow("foreground", fg)
    if cv2.waitKey(30) == 27:
        break
cap.release()
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
import numpy as np
import cv2

# 手写简化版：每像素存 nSamples 个样本，距离阈值判定
nSamples, dist2 = 10, 400.0
gray = cv2.cvtColor(cv2.imread("street.jpg"), cv2.COLOR_BGR2GRAY)

samples = np.repeat(gray[:, :, None], nSamples, axis=2).astype(np.int16)
rng = np.random.default_rng(0)

# 模拟新来的一帧（这里直接用同一张图加噪，示意判定流程）
new = gray.astype(np.int16) + rng.integers(-5, 6, gray.shape).astype(np.int16)
diff2 = (new[:, :, None] - samples) ** 2
close = (diff2 < dist2).sum(axis=2)

fg_mask = (close < 2).astype(np.uint8) * 255     # 近样本太少 -> 前景
print("前景像素数:", int((fg_mask > 0).sum()))
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| history | 历史帧数 | **500** |
| dist2Threshold | 距离平方阈值 | **400** |
| detectShadows | 检测阴影 | **True** |
| nSamples | 每像素样本数（构造参数） | **7~20** |

::: tip 工程实现说明
OpenCV 提供 createBackgroundSubtractorKNN（标准库）与 MOG2 两个内置方法；阴影像素值为 127，前景为 255。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
