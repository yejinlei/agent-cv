# 分水岭分割 · 踩坑清单

<AlgorithmCard
  name="分水岭分割"
  enName="Watershed Transform"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="1991"
  author="Luc Vincent / Pierre Soille"
  paper="—"
  level="mid"
  tagline="把灰度图当地形图灌水，两个水坑汇合的地方就是分界线，专门切粘连物体"
  analogy="想象你在一块凹凸的地形上，从每个谷底开始慢慢灌水。当两个湖的水面要汇合时，你在汇合处修一道水坝——这些水坝就是分割线"
  scene="分离粘连硬币/细胞/颗粒、医学影像分割细胞、工业检测数零件、重叠物体分割"
  :pros='["闭合连续边界", "分离粘连物体", "速度较快", "支持种子点控制"]'
  :cons='["直接用会过度分割", "必须先做标记", "对噪声敏感", "需要形态学预处理"]'
/>

## 分水岭分割 的常见坑

::: danger 坑：直接 watershed 不做标记，结果碎成渣
**现象**：直接传二值图或空 markers 给 watershed，结果到处是 -1 的边界，图像像被乱刀切碎。

**解决**：**一定要做 marker-controlled**：确定前景、确定背景、未知区域。只允许从确定种子开始灌水。
:::

::: danger 坑：Otsu 二值化效果差
**现象**：光照不均导致二值化后物体粘连或破碎。

**解决**：二值化前先做**自适应阈值**或**背景校正**：`cv2.adaptiveThreshold`。
:::

::: danger 坑：距离变换阈值选错
**现象**：阈值 0.5*maxDist 时前景区域很小或很大，分割不准。

**解决**：0.4–0.7 之间调整，或用 `peak_local_max`（skimage）找真正的峰值。
:::

::: danger 坑：markers 没加 1
**现象**：OpenCV 要求：背景必须是 1，前景从 2 开始，0 是未知。直接 connectedComponents 输出（背景=0）会出错。

**解决**：**一定要 markers = markers + 1**，然后把 unknown 置 0。
:::

::: danger 坑：直接传灰度图给 watershed
**现象**：watershed 需要彩色原图（3 通道）和 markers（int32），传灰度图会报错。

**解决**：第一参数必须是**原始彩色图**（用于梯度），markers 是 `int32` 类型。
:::

::: danger 坑：重叠物体没有任何凹点
**现象**：完全重叠的圆饼或颗粒，距离变换只找出一个峰，无法分开。

**解决**：这种情况需要用凹点检测、或者深度学习实例分割。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

