# SGM 半全局立体匹配

## 🚀 动手体验

> 🧪 **先懂原理**：翻到下一节「核心概念」，页面里直接嵌入了可拖动滑块的原理动画（SIFT高斯金字塔、FLANN KD树、GrabCut迭代、KCF响应峰、ICP配准等），拖一拖就懂。

> 🎮 **再跑真机**：跳到第5页「源码实现」，底部有真机实验室（OpenCV.js 浏览器本地运行），选图调参即可看到真实效果与三语代码。

---

<AlgorithmCard
  name="SGM 半全局立体匹配"
  enName="Semi-Global Matching"
  chapter="第9章 · 立体视觉"  chapterLink="/chapters/ch09-stereo"
  branch="geometry"
  year="2005"
  author="Heiko Hirschmüller"
  paper="https://ieeexplore.ieee.org/document/4359315"
  level="advanced"
  tagline="双目测距的工业标准，8 个方向做平滑约束，又快又稳出稠密视差图"
  analogy="BM 块匹配像个没耐心的小孩，只看自己周围一小圈就乱猜；SGM 像个老练的侦探，从上下左右斜 8 个方向打听消息，让相邻像素的深度「差不多」，拼出连贯的深度图"
  scene="双目深度相机（RealSense、自动驾驶双目）、无人机避障、机器人导航、三维重建、工业检测"
  :pros='["输出稠密视差图", "速度可接受（CPU 实时）", "精度在经典方法里最高", "OpenCV 内置 StereoSGBM", "参数可解释（P1/P2 平滑）"]'
  :cons='["参数多（numDisparities/blockSize/P1/P2 等）", "无纹理区域仍失败", "重复纹理误匹配", "需要精确双目标定和立体校正", "远处深度误差平方级增长"]'
/>

## 一句话理解

双目测距的工业标准，8 个方向做平滑约束，又快又稳出稠密视差图。BM 块匹配像个没耐心的小孩，只看自己周围一小圈就乱猜；SGM 像个老练的侦探，从上下左右斜 8 个方向打听消息，让相邻像素的深度「差不多」，拼出连贯的深度图。

```mermaid
flowchart LR
  A["输入图像"] --> B["SGM 半全局立体匹配"]
  B --> C["输出结果"]
```

## 生活类比

BM 块匹配像个没耐心的小孩，只看自己周围一小圈就乱猜；SGM 像个老练的侦探，从上下左右斜 8 个方向打听消息，让相邻像素的深度「差不多」，拼出连贯的深度图

## 它解决什么问题

双目深度相机（RealSense、自动驾驶双目）、无人机避障、机器人导航、三维重建、工业检测。

在传统 CV 的六分支体系中，SGM 半全局立体匹配 属于 **geometry** 分支，主要解决的是该分支中双目测距的工业标准，8 个方向做平滑约束，又快又稳出稠密视差图的问题。

## 核心优点

- ✅ **输出稠密视差图**
- ✅ **速度可接受（CPU 实时）**
- ✅ **精度在经典方法里最高**
- ✅ **OpenCV 内置 StereoSGBM**
- ✅ **参数可解释（P1/P2 平滑）**

## 它的短板

- ⚠️ 参数多（numDisparities/blockSize/P1/P2 等）
- ⚠️ 无纹理区域仍失败
- ⚠️ 重复纹理误匹配
- ⚠️ 需要精确双目标定和立体校正
- ⚠️ 远处深度误差平方级增长

## 本算法档案包含 7 个页面

| 页面 | 内容 |
|---|---|
| [论文故事](/algorithms/sgbm/paper) | 作者、发表时间、核心贡献、为什么它会被提出 |
| [核心概念](/algorithms/sgbm/concepts) | 用生活比方讲清它依赖的关键概念 |
| [算法流程](/algorithms/sgbm/architecture) | 一步步走通算法全流程，配 mermaid 图 |
| [源码实现](/algorithms/sgbm/source) | OpenCV 调用 + NumPy 手写最小实现 |
| [踩坑清单](/algorithms/sgbm/painpoints) | 新手最常犯的 N 个错误 |
| [调参口诀](/algorithms/sgbm/tricks) | 参数怎么选、实战技巧、性能优化 |

## 相关链接

- 返回 [六大分支总览](/branches/)
- [SGM 半全局立体匹配所在分支](/branches/geometry/)
- [算法档案总览](/algorithms/)
