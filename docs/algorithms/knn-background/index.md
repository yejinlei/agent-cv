## 🎮 真机互动

<ClientOnly><OpencvPlayground initial-algo="knn-background" compact /></ClientOnly>

---
layout: doc
---

<AlgorithmCard
  name="KNN 背景建模"
  enName="K-Nearest Neighbors Background Subtraction"
  chapter="第11章 · 运动分析"
  chapterLink="/chapters/ch11-motion"
  branch="图像处理"
  year="2006"
  author="Zoran Zivkovic / Ferdinand van der Heijden"
  paper="https://ieeexplore.ieee.org/document/1640821"
  level="中级"
  tagline="记住每个像素最近的 N 个历史颜色，新颜色离它们太远就判为前景"
  analogy="你家门口监控盯着一块地砖。这块砖最近见过 20 种“正常”颜色（晴天阴影、雨天湿、黄昏黄）。忽然来了一种谁都没见过的颜色——那多半是有东西停在那，报警！KNN 背景建模就是给每个像素存一小本“正常颜色账本”。"
  scene="监控运动检测、人流量统计、车辆计数、周界入侵报警（比 MOG2 更抗噪）"
  :pros='["比 MOG2 抗噪、对缓慢光照变化更稳", "无需假设高斯分布（非参数）", "能处理多峰背景（如晃动的树叶）", "OpenCV 内置一行调用"]'
  :cons='["比 MOG2 慢", "内存占用更高（每像素存 N 个样本）", "参数（history/nSamples/dist2Threshold）需调", "对突然的全局光照突变会有短暂误检"]'
/>

## 一句话理解

> 为每个像素保存最近 N 个历史颜色值，新像素若与其中多数样本都「离得远」，判为前景。

## 为什么需要它？

视频监控的第一步永远是「把动的从不动里分出来」。帧差法太简陋、MOG2 用高斯假设又在晃动树叶前失灵。KNN 背景建模用**非参数**方式存历史样本，对多峰背景与噪声更宽容，是监控场景的稳健选择。

## 生活场景

小区监控摄像头对着一个门口。白天有阳光、夜晚有路灯、下雨地面反光——同一个像素的背景颜色一直在变。KNN 给每个像素存了 20 个历史颜色，这些变化全被记住，于是只有真正出现的人影才会被报警。

## 七页速览

| 页面 | 内容 | 你会得到什么 |
|------|------|--------------|
| [第1页 · 总览](index) | 你现在看的 | 快速判断「要不要用它」 |
| [第2页 · 论文溯源](paper) | 原始论文 | 搞懂「非参数背景建模」和 MOG2 高斯假设的区别 |
| [第3页 · 核心概念](concepts) | 原理直觉 | 理解为什么要给每个像素存多个历史样本 |
| [第4页 · 算法架构](architecture) | 流程图与步骤 | 掌握 history / nSamples / dist2Threshold 的调法 |
| [第5页 · 源码实现](source) | 可跑代码 | 抄一段能直接跑的运动检测代码 |
| [第6页 · 踩坑清单](painpoints) | 新手陷阱 | 避开内存、噪点、光照突变等坑 |
| [第7页 · 调参口诀](tricks) | 实战经验 | 会和 MOG2 / 帧差法对比选型 |

::: tip 阅读建议
第一次接触请按 1 → 3 → 4 顺序读，先建立直觉再看流程；要动手就直接跳到第 5 页抄代码。
:::
