# 经典算法版本档案

> 对应 agent-yolo 的 `/versions/` 目录。每一个算法都是"版本"——它解决上一代的什么痛点、又被谁取代。
> 每个算法都有独立 7 页档案（index/paper/concepts/architecture/source/painpoints/tricks），结构与 YOLO 版本档案一致。

::: tip 如何读一个算法档案
1. **index**：白话比喻 + 一句话定位
2. **paper**：原始论文精读（关键段落翻译 + 核心贡献）
3. **concepts**：核心概念（公式只放关键 1–2 个）
4. **architecture**：算法流程图（Mermaid）+ 步骤拆解
5. **source**：OpenCV 调用 + Numpy 手写最小实现
6. **painpoints**：这个算法的坑（参数敏感/失效场景）
7. **tricks**：调参经验（工业界传下来的口诀）
:::

## 六大分支的版本索引

### ① 图像处理（基础积木）

| 版本 | 年代 | 一句话 | 档案 |
|---|---|---|---|
| 双边滤波 | 1998 | 空间×值域高斯，保边去噪 | [→ bilateral（完整档案）](/algorithms/bilateral/) |
| CLAHE 限制对比度自适应直方图均衡 | 1994 | 分块直方图均衡 + 对比度裁剪 | [→ clahe（完整档案）](/algorithms/clahe/) |
| 连通域分析（Two-Pass） | 1966 | 两遍扫描标记连通块 | [→ connected-components（完整档案）](/algorithms/connected-components/) |
| 距离变换 | 1966 | 到最近背景的欧氏距离场 | [→ distance-transform（完整档案）](/algorithms/distance-transform/) |
| Gabor 纹理滤波 | 1985 | 方向/频率选择性纹理滤波 | [→ gabor（完整档案）](/algorithms/gabor/) |
| 高斯滤波 | 1990 | 可分离高斯核线性平滑，去噪基石 | [→ gaussian-blur（完整档案）](/algorithms/gaussian-blur/) |
| Haar 小波变换 | 1989 | 多分辨率分解，压缩与特征 | [→ haar-wavelet（完整档案）](/algorithms/haar-wavelet/) |
| KNN 背景建模 | 2006 | 非参数最近样本背景估计 | [→ knn-background（完整档案）](/algorithms/knn-background/) |
| LBP 局部二值模式 | 1996 | 局部二值模式纹理描述 | [→ lbp（完整档案）](/algorithms/lbp/) |
| 中值滤波 | 1979 | 排序取中值，去椒盐不糊边 | [→ median-filter（完整档案）](/algorithms/median-filter/) |
| 形态学操作 | 1964 | 膨胀/腐蚀/开闭，形状滤波基础 | [→ morphology（完整档案）](/algorithms/morphology/) |
| Otsu 大津阈值法 | 1979 | 类间方差最大自动阈值 | [→ otsu（完整档案）](/algorithms/otsu/) |
| Sobel 边缘算子 | 1968 | 3×3 卷积算梯度，边缘鼻祖 | [→ sobel（完整档案）](/algorithms/sobel/) |
| ViBe 背景建模 | 2011 | 样本一致性随机传播背景建模 | [→ vibe（完整档案）](/algorithms/vibe/) |

### ② 特征检测（找关键点）

| 版本 | 年代 | 一句话 | 档案 |
|---|---|---|---|
| AKAZE 加速 KAZE 特征 | 2013 | 非线性扩散尺度空间 + M-LDB | [→ akaze（完整档案）](/algorithms/akaze/) |
| BRIEF 二进制描述子 | 2010 | 256 bit 二进制描述子 | [→ brief（完整档案）](/algorithms/brief/) |
| BRISK 二进制鲁棒不变可伸缩关键点 | 2011 | AGAST+同心采样，二进制快特征 | [→ brisk（完整档案）](/algorithms/brisk/) |
| Canny 边缘检测 | 1986 | 三阶段管线，单像素细边 | [→ canny（完整档案）](/algorithms/canny/) |
| 轮廓拟合与多边形逼近 | 1973 | 道格拉斯-普克折线简化 | [→ contour-fitting（完整档案）](/algorithms/contour-fitting/) |
| FAST 角点检测 | 2006 | 决策树判定，比 Harris 快 10 倍 | [→ fast（完整档案）](/algorithms/fast/) |
| FREAK 仿生二进制描述子 | 2012 | 仿视网膜级联二进制描述子 | [→ freak（完整档案）](/algorithms/freak/) |
| Harris 角点检测 | 1988 | 自相关矩阵角点 | [→ harris（完整档案）](/algorithms/harris/) |
| 霍夫圆变换 | 1972 | 圆心投票检测圆 | [→ hough-circles（完整档案）](/algorithms/hough-circles/) |
| MSER 最大稳定极值区域 | 2002 | 阈值稳定极值区域 | [→ mser（完整档案）](/algorithms/mser/) |
| ORB 实时特征点 | 2011 | oFAST+rBRIEF 免费实时 | [→ orb（完整档案）](/algorithms/orb/) |
| Shi-Tomasi 角点 | 1994 | min(λ1,λ2)，光流友好角点 | [→ shi-tomasi（完整档案）](/algorithms/shi-tomasi/) |
| SURF 加速稳健特征 | 2006 | Hessian 近似+积分图加速 | [→ surf（完整档案）](/algorithms/surf/) |

