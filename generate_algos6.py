#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第三批：几何视觉+跟踪：sgbm, pnpsolver, icp, homography, horn-schunck, farneback, camshift"""
import sys
sys.path.insert(0, "/home/user/workspace/7648064683708846935/agent-cv")
from generate_algos3 import build_algo

build_algo(
    "sgbm",
    meta=dict(
        name="SGM 半全局立体匹配", en="Semi-Global Matching",
        branch="geometry", year="2005", author="Heiko Hirschmüller",
        chapter="ch-14-3d-vision", level="advanced",
        tagline="双目测距的工业标准，8 个方向做平滑约束，又快又稳出稠密视差图",
        analogy="BM 块匹配像个没耐心的小孩，只看自己周围一小圈就乱猜；SGM 像个老练的侦探，从上下左右斜 8 个方向打听消息，让相邻像素的深度差不多，拼出连贯的深度图",
        scene="双目深度相机（RealSense、自动驾驶双目）、无人机避障、机器人导航、三维重建、工业检测",
        pros=["稠密视差图","速度可接受(CPU实时)","精度经典最高","OpenCV内置StereoSGBM","参数可解释"],
        cons=["参数多","无纹理区域失败","重复纹理误匹配","需要精确标定","远处深度误差大"]),
    concepts=[
        ("视差 Disparity",
         "双目相机左右水平放置，同一空间点在左图坐标 x_L、右图坐标 x_R，**视差 d = x_L - x_R**。深度 Z = f·B/d，其中 f 是焦距、B 是基线距离。**视差越大=越近，视差越小=越远**。",
         None),
        ("匹配代价",
         "对左图每个像素 (x,y) 和可能视差 d，算右图 (x-d,y) 位置的像素**相似度（代价）**。常用：BT（Birchfield-Tomasi）、Census 变换、互信息 MI。代价越小，这个视差越可能是真的。",
         None),
        ("半全局聚合",
         "如果只看单像素最小代价，得到的视差图全是噪声。SGM 沿**8 或 16 个方向**做动态规划路径聚合，每条路径上对**视差突变**加惩罚 P1（小跳变）和 P2（大跳变），让相邻像素视差趋于一致。",
         "flowchart TB\n  A[\"逐像素代价值 C(p,d)\"] --> B[\"沿 8/16 方向<br/>做 1D 动态规划\"]\n  B --> C[\"路径代价聚合 S(p,d)\"]\n  C --> D[\"每个像素选 argmin_d S(p,d)\"]\n  D --> E[\"稠密视差图 ✅\"]"),
        ("P1/P2 惩罚",
         "P1 惩罚相邻像素视差差 1 的情况（斜面，允许）；P2 惩罚视差差 >1 的情况（跳变，重罚）。**P1 控制平滑度，P2 控制对不连续的保留**。P2 通常与相邻像素灰度差成反比（灰度差大→很可能真是深度跳变→少罚）。",
         None),
        ("WLS 后处理",
         "OpenCV 提供 ximgproc 的 `DisparityWLSFilter`：用左右一致性检查（左右视差图一致性）过滤错误点，用加权最小二乘做边缘保留的视差图平滑，效果显著提升。",
         None),
    ],
    arch_steps=[
        ("双目标定+校正", "先标定获取内参、外参、畸变，双目校正把左右图对准（极线水平）"),
        ("代价计算", "对每个像素、每个视差级别计算匹配代价（BT/Census）"),
        ("代价聚合", "沿 8/16 方向用 P1/P2 做动态规划路径聚合"),
        ("WTA 选最优", "每个像素选聚合代价最小的视差"),
        ("亚像素细化", "对视差抛物线拟合获得亚像素精度（SGBM 内部分 16 份）"),
        ("左右一致性检查", "算左→右和右→左两张视差图，不一致的点打为无效"),
        ("WLS 滤波", "用导向滤波/WLS 平滑视差图，保留边缘"),
        ("视差→深度", "Z = f·B / d（用 reprojectImageTo3D 直接出点云）"),
    ],
    opencv='''imgL = cv2.imread("left.jpg", 0)
imgR = cv2.imread("right.jpg", 0)
min_disp = 0
num_disp = 16*5   # 必须是 16 的倍数
block = 11
stereo = cv2.StereoSGBM_create(
    minDisparity=min_disp, numDisparities=num_disp, blockSize=block,
    P1=8*3*block**2, P2=32*3*block**2,
    disp12MaxDiff=1, uniquenessRatio=15,
    speckleWindowSize=100, speckleRange=2,
    preFilterCap=63, mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
)
disp = stereo.compute(imgL, imgR).astype(np.float32) / 16.0
# WLS 滤波后处理（需 opencv-contrib）
right_matcher = cv2.ximgproc.createRightMatcher(stereo)
disp_r = right_matcher.compute(imgR, imgL).astype(np.float32)/16.0
wls = cv2.ximgproc.createDisparityWLSFilter(stereo)
wls.setLambda(8000); wls.setSigmaColor(1.5)
disp_f = wls.filter(disp, imgL, disparity_map_right=disp_r)
# 视差转深度
points3d = cv2.reprojectImageTo3D(disp_f, Q)''',
    numpy_impl='''# SGM 完整实现很长（8 方向 DP），这里给出 Census 代价核心
def census_transform(img, win=9):
    h, w = img.shape
    half = win//2
    out = np.zeros((h,w), dtype=np.uint64)
    for y in range(half, h-half):
        for x in range(half, w-half):
            center = img[y,x]
            val = 0; idx = 0
            for dy in range(-half, half+1):
                for dx in range(-half, half+1):
                    if dx==0 and dy==0: continue
                    val <<= 1
                    if img[y+dy,x+dx] > center: val |= 1
                    idx += 1
            out[y,x] = val
    return out
def census_cost(cL, cR, d, y, x):
    return bin((cL[y,x]^cR[y,x-d]).item()).count('1')''',
    pitfalls=[
        ("numDisparities 不是 16 的倍数", "报错或结果奇怪。",
         "**numDisparities 必须是 16 的整数倍**（16/32/48/…/256）。"),
        ("P1/P2 乱填", "视差图要么全是阶梯状（平滑过强），要么全是噪声（平滑不足）。",
         "**P1=8·3·block²，P2=32·3·block²** 是官方推荐；P2 一般是 P1 的 4 倍。"),
        ("忘记除以 16.0", "视差值都是 16 的倍数（看起来有 16 层阶梯）。",
         "SGBM 输出是**定点 16 位小数**（4 位小数），必须 `.astype(np.float32)/16.0`。"),
        ("minDisparity 设错", "目标很近但 minDisparity 太大，导致前景一片黑。",
         "minDisparity 默认 0；如果相机有会聚角导致无穷远视差不为 0，需要调整。"),
        ("没做双目标定/校正直接喂图", "视差图满屏噪声。",
         "SGBM **必须**基于校正后的图（极线水平）。先 `stereoCalibrate + stereoRectify + initUndistortRectifyMap + remap`。"),
        ("没有 WLS 后处理，视差图全是孔洞", "直接用 SGBM 输出，很多无效区域（值=min_disp-1）。",
         "**强烈建议用 DisparityWLSFilter**，同时配 disp12MaxDiff、speckle 过滤。"),
    ],
    koujue="""视差倍数十六个，少了报错多了慢；
block 取 5 到 11，小的细节多大的平滑；
P1 八倍三乘 block 平方，P2 四倍于 P1 不瞎跑；
uniqueness 十五，speckle 一百加二；
输出除十六得浮点，不然是阶梯块状；
必须先做双目标定校正，不然结果全是噪；
要好看上 WLS 滤波，八千 lambda 一点五 sigma。""",
    params=[
        ("numDisparities", "视差搜索范围", "64-128", "适合近景", "适合远景"),
        ("blockSize", "匹配块大小", "11", "平滑", "细节多"),
        ("P1", "视差变化±1 惩罚", "8*3*block²", "平滑", "保留细节"),
        ("P2", "视差大跳变惩罚", "32*3*block²", "保留边界", "过度平滑"),
        ("uniquenessRatio", "唯一性比率", "10-15", "匹配严", "匹配宽松"),
    ],
    tips=[
        ("标定质量决定一切",
         "先拍 20+ 对棋盘图，标定重投影误差要 **< 0.3 像素**。超过 0.5 像素 SGBM 就开始出现误匹配。标定时注意光照均匀、棋盘覆盖全画面。"),
        ("基线选择",
         "经验：**基线 B ≈ 最短工作距离 / 20**（如 1 米工作距离，基线 5cm）。基线太短→远处深度误差大；基线太长→近景视差超出 numDisparities。"),
        ("深度误差公式",
         "深度精度 ∝ Z²/(f·B)。距离翻倍，误差翻 4 倍。所以双目相机对**近距离精度高、远距离差**，10 米外基本没法用。"),
    ],
    perf=[
        ("StereoSGBM (640×480, num=64)", "~40 ms", "CPU 单线程"),
        ("StereoSGBM (1280×720, num=128)", "~200 ms", "CPU"),
        ("+WLS 滤波", "+~30% 时间", "效果显著提升"),
    ],
    notes=""
)

