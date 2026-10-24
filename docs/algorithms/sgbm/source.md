# SGM 半全局立体匹配 · 源码实现

<AlgorithmCard
  name="SGM 半全局立体匹配"
  enName="Semi-Global Matching"
  chapter="ch-14-3d-vision"
  branch="geometry"
  year="2005"
  author="Heiko Hirschmüller"
  paper="—"
  level="advanced"
  tagline="双目测距的工业标准，8 个方向做平滑约束，又快又稳出稠密视差图"
  analogy="BM 块匹配像个没耐心的小孩，只看自己周围一小圈就乱猜；SGM 像个老练的侦探，从上下左右斜 8 个方向打听消息，让相邻像素的深度差不多，拼出连贯的深度图"
  scene="双目深度相机（RealSense、自动驾驶双目）、无人机避障、机器人导航、三维重建、工业检测"
  :pros='["稠密视差图", "速度可接受(CPU实时)", "精度经典最高", "OpenCV内置StereoSGBM", "参数可解释"]'
  :cons='["参数多", "无纹理区域失败", "重复纹理误匹配", "需要精确标定", "远处深度误差大"]'
/>

## OpenCV 调用方法

SGM 半全局立体匹配在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

imgL = cv2.imread("left.jpg", 0)
imgR = cv2.imread("right.jpg", 0)
min_disp = 0
num_disp = 16*5   # 必须是 16 的倍数
block = 11
stereo = cv2.StereoSGBM_create(
    minDisparity=min_disp, numDisparities=num_disp, blockSize=block,
    P1=8*3*block**2, P2=32*3*block**2,
    disp12MaxDiff=1, uniquenessRatio=15,
    speckleWindowSize=100, speckleRange=2,
    preFilterCap=63, mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
)
disp = stereo.compute(imgL, imgR).astype(np.float32) / 16.0
# WLS 滤波后处理（需 opencv-contrib）
right_matcher = cv2.ximgproc.createRightMatcher(stereo)
disp_r = right_matcher.compute(imgR, imgL).astype(np.float32)/16.0
wls = cv2.ximgproc.createDisparityWLSFilter(stereo)
wls.setLambda(8000); wls.setSigmaColor(1.5)
disp_f = wls.filter(disp, imgL, disparity_map_right=disp_r)
# 视差转深度
points3d = cv2.reprojectImageTo3D(disp_f, Q)
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

# SGM 完整实现很长（8 方向 DP），这里给出 Census 代价核心
def census_transform(img, win=9):
    h, w = img.shape
    half = win//2
    out = np.zeros((h,w), dtype=np.uint64)
    for y in range(half, h-half):
        for x in range(half, w-half):
            center = img[y,x]
            val = 0; idx = 0
            for dy in range(-half, half+1):
                for dx in range(-half, half+1):
                    if dx==0 and dy==0: continue
                    val <<= 1
                    if img[y+dy,x+dx] > center: val |= 1
                    idx += 1
            out[y,x] = val
    return out
def census_cost(cL, cR, d, y, x):
    return bin((cL[y,x]^cR[y,x-d]).item()).count('1')
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

