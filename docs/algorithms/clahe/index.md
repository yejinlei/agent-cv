---
layout: doc
---

<AlgorithmCard
  name="CLAHE 限制对比度自适应直方图均衡"
  enName="Contrast Limited Adaptive Histogram Equalization"
  chapter="ch03"
  branch="image-processing"
  year="1994"
  author="Karel Zuiderveld"
  paper="Graphics Gems IV (1994)"
  level="low"
  tagline="每个小格子自己拉对比度，超过阈值的部分切下来平均分给所有人，既增强细节又不放大噪声"
  analogy="普通直方图均衡像给整个房间装一个总调光开关：亮的地方太亮，暗的地方太暗。普通 AHE 像给每平米装一个小开关，但暗部噪声也被放大成雪花。CLAHE 给每个小开关加了「功率上限」：你不能把噪声拉到和信号一样亮，超过的功率平均分给大家——细节出来了，噪声还在底。"
  scene="医学影像（X 光、CT、眼底照）、低光照/逆光图像增强、人脸识别预处理、OCR 文档增强、车牌识别前处理。"
  :pros='["局部增强，能照顾暗部细节", "clipLimit 限制噪声放大", "双线性插值无网格边界", "速度快、无 GPU 依赖", "OpenCV 原生、一个 API 搞定"]'
  :cons='["clipLimit 要根据噪声调", "tileGridSize 影响局部性", "对彩色图要转到 LAB 空间处理 L 通道", "过度增强会产生「脏脏」的对比度"]'
/>


## 一分钟速览

**CLAHE 限制对比度自适应直方图均衡**（Contrast Limited Adaptive Histogram Equalization，1994，Karel Zuiderveld）
把图像分成 8×8 的小 tile，每个 tile 内做带 clip 限制的直方图均衡，再用双线性插值拼回去——一个被工业界用了 30 年仍在首选的**对比度增强**算法。

<ChildPages />


---

## 🚀 动手体验（浏览器里直接玩，不用装环境）

> 下面这些组件都在**你的浏览器本地运行**，不上传任何图片、也不用安装 OpenCV 或写代码。

### 🧪 先懂原理：直方图到底在算什么

拖动滑块，看数学是怎么一步步变成图像的——纯 Canvas 绘制，秒开。

<ClientOnly>
  <MathVisualizer initial-tab="hist" compact />
</ClientOnly>

### 🎮 再跑真机：在浏览器里真跑 CLAHE 限制对比度自适应直方图均衡

换成你自己的照片也行；下面还会**实时生成**对应的 Python / C++ / JavaScript 代码，拖参数时代码同步更新。

<ClientOnly>
  <OpencvPlayground initial-algo="clahe" compact />
</ClientOnly>

> 想换示例图、上传自己的照片、或切换别的算法？去 [🎮 真机实验室](/playgrounds/)；想看完整的 14 个数学原理互动？去 [🧪 原理实验室](/math-lab/)。
