# 源码走读：AKAZE 加速 KAZE 特征

## OpenCV 最简调用

```python
import cv2
img = cv2.imread('scene.jpg', 0)

akaze = cv2.AKAZE_create(
    descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB,
    descriptor_size=0,       # 0 = full 486 bits
    threshold=0.001,
    nOctaves=4,
    nOctaveLayers=4,
)
kps, des = akaze.detectAndCompute(img, None)

bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
matches = bf.knnMatch(des1, des2, k=2)
good = [m for m,n in matches if m.distance < 0.75 * n.distance]

```

## 手写最小实现（理解原理）

```python
import numpy as np, cv2

def perona_malik_diffuse(img, iters=10, lam=0.15, k=0.03):
    """极简 Perona-Malik 各向异性扩散（教学用，单 octave 单层）"""
    L = img.astype(np.float32) / 255.0
    for _ in range(iters):
        n = L[:-2,1:-1] - L[1:-1,1:-1]
        s = L[2:,1:-1]  - L[1:-1,1:-1]
        e = L[1:-1,2:]  - L[1:-1,1:-1]
        w = L[1:-1,:-2] - L[1:-1,1:-1]
        c_n = np.exp(-(n**2)/(k*k))
        c_s = np.exp(-(s**2)/(k*k))
        c_e = np.exp(-(e**2)/(k*k))
        c_w = np.exp(-(w**2)/(k*k))
        L[1:-1,1:-1] += lam*(c_n*n + c_s*s + c_e*e + c_w*w)
    return (np.clip(L,0,1)*255).astype(np.uint8)

def akaze_naive_demo(img_path):
    img = cv2.imread(img_path, 0)
    L2 = perona_malik_diffuse(img, iters=5, k=0.05)
    L4 = perona_malik_diffuse(img, iters=20, k=0.05)
    return L2, L4  # 对应两个尺度层

```

## OpenCV 源码核心片段解读

OpenCV AKAZE 源码在 `modules/features2d/src/akaze.cpp`：

- `AKAZE::Compute_Nonlinear_Scale_Space()`：构造非线性尺度空间，内部调用 `fed_tvL1()` / `fed_g2()` / `fed_pm1()` / `fed_pm2()`（四种 diffusivity）
- `nldf_evolution_*()` 系列函数：单步 FED 更新，纯浮点像素循环，可 SIMD 优化
- `AKAZE::Compute_Detector_Hessian()`：每层算 Hessian 行列式
- `AKAZE::Compute_Main_Orientation_SURF()`：Haar 响应扇形滑动窗口
- `AKAZE::Compute_Descriptors_MLDB()`：M-LDB 描述子，按 grid 比 V/dx/dy

一个重要细节：OpenCV 默认把 diffusivity 设为 `DIFF_PM_G2`（g_2 = 1/(1 + |∇L|²/k²)），这是保边最强的选项，**不要随便改成 DIFF_PM_G1**，后者对噪声更敏感。
