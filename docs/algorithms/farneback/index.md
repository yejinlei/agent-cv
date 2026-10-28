# Farnebäck 稠密光流

<!-- VIDEOLAB-AUTO: 视频真机实验，嵌入在算法首页最顶部 -->
## 🎬 视频真机实验（光流 / 运动跟踪）

> 这个算法**天生依赖帧与帧之间**的变化，用单张静态图演示不出来。下面是真实视频输入的**逐帧处理**：
> 左边原视频、右边算法输出，可以换算法、拖滑块、**上传自己的视频**，旁边同步给出 Python / C++ / JavaScript 代码。

<VideoLab algo="farneback" />

---



<AlgorithmCard
  name="Farnebäck 稠密光流"
  enName="Gunnar Farnebäck Dense Optical Flow"
  chapter="第11章 · 运动分析"  chapterLink="/chapters/ch11-motion"
  branch="geometry"
  year="2003"
  author="Gunnar Farnebäck"
  paper="https://www.researchgate.net/publication/2408653_Two-Frame_Motion_Estimation_Based_on_Polynomial_Expansion"
  level="mid"
  tagline="用二次多项式拟合邻域，根据多项式系数变化估计稠密光流，CPU 上的经典稠密选择"
  analogy="在一张地图上你看不清路牌（像素值），但你能看清每块地形的「坡度」（多项式系数）。两帧之间坡度形状不变，只是整体平移了一点——Farnebäck 通过比较两块地形的坡度差，算出这块地平移了多少"
  scene="视频运动分析、动作识别稠密光流输入、视频稳像、图像配准、稠密对齐、传统视频插帧"
  :pros='["稠密输出（每像素都有）", "OpenCV 原生 calcOpticalFlowFarneback", "参数直观", "精度优于 HS（工程上）", "多尺度金字塔处理大运动"]'
  :cons='["速度慢（1080p 几百毫秒）", "对光照变化敏感", "运动边界模糊", "实时性差", "参数 pyr_scale/levels/winsize 组合多"]'
/>

## 一句话理解

用二次多项式拟合邻域，根据多项式系数变化估计稠密光流，CPU 上的经典稠密选择。在一张地图上你看不清路牌（像素值），但你能看清每块地形的「坡度」（多项式系数）。两帧之间坡度形状不变，只是整体平移了一点——Farnebäck 通过比较两块地形的坡度差，算出这块地平移了多少。

```mermaid
flowchart LR
  A["输入图像"] --> B["Farnebäck 稠密光流"]
  B --> C["输出结果"]
```

## 生活类比

在一张地图上你看不清路牌（像素值），但你能看清每块地形的「坡度」（多项式系数）。两帧之间坡度形状不变，只是整体平移了一点——Farnebäck 通过比较两块地形的坡度差，算出这块地平移了多少

## 它解决什么问题

视频运动分析、动作识别稠密光流输入、视频稳像、图像配准、稠密对齐、传统视频插帧。

在传统 CV 的六分支体系中，Farnebäck 稠密光流 属于 **geometry** 分支，主要解决的是该分支中用二次多项式拟合邻域，根据多项式系数变化估计稠密光流，CPU 上的经典稠密选择的问题。

## 核心优点

- ✅ **稠密输出（每像素都有）**
- ✅ **OpenCV 原生 calcOpticalFlowFarneback**
- ✅ **参数直观**
- ✅ **精度优于 HS（工程上）**
- ✅ **多尺度金字塔处理大运动**

## 它的短板

- ⚠️ 速度慢（1080p 几百毫秒）
- ⚠️ 对光照变化敏感
- ⚠️ 运动边界模糊
- ⚠️ 实时性差
- ⚠️ 参数 pyr_scale/levels/winsize 组合多

## 本算法档案包含 7 个页面

| 页面 | 内容 |
|---|---|
| [论文故事](/algorithms/farneback/paper) | 作者、发表时间、核心贡献、为什么它会被提出 |
| [核心概念](/algorithms/farneback/concepts) | 用生活比方讲清它依赖的关键概念 |
| [算法流程](/algorithms/farneback/architecture) | 一步步走通算法全流程，配 mermaid 图 |
| [源码实现](/algorithms/farneback/source) | OpenCV 调用 + NumPy 手写最小实现 |
| [踩坑清单](/algorithms/farneback/painpoints) | 新手最常犯的 N 个错误 |
| [调参口诀](/algorithms/farneback/tricks) | 参数怎么选、实战技巧、性能优化 |

## 相关链接

- 返回 [六大分支总览](/branches/)
- [Farnebäck 稠密光流所在分支](/branches/geometry/)
- [算法档案总览](/algorithms/)


---

## 🚀 动手体验（浏览器里直接玩，不用装环境）

> 下面这些组件都在**你的浏览器本地运行**，不上传任何图片、也不用安装 OpenCV 或写代码。

### 🧪 先懂原理：Lucas-Kanade 光流到底在算什么

拖动滑块，看数学是怎么一步步变成图像的——纯 Canvas 绘制，秒开。

<ClientOnly>
  <MathVisualizer initial-tab="lk" compact />
</ClientOnly>

### 🎮 再跑真机：在浏览器里真跑 Farnebäck 稠密光流

换成你自己的照片也行；下面还会**实时生成**对应的 Python / C++ / JavaScript 代码，拖参数时代码同步更新。

<ClientOnly>
  <OpencvPlayground initial-algo="gradient-flow" compact />
</ClientOnly>

> 想换示例图、上传自己的照片、或切换别的算法？去 [🎮 真机实验室](/playgrounds/)；想看完整的 14 个数学原理互动？去 [🧪 原理实验室](/math-lab/)。
