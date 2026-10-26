# 源码走读：连通域分析（Two-Pass）

## OpenCV 最简调用

```python
import cv2, numpy as np
img = cv2.imread('binary.png', 0)
_, bw = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

n, labels, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)
# n = 域个数（含背景）
# labels = (H,W) int32 标签图
# stats[i] = [left, top, width, height, area]
# centroids[i] = [cx, cy]

# 可视化：给每个域涂随机颜色
vis = np.zeros((*bw.shape, 3), dtype=np.uint8)
for i in range(1, n):
    vis[labels == i] = np.random.randint(0, 255, 3)

# 筛面积：只保留 100–10000 的域
keep = [i for i in range(1,n) if 100 < stats[i, cv2.CC_STAT_AREA] < 10000]

```

## 手写最小实现（理解原理）

```python
import numpy as np

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

def cc_two_pass(bw, conn=8):
    h, w = bw.shape
    labels = np.zeros((h,w), dtype=np.int32)
    uf = DSU(h*w)
    nxt = 1
    for y in range(h):
        for x in range(w):
            if bw[y,x] == 0: continue
            neighbors = []
            if conn == 8:
                if y>0 and x>0 and labels[y-1,x-1]: neighbors.append(labels[y-1,x-1])
            if y>0 and labels[y-1,x]: neighbors.append(labels[y-1,x])
            if conn==8 and y>0 and x<w-1 and labels[y-1,x+1]: neighbors.append(labels[y-1,x+1])
            if x>0 and labels[y,x-1]: neighbors.append(labels[y,x-1])
            if not neighbors:
                labels[y,x] = nxt; nxt += 1
            else:
                m = min(neighbors); labels[y,x] = m
                for n in neighbors: uf.union(m, n)
    # 第二遍
    for y in range(h):
        for x in range(w):
            if labels[y,x]:
                labels[y,x] = uf.find(labels[y,x])
    return labels, nxt

```

## OpenCV 源码核心片段解读

OpenCV 连通域源码在 `modules/imgproc/src/connectedcomponents.cpp`：

- `cv::connectedComponents_sub1`：入口，按 ltype/ccltype 分派
- `CCL_SAUF<>`、`CCL_BBDT<>`、`CCL_GRANA<>` 等模板特化
- SAUF（Scan Array Union Find）：Grana 2010 算法，每个像素用一棵 16 叶决策树决定如何处理邻居（0=全 0、1=只有左、…、15=四个邻居全前景点），是当前最快算法
- stats 累加用了向量化：`LabelStatistics::addBlock()` 一次性加一块，减少逐像素判断

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **connected components** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="connected" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
