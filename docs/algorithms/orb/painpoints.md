# ORB 实战踩坑

## 坑 1：描述子是 uint8 二进制，千万别用 NORM_L2

### 症状
```python
bf = cv2.BFMatcher(cv2.NORM_L2)  # ❌
matches = bf.knnMatch(des1, des2, k=2)
```
- 结果一堆错位匹配
- 距离值都很大（几百上千），ratio test 不工作
- 看起来像"ORB 不好用"

### 根因
`des` 的 dtype 是 `uint8`，**每个 uint8 里装的是 8 bit 的 0/1**，不是浮点数灰度。用 L2 距离算的是字节值差，完全不是二进制相似度。

### 避坑
```python
# WTA_K=2（默认）时用 NORM_HAMMING
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

# WTA_K=3 或 4 时用 NORM_HAMMING2（每 2 bit 一位）
# orb.setWTA_K(3)
# bf = cv2.BFMatcher(cv2.NORM_HAMMING2)
```

## 坑 2：edgeThreshold 太小导致边缘出一堆坏点

### 症状
- 图像边缘（黑边/边框）出现大量关键点
- 这些点匹配经常错，因为 patch 出界了

### 根因
ORB 要在关键点周围取 31×31 的 patch 算描述子，**太靠近边缘时 patch 取不全**，描述子不可靠。

### 避坑
```python
orb = cv2.ORB_create(
    edgeThreshold=31,  # 默认 31，等于 patchSize
    patchSize=31
)
```
如果图很小（<64px），要把 `edgeThreshold` 和 `patchSize` 都调小：
```python
orb = cv2.ORB_create(edgeThreshold=15, patchSize=15)  # 小图
```

## 坑 3：忘了转灰度图

### 症状
```
error: (-215:Assertion failed) _img.depth() == 0 || _img.depth() == 1 ...
```
或默默工作但结果不对。

### 根因
ORB 只接受 CV_8UC1（单通道 8bit 灰度）。

### 避坑
```python
gray = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
kp, des = orb.detectAndCompute(gray, None)
```

## 坑 4：nfeatures 设太小/太大

### 症状
- **设太小（100）**：关键点覆盖不足，匹配率低，RANSAC 内点不够
- **设太大（10000）**：匹配慢（O(N²)）、内存暴涨、误匹配多

### 推荐值

| 场景 | nfeatures |
|---|---|
| 图像拼接、物体识别 | **500~1500** |
| ORB-SLAM（关键帧） | 2000 |
| 实时跟踪/AR | 500~1000 |
| 模板匹配/小目标 | 300~500 |
| 全景/大图 | 2000~5000（配合 KD-Tree/FLANN） |

## 坑 5：scaleFactor 设得太激进

### 症状
- `scaleFactor=1.5`：大尺度跳变时匹配不上，小物体在某层被跳过
- `scaleFactor=1.1`：金字塔层数变多，速度明显变慢

### 根因
scaleFactor 是金字塔每层缩小的倍数。**值越大，层间尺度跨度越大，漏掉物体的概率越高**；值越小，层数越多越慢。

### 避坑
| 场景 | scaleFactor | nlevels |
|---|---|---|
| 默认通用 | 1.2 | 8 |
| 尺度变化大（远近变化） | 1.2 | 12~16 |
| 尺度固定（固定焦距） | 1.3 | 6 |
| 追求速度 | 1.4~1.5 | 6 |

## 坑 6：fastThreshold 太低出一堆弱角点

### 症状
- 边缘、天空、墙面等"伪角点"出很多
- 匹配时这些点对不上，增加噪声

### 根因
FAST 的亮度差阈值太小，任何微弱变化都当角点。

### 避坑
| 场景 | fastThreshold |
|---|---|
| 默认 | 20 |
| 光照好、对比度高 | 25~30 |
| 光照差、低对比度（夜景/低光） | 10~15 |

```python
orb = cv2.ORB_create(fastThreshold=20)
```

## 坑 7：跨尺度匹配失败（大物体 vs 小物体）

### 症状
一张是近景大图，一张是远景小图，匹配点很少。

### 根因
ORB 的图像金字塔是**离散的**，而且每层 scaleFactor=1.2，覆盖尺度范围有限。

