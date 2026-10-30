---
layout: doc
---

<AlgorithmCard
  name="AKAZE 加速 KAZE 特征"
  enName="Accelerated-KAZE"
  chapter="ch08"
  branch="feature-detection"
  year="2013"
  author="Pablo F. Alcantarilla / Jesús Nuevo / Adrien Bartoli"
  paper="AKAZE (BMVC 2013)"
  level="mid"
  tagline="用非线性扩散替代高斯金字塔，边缘保留得更好；描述子是改进版二进制 LDB，免费且比 SIFT 鲁棒"
  analogy="SIFT/SURF/ORB/BRISK 的尺度金字塔都用**高斯模糊**——相当于给照片蒙一层毛玻璃，细节和边缘一起糊掉；KAZE/AKAZE 用**非线性扩散**——像让墨水在宣纸上晕开，**边缘处不晕、平坦处才晕**，所以尺度空间里的边缘一直锐利。"
  scene="需要高重复率、对边缘细节敏感的场景：文档拼接、低光照图像匹配、航拍拼接、对精度要求高的 SLAM。"
  :pros='["非线性尺度空间，边缘保留好", "重复率高于 ORB/BRISK", "M-LDB 二进制描述子匹配快", "专利免费（KAZE 也是免费）", "OpenCV 原生支持"]'
  :cons='["比 ORB 慢（但比 SIFT/KAZE 快）", "非线性扩散需要迭代求解（有一定开销）", "参数比 ORB 多", "在非常简单的场景优势不明显"]'
/>


## 一分钟速览

**AKAZE 加速 KAZE 特征**（Accelerated-KAZE，2013，Pablo F. Alcantarilla / Jesús Nuevo / Adrien Bartoli）
用 FED 快速求解非线性扩散方程建立尺度空间，Hessian 检测关键点，再用 Modified-LDB 二进制描述子，是目前 OpenCV 里**性能最好且专利免费**的特征检测器之一。

<ChildPages />


---

## 🚀 动手体验（浏览器里直接玩，不用装环境）

> 下面这些组件都在**你的浏览器本地运行**，不上传任何图片、也不用安装 OpenCV 或写代码。

### 🎮 再跑真机：在浏览器里真跑 AKAZE 加速 KAZE 特征

换成你自己的照片也行；下面还会**实时生成**对应的 Python / C++ / JavaScript 代码，拖参数时代码同步更新。

<ClientOnly>
  <OpencvPlayground initial-algo="akaze" compact />
</ClientOnly>

> 想换示例图、上传自己的照片、或切换别的算法？去 [🎮 真机实验室](/playgrounds/)；想看完整的 14 个数学原理互动？去 [🧪 原理实验室](/math-lab/)。
