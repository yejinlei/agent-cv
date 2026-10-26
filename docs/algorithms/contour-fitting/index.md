---
layout: doc
---

<AlgorithmCard
  name="轮廓拟合与多边形逼近"
  enName="Contour Fitting & Polygon Approximation"
  chapter="第8章 · 形状分析"
  chapterLink="/chapters/ch08-shape"
  branch="图像处理"
  year="1973"
  author="Urs Ramer / David Douglas / Thomas Peucker；椭圆拟合见 Fitzgibbon 1996"
  paper="https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm"
  level="基础"
  tagline="把一坨几百个点的轮廓，压成几条线、一个圆或一个椭圆"
  analogy="你沿着一个不规则湖岸走了 500 步，记下每步的位置。要跟别人描述这个湖，你不会报 500 个坐标，而会说「大概是个椭圆，长轴 3 公里」。轮廓拟合就是干这个——用最少的参数概括轮廓的形状。"
  scene="工业零件尺寸测量、车牌/纸面矫正、形状分类、手写笔迹简化、地图边界压缩"
  :pros='["用极少参数描述形状（压缩）", "抗噪（拟合容忍离群点）", "直接给出几何量（周长/角度/长短轴）", "计算快，适合实时检测"]'
  :cons='["epsilon 太大会丢角点", "椭圆拟合对离群点敏感（需鲁棒版）", "只对单连通轮廓有效", "对凹形/复杂形状表达能力有限"]'
/>

## 一句话理解

> 用少量参数（几条直线段、一个圆或椭圆）去近似一条由大量像素点组成的轮廓。

## 为什么需要它？

findContours 给你的是成百上千个像素点，没法直接用。要测尺寸、判形状、做分类，就得把轮廓**抽象成几何量**。多边形逼近、最小外接圆、椭圆拟合就是这套「从点集到形状」的工具箱。

## 生活场景

质检线上要判断螺母是不是圆的、螺栓有没有变形。把轮廓拟合出椭圆，比一下长短轴之比，一个比值就能判定合格与否。

## 七页速览

| 页面 | 内容 | 你会得到什么 |
|------|------|--------------|
| [第1页 · 总览](index) | 你现在看的 | 快速判断「要不要用它」 |
| [第2页 · 论文溯源](paper) | 原始论文 | 搞懂 Douglas-Peucker 逼近算法怎么「扔点」 |
| [第3页 · 核心概念](concepts) | 原理直觉 | 分清 approxPolyDP / fitEllipse / minEnclosingCircle 各用在哪 |
| [第4页 · 算法架构](architecture) | 流程图与步骤 | 理解 epsilon 与形状保真度的取舍 |
| [第5页 · 源码实现](source) | 可跑代码 | 抄一段从轮廓到几何量的完整代码 |
| [第6页 · 踩坑清单](painpoints) | 新手陷阱 | 避开丢角点、离群点拉偏等坑 |
| [第7页 · 调参口诀](tricks) | 实战经验 | 会用拟合结果做形状分类 |

::: tip 阅读建议
第一次接触请按 1 → 3 → 4 顺序读，先建立直觉再看流程；要动手就直接跳到第 5 页抄代码。
:::


---

## 🚀 动手体验（浏览器里直接玩，不用装环境）

> 下面这些组件都在**你的浏览器本地运行**，不上传任何图片、也不用安装 OpenCV 或写代码。

### 🎮 再跑真机：在浏览器里真跑 轮廓拟合与多边形逼近

换成你自己的照片也行；下面还会**实时生成**对应的 Python / C++ / JavaScript 代码，拖参数时代码同步更新。

<ClientOnly>
  <OpencvPlayground initial-algo="contours" compact />
</ClientOnly>

> 想换示例图、上传自己的照片、或切换别的算法？去 [🎮 真机实验室](/playgrounds/)；想看完整的 14 个数学原理互动？去 [🧪 原理实验室](/math-lab/)。
