# Otsu 源码走读

> 从「一行调用」到「产线级二值化管线」，这一页给你能直接抄的代码。

## 档位一：OpenCV 一行（最简）

```python
import cv2

gray = cv2.imread('doc.png', cv2.IMREAD_GRAYSCALE)

# Otsu：阈值参数传 0，由 THRESH_OTSU 标志自动算
th, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
print(f'自动阈值 = {th:.1f}')
```

## 档位二：手写增量版（比朴素版快 10 倍以上）

```python
import numpy as np
import cv2

def otsu_fast(gray):
    """用前缀和 + 增量，等价于 OpenCV 内部实现"""
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
    total = hist.sum()
    idx = np.arange(256)

    # 前缀和，用于 O(1) 求 ω0 和 μ0
    cum_p = np.cumsum(hist) / total                       # ω0(t)
    cum_m = np.cumsum(hist * idx) / total                 # ω0(t)·μ0(t)

    mu_T = cum_m[-1]
    # 避免除零
    omega0 = cum_p
    omega1 = 1 - omega0
    valid = (omega0 > 0) & (omega1 > 0)

    mu0 = np.divide(cum_m, omega0, out=np.zeros_like(cum_m), where=omega0 > 0)
    mu1 = np.divide(mu_T - cum_m, omega1, out=np.zeros_like(cum_m), where=omega1 > 0)

    var_between = np.where(valid, omega0 * omega1 * (mu0 - mu1) ** 2, 0)
    t = int(np.argmax(var_between))
    return t
```

**为什么快**：整段只有几次向量化运算，没有 Python 循环。1080p 图在毫秒级完成。

## 档位三：工业级二值化管线

### 场景 A：文档扫描 / OCR 前处理

```python
def binarize_document(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    # 1. 去噪（文档常有扫痕、噪点）
    img = cv2.medianBlur(img, 3)

    # 2. 光照不均 → 先做背景归一化（关键技术）
    bg = cv2.morphologyEx(img, cv2.MORPH_CLOSE,
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    norm = cv2.divide(img, bg, scale=255)     # 抹平光照梯度

    # 3. 再上 Otsu
    th, binary = cv2.threshold(norm, 0, 255,
                               cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 4. 去小噪点
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN,
                              np.ones((2, 2), np.uint8))
    return binary, th
```

::: tip 光照不均的三板斧
文档/工业图常见问题是**「左边亮右边暗」**，此时全局 Otsu 会「亮区还清、暗区全黑」。三种解法：

1. **背景归一化**（上面的 `divide`）——最推荐，保留全局 Otsu
2. **分块 Otsu**——把图切成小格，各自算阈值
3. **自适应阈值**——`adaptiveThreshold` 逐像素算
:::

### 场景 B：工业缺陷分割（面积悬殊的处理）

```python
def segment_defect(gray, expected_ratio=0.05):
    """小缺陷：Otsu 会偏移，做加权或改用局部"""
    # 方法一：直接 Otsu + 面积过滤
    th, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_img = gray.size
    defects = [c for c in cnts if 20 < cv2.contourArea(c) < area_img * expected_ratio]

    # 方法二（面积极悬殊时）：局部 Otsu 分块
    return defects

def otsu_tiled(gray, tile=128, overlap=16):
    """分块 Otsu：每块独立算阈值，缓解面积悬殊和光照梯度"""
    h, w = gray.shape
    out = np.zeros_like(gray)
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            patch = gray[y:y+tile+overlap, x:x+tile+overlap]
            if patch.size < 256:
                continue
            t, _ = cv2.threshold(patch, 0, 255,
                                 cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            out[y:y+tile, x:x+tile] = (patch[:tile, :tile] > t) * 255
    return out
```

### 场景 C：给 Canny 自动定阈值（Otsu 的隐藏用法）

```python
def canny_auto(img, k=0.5):
    """用 Otsu 值作为 Canny 高阈值，低阈值按比例"""
    blur = cv2.GaussianBlur(img, (5, 5), 1.4)
    th_otsu, _ = cv2.threshold(blur, 0, 255,
                               cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    high = int(th_otsu)
    low = int(high * k)
    return cv2.Canny(blur, low, high)
```

**为什么可行**：Otsu 给出的其实是「边缘幅度的一个合理分界」，天然适合当作 Canny 的强阈值。

## 数值与性能细节

| 细节 | 说明 |
|---|---|
| **阈值取整** | OpenCV 返回的 `th` 是浮点；实际分界是「像素 > th」 |
| **平局处理** | 多个 $t$ 方差相同时，通常取**最小**的 $t$（更保守） |
| **单峰陷阱** | 全黑或全白图，Otsu 会返回 0 或 255，需加保护 |
| **16 位图** | `THRESH_OTSU` 默认按 8 位直方图，16 位图需先归一化到 0-255 |
| **彩色图** | OpenCV 会先转灰度再算，但建议自己显式转换以控制 |

```python
# 单峰保护写法
if gray.std() < 5:                 # 对比度极低，别信 Otsu
    th = 127
else:
    th, _ = cv2.threshold(gray, 0, 255,
                          cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

## 多语言等价 API

| 语言/库 | 调用 |
|---|---|
| Python OpenCV | `cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)` |
| C++ OpenCV | `cv::threshold(g, dst, 0, 255, cv::THRESH_BINARY | cv::THRESH_OTSU);` |
| scikit-image | `skimage.filters.threshold_otsu(img)` |
| MATLAB | `graythresh(I)` |
| OpenMV | `img.get_histogram().get_threshold().value()` |

## 性能参考（1080p 灰度，单核 CPU）

| 实现 | 耗时 |
|---|---|
| `cv2.threshold` + OTSU | ≈ 3 ms |
| Numpy 向量化手写 | ≈ 4 ms |
| Numpy 逐 t 循环手写 | ≈ 8 ms |
| 分块 Otsu（128 块） | ≈ 20 ms |

::: warning Otsu 本身极快
Otsu 的耗时几乎等于「算一次直方图」。如果你的管线慢，瓶颈一定不在 Otsu，而在前面的滤波或后面的形态学。
:::

[← 上一篇：算法流程](./architecture) · [下一篇：实战与踩坑 →](./painpoints)

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **otsu** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="threshold" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