build_algo(
    "pnpsolver",
    meta=dict(
        name="PnP 位姿估计", en="Perspective-n-Point",
        branch="geometry", year="1841/2009(EPnP)", author="Grunert / Lepetit(EPnP)",
        chapter="ch-14-3d-vision", level="advanced",
        tagline="已知几个 3D 点和它们在图上的位置，反推出相机在哪里看——AR 和机器人抓取的基石",
        analogy="你站在房间里，认出了墙上的钟、桌上的杯子、书架上的花盆——这三个东西真实位置你知道，就能反推出自己站在房间的什么地方、朝什么方向看",
        scene="AR 标记跟踪、机械臂抓取、视觉伺服、无人机着陆、AR 虚拟物体叠加、SLAM 位姿求解",
        pros=["最少 3 点可解(P3P)","毫秒级","RANSAC 鲁棒","OpenCV 内置多种方法","精度高"],
        cons=["需要已知内参","3D 点精度要高","点共面/共线退化","对外点敏感","单位易搞错"]),
    concepts=[
        ("n 点透视问题",
         "已知 n 个 3D 点在世界坐标系的位置，以及它们在图像上的 2D 投影，求相机外参 [R|t]（相机相对于世界坐标系的旋转+平移，共 6DoF）。这就是经典的 PnP（Perspective-n-Point）问题。",
         None),
        ("3D-2D 对应",
         "核心方程是投影公式：s·p = K[R|t]·P，其中 P 是 3D 点齐次坐标、p 是 2D 像素齐次坐标、K 是内参、[R|t] 是外参。n 对 (P_i, p_i) 给你，求 R 和 t。",
         None),
        ("P3P 与 EPnP",
         "P3P：3 对点最多 4 个解，需要第 4 点消歧；EPnP（Lepetit 2009）：把 3D 点表示为 4 个虚拟控制点的加权和，复杂度 O(n)，是现代最常用方法；Iterative：基于 Levenberg-Marquardt 迭代最小化重投影误差，精度最高但慢。",
         None),
        ("RANSAC 抗外点",
         "实际场景匹配往往有误匹配（外点），`solvePnPRansac` 会多次随机采样最小子集求解并选内点最多的模型，鲁棒性强。",
         None),
    ],
    arch_steps=[
        ("准备数据", "已知内参 K、畸变系数 dist、n 对 (3D 点世界坐标, 2D 像素坐标)"),
        ("去畸变或用 dist", "可以直接带畸变参数调用，OpenCV 内部处理"),
        ("选择方法", "P3P(需4+点) / EPnP / ITERATIVE / DLS / AP3P / SQPnP"),
        ("求解", "cv2.solvePnP(obj, img, K, dist, rvec, tvec, useExtrinsicGuess, flags)"),
        ("RANSAC 版本", "solvePnPRansac 自动排除外点，返回 inliers 掩码"),
        ("Rodrigues 变换", "输出 rvec 是旋转向量，用 cv2.Rodrigues 转旋转矩阵 R"),
        ("精度评估", "用 projectPoints 重投影计算重投影误差（<1-2 像素为好）"),
    ],
    opencv='''# 3D 点（单位: 米或 mm，但单位要和 t 一致）
obj_pts = np.array([
    [0,0,0], [0.1,0,0], [0.1,0.1,0], [0,0.1,0],   # 正方形四个角 (10cm)
], dtype=np.float32)
# 2D 像素点
img_pts = np.array([[300,200],[400,205],[405,300],[295,295]], dtype=np.float32)
K = np.array([[800,0,320],[0,800,240],[0,0,1]], dtype=np.float32)
dist = np.zeros(5)
# 求解（RANSAC 版）
success, rvec, tvec, inliers = cv2.solvePnPRansac(
    obj_pts, img_pts, K, dist, iterationsCount=100,
    reprojectionError=8.0, confidence=0.99, flags=cv2.SOLVEPNP_EPNP
)
# 旋转向量转旋转矩阵
R, _ = cv2.Rodrigues(rvec)
print("相机位姿：\nR =", R, "\nt =", tvec)
# 重投影验证
proj, _ = cv2.projectPoints(obj_pts, rvec, tvec, K, dist)
err = np.linalg.norm(proj.reshape(-1,2)-img_pts, axis=1).mean()
print(f"重投影误差: {err:.3f} px")''',
    numpy_impl='''# PnP 完整实现较复杂（DLT+非线性优化），这里给 DLT 线性解
def pnp_dlt(obj_pts, img_pts, K):
    """直接线性变换（DLT）求位姿（需要 ≥6 点，精度一般，给初值用）"""
    K_inv = np.linalg.inv(K)
    n = len(obj_pts)
    A = []
    for i in range(n):
        X = np.append(obj_pts[i], 1)
        x, y = img_pts[i]
        # 去归一化
        p = K_inv @ np.array([x,y,1])
        xn, yn = p[0]/p[2], p[1]/p[2]
        A.append([-X[0],-X[1],-X[2],-1, 0,0,0,0, xn*X[0],xn*X[1],xn*X[2],xn])
        A.append([0,0,0,0, -X[0],-X[1],-X[2],-1, yn*X[0],yn*X[1],yn*X[2],yn])
    A = np.array(A)
    _, _, Vt = np.linalg.svd(A)
    P = Vt[-1].reshape(3,4)
    R = P[:3,:3]; t = P[:3,3]
    # 正交化 R
    U,S,Vt = np.linalg.svd(R)
    R = U @ Vt
    if np.linalg.det(R) < 0: R = -R
    return R, t''',
    pitfalls=[
        ("点不够或共面/共线", "4 个点共线或共面时解不稳定，出现奇怪的位姿。",
         "至少 **6 个非共面 3D 点**，分布在 Z 方向上有层次；最少 4 点但要用 P3P。"),
        ("内参没标定或不准", "重投影误差 5+ 像素，位姿完全错。",
         "PnP 对 K 敏感，**必须先标定内参**（重投影误差 < 0.3 像素）。"),
        ("3D 点单位和 t 单位搞混", "算出来 t 数值是 0.05 以为 5cm 结果是 50cm，差 10 倍。",
         "**t 的单位 = 你 3D 点的单位**。常用 mm 全部 mm、m 全部 m。"),
        ("忘记 Rodrigues 把 rvec 转 R", "直接把 rvec 当旋转矩阵用，结果报错。",
         "PnP 返回的是**旋转向量**（axis-angle，3 个元素），不是矩阵。需要 `cv2.Rodrigues(rvec)` 转 3×3 矩阵。"),
        ("用 solvePnP 不用 RANSAC 版本", "2D 点有几个误匹配，结果直接偏 30°。",
         "实际场景**永远用 solvePnPRansac**；只有在仿真或点 100% 可靠时才用 solvePnP。"),
        ("2D 点 dtype 不对", "报 OpenCV(4.x) error or (-215) 错误。",
         "obj_pts 和 img_pts 必须是 `np.float32`（不能是 float64），形状是 (N,1,2) 或 (N,2)。"),
    ],
    koujue="""内参先标定好，K 不准位姿全歪；
点非共面至少六个，P3P 四点四个解；
推荐用 SOLVEPNP_EPNP，速度快精度也够高；
现实数据必用 RANSAC，重投影阈值八个像素；
旋转向量要 Rodrigues 转矩阵，不然没法用；
3D 点的单位决定 t 的单位，毫米就全毫米米就全米；
重投影误差小于一像素才算好。""",
    params=[
        ("method flag", "求解方法", "SOLVEPNP_EPNP", "—", "—"),
        ("iterationsCount", "RANSAC 迭代", "100", "鲁棒", "快"),
        ("reprojectionError", "内点阈值(px)", "8", "严", "宽松"),
        ("confidence", "置信度", "0.99", "准", "快"),
    ],
    tips=[
        ("AR 标记跟踪",
         "ArUco/ArUco3 库内置 solvePnP，标记检测直接出 rvec/tvec：\n```python\naruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)\nparams = cv2.aruco.DetectorParameters()\ncorners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=params)\nrvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, 0.05, K, dist)\n```"),
        ("手眼配合抓取",
         "PnP 算出的 t 是相机在物体坐标系下的位姿，要转换到机械臂基座，需要做**手眼标定**（cv2.calibrateHandEye）。"),
        ("用 SOLVEPNP_IPPE_SQUARE 解平面正方形",
         "当 4 点共面且是已知边长的正方形（如 ArUco 标记），用 `SOLVEPNP_IPPE_SQUARE` 精度最好、无歧义。"),
    ],
    perf=[
        ("solvePnP (EPnP, 50 points)", "< 1 ms", "CPU"),
        ("solvePnPRansac (50 points, 100 iter)", "~5 ms", "CPU"),
    ],
    notes=""
)

