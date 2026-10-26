# 💻 源码实现

## ① OpenCV 一行调用

```python
import cv2
img = cv2.imread("portrait.jpg")
# d=核直径(常用 -1 自动由 sigmaSpace 算); sigmaColor=75; sigmaSpace=75
smooth = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
```

## ② 人像磨皮完整流水线

```python
import cv2, numpy as np

def beauty_face(img, d=15, sigma=75, detail_keep=0.5):
    """磨皮：强双边 + 细节回注"""
    blur = cv2.bilateralFilter(img, d=d, sigmaColor=sigma, sigmaSpace=sigma)
    detail = img.astype(np.float32) - blur.astype(np.float32)
    out = blur.astype(np.float32) + detail * detail_keep  # 保留一半高频
    return np.clip(out, 0, 255).astype(np.uint8)

img = cv2.imread("face.jpg")
res = beauty_face(img, d=21, sigma=90, detail_keep=0.4)
cv2.imwrite("face_beauty.jpg", res)
```

## ③ 手写最小版（理解原理，不用于生产）

```python
import numpy as np, cv2

def bilateral_filter_naive(img, d=5, sigma_s=10, sigma_r=30):
    h, w = img.shape[:2]
    pad = d // 2
    I = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_REFLECT).astype(np.float32)
    out = np.zeros_like(I)
    # 预计算空间高斯
    yy, xx = np.mgrid[-pad:pad+1, -pad:pad+1]
    gs = np.exp(-(xx*xx + yy*yy) / (2*sigma_s*sigma_s))
    for y in range(pad, h+pad):
        for x in range(pad, w+pad):
            patch = I[y-pad:y+pad+1, x-pad:x+pad+1]
            diff = patch - I[y, x]
            if img.ndim == 3:
                gr = np.exp(-np.sum(diff*diff, axis=2) / (2*sigma_r*sigma_r))
            else:
                gr = np.exp(-diff*diff / (2*sigma_r*sigma_r))
            w = gs * gr
            if img.ndim == 3:
                out[y, x] = np.sum(patch * w[..., None], axis=(0,1)) / np.sum(w)
            else:
                out[y, x] = np.sum(patch * w) / np.sum(w)
    return out[pad:h+pad, pad:w+pad].astype(np.uint8)
```

**注意**：这个手写版比 OpenCV 慢 1000 倍，仅供理解；生产一定要用 `cv2.bilateralFilter`。

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **bilateral** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="bilateral" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
