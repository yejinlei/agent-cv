# 源码走读 · RANSAC

> 这一页回答一个问题：**工程里到底怎么把 RANSAC 用起来？**
> 先讲 OpenCV 三个最常用的 API 各自在做什么，再手写一遍，
> 让你看清「采样 → 拟合 → 投票 → 重拟合」在代码里长什么样。

## 一、OpenCV 三大 API：99% 的场景都用它们

| API | 模型 | 最小样本 $s$ | 距离度量 | 典型用途 |
|---|---|---|---|---|
| `cv2.findHomography` | 单应矩阵 H | 4 | 重投影距离（px） | 图像拼接、文档矫正、平面测距 |
| `cv2.findFundamentalMat` | 基础矩阵 F / 本质矩阵 E | 8 或 7（5 点法为 5） | Sampson 距离（px） | 双目、SFM、对极几何 |
| `cv2.solvePnPRansac` | 相机位姿 (R, t) | 3~4 | 重投影误差（px） | 位姿估计、AR、机器人定位 |

### 1. findHomography：最常用

```python
import cv2
import numpy as np

# src_pts / dst_pts: N x 2 的 float32 数组（SIFT 匹配对）
H, mask = cv2.findHomography(
    src_pts, dst_pts,
    method=cv2.RANSAC,
    ransacReprojThreshold=3.0,   # 像素单位，默认 3.0
    maxIters=2000,
    confidence=0.995,
)
inliers = src_pts[mask.ravel() == 1]
```

**参数逐条拆**：

- `method`：`cv2.RANSAC`（标准）或 `cv2.LMEDS`（抗外点更强，但更慢）
- `ransacReprojThreshold`：**单位是像素**，指「目标点到投影点的距离」，3~5 px 是常规起点
- `maxIters`：迭代上限，只在置信度没达标时才跑满
- `confidence`：期望正确概率 $p$，默认 0.995

**返回值**：`H` 是 3×3 矩阵；`mask` 是 N×1 的 0/1 掩码，**别丢**——保留正确匹配对全靠它。

### 2. findFundamentalMat：注意阈值尺度

```python
F, mask = cv2.findFundamentalMat(
    pts1, pts2,
    method=cv2.FM_RANSAC,
    ransacReprojThreshold=1.0,   # Sampson 距离，1~3 px
    confidence=0.99,
)
```

`method` 可选 `FM_7POINT` / `FM_8POINT` / `FM_RANSAC` / `FM_LMEDS` / `USAC_*`。
**5 点法**（`cv2.findEssentialMat`）虽然只需 5 个点，但它是**非线性求解**，
比 8 点法慢，仅在点数少、需要最小样本时用。

### 3. solvePnPRansac：位姿估计

```python
ok, rvec, tvec, inliers = cv2.solvePnPRansac(
    object_points,    # N x 3，世界坐标
    image_points,     # N x 2，像素坐标
    K, dist_coeffs,
    reprojectionError=4.0,   # 像素
    iterationsCount=1000,
    confidence=0.99,
)
```

注意它返回的是 `(ok, rvec, tvec, inliers)` 四个值，和上面两个 API 的形态不一样。

## 二、手写一遍：直线拟合的 RANSAC（20 行）

```python
import numpy as np

def ransac_line(pts, t=2.0, max_iters=1000, seed=0):
    """pts: (N, 2) 点集；返回 (best_model, inlier_mask)"""
    rng = np.random.default_rng(seed)
    n = len(pts)
    best_count, best_mask = 0, None

    for _ in range(max_iters):
        i, j = rng.choice(n, size=2, replace=False)   # s = 2
        p1, p2 = pts[i], pts[j]
        d = p2 - p1
        norm = np.hypot(*d)
        if norm < 1e-8:                                # 退化：两点重合
            continue
        # 点到直线距离：|(p - p1) x d| / |d|
        dist = np.abs((pts[:, 0] - p1[0]) * d[1] -
                      (pts[:, 1] - p1[1]) * d[0]) / norm
        mask = dist < t
        if mask.sum() > best_count:
            best_count, best_mask = mask.sum(), mask

    # 重拟合：用全部内点做最小二乘
    inl = pts[best_mask]
    A = np.c_[inl[:, 0], np.ones(len(inl))]
    k, b = np.linalg.lstsq(A, inl[:, 1], rcond=None)[0]
    return (k, b), best_mask
```

