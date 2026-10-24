# 对极几何源码走读

> 从「一行求 F」到「完整两视图重建」，再到「双目极线校正」，这一页给你能直接跑的代码。

## 档位一：求 F 并可视化对极线

```python
import cv2
import numpy as np

img1 = cv2.imread('left.jpg', cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread('right.jpg', cv2.IMREAD_GRAYSCALE)

# SIFT + 暴力匹配 + Lowe 比值
sift = cv2.SIFT_create()
k1, d1 = sift.detectAndCompute(img1, None)
k2, d2 = sift.detectAndCompute(img2, None)

bf = cv2.BFMatcher()
matches = bf.knnMatch(d1, d2, k=2)
good = [m for m, n in matches if m.distance < 0.75 * n.distance]

pts1 = np.float32([k1[m.queryIdx].pt for m in good])
pts2 = np.float32([k2[m.trainIdx].pt for m in good])

# 求基础矩阵
F, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC, 1.0, 0.999)
print(f'内点率：{mask.mean():.1%}')

# 画左图某个点的对极线到右图
def draw_epipolar_line(img1, img2, F, pt1):
    line = F @ np.array([pt1[0], pt1[1], 1.0])       # l' = F p
    a, b, c = line
    h, w = img2.shape
    x0, x1 = 0, w
    y0 = int(-(a * x0 + c) / b)
    y1 = int(-(a * x1 + c) / b)
    return cv2.line(cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR),
                    (x0, y0), (x1, y1), (0, 0, 255), 2)
```

## 档位二：完整两视图重建（可直接跑）

```python
import cv2
import numpy as np

def two_view_reconstruction(pts1, pts2, K):
    """从匹配点恢复 相机位姿 + 三维点"""
    # ① 求本质矩阵（RANSAC）
    E, mask = cv2.findEssentialMat(
        pts1, pts2, K,
        method=cv2.RANSAC, prob=0.999, threshold=1.0
    )
    if E is None or mask.sum() < 10:
        return None

    pts1_in = pts1[mask.ravel() == 1]
    pts2_in = pts2[mask.ravel() == 1]

    # ② 恢复位姿（recoverPose 自动选正深度解）
    n_inliers, R, t, mask_pose = cv2.recoverPose(E, pts1_in, pts2_in, K)
    print(f'内点数：{n_inliers}，平移方向：{t.ravel()}')

    # ③ 三角化
    P1 = K @ np.hstack([np.eye(3), np.zeros((3, 1))])
    P2 = K @ np.hstack([R, t])
    pts4d = cv2.triangulatePoints(P1, P2, pts1_in.T, pts2_in.T)
    pts3d = (pts4d[:3] / pts4d[3]).T

    # ④ 过滤：深度必须为正
    valid = pts3d[:, 2] > 0
    return R, t, pts3d[valid], pts1_in[valid], pts2_in[valid]
```

## 档位三：三角化质量过滤（工程必备）

```python
def filter_by_triangulation_angle(pts3d, R, t, min_angle_deg=2.0):
    """剔除三角化夹角过小的点（深度不可信）"""
    C1 = np.zeros(3)              # 左相机中心
    C2 = -R.T @ t.ravel()         # 右相机中心

    keep = []
    for i, P in enumerate(pts3d):
        v1 = P - C1
        v2 = P - C2
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 < 1e-6 or n2 < 1e-6:
            continue
        cos_a = np.clip(np.dot(v1, v2) / (n1 * n2), -1, 1)
        angle = np.degrees(np.arccos(cos_a))
        if angle > min_angle_deg:
            keep.append(i)
    return np.array(keep)
```

::: tip 为什么要做这个过滤
三角化误差 $\propto Z^2/(fB)$。当两条视线夹角很小时，深度几乎由噪声决定——这些点看着数值正常，实际**完全不可信**。SLAM/SFM 都会剔除它们。
:::

## 档位四：双目极线校正（对极几何的直接应用）

双目视觉里，把两个相机的图像**校正到对极线水平**，匹配就从二维搜索降到「同一行」搜索：

