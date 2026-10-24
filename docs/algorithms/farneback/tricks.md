# Farnebäck 稠密光流 · 调参口诀

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

## Farnebäck 稠密光流 调参口诀

```
pyr_scale 零点五，每层缩一半；
levels 三是默认，大运动加到五；
winsize 十五起，大运动加大到二十一；
iterations 每层三，多加几次精度提升；
poly_n 五 sigma 一点二，默认组合论文推；
HSV 色轮可视化，色调表方向明度表大小；
要实时用 DIS，Dense Inverse Search 四毫秒一帧。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| pyr_scale | 金字塔缩放比例 | **0.5** | 金字塔高 | 精度高 |
| levels | 金字塔层数 | **3** | 处理大运动 | 快 |
| winsize | 平均窗口大小 | **15** | 平滑鲁棒 | 保留细节 |
| iterations | 每层迭代数 | **3** | 精 | 快 |
| poly_n | 多项式邻域大小 | **5** | — | — |
| poly_sigma | 多项式高斯 sigma | **1.2** | — | — |

## 实战技巧

### 实时替代：DIS 光流

```python
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
flow = dis.calc(prev, curr, None)
```
速度提升 50–100 倍，精度略降。

### 光流用于视频稳像

估计帧间全局运动（取光流中位数作为相机运动），反向做仿射变换补偿即可。

### 光流外点过滤

用光流做跟踪时，对 mag 取阈值去掉过大位移（通常是遮挡或误匹配）。

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| Farneback (640×480) | ~200 ms | CPU C++ |
| Farneback (1920×1080) | ~1.5 s | CPU |
| DIS (640×480) | ~5 ms | CPU |

## 选型建议

**适用场景**：视频运动分析、动作识别稠密光流输入、视频稳像、图像配准、稠密对齐、传统视频插帧

**不适用场景**：速度慢(1080p几百ms)、光照敏感、运动边界模糊

