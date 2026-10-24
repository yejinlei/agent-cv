# 论文解读：A Flexible New Technique for Camera Calibration (2000)

> **论文**：Zhang, Zhengyou. "A Flexible New Technique for Camera Calibration." *IEEE T-PAMI*, Vol. 22, No. 11, Nov 2000, pp. 1330-1334.
>
> **链接**：[微软研究院官方 PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr98-71.pdf)
>
> **作者**：张正友（Zhengyou Zhang），当时在微软研究院（Microsoft Research），后为 IEEE Fellow、ACM Fellow。这篇论文**被引用超过 2.7 万次**，是 OpenCV/Matlab/HALCON 标定工具的理论基础。

## 历史背景：1999 年之前标定有多痛苦

### 当时的三种方案都有明显问题

| 方案 | 代表 | 问题 |
|---|---|---|
| **3D 标定物** | Tsai 1987、Faugeras 1986 | 精密加工的 3D 立方块/标定架，几千到几万元 |
| **主动视觉** | Hartley 1992 | 需要精密运动台控制相机做正交平移 |
| **自标定** | Faugeras 1992、Maybank 1992 | 什么都不用，只靠场景中的点对应 | 对噪声极敏感，实际不可用 |

> 张正友在 1998 年微软技术报告 TR-98-71 里提出了一个"中间路线"：**用平面作为标定物，但不需要知道平面怎么动**——平面只要是平的，打印在纸上就行。1998 年 ICCV 做了报告，2000 年以短文形式发在 T-PAMI。

### 核心洞察

张正友的关键洞察只有一句话：

> **如果所有标定点都在一个平面上，那么从这个平面到图像的变换就是一个"单应矩阵" H（8 自由度）；而 H 内藏了相机内参 K 的约束。拍至少 3 张不同角度的图，就能用这些约束闭解 K。**

这个洞察把"需要 3D 物体"这个约束直接扔掉，代之以"多姿态下的同一平面"，成本从几千元降到一张 A4 纸。

## 论文三大核心贡献

### 贡献一：平面单应与内参约束（§3.1 Closed-form solution）

这是论文的数学心脏。

**设定**：世界坐标系 z=0 放在棋盘平面上，棋盘上点 $(X, Y, 0)$，图像点 $(u, v)$。投影公式：

$$
s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = K \begin{bmatrix} r_1 & r_2 & t \end{bmatrix} \begin{bmatrix} X \\ Y \\ 1 \end{bmatrix} = H \begin{bmatrix} X \\ Y \\ 1 \end{bmatrix}
$$

其中 $r_1, r_2$ 是旋转矩阵的前两列，$t$ 是平移。因此：

$$
H = \lambda K \begin{bmatrix} r_1 & r_2 & t \end{bmatrix}
$$

**关键约束**：$r_1$ 和 $r_2$ 是单位正交向量：

$$
r_1^T r_2 = 0, \quad r_1^T r_1 = r_2^T r_2 = 1
$$

把 $H = [h_1 \ h_2 \ h_3]$ 代入，可得：

$$
h_1^T K^{-T} K^{-1} h_2 = 0, \quad h_1^T K^{-T} K^{-1} h_1 = h_2^T K^{-T} K^{-1} h_2
$$

记 $B = K^{-T} K^{-1}$（这是一个对称矩阵，6 个独立元素），每张图给 2 个方程：

$$
h_1^T B h_2 = 0, \quad h_1^T B h_1 = h_2^T B h_2
$$

$B$ 有 5 个自由度（$f_x, f_y, c_x, c_y, \gamma$），**2 张图只能给 4 个方程，3 张图给 6 个方程，恰好解出 5 个内参**。

这就是为什么"至少拍 3 张不同角度的棋盘照片"的数学根源。

**生活理解**：想象你用一把未知单位的尺子去量一个已知长度的东西，量一次只能得到一个比例；从不同位置量三次（看到尺子的不同投影），就可以反推出"这把尺子的实际刻度"。

### 贡献二：径向畸变的闭解估计（§3.2 Estimating radial distortion）

真实镜头有径向畸变（桶形/枕形），如果不处理，会让内参估计偏差。张正友在闭解阶段就给出了 k1、k2 的线性估计：

$$
\begin{bmatrix} (u-u_0)(x'^2+y'^2) & (u-u_0)(x'^2+y'^2)^2 \\ (v-v_0)(x'^2+y'^2) & (v-v_0)(x'^2+y'^2)^2 \end{bmatrix} \begin{bmatrix} k_1 \\ k_2 \end{bmatrix} = \begin{bmatrix} \hat{u}-u \\ \hat{v}-v \end{bmatrix}
$$

其中 $(x', y')$ 是理想针孔投影坐标，$(\hat{u}, \hat{v})$ 是观测到的畸变像素坐标，$(u, v)$ 是用估计出的 K 算出的无畸变像素坐标。

