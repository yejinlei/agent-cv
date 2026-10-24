# 📄 原始论文

> **Ojala, T., Pietikäinen, M., & Harwood, D. (1996).**
> *A comparative study of texture measures with classification based on featured distributions.* Pattern Recognition 1996.
>
> 扩展版：Ojala et al. (2002) *Multiresolution gray-scale and rotation invariant texture classification with local binary patterns.* IEEE TPAMI.

## 论文一句话主张

> 「纹理分类不需要复杂滤波器组——只需要统计**局部二值模式**的出现频率，就能超过当时所有主流纹理特征（Gabor、MRF 等），而且快上百倍。」

## 历史地位

- 1996 原始 LBP（3×3 正方形邻域，256 维）。
- 2002 提出**圆形邻域（P,R）**、**旋转不变 LBP**、**Uniform LBP（59 维）**，成为工业标准。
- 2004 Ahonen 将 LBP 用到人脸识别（LBP Face），**在 FERET 人脸库上刷到 SOTA**，推动了整个"局部特征→人脸识别"方向。
- 2010 年代虽然被深度学习超过，但在**嵌入式设备、工业质检、小样本**场景仍被广泛使用。

## 衍生家族

| 变种 | 干什么 |
| --- | --- |
| 原始 LBP(8,1) | 3×3 8 邻居，256 维 |
| **LBP(P,R)** | 圆形邻域，P 点半径 R |
| **Uniform LBP_u2** | 只保留跳变≤2次的模式，58+1=59 维 |
| **Rotation Invariant LBP_ri** | 循环移位取最小值，36 维 |
| MB-LBP | 基于区域均值而不是单点，更抗噪 |
| LBP-TOP | 三正交平面，视频里的动态纹理 |