### ③ 特征匹配（建立对应）

| 版本 | 年代 | 一句话 | 档案 |
|---|---|---|---|
| FLANN 快速最近邻搜索 | 2009 | 自动配置的近似最近邻搜索 | [→ flann（完整档案）](/algorithms/flann/) |
| Lucas-Kanade 光流 | 1981 | 稀疏光流跟踪 | [→ lucas-kanade（完整档案）](/algorithms/lucas-kanade/) |
| RANSAC 随机采样一致 | 1981 | 随机采样一致剔除外点 | [→ ransac（完整档案）](/algorithms/ransac/) |
| SIFT 尺度不变特征变换 | 1999 | DoG 尺度+128 维描述子 | [→ sift（完整档案）](/algorithms/sift/) |

### ④ 图像分割

| 版本 | 年代 | 一句话 | 档案 |
|---|---|---|---|
| 高效图分割 Felzenszwalb | 2004 | 最小生成树贪心超像素 | [→ felzenszwalb-segmentation（完整档案）](/algorithms/felzenszwalb-segmentation/) |
| GrabCut 抠图 | 2004 | GMM+GraphCut 迭代抠图 | [→ grabcut（完整档案）](/algorithms/grabcut/) |
| 霍夫变换 | 1962 | 参数空间投票找直线/圆 | [→ hough（完整档案）](/algorithms/hough/) |
| K-Means 颜色聚类 | 1967 | 颜色空间聚类 | [→ kmeans（完整档案）](/algorithms/kmeans/) |
| MeanShift 均值漂移 | 2002 | 密度峰值非参数聚类 | [→ meanshift（完整档案）](/algorithms/meanshift/) |
| 区域生长分割 | 1994 | 种子点相似性扩张分割 | [→ region-growing（完整档案）](/algorithms/region-growing/) |
| SLIC 超像素 | 2010 | LabXY 5 维局部 K-Means | [→ slic（完整档案）](/algorithms/slic/) |
| 分水岭分割 | 1991 | 梯度地形浸没分割 | [→ watershed（完整档案）](/algorithms/watershed/) |

### ⑤ 目标检测（传统派）

| 版本 | 年代 | 一句话 | 档案 |
|---|---|---|---|
| 词袋模型 BoVW | 2004 | 视觉词袋+SVM 检索 | [→ bovw（完整档案）](/algorithms/bovw/) |
| CamShift 连续自适应 MeanShift | 1998 | 自适应 MeanShift 跟踪 | [→ camshift（完整档案）](/algorithms/camshift/) |
| CSRT 通道与空间可靠性跟踪 | 2017 | 通道+空间可靠性跟踪 | [→ csrt（完整档案）](/algorithms/csrt/) |
| 可变形部件模型 DPM | 2008 | 可变形部件传统检测巅峰 | [→ dpm（完整档案）](/algorithms/dpm/) |
| HOG + SVM 行人检测 | 2005 | 行人检测标配 | [→ hog-svm（完整档案）](/algorithms/hog-svm/) |
| KCF 核相关滤波跟踪 | 2015 | 循环矩阵核相关滤波跟踪 | [→ kcf（完整档案）](/algorithms/kcf/) |
| MOSSE 相关滤波跟踪 | 2010 | 频域相关滤波，600+ FPS | [→ mosse（完整档案）](/algorithms/mosse/) |
| Viola-Jones 人脸检测 | 2001 | Haar+AdaBoost 级联人脸 | [→ viola-jones（完整档案）](/algorithms/viola-jones/) |

### ⑥ 几何视觉

