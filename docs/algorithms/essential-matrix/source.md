---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import cv2
import numpy as np

img1 = cv2.imread("a.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("b.jpg", cv2.IMREAD_GRAYSCALE)
K = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], np.float32)

sift = cv2.SIFT_create()
kp1, d1 = sift.detectAndCompute(img1, None)
kp2, d2 = sift.detectAndCompute(img2, None)

flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
knn = flann.knnMatch(d1, d2, k=2)
good = [m for m, n in knn if m.distance < 0.75 * n.distance]

pts1 = np.float32([kp1[m.queryIdx].pt for m in good])
pts2 = np.float32([kp2[m.trainIdx].pt for m in good])

# 用 RANSAC 求本质矩阵
E, mask = cv2.findEssentialMat(pts1, pts2, K, method=cv2.RANSAC,
                               prob=0.999, threshold=1.0)
# 从 E 恢复旋转与平移（会内部筛选出唯一解）
_, R, t, mask_pose = cv2.recoverPose(E, pts1, pts2, K, mask=mask)
print("旋转 R:\n", R)
print("平移方向 t:", t.ravel())
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
import numpy as np

# 手写 8 点法（线性求解，未做 RANSAC / 归一化，仅示意）
def eight_point(pts1, pts2):
    """pts1, pts2: (N,2) 归一化相机坐标。返回 E。"""
    A = []
    for (x1, y1), (x2, y2) in zip(pts1, pts2):
        A.append([x2 * x1, x2 * y1, x2,
                  y2 * x1, y2 * y1, y2,
                  x1, y1, 1])
    A = np.array(A)
    _, _, Vt = np.linalg.svd(A)
    E = Vt[-1].reshape(3, 3)

    # 强制秩 2 约束：奇异值置为 (1,1,0)
    U, S, Vt2 = np.linalg.svd(E)
    S = np.array([1.0, 1.0, 0.0])
    return U @ np.diag(S) @ Vt2


pts1 = np.random.rand(20, 2)
pts2 = pts1 + 0.01 * np.random.randn(20, 2)
E = eight_point(pts1, pts2)
print("E 的奇异值:", np.linalg.svd(E)[1])   # 应为 (1,1,~0)
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| threshold | RANSAC 内点阈值 | **1.0 像素** |
| prob | 置信度 | **0.999** |
| K | 相机内参矩阵 | **必须先标定** |
| method | 求解器 | **cv2.RANSAC** |

::: tip 工程实现说明
务必先用内参 K 归一化坐标，否则求出的实为基础矩阵 F；务必用 RANSAC 版本，纯 8 点法对误匹配极敏感。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