**这是一个最小二乘问题，每张图、每个点贡献 2 个方程，直接解 k1、k2**。

### 贡献三：最大似然非线性精化（§3.3 Maximum likelihood estimation）

闭解给出的 K、dist、外参初值在有噪声时不是最优，论文给出用 Levenberg-Marquardt（LM）最小化重投影误差：

$$
\sum_{i=1}^{N} \sum_{j=1}^{M} \left\| m_{ij} - \hat{m}(K, k_1, k_2, R_i, t_i, M_j) \right\|^2
$$

其中 $m_{ij}$ 是第 i 张图上第 j 个点的观测像素坐标，$\hat{m}(\cdot)$ 是用当前参数投影出来的点。

**这就是为什么 calibrateCamera 内部会跑 LM 迭代**：闭解给初值，非线性优化把重投影误差压到最小。

## 论文实验结论（§4 Experimental Results）

| 实验 | 配置 | 精度 |
|---|---|---|
| **仿真数据** | 20 张图，3 个噪声级别 | 0.1 像素高斯噪声下，焦距误差 < 0.2% |
| **桌面实验** | 640×480，20 张 | 重投影误差 0.099 像素 |
| **对比 Tsai** | 同数据 | 精度相当，但张氏不需要运动台 |

## 为什么是"Flexible New Technique"（"灵活"在哪里）

1. **标定物灵活**：打印在 A4 纸上，贴在平面上（木板、书本、墙壁都行）
2. **拍摄灵活**：不需要运动台，手持相机/固定相机拍移动棋盘都行
3. **数量灵活**：≥3 张就能标，多拍几张精度更高
4. **模型灵活**：可扩展到带切向畸变的模型（OpenCV 就是这么做的）
5. **实现灵活**：算法对镜头类型不敏感，针孔模型通用

## 论文里被忽略但工业界最看重的细节

### 细节一：拍摄姿态分布的建议
论文明确指出：**图片不能都从同一方向拍**，否则约束退化。建议：
- 图片要覆盖不同的旋转角度（绕光轴倾斜 ±30°）
- 要覆盖不同的距离（近/中/远）
- 棋盘要覆盖图像各个位置（中心/边缘/四角）

### 细节二：B 矩阵的分解
得到 B 后怎么恢复 K？论文给出了明确的闭式分解公式（§3.1, Eq. 11-14）：从 B 的 6 个元素直接算出 $v_0, \lambda, f_x, f_y, \gamma, u_0$。这一步 OpenCV 内部已经实现，但**理解它有助于你理解为什么"拍歪了的图也能标"——因为 B 的约束不依赖具体姿态**。

### 细节三：退化情况
论文也指出了两种退化情况：
- **所有图像都是同一方向平行拍摄**：约束不足（平面平行时 H 只剩 6 个自由度）
- **光心落在所有棋盘平面的共焦平面上**：数学上退化

**这就是为什么你拍了 20 张但误差还是很大——如果都是正对着拍，数学上等于只拍了 1 张。**

## 伪代码（论文附录版）

```
Input:  N 张图片，每张有 M 个世界点（棋盘格点）
Output: K, dist, {R_i, t_i}

// Step 1: 检测每张图的图像点 m_ij
for i = 1..N:
    m_ij = 角点检测 + 亚像素优化

// Step 2: 估计每张图的单应 H_i
for i = 1..N:
    H_i = DLT(M_j, m_ij)  // 8 个参数的单应

// Step 3: 闭解内参 K
B = solve_linear(∪_i {h_i1^T B h_i2 = 0, h_i1^T B h_i1 = h_i2^T B h_i2})
K = decompose_B(B)

// Step 4: 估计每张图的外参
for i = 1..N:
    [R_i | t_i] = extrinsic_from_H(K, H_i)

// Step 5: 闭解径向畸变 k1, k2
[k1, k2] = solve_linear_distortion(K, {R_i,t_i}, {M_j, m_ij})

// Step 6: LM 非线性优化
params = LM_minimize(reprojection_error, params0=[K, k1, k2, {R_i,t_i}])

// Step 7: 返回
return params.K, [k1, k2, 0, 0, 0], params.{R_i,t_i}
```

## 后世影响

| 工具 | 底层算法 |
|---|---|
| OpenCV `calibrateCamera` | 张氏 + Brown 畸变模型扩展 |
| MATLAB Camera Calibrator App | 张氏（实现完全一致） |
| HALCON `calibrate_cameras` | 张氏（工业级扩展） |
| ROS `camera_calibration` | 基于 OpenCV，张氏 |
| Kalibr（多相机/IMU）| 张氏 + 时间同步 |
| AprilCal（AprilTag 标定）| 张氏变种（用 AprilTag 替代棋盘）|
| Open3D RGB-D 标定 | 张氏 |

**这篇论文是计算机视觉工程落地的"0 号基础设施"**——任何一个做过相机项目的工程师，都应该至少读过一遍它的 §3。
