# ICP 迭代最近点 · 源码实现

<AlgorithmCard
  name="ICP 迭代最近点"
  enName="Iterative Closest Point"
  chapter="ch-14-3d-vision"
  branch="geometry"
  year="1992"
  author="Paul Besl / Neil McKay"
  paper="—"
  level="advanced"
  tagline="两片点云拼起来的经典算法：找最近点配对，算刚体变换，反复迭代到对齐"
  analogy="你拿着两张撕碎的地图，每次把一片上每个点在另一片上找最近对应，算平移旋转让它们靠近，再重新找对应点……几十次后两片就严丝合缝拼在一起了"
  scene="激光雷达点云配准、三维重建、机器人 LiDAR SLAM、多视角点云融合、医学影像配准"
  :pros='["思想简单", "任意维度适用", "无需特征提取", "Open3D/PCL高效实现", "局部收敛保证"]'
  :cons='["需要初始位姿", "对离群点敏感", "原始O(N²)慢", "重叠率要够", "点到点精度不如点到面"]'
/>

## OpenCV 调用方法

ICP 迭代最近点在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

# ICP 在 OpenCV 中接口有限，推荐用 Open3D
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
    o3d.pipelines.registration.TransformationEstimationPointToPlane())
```

### 关键参数说明

| 参数 | 含义 | 建议值 |
|---|---|---|
| （见各算法具体参数表） | — | — |

## NumPy 手写最小实现

下面写一个简化版的实现，帮助理解原理（性能远不如 OpenCV，仅用于教学）：

```python
import numpy as np
import cv2

def icp_svd(P, Q, max_iter=30, tol=1e-5):
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
    return T, err
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

