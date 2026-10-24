# GrabCut 抠图 · 踩坑清单

<AlgorithmCard
  name="GrabCut 抠图"
  enName="GrabCut Interactive Foreground Extraction"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="2004"
  author="C. Rother / V. Kolmogorov / A. Blake"
  paper="—"
  level="mid"
  tagline="画一个框就能把目标抠出来，GMM+GraphCut 迭代优化，Photoshop 快速选择的灵魂"
  analogy="你用笔在目标周围画个圈，对算法说「圈外肯定是背景，圈内有前景也有背景」。GrabCut 就像一个聪明的学徒，先猜哪些颜色像前景，再用 GraphCut 切一刀，反复 5 次抠得干干净净"
  scene="照片抠图换背景、数据集快速标注、医学影像交互式分割、人像美颜前景提取"
  :pros='["用户只需画一个框", "边缘细节比 GraphCut 好", "支持笔刷精修", "GMM 建模多峰颜色分布"]'
  :cons='["高分辨率慢", "前景背景颜色接近时效果差", "矩形外永远是背景", "边缘毛发需 matting"]'
/>

## GrabCut 抠图 的常见坑

::: danger 坑：框画太小
**现象**：目标边缘被切成确定背景，怎么迭代都回不来。

**解决**：**框要比目标大 5–15%**；不要紧贴目标。
:::

::: danger 坑：前景背景颜色接近
**现象**：人和背景都是白墙，GrabCut 会把部分前景当背景或反之。

**解决**：**手动标注**（GC_INIT_WITH_MASK）：用前景笔刷画几笔确认为前景、背景笔刷确认背景，再跑。
:::

::: danger 坑：GrabCut 太慢（1080p 5s）
**现象**：迭代 5 次大图像耗时数秒。

**解决**：**先降分辨率 0.25x 跑 GrabCut**，把 mask 上采样回原尺寸，再在原分辨率上 `GC_INIT_WITH_MASK iters=2` 精修——能提速 10 倍。
:::

::: danger 坑：bgdModel/fgdModel 形状错
**现象**：报错 Expected 65 columns 或 dtype 不对。

**解决**：必须是 **`np.zeros((1,65), np.float64)`**，每次处理新图重置。
:::

::: danger 坑：忘了三通道
**现象**：传灰度图进去报错。

**解决**：GrabCut 需要 **3 通道 BGR** 图。灰度图先 `cvtColor(gray, COLOR_GRAY2BGR)`。
:::

::: danger 坑：mask 值混淆
**现象**：前景背景判反，输出完全反色。

**解决**：前景判据：`(mask==1)|(mask==3)` 即 `(GC_FGD)|(GC_PR_FGD)`。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

