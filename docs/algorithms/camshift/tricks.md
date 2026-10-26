# CamShift 连续自适应 MeanShift · 调参口诀

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

## CamShift 连续自适应 MeanShift 调参口诀

```
颜色跟踪 HSV 通道，色调 H 建直方图；
低饱和暗像素先 mask 掉，S 六十 V 三十二起；
直方图归一化到零到二五五，反向投影才准确；
CamShift 返回旋转矩形，boxPoints 画出来才漂亮；
同色背景会漂移，多线索融合才牢靠；
丢了不会自动找回，配个检测器做初始化；
教学演示很拿手，产品级用 KCF 或深度跟踪。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| histogram bins | H 通道 bin 数 | **180** | 精细 | 泛化 |
| termination maxCount | MeanShift 最大迭代 | **10** | 精 | 快 |
| termination epsilon | 收敛阈值(px) | **1** | 精 | 快 |

## 实战技巧

### 肤色 HSV 范围

不同种族肤色范围有差别，常用范围：
```
H: 0–20 (部分人 0–40)
S: 60–255 (排除灰色)
V: 32–255 (排除暗黑)
```

### 与 Kalman 滤波结合

用 Kalman 预测目标位置作为 CamShift 初始窗口，抗快速运动和短暂遮挡，工业中常见组合。

### 初始化自动人脸检测

```python
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
faces = face_cascade.detectMultiScale(gray)
# 取第一个人脸作为 track_window
```

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| CamShift 每帧 | ~1 ms | CPU，30fps+ |

## 选型建议

**适用场景**：实时人脸/人手跟踪、肤色目标跟踪、视频会议人脸锁定、简单无模型跟踪、HCI 手势交互

**不适用场景**：需初始化ROI、同色背景易漂移、光照敏感

<!-- AUTO-EXTENSION-2 -->

## 🎯 代码骨架

```python
roi = hsv[y:y+h, x:x+w]
mask = cv2.inRange(roi, (0,60,32), (180,255,255))
roi_hist = cv2.calcHist([roi], [0], mask, [180], [0,180])
cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)

# 跟踪
dst = cv2.calcBackProject([hsv], [0], roi_hist, [0,180], 1)
track_window = (x,y,w,h)
rot_rect, track_window = cv2.CamShift(dst, track_window, term_crit)
box = cv2.boxPoints(rot_rect).astype(int)
cv2.polylines(img, [box], True, (0,255,0), 2)
```
