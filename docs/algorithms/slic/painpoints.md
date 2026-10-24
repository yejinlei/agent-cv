# SLIC 超像素 · 踩坑清单

<AlgorithmCard
  name="SLIC 超像素"
  enName="Simple Linear Iterative Clustering"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="2010"
  author="R. Achanta et al."
  paper="—"
  level="mid"
  tagline="把 200 万像素切成 200 个颜色一致、大小均匀的小方块，后续处理快 1000 倍"
  analogy="把一张大图当大蛋糕，先按网格切小方块，然后每块根据颜色微调，最后得到一堆大小差不多、颜色统一的小块"
  scene="分割预处理、显著性检测、光流加速、弱监督标注、深度估计超像素化、风格迁移"
  :pros='["速度极快", "超像素紧凑均匀", "内存小", "仅 2 参数", "边界贴合好"]'
  :cons='["必须指定超像素数", "OpenCV 主分支没有", "紧凑度 m 影响边界", "不是分割终点"]'
/>

## SLIC 超像素 的常见坑

::: danger 坑：n_segments 设得太大或太小
**现象**：设 10000 个超像素和像素级差不多没意义；设 10 个就是大色块。

**解决**：通常 **200–1000** 个超像素够用；一般经验：**每超像素 ~500–1000 像素**。
:::

::: danger 坑：compactness m 理解错
**现象**：m=1 超像素完全贴边界但形状破碎；m=50 几乎是方块。

**解决**：默认 **m=10** 是论文推荐；要形状方正 m=20–40；要贴边界 m=1–5。
:::

::: danger 坑：以为 OpenCV 主模块有 SLIC
**现象**：`import cv2; cv2.SLIC_create` 报错。

**解决**：需要 `opencv-contrib-python`：`cv2.ximgproc.createSuperpixelSLIC`；或者用 `skimage.segmentation.slic`。
:::

::: danger 坑：没转 Lab 直接 RGB 算
**现象**：用 RGB 空间算欧氏距离不符合人眼感知。

**解决**：SLIC 论文用 CIELAB，**务必先 BGR→Lab**（skimage 内部会处理）。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