| 版本 | 年代 | 一句话 | 档案 |
|---|---|---|---|
| 光束法平差 BA | 1958 | 全局重投影误差最小化 | [→ bundle-adjustment（完整档案）](/algorithms/bundle-adjustment/) |
| 对极几何与基础矩阵 | 1981 | 基础矩阵+三角化 | [→ epipolar-geometry（完整档案）](/algorithms/epipolar-geometry/) |
| 本质矩阵与八点法 | 1981 | 两视图相对位姿求解 | [→ essential-matrix（完整档案）](/algorithms/essential-matrix/) |
| Farnebäck 稠密光流 | 2003 | 多项式稠密光流 | [→ farneback（完整档案）](/algorithms/farneback/) |
| 单应矩阵估计 | 1981 | 4 点 RANSAC 估算平面变换 | [→ homography（完整档案）](/algorithms/homography/) |
| Horn-Schunck 稠密光流 | 1981 | 全局平滑稠密光流 | [→ horn-schunck（完整档案）](/algorithms/horn-schunck/) |
| ICP 迭代最近点 | 1992 | 迭代最近点点云配准 | [→ icp（完整档案）](/algorithms/icp/) |
| MOG2 背景减除 | 2004 | 自适应高斯混合背景模型 | [→ mog2（完整档案）](/algorithms/mog2/) |
| PnP 位姿估计 | 2009 | O(n) 位姿求解 | [→ pnpsolver（完整档案）](/algorithms/pnpsolver/) |
| SGM 半全局立体匹配 | 2005 | 半全局立体匹配 | [→ sgbm（完整档案）](/algorithms/sgbm/) |
| 三角化重建 | 1997 | 两视线求交还原三维点 | [→ triangulation（完整档案）](/algorithms/triangulation/) |
| 张氏相机标定法 | 2000 | 棋盘格标定相机 | [→ zhang-calibration（完整档案）](/algorithms/zhang-calibration/) |
---

## 全算法对比大表

