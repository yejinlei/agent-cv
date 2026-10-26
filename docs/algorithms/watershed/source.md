# 分水岭分割 · 源码实现

<AlgorithmCard
  name="分水岭分割"
  enName="Watershed Transform"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="1991"
  author="Luc Vincent / Pierre Soille"
  paper="—"
  level="mid"
  tagline="把灰度图当地形图灌水，两个水坑汇合的地方就是分界线，专门切粘连物体"
  analogy="想象你在一块凹凸的地形上，从每个谷底开始慢慢灌水。当两个湖的水面要汇合时，你在汇合处修一道水坝——这些水坝就是分割线"
  scene="分离粘连硬币/细胞/颗粒、医学影像分割细胞、工业检测数零件、重叠物体分割"
  :pros='["闭合连续边界", "分离粘连物体", "速度较快", "支持种子点控制"]'
  :cons='["直接用会过度分割", "必须先做标记", "对噪声敏感", "需要形态学预处理"]'
/>

## OpenCV 调用方法

分水岭分割在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

img = cv2.imread("coins.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
# 去噪
kernel = np.ones((3,3), np.uint8)
opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
# 确定背景
sure_bg = cv2.dilate(opening, kernel, iterations=3)
# 距离变换找确定前景
dist = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
_, sure_fg = cv2.threshold(dist, 0.5*dist.max(), 255, cv2.THRESH_BINARY)
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)
# 标记
_, markers = cv2.connectedComponents(sure_fg)
markers = markers + 1                    # 背景=1
markers[unknown==255] = 0                # 未知=0
markers = cv2.watershed(img, markers)
# 边界=-1，画红
img[markers==-1] = [0,0,255]
cv2.imwrite("watershed.jpg", img)
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

# 分水岭核心实现复杂（优先队列泛洪），这里展示距离变换
def distance_transform_me(binary):
    """简化的距离变换：对每个前景点，到最近背景点的欧氏距离"""
    from scipy.ndimage import distance_transform_edt
    return distance_transform_edt(binary)
# 真正的分水岭算法建议直接用 OpenCV（基于 Vincent-Soille 浸没算法，1000 行代码级别）
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **watershed** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="watershed" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
