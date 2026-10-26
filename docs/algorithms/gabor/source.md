# 源码走读：Gabor 滤波器

## OpenCV 最简调用

```python
import cv2, numpy as np
img = cv2.imread('fingerprint.jpg', 0)

# 构建 Gabor 滤波器组（8 方向 × 5 尺度）
def build_gabor_bank():
    bank = []
    for theta in np.arange(0, np.pi, np.pi/8):
        for lambd in [3,5,9,15,25]:
            ksize = 31
            sigma = 0.56 * lambd
            gamma = 0.5
            k = cv2.getGaborKernel((ksize,ksize), sigma, theta, lambd, gamma, 0, ktype=cv2.CV_32F)
            bank.append(k)
    return bank

bank = build_gabor_bank()
responses = [cv2.filter2D(img, cv2.CV_32F, k) for k in bank]

# 取多方向 max（多方向边缘）
multi_edge = np.max([np.abs(r) for r in responses], axis=0)

# 纹理特征：每张响应图的 mean + std
feat = []
for r in responses:
    feat.extend([r.mean(), r.std()])
feat = np.array(feat)   # 80 维向量

```

## 手写最小实现（理解原理）

```python
import numpy as np

def gabor_kernel(ksize=31, sigma=4.0, theta=0, lambd=10, gamma=0.5, psi=0):
    """手写 Gabor 核（教学用，可与 cv2.getGaborKernel 对照）"""
    ax = np.arange(-ksize//2+1, ksize//2+1)
    xx, yy = np.meshgrid(ax, ax)
    x_prime = xx*np.cos(theta) + yy*np.sin(theta)
    y_prime = -xx*np.sin(theta) + yy*np.cos(theta)
    gauss = np.exp(-(x_prime**2 + (gamma*y_prime)**2) / (2*sigma**2))
    sinusoid = np.cos(2*np.pi*x_prime/lambd + psi)   # 实部
    return gauss * sinusoid

```

## OpenCV 源码核心片段解读

OpenCV `cv::getGaborKernel` 在 `modules/imgproc/src/gabor.cpp`，代码非常短（约 50 行）：
1. 按公式算旋转后的 x'/y' 坐标（meshgrid）
2. 计算高斯项和正弦项逐像素相乘
3. 做 DC 校正：减去均值，让核零均值（避免响应受灰度整体偏移影响）
4. 归一化 L1 或 L2

注意：OpenCV 默认返回**实部（余弦）**。若要复数值响应，需要分别取 psi=0 和 psi=π/2 生成两个核，分别卷积得到 Re 和 Im，再取幅值。

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **gabor** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="gabor" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
