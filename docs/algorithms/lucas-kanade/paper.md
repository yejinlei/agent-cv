# 论文精读：Lucas-Kanade 1981

> **B. D. Lucas and T. Kanade**, "An Iterative Image Registration Technique with an Application to Stereo Vision", *Proceedings of the 7th International Joint Conference on Artificial Intelligence (IJCAI)*, pp. 674–679, 1981.
>
> 📄 [原文 PDF](https://www.ri.cmu.edu/pub_files/pub3/lucas_bruce_d_1981_1/lucas_bruce_d_1981_1.pdf) · 被引 **23,000+**

## 论文背景

1981 年，卡内基梅隆大学的 Bruce Lucas 和 Takeo Kanade 在做**立体视觉匹配**——就是给两张从不同角度拍的图，找出对应的点。

当时主流做法有两个：
- **块匹配（Block Matching）**：暴力滑动窗口算 SSD，慢，且只在纹理丰富处能用
- **Horn-Schunck（1981 同年发表）**：稠密光流，但需要全局迭代，不实时

Lucas 和 Kanade 的想法很朴素：**为什么非要让整幅图平滑？我只关心那几百个好点**。他们把问题局部化，在一个小窗口内用最小二乘"拟合"出位移，既快又稳。

## 三大核心贡献

### 贡献 1：把配准问题表述成最小二乘

给定两帧图像 $I$ 和 $J$，假设一个小窗口内所有像素做了相同的位移 $h$，我们要找 $h$ 使两帧在窗口内的差最小：

$$
h^* = \arg\min_h \sum_{x \in W} \left[ J(x+h) - I(x) \right]^2
$$

把 $J(x+h)$ 在 $x$ 处做一阶泰勒展开：

$$
J(x+h) \approx J(x) + h \cdot \nabla J(x)
$$

代入误差函数并对 $h$ 求导令其为零，得到线性方程 $G \cdot h = e$，其中 $G$ 是窗口内梯度外积和（即后来的结构张量 $M$），$e$ 是残差。

::: tip 为什么用最小二乘而不是简单的"求零点"
一个方程 $I_x u + I_y v = -I_t$ 无法解（两个未知数）——这就是**孔径问题**。但窗口里有 $N^2$ 个像素，每个提供一个方程，于是变成超定方程组，最小二乘给出"最符合大多数像素"的解。
:::

### 贡献 2：提出迭代求解 + 高斯牛顿

第一次解出来的 $h$ 是近似解（一阶泰勒展开的假设是小位移）。他们用了**迭代**：每次解出 $h$ 后把 $J$ 用双线性插值 warp 到 $x+h$，再在残差上重复求解，直到收敛。

这就是后来所有"光流迭代"范式的源头，也是 KLT 跟踪器名字里 **Iterative** 的由来。

### 贡献 3：指出局部结构决定可跟踪性

论文里明确讨论了：$G$ 矩阵（即结构张量 $M$）的条件数决定了这个点是否"好跟踪"。
- 两个特征值都大 → 角点 → 可跟
- 一个大一个小 → 边缘 → 孔径问题
- 两个都小 → 平坦区 → 完全不可跟

后来 Shi & Tomasi 1994 年"Good Features to Track"把这个判据形式化成"选最小特征值 $\lambda_2$ 大的点"，直接奠定了 KLT 跟踪的选点标准。

## 一个有意思的冷知识

这篇论文**本意是做立体匹配**（左右两帧的静态配准），不是做**视频跟踪**。把它扩展到视频序列、加上高斯金字塔、变成通用 KLT 跟踪器的是 Jean-Yves Bouguet 2000 年在 Intel 的技术报告 ["Pyramidal Implementation of the Lucas Kanade Feature Tracker"](https://docs.opencv.org/3.4/d4/dee/tutorial_optical_flow.html)。

所以你在 OpenCV 里用的 `calcOpticalFlowPyrLK`，其实是 Lucas-Kanade (1981) 的思想 + Bouguet (2000) 的金字塔实现 + Shi-Tomasi (1994) 的选点——三篇论文的合体。

## 算法伪代码（论文版）

```
输入：图像 I, J, 窗口 W, 初始位移 h₀ = 0
迭代直到 |Δh| < ε：
  1. 对 J 在 x+h 位置做插值，得到 J_warped
  2. 计算残差 e(x) = I(x) - J_warped(x)
  3. 在窗口 W 内计算 J 的梯度 ∇J
  4. 构造 G = Σ ∇J · ∇Jᵀ,   b = Σ ∇J · e(x)
  5. 解 Δh = G⁻¹ · b
  6. h = h + Δh
输出：h*
```

## 与 Horn-Schunck 的同年对比

1981 年是光流元年，Berthold Horn 和 Brian Schunck 同年在 *AI Lab Memo* 发表了 "Determining Optical Flow"：

| 维度 | Lucas-Kanade (1981) | Horn-Schunck (1981) |
|---|---|---|
| 稀疏/稠密 | **稀疏**（局部窗口） | **稠密**（整幅） |
| 约束 | 局部运动一致 | 全局平滑正则 |
| 求解 | 2×2 线性方程（解析解） | 变分迭代（Gauss-Seidel） |
| 速度 | ⚡ 实时 | 🐢 慢 |
| 边界 | 不处理边界 | 有平滑边界过冲 |
| 工业地位 | 视频跟踪/SLAM 绝对主流 | 主要用于教学和稠密光流研究 |

两个方向（局部稀疏 vs 全局稠密）从此分叉，44 年后仍然是光流的两大范式，甚至所有深度学习光流（FlowNet/RAFT）都能找到这两个思想的影子。

## 论文本身的局限

1. **小位移假设**：原始 LK 只在位移小于 1~2 像素时准，这也是后来需要金字塔的原因
2. **亮度恒常**：论文假设灰度不变，光照一变就挂
3. **局部线性**：一阶泰勒展开只能近似，需要迭代才能精化
4. **没有"好点"的自动化选择**：Shi-Tomasi (1994) 才补上
5. **没有金字塔**：Bouguet (2000) 才补上

## 这篇论文在工业界的影响

- OpenCV `calcOpticalFlowPyrLK`：KLT 跟踪器的事实标准
- ORB-SLAM / VINS-Mono / SVO 等视觉 SLAM 前端标配
- 所有动作捕捉系统（OptiTrack/Vicon）在相机间做点跟踪都用 LK 变体
- 视频稳像（iOS/Android 防抖、DJI 云台）核心就是 LK 光流估计全局运动
- 医学图像配准（超声、内窥镜跟踪）的基础工具
