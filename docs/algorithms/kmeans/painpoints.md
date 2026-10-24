# K-Means 颜色聚类 · 踩坑清单

<AlgorithmCard
  name="K-Means 颜色聚类"
  enName="K-Means Clustering"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="1967"
  author="Stuart Lloyd / James MacQueen"
  paper="—"
  level="basic"
  tagline="把所有像素按颜色分成 K 堆，每堆一个代表色，图像立刻变卡通"
  analogy="把一盒彩笔按颜色分成 K 堆：先随机挑 K 支笔当组长，其他笔投奔最近的组长；每堆重新选平均色当新组长；反复到组长不再变"
  scene="颜色量化、海报风格化、肤色区域分割、语义分割前处理、调色板生成"
  :pros='["思想极简单", "速度快", "OpenCV/sklearn 一行调用", "适用范围广"]'
  :cons='["必须指定 K", "只看颜色不看位置", "对初始值敏感", "对噪声敏感"]'
/>

## K-Means 颜色聚类 的常见坑

::: danger 坑：忘了转 float32
**现象**：`cv2.kmeans` 报 Unsupported depth/format 错误。

**解决**：Z 必须是 `np.float32`，不能是 uint8。
:::

::: danger 坑：K 值选得离谱
**现象**：K=2 时只剩两种颜色，K=32 时和原图差不多看不出差别。

**解决**：图像风格化 **K=4–8**；颜色量化 **K=16–64**；二分类 K=2。
:::

::: danger 坑：每次结果不一样
**现象**：kmeans 随机初始化，同样参数两次结果不同。

**解决**：设随机种子：`cv2.setRNGSeed(42)`；用 `KMEANS_PP_CENTERS` 稳定性更好。
:::

::: danger 坑：直接 3 维 K-Means 颜色碎
**现象**：同色物体分散在不同位置聚在一起后分割不连贯。

**解决**：加空间坐标变成 5 维，或先用 SLIC 超像素再聚类。
:::

::: danger 坑：不做 kmeans++
**现象**：用 KMEANS_RANDOM_CENTERS 可能得到空类、效果差。

**解决**：**永远用 `cv2.KMEANS_PP_CENTERS`**（默认）。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

