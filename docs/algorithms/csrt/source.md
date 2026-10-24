# 源码走读：CSRT 通道与空间可靠性跟踪

## OpenCV 最简调用

```python
import cv2
tracker = cv2.TrackerCSRT_create()
# 调参（可选）
tracker.setParams(
    padding=3.0,
    template_size=32,
    gsl_sigma=1.0,
    filter_lr=0.02,
)
cap = cv2.VideoCapture('video.mp4')
ok, frame = cap.read()
bbox = cv2.selectROI('select', frame, False)
tracker.init(frame, bbox)

while True:
    ok, frame = cap.read()
    if not ok: break
    ok, bbox = tracker.update(frame)
    if ok:
        x,y,w,h = [int(v) for v in bbox]
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
    cv2.imshow('CSRT', frame)
    if cv2.waitKey(30) & 0xFF == 27: break

```

## 手写最小实现（理解原理）

```python
import numpy as np, cv2

# 简化版 CSRT 核心思想演示：空间掩膜 + 通道加权
def cos_window(sz):
    h, w = sz
    c = np.hanning(w)[None,:] * np.hanning(h)[:,None]
    return c.astype(np.float32)

def train_dcf_with_mask(x, y, m, lam=0.01, iters=4):
    """带掩膜 DCF 简化版（CG 迭代示意，非真正 CSRT）"""
    # x: (C,H,W) features, m: (H,W) mask, y: (H,W) label
    C, H, W = x.shape
    Xf = np.fft.fft2(x, axes=(1,2))
    Yf = np.fft.fft2(y)
    Wf = np.zeros_like(Xf)
    r = Yf - np.einsum('chw,chw->hw', np.conj(Xf), Wf) - lam*Wf[0]
    p = r.copy()
    for _ in range(iters):
        Ap = np.einsum('chw,chw->hw', np.conj(Xf), p) * Xf/Xf.shape[0] + lam*p
        alpha = np.sum(r*np.conj(r)) / (np.sum(p*np.conj(Ap)) + 1e-8)
        Wf = Wf + alpha*p
        r_new = r - alpha*Ap
        beta = np.sum(r_new*np.conj(r_new)) / (np.sum(r*np.conj(r)) + 1e-8)
        p = r_new + beta*p
        r = r_new
    return Wf

```

## OpenCV 源码核心片段解读

OpenCV CSRT 源码在 `opencv_contrib/modules/tracking/src/trackerCSRT.cpp`：

- `TrackerCSRTImpl::initImpl()`：初始化，构造 `CSRTFilter`、`ScaleEstimator`、`Histogram`
- `TrackerCSRTImpl::updateImpl()`：每帧更新主循环
- `CSRTFilter::detect()`：在多通道特征上做相关，加权求和
- `CSRTFilter::update()`：调用 `StandardCGImpl::update()` 做共轭梯度迭代
- `SpatialMask::estimateMask()`：根据颜色直方图 + 高斯先验算空间掩膜
- `ChannelReliability::computeReliability()`：按 PSR + 学习稳定性算 w_d

OpenCV 版本比论文稍简化（比如没完全用 ADMM，用了简化 CG），但精度仍然显著高于 KCF。
