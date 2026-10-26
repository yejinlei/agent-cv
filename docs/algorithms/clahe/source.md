# 源码走读：CLAHE 限制对比度自适应直方图均衡

## OpenCV 最简调用

```python
import cv2
img = cv2.imread('lowlight.jpg')
# 彩色图：转到 LAB 只增强 L 通道
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
l2 = clahe.apply(l)
lab2 = cv2.merge([l2, a, b])
out = cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)

```

## 手写最小实现（理解原理）

```python
import numpy as np, cv2

def clahe_naive(img, clipLimit=2.0, tileGridSize=(8,8)):
    """极简 CLAHE（教学用：单通道灰度，无边界插值优化）"""
    h, w = img.shape
    th, tw = tileGridSize
    tile_h, tile_w = h // th, w // tw
    out = np.zeros_like(img)
    LUTs = {}

    # 每个 tile 算 clipped CDF
    for i in range(th):
        for j in range(tw):
            tile = img[i*tile_h:(i+1)*tile_h, j*tile_w:(j+1)*tile_w]
            hist, _ = np.histogram(tile.flatten(), 256, [0,256])
            limit = int(clipLimit * tile_h * tile_w / 256)
            excess = 0
            for k in range(256):
                if hist[k] > limit:
                    excess += hist[k] - limit
                    hist[k] = limit
            inc = excess // 256
            hist += inc
            cdf = np.cumsum(hist).astype(np.float32)
            cdf = 255 * (cdf - cdf.min()) / (cdf.max() - cdf.min() + 1e-6)
            LUTs[(i,j)] = cdf.astype(np.uint8)

    # 最近邻插值版（简化，略去双线性）
    for i in range(th):
        for j in range(tw):
            tile = img[i*tile_h:(i+1)*tile_h, j*tile_w:(j+1)*tile_w]
            out[i*tile_h:(i+1)*tile_h, j*tile_w:(j+1)*tile_w] = LUTs[(i,j)][tile]
    return out

```

## OpenCV 源码核心片段解读

OpenCV CLAHE 在 `modules/imgproc/src/clahe.cpp`，核心类 `CLAHE_Impl`：

- `CLAHE_Impl::apply()`：入口，分 tile、并行处理
- `CLAHE_Impl::calcLUT()`：对每个 tile 算 clip + CDF，用 `cv::parallel_for_` 并行
- `CLAHE_Impl::interpolate`：双线性插值的四种情况（tile 内部/边界/四角），SSE/AVX 优化过
- Clip 循环用了个小技巧：不是「一次裁剪+均摊」，而是循环「裁剪→均摊→再裁剪」到没有 bin 超限（通常 2–3 次收敛）

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **clahe** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="clahe" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
