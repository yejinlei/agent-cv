# PnP 位姿估计 · 源码实现

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

## OpenCV 调用方法

PnP 位姿估计在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

# 3D 点（单位: 米或 mm，但单位要和 t 一致）
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
print("相机位姿：
R =", R, "
t =", tvec)
# 重投影验证
proj, _ = cv2.projectPoints(obj_pts, rvec, tvec, K, dist)
err = np.linalg.norm(proj.reshape(-1,2)-img_pts, axis=1).mean()
print(f"重投影误差: {err:.3f} px")
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

# PnP 完整实现较复杂（DLT+非线性优化），这里给 DLT 线性解
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
    return R, t
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

