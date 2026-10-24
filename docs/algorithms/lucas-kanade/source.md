# Lucas-Kanade 光流：源码走读

从三个层次带你看懂 LK：OpenCV 开箱调用 → 用 Numpy 手写核心 → 工业级完整 demo。

## 一、OpenCV 开箱调用（5 行核心）

这是最常用的形式，已经是工业级：

```python
import cv2, numpy as np

# ===== 初始化：在第 1 帧选点 =====
cap = cv2.VideoCapture("video.mp4")
ret, old_frame = cap.read()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

# ★ 关键 1：Shi-Tomasi 选点（参数含义见下）
feature_params = dict(maxCorners=200, qualityLevel=0.3, minDistance=7, blockSize=7)
p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

# ★ 关键 2：LK 参数
lk_params = dict(winSize=(15, 15),
                 maxLevel=3,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

mask = np.zeros_like(old_frame)      # 画轨迹用
color = np.random.randint(0, 255, (200, 3))

while True:
    ret, frame = cap.read()
    if not ret: break
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ★ 关键 3：前向 LK
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

    # ★ 关键 4：反向检查（Forward-Backward Error，强烈推荐）
    p0r, st_b, _ = cv2.calcOpticalFlowPyrLK(frame_gray, old_gray, p1, None, **lk_params)
    fb_err = np.linalg.norm(p0 - p0r, axis=2).reshape(-1)   # 回原位置的距离
    good = (st.reshape(-1) == 1) & (st_b.reshape(-1) == 1) & (fb_err < 2)

    good_new = p1[good]
    good_old = p0[good]

    # 画轨迹
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        a, b = new.ravel().astype(int)
        c, d = old.ravel().astype(int)
        mask = cv2.line(mask, (a, b), (c, d), color[i].tolist(), 2)
        frame = cv2.circle(frame, (a, b), 5, color[i].tolist(), -1)
    img = cv2.add(frame, mask)
    cv2.imshow("KLT Tracking", img)
    if cv2.waitKey(30) & 0xFF == 27: break

    # ★ 关键 5：更新 + 补点
    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1, 1, 2)

    if len(p0) < 50:          # 好点少于 50 个就补
        new_pts = cv2.goodFeaturesToTrack(frame_gray, mask=None, **feature_params)
        if new_pts is not None:
            p0 = np.vstack([p0, new_pts])[:200]   # 最多 200 个点

cv2.destroyAllWindows(); cap.release()
```

### 参数速调口诀
- **点不够跟**：`qualityLevel` 调低（0.01 甚至更低）、`maxCorners` 加大、`minDistance` 减小
- **点跑飞**：`winSize` 加大到 (21,21)、`maxLevel` 加到 4、必须加反向检查、`fb_err` 阈值 1~2
- **大位移跟不住**：`maxLevel=4~5`，`winSize` 加到 31
- **CPU 吃紧**：`maxCorners=100`，`winSize=(11,11)`，`maxLevel=2`

## 二、Numpy 手写金字塔 LK（教学版）

单步版本在上一页给出了，这里补金字塔 + 迭代版本（约 80 行）：

```python
def pyr_lk(prev, curr, points, win=15, max_level=3, n_iter=5):
    """金字塔 + 迭代 LK（教学版，非生产）"""
    # 1. 建金字塔
    pyr_prev, pyr_curr = [prev], [curr]
    for _ in range(max_level):
        pyr_prev.append(cv2.pyrDown(pyr_prev[-1]))
        pyr_curr.append(cv2.pyrDown(pyr_curr[-1]))

    H, W = prev.shape[:2]
    pts = points.reshape(-1, 2).astype(np.float64).copy() / (2 ** max_level)

    # 2. 自顶向下
    for L in range(max_level, -1, -1):
        p, c = pyr_prev[L], pyr_curr[L]
        Ix = cv2.Sobel(p, cv2.CV_64F, 1, 0, ksize=3)
        Iy = cv2.Sobel(p, cv2.CV_64F, 0, 1, ksize=3)
        half = win // 2

        # 迭代精化
        for _ in range(n_iter):
            dxs, dys = [], []
            for (x, y) in pts:
                xi, yi = int(round(x)), int(round(y))
                if xi<half or yi<half or xi>=p.shape[1]-half or yi>=p.shape[0]-half:
                    dxs.append(0); dys.append(0); continue
                # 双线性插值 warp 当前估计
                patch_curr = cv2.getRectSubPix(c, (win,win), (x,y))
                patch_prev = cv2.getRectSubPix(p, (win,win), (x,y))
                It = patch_curr.astype(np.float64) - patch_prev.astype(np.float64)
                Ixw = cv2.getRectSubPix(Ix, (win,win), (x,y))
                Iyw = cv2.getRectSubPix(Iy, (win,win), (x,y))
                Ixx = (Ixw*Ixw).sum(); Iyy = (Iyw*Iyw).sum(); Ixy = (Ixw*Iyw).sum()
                Ixt = (Ixw*It).sum();  Iyt = (Iyw*It).sum()
                det = Ixx*Iyy - Ixy*Ixy
                if abs(det) < 1e-10:
                    dxs.append(0); dys.append(0); continue
                dx = ( Iyy*(-Ixt) + (-Ixy)*(-Iyt)) / det
                dy = (-Ixy*(-Ixt) +  Ixx*(-Iyt)) / det
                dxs.append(dx); dys.append(dy)
            pts[:, 0] += np.array(dxs)
            pts[:, 1] += np.array(dys)

        if L > 0:
            pts *= 2      # 下一层分辨率加倍
    return pts.reshape(-1,1,2).astype(np.float32)
```

