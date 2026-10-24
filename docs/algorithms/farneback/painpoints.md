# Farnebäck 稠密光流 · 踩坑清单

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

## Farnebäck 稠密光流 的常见坑

::: danger 坑：winsize 太小
**现象**：winsize=5 噪声多；winsize=30 运动边界模糊。

**解决**：**winsize=15**（默认附近）；快速运动加大到 21–30。
:::

::: danger 坑：poly_n/poly_sigma 不匹配
**现象**：poly_n=5 时 sigma=1.1–1.2；poly_n=7 时 sigma=1.5。

**解决**：OpenCV 默认 poly_n=5, poly_sigma=1.2 是论文推荐组合，一般不用改。
:::

::: danger 坑：levels 太少处理不了大运动
**现象**：快速运动物体光流全错。

**解决**：levels=3 能处理到 8 像素位移；更大位移加 levels 到 5。
:::

::: danger 坑：把 Farneback 当实时用
**现象**：1080p 几百毫秒，没法 30fps。

**解决**：实时请用 `cv2.DISOpticalFlow_create()`（2016 年，4ms/帧）。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

