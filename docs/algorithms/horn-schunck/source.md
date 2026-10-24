# Horn-Schunck 稠密光流 · 源码实现

<AlgorithmCard
  name="Horn-Schunck 稠密光流"
  enName="Horn-Schunck Optical Flow"
  chapter="ch-13-motion-analysis"
  branch="geometry"
  year="1981"
  author="Berthold Horn / Brian Schunck"
  paper="paper-horn-schunck-1981"
  level="advanced"
  tagline="给光流加全局平滑约束，用变分法求每个像素运动，开创稠密光流学派"
  analogy="LK 光流像独立办案的刑警，每个小窗口自己算自己的；Horn-Schunck 像一个总指挥，要求所有像素运动方向差不多，全局求解出密密麻麻的运动箭头图"
  scene="稠密运动场估计、流体运动分析、医学影像序列、变分光流研究基准、视频慢动作插帧（传统方法）"
  :pros='["稠密输出(每像素)", "全局一致平滑", "变分学派开创者", "理论优美", "基准方法"]'
  :cons='["迭代慢", "大运动不适用(需金字塔)", "运动边界过度平滑", "亮度恒定假设苛刻", "工程上Farneback/DIS更常用"]'
/>

## OpenCV 调用方法

Horn-Schunck 稠密光流在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

# OpenCV 主模块无直接 HS API，可用 cv2.calcOpticalFlowFarneback（同属稠密光流）
# 下面用 scipy/手写实现（教学演示）
import cv2, numpy as np
def horn_schunck(I1, I2, alpha=10, n_iter=100):
    I1 = I1.astype(np.float32)/255
    I2 = I2.astype(np.float32)/255
    # 时空梯度
    Ix = cv2.Sobel(I1, cv2.CV_32F, 1, 0, ksize=3) / 8
    Iy = cv2.Sobel(I1, cv2.CV_32F, 0, 1, ksize=3) / 8
    It = cv2.GaussianBlur(I2-I1, (3,3), 1)
    u = np.zeros_like(I1); v = np.zeros_like(I1)
    k = np.array([[1,1,1],[1,0,1],[1,1,1]], np.float32)/8
    a2 = alpha*alpha
    for _ in range(n_iter):
        u_avg = cv2.filter2D(u, -1, k)
        v_avg = cv2.filter2D(v, -1, k)
        num = Ix*u_avg + Iy*v_avg + It
        den = a2 + Ix*Ix + Iy*Iy
        u = u_avg - Ix*num/den
        v = v_avg - Iy*num/den
    return u, v
img1 = cv2.imread("f1.jpg", 0); img2 = cv2.imread("f2.jpg", 0)
u, v = horn_schunck(img1, img2, alpha=10, n_iter=200)
# 可视化 HSV 色轮
mag, ang = cv2.cartToPolar(u, v)
hsv = np.zeros((*img1.shape,3), np.uint8)
hsv[...,0] = ang*180/np.pi/2; hsv[...,1] = 255
hsv[...,2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
flow_rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
cv2.imwrite("hs_flow.jpg", flow_rgb)
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

# 见上方 horn_schunck 函数（已为 numpy 实现）
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

