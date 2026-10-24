# SLIC 超像素

<AlgorithmCard
  name="SLIC 超像素"
  enName="Simple Linear Iterative Clustering"
  chapter="第5章 · 目标分割"  chapterLink="/chapters/ch05-segmentation"
  branch="segmentation"
  year="2010"
  author="Radhakrishna Achanta / Appu Shaji / Kevin Smith / Aurelien Lucchi / Pascal Fua / Sabine Süsstrunk"
  paper="https://core.ac.uk/download/pdf/147983593.pdf"
  level="mid"
  tagline="把 200 万像素切成 200 个颜色一致、大小均匀的小方块，后续处理快 1000 倍"
  analogy="把一张大图当成一块大蛋糕，先按网格切成小方块（期望大小），然后每块根据颜色往邻居那边微调，最后得到一堆大小差不多、颜色统一的小块。后续再做分割/检测时，以这些小块为单位，200 块比 200 万像素快 1 万倍"
  scene="分割预处理、显著性检测、光流加速、弱监督标注、深度估计超像素化、风格迁移"
  :pros='["速度极快（线性复杂度）", "超像素紧凑均匀", "内存占用小", "仅两个参数（n_segments + compactness）", "边界贴合度好"]'
  :cons='["必须指定超像素数", "OpenCV 主分支没有（需 ximgproc）", "紧凑度 m 影响边界贴合", "不是分割终点，只是预处理"]'
/>

## 一句话理解

把 200 万像素切成 200 个颜色一致、大小均匀的小方块，后续处理快 1000 倍。把一张大图当成一块大蛋糕，先按网格切成小方块（期望大小），然后每块根据颜色往邻居那边微调，最后得到一堆大小差不多、颜色统一的小块。后续再做分割/检测时，以这些小块为单位，200 块比 200 万像素快 1 万倍。

```mermaid
flowchart LR
  A["输入图像"] --> B["SLIC 超像素"]
  B --> C["输出结果"]
```

## 生活类比

把一张大图当成一块大蛋糕，先按网格切成小方块（期望大小），然后每块根据颜色往邻居那边微调，最后得到一堆大小差不多、颜色统一的小块。后续再做分割/检测时，以这些小块为单位，200 块比 200 万像素快 1 万倍

## 它解决什么问题

分割预处理、显著性检测、光流加速、弱监督标注、深度估计超像素化、风格迁移。

在传统 CV 的六分支体系中，SLIC 超像素 属于 **segmentation** 分支，主要解决的是该分支中把 200 万像素切成 200 个颜色一致、大小均匀的小方块，后续处理快 1000 倍的问题。

## 核心优点

- ✅ **速度极快（线性复杂度）**
- ✅ **超像素紧凑均匀**
- ✅ **内存占用小**
- ✅ **仅两个参数（n_segments + compactness）**
- ✅ **边界贴合度好**

## 它的短板

- ⚠️ 必须指定超像素数
- ⚠️ OpenCV 主分支没有（需 ximgproc）
- ⚠️ 紧凑度 m 影响边界贴合
- ⚠️ 不是分割终点，只是预处理

## 本算法档案包含 7 个页面

| 页面 | 内容 |
|---|---|
| [论文故事](/algorithms/slic/paper) | 作者、发表时间、核心贡献、为什么它会被提出 |
| [核心概念](/algorithms/slic/concepts) | 用生活比方讲清它依赖的关键概念 |
| [算法流程](/algorithms/slic/architecture) | 一步步走通算法全流程，配 mermaid 图 |
| [源码实现](/algorithms/slic/source) | OpenCV 调用 + NumPy 手写最小实现 |
| [踩坑清单](/algorithms/slic/painpoints) | 新手最常犯的 N 个错误 |
| [调参口诀](/algorithms/slic/tricks) | 参数怎么选、实战技巧、性能优化 |

## 相关链接

- 返回 [六大分支总览](/branches/)
- [SLIC 超像素所在分支](/branches/segmentation/)
- [算法档案总览](/algorithms/)
