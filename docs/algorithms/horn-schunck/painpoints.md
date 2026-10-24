# Horn-Schunck 稠密光流 · 踩坑清单

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

## Horn-Schunck 稠密光流 的常见坑

::: danger 坑：直接用 HS 处理大运动
**现象**：物体移动超过 3–5 像素，结果完全是噪声。

**解决**：必须做**金字塔多尺度 coarse-to-fine**；或使用更鲁棒的算法（Farnebäck、DIS）。
:::

::: danger 坑：迭代次数不够
**现象**：n_iter=10 时光流还没收敛，结果很噪。

**解决**：单尺度 **n_iter=100–200**；多尺度每层 30–50 次。
:::

::: danger 坑：α 太小全是噪声
**现象**：α=1 时光流像麻点；α=100 过度平滑。

**解决**：典型 α=10–20；根据图像噪声调整。
:::

::: danger 坑：没做高斯预平滑
**现象**：梯度估计受噪声影响严重。

**解决**：梯度估计前先做 3×3 高斯平滑；或用 Sobel 核（自带平滑）。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

