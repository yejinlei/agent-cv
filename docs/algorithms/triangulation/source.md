---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import cv2
import numpy as np

# 假设已有两视图投影矩阵 P1, P2 与匹配点 pts1, pts2
K = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], np.float32)
R = np.eye(3, dtype=np.float32)
t = np.array([[1.0], [0.0], [0.0]], np.float32)   # 基线 1 个单位
P1 = K @ np.hstack([np.eye(3), np.zeros((3, 1))])
P2 = K @ np.hstack([R, t])

pts1 = np.array([[320.0, 240.0], [400.0, 300.0]], np.float32)   # (N,2)
pts2 = np.array([[300.0, 240.0], [380.0, 300.0]], np.float32)

points4d = cv2.triangulatePoints(P1, P2, pts1.T, pts2.T)
points3d = (points4d[:3] / points4d[3]).T          # 齐次化 -> (N,3)
print("重建的 3D 点:\n", points3d)
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
import numpy as np


def triangulate_dlt(P1, P2, x1, x2):
    """手写 DLT 三角化。x1,x2 为齐次像素坐标 (3,)。"""
    A = np.vstack([
        x1[0] * P1[2] - x1[2] * P1[0],
        x1[1] * P1[2] - x1[2] * P1[1],
        x2[0] * P2[2] - x2[2] * P2[0],
        x2[1] * P2[2] - x2[2] * P2[1],
    ])
    _, _, Vt = np.linalg.svd(A)
    X = Vt[-1]
    return X[:3] / X[3]


K = np.array([[800., 0, 320], [0, 800., 240], [0, 0, 1]])
P1 = K @ np.hstack([np.eye(3), np.zeros((3, 1))])
P2 = K @ np.hstack([np.eye(3), np.array([[1.], [0], [0]])])

x1 = np.array([320., 240., 1.])
x2 = np.array([300., 240., 1.])
X = triangulate_dlt(P1, P2, x1, x2)
print("3D 点:", X)
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| P1/P2 | 两视图投影矩阵 | **K[R|t]** |
| min_depth | 最小深度过滤 | **>0** |
| reproj_thresh | 重投影误差阈值 | **1~3 像素** |
| normalize | 坐标归一化 | **推荐开启** |

::: tip 工程实现说明
基线越长深度越稳；务必做重投影误差过滤，剔除误差大或深度不合理的点，否则点云里全是飞点。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
