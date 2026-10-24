# 源码走读：从 0 到 1 写一个标定脚本

> 张氏标定的代码非常短，核心就是"拍好照片 → 喂给 calibrateCamera"。但实际工程里的坑都在代码**外围**：怎么批量读图、怎么可视化角点、怎么判断哪张图是坏样本、怎么用标定结果去畸变和测量。

## 一、OpenCV 一行调用版（最简）

```python
import cv2, numpy as np, glob

# 1. 准备世界坐标（棋盘格点，z=0）
cols, rows, square = 9, 6, 25.0  # 9x6 内角点，格子边长 25mm
objp = np.zeros((cols*rows, 3), np.float32)
objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2) * square

obj_pts, img_pts = [], []
size = None

# 2. 遍历图像，检测角点
for f in sorted(glob.glob('calib_images/*.jpg')):
    img = cv2.imread(f)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    size = gray.shape[::-1]

    ret, corners = cv2.findChessboardCorners(gray, (cols, rows), None)
    if ret:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        obj_pts.append(objp)
        img_pts.append(corners2)
        # 可视化
        cv2.drawChessboardCorners(img, (cols, rows), corners2, ret)
        cv2.imshow('corners', img); cv2.waitKey(200)

cv2.destroyAllWindows()
print(f'成功检测到 {len(obj_pts)} 张标定图')

# 3. 标定！
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    obj_pts, img_pts, size, None, None)

print(f'重投影误差 RMSE: {ret:.4f} px')
print(f'内参 K:\n{K}')
print(f'畸变 dist (k1,k2,p1,p2,k3): {dist.ravel()}')

# 4. 保存
np.savez('calib.npz', K=K, dist=dist, rvecs=rvecs, tvecs=tvecs,
         size=size, rmse=ret)
```

## 二、工业级标定脚本（含质量评估 + 坏图剔除）

简单版有个大问题：**它不会告诉你哪张图拍坏了**。工业场景必须逐图评估重投影误差，把误差大的图删掉重拍。

```python
import cv2, numpy as np, glob, matplotlib.pyplot as plt

cols, rows, square = 9, 6, 25.0
objp = np.zeros((cols*rows, 3), np.float32)
objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2) * square

files = sorted(glob.glob('calib_images/*.jpg'))
obj_pts, img_pts, filenames = [], [], []

for f in files:
    img = cv2.imread(f)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (cols, rows), None)
    if ret:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        obj_pts.append(objp); img_pts.append(corners2)
        filenames.append(f)

# 首次标定
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(obj_pts, img_pts, gray.shape[::-1], None, None)
print(f'初始整体 RMSE: {ret:.4f} px')

# ====== 逐图评估，剔除误差过大的图 ======
def per_image_errors(obj_pts, img_pts, K, dist, rvecs, tvecs):
    errs = []
    for i in range(len(obj_pts)):
        proj, _ = cv2.projectPoints(obj_pts[i], rvecs[i], tvecs[i], K, dist)
        err = np.linalg.norm(proj - img_pts[i], axis=2).mean()
        errs.append(err)
    return np.array(errs)

errs = per_image_errors(obj_pts, img_pts, K, dist, rvecs, tvecs)
median = np.median(errs)
bad_idx = np.where(errs > median * 2.0)[0]  # 比中位数大 2 倍的视为坏图

print(f'坏图索引（误差 > {median*2:.3f}px）:')
for i in bad_idx:
    print(f'  {filenames[i]}  err={errs[i]:.3f} px')

# 剔除坏图后重新标定
good_idx = [i for i in range(len(obj_pts)) if i not in bad_idx]
obj_pts_g = [obj_pts[i] for i in good_idx]
img_pts_g = [img_pts[i] for i in good_idx]
ret2, K2, dist2, rvecs2, tvecs2 = cv2.calibrateCamera(obj_pts_g, img_pts_g, gray.shape[::-1], None, None)
print(f'剔除坏图后 RMSE: {ret2:.4f} px  ({len(obj_pts_g)}/{len(obj_pts)} 张)')

# ====== 可视化：每张图的误差柱状图 ======
errs2 = per_image_errors(obj_pts_g, img_pts_g, K2, dist2, rvecs2, tvecs2)
plt.figure(figsize=(12, 4))
plt.bar(range(len(errs2)), errs2)
plt.axhline(ret2, color='r', ls='--', label=f'overall RMSE={ret2:.3f}')
plt.xlabel('Image index'); plt.ylabel('Reprojection error (px)')
plt.title('Per-image reprojection error'); plt.legend()
plt.tight_layout(); plt.savefig('calib_errors.png', dpi=100)

# 保存最终结果
np.savez('calib_final.npz', K=K2, dist=dist2, rmse=ret2,
         rvecs=rvecs2, tvecs=tvecs2, n_images=len(obj_pts_g))
```

## 三、标定结果的典型应用

### 3.1 去畸变（最常用）

```python
# 加载标定参数
calib = np.load('calib_final.npz')
K, dist = calib['K'], calib['dist']

img = cv2.imread('test.jpg')
h, w = img.shape[:2]

# 方法一：直接 undistort（简单）
new_K, roi = cv2.getOptimalNewCameraMatrix(K, dist, (w, h), 1, (w, h))
dst = cv2.undistort(img, K, dist, None, new_K)
# 裁剪掉黑边
x, y, w, h = roi
dst_cropped = dst[y:y+h, x:x+w]

# 方法二：initUndistortRectifyMap + remap（视频用更快）
mapx, mapy = cv2.initUndistortRectifyMap(K, dist, None, new_K, (w, h), 5)
dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)  # 视频循环里只需这一行
```

