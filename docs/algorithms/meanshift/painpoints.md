# MeanShift 均值漂移 · 踩坑清单

<AlgorithmCard
  name="MeanShift 均值漂移"
  enName="Mean-Shift Mode Seeking"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="1975/2002"
  author="K. Fukunaga / D. Comaniciu / P. Meer"
  paper="—"
  level="mid"
  tagline="每个点朝邻居最密的方向挪一步，最后聚成几坨——不用提前说有几坨"
  analogy="广场上站了一群人，每个人都往「周围人最密集的方向」走一步。走几步后大家会聚成几个紧密的小圈子，每个圈子就是一类"
  scene="图像平滑分割（pyrMeanShiftFiltering）、目标跟踪（CamShift）、聚类、运动目标分割"
  :pros='["无需指定聚类数", "同时考虑颜色+空间", "任意形状聚类", "对光照鲁棒"]'
  :cons='["速度很慢", "带宽 sp/sr 参数难调", "窗口大小固定", "高维不行"]'
/>

## MeanShift 均值漂移 的常见坑

::: danger 坑：1080p 图跑几秒
**现象**：pyrMeanShiftFiltering 在 1080p 上耗时 2–3 秒，没法实时。

**解决**：先降采样到 480p，处理完上采样标签；或改用 SLIC（快 10–50 倍）。
:::

::: danger 坑：sp/sr 参数没调好
**现象**：sp=30 大块糊成一片；sp=5 碎成小颗粒。sr=60 颜色被平滑得没细节。

**解决**：从 **sp=10–20, sr=20–40** 起步，根据效果微调。
:::

::: danger 坑：只滤波不做连通域
**现象**：pyrMeanShiftFiltering 只做颜色平滑（同一区域颜色变一致），不直接输出标签。

**解决**：滤波后必须再用 `connectedComponents` 或阈值+连通域取得具体分割。
:::

::: danger 坑：以为 meanShift 跟踪很鲁棒
**现象**：MeanShift/CamShift 跟踪在背景有同色物体时严重漂移。

**解决**：对跟踪而言 MeanShift 适合肤色、固定颜色目标；更复杂场景用 KCF/深度学习跟踪器。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

