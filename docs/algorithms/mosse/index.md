## 🧪 原理互动演示

<AlgoVisualizer type="mosse" />

---
layout: doc
---

## 🚀 动手体验

> 🧪 **先懂原理**：翻到下一节「核心概念」，页面里直接嵌入了可拖动滑块的原理动画（SIFT高斯金字塔、FLANN KD树、GrabCut迭代、KCF响应峰、ICP配准等），拖一拖就懂。

> 🎮 **再跑真机**：跳到第5页「源码实现」，底部有真机实验室（OpenCV.js 浏览器本地运行），选图调参即可看到真实效果与三语代码。

---

<AlgorithmCard
  name="MOSSE 相关滤波跟踪"
  enName="Minimum Output Sum of Squared Error Filter"
  chapter="第11章 · 运动分析"
  chapterLink="/chapters/ch11-motion"
  branch="目标检测"
  year="2010"
  author="David S. Bolme / J. Ross Beveridge / Bruce A. Draper / Yui Man Lui"
  paper="https://www.cs.colostate.edu/~draper/papers/bolme_cvpr10.pdf"
  level="中级"
  tagline="用傅里叶变换把「找目标」变成「一次乘除」，600 FPS 的开山鼻祖"
  analogy="你在找一枚硬币，手里拿着一张「硬币模板」。MOSSE 说：别一格格挪着比，我把它变到频率世界，用一次乘除就知道哪里最像。于是每秒能扫 600 次。它是 KCF、CSRT 这一整族跟踪算法的祖师爷。"
  scene="高速单目标跟踪、无人机视觉跟随、体育转播自动追球、实时 AR 追踪"
  :pros='["极快（600+ FPS）", "只需一个矩形框初始化", "对形变、光照有一定鲁棒性", "代码短、易实现"]'
  :cons='["不具备尺度自适应", "快速运动/遮挡易丢失", "精度不如 KCF/CSRT", "对旋转敏感"]'
/>

## 一句话理解

> 训练一个滤波器，使它与目标模板卷积后响应最大；再对这个响应图求峰值定位目标。

## 为什么需要它？

跟踪是视频分析的基石。光流、CamShift 各有局限，2010 年 MOSSE 首次把**相关滤波 + 傅里叶加速**引入跟踪，一举把速度提到 600 FPS，开启了 KCF/CSRT 这条黄金谱系。

## 生活场景

无人机要自动跟拍一个人。机上 CPU 只有手机级别，深度学习跑不动。用 MOSSE，一个矩形框圈住人，之后每帧一次 FFT 乘除就锁住他，600 FPS 绰绰有余。

## 七页速览

| 页面 | 内容 | 你会得到什么 |
|------|------|--------------|
| [第1页 · 总览](index) | 你现在看的 | 快速判断「要不要用它」 |
| [第2页 · 论文溯源](paper) | 原始论文 | 搞懂「相关滤波」为什么能定位目标 |
| [第3页 · 核心概念](concepts) | 原理直觉 | 理解 FFT 如何把卷积变成乘除 |
| [第4页 · 算法架构](architecture) | 流程图与步骤 | 知道 MOSSE 和 KCF 的传承关系 |
| [第5页 · 源码实现](source) | 可跑代码 | 抄一段可跑的 MOSSE 跟踪代码 |
| [第6页 · 踩坑清单](painpoints) | 新手陷阱 | 避开丢失不找回、尺度固定等坑 |
| [第7页 · 调参口诀](tricks) | 实战经验 | 会选 MOSSE / KCF / CSRT |

::: tip 阅读建议
第一次接触请按 1 → 3 → 4 顺序读，先建立直觉再看流程；要动手就直接跳到第 5 页抄代码。
:::
