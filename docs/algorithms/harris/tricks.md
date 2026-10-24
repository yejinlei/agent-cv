---
title: 调参技巧与最佳实践 — Harris 角点检测
outline: deep
---

# 调参技巧与最佳实践

## 一、3 个核心参数的调参顺序

Harris 真正影响结果的只有 3 个参数：**blockSize、k、thresh_ratio**。调的时候按这个顺序：

```
① blockSize（看场景尺度）
    ↓
② k（看点数多少）
    ↓
③ thresh_ratio（最后过滤）
```

### Step 1：先定 blockSize

| 场景特征 | blockSize |
|---|---|
| 微观/高频细节（标定板、PCB、细纹理）| **2–3** |
| 一般自然场景 | **3** |
| 建筑/大结构/粗角点 | **5** |
| 远距离、图像压缩严重 | **5–7** |

### Step 2：再调 k

| 对点数的需求 | k |
|---|---|
| 宁少勿滥（标定、稳定跟踪）| **0.05–0.06** |
| 平衡（默认）| **0.04** |
| 宁多勿漏（图像检索、宽基线匹配）| **0.02–0.03** |

### Step 3：最后用 thresh_ratio 微调

| 想要的点密度 | thresh_ratio（相对 R.max()）|
|---|---|
| 极稀疏（每个角点都要是真的）| 0.05 |
| 稀疏 | 0.02 |
| 平衡（默认）| **0.01** |
| 密集 | 0.005 |
| 很密（后续再 RANSAC 筛）| 0.001 |

**经验**：先用 `goodFeaturesToTrack(maxCorners=500, qualityLevel=0.01, minDistance=10)` 当起点，根据结果再改 qualityLevel 和 minDistance——这比裸 Harris 省一半调参时间。

## 二、5 个场景的"抄作业"参数

### 场景 1：棋盘格标定板

```python
# 标定——直接用 findChessboardCorners，不要自己写 Harris
ret, corners = cv2.findChessboardCorners(gray, (9,6), None)
if ret:
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    corners = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
```

> 标定场景**绝对不要**自己调 Harris 找角点，OpenCV 的 `findChessboardCorners` 内置了多尺度、亚像素、几何约束，手写比不过。

### 场景 2：KLT 光流跟踪初始化

```python
# 光流——用 Shi-Tomasi，不要用裸 Harris
p0 = cv2.goodFeaturesToTrack(
    gray,
    maxCorners=200,
    qualityLevel=0.01,
    minDistance=10,
    blockSize=3
)
# 点数 <30 就重新检测
```

### 场景 3：图像拼接 / 宽基线匹配初始点

```python
# 拼接——要多、要均匀，阈值宽一点
p0 = cv2.goodFeaturesToTrack(gray, maxCorners=1000, qualityLevel=0.005,
                             minDistance=5, blockSize=3)
```

**为什么 minDistance 小**：宽基线匹配会丢很多点，初始点多才能保证 RANSAC 有足够内点。

### 场景 4：工业 PCB / 精密零件角点

```python
# 精密定位——blockSize 小、亚像素
gray = cv2.GaussianBlur(gray, (3,3), 0.8)
corners = cv2.goodFeaturesToTrack(gray, 500, 0.02, 8, blockSize=3)
corners = cv2.cornerSubPix(gray, corners, (5,5), (-1,-1),
    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.001))
```

### 场景 5：嵌入式/实时（树莓派、K210）

```python
# 实时——用 FAST 或降低分辨率
fast = cv2.FastFeatureDetector_create(threshold=20)
kp = fast.detect(gray, None)
# FAST 比 Harris 快 5–10 倍
```

**嵌入式上 Harris 跑不动 1080p 时的招**：先把图缩小到 320×240 再跑 Harris，再把坐标乘回原分辨率（亚像素精度会差一点但能接受）。

## 三、去伪角点的 5 种办法

Harris 会误报，工业里必须后处理：

### 办法 1：minDistance 强制均匀分布

`goodFeaturesToTrack` 的 `minDistance=10` 能让点在 10 像素内只留最强的那个——这是**最有效的单步去伪**。

### 办法 2：非极大抑制窗口加大

默认 NMS 是 3×3；伪点多时可以改成 5×5：

```python
R_dilated = cv2.dilate(R, np.ones((5,5), np.uint8))
```

### 办法 3：方向一致性过滤

真角点附近的梯度方向应该在 ±90° 内分散开（角是两条边交汇）；伪角点梯度方向往往单一（还是边缘）。这招手写要 10 行代码，用 `cv2.cornerEigenValsAndVecs` 能拿到主方向。

### 办法 4：多尺度一致性

在原图和下采样 1.5 倍的图上各跑一次 Harris，**两个尺度都被检出**的才留——能砍掉 70% 的假点。

### 办法 5：几何先验约束

标定板角点必须在棋盘格线上、物体角点必须在边缘交点附近——利用**应用层几何先验**过滤，效果远胜任何算子调参。

## 四、算法选型：Harris 还是 SIFT/FAST/ORB？

| 场景 | 用什么 | 原因 |
|---|---|---|
| 单纯找角点 / 跟踪初始化 | **Shi-Tomasi (goodFeaturesToTrack)** | 稳、自带 NMS、KLT 标配 |
| 需要尺度不变（远近都要检）| **SIFT/SURF** | 有尺度空间 |
| 实时 / 嵌入式 | **FAST** | 比 Harris 快 5–10 倍 |
| SLAM / 实时三维重建 | **ORB**（FAST + 方向 + BRIEF）| 免费、快、有旋转不变 |
| 标定棋盘格 | **findChessboardCorners** | 专门优化过，不要自己写 |
| 教学 / 理解原理 | **手写 Harris** | 数学最干净 |

**一句话**：Harris 是**学原理用的基准**，工业实际 80% 场景用 `goodFeaturesToTrack`（Shi-Tomasi），需要实时用 FAST，需要尺度/旋转用 ORB，需要专利没限制免费商用也用 ORB。

## 五、性能优化清单

1. **先高斯再 Sobel**，不要先 Sobel 再高斯——顺序错了会多做两次卷积
2. **下采样后再检测**，再把坐标乘回来：640×480 比 1920×1080 快 9 倍
3. **ROI 检测**：只在你关心的区域跑 Harris，不要整图
4. **积分图加速**（工业 CV 库如 HALCON 常用）：窗口求和用积分图像 O(1) 算，和 blockSize 无关
5. **用 FAST 替代**：如果不需要 Harris 的"边/角/平坦统一判据"，FAST 快一个量级

## 六、调参日记示范

假设你在做 PCB 焊点定位，按这个顺序调：

1. **blockSize=3, k=0.04, thresh=0.01** 起步 → 检出 500+ 点，很多假点
2. **thresh 升到 0.02** → 点降到 200，仍然有一些在丝印边缘的伪点
3. **minDistance 加到 8**（goodFeaturesToTrack）→ 点更均匀
4. 加上 **cornerSubPix** → 坐标从整数精度变亚像素，定位误差从 1.5 像素降到 0.1 像素
5. 还剩的几个伪点用**焊点几何先验**（圆形、亮度）过滤掉

**最终**：每个焊点稳定检出一个亚像素角点，定位精度满足要求。

---

**↩ 返回 [Harris 总览](./index) · ↩ 返回 [算法档案首页](../)**
