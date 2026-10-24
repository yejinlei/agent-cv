---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import cv2

# OpenCV 提供 MOSSE（旧版 API：cv2.legacy）
tracker = cv2.legacy.TrackerMOSSE_create()
cap = cv2.VideoCapture("video.mp4")
ok, frame = cap.read()
bbox = cv2.selectROI("select", frame, False)   # 手动框选目标
tracker.init(frame, bbox)

while True:
    ok, frame = cap.read()
    if not ok:
        break
    ok, box = tracker.update(frame)
    if ok:
        x, y, w, h = [int(v) for v in box]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    else:
        cv2.putText(frame, "LOST", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("MOSSE", frame)
    if cv2.waitKey(1) == 27:
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

# 手写 MOSSE 核心：FFT 域训练 + 相关定位（高度简化）
H, W = 32, 32
sigma, lr, eps = 2.0, 0.125, 1e-5

# 期望响应：中心亮的高斯
ys, xs = np.mgrid[0:H, 0:W]
ys, xs = ys - H // 2, xs - W // 2
G = np.exp(-(xs ** 2 + ys ** 2) / (2 * sigma ** 2)).astype(np.float32)
Gf = np.fft.fft2(G)
Hf = np.zeros((H, W), np.complex64)
Gf_sum, Ff_sum = np.zeros((H, W), np.complex64), np.zeros((H, W), np.complex64)

# 用若干含小形变的样本训练（此处示意用同一块加噪）
patch = cv2.imread("target.png", 0).astype(np.float32) / 255.0
for _ in range(8):
    Ff = np.fft.fft2(patch + 0.01 * np.random.randn(H, W))
    Gf_sum += Gf * np.conj(Ff)
    Ff_sum += np.conj(Ff) * Ff
Hf = Gf_sum / (Ff_sum + eps)

# 推理：新帧相关并找峰值
frame_patch = patch + 0.02 * np.random.randn(H, W)
resp = np.real(np.fft.ifft2(Hf * np.fft.fft2(frame_patch)))
dy, dx = np.unravel_index(np.argmax(resp), resp.shape)
print("峰值偏移:", (dx - W // 2, dy - H // 2))
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| learning_rate | 在线更新学习率 | **0.125** |
| sigma | 期望高斯响应 σ | **2.0** |
| psr_threshold | PSR 丢失阈值 | **7.0** |
| search_window | 搜索窗倍数 | **1.5** |

::: tip 工程实现说明
OpenCV 4.x 的 MOSSE 在 legacy 命名空间：cv2.legacy.TrackerMOSSE_create()；需安装 opencv-contrib-python。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
