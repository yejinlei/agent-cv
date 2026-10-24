# MSER 最大稳定极值区域 · 源码实现

<AlgorithmCard
  name="MSER 最大稳定极值区域"
  enName="Maximally Stable Extremal Regions"
  chapter="ch-8-local-feature"
  branch="feature-detection"
  year="2002"
  author="Jiri Matas et al."
  paper="—"
  level="mid"
  tagline="像往黑白照片上浇水，颜色深浅慢慢渗开，那些形状最稳定的水坑就是好区域"
  analogy="把灰度图想象成一块地形，从黑到白慢慢淹水：一开始只有最深的坑有水，水涨后水面扩大。那些「水位变一点、水面大小几乎不变」的湖泊，就是最稳定的区域——MSER"
  scene="宽基线立体匹配、文本检测（自然场景文字）、目标识别、对仿射变换要求高的场景"
  :pros='["仿射不变性", "多尺度区域检测", "无需预设阈值", "对光照鲁棒", "形状任意"]'
  :cons='["对模糊敏感", "速度较慢", "参数 delta/minArea/maxArea 要调", "不适合低对比度"]'
/>

## OpenCV 调用方法

MSER 最大稳定极值区域在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

img = cv2.imread("text.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
mser = cv2.MSER_create(
    _delta=5,               # 阈值变化步长
    _min_area=60,           # 最小区域（像素）
    _max_area=14400,        # 最大区域（像素，= 图像 5%）
    _max_variation=0.25,    # 最大面积变化率（越大容忍越多变）
    _min_diversity=0.2      # 子区域多样性阈值
)
regions, bboxes = mser.detectRegions(gray)
# 绘制
vis = img.copy()
for region in regions:
    hull = cv2.convexHull(region.reshape(-1, 1, 2))
    cv2.polylines(vis, [hull], True, (0,255,0), 1)
cv2.imwrite("mser.jpg", vis)
print(f"检测到 {len(regions)} 个 MSER 区域")
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

# MSER 的完整实现较复杂（需要并查集+分量面积跟踪），这里给出核心"灌水"框架
class MSERSimple:
    def __init__(self, delta=5, min_area=60, max_area=14400, max_var=0.25):
        self.delta, self.min_area, self.max_area = delta, min_area, max_area
        self.max_var = max_var
    def detect(self, gray):
        h, w = gray.shape
        # 按灰度分组像素
        pixels_by_val = [[] for _ in range(256)]
        for y in range(h):
            for x in range(w):
                pixels_by_val[gray[y, x]].append((y, x))
        # 并查集（简易版，省略）
        parent = {}
        area = {}
        def find(p):
            while parent[p] != p:
                parent[p] = parent[parent[p]]; p = parent[p]
            return p
        # 逐阈值灌水
        history = {}   # root -> {threshold: area}
        for t in range(256):
            for (y, x) in pixels_by_val[t]:
                p = (y, x); parent[p] = p; area[p] = 1
                for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ny, nx = y+dy, x+dx
                    if (ny, nx) in parent:
                        rp, rq = find(p), find((ny, nx))
                        if rp != rq:
                            parent[rq] = rp; area[rp] += area[rq]
                r = find(p)
                history.setdefault(id(r), []).append((t, area[r]))
        # 简化：真正 MSER 还要跟踪区域演化和 q(i)，这里省略
        return []
mser = MSERSimple()
```

::: tip 说明
工程上 MSER 在 OpenCV 主模块可用，但自然场景文本检测的完整 pipeline 建议用 opencv-contrib 的 `text` 模块。
:::

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

