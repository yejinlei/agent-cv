# SURF 源码走读

## ① OpenCV 调用（工业界标准用法）

```python
import cv2
import numpy as np

# ⚠️ SURF 在 opencv-contrib-python 里，主包没有
# pip install opencv-contrib-python

img = cv2.imread('lena.png', 0)  # 灰度图

# 1) 创建 SURF 检测器
surf = cv2.xfeatures2d.SURF_create(
    hessianThreshold=400,   # Hessian 响应阈值，越大点越少
    nOctaves=4,             # octave 数量
    nOctaveLayers=3,        # 每 octave 层数
    extended=False,         # False=64维, True=128维
    upright=False           # False=带方向（旋转不变），True=U-SURF
)

# 2) 检测关键点 + 计算描述子
kp, des = surf.detectAndCompute(img, mask=None)

print(f"关键点个数: {len(kp)}")
print(f"描述子形状: {des.shape}")  # (N, 64) 或 (N, 128)

# 3) 看每个关键点的属性
for i in range(min(5, len(kp))):
    p = kp[i]
    print(f"点{i}: 位置=({p.pt[0]:.1f},{p.pt[1]:.1f}), "
          f"尺度={p.size:.1f}, 方向={p.angle:.1f}°, "
          f"响应={p.response:.3f}")

# 4) 画出关键点
img_kp = cv2.drawKeypoints(img, kp, None, (0,255,0),
                           flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv2.imwrite('surf_keypoints.png', img_kp)
```

## ② 两张图匹配

```python
img1 = cv2.imread('box.png', 0)
img2 = cv2.imread('box_in_scene.png', 0)

surf = cv2.xfeatures2d.SURF_create(500)
kp1, des1 = surf.detectAndCompute(img1, None)
kp2, des2 = surf.detectAndCompute(img2, None)

# SURF 描述子是 float，用 FLANN 匹配（比 BFMatcher 快）
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)

matches = flann.knnMatch(des1, des2, k=2)

# Lowe 比值检验
good = [m for m, n in matches if m.distance < 0.75 * n.distance]

result = cv2.drawMatches(img1, kp1, img2, kp2, good, None,
                         flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
cv2.imwrite('surf_matches.png', result)
print(f"良好匹配点对: {len(good)}")
```

## ③ numpy 手写积分图（原理版）

```python
import numpy as np

def integral_image(img: np.ndarray) -> np.ndarray:
    """计算积分图，返回比原图大 1 像素的矩阵（首行首列为0）"""
    H, W = img.shape
    I = np.zeros((H+1, W+1), dtype=np.int64)
    # 行方向累加
    for y in range(1, H+1):
        row_sum = 0
        for x in range(1, W+1):
            row_sum += int(img[y-1, x-1])
            I[y, x] = I[y-1, x] + row_sum
    return I

def rect_sum(I: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> int:
    """用积分图算矩形 (x1,y1)~(x2,y2) 内的像素和（含两端，闭区间）"""
    # 转成积分图坐标系（左上角为原点，偏移1）
    a = I[y2+1, x2+1]
    b = I[y1,   x2+1]
    c = I[y2+1, x1]
    d = I[y1,   x1]
    return int(a - b - c + d)

# 测试
img = (np.random.rand(100, 100) * 255).astype(np.uint8)
I = integral_image(img)
# 验证：积分图算的和 与 直接切片求和是否相等
x1, y1, x2, y2 = 10, 20, 50, 70
s1 = rect_sum(I, x1, y1, x2, y2)
s2 = int(img[y1:y2+1, x1:x2+1].sum())
assert s1 == s2, f"{s1} != {s2}"
print("积分图验证通过 ✓")
```

## ④ numpy 手写 Fast-Hessian 近似响应（原理版）

```python
def box_filter_Dxx(I: np.ndarray, x: int, y: int, size: int) -> float:
    """
    用积分图近似 Lxx（Dxx 箱式滤波响应）。
    size: 滤波核边长（奇数）。
    Dxx 核结构：
      上 1/3: -1
      中 1/3: -1
      下 1/3: +1（注意：实际 SURF Dxx 分三块）
    简化说明：真实 Dxx 是中间一条 -2，上下两条 +1，对称。
    """
    # 真实 SURF Dxx 核（边长 size）：
    # 外框 h0=size//6, 中心 h1=(size-2*h0)//2
    h = size
    h2 = h // 2
    w2 = h // 2
    # 区域分为三段（垂直方向），外两段 +1，中间 -2
    third = h // 3
    # 上块
    top    = rect_sum(I, x-w2, y-h2,         x+w2, y-h2+third-1)
    # 中块
    middle = rect_sum(I, x-w2, y-third,      x+w2, y+third)
    # 下块
    bottom = rect_sum(I, x-w2, y+h2-third+1, x+w2, y+h2)
    Dxx = top - 2 * middle + bottom
    return Dxx

def box_filter_Dyy(I, x, y, size):
    """Dyy 是 Dxx 的旋转 90° 版本，水平方向分三段。"""
    h = size
    h2 = h // 2
    w2 = h // 2
    third = h // 3
    left   = rect_sum(I, x-w2,          y-h2, x-w2+third-1, y+h2)
    middle = rect_sum(I, x-third,       y-h2, x+third,      y+h2)
    right  = rect_sum(I, x+h2-third+1,  y-h2, x+w2,         y+h2)
    Dyy = left - 2 * middle + right
    return Dyy

def hessian_response(I, x, y, size):
    """近似 det(H) = Dxx*Dyy - (0.9*Dxy)^2"""
    Dxx = box_filter_Dxx(I, x, y, size)
    Dyy = box_filter_Dyy(I, x, y, size)
    # Dxy 实现略（四个象限），原理类似
    return Dxx * Dyy  # 简化版
```

> 实际工程中**强烈建议直接用 OpenCV 的 SURF**，手写版本主要用来理解积分图如何让任意尺度滤波都变成 O(1)。

## ⑤ Haar 小波响应（用积分图）

```python
def haar_x(I, x, y, size):
    """Haar dx：右半 − 左半"""
    h = size // 2
    left  = rect_sum(I, x-h, y-h, x-1, y+h)
    right = rect_sum(I, x+1, y-h, x+h, y+h)
    return right - left

def haar_y(I, x, y, size):
    """Haar dy：下半 − 上半"""
    h = size // 2
    top    = rect_sum(I, x-h, y-h, x+h, y-1)
    bottom = rect_sum(I, x-h, y+1, x+h, y+h)
    return bottom - top
```

## 源码关键实现参考

真正的工业级 SURF 实现（OpenCV `modules/xfeatures2d/src/surf.cpp`）核心要点：

1. **积分图**用 `cv::integral()` 算，数据类型用 `int` 或 `float`
2. **尺度金字塔**不采样图像，而是从 9×9 开始，每次尺寸 +6 递增
3. **描述子**生成时用查表的方式选采样点位置，每个采样点的 dx/dy 都用积分图算
4. **方向分配**时先把所有 Haar 响应存在数组里，再滑动窗口求最长向量方向
