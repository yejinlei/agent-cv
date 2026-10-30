---
layout: doc
---

# PnP 位姿估计

<ClientOnly>
  <AlgoVisualizer type="pnp" />
</ClientOnly>


## 🎮 真机互动



<AlgorithmCard
  name="PnP 位姿估计"
  enName="Perspective-n-Point"
  chapter="第10章 · 三维景物恢复"  chapterLink="/chapters/ch10-3d-recovery"
  branch="geometry"
  year="1841 (Grunert P3P) / 2009 (EPnP)"
  author="Grunert / Fischler / Quan&Lan / Vincent Lepetit (EPnP)"
  paper="https://ieeexplore.ieee.org/document/4421461"
  level="advanced"
  tagline="已知几个 3D 点和它们在图上的位置，反推出相机在哪里看——AR 和机器人抓取的基石"
  analogy="你站在房间里，认出了墙上的钟、桌子上的杯子、书架顶上的花盆——这三个东西真实位置你知道（比如钟挂在门正上方 2.2 米），你就能反推出你自己站在房间的什么地方、朝什么方向看。PnP 就是这个「看几个地标定位自己」的算法"
  scene="AR 标记跟踪、机械臂抓取、视觉伺服、无人机着陆、增强现实虚拟物体叠加、SLAM 位姿求解"
  :pros='["最少 3 个点就能解（P3P）", "一次 solvePnP 毫秒级", "RANSAC 版本鲁棒", "OpenCV 内置（P3P/EPnP/ITERATIVE/DLS）", "精度高"]'
  :cons='["需要已知内参 K", "3D 点精度要高（依赖标定）", "点共面/共线时退化", "对匹配外点敏感（需 RANSAC）", "输出的 t 与 3D 点单位一致，易出错"]'
/>

## 一句话理解

已知几个 3D 点和它们在图上的位置，反推出相机在哪里看——AR 和机器人抓取的基石。你站在房间里，认出了墙上的钟、桌子上的杯子、书架顶上的花盆——这三个东西真实位置你知道（比如钟挂在门正上方 2.2 米），你就能反推出你自己站在房间的什么地方、朝什么方向看。PnP 就是这个「看几个地标定位自己」的算法。

```mermaid
flowchart LR
  A["输入图像"] --> B["PnP 位姿估计"]
  B --> C["输出结果"]
```

## 生活类比

你站在房间里，认出了墙上的钟、桌子上的杯子、书架顶上的花盆——这三个东西真实位置你知道（比如钟挂在门正上方 2.2 米），你就能反推出你自己站在房间的什么地方、朝什么方向看。PnP 就是这个「看几个地标定位自己」的算法

## 它解决什么问题

AR 标记跟踪、机械臂抓取、视觉伺服、无人机着陆、增强现实虚拟物体叠加、SLAM 位姿求解。

在传统 CV 的六分支体系中，PnP 位姿估计 属于 **geometry** 分支，主要解决的是该分支中已知几个 3D 点和它们在图上的位置，反推出相机在哪里看——AR 和机器人抓取的基石的问题。

## 核心优点

- ✅ **最少 3 个点就能解（P3P）**
- ✅ **一次 solvePnP 毫秒级**
- ✅ **RANSAC 版本鲁棒**
- ✅ **OpenCV 内置（P3P/EPnP/ITERATIVE/DLS）**
- ✅ **精度高**

## 它的短板

- ⚠️ 需要已知内参 K
- ⚠️ 3D 点精度要高（依赖标定）
- ⚠️ 点共面/共线时退化
- ⚠️ 对匹配外点敏感（需 RANSAC）
- ⚠️ 输出的 t 与 3D 点单位一致，易出错

## 本算法档案包含 7 个页面

| 页面 | 内容 |
|---|---|
| [论文故事](/algorithms/pnpsolver/paper) | 作者、发表时间、核心贡献、为什么它会被提出 |
| [核心概念](/algorithms/pnpsolver/concepts) | 用生活比方讲清它依赖的关键概念 |
| [算法流程](/algorithms/pnpsolver/architecture) | 一步步走通算法全流程，配 mermaid 图 |
| [源码实现](/algorithms/pnpsolver/source) | OpenCV 调用 + NumPy 手写最小实现 |
| [踩坑清单](/algorithms/pnpsolver/painpoints) | 新手最常犯的 N 个错误 |
| [调参口诀](/algorithms/pnpsolver/tricks) | 参数怎么选、实战技巧、性能优化 |

## 相关链接

- 返回 [六大分支总览](/branches/)
- [PnP 位姿估计所在分支](/branches/geometry/)
- [算法档案总览](/algorithms/)

> ⚠️ **本算法在当前 OpenCV.js 浏览器构建中暂未提供**，真机实验室无法直接跑。请查看上方 🧪 原理互动演示理解算法行为，或参考「源码/真机实验室」章节的 Python / C++ 代码在本地运行。