::: tip alpha 参数
`getOptimalNewCameraMatrix(..., alpha, ...)` 中 alpha 控制保留多少原始像素：
- **alpha=1**：保留所有原图像素，边缘会有黑边
- **alpha=0**：裁剪到全是有效像素，可能丢失部分边缘
- **alpha=0.5**：折中（常用）
:::

### 3.2 已知像素坐标 + 平面，算真实世界坐标（平面测量）

如果已知目标在某个平面上（比如工件在传送带上 z=0），可以用单应反推真实坐标：

```python
def pixel_to_world(u, v, H_world_to_pixel, z=0):
    """已知像素(u,v)和世界平面z，反推(X,Y)"""
    H_inv = np.linalg.inv(H_world_to_pixel)
    p = np.array([u, v, 1.0])
    w = H_inv @ p
    X, Y = w[0]/w[2], w[1]/w[2]
    return X, Y

# 实际场景：拍一张放了棋盘的场景，用棋盘角点求 H
# 之后只要目标在棋盘平面上（z=0），就能从像素算出毫米坐标
```

这就是**视觉测量**的核心原理——手机拍 A4 纸测物体长度、工业视觉测零件尺寸，都用这个方法。

### 3.3 位姿估计（PnP：单图求外参）

标定后，用已知 3D 点 + 图像 2D 点可以求物体的位姿（这就是 AR、机械臂抓取的基础）：

```python
# 已知 3D 点（物体坐标系下，单位 mm）
obj_3d = np.array([[0,0,0], [50,0,0], [50,50,0], [0,50,0]], dtype=np.float32)
# 对应的图像 2D 点（手动点/特征点检测）
img_pts = np.array([[300,200], [400,205], [400,300], [295,295]], dtype=np.float32)

# 求解位姿
success, rvec, tvec = cv2.solvePnP(obj_3d, img_pts, K, dist)
R, _ = cv2.Rodrigues(rvec)
print(f'物体相对相机位置 (mm): {tvec.ravel()}')
```

### 3.4 双目标定 + 深度计算

```python
# 双目标定（stereoCalibrate）
ret, K1, dist1, K2, dist2, R, T, E, F = cv2.stereoCalibrate(
    obj_pts, img_pts1, img_pts2, K1, dist1, K2, dist2, size)

# 立体校正
R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(K1, dist1, K2, dist2, size, R, T)

# 计算视差 → 深度
# 视差 d -> 深度 Z = f*B/d，B 是基线长度
```

## 四、标定结果自检：怎么画重投影图

```python
def draw_reprojection(img, obj_pts, img_pts, K, dist, rvec, tvec):
    proj, _ = cv2.projectPoints(obj_pts, rvec, tvec, K, dist)
    vis = img.copy()
    for p_obs, p_proj in zip(img_pts.reshape(-1, 2), proj.reshape(-1, 2)):
        u1, v1 = p_obs.astype(int)
        u2, v2 = p_proj.astype(int)
        cv2.circle(vis, (u1, v1), 4, (0, 255, 0), 1)     # 观测点：绿色
        cv2.circle(vis, (u2, v2), 4, (0, 0, 255), 1)     # 重投影点：红色
        cv2.line(vis, (u1, v1), (u2, v2), (255, 0, 0), 1) # 误差线：蓝色
    return vis
```

绿点是观测到的角点，红点是模型投影的位置，蓝线是误差。**好的标定应该几乎看不到蓝线**。

## 五、OpenCV 源码里几个没写在文档里的细节

OpenCV 的 `calibrateCamera` 在 `modules/calib3d/src/calibration.cpp` 中实现，几个值得知道的细节：

1. **闭解默认启用**：如果 `cameraMatrix` 传 None，内部会自动用 `cvCalibrateCamera2Internal` 先做张氏闭解，再进 LM。如果你传了初值但没设 `CALIB_USE_INTRINSIC_GUESS`，初值会被忽略。

2. **内部使用 Levenberg-Marquardt**：`cv::calibrateCamera` 内部调 `cvLevMarq`，雅可比用**解析导数**（不是数值差分），所以收敛快且稳定。

3. **棋盘角点排序规则**：`findChessboardCorners` 总是把角点按"从左到右、从上到下"排序——但"哪是上"取决于棋盘朝向。所以**如果棋盘旋转 180° 拍，角点顺序不会自动对齐**（不过因为对称，不影响标定）。

4. **rational 模型的 8 个畸变参数**：k1~k6 + p1~p2，k4~k6 对应 $r^4, r^6, r^8$ 项的扩展——必须显式加 `CALIB_RATIONAL_MODEL` flag 才会估计。

5. **`CALIB_FIX_FOCAL_LENGTH` 的坑**：如果你设置了这个 flag 且没传初值，f 会固定在一个内部默认值（不是图像宽度）——大概率得到错误结果。**用 FIX 标志时一定要传正确初值**。

## 六、完整标定命令行工具（推荐写一个）

如果你做工业项目，建议写一个 `calibrate.py`：

```bash
# 推荐用法：
python calibrate.py --images calib/*.jpg --pattern 9x6 --square 25 \
                    --out calib.npz --vis --reject-threshold 0.5
```

参数包括：
- `--pattern 9x6`：内角点个数
- `--square 25`：格子边长（mm）
- `--reject-threshold 0.5`：单图误差超过多少像素自动剔除
- `--vis`：显示角点和重投影可视化
- `--no-tangent`：固定 p1=p2=0（镜头装得正）
- `--fisheye`：使用 fisheye 模型

这样团队里任何人拿到都能直接标，不用手写代码。
