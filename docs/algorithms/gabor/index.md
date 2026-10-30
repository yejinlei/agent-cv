---
layout: doc
---

<AlgorithmCard
  name="Gabor 滤波器"
  enName="Gabor Filter / Gabor Wavelet"
  chapter="ch07"
  branch="image-processing"
  year="1946 / 1980s"
  author="Dennis Gabor (1946) / Daugman (1985) / Jain et al. (1990s)"
  paper="Daugman 1985 / Bovik et al. 1990"
  level="mid"
  tagline="一块带方向和纹路频率的「放大镜」，旋转不同角度扫一遍图，就能把对应方向的纹理抓出来"
  analogy="想象你拿一把梳子去刮不同方向的木纹：梳子方向和木纹平行时阻力最大（响应强），垂直时没感觉。Gabor 核就是这样一把梳子——一个特定方向、特定频率的「纹路探针」，通常要做 8 个方向 × 5 个频率共 40 个核组成 Gabor 滤波器组，才能把图像里各个方向、粗细的纹理全抓出来。"
  scene="指纹识别（核心）、虹膜识别（Daugman 用的就是它）、纹理分类、布匹/纸张缺陷检测、文档/车牌识别前处理、人脸识别（弹性图匹配）、边缘检测（多方向）。"
  :pros='["时频局部化最优（不确定性原理下界）", "方向选择性强、尺度选择性强", "类似生物视觉 V1 区简单细胞感受野", "OpenCV 直接生成核", "对光照/对比度局部鲁棒"]'
  :cons='["需要一个滤波器组（几十核），计算量大", "参数多（波长/方向/相位/带宽/纵横比）", "输出是多维特征（每个像素 40 维响应）", "非旋转不变（需要做多个方向）"]'
/>


## 一分钟速览

**Gabor 滤波器**（Gabor Filter / Gabor Wavelet，1946 / 1980s，Dennis Gabor (1946) / Daugman (1985) / Jain et al. (1990s)）
Gabor 核 = 高斯窗口 × 复正弦波；用不同方向/尺度组成滤波器组，卷积后每个像素得到一个响应向量，就是该点的「纹理指纹」——是工业纹理分析和生物识别的黄金标准。

<ChildPages />


---

## 🚀 动手体验（浏览器里直接玩，不用装环境）

> 下面这些组件都在**你的浏览器本地运行**，不上传任何图片、也不用安装 OpenCV 或写代码。

### 🧪 先懂原理：傅里叶频域到底在算什么

拖动滑块，看数学是怎么一步步变成图像的——纯 Canvas 绘制，秒开。

<ClientOnly>
  <MathVisualizer initial-tab="fourier" compact />
</ClientOnly>

### 🎮 再跑真机：在浏览器里真跑 Gabor 滤波器

换成你自己的照片也行；下面还会**实时生成**对应的 Python / C++ / JavaScript 代码，拖参数时代码同步更新。

<ClientOnly>
  <OpencvPlayground initial-algo="gabor" compact />
</ClientOnly>

> 想换示例图、上传自己的照片、或切换别的算法？去 [🎮 真机实验室](/playgrounds/)；想看完整的 14 个数学原理互动？去 [🧪 原理实验室](/math-lab/)。
