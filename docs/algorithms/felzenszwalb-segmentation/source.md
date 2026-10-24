---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
import cv2
import numpy as np

img = cv2.imread("street.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# OpenCV 的 ximgproc 提供 selecsearch 与 felzenszwalb（部分构建含）
seg = cv2.ximgproc.segmentation.createGraphSegmentation()
seg.setSigma(0.8)
seg.setK(300)          # 尺度参数 k，越大区域越大
seg.setMinSize(100)    # 最小区域，防碎块
segmented = seg.processImage(img)

# 给每个区域随机着色，直观可视化
rng = np.random.default_rng(0)
colors = rng.integers(0, 255, size=(segmented.max() + 1, 3), dtype=np.uint8)
vis = colors[segmented]
cv2.imwrite("seg.png", cv2.cvtColor(vis, cv2.COLOR_RGB2BGR))
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
import numpy as np
import cv2


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def felzenszwalb(gray, k=300.0, min_size=50):
    h, w = gray.shape
    n = h * w
    dsu = DSU(n)
    int_diff = np.zeros(n)          # 每个区域内部差异
    size = np.ones(n, int)          # 每个区域大小

    # 建边并排序
    edges = []
    for y in range(h):
        for x in range(w):
            if x + 1 < w:
                edges.append((abs(int(gray[y, x]) - int(gray[y, x + 1])), y * w + x, y * w + x + 1))
            if y + 1 < h:
                edges.append((abs(int(gray[y, x]) - int(gray[y + 1, x])), y * w + x, (y + 1) * w + x))
    edges.sort()

    for wgt, a, b in edges:
        ra, rb = dsu.find(a), dsu.find(b)
        if ra == rb:
            continue
        tau = k / min(size[ra], size[rb])
        if wgt <= min(int_diff[ra] + tau, int_diff[rb] + tau):
            dsu.union(ra, rb)
            root = dsu.find(ra)
            size[root] = size[ra] + size[rb]
            int_diff[root] = max(int_diff[ra], int_diff[rb], wgt)

    labels = np.array([dsu.find(i) for i in range(n)]).reshape(h, w)
    return labels


gray = cv2.imread("street.jpg", 0)
lab = felzenszwalb(gray, k=300, min_size=50)
print("区域数:", len(np.unique(lab)))
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
| k (scale) | 尺度参数，越大区域越大 | **300** |
| sigma | 预处理高斯 σ | **0.8** |
| min_size | 最小区域尺寸 | **50~100** |
| 输入空间 | 建议 Lab | **RGB/Lab** |

::: tip 工程实现说明
OpenCV 中该算法位于 ximgproc（opencv-contrib），标准 pip 包需安装 opencv-contrib-python；或直接用 scikit-image 的 felzenszwalb。
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
