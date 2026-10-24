---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import numpy as np
import cv2


class ViBe:
    """极简 ViBe 背景建模实现。"""

    def __init__(self, height, width, n=20, r=20, min_match=2, phi=16):
        self.n, self.r, self.min_match, self.phi = n, r, min_match, phi
        self.samples = np.zeros((n, height, width), np.uint8)
        self.height, self.width = height, width

    def init(self, frame):
        pad = np.pad(frame, 1, mode="edge")
        for k in range(self.n):
            dy, dx = np.random.randint(0, 3, 2) - 1
            self.samples[k] = pad[1 + dy:1 + dy + self.height, 1 + dx:1 + dx + self.width]
        return np.zeros(frame.shape, np.uint8)

    def apply(self, frame):
        diff = np.abs(self.samples.astype(np.int16) - frame.astype(np.int16))
        match = (diff < self.r).sum(axis=0)
        fg = (match < self.min_match).astype(np.uint8) * 255

        # 随机更新
        bg = fg == 0
        upd = bg & (np.random.rand(self.height, self.width) < 1.0 / self.phi)
        idx = np.random.randint(0, self.n, size=(self.height, self.width))
        for k in range(self.n):
            self.samples[k][upd & (idx == k)] = frame[upd & (idx == k)]
        return fg


cap = cv2.VideoCapture("video.mp4")
ok, frame0 = cap.read()
gray0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
vibe = ViBe(*gray0.shape)
vibe.init(gray0)
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
# 若不想自己实现，也可用 MOG2 近似「随机更新」的轻量效果
import cv2

mog2 = cv2.createBackgroundSubtractorMOG2(
    history=100,          # 短历史 = 更新更快，接近 ViBe 的轻量感
    varThreshold=24,
    detectShadows=False,
)
cap = cv2.VideoCapture("video.mp4")
while cap.isOpened():
    ok, frame = cap.read()
    if not ok:
        break
    fg = mog2.apply(frame)
    cv2.imshow("fg", fg)
    if cv2.waitKey(30) == 27:
        break
cap.release()
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| N | 样本集大小 | **20** |
| R | 颜色距离半径 | **20** |
| minMatch | 判定背景的最少匹配数 | **2** |
| phi | 随机更新概率倒数 | **16** |

::: tip 工程实现说明
OpenCV 未内置 ViBe；可用不等长的短历史 MOG2 近似其轻量特性，或用 opencv-contrib/第三方实现。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
