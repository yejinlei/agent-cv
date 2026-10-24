# SURF 调参技巧

## ① hessianThreshold：最该调的一个参数

**默认 400**，直接决定关键点数量和质量。

| 场景 | 推荐值 | 大致点数（800×600 图） |
|---|---|---|
| 要稠密点（光流替代、三维重建） | 100 ~ 200 | 3000 ~ 8000 |
| **通用默认** | **400 ~ 500** | **500 ~ 2000** |
| 图像拼接、物体识别 | 500 ~ 800 | 300 ~ 1000 |
| 只想要最稳定点（快速匹配） | 1000 ~ 2000 | 50 ~ 300 |
| 大图（>2000px）/ 大尺度差 | 600 ~ 1000 | — |

**调参心法**：
1. 先用 500 跑一次，看 `len(kp)`
2. 点太多（>3000）→ 阈值乘 1.5
3. 点太少（<100）→ 阈值除以 2
4. 重复直到点在 500~1500 之间（匹配效率和覆盖率的甜点）

## ② extended：64 维还是 128 维？

| | 64 维（默认） | 128 维 |
|---|---|---|
| 匹配速度 | 基准 | 慢约 40%~80% |
| 内存 | 小 | 大 1 倍 |
| 区分度 | 好 | **略好** |
| 推荐场景 | **实时、移动端** | 精度优先、点少的精细匹配 |

**实操**：绝大多数场景 64 维足够；如果发现误匹配偏多（ratio test 后 good 点占比<10%）再试 128 维。

```python
surf = cv2.xfeatures2d.SURF_create(500, extended=True)  # 128维
```

## ③ upright：要不要旋转不变？

| 场景 | upright |
|---|---|
| **相机可能旋转**（手机拍照、手持设备） | **False**（默认） |
| **相机固定朝下/朝前**（工业检测、俯拍文档、扫描） | **True**（U-SURF，快约 15%，且方向不抖动） |

**经验法则**：
- 图像的地平线/文字方向基本固定 → True
- 全景拼接、SLAM、手持拍照 → False

## ④ nOctaves 与 nOctaveLayers：尺度金字塔

### 默认值
- nOctaves = 4（4 个倍频程）
- nOctaveLayers = 4（每 octave 4 层）

### 怎么调

| 场景 | nOctaves | nOctaveLayers |
|---|---|---|
| **默认通用** | **4** | **3~4** |
| 物体尺度差异大（大图里找小物体） | 5~6 | 4 |
| 近距离、尺度变化小（固定焦距拍摄） | 3 | 3 |
| 想要更快 | 3 | 2 |

**经验**：`nOctaves=4` 覆盖到 ~10 倍尺度，已经够大部分场景了，**很少需要超过 5**。

## ⑤ 与 SIFT / ORB 的选型对照

| 需求 | 选谁 | 理由 |
|---|---|---|
| 商业闭源、实时 | **ORB** | 免费、二进制、最快 |
| 高精度、不缺算力、商业可用 | **SIFT** | 专利 2020 年已到期，精度最高 |
| 科研/个人、要比 SIFT 快 | **SURF** | 约 3× 加速、精度接近 |
| 非线性尺度变化、强形变 | AKAZE | 非线性尺度空间，比 SURF 更鲁棒 |
| 嵌入式/CPU-only 实时 | **ORB** | 二进制描述子 Hamming 距离极快 |

## ⑥ 匹配阶段技巧

### 6.1 距离度量

SURF 描述子是 float，用 **L2 距离**：
```python
bf = cv2.BFMatcher(cv2.NORM_L2)  # 正确
# bf = cv2.BFMatcher(cv2.NORM_HAMMING)  # ❌ 这是给二进制描述子（ORB/BRISK）的
```

### 6.2 Lowe 比值检验（必加！）

```python
matches = flann.knnMatch(des1, des2, k=2)
good = []
for m, n in matches:
    if m.distance < 0.75 * n.distance:  # 经典 0.75
        good.append(m)
```

- 场景简单（清晰、光照好）→ 可以提高到 0.8（召回更多）
- 场景复杂（重复纹理、光照差）→ 降到 0.6~0.7（更严格）

### 6.3 交叉匹配（cross-check）

```python
bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
matches = bf.match(des1, des2)
```

交叉匹配只保留"1→2 最近且 2→1 最近"的点对，**误匹配显著减少**，但速度翻倍，适合点数少的场景。

## ⑦ 几何验证再加一层保险

RANSAC + 单应矩阵过滤错匹配（必做！）：

```python
if len(good) >= 4:
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    matches_mask = mask.ravel().tolist()
    good_inliers = [m for m, inlier in zip(good, matches_mask) if inlier]
    print(f"RANSAC 内点: {len(good_inliers)}/{len(good)}")
```

**RANSAC 阈值 5.0**（像素）是经典值，图像分辨率高可调到 5~10，分辨率低调到 3。

## ⑧ 典型参数模板

### 模板 A：实时 AR / SLAM（速度优先）
```python
surf = cv2.xfeatures2d.SURF_create(
    hessianThreshold=800, nOctaves=3, nOctaveLayers=3,
    extended=False, upright=True   # U-SURF，快
)
# 匹配：BF + crossCheck，点数少
```

### 模板 B：图像拼接（质量优先）
```python
surf = cv2.xfeatures2d.SURF_create(
    hessianThreshold=300, nOctaves=4, nOctaveLayers=4,
    extended=False, upright=False
)
# 匹配：FLANN + ratio test(0.75) + RANSAC
```

### 模板 C：物体识别（中等平衡）
```python
surf = cv2.xfeatures2d.SURF_create(
    hessianThreshold=500, nOctaves=4, nOctaveLayers=3,
    extended=True, upright=False   # 128 维，区分度高
)
# 匹配：FLANN + ratio test(0.7) + RANSAC
```

## ⑨ 什么时候不应该用 SURF

- **产品要闭源商业发布**：专利用不了
- **手机/嵌入式 30fps 实时**：SURF 还是不够快，用 ORB
- **深度学习时代**：现在特征点有 SuperPoint/DISK 等学习方法，传统 SURF 更多是教学/兜底方案
- **需要密集匹配**：用 SIFT 或 AKAZE，SURF 描述子稍粗

## 速查表

| 参数 | 默认 | 推荐调优范围 |
|---|---|---|
| hessianThreshold | 400 | 100~2000（越大点越少越稳） |
| nOctaves | 4 | 3~5 |
| nOctaveLayers | 3 | 2~4 |
| extended | False | 精度需求高→True |
| upright | False | 相机固定→True |
