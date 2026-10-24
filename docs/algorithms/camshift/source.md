# CamShift 连续自适应 MeanShift · 源码实现

<AlgorithmCard
  name="CamShift 连续自适应 MeanShift"
  enName="Continuously Adaptive Mean-Shift"
  chapter="ch-11-object-detection"
  branch="detection"
  year="1998"
  author="Gary Bradski"
  paper="—"
  level="mid"
  tagline="MeanShift 的视频版——窗口大小自动跟着目标变，肤色跟踪的经典算法"
  analogy="MeanShift 像用放大镜盯跳蚤，大小不变；CamShift 像自适应聚光灯，跳蚤跳近光圈小、跳远光圈大，始终把跳蚤照亮在中间"
  scene="实时人脸/人手跟踪、肤色目标跟踪、视频会议人脸锁定、简单无模型跟踪、HCI 手势交互"
  :pros='["实现简单", "自适应窗口大小", "速度快", "非刚体变形容忍", "无需训练"]'
  :cons='["需初始化ROI", "同色背景易漂移", "光照敏感", "快速运动易丢", "只能跟踪颜色显著目标"]'
/>

## OpenCV 调用方法

CamShift 连续自适应 MeanShift在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
r, h, c, w = 200, 100, 300, 100   # 初始 ROI
track_window = (c, r, w, h)
roi = frame[r:r+h, c:c+w]
hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv_roi, np.array([0,60,32]), np.array([180,255,255]))
roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0,180])
cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
term = (cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT, 10, 1)
while True:
    ret, frame = cap.read()
    if not ret: break
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv], [0], roi_hist, [0,180], 1)
    ret, track_window = cv2.CamShift(dst, track_window, term)
    pts = cv2.boxPoints(ret).astype(int)
    cv2.polylines(frame, [pts], True, (0,0,255), 2)
    cv2.imshow("CamShift", frame)
    if cv2.waitKey(30)==27: break
cap.release(); cv2.destroyAllWindows()
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

def meanshift_step(prob, window):
    """一次 MeanShift 更新"""
    x,y,w,h = window
    roi = prob[y:y+h, x:x+w]
    M00 = roi.sum()
    if M00 < 1e-6: return window, False
    ys, xs = np.indices(roi.shape)
    cx = x + (xs*roi).sum()/M00
    cy = y + (ys*roi).sum()/M00
    nw = (int(cx-w/2), int(cy-h/2), w, h)
    return nw, abs(nw[0]-x)+abs(nw[1]-y) > 1
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

