---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import cv2
import numpy as np

img = cv2.imread("input.jpg")

# 最常用：ksize=(5,5)，sigmaX=0 让 OpenCV 自动推导
blur = cv2.GaussianBlur(img, (5, 5), 0)

# 想自己控制模糊程度：先定 sigma，再反推 ksize
sigma = 2.0
k = int(2 * round(3 * sigma) + 1)
blur2 = cv2.GaussianBlur(img, (k, k), sigma)

cv2.imwrite("blur.png", blur)
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
import numpy as np
import cv2


def gaussian_kernel(size, sigma):
    """生成归一化的一维高斯核。"""
    ax = np.arange(-(size // 2), size // 2 + 1, dtype=np.float32)
    g = np.exp(-(ax ** 2) / (2 * sigma ** 2))
    return g / g.sum()


def my_gaussian_blur(img, ksize, sigma):
    """可分离高斯模糊：先横向再纵向。"""
    g = gaussian_kernel(ksize, sigma)
    out = img.astype(np.float32)
    # 横向
    tmp = np.apply_along_axis(lambda r: np.convolve(r, g, mode="same"), 1, out)
    # 纵向
    res = np.apply_along_axis(lambda c: np.convolve(c, g, mode="same"), 0, tmp)
    return np.clip(res, 0, 255).astype(np.uint8)


img = cv2.imread("input.jpg", cv2.IMREAD_GRAYSCALE)
out = my_gaussian_blur(img, 9, 2.0)
print(out.shape)
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| ksize | 高斯核尺寸（正奇数） | **(5,5)** |
| sigmaX | X 方向标准差 | **0（自动）** |
| sigmaY | Y 方向标准差 | **0（跟随 sigmaX）** |
| borderType | 边界填充方式 | **BORDER_DEFAULT** |

::: tip 工程实现说明
ksize 必须是正奇数；sigmaX=0 时 OpenCV 按 ksize 公式 sigma = 0.3·((ksize−1)·0.5 − 1) + 0.8 自动推导。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
