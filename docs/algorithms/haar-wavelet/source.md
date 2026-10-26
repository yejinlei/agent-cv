---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import numpy as np
import cv2

img = cv2.imread("lena.jpg", cv2.IMREAD_GRAYSCALE).astype(np.float32)


def haar_2d(img):
    """一层二维 Haar 分解，返回 LL, LH, HL, HH。"""
    h, w = img.shape
    # 行方向：低通(平均) 与 高通(差分)
    row = img.reshape(h, w // 2, 2)
    low = (row[:, :, 0] + row[:, :, 1]) / np.sqrt(2)
    high = (row[:, :, 0] - row[:, :, 1]) / np.sqrt(2)
    L = np.hstack([low, high])
    # 列方向同理
    Lr = L.reshape(h // 2, 2, w)
    LL = (Lr[:, 0, :] + Lr[:, 1, :]) / np.sqrt(2)
    LH = (Lr[:, 0, :] - Lr[:, 1, :]) / np.sqrt(2)
    col = np.vstack([LL, LH])
    return col[:h // 2, :], col[h // 2:, :]


LL, detail_rows = haar_2d(img)
print("一层分解 LL 形状:", LL.shape)
cv2.imwrite("haar_ll.png", np.clip(LL, 0, 255).astype(np.uint8))
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
import numpy as np
import pywt   # pip install PyWavelets

img = np.array([[10, 12, 20, 22],
                [11, 13, 21, 23],
                [30, 32, 40, 42],
                [31, 33, 41, 43]], dtype=np.float32)

# 一层 haar 分解，得到 4 个子带
coeffs = pywt.dwt2(img, "haar")
LL, (LH, HL, HH) = coeffs
print("LL (低频):\n", LL)
print("LH (竖边缘):\n", LH)
print("HL (横边缘):\n", HL)
print("HH (对角):\n", HH)

# 逆变换重构
recon = pywt.idwt2((LL, (LH, HL, HH)), "haar")
print("重构是否还原:", np.allclose(recon, img))
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| level | 分解层数 | **2~5** |
| wavelet | 小波基 | **haar** |
| mode | 边界延拓 | **symmetric** |
| threshold | 去噪阈值 | **3σ（软阈值）** |

::: tip 工程实现说明
直接用小波做特征时，差分子带对噪声敏感，建议先轻微高斯平滑；做去噪时用软阈值而非硬阈值以减少振铃。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **haar wavelet** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="haarwavelet" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
