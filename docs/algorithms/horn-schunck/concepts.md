# Horn-Schunck 稠密光流 · 核心概念

<AlgorithmCard
  name="Horn-Schunck 稠密光流"
  enName="Horn-Schunck Optical Flow"
  chapter="ch-13-motion-analysis"
  branch="geometry"
  year="1981"
  author="Berthold Horn / Brian Schunck"
  paper="paper-horn-schunck-1981"
  level="advanced"
  tagline="给光流加全局平滑约束，用变分法求每个像素运动，开创稠密光流学派"
  analogy="LK 光流像独立办案的刑警，每个小窗口自己算自己的；Horn-Schunck 像一个总指挥，要求所有像素运动方向差不多，全局求解出密密麻麻的运动箭头图"
  scene="稠密运动场估计、流体运动分析、医学影像序列、变分光流研究基准、视频慢动作插帧（传统方法）"
  :pros='["稠密输出(每像素)", "全局一致平滑", "变分学派开创者", "理论优美", "基准方法"]'
  :cons='["迭代慢", "大运动不适用(需金字塔)", "运动边界过度平滑", "亮度恒定假设苛刻", "工程上Farneback/DIS更常用"]'
/>

<div class="tip custom-block"><p>🧪 公式看不懂？去 <a href="/math-lab/">原理实验室</a> 拖动滑块直观体验卷积/梯度/高斯/霍夫/角点/RANSAC/光流等核心概念；看完原理再去本页底部 <a href="./source">源码/真机实验室</a> 亲手调参数。</p></div>


## Horn-Schunck 稠密光流的核心思想

给光流加全局平滑约束，用变分法求每个像素运动，开创稠密光流学派。LK 光流像独立办案的刑警，每个小窗口自己算自己的；Horn-Schunck 像一个总指挥，要求所有像素运动方向差不多，全局求解出密密麻麻的运动箭头图

**生活类比**：LK 光流像独立办案的刑警，每个小窗口自己算自己的；Horn-Schunck 像一个总指挥，要求所有像素运动方向差不多，全局求解出密密麻麻的运动箭头图

**典型应用**：稠密运动场估计、流体运动分析、医学影像序列、变分光流研究基准、视频慢动作插帧（传统方法）

```mermaid
flowchart LR
  A["输入图像"] --> B["核心处理"]
  B --> C["输出结果"]
```

## 核心概念详解

### 概念1：亮度恒定+小运动+空间平滑

同一点亮度不变 I(x,y,t)=I(x+u,y+v,t+1)，小运动允许泰勒展开 I_x·u+I_y·v+I_t=0，空间平滑要求相邻像素 (u,v) 差不多。

### 概念2：能量函数

HS 定义能量：$E = \int\int (I_x u+I_y v+I_t)^2 + \alpha^2(||\nabla u||^2 + ||\nabla v||^2) dxdy$。第一项是亮度恒定误差（数据项），第二项是平滑约束（正则项），α 控制平滑强度。

### 概念3：欧拉-拉格朗日方程

对能量函数求变分等于零，得到两个耦合的偏微分方程，用迭代方法（高斯-赛德尔迭代）求解：$u^{k+1}=\bar{u}^k - I_x(I_x\bar{u}^k+I_y\bar{v}^k+I_t)/(α²+I_x²+I_y²)$，v 类似。

```mermaid
flowchart TB
  A["初始化 u=0,v=0"] --> B["算 Ix,Iy,It"]
  B --> C["计算 u,v 的邻域均值"]
  C --> D["高斯-赛德尔迭代更新 u,v"]
  D -->|"未收敛"| C
  D -->|"收敛"| E["稠密光流场 (u,v) ✅"]
```

### 概念4：α 参数

α 越大，平滑项权重越大，光流越平滑但边界越糊；α 越小，数据项主导，光流越锐利但越噪。α² 取 100（α=10）左右是常见选择。

### 概念5：与 LK 的区别

LK 是局部方法（窗口内常数流），HS 是全局方法（全图平滑）；LK 产稀疏流（只在角点），HS 产稠密流（每像素）；LK 线性方程直接解，HS 迭代求解。


---

## 🧪 原理可视化

看不懂上面的公式？下面这个互动组件把「Lucas-Kanade 光流」画出来了——拖动滑块，看每一步怎么算。

<ClientOnly>
  <MathVisualizer initial-tab="lk" compact />
</ClientOnly>

> 想看它在真实照片上的实际效果？回到 [本算法首页](./index) 或去 [🎮 真机实验室](/playgrounds/)。

<!-- AUTO-EXTENSION-2 -->

## 🧓 大白话：Horn-Schunck 光流 = "全局平滑的稠密光流"

Lucas-Kanade 是**局部**方法（假设一个小窗口内光流不变），所以只能算稀疏点的光流，而且在边缘处易漂。

**Horn-Schunck（1981）** 是第一个**稠密光流**算法：它提出一个全局能量函数

$$E = \iint (I_x u + I_y v + I_t)^2 + \alpha(|\nabla u|^2 + |\nabla v|^2) \, dxdy$$

第一项是**光流约束方程**（亮度不变），第二项是**平滑项**（α 越大，光流场越平滑），最小化这个能量得到每一个像素的光流 (u,v)——用变分法+迭代求解。

## Lucas-Kanade vs Horn-Schunck vs Farnebäck

| 方法 | 稀疏/稠密 | 特点 |
| --- | --- | --- |
| Lucas-Kanade | 稀疏 | 快，点要可跟踪 |
| Horn-Schunck | 稠密 | 全局平滑，边界易糊 |
| Farnebäck | 稠密 | 基于多项式展开，精度较好、速度中等 |
| TV-L1 | 稠密 | L1 数据项+全变分平滑，保边但慢 |

Horn-Schunck 由于平滑项是 L2，会在运动边界处"过度平滑"（一个物体的运动溢到旁边），现在主要用于教学；工业稠密光流常用 **Farnebäck** 或 **TV-L1** 或深度学习光流（RAFT）。
