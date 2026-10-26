---
title: 源码走读 — Harris 角点检测
outline: deep
---

# 源码走读：OpenCV Harris 与实战 demo

> 这一页给四个层级的代码：(1) OpenCV 一行调用；(2) Numpy 手写完整实现；(3) Shi-Tomasi + cornerSubPix 亚像素定位；(4) 视频 KLT 跟踪完整 demo。

## 一、OpenCV 一行调用（最常用）

```python
import cv2
import numpy as np

img = cv2.imread("chessboard.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# ① 直接调 Harris
gray_f = np.float32(gray)                       # ← 必须 float32
R = cv2.cornerHarris(gray_f, blockSize=2, ksize=3, k=0.04)

# ② 膨胀（仅为标记更显眼，不影响结果）
R = cv2.dilate(R, None)

# ③ 阈值化标红（阈值用 R.max() 的 1%）
img[R > 0.01 * R.max()] = [0, 0, 255]

cv2.imwrite("harris_quick.png", img)
```

### 易错点 1：忘记 `np.float32`

如果直接传 uint8 的 gray 进去，OpenCV 不会报错，但算出来的 R 值完全错误——因为内部用 CV_32F 累加，uint8 相乘会溢出。**这是新手第一大坑**。

### 易错点 2：阈值不能用固定值

R 值大小和图像整体亮度、对比度相关，**必须用 `thresh_ratio * R.max()`** 这种相对阈值，不能写死 `R > 10000`。

## 二、Numpy 完整手写（理解原理）

```python
import numpy as np
import cv2

def my_harris(img, blockSize=3, ksize=3, k=0.04, thresh=0.01):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # 预平滑
    gray = cv2.GaussianBlur(gray, (5,5), 1.4)

    # Sobel 梯度
    Ix = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=ksize)
    Iy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=ksize)

    Ix2 = Ix * Ix
    Iy2 = Iy * Iy
    Ixy = Ix * Iy

    # 窗口高斯加权
    sigma = 0.3 * (blockSize//2 - 1) + 0.8 if blockSize >= 3 else 0.5
    A = cv2.GaussianBlur(Ix2, (blockSize,blockSize), sigma)
    B = cv2.GaussianBlur(Iy2, (blockSize,blockSize), sigma)
    C = cv2.GaussianBlur(Ixy, (blockSize,blockSize), sigma)

    # R = det - k·tr²
    R = (A*B - C*C) - k * (A+B)**2

    # 非极大抑制（用 dilate 实现 3×3 max filter）
    R_max = cv2.dilate(R, np.ones((3,3), np.uint8))
    mask = (R > thresh * R.max()) & (R == R_max)
    ys, xs = np.where(mask)
    return np.column_stack([xs, ys]).astype(np.float32)

img = cv2.imread("chessboard.png")
pts = my_harris(img)
for (x,y) in pts:
    cv2.circle(img, (int(x),int(y)), 3, (0,0,255), -1)
cv2.imwrite("my_harris.png", img)
print(f"检测到 {len(pts)} 个角点")
```

**为什么用 dilate 当 NMS**：`cv2.dilate` 对每个像素取邻域最大值，所以 `R == R_dilated` 的位置就是邻域最大值点——这是一个 1 行 NMS 的经典 trick（Canny 里也用了类似思路）。

## 三、Shi-Tomasi + 亚像素定位（标定/跟踪标配）

标定棋盘格、KLT 光流跟踪**永远用这个组合**，不用裸 Harris：

```python
import cv2
import numpy as np

img = cv2.imread("chessboard.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# ① 找初始角点（Shi-Tomasi，自带 NMS 和 minDistance）
corners = cv2.goodFeaturesToTrack(
    gray,
    maxCorners=200,          # 最多返回 200 个
    qualityLevel=0.01,       # 质量 < 1% × max(R) 的丢掉
    minDistance=10,          # 角点之间最小距离 10 像素
    blockSize=3,
    useHarrisDetector=False, # 默认 Shi-Tomasi
    k=0.04
)
print(f"初始角点: {len(corners)}")

# ② 亚像素精化
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
corners_sub = cv2.cornerSubPix(
    gray, corners,
    winSize=(5,5),     # 搜索窗口 11×11
    zeroZone=(-1,-1),  # 无死区
    criteria=criteria
)

# ③ 画出来（红=整数像素，绿=亚像素精化后）
for c in corners:
    x,y = c.ravel()
    cv2.circle(img, (int(x),int(y)), 5, (0,0,255), 1)
for c in corners_sub:
    x,y = c.ravel()
    cv2.circle(img, (int(x),int(y)), 2, (0,255,0), -1)

cv2.imwrite("harris_subpixel.png", img)
```

