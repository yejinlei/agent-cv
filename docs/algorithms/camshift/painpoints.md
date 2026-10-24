# CamShift 连续自适应 MeanShift · 踩坑清单

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

## CamShift 连续自适应 MeanShift 的常见坑

::: danger 坑：不做低饱和度过滤
**现象**：肤色跟踪时头发、阴影这些低饱和度像素污染直方图，跟踪漂移到背景。

**解决**：建直方图时必须用 inRange **过滤 S<60 或 V<32 的像素**。
:::

::: danger 坑：H 通道 0–180 范围搞错
**现象**：calcHist 和 calcBackProject 范围用 0–255，直方图错位。

**解决**：OpenCV H 通道范围是 **0–179**，histSize=180, ranges=[0,180]。
:::

::: danger 坑：目标快速运动丢了跟不回来
**现象**：目标一帧移出窗口，CamShift 永远跟在空地方。

**解决**：CamShift 没有重检测机制。丢了要靠外部检测器重新初始化；或用**卡尔曼滤波**预测位置。
:::

::: danger 坑：背景有肤色物体干扰
**现象**：后面的人肤色被跟踪，窗口直接漂走。

**解决**：CamShift 只看颜色，没有其他信息。鲁棒方案是 **CamShift + 光流/边缘/运动检测** 多线索融合，或换 KCF/深度学习跟踪器。
:::

::: danger 坑：窗口大小不收敛
**现象**：窗口越来越大最终包住整个人。

**解决**：CamShift 大小受直方图影响，若背景颜色相似会扩散。实际工程要给窗口大小加 clamp（如最小 20×20、最大 300×300）。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

