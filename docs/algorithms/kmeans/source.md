# K-Means 颜色聚类 · 源码实现

<AlgorithmCard
  name="K-Means 颜色聚类"
  enName="K-Means Clustering"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="1967"
  author="Stuart Lloyd / James MacQueen"
  paper="—"
  level="basic"
  tagline="把所有像素按颜色分成 K 堆，每堆一个代表色，图像立刻变卡通"
  analogy="把一盒彩笔按颜色分成 K 堆：先随机挑 K 支笔当组长，其他笔投奔最近的组长；每堆重新选平均色当新组长；反复到组长不再变"
  scene="颜色量化、海报风格化、肤色区域分割、语义分割前处理、调色板生成"
  :pros='["思想极简单", "速度快", "OpenCV/sklearn 一行调用", "适用范围广"]'
  :cons='["必须指定 K", "只看颜色不看位置", "对初始值敏感", "对噪声敏感"]'
/>

## OpenCV 调用方法

K-Means 颜色聚类在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

img = cv2.imread("scene.jpg")
Z = img.reshape((-1,3)).astype(np.float32)
K = 8
criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
ret, label, center = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
center = np.uint8(center)
res = center[label.flatten()].reshape(img.shape)
cv2.imwrite(f"kmeans_K{K}.jpg", res)
# 含空间坐标的 5 维版本
h, w = img.shape[:2]
ys, xs = np.mgrid[0:h, 0:w]
feat = np.stack([ys/h*255, xs/w*255, img[...,0], img[...,1], img[...,2]],
                axis=2).reshape(-1,5).astype(np.float32)
ret, label5, center5 = cv2.kmeans(feat, K, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
res5 = np.uint8(center5[label5.flatten(), 2:]).reshape(img.shape)
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

def kmeans_numpy(X, K, max_iter=10, tol=1e-4, seed=42):
    rng = np.random.default_rng(seed)
    # kmeans++ 初始化
    idx = rng.choice(len(X), 1)
    centers = [X[idx[0]]]
    for _ in range(K-1):
        d2 = np.min([np.sum((X - c)**2, axis=1) for c in centers], axis=0)
        probs = d2 / d2.sum()
        idx = rng.choice(len(X), 1, p=probs)
        centers.append(X[idx[0]])
    centers = np.array(centers)
    for it in range(max_iter):
        # 分配
        d = np.linalg.norm(X[:,None] - centers[None], axis=2)
        labels = d.argmin(axis=1)
        # 更新
        new_centers = np.array([X[labels==k].mean(0) for k in range(K)])
        if np.linalg.norm(new_centers - centers) < tol:
            break
        centers = new_centers
    return labels, centers
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **kmeans** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="kmeans" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
