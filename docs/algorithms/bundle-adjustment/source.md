---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import numpy as np
from scipy.optimize import least_squares

# 极简 BA：优化一个 3D 点与一个相机的外参（示意）
X0 = np.array([0.0, 0.0, 5.0])          # 初始 3D 点
K = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], np.float32)
observed = np.array([318.0, 242.0])     # 观测到的像素


def project(params):
    tx, ty, tz, Xx, Xy, Xz = params
    Xc = np.array([Xx + tx, Xy + ty, Xz + tz])   # 平移到相机坐标
    proj = K @ Xc
    return proj[:2] / proj[2]


def residual(params):
    return project(params) - observed


x_init = np.array([0.0, 0.0, 0.0, *X0])
res = least_squares(residual, x_init, method="lm")
print("优化后参数:", res.x)
print("最终重投影误差:", np.linalg.norm(res.fun))
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
# 生产环境请用专门的 BA 库，别手写
# 方案1：Ceres Solver（C++，最主流）
#   - 定义 ResidualBlock 描述重投影误差
#   - 交给 ceres::Solve 自动求导与 LM 优化
# 方案2：g2o（C++，SLAM 常用）
#   - 顶点=相机位姿/3D点，边=观测约束
#   - 调用 optimizer.optimize(iterations)
# 方案3：scipy.optimize.least_squares（Python 小规模）
#   - 直接传残差函数，适合几千参数以内

# 下面用 g2o 风格的伪代码示意流程：
PLAN = """
1. 建图：为每个相机位姿、每个 3D 点添加顶点
2. 加边：每个观测 x_ij 添加一条「投影误差」边
3. 设初值：用 PnP/三角化结果填充顶点
4. 选优化器：Levenberg-Marquardt
5. 迭代优化：optimizer.optimize(50)
6. 输出：优化后的位姿与点云
"""
print(PLAN)
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| loss | 鲁棒损失函数 | **Huber** |
| max_iter | 最大迭代次数 | **50~200** |
| fix_intrinsics | 是否固定内参 | **数据少时固定** |
| optimizer | 优化器 | **LM** |

::: tip 工程实现说明
生产环境不要手写 BA，直接用 Ceres / g2o / GTSAM；手写仅用于理解目标函数。务必加 Huber 鲁棒损失抵抗误匹配。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