| 算法 | 年代 | 任务 | 特征类型 | 计算复杂度 | 尺度不变 | 旋转不变 | 抗光照 | 开源免费 | 典型场景 |
|---|---|---|---|---|---|---|---|---|---|
| 双边滤波 | 1998 | 保边滤波 | 空间×值域高斯 | O(r²·N) | ❌ | ❌ | ✅ | ✅ | 美颜、HDR、卡通化 |
| CLAHE 限制对比度自适应直方图均衡 | 1994 | 增强 | 局部直方图 | O(N) | ❌ | ❌ | ✅ | ✅ | 医学影像、低对比增强 |
| 连通域分析（Two-Pass） | 1966 | 连通分析 | 并查集/等价表 | O(N) | ❌ | ❌ | ✅ | ✅ | 目标计数、区域标记 |
| 距离变换 | 1966 | 距离场 | 两遍扫描 | O(N) | ❌ | ❌ | ✅ | ✅ | 骨架、粘连分离 |
| Gabor 纹理滤波 | 1985 | 纹理 | Gabor 核 | O(N·k) | ❌ | ⚠️方向组 | ✅ | ✅ | 纹理分类、指静脉 |
| 高斯滤波 | 1990 | 平滑 | 线性卷积 | O(N·k) 可分离 | ❌ | ❌ | ✅ | ✅ | 预处理、尺度空间 |
| Haar 小波变换 | 1989 | 变换 | 低通/高通滤波组 | O(N) | ❌ | ❌ | ✅ | ✅ | 压缩、Haar 特征 |
| KNN 背景建模 | 2006 | 运动前景 | KNN 密度估计 | O(N·K) | — | — | ⚠️ | ✅ | 多模态背景监控 |
| LBP 局部二值模式 | 1996 | 纹理描述 | 局部二值模式直方图 | O(N) | ❌ | ❌ | ✅(单调不变) | ✅ | 人脸、纹理、缺陷 |
| 中值滤波 | 1979 | 去噪 | 秩排序非线性 | O(N·k²) | ❌ | ❌ | ✅ | ✅ | 脉冲/椒盐噪声 |
| 形态学操作 | 1964 | 形状滤波 | 结构元素 | O(N) | ❌ | ❌ | ✅ | ✅ | 去噪、连通、缺陷检测 |
| Otsu 大津阈值法 | 1979 | 二值化 | 直方图 | O(N) | ❌ | ❌ | ⚠️ | ✅ | 文档/缺陷分割 |
| Sobel 边缘算子 | 1968 | 边缘 | 梯度 | O(N) | ❌ | ❌ | ❌ | ✅ | 边缘粗提取 |
| ViBe 背景建模 | 2011 | 运动前景 | 样本一致性 | O(N·K) | — | — | ⚠️ | ✅ | 嵌入式运动检测 |
| AKAZE 加速 KAZE 特征 | 2013 | 特征点 | 非线性扩散+M-LDB | O(N) | ✅ | ✅ | ✅ | ✅ | 手机端匹配 |
| BRIEF 二进制描述子 | 2010 | 描述子 | 256 bit 点对比较 | O(N·D) | ❌ | ❌ | ⚠️ | ✅ | 快速匹配 |
| BRISK 二进制鲁棒不变可伸缩关键点 | 2011 | 特征点 | AGAST+同心采样 | O(N) | ✅ | ✅ | ⚠️ | ✅ | 移动端 SLAM |
| Canny 边缘检测 | 1986 | 边缘 | 梯度+NMS | O(N) | ❌ | ❌ | ⚠️ | ✅ | 高质量边缘 |
| 轮廓拟合与多边形逼近 | 1973 | 轮廓 | 递归分治 | O(N log N) | ❌ | ❌ | ✅ | ✅ | 形状分析、多边形拟合 |
| FAST 角点检测 | 2006 | 角点 | 圆周 16 像素决策树 | O(N) | ❌ | ❌ | ⚠️ | ✅ | 实时关键点、SLAM 前端 |
| FREAK 仿生二进制描述子 | 2012 | 描述子 | 同心采样级联比较 | O(N·D) | ❌ | ⚠️ | ⚠️ | ✅ | 嵌入式端到端匹配 |
| Harris 角点检测 | 1988 | 角点 | 自相关矩阵 | O(N) | ❌ | ✅ | ⚠️ | ✅ | 追踪、拼接 |
| 霍夫圆变换 | 1972 | 圆检测 | 参数投票 | O(N³) | ❌ | ❌ | ⚠️ | ✅ | 硬币/虹膜/工件圆心 |
| MSER 最大稳定极值区域 | 2002 | 区域/斑点 | 阈值稳定极值区域 | O(N log N) | ✅ | ✅ | ⚠️ | ✅ | 宽基线匹配、文本检测 |
| ORB 实时特征点 | 2011 | 特征点 | oFAST+rBRIEF | O(N) | ⚠️多尺度 | ✅ | ✅ | ✅ | SLAM、AR |
| Shi-Tomasi 角点 | 1994 | 角点 | min(λ1,λ2) | O(N) | ❌ | ✅ | ⚠️ | ✅ | KLT 光流跟踪 |
| SURF 加速稳健特征 | 2006 | 特征点 | Hessian+64维 | O(N) | ✅ | ✅ | ✅ | ✅ | 实时匹配 |
| FLANN 快速最近邻搜索 | 2009 | 匹配加速 | kd-tree / 层次聚类树 | O(N log N) | — | — | — | ✅ | 大规模特征匹配 |
| Lucas-Kanade 光流 | 1981 | 光流 | 灰度守恒 | O(N·iter) | ❌ | ❌ | ❌ | ✅ | KLT 追踪 |
| RANSAC 随机采样一致 | 1981 | 几何拟合 | — | 随机采样 | — | — | — | ✅ | 剔除外点 |
| SIFT 尺度不变特征变换 | 1999 | 特征点 | DoG+128维 | O(N·M) | ✅ | ✅ | ✅ | ✅ | 图像拼接、识别 |
| 高效图分割 Felzenszwalb | 2004 | 超像素 | MST 贪心合并 | O(N log N) | ❌ | ❌ | ⚠️ | ✅ | 候选区域生成 |
| GrabCut 抠图 | 2004 | 抠图 | GMM+GraphCut | O(N³) 最坏 | ❌ | ❌ | ⚠️ | ✅ | 人像抠图 |
| 霍夫变换 | 1962 | 形状检测 | 投票 | O(N·θ) | ❌ | ❌ | ⚠️ | ✅ | 直线检测 |
| K-Means 颜色聚类 | 1967 | 聚类分割 | 颜色空间 Lloyd | O(N·K·iter) | ❌ | ❌ | ❌ | ✅ | 颜色量化、超像素基础 |
| MeanShift 均值漂移 | 2002 | 聚类/跟踪 | 核密度梯度上升 | O(N²) | ❌ | ❌ | ❌ | ✅ | 视频跟踪、分割 |
| 区域生长分割 | 1994 | 分割 | 区域增长 | O(N) | ❌ | ❌ | ⚠️ | ✅ | 医学/缺陷区域提取 |
| SLIC 超像素 | 2010 | 超像素 | LabXY 局部 K-Means | O(N) | ❌ | ❌ | ⚠️ | ✅ | 超像素前处理 |
| 分水岭分割 | 1991 | 分割 | 梯度地形浸没 | O(N log N) | ❌ | ❌ | ❌ | ✅ | 细胞/颗粒分割 |
| 词袋模型 BoVW | 2004 | 分类/检索 | 视觉词袋直方图 | O(N·K) | ⚠️SPM | ❌ | ⚠️TF-IDF | ✅ | 图像检索、分类 |
| CamShift 连续自适应 MeanShift | 1998 | 跟踪 | 肤色反投影+MeanShift | O(N·iter) | ❌ | ⚠️ | ❌ | ✅ | 人脸/目标跟踪 |
| CSRT 通道与空间可靠性跟踪 | 2017 | 单目标跟踪 | 多通道相关滤波 | O(N log N) | ❌ | ⚠️ | ⚠️ | ✅ | 高精度短时跟踪 |
| 可变形部件模型 DPM | 2008 | 通用检测 | HOG+部件 | O(N·window·part) | ⚠️金字塔 | ⚠️ | ⚠️ | ✅ | PASCAL 时代巅峰 |
| HOG + SVM 行人检测 | 2005 | 行人检测 | 梯度直方图 | O(N·window) | ❌ | ⚠️ | ⚠️ | ✅ | 行人、刚性物体 |
| KCF 核相关滤波跟踪 | 2015 | 单目标跟踪 | 核相关滤波+HOG | O(N log N) | ❌(需DSST) | ⚠️ | ⚠️ | ✅ | 短时跟踪、UAV |
| MOSSE 相关滤波跟踪 | 2010 | 单目标跟踪 | 相关滤波频域解 | O(N log N) | ❌ | ⚠️ | ❌ | ✅ | 高速实时跟踪 |
| Viola-Jones 人脸检测 | 2001 | 人脸检测 | Haar+积分图 | 级联加速 | ❌ | 正面 | ❌ | ✅ | 人脸、正脸 |
| 光束法平差 BA | 1958 | 优化 | 稀疏 LM | O(n³) 稀疏 | — | — | — | ✅ | SfM/SLAM 后端 |
| 对极几何与基础矩阵 | 1981 | 双视图几何 | — | O(N) | — | — | — | ✅ | 三维重建、SLAM |
| 本质矩阵与八点法 | 1981 | 两视图几何 | 八点法+分解 | O(N) | — | — | — | ✅ | SfM 初始化 |
| Farnebäck 稠密光流 | 2003 | 稠密光流 | 二次多项式展开 | O(N) | ❌ | ❌ | ⚠️ | ✅ | 视频稳像、动作识别 |
| 单应矩阵估计 | 1981 | 几何变换 | DLT/RANSAC | O(N) | — | — | — | ✅ | 图像拼接、AR 平面 |
| Horn-Schunck 稠密光流 | 1981 | 稠密光流 | 全局变分 | O(N·iter) | ❌ | ❌ | ❌ | ✅ | 平滑稠密运动场 |
| ICP 迭代最近点 | 1992 | 点云配准 | 最近点+SVD | O(N log N) | — | — | — | ✅ | 三维重建、激光定位 |
| MOG2 背景减除 | 2004 | 运动前景 | 自适应高斯混合 | O(N·K) | — | — | ⚠️ | ✅ | 监控、人流统计 |
| PnP 位姿估计 | 2009 | 位姿估计 | 虚拟控制点 | O(n) | — | — | — | ✅ | AR、无人机位姿 |
| SGM 半全局立体匹配 | 2005 | 立体深度 | 半全局多方向 DP | O(N·D) | ❌ | ❌ | ⚠️ | ✅ | 双目深度 |
| 三角化重建 | 1997 | 三维重建 | DLT/最优三角化 | O(N) | — | — | — | ✅ | SfM、双目 3D |
| 张氏相机标定法 | 2000 | 相机标定 | 棋盘角点 | O(N·img) | — | — | — | ✅ | 所有三维视觉前置 |


[系列家族](/global/family) · [小白入门](/for-beginners) · [技术分支总览](/branches/) · [算法档案总览](/algorithms/)
