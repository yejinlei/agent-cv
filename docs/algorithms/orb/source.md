# ORB 源码走读

## ① OpenCV 标准调用

```python
import cv2
import numpy as np

img = cv2.imread('lena.png', 0)  # 灰度图

# 1) 创建 ORB 检测器
orb = cv2.ORB_create(
    nfeatures=1000,          # 最多返回的关键点数量
    scaleFactor=1.2,         # 金字塔每层缩放比
    nlevels=8,               # 金字塔层数
    edgeThreshold=31,        # 边缘屏蔽距离（≥patchSize）
    firstLevel=0,
    WTA_K=2,                 # τ 测试每次比几个点
    scoreType=cv2.ORB_HARRIS_SCORE,  # 或 ORB_FAST_SCORE
    patchSize=31,            # 描述子 patch 尺寸
    fastThreshold=20         # FAST 阈值
)

# 2) 检测 + 计算
kp, des = orb.detectAndCompute(img, mask=None)

print(f"关键点: {len(kp)}")
print(f"描述子 dtype: {des.dtype}, shape: {des.shape}")
# 例: uint8, (N, 32)  ← 256 bit = 32 字节

# 3) 看关键点
for p in kp[:5]:
    print(f"位置=({p.pt[0]:.1f},{p.pt[1]:.1f}), 尺度={p.size:.1f}, "
          f"方向={p.angle:.1f}°, 响应={p.response:.3f}, octave={p.octave}")

# 4) 绘制
out = cv2.drawKeypoints(img, kp, None, color=(0,255,0),
                        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv2.imwrite('orb_keypoints.png', out)
```

## ② 两张图匹配（Hamming 距离！）

```python
img1 = cv2.imread('box.png', 0)
img2 = cv2.imread('box_in_scene.png', 0)

orb = cv2.ORB_create(1000)
kp1, des1 = orb.detectAndCompute(img1, None)
kp2, des2 = orb.detectAndCompute(img2, None)

# ⚠️ ORB 描述子是二进制 uint8，必须用 NORM_HAMMING！
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)
matches = sorted(matches, key=lambda x: x.distance)  # 按距离排序

# 画前 30 个最好匹配
res = cv2.drawMatches(img1, kp1, img2, kp2, matches[:30], None,
                      flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
cv2.imwrite('orb_matches.png', res)
```

::: warning 千万别用 NORM_L2！
ORB 的 des 是 uint8（0/255 代表 0/1 bit），用 NORM_L2（欧氏距离）算出来的是 **32 个字节的数值差**，完全没有意义——必须用 `NORM_HAMMING` 或 `NORM_HAMMING2`（WTA_K=3 或 4 时）。
:::

## ③ KNN + ratio test 版（更稳健）

```python
bf = cv2.BFMatcher(cv2.NORM_HAMMING)
matches = bf.knnMatch(des1, des2, k=2)

good = []
for m, n in matches:
    if m.distance < 0.75 * n.distance:
        good.append(m)

# RANSAC 单应矩阵（必加！）
if len(good) >= 4:
    src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    dst = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    print(f"RANSAC 内点: {mask.sum()}/{len(good)}")
```

## ④ numpy 手写 FAST 角点（原理版）

```python
import numpy as np

def fast_detect(img: np.ndarray, t: int = 20, n_contig: int = 9):
    """
    简易 FAST-9 角点检测
    img: 单通道 uint8
    t: 亮度阈值
    n_contig: 连续 N 点亮/暗才算角点（9 或 12）
    返回: [(x,y), ...]
    """
    H, W = img.shape
    # Bresenham 半径=3 的 16 个圆上点，按顺时针从 3 点钟方向开始
    circle = [(3,0),(3,1),(2,2),(1,3),(0,3),(-1,3),(-2,2),(-3,1),
              (-3,0),(-3,-1),(-2,-2),(-1,-3),(0,-3),(1,-3),(2,-2),(3,-1)]
    # 四个锚点（上/右/下/左 = 索引 1,5,9,13）
    anchors = [1, 5, 9, 13]
    kps = []
    for y in range(3, H-3):
        for x in range(3, W-3):
            Ip = int(img[y, x])
            # 取 16 个圆上像素
            pix = [int(img[y+dy, x+dx]) for dx, dy in circle]
            bright = [p > Ip + t for p in pix]
            dark   = [p < Ip - t for p in pix]
            # 锚点初筛：必须至少有 3 个亮或 3 个暗
            b_anch = sum(bright[i] for i in anchors)
            d_anch = sum(dark[i]   for i in anchors)
            if b_anch < 3 and d_anch < 3:
                continue
            # 检查完整 16 点是否有连续 n_contig 个亮/暗
            for cond in (bright, dark):
                doubled = cond + cond
                run = 0
                found = False
                for v in doubled:
                    run = run + 1 if v else 0
                    if run >= n_contig:
                        found = True
                        break
                if found:
                    kps.append((x, y))
                    break
    return kps

# 测试
img = cv2.imread('lena.png', 0)
kps = fast_detect(img, t=20, n_contig=9)
print(f"FAST 角点: {len(kps)}")
```

> 真实 OpenCV FAST 用**决策树**（ID3 训练的判断顺序）优化，速度是这个朴素版本的 10 倍以上，但核心判断逻辑一致。

## ⑤ numpy 手写灰度质心法（方向）

```python
import math

def ic_angle(img: np.ndarray, cx: int, cy: int, half_k: int = 15):
    """灰度质心法返回主方向（弧度）"""
    m01 = 0
    m10 = 0
    for dy in range(-half_k, half_k+1):
        # 只计算圆形内的点（u 形扫描）
        dx_r = int(math.sqrt(half_k*half_k - dy*dy))
        for dx in range(-dx_r, dx_r+1):
            v = int(img[cy+dy, cx+dx])
            m10 += dx * v
            m01 += dy * v
    return math.atan2(m01, m10)
```

## ⑥ numpy 手写 Hamming 距离匹配

```python
def hamming_distance(a: np.ndarray, b: np.ndarray) -> int:
    """两个 32 字节 uint8 向量的汉明距离"""
    return int(np.unpackbits(np.bitwise_xor(a, b)).sum())

def bf_match(des1: np.ndarray, des2: np.ndarray):
    """暴力匹配：对 des1 每个点找 des2 中 Hamming 最近的点"""
    matches = []
    for i, d1 in enumerate(des1):
        best_d = 257
        best_j = -1
        for j, d2 in enumerate(des2):
            d = hamming_distance(d1, d2)
            if d < best_d:
                best_d = d
                best_j = j
        matches.append((i, best_j, best_d))
    return matches
```

**真实 OpenCV 实现**用 POPCNT 指令 + 多线程，比这个快 50~100 倍，但算法一致。

## OpenCV 源码核心文件参考

- `modules/features2d/src/orb.cpp`：ORB 实现主体
  - `computeOrbPyramidKeypoints`：金字塔 + FAST
  - `computeKeyPoints`：Harris 评分 + 选点
  - `computeDescriptors`：rBRIEF 旋转 + 比较
  - `pattern` 常量：预训练的 512 个点坐标（256 对）
- `modules/features2d/src/fast.cpp`：FAST 角点检测（决策树版）
