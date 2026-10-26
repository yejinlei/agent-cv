# FAST 角点检测

<AlgorithmCard
  name="FAST 角点检测"
  enName="Features from Accelerated Segment Test"
  chapter="第4章 · 基元检测"  chapterLink="/chapters/ch04-primitives"
  branch="feature-detection"
  year="2006"
  author="Edward Rosten / Tom Drummond"
  paper="https://link.springer.com/chapter/10.1007/11744023_34"
  level="mid"
  tagline="用一个圆圈 16 个邻居，一眼认出角点，速度比 Harris 快 10 倍"
  analogy="FAST 像一个哨兵：不进屋检查，只趴在窗户上数——窗外 16 个邻居里如果连续 12 个都比屋里亮或都比屋里暗，那这间房肯定是个「犄角旮旯」"
  scene="SLAM、AR、实时物体识别里做特征点检测，毫秒级返回几千个点，CPU 上就能跑 60fps"
  :pros='["速度极快（比 Harris 快 10 倍以上）", "实现简单，一个 for 循环就够", "角点重复率高", "OpenCV 高度优化"]'
  :cons='["不具备尺度不变性", "不具备旋转不变性（后来 ORB 加上了）", "阈值敏感，噪声点多", "需要搭配 NMS 避免扎堆", "不含描述子，必须另配 BRIEF/ORB"]'
/>

## 一句话理解

用一个圆圈 16 个邻居，一眼认出角点，速度比 Harris 快 10 倍。FAST 像一个哨兵：不进屋检查，只趴在窗户上数——窗外 16 个邻居里如果连续 12 个都比屋里亮或都比屋里暗，那这间房肯定是个「犄角旮旯」。

```mermaid
flowchart LR
  A["输入图像"] --> B["FAST 角点检测"]
  B --> C["输出结果"]
```

## 生活类比

FAST 像一个哨兵：不进屋检查，只趴在窗户上数——窗外 16 个邻居里如果连续 12 个都比屋里亮或都比屋里暗，那这间房肯定是个「犄角旮旯」

## 它解决什么问题

SLAM、AR、实时物体识别里做特征点检测，毫秒级返回几千个点，CPU 上就能跑 60fps。

在传统 CV 的六分支体系中，FAST 角点检测 属于 **feature-detection** 分支，主要解决的是该分支中用一个圆圈 16 个邻居，一眼认出角点，速度比 Harris 快 10 倍的问题。

## 核心优点

- ✅ **速度极快（比 Harris 快 10 倍以上）**
- ✅ **实现简单，一个 for 循环就够**
- ✅ **角点重复率高**
- ✅ **OpenCV 高度优化**

## 它的短板

- ⚠️ 不具备尺度不变性
- ⚠️ 不具备旋转不变性（后来 ORB 加上了）
- ⚠️ 阈值敏感，噪声点多
- ⚠️ 需要搭配 NMS 避免扎堆
- ⚠️ 不含描述子，必须另配 BRIEF/ORB

## 本算法档案包含 7 个页面

| 页面 | 内容 |
|---|---|
| [论文故事](/algorithms/fast/paper) | 作者、发表时间、核心贡献、为什么它会被提出 |
| [核心概念](/algorithms/fast/concepts) | 用生活比方讲清它依赖的关键概念 |
| [算法流程](/algorithms/fast/architecture) | 一步步走通算法全流程，配 mermaid 图 |
| [源码实现](/algorithms/fast/source) | OpenCV 调用 + NumPy 手写最小实现 |
| [踩坑清单](/algorithms/fast/painpoints) | 新手最常犯的 N 个错误 |
| [调参口诀](/algorithms/fast/tricks) | 参数怎么选、实战技巧、性能优化 |

## 相关链接

- 返回 [六大分支总览](/branches/)
- [FAST 角点检测所在分支](/branches/feature-detection/)
- [算法档案总览](/algorithms/)


---

## 🚀 动手体验（浏览器里直接玩，不用装环境）

> 下面这些组件都在**你的浏览器本地运行**，不上传任何图片、也不用安装 OpenCV 或写代码。

### 🎮 再跑真机：在浏览器里真跑 FAST 角点检测

换成你自己的照片也行；下面还会**实时生成**对应的 Python / C++ / JavaScript 代码，拖参数时代码同步更新。

<ClientOnly>
  <OpencvPlayground initial-algo="fast" compact />
</ClientOnly>

> 想换示例图、上传自己的照片、或切换别的算法？去 [🎮 真机实验室](/playgrounds/)；想看完整的 14 个数学原理互动？去 [🧪 原理实验室](/math-lab/)。
