---
layout: doc
---

<AlgorithmCard
  name="距离变换"
  enName="Distance Transform"
  chapter="ch03"
  branch="image-processing"
  year="1966"
  author="Azriel Rosenfeld / John Pfaltz / Gunilla Borgefors"
  paper="Rosenfeld & Pfaltz 1966 / Borgefors 1986"
  level="low"
  tagline="给二值图每个像素发一张「到最近墙有多远」的地图，中心最远、边缘最近；分水岭、骨架、点匹配都要靠它"
  analogy="想象在一个漆黑的迷宫里（白色=能走，黑色=墙），给每个位置标出「离最近一堵墙有几步」：墙根是 0，走廊中间是大数字，大厅正中央是最大的数。画成热力图，最亮的地方就是「整个区域的脊梁」——这就是距离变换。"
  scene="分水岭分割的种子生成、目标骨架提取、二值图匹配（chamfer matching）、形态学细化、医学影像中心线提取、文字识别的字宽估计。"
  :pros='["O(N) 复杂度（两次扫描）", "结果稳定、可解释", "是分水岭、骨架、匹配等算法的基础", "OpenCV 一行调用"]'
  :cons='["输入必须是干净的二值图（0/1 或 0/255）", "不同距离类型精度不同（L1/L2/C）", "边界条件要注意", "距离类型选错会导致结果偏差"]'
/>


## 一分钟速览

**距离变换**（Distance Transform，1966，Azriel Rosenfeld / John Pfaltz / Gunilla Borgefors）
对二值图做两次反向扫描，用 3×3 邻域最小距离递推，得到每个前景点到最近背景的距离图——形态学、分割、匹配的底层积木。

<ChildPages />


---

## 🚀 动手体验（浏览器里直接玩，不用装环境）

> 下面这些组件都在**你的浏览器本地运行**，不上传任何图片、也不用安装 OpenCV 或写代码。

### 🧪 先懂原理：邻域与距离到底在算什么

拖动滑块，看数学是怎么一步步变成图像的——纯 Canvas 绘制，秒开。

<ClientOnly>
  <MathVisualizer initial-tab="neighbor" compact />
</ClientOnly>

### 🎮 再跑真机：在浏览器里真跑 距离变换

换成你自己的照片也行；下面还会**实时生成**对应的 Python / C++ / JavaScript 代码，拖参数时代码同步更新。

<ClientOnly>
  <OpencvPlayground initial-algo="distance" compact />
</ClientOnly>

> 想换示例图、上传自己的照片、或切换别的算法？去 [🎮 真机实验室](/playgrounds/)；想看完整的 14 个数学原理互动？去 [🧪 原理实验室](/math-lab/)。