亚像素精化后点的精度从 1 像素提到 **0.01 像素**——相机标定时必须用它，否则重投影误差会很差。

## 四、视频实时角点跟踪 demo（KLT 前置）

Harris 角点最常见的工业用途就是给 KLT 光流提供初始点。下面是一个完整的实时 demo：

```python
import cv2
import numpy as np

cap = cv2.VideoCapture(0)  # 或视频文件路径
if not cap.isOpened():
    raise RuntimeError("打不开摄像头")

# 初始化第一帧的角点
ret, old_frame = cap.read()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, maxCorners=100, qualityLevel=0.01,
                             minDistance=10, blockSize=3)
mask = np.zeros_like(old_frame)

# Lucas-Kanade 参数
lk_params = dict(winSize=(15,15), maxLevel=2,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 10, 0.03))

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 光流跟踪
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

    if p1 is not None:
        good_new = p1[st==1]
        good_old = p0[st==1]

        for i, (new, old) in enumerate(zip(good_new, good_old)):
            a,b = new.ravel().astype(int)
            c,d = old.ravel().astype(int)
            mask = cv2.line(mask, (a,b), (c,d), (0,255,0), 2)
            frame = cv2.circle(frame, (a,b), 5, (0,0,255), -1)

        img = cv2.add(frame, mask)
        cv2.imshow("Harris + KLT Tracking", img)

        # 点数太少就重新检测
        if len(good_new) < 30:
            p0 = cv2.goodFeaturesToTrack(frame_gray, 100, 0.01, 10, blockSize=3)
            mask = np.zeros_like(frame)
        else:
            p0 = good_new.reshape(-1,1,2)
        old_gray = frame_gray.copy()

    if cv2.waitKey(30) & 0xFF == 27:  # ESC 退出
        break

cap.release()
cv2.destroyAllWindows()
```

**为什么用 Shi-Tomasi 不用裸 Harris 喂 KLT**：实验证明 `min(λ₁,λ₂)` 判据选出来的点，跟踪稳定性比 R = det - k·tr² 高——KLT 原论文里推荐的就是 Shi-Tomasi。

## 五、OpenCV 源码级的 3 个细节

### 1. blockSize=2 为什么能是偶数？

多数核要求奇数尺寸，但 Harris 的 `blockSize=2` 是合法的——OpenCV 内部用 `blockSize×blockSize` 的**矩形盒滤波**（`boxFilter`）做窗口求和，不是高斯；`blockSize=2` 实际计算 2×2 区域。但实践中 3 或 5 效果更好。

### 2. borderType 为什么一般不改？

图像边界 1–2 像素没有完整窗口，OpenCV 用 BORDER_REFLECT_101 镜像填充，基本不会影响角点检测（角点很少恰好在边界）。

### 3. cornerHarris 的 float32 要求是硬约束吗？

OpenCV 4.x 允许传 CV_8U，内部会转 float32，但自己显式转更可控——尤其你自己手写 pipeline 时，float32 能避免 Ix² 溢出（uint8 梯度范围 [-255,255]，平方后 65025，uint8 容不下）。

## 六、输入/输出约定

| 项 | 约定 |
|---|---|
| 输入图 | BGR 三通道或灰度单通道 |
| 输入 dtype | `np.float32` 最稳 |
| R 值范围 | 可正可负，数量级通常 10⁴~10⁹，**必须用相对阈值** |
| 输出坐标 | `cv2.goodFeaturesToTrack` 返回 shape=(N,1,2) float32 |
| 亚像素精度 | `cornerSubPix` 后 ~0.01 像素 |

---

**下一篇**：[常见坑与踩雷指南 →](./painpoints)

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **harris** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="harris" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
