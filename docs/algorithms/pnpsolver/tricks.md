# PnP 位姿估计 · 调参口诀

<AlgorithmCard
  name="PnP 位姿估计"
  enName="Perspective-n-Point"
  chapter="ch-14-3d-vision"
  branch="geometry"
  year="1841/2009(EPnP)"
  author="Grunert / Lepetit(EPnP)"
  paper="—"
  level="advanced"
  tagline="已知几个 3D 点和它们在图上的位置，反推出相机在哪里看——AR 和机器人抓取的基石"
  analogy="你站在房间里，认出了墙上的钟、桌上的杯子、书架上的花盆——这三个东西真实位置你知道，就能反推出自己站在房间的什么地方、朝什么方向看"
  scene="AR 标记跟踪、机械臂抓取、视觉伺服、无人机着陆、AR 虚拟物体叠加、SLAM 位姿求解"
  :pros='["最少 3 点可解(P3P)", "毫秒级", "RANSAC 鲁棒", "OpenCV 内置多种方法", "精度高"]'
  :cons='["需要已知内参", "3D 点精度要高", "点共面/共线退化", "对外点敏感", "单位易搞错"]'
/>

## PnP 位姿估计 调参口诀

```
内参先标定好，K 不准位姿全歪；
点非共面至少六个，P3P 四点四个解；
推荐用 SOLVEPNP_EPNP，速度快精度也够高；
现实数据必用 RANSAC，重投影阈值八个像素；
旋转向量要 Rodrigues 转矩阵，不然没法用；
3D 点的单位决定 t 的单位，毫米就全毫米米就全米；
重投影误差小于一像素才算好。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| method flag | 求解方法 | **SOLVEPNP_EPNP** | — | — |
| iterationsCount | RANSAC 迭代 | **100** | 鲁棒 | 快 |
| reprojectionError | 内点阈值(px) | **8** | 严 | 宽松 |
| confidence | 置信度 | **0.99** | 准 | 快 |

## 实战技巧

### AR 标记跟踪

ArUco/ArUco3 库内置 solvePnP，标记检测直接出 rvec/tvec：
```python
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
params = cv2.aruco.DetectorParameters()
corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=params)
rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, 0.05, K, dist)
```

### 手眼配合抓取

PnP 算出的 t 是相机在物体坐标系下的位姿，要转换到机械臂基座，需要做**手眼标定**（cv2.calibrateHandEye）。

### 用 SOLVEPNP_IPPE_SQUARE 解平面正方形

当 4 点共面且是已知边长的正方形（如 ArUco 标记），用 `SOLVEPNP_IPPE_SQUARE` 精度最好、无歧义。

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| solvePnP (EPnP, 50 points) | < 1 ms | CPU |
| solvePnPRansac (50 points, 100 iter) | ~5 ms | CPU |

## 选型建议

**适用场景**：AR 标记跟踪、机械臂抓取、视觉伺服、无人机着陆、AR 虚拟物体叠加、SLAM 位姿求解

**不适用场景**：需要已知内参、3D 点精度要高、点共面/共线退化