```python
def stereo_rectify(img1, img2, K1, d1, K2, d2, image_size):
    # 立体标定：求相对位姿
    flags = cv2.CALIB_FIX_INTRINSIC
    ret, K1, d1, K2, d2, R, T, E, F = cv2.stereoCalibrate(
        object_points, img_points1, img_points2,
        K1, d1, K2, d2, image_size, flags=flags
    )

    # 校正：让两图的对极线水平对齐
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
        K1, d1, K2, d2, image_size, R, T, alpha=0
    )

    # 生成映射表并重映射
    map1x, map1y = cv2.initUndistortRectifyMap(K1, d1, R1, P1, image_size, cv2.CV_32FC1)
    map2x, map2y = cv2.initUndistortRectifyMap(K2, d2, R2, P2, image_size, cv2.CV_32FC1)

    rect1 = cv2.remap(img1, map1x, map1y, cv2.INTER_LINEAR)
    rect2 = cv2.remap(img2, map2x, map2y, cv2.INTER_LINEAR)
    return rect1, rect2, Q
```

**校正后的效果**：同一个空间点在两张校正图里**在同一行**（$y_1 = y_2$），匹配只需横向搜索。

## 档位五：SLAM 前端的典型用法

```python
class TwoViewInitializer:
    """视觉 SLAM 的初始化：用对极几何估计初始位姿与地图点"""
    def __init__(self, K):
        self.K = K

    def initialize(self, pts1, pts2):
        # ① 尝试用 H（平面/纯旋转场景）
        H, mask_H = cv2.findHomography(pts1, pts2, cv2.RANSAC, 3.0)
        # ② 尝试用 F（一般场景）
        F, mask_F = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC, 1.0, 0.999)

        ratio_H = mask_H.mean() if mask_H is not None else 0
        ratio_F = mask_F.mean() if mask_F is not None else 0

        # ③ 谁的内点率高，就用谁
        if ratio_H > 0.6 and ratio_H > ratio_F:
            return self._from_homography(H, pts1, pts2), 'H'
        else:
            return self._from_fundamental(F, mask_F, pts1, pts2), 'F'

    def _from_fundamental(self, F, mask, pts1, pts2):
        pts1_in = pts1[mask.ravel() == 1]
        pts2_in = pts2[mask.ravel() == 1]
        E = self.K.T @ F @ self.K
        _, R, t, _ = cv2.recoverPose(E, pts1_in, pts2_in, self.K)
        return R, t, pts1_in, pts2_in
```

::: tip SLAM 里 H 和 F 为什么都要算
纯旋转（相机原地转头）时 F 退化，但 H 完美工作；有深度变化时反过来。工程上**两个都算，按内点率选**，这是 ORB-SLAM 初始化的标准做法。
:::

## OpenCV 源码级细节

| 细节 | 说明 |
|---|---|
| **`findFundamentalMat` 内部做归一化** | Hartley 归一化是默认步骤，不必手动做 |
| **7 点法可能返回多个 F** | `FM_7POINT` 最多返回 3 个解，需逐个验证 |
| **`findEssentialMat` 默认用 5 点法** | 传 `method=cv2.RANSAC` 时内部是 Nister 五点法 |
| **`recoverPose` 返回的是旋转 + 单位平移** | 平移只有方向，尺度需外部提供（双目用基线，单目靠其他约束） |
| **`triangulatePoints` 输入需为 2×N** | 注意转置，输出是 4×N 齐次坐标 |

## 多语言等价 API

| 语言/库 | 求 F | 求 E | 三角化 |
|---|---|---|---|
| Python OpenCV | `cv2.findFundamentalMat` | `cv2.findEssentialMat` | `cv2.triangulatePoints` |
| C++ OpenCV | `cv::findFundamentalMat` | `cv::findEssentialMat` | `cv::triangulatePoints` |
| scikit-image | — | — | — |
| COLMAP | 内置 | 内置 | 内置 |
| MATLAB CV Toolbox | `estimateFundamentalMatrix` | — | `triangulate` |

[← 上一篇：算法流程](./architecture) · [下一篇：实战与踩坑 →](./painpoints)
