# MSER 最大稳定极值区域 · 踩坑清单

<AlgorithmCard
  name="MSER 最大稳定极值区域"
  enName="Maximally Stable Extremal Regions"
  chapter="ch-8-local-feature"
  branch="feature-detection"
  year="2002"
  author="Jiri Matas et al."
  paper="—"
  level="mid"
  tagline="像往黑白照片上浇水，颜色深浅慢慢渗开，那些形状最稳定的水坑就是好区域"
  analogy="把灰度图想象成一块地形，从黑到白慢慢淹水：一开始只有最深的坑有水，水涨后水面扩大。那些「水位变一点、水面大小几乎不变」的湖泊，就是最稳定的区域——MSER"
  scene="宽基线立体匹配、文本检测（自然场景文字）、目标识别、对仿射变换要求高的场景"
  :pros='["仿射不变性", "多尺度区域检测", "无需预设阈值", "对光照鲁棒", "形状任意"]'
  :cons='["对模糊敏感", "速度较慢", "参数 delta/minArea/maxArea 要调", "不适合低对比度"]'
/>

## MSER 最大稳定极值区域 的常见坑

::: danger 坑：参数默认值在小图上检不出
**现象**：640×480 图上默认 _min_area=60、_max_area=14400（占 5%）可能导致重要区域被过滤。

**解决**：根据图像大小调整 min/max 面积。一般 min_area ≈ 图像面积的 0.01%。
:::

::: danger 坑：在模糊图上 MSER 数量爆炸
**现象**：图像模糊后稳定区域边界不再清晰，出现大量小而杂的区域。

**解决**：**不要在严重模糊图上直接用 MSER**；先适度锐化，或提高 _max_variation 到 0.5。
:::

::: danger 坑：嵌套区域重复检测
**现象**：一个大字被检测为一个区域，字内部的孔洞也被检测为一个区域，导致同一位置多个框。

**解决**：用 `_min_diversity=0.5` 或在 bboxes 上做 NMS 去重。
:::

::: danger 坑：低对比度图像检不出
**现象**：光照均匀、对比度低时，区域面积随阈值变化快，没有稳定区。

**解决**：先做直方图均衡：`gray = cv2.equalizeHist(gray)`。
:::

::: danger 坑：只拿 MSER 当区域没提描述子
**现象**：MSER 只给连通区域，直接当特征用会发现没法匹配。

**解决**：把每个 MSER 区域仿射归一化到 41×41 patch，然后提 SIFT/ROOT-SIFT 描述子。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

