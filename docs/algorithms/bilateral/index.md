---
title: 双边滤波 Bilateral Filter (1998)
outline: deep
---

# 双边滤波 Bilateral Filter (1998)

<AlgorithmCard
  name="双边滤波"
  enName="Bilateral Filter"
  year="1998"
  chapter="第3章 · 图像预处理"  chapterLink="/chapters/ch03-preprocessing"
  branch="图像处理"
  level="低层"
  tagline="保边去噪的「近邻兄弟」滤镜"
  analogy="给照片磨皮：离得近的像素才影响它，而且只让颜色差不多的互相匀一匀——色斑去掉了，但眼睛、睫毛、皮肤皱纹这种边缘给你留着。"
  scene="人像美颜磨皮、HDR 色调映射的 base/detail 分解、卡通化、去噪同时保边"
  :pros='["去噪同时保留边缘（高斯做不到）", "单参数可控、无需 GPU", "基础版线性复杂度可实时"]'
  :cons='["比高斯慢一个量级", "核大了会产生伪影", "不能处理强椒盐噪声"]'
  paper="https://people.csail.mit.edu/sparis/publi/2008/fnt/Paris_08_Bilateral_Filtering.pdf"
/>

## 一句话速记

把普通高斯滤波「只看像素离得多近」升级成「**既看离得多近、又看颜色差多大**」——近+像的邻居才被加权进来，**跨边缘的像素自动被降权**，所以边缘保住了。

## 七页导航

| 页面 | 讲什么 |
| --- | --- |
| [📄 原始论文](./paper) | Tomasi & Manduchi 1998 — 原文主张与公式 |
| [💡 核心概念](./concepts) | 高斯 vs 双边：空间高斯 × 值域高斯的乘积核 |
| [🏗 算法流程](./architecture) | O(1) 双边滤波加速 / 引导滤波对比 |
| [💻 源码实现](./source) | OpenCV 调用 + 手写最小版 |
| [🔥 踩坑清单](./painpoints) | 「磨皮过头的假面感」是怎么来的 |
| [⚙ 调参口诀](./tricks) | sigmaSpace / sigmaColor 怎么选 |

## 适用场景速查

✅ 人像美颜磨皮、皮肤处理
✅ HDR Tone Mapping 中的 Base/Detail 分解（Durand 2002）
✅ 卡通/插画滤镜（edge-aware smooth）
✅ 作为深度图/光流图的后处理

❌ 强椒盐噪声（用中值先顶一下）
❌ 实时视频超大核（用导向滤波替代）
