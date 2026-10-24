# 原始论文精读 · 霍夫变换

> 霍夫变换从专利到标准算法，经过了三次关键改进，最终在车道线/圆检测上用了 60 年。

## 三份关键文献

### ① Hough 1962 专利（原始思想）

- **标题**：Method and Means for Recognizing Complex Patterns
- **作者**：Paul V. C. Hough
- **年份**：1962
- **来源**：U.S. Patent 3069654
- **被引**：~12000
- **时代背景**：Hough 当时在波音做气泡室（bubble chamber）粒子径迹分析，需要从大量照片里自动找出带电粒子留下的直线路径——当时全靠人工描，工作量巨大。

**原始想法**：
- 图像里一条直线上的点 $(x,y)$ 满足 $y = kx + b$，可以反过来把它看成 $(k,b)$ 参数空间的一个点。
- 一个边缘点 $(x_0,y_0)$ 对应 $(k,b)$ 平面上一条直线 $b = -x_0 k + y_0$。
- **同一条直线上的 N 个点，在 (k,b) 空间交汇于同一点**——这就是直线参数。

**原始方法的致命问题**：
- 垂直直线斜率 $k$ 无穷大，无法用 $(k,b)$ 参数化；近垂直直线 $k$ 很大，累加器需要极大存储。
- 参数范围无界（$k \in (-\infty, +\infty)$），累加器难以分配。

### ② Duda & Hart 1972（极坐标参数化，标准 HT 诞生）

- **标题**：Use of the Hough Transformation to Detect Lines and Curves in Pictures
- **作者**：Richard O. Duda, Peter E. Hart
- **年份**：1972
- **来源**：Communications of the ACM, Vol. 15, No. 1
- **被引**：~14000
- **时代背景**：Duda 和 Hart 是 SRI 人工智能组的元老（两人也是《Pattern Classification》这本经典教材的作者），他们把 Hough 的专利思想从工程技巧变成了**可分析的标准算法**。

**核心贡献**：
1. **改用极坐标参数化**：$x \cos\theta + y \sin\theta = \rho$
   - $\theta \in [-\pi/2, \pi/2]$（或 $[0, \pi]$），$\rho \in [-\rho_\max, \rho_\max]$，**参数空间有界**！
   - 垂直直线 $\theta = 0$，水平直线 $\theta = \pi/2$，完美覆盖所有方向。
2. 一个边缘点在 $(\rho, \theta)$ 空间变成**一条正弦曲线**（不是 (k,b) 里的直线）。
3. 多条正弦曲线的交点就是直线。
4. 系统分析了累加器量化步长 $\Delta\rho, \Delta\theta$ 对精度和假阳性的影响。

👉 **这篇论文之后，"霍夫变换"才真正成为标准算法**。OpenCV 的 `HoughLines` 实现的就是 Duda-Hart 版本。

### ③ Matas, Galambos, Kittler 1998 PPHT（渐进概率霍夫）

- **标题**：Progressive Probabilistic Hough Transform
- **作者**：Jiri Matas, C. Galambos, J. Kittler
- **年份**：1998
- **来源**：BMVC / CVIU 2000
- **时代背景**：标准 HT 必须遍历所有边缘点，90 年代末高分辨率图像开始出现，速度成为瓶颈。

**核心贡献**：
1. **不遍历所有边缘点**：随机抽一个边缘点投票。
2. **一旦某（ρ,θ）累加值超过阈值**，立即沿该方向在图像中"行走"寻找线段端点，输出线段。
3. **把已经属于这条线段的边缘点从池子里移除**，不再参与后续投票。
4. 直到边缘点池空（或满足停止条件）。

效果：
- 速度比标准 HT **快 5~10 倍**。
- **直接输出线段两个端点**，省掉了"直线→线段"的二次搜索。
- 直线密度高的图像收益更大。

👉 **这就是 OpenCV 的 `cv2.HoughLinesP`（P = Probabilistic）**，工业 90% 场景用它。

### 补充：Kimme, Ballard, Sklansky 1975（圆霍夫变换）