build_algo(
    "icp",
    meta=dict(
        name="ICP 迭代最近点", en="Iterative Closest Point",
        branch="geometry", year="1992", author="Paul Besl / Neil McKay",
        chapter="ch-14-3d-vision", level="advanced",
        tagline="两片点云拼起来的经典算法：找最近点配对，算刚体变换，反复迭代到对齐",
        analogy="你拿着两张撕碎的地图，每次把一片上每个点在另一片上找最近对应，算平移旋转让它们靠近，再重新找对应点……几十次后两片就严丝合缝拼在一起了",
        scene="激光雷达点云配准、三维重建、机器人 LiDAR SLAM、多视角点云融合、医学影像配准",
        pros=["思想简单","任意维度适用","无需特征提取","Open3D/PCL高效实现","局部收敛保证"],
        cons=["需要初始位姿","对离群点敏感","原始O(N²)慢","重叠率要够","点到点精度不如点到面"]),
    concepts=[
        ("点云配准问题",
         "给定两片点云 P（源）和 Q（目标），两者表示同一个物体/场景，但有一个刚体变换（旋转 R + 平移 t）把它们错开。ICP 的目标就是求 (R,t) 让变换后的 P 和 Q 对齐。",
         None),
        ("最近点对应",
         "对 P 中每个点 p_i，在 Q 中找欧氏距离最近的点 q_i，认为它们是对应点。原始 ICP 用全搜索（O(N·M)），实际用 KD-Tree 加速到 O(N log M)。",
         "flowchart LR\n  A[\"源点云 P\"] --> C[\"KD-Tree 查询<br/>Q 中最近点\"]\n  B[\"目标点云 Q\"] --> C\n  C --> D[\"对应对 (p_i, q_i)\"]"),
        ("SVD 求刚体变换",
         "给定对应点对，用 SVD 分解求最优 R、t：① 去中心化；② 计算 H = Σ (p_i - p̄)(q_i - q̄)ᵀ；③ SVD H = UΣVᵀ；④ R = VUᵀ；⑤ t = q̄ - R p̄。这保证 R 是正交的（旋转而非镜像）。",
         None),
        ("迭代收敛",
         "找对应→求变换→应用变换→再找对应……反复直到平均最近点距离变化 < ε 或达到最大迭代次数。由于每次迭代对应误差单调下降，理论上保证收敛到局部最优。",
         None),
        ("点到点 vs 点到面",
         "点到点：最小化对应点距离；点到面：点到目标点切平面的距离（精度更高、收敛更快，但 Q 要有法向量）。工业实现常用点到面 ICP。",
         None),
    ],
    arch_steps=[
        ("输入两片点云", "源 P、目标 Q，以及可选的初始位姿 T0"),
        ("初始化", "用 T0 变换 P（没有就用单位矩阵）"),
        ("KD-Tree 建 Q 索引", "加速最近点查询"),
        ("找最近点", "对 P 中每个点，在 Q 中找最近点（可加距离阈值剔除离群点）"),
        ("去中心+SVD", "计算最优 R、t（基于当前对应）"),
        ("应用变换", "把 P 用新的 (R,t) 变换"),
        ("收敛判断", "平均对应距离变化 < ε 或迭代到 max_iter"),
    ],
    opencv='''# ICP 在 OpenCV 中接口有限，推荐用 Open3D
import open3d as o3d
import numpy as np
source = o3d.io.read_point_cloud("source.ply")
target = o3d.io.read_point_cloud("target.ply")
threshold = 0.02   # 对应点最大距离
trans_init = np.eye(4)
# 点到点 ICP
reg_p2p = o3d.pipelines.registration.registration_icp(
    source, target, threshold, trans_init,
    o3d.pipelines.registration.TransformationEstimationPointToPoint(),
    o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=50))
print(reg_p2p.transformation)   # 4×4 位姿矩阵
print(f"fitness={reg_p2p.fitness:.3f}, RMSE={reg_p2p.inlier_rmse:.4f}")
# 点到面 ICP（需要法向量）
target.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
reg_p2l = o3d.pipelines.registration.registration_icp(
    source, target, threshold, trans_init,
    o3d.pipelines.registration.TransformationEstimationPointToPlane())''',
    numpy_impl='''def icp_svd(P, Q, max_iter=30, tol=1e-5):
    """点到点 ICP 极简实现（P, Q: Nx3 numpy array）"""
    from scipy.spatial import cKDTree
    assert len(P)==len(Q)
    P = P.copy()
    T = np.eye(4)
    tree = cKDTree(Q)
    prev_err = 1e9
    for it in range(max_iter):
        d, idx = tree.query(P, k=1)
        Q_matched = Q[idx]
        # 剔除太远的离群点
        mask = d < np.percentile(d, 90)
        p, q = P[mask], Q_matched[mask]
        # SVD
        p_mean, q_mean = p.mean(0), q.mean(0)
        pc, qc = p-p_mean, q-q_mean
        H = pc.T @ qc
        U,S,Vt = np.linalg.svd(H)
        R = Vt.T @ U.T
        if np.linalg.det(R) < 0: Vt[-1,:]*=-1; R = Vt.T @ U.T
        t = q_mean - R @ p_mean
        P = (R @ P.T).T + t
        # 累积 T
        T[:3,:3] = R @ T[:3,:3]
        T[:3,3] = R @ T[:3,3] + t
        err = d[mask].mean()
        if abs(prev_err - err) < tol: break
        prev_err = err
    return T, err''',
    pitfalls=[
        ("初始位姿差太远", "两片点云重叠率 < 30% 或初始旋转 > 30°，ICP 收敛到错误局部最优。",
         "ICP **不是全局注册**！先用 RANSAC+FPFH/SHOT 特征做粗配准，再用 ICP 精配准。"),
        ("没剔除离群点", "动态物体、噪声点让 R/t 估计偏。",
         "做距离阈值过滤（保留 90% 最近点）或用 Tukey/Huber 鲁棒损失。"),
        ("点到点精度不够", "大场景下点到点 ICP 收敛慢、RMSE 大。",
         "用**点到面 ICP**（需要法线），或更先进的 Generalized-ICP。"),
        ("两片点云密度差太大", "稀疏点云和稠密点云直接 ICP，对应关系错误。",
         "先下采样到同一体素尺寸：`o3d.geometry.voxel_down_sample(voxel_size)`。"),
        ("忘记降采样", "百万点级别直接跑 ICP 要几分钟。",
         "先用**体素下采样**到 5–10cm 体素大小（几千点）跑 ICP，收敛后再上原始点云做最后精调。"),
    ],
    koujue="""ICP 局部是好汉，初值给错全白干；
粗配准用 FPFH 加 RANSAC，再来 ICP 细打磨；
KD-Tree 找最近点，全搜是找罪受；
距离阈值剔除离群点，九十百分位最保险；
SVD 求 R 要检查行列式，小于零要翻转最后行；
点到面比点到点精，但是需要先算法线；
先下采样再 ICP，百万点变几千跑起来飞。""",
    params=[
        ("threshold", "对应点最大距离", "~2-3 倍分辨率", "严", "宽松"),
        ("voxel_size", "下采样体素", "5cm（室内）", "精细", "快"),
        ("max_iteration", "最大迭代", "50-100", "精确", "快"),
        ("normal radius", "法向量估计半径", "2×voxel_size", "光滑", "细节"),
    ],
    tips=[
        ("粗配准到精配准",
         "```python\n# ① 体素下采样\npcd_ds = pcd.voxel_down_sample(voxel_size)\n# ② 提 FPFH 特征\nfpfh = o3d.pipelines.registration.compute_fpfh_feature(pcd_ds, ...)\n# ③ RANSAC 粗配准\ntr = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(...)\n# ④ ICP 精配准\ntf = o3d.pipelines.registration.registration_icp(pcd_ds, ..., tr.transformation, ...)\n```"),
        ("评估配准质量",
         "fitness = 内点比例（越高越好，>0.7 算良好）；inlier_rmse = 内点 RMSE（越小越好，毫米/厘米级看场景）。"),
    ],
    perf=[
        ("ICP 点到点 (5000 点)", "~20 ms/迭代", "CPU"),
        ("Open3D 是高度优化的 C++", "—", "比纯 Python 快 50 倍+"),
    ],
    notes=""
)

print("sgbm, pnpsolver, icp done")
