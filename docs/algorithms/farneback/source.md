# Farnebäck 稠密光流 · 源码实现

<AlgorithmCard
  name="Farnebäck 稠密光流"
  enName="Gunnar Farnebäck Dense Optical Flow"
  chapter="ch-13-motion-analysis"
  branch="geometry"
  year="2003"
  author="Gunnar Farnebäck"
  paper="—"
  level="mid"
  tagline="用二次多项式拟合邻域，根据多项式系数变化估计稠密光流，CPU 上的经典稠密选择"
  analogy="在一张地图上你看不清路牌（像素值），但你能看清每块地形的坡度（多项式系数）。两帧之间坡度形状不变，只是整体平移了一点——Farnebäck 通过比较两块地形的坡度差算出平移"
  scene="视频运动分析、动作识别稠密光流输入、视频稳像、图像配准、稠密对齐、传统视频插帧"
  :pros='["稠密输出", "OpenCV原生calcOpticalFlowFarneback", "参数直观", "精度优于HS(工程上)", "多尺度金字塔"]'
  :cons='["速度慢(1080p几百ms)", "光照敏感", "运动边界模糊", "实时性差", "参数组合多"]'
/>

## OpenCV 调用方法

Farnebäck 稠密光流在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

prev = cv2.imread("f1.jpg", 0)
curr = cv2.imread("f2.jpg", 0)
flow = cv2.calcOpticalFlowFarneback(
    prev, curr, None,
    pyr_scale=0.5, levels=3, winsize=15,
    iterations=3, poly_n=5, poly_sigma=1.2, flags=0
)
# flow shape (h,w,2): flow[...,0]=u, flow[...,1]=v
mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
hsv = np.zeros((*prev.shape,3), np.uint8)
hsv[...,0] = ang*180/np.pi/2
hsv[...,1] = 255
hsv[...,2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
cv2.imwrite("farneback.jpg", rgb)
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

# Farnebäck 多项式展开较复杂，这里给出调用接口与 HSV 可视化
# 工程直接用 cv2.calcOpticalFlowFarneback
# 如需手写需实现：高斯导数滤波 → 二次多项式拟合 → 邻域融合 → 多尺度 warp
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **farneback** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="gradient-flow" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