写完这个你就完全理解金字塔 + 迭代 + warp 的逻辑了。生产环境**永远**用 OpenCV 版本（它用 SIMD 优化，比手写快 50~100 倍）。

## 三、应用案例：视频稳像（10 行核心）

光流最常见的工业应用是视频稳像——算相机全局运动，反方向补偿：

```python
def stabilize(old_gray, frame_gray, p0):
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    good_old = p0[st.reshape(-1)==1]
    good_new = p1[st.reshape(-1)==1]
    # 用 LK 光流的点对估计仿射变换（刚体运动）
    M, inliers = cv2.estimateAffinePartial2D(good_old, good_new)
    # 提取平移 dx, dy
    dx, dy = M[0,2], M[1,2]
    # 反方向平移补偿
    T = np.float32([[1,0,-dx],[0,1,-dy]])
    stabilized = cv2.warpAffine(frame_gray, T, (frame_gray.shape[1], frame_gray.shape[0]))
    return stabilized, M
```

这就是手机/无人机电子防抖（EIS）的核心原理，比陀螺仪防抖还稳。

## 四、OpenCV 源码里你看不到的 3 个细节

1. **每层内部是怎么迭代的**
   OpenCV 在每层会做若干次迭代（由 `criteria.count` 控制）。每次迭代用当前估计 warp 下一帧，在残差上解 LK，直到位移变化小于 `criteria.epsilon`。这就是为什么 criteria 要设 `(EPS+COUNT, 30, 0.01)`。

2. **为什么返回 err 是"平均亮度差"**
   err = 窗口内 |I(x+u,y+v) - J(x,y)| 的平均，不是真 SSD。如果 err > 20 左右（在 uint8 尺度下），基本就是失败了。

3. **minEigThreshold 过滤的是什么**
   每个点都会先算 M 的最小特征值（除以窗口面积），小于 `minEigThreshold` 直接标 status=0，**根本不进入求解**。这步是为了在边缘/平坦点上省计算。默认值 1e-4 偏紧，噪点多的图像可以调到 1e-3。

4. **它用的是 Bouguet 2000 的金字塔实现，不是原始 LK**
   所以严格说函数名叫 "Lucas-Kanade" 是"致敬"，实现里是完整的迭代+金字塔+反向组合，和论文里的简单版差了 19 年的工程积累。

## 五、其他语言 / 库的等价 API

| 库 | API | 备注 |
|---|---|---|
| OpenCV (C++/Python) | `cv::calcOpticalFlowPyrLK` | 事实标准 |
| scikit-image | `skimage.registration.optical_flow_tvl1`（稠密）/ 无直接稀疏 LK | 适合教学 |
| Matlab | `vision.PointTracker` | 系统对象，自动管理点 |
| OpenMV (MicroPython) | `find_displacement()` 或 `sensor.ioctl(sensor.IOCTL_SET_LK_OPTICAL_FLOW, ...)` | 嵌入式，硬编码 8 点 |
| ROS | `viso2`、`opencv_apps/camshift`/`lk_flow` | ROS wrapper |
| Open3D | `RegistrationICP`（3D）、`compute_flow`（需自己接 LK） | 点云为主 |

**生产选型一句话**：Python/C++ 直接 OpenCV；嵌入式看 OpenMV/K210 是否满足精度；GPU 场景上 DeepFlow 或 RAFT。
