# 论文精读：CLAHE 限制对比度自适应直方图均衡

## 论文信息

| 项 | 内容 |
|---|---|
| 论文标题 | Contrast Limited Adaptive Histogram Equalization |
| 作者 | Karel Zuiderveld |
| 发表年份/会议 | 1994 |
| 引用数（约） | ~10000+ |
| 核心贡献 | 把图像切成 tile，每个 tile 内做直方图均衡，但对直方图做 clip 限制对比度，避免噪声被放大；tile 之间用双线性插值消除网格边界 |
| OpenCV 实现 | `cv2.createCLAHE(clipLimit, tileGridSize)` |

## 论文为什么被写出来？

直方图均衡（HE）是最早的图像增强方法：把灰度直方图强制拉平，让对比度最大化。但它有两个问题：
1. **全局**：对整张图做，亮区更亮、暗区更暗，局部细节照顾不到
2. **过度增强**：在接近平坦的区域（比如天空、皮肤），直方图的少数峰值被强力拉大，**噪声被放大**到肉眼可见

AHE（Adaptive HE，1970s 起）解决了全局问题——把图切成小 tile 分别均衡。但 AHE 在**暗区**会把噪声放大到离谱。

Pizer et al.（1987）提出 CLAHE 的雏形——在 AHE 的基础上对每个 tile 的直方图加 clip。Zuiderveld 1994 年在 Graphics Gems IV 上给出了一个**80 行 C 语言**的极简实现，成为工程界事实上的标准。

## 核心创新点

**创新 1：分块处理**
把图像均匀划分成 M×N 个 tile（OpenCV 默认 8×8），每个 tile 独立计算直方图和映射函数（CDF）。

**创新 2：Clip Limit（对比度限制）**
对每个 tile 的直方图 h，计算 clipLimit（典型值 2–4 倍平均像素数）：
- 超过 clipLimit 的 bin 把超出部分「切下来」
- 把切下来的总像素数 **平均分配**到所有 256 个 bin
- 重复一次直至没有 bin 超限（其实一次就差不多）

这步让平坦区的直方图不会被拉到极端，噪声也就不会被暴力放大。

**创新 3：双线性插值拼接**
在 tile 边界处，如果直接用相邻 tile 各自的映射会出现「网格边」。CLAHE 对每个像素，取它所在的 **4 个相邻 tile** 的映射结果做双线性插值，整张图无缝衔接。

## 论文里的关键结果

- 在医学影像（乳腺 X 光、眼底照）上，CLAHE 让结节/病灶可见度提升显著
- 在人脸/低光照增强上，比全局 HE 少出现「过曝脸」
- 速度：800×600 图约 5–10ms（CPU 单线程），完全实时

## 论文的局限与后人改进

- clipLimit 仍需手动调，没有数据驱动的自适应方法
- 对高动态范围场景（同时存在强光和极暗）仍不够
- tileGridSize 固定，图像内容变化大时不够灵活
- 后来出现 AGCWD、Retinex、Zero-DCE 等更强的增强算法，但 CLAHE 因简单快速仍在工业首选

## 论文阅读建议

- 初读：只看 abstract + 直接读 Graphics Gems IV 第 VIII.5 节，只有 8 页
- 精读：再看算法流程图与 Zuiderveld 给出的 `ClipHistogram` 和 `Interpolate` 函数，代码本身就是论文
- 工程落地：直接对照 OpenCV `cv2.createCLAHE(clipLimit, tileGridSize)` 源码，**不必复现论文**
