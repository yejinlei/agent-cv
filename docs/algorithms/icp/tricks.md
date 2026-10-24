# ICP 迭代最近点 · 调参口诀

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

## ICP 迭代最近点 调参口诀

```
ICP 局部是好汉，初值给错全白干；
粗配准用 FPFH 加 RANSAC，再来 ICP 细打磨；
KD-Tree 找最近点，全搜是找罪受；
距离阈值剔除离群点，九十百分位最保险；
SVD 求 R 要检查行列式，小于零要翻转最后行；
点到面比点到点精，但是需要先算法线；
先下采样再 ICP，百万点变几千跑起来飞。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| threshold | 对应点最大距离 | **~2-3 倍分辨率** | 严 | 宽松 |
| voxel_size | 下采样体素 | **5cm（室内）** | 精细 | 快 |
| max_iteration | 最大迭代 | **50-100** | 精确 | 快 |
| normal radius | 法向量估计半径 | **2×voxel_size** | 光滑 | 细节 |

## 实战技巧

### 粗配准到精配准

```python
# ① 体素下采样
pcd_ds = pcd.voxel_down_sample(voxel_size)
# ② 提 FPFH 特征
fpfh = o3d.pipelines.registration.compute_fpfh_feature(pcd_ds, ...)
# ③ RANSAC 粗配准
tr = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(...)
# ④ ICP 精配准
tf = o3d.pipelines.registration.registration_icp(pcd_ds, ..., tr.transformation, ...)
```

### 评估配准质量

fitness = 内点比例（越高越好，>0.7 算良好）；inlier_rmse = 内点 RMSE（越小越好，毫米/厘米级看场景）。

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| ICP 点到点 (5000 点) | ~20 ms/迭代 | CPU |
| Open3D 是高度优化的 C++ | — | 比纯 Python 快 50 倍+ |

## 选型建议

**适用场景**：激光雷达点云配准、三维重建、机器人 LiDAR SLAM、多视角点云融合、医学影像配准

**不适用场景**：需要初始位姿、对离群点敏感、原始O(N²)慢