### 避坑
1. **增加金字塔层数**：`nlevels=16`（覆盖尺度到 ~1.2¹⁵ ≈ 15 倍）
2. **调小 scaleFactor**：`scaleFactor=1.15` 让层间更密
3. **多张图/多种尺度分别匹配**再合并
4. 如果知道物体尺度范围，可以**提前 resize 图像**到相近尺度

## 坑 8：WTA_K 设错导致距离类型不对

### 症状
```python
orb.setWTA_K(3)
bf = cv2.BFMatcher(cv2.NORM_HAMMING)  # ❌ 应该用 HAMMING2
```
匹配报错或结果异常。

### 根因
- WTA_K=2：每个 bit 独立比较，用 NORM_HAMMING
- WTA_K=3/4：每次比较 3/4 个点，结果存 2 bit，必须用 **NORM_HAMMING2**（每 2 bit 为单位计数）

### 避坑
```python
orb = cv2.ORB_create(WTA_K=2)       # 默认
bf = cv2.BFMatcher(cv2.NORM_HAMMING)

# 或
orb.setWTA_K(3)
bf = cv2.BFMatcher(cv2.NORM_HAMMING2)
```

## 坑 9：ORB 对大视角变化鲁棒性差

### 症状
- 两个相机视角差 45° 以上，匹配点断崖式下降
- 平面匹配可用单应矩阵 RANSAC 救，但 3D 场景大视角基本失效

### 根因
rBRIEF 的旋转不变性只学到平面内旋转（around optical axis），**对 out-of-plane rotation（视角俯仰变化）本质上无法靠简单旋转补偿**。

### 避坑
- 尽量控制相机视角差在 30° 以内
- 大视角场景用 ASIFT（Affine SIFT）或深度学习特征（SuperPoint、DISK、LoFTR）
- SLAM 中通过关键帧/共视图保证相邻帧视角差小

## 坑 10：不做 RANSAC 几何验证

### 症状
- ratio test 后仍有很多错匹配（斜线）
- 单应矩阵/基础矩阵计算不稳定

### 根因
二进制描述子区分度比浮点低，**几何验证是必备**，不是可选。

### 避坑
```python
# 1) ratio test
good = [m for m, n in knn_matches if m.distance < 0.75 * n.distance]
# 2) RANSAC 找单应矩阵（平面场景）或基础矩阵（一般场景）
if len(good) >= 8:
    src = np.float32([kp1[m.queryIdx].pt for m in good])
    dst = np.float32([kp2[m.trainIdx].pt for m in good])
    # 平面: findHomography; 非平面: findFundamentalMat
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    inliers = [m for m, ok in zip(good, mask.ravel()) if ok]
```

## 坑 11：FLANN 二进制参数不对

### 症状
```python
FLANN_INDEX_KDTREE = 1
flann = cv2.FlannBasedMatcher(dict(algorithm=FLANN_INDEX_KDTREE, trees=5), ...)
```
对 ORB 二进制描述子效果极差。

### 根因
KD-Tree 是为浮点向量设计的，对二进制不好使。

### 避坑
二进制描述子用 **LSH（Locality Sensitive Hashing）**：
```python
FLANN_INDEX_LSH = 6
index_params = dict(
    algorithm=FLANN_INDEX_LSH,
    table_number=6,    # 哈希表数
    key_size=12,       # 哈希 key 大小
    multi_probe_level=1
)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)
```
不过实战中 **ORB 点数 < 5000 时 BFMatcher 比 FLANN 更快更稳**，不要迷信 FLANN。

## 常见错误速查表

| 错误 | 原因 | 解法 |
|---|---|---|
| `(-215) _img.depth() == 0` | 没转灰度 | cvtColor COLOR_BGR2GRAY |
| matcher 报数据类型错 | 用了 NORM_L2 | 改用 NORM_HAMMING |
| 边缘一堆坏点 | edgeThreshold 太小 | 设为 ≥patchSize(31) |
| 匹配点几乎全错 | 没做 ratio test+RANSAC | 必加 |
| 描述子为 None | 图像全黑/阈值太高 | 检查图像、降 fastThreshold |
| FLANN 匹配结果差 | 用了 KD-Tree | 点数少用 BF；否则用 LSH |
