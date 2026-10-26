# Sobel 源码走读

> 从「一行调用」到「工业级轮廓提取」，这一页给你三档代码：能跑、能懂、能上产线。

## 档位一：OpenCV 一行调用（最简）

```python
import cv2
import numpy as np

img = cv2.imread('part.png', cv2.IMREAD_GRAYSCALE)

# ① 分别求 x / y 梯度，必须用 CV_16S 接住负值
gx = cv2.Sobel(img, cv2.CV_16S, 1, 0, ksize=3)
gy = cv2.Sobel(img, cv2.CV_16S, 0, 1, ksize=3)

# ② 取绝对值并转回 uint8（convertScaleAbs 一步搞定）
abs_gx = cv2.convertScaleAbs(gx)
abs_gy = cv2.convertScaleAbs(gy)

# ③ 合成幅值（两方向等权）
mag = cv2.addWeighted(abs_gx, 0.5, abs_gy, 0.5, 0)

cv2.imshow('sobel magnitude', mag)
```

## 档位二：手写完整版（带方向、带可分离）

```python
import cv2
import numpy as np

def sobel_full(gray, use_l2=True):
    """返回：Gx, Gy, 幅值(0-255), 方向(弧度)"""
    img = gray.astype(np.float32)

    # 可分离实现：先平滑后差分（等价于 3×3 Sobel，但快）
    sm = cv2.getGaussianKernel(3, 0).flatten()      # [0.25, 0.5, 0.25]
    dfx = np.array([-1, 0, 1], dtype=np.float32)    # 水平差分

    # 用 separable filter 加速
    gx = cv2.sepFilter2D(img, cv2.CV_32F, dfx, sm)      # 水平差分 × 垂直平滑
    gy = cv2.sepFilter2D(img, cv2.CV_32F, sm, dfx)      # 垂直差分 × 水平平滑

    if use_l2:
        mag = np.sqrt(gx**2 + gy**2)
    else:
        mag = np.abs(gx) + np.abs(gy)

    ang = np.arctan2(gy, gx)

    mag8 = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return gx, gy, mag8, ang

gx, gy, mag, ang = sobel_full(img)
```

## 档位三：工业级用途（三个真实场景）

### 场景 A：零件轮廓提取 + 形态学清理

```python
def extract_contour_mask(gray, thresh=60):
    """从 Sobel 幅值图提取干净的轮廓掩膜"""
    # 1. 轻度去噪（Sobel 自带平滑不够，工业噪点多）
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # 2. Sobel 求幅值
    gx = cv2.Sobel(blur, cv2.CV_16S, 1, 0, ksize=3)
    gy = cv2.Sobel(blur, cv2.CV_16S, 0, 1, ksize=3)
    mag = cv2.addWeighted(cv2.convertScaleAbs(gx), 0.5,
                          cv2.convertScaleAbs(gy), 0.5, 0)

    # 3. 二值化
    _, bw = cv2.threshold(mag, thresh, 255, cv2.THRESH_BINARY)

    # 4. 形态学闭运算：把断掉的轮廓连起来
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel, iterations=1)

    return closed
```

::: tip 为什么工业上 Sobel 常配形态学
Sobel 出来的轮廓常常是**断断续续**的（弱边处幅值不够）。闭运算（先膨胀后腐蚀）能把 1-2 像素的缝隙补上，得到闭合的轮廓，便于后续 `findContours` + 面积/周长测量。
:::

### 场景 B：方向敏感的 Scharr 替代（斜边更准）

```python
# 需要方向对称性时（如图像旋转后再检测、圆形目标）
gx = cv2.Scharr(blur, cv2.CV_16S, 1, 0)
gy = cv2.Scharr(blur, cv2.CV_16S, 0, 1)
# 等价写法：cv2.Sobel(blur, cv2.CV_16S, 1, 0, ksize=-1)
```

### 场景 C：给 HOG / Harris 提供梯度（内部原理）

```python
# HOG 的梯度方向直方图，第一步就是在算 Sobel
def hog_gradients(gray):
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=1)   # ksize=1 → 最原始差分
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=1)
    mag = np.sqrt(gx**2 + gy**2)
    ang = np.rad2deg(np.arctan2(gy, gx)) % 180        # HOG 用 0-180 无符号方向
    return mag, ang

# Harris 的结构张量，也是 Ix, Iy 的乘积
def harris_terms(gray):
    Ix = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    Iy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    Ixx = cv2.GaussianBlur(Ix * Ix, (3, 3), 0)
    Iyy = cv2.GaussianBlur(Iy * Iy, (3, 3), 0)
    Ixy = cv2.GaussianBlur(Ix * Iy, (3, 3), 0)
    return Ixx, Iyy, Ixy
```

**看到没**：`ksize=1` 时 OpenCV 用的是最朴素的 $[-1, 0, 1]$ 差分核（不带平滑）。HOG 原论文用的正是这个——因为它随后会用 block 归一化来对抗光照与噪声。

## OpenCV 源码级细节（三个容易忽略的）

| 细节 | 说明 |
|---|---|
| **核是浮点的** | `cv2.getDerivKernels(1, 0, 3)` 返回的 1D 核是 `[-1, 0, 1]` 和 `[1, 2, 1]`，卷积后**不除以 8**。所以幅值比真实梯度大 8 倍——好在边缘检测只关心相对大小 |
| **ksize=1 的特殊处理** | `ksize=1` 时不加平滑，纯 1D 差分（`[-1, 0, 1]`），这正是 HOG、Harris 的常见配置 |
| **borderType 的影响** | 默认 `BORDER_REFLECT_101`，图像最外一圈像素的梯度会略失真；对全图测量无影响，但对「接触边界的零件」要留意 |

## 数值类型速查表

| 你想做的事 | `ddepth` 该选 | 理由 |
|---|---|---|
| 只要显示幅值 | `CV_16S` → `convertScaleAbs` | 保留负值，再翻正 |
| 要精确梯度值（如算光流） | `CV_32F` | 浮点，无截断无量化 |
| 快速预览 | `CV_8U`（**不推荐**） | 负值被截断成 0，**会丢一半边缘** |

## 多语言等价 API

| 语言 | 调用 |
|---|---|
| Python | `cv2.Sobel(src, cv2.CV_16S, 1, 0, ksize=3)` |
| C++ | `cv::Sobel(src, dst, CV_16S, 1, 0, 3);` |
| MATLAB | `imgradientxy(I, 'sobel')` 或 `fspecial('sobel')` |
| skimage | `skimage.filters.sobel(img)` |
| OpenMV（MCU） | `img.find_edges(image.EDGE_SIMPLE)`（内部即 Sobel 类梯度） |

## 性能参考（1920×1080 灰度，单核 CPU）

| 实现 | 耗时 |
|---|---|
| `cv2.Sobel` ksize=3（单方向） | ≈ 4 ms |
| `cv2.Sobel` ksize=3（两方向） | ≈ 8 ms |
| `cv2.Scharr`（两方向） | ≈ 12 ms |
| `cv2.filter2D` 手写 3×3 | ≈ 15 ms |
| Numpy 手写双重循环 | ≈ 2000 ms（**别上产线**） |

::: warning 手写循环只能用于教学
上面的 `conv2d_valid` 双重 for 循环在 1080p 图上要几秒。产线必须用 OpenCV（SIMD 优化）或分离核。
:::

[← 上一篇：算法流程](./architecture) · [下一篇：实战与踩坑 →](./painpoints)

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **sobel** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="sobel" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
