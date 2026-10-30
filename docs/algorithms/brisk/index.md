---
layout: doc
---

<AlgorithmCard
  name="BRISK 二进制鲁棒不变可伸缩关键点"
  enName="Binary Robust Invariant Scalable Keypoints"
  chapter="ch08"
  branch="feature-detection"
  year="2011"
  author="Stefan Leutenegger / Margarita Chli / Roland Siegwart"
  paper="BRISK (ICCV 2011)"
  level="mid"
  tagline="FAST 找角点 + 同心圆圈采样 + 长短点对分工，速度比 SIFT 快一个量级还带尺度旋转"
  analogy="ORB 像一个快枪手：拔枪快、出弹快，但准星简单、打不远；BRISK 像一个特种兵：在战场上布好同心圆阵地（多层采样），远处点对用来估方向（长点对），近处点对用来拼指纹（短点对），512 位描述子比 ORB 的 256 位更抗噪。"
  scene="无人机航拍拼接、SLAM（尤其是 OKVIS 作者的成名作）、移动 AR、需要尺度不变但算力有限的嵌入式场景。"
  :pros='["尺度+旋转不变", "二进制 512 位，汉明距离匹配快", "比 ORB 更稳、比 SIFT/SURF 快", "专利免费（可商用）", "OpenCV 原生支持"]'
  :cons='["速度略慢于 ORB（仍快于 SIFT）", "采样点固定模式参数多", "对极端视角变化弱于 AKAZE", "描述子更长（64 字节）"]'
/>


## 一分钟速览

**BRISK 二进制鲁棒不变可伸缩关键点**（Binary Robust Invariant Scalable Keypoints，2011，Stefan Leutenegger / Margarita Chli / Roland Siegwart）
用 AGAST 在多尺度金字塔上找角点，再用精心设计的同心圆采样模式生成 512 位二进制描述子，长点对估朝向、短点对拼指纹，是「免费版 SIFT」的有力竞争者。

<ChildPages />


---

## 🚀 动手体验（浏览器里直接玩，不用装环境）

> 下面这些组件都在**你的浏览器本地运行**，不上传任何图片、也不用安装 OpenCV 或写代码。

### 🎮 再跑真机：在浏览器里真跑 BRISK 二进制鲁棒不变可伸缩关键点

换成你自己的照片也行；下面还会**实时生成**对应的 Python / C++ / JavaScript 代码，拖参数时代码同步更新。

<ClientOnly>
  <OpencvPlayground initial-algo="brisk" compact />
</ClientOnly>

> 想换示例图、上传自己的照片、或切换别的算法？去 [🎮 真机实验室](/playgrounds/)；想看完整的 14 个数学原理互动？去 [🧪 原理实验室](/math-lab/)。
