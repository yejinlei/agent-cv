# BRIEF 二进制描述子 · 踩坑清单

<AlgorithmCard
  name="BRIEF 二进制描述子"
  enName="Binary Robust Independent Elementary Features"
  chapter="ch-8-local-feature"
  branch="feature-detection"
  year="2010"
  author="Michael Calonder et al."
  paper="—"
  level="mid"
  tagline="不再算浮点数直方图，只比 256 对像素大小，一个整数就能描述一个角点"
  analogy="SIFT/SURF 像做了一份 128 项血常规，BRIEF 只问 256 个「你比你旁边那个大吗」的是非题，用答案拼出一个 256 位的指纹"
  scene="资源受限的嵌入式设备、移动端、实时 SLAM 前端，毫秒级匹配几千个点"
  :pros='["描述子 256 位（32 字节）", "汉明距离匹配极快", "对光照模糊鲁棒", "构造简单"]'
  :cons='["不抗旋转", "不抗尺度", "对噪声敏感", "随机点对选择影响性能"]'
/>

## BRIEF 二进制描述子 的常见坑

::: danger 坑：错用欧氏距离匹配
**现象**：用 BFMatcher(NORM_L2) 匹配 BRIEF 描述子结果稀烂，速度慢、错配多。

**解决**：BRIEF 是二进制描述子，**必须用 NORM_HAMMING**：`cv2.BFMatcher(cv2.NORM_HAMMING)`。如果用 3 点 WTA_K（ORB 中）要用 NORM_HAMMING2。
:::

::: danger 坑：以为 BRIEF 抗旋转
**现象**：图一转 30°，原本能匹配上的点对全部失败。

**解决**：需要抗旋转请直接用 **ORB**（内部用灰度质心法加方向，再做 steered BRIEF）；或自己计算关键点方向后做点对旋转。
:::

::: danger 坑：直接把 BRIEF 用在多尺度图之间
**现象**：图放大 1.5 倍后，固定 31×31 patch 覆盖的物理范围变了，描述子不匹配。

**解决**：BRIEF 本身不抗尺度——需配合图像金字塔（检测阶段提多尺度点），这正是 ORB 的做法。
:::

::: danger 坑：没做平滑直接提描述子
**现象**：在噪声大的图上，单个像素比较结果不稳定。

**解决**：提描述前必须对 patch 做**高斯平滑（sigma=2，核 9×9）**，OpenCV 内置已经做了；手写版本务必加。
:::

::: danger 坑：patch 越界没处理
**现象**：关键点在图像边缘 15 像素内时，31×31 patch 会跑到图外。

**解决**：要么跳过边缘关键点（推荐），要么边界填 0/复制。OpenCV 默认跳过边界点。
:::

::: danger 坑：用 BRIEF 做长基线大视角变化匹配
**现象**：视角变化超过 30° 时，BRIEF 匹配率断崖式下跌。

**解决**：宽基线匹配请用 SIFT 或带仿射不变的 AKAZE；BRIEF 适合短基线、小旋转的实时场景。
:::

::: danger 坑：bytes 参数用错
**现象**：`bytes=16` 时描述子只有 128 位，区分度差；`bytes=64` 时 512 位，慢。

**解决**：默认 **bytes=32（256 位）**是论文推荐最优。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

