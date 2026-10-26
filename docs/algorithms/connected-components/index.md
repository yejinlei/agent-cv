<AlgorithmCard
  name="连通域分析（Two-Pass）"
  enName="Connected Components Labeling"
  chapter="ch03"
  branch="image-processing"
  year="1966 / 2008 / 2016"
  author="Rosenfeld / Wu et al. / Grana et al."
  paper="Rosenfeld 1966 / Wu-Lin 2009 BBDT / Grana 2016 SAUF"
  level="low"
  tagline="把二值图里「连在一起」的白像素涂成同一种颜色，一次遍历打完标签，还给每个斑点亮出户口本（面积、框、质心）"
  analogy="想象一张地图上有很多群岛，你坐直升机沿海岸线飞一圈：遇到一个没被标记的岛屿，就给它插一面旗子，之后所有连在一起的陆地都插同样颜色的旗子——最后每个岛都有一个专属颜色和档案（多大、在哪、中心在哪）。"
  scene="OCR 字符分割（先找字块再识别）、细胞计数、缺陷检测（数有几个瑕疵）、文字块分割、背景减除后找前景目标、任意二值图里的「物件个数统计」。"
  :pros='["O(N) 线性时间（Two-Pass 现代算法极快）", "直接给出面积/外接框/质心", "OpenCV 一行调用", "比 findContours 更适合「数个数」场景", "支持 4-连通/8-连通"]'
  :cons='["输入必须是干净的二值图", "大图像会产生很多临时标签，需要并查集优化", "不提供轮廓点（需要轮廓还是用 findContours）", "不区分孔洞（8-连通下背景和孔洞连通）"]'
/>


## 一分钟速览

**连通域分析（Two-Pass）**（Connected Components Labeling，1966 / 2008 / 2016，Rosenfeld / Wu et al. / Grana et al.）
第一遍扫描用并查集合并等价标签，第二遍把所有标签换成等价类根标签，同时统计每个标签的面积/框/质心——是工业界「数个数/筛大小」最高频的底层操作。

<ChildPages />


---

## 🚀 动手体验（浏览器里直接玩，不用装环境）

> 下面这些组件都在**你的浏览器本地运行**，不上传任何图片、也不用安装 OpenCV 或写代码。

### 🧪 先懂原理：邻域与距离到底在算什么

拖动滑块，看数学是怎么一步步变成图像的——纯 Canvas 绘制，秒开。

<ClientOnly>
  <MathVisualizer initial-tab="neighbor" compact />
</ClientOnly>

### 🎮 再跑真机：在浏览器里真跑 连通域分析（Two-Pass）

换成你自己的照片也行；下面还会**实时生成**对应的 Python / C++ / JavaScript 代码，拖参数时代码同步更新。

<ClientOnly>
  <OpencvPlayground initial-algo="connected" compact />
</ClientOnly>

> 想换示例图、上传自己的照片、或切换别的算法？去 [🎮 真机实验室](/playgrounds/)；想看完整的 14 个数学原理互动？去 [🧪 原理实验室](/math-lab/)。
