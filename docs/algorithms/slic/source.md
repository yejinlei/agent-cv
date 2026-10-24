# SLIC 超像素 · 源码实现

<AlgorithmCard
  name="SLIC 超像素"
  enName="Simple Linear Iterative Clustering"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="2010"
  author="R. Achanta et al."
  paper="—"
  level="mid"
  tagline="把 200 万像素切成 200 个颜色一致、大小均匀的小方块，后续处理快 1000 倍"
  analogy="把一张大图当大蛋糕，先按网格切小方块，然后每块根据颜色微调，最后得到一堆大小差不多、颜色统一的小块"
  scene="分割预处理、显著性检测、光流加速、弱监督标注、深度估计超像素化、风格迁移"
  :pros='["速度极快", "超像素紧凑均匀", "内存小", "仅 2 参数", "边界贴合好"]'
  :cons='["必须指定超像素数", "OpenCV 主分支没有", "紧凑度 m 影响边界", "不是分割终点"]'
/>

## OpenCV 调用方法

SLIC 超像素在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

# SLIC 在 opencv-contrib 的 ximgproc 模块，或直接用 skimage
from skimage.segmentation import slic, mark_boundaries
from skimage import img_as_float
image = img_as_float(cv2.imread("scene.jpg")[:,:,::-1])  # BGR→RGB
segments = slic(image, n_segments=200, compactness=10, sigma=1, start_label=0)
boundaries = mark_boundaries(image, segments, color=(1,0,0))
# OpenCV contrib 版本（如果装了）
# slic = cv2.ximgproc.createSuperpixelSLIC(img, region_size=20, ruler=10)
# slic.iterate(10); labels = slic.getLabels()
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

def slic_simple(img_lab, K=200, m=10, iters=10):
    """简化 SLIC"""
    h, w = img_lab.shape[:2]
    N = h*w
    S = int((N/K)**0.5)
    # 初始化中心
    centers = []
    for y in range(S//2, h, S):
        for x in range(S//2, w, S):
            centers.append([img_lab[y,x,0],img_lab[y,x,1],img_lab[y,x,2],y,x])
    centers = np.array(centers, dtype=np.float64)
    labels = -np.ones((h,w), dtype=np.int32)
    dist = np.full((h,w), np.inf)
    for it in range(iters):
        for i, c in enumerate(centers):
            yc, xc = int(c[3]), int(c[4])
            for y in range(max(0,yc-2*S), min(h,yc+2*S+1)):
                for x in range(max(0,xc-2*S), min(w,xc+2*S+1)):
                    dlab = np.sqrt(np.sum((img_lab[y,x]-c[:3])**2))
                    dxy = np.sqrt((y-c[3])**2+(x-c[4])**2)
                    D = dlab + (m/S)*dxy
                    if D < dist[y,x]:
                        dist[y,x] = D
                        labels[y,x] = i
        # 更新中心
        for i in range(len(centers)):
            mask = labels==i
            if mask.sum()==0: continue
            ys, xs = np.where(mask)
            centers[i,3] = ys.mean(); centers[i,4] = xs.mean()
            centers[i,:3] = img_lab[ys,xs].mean(0)
    return labels
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