**这段代码里每一行都对应论文里的一个概念**：

- `rng.choice(n, size=2)` → 最小样本采样
- `dist < t` → 内点判定
- `mask.sum() > best_count` → 一致性投票
- 最后的 `lstsq` → 重拟合

## 三、手写单应矩阵 RANSAC（$s = 4$）

```python
def collinear(pts):
    """判断 3 点是否近似共线"""
    x = pts[:, 0]
    y = pts[:, 1]
    area2 = (x[1] - x[0]) * (y[2] - y[0]) - (x[2] - x[0]) * (y[1] - y[0])
    return abs(area2) < 1e-6

def ransac_homography(src, dst, t=3.0, max_iters=2000, seed=0):
    rng = np.random.default_rng(seed)
    n = len(src)
    best_count, best_mask, best_H = 0, None, None

    for _ in range(max_iters):
        idx = rng.choice(n, size=4, replace=False)
        # 4 点中任意 3 点不能共线，否则解不出 H
        if collinear(src[idx]) or collinear(dst[idx]):
            continue
        H = cv2.getPerspectiveTransform(src[idx], dst[idx])

        # 把 src 投影过去，算重投影距离
        proj = cv2.perspectiveTransform(src.reshape(-1, 1, 2), H).reshape(-1, 2)
        dist = np.linalg.norm(proj - dst, axis=1)
        mask = dist < t
        if mask.sum() > best_count:
            best_count, best_mask, best_H = mask.sum(), mask, H

    # 用全部内点重拟合：method=0 表示纯最小二乘，不再跑 RANSAC
    best_H, _ = cv2.findHomography(src[best_mask], dst[best_mask], 0)
    return best_H, best_mask
```

两个细节：**① 退化检测**——3 点共线时 `getPerspectiveTransform` 会返回一个
数值爆炸的矩阵，必须先剔除；**② 重拟合时 `method` 传 0**，让 OpenCV
只做最小二乘、不再跑一遍 RANSAC。

## 四、OpenCV 内部做了什么

OpenCV 的 RANSAC 实现在 `modules/calib3d/src/ptsetreg.cpp`，
核心类是 `RANSACPointSetRegistrator`，流程和上面手写的完全一致，
但加了三处工程优化：

1. **自适应迭代次数**：每轮用当前最好模型算 $w$，用 $k = \dfrac{\log(1-p)}{\log(1-w^s)}$ 收缩上限，提前收敛。
2. **提前终止**：某轮内点数已覆盖到预设比例时直接返回。
3. **现代实现**：`cv2.USAC_*` 系列（OpenCV 4.5+）走 `usac` 模块，融合 PROSAC / LO-RANSAC，低内点率下明显更快更稳。

## 五、选型速查

| 需求 | 推荐 |
|---|---|
| 常规几何估计 | `cv2.RANSAC` |
| 内点率 < 30% | `cv2.USAC_MAGSAC` 或 PROSAC |
| 匹配质量差别大 | PROSAC（按匹配距离排序采样） |
| 需要确定性结果 | 固定随机种子，或 RANSAC 后再做一次最小二乘 |
| 点云配准 | Open3D `registration_ransac_based_on_feature_matching` |

## 下一步

- [⚠️ 踩坑指南](/algorithms/ransac/painpoints)：10 个典型坑
- [🎛️ 调参技巧](/algorithms/ransac/tricks)：$t$ 怎么定 + 7 个场景抄作业
- [📄 原始论文](/algorithms/ransac/paper)：Fischler & Bolles 1981