- **标题**：Finding Circles by an Array of Accumulators
- **年份**：1975（CACM）
- **思路**：圆方程 $(x-a)^2 + (y-b)^2 = r^2$，需要三维累加器 $(a, b, r)$，但可以用**边缘点的梯度方向**限定圆心方向，把搜索从 3D 降到 2D。
- OpenCV `HoughCircles` 实现的是改进版（"2-1 Hough Transform"，21HT，Yuen et al. 1990）：先用梯度方向在 2D 累加器里找圆心，再在半径维投票。

### 补充：Ballard 1981（广义霍夫变换 GHT）

- **标题**：Generalizing the Hough Transform to Detect Arbitrary Shapes
- **年份**：1981（Pattern Recognition）
- **思路**：用一张 **R-table**（查表）把"边缘点在边缘法线方向上距离参考点多远"存起来，任意形状都可以投票。
- R-table 相当于"形状模板"，本质上把模板匹配升级成了投票——后续的可变形部件模型、霍夫森林、HoughNet 都继承了这一思想。

## 为什么要读这三篇

| 版本 | 解决什么问题 | 现在哪里用 |
|---|---|---|
| Hough 1962 | 从气泡室照片里找直线 | 思想源头，已淘汰 |
| Duda-Hart 1972 | 垂直直线 + 参数无界 | OpenCV `HoughLines`（标准 HT）|
| Matas 1998 PPHT | 标准 HT 太慢 | OpenCV `HoughLinesP`（**工业默认**）|
| Kimme 1975 | 检测圆 | OpenCV `HoughCircles` |
| Ballard 1981 GHT | 任意形状 | 少用，被深度学习取代 |

## 三个反直觉事实

1. **Hough 本人的原始方法其实不好用**，今天所有人用的都是 Duda-Hart 1972 版，"霍夫变换"这个名字是纪念发明人，但技术核心是后来者改良的。
2. **HoughLinesP 的"P"不是"Parameters"**，是 **"Probabilistic"**（概率的），因为它随机采样点而不是遍历所有点——很多人用了十年都不知道。
3. **HoughCircles 内置了 Canny**：你传原图就行，不用先调用 Canny；但它也有 `param1`（Canny 高阈值）、`param2`（累加器阈值）两个参数，你其实是在间接调 Canny。

## 伪代码（Duda-Hart 标准 HT）

```text
输入：二值边缘图 E（0/1），Δρ，Δθ，阈值 T
输出：检测到的直线 {(ρ_i, θ_i)}

1. 初始化累加器 A[ρ_bins, θ_bins] = 0
2. θ ∈ [0, π)，步长 Δθ（通常 1° = π/180）
3. ρ ∈ [-ρ_max, ρ_max]，步长 Δρ（通常 1 像素）
4. For each edge pixel (x, y) in E:
     For each θ_k in θ_bins:
        ρ_k = x * cos(θ_k) + y * sin(θ_k)
        ρ_idx = round((ρ_k + ρ_max) / Δρ)
        A[ρ_idx, k] += 1
5. For each cell in A where A[i,j] > T 且是局部极大值:
     输出 (ρ_i, θ_j) 作为一条直线
```

## 后世影响

- **车道线检测**：Tesla Autopilot 早期、Mobileye、几乎所有 ADAS 原型都用 HoughLinesP + ROI 裁剪。
- **工业检测**：Halcon、VisionPro、OpenMV 都内置霍夫线/圆算子，PCB 走线、瓶盖、O 型圈、轴承检测标准工具。
- **文档处理**：文档倾斜校正（doc-scanner、CamScanner 的倾斜检测）。
- **深度学习时代**：
  - **LSD**（Line Segment Detector, 2010）是 Hough 的主要竞争者，但参数少速度快；
  - **HoughNet**（2020）把投票思想嵌入 CNN 做目标检测；
  - 最近的 **LineTR / SOLD2 / HAWP** 等深度学习直线检测器仍在跟 Hough 做对比。

**60 年过去了，Hough 变换仍是"已知几何基元检测"的最快、最稳、最便宜的方法**——在边缘 AI、嵌入式、工业质检里，它永远不会被完全取代。

下一章：[💡 核心概念](/algorithms/hough/concepts)
