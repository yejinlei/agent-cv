#!/usr/bin/env python3
"""批量生成剩余所有核心传统CV算法的 7 页档案（7页齐全，每篇约1000行）。"""
import os, sys, textwrap
from pathlib import Path

ROOT = Path(__file__).parent
ALGO_DIR = ROOT / "docs/algorithms"

# ============ 剩余待补的算法清单 ============
# 每个算法一个 dict，所有文本都是生活化、通俗易懂风格
ALGOS = [
    # ========== 图像预处理 ==========
    {
        "slug": "gaussian-blur",
        "name": "高斯滤波", "enName": "Gaussian Blur", "year": 1809,
        "author": "Carl Friedrich Gauss（高斯，数学公式）",
        "paper": "高斯模糊源于高斯函数，非单篇论文；图像处理中广泛用作平滑核",
        "paperUrl": "https://homepages.inf.ed.ac.uk/rbf/HIPR2/gsmooth.htm",
        "chapter": "第3章 · 图像预处理", "branch": "图像处理",
        "tagline": "给图像戴一副老花镜——平滑去噪的瑞士军刀",
        "analogy": "想象你隔着一层磨砂玻璃看照片，近处的细纹看不清了，但大轮廓还在——这就是高斯模糊。离你越近的像素权重越大，越远的权重越小，像一个钟形的钟罩把附近颜色「加权平均」掉。",
        "scene": "拍照手抖的模糊感、人脸磨皮美颜、Canny 边缘检测前的去噪预处理、SIFT/SURF 尺度空间的构建",
        "pros": "数学优美、各向同性、可分离卷积（速度快）、无数算法的前置步骤",
        "cons": "会把边缘一起糊掉（不能保边）、不能去掉椒盐噪声",
        "params": "ksize（核大小，奇数，常用 3/5/7）；sigmaX（σ，越大越糊）",
        "branch_label": "image-processing",
        "branch_id": "branch-image-processing",
    },
    {
        "slug": "median-filter",
        "name": "中值滤波", "enName": "Median Filter", "year": 1978,
        "author": "John Tukey",
        "paper": "Nonlinear (nonsuperposable) methods for smoothing data",
        "paperUrl": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1163410",
        "chapter": "第3章 · 图像预处理", "branch": "图像处理",
        "tagline": "邻居投票取中位数——椒盐噪声的克星",
        "analogy": "你站在广场上听大家喊价格，大家都报 50 块，有两个人恶作剧喊 0 和 1000。平均是 (50+50+0+1000)/4 = 275，严重失真；但取中位数还是 50，完美干掉捣蛋鬼。",
        "scene": "椒盐噪声（黑点白点）去除、扫描文档去噪、老照片修复、二值图像去白点",
        "pros": "彻底消灭椒盐噪声、不模糊边缘、实现简单",
        "cons": "对高斯噪声效果差、核大了会抹掉细线条、速度随核大小平方增长",
        "params": "ksize（核大小，奇数，常用 3/5）",
        "branch_label": "image-processing",
        "branch_id": "branch-image-processing",
    },
    {
        "slug": "clahe",
        "name": "CLAHE 自适应直方图均衡", "enName": "Contrast Limited Adaptive Histogram Equalization",
        "year": 1987, "author": "Stephen Pizer, R. Austin, et al.",
        "paper": "Adaptive Histogram Equalization and Its Variations",
        "paperUrl": "https://www.cs.unc.edu/Research/Image/MIDAG/pubs/papers/87-CV-GIP-AHE-variations.pdf",
        "chapter": "第3章 · 图像预处理", "branch": "图像处理",
        "tagline": "分块提亮+防过曝——阴天拍照救星",
        "analogy": "给一张阴天拍的照片调光，你不是整图拉亮度，而是把图像切成 8×8 的小格子，每个格子单独拉对比度；但怕太亮变噪点，就给每个格子的直方图剪一刀（clipLimit），过亮的部分摊给其他亮度。",
        "scene": "医疗影像增强、X光/CT 细节、暗光拍照提亮、人脸识别前的光照归一化",
        "pros": "局部自适应、不过曝、阴影区能看见细节",
        "cons": "有块效应边界、参数需要调、会放大噪声",
        "params": "clipLimit（对比度阈值，2-4）；tileGridSize（块大小，常用 8×8）",
        "branch_label": "image-processing",
        "branch_id": "branch-image-processing",
    },
    {
        "slug": "bilateral-thick",
        "name": "双边滤波（加厚深度版）", "enName": "Bilateral Filter", "year": 1998,
        "author": "Carlo Tomasi, Roberto Manduchi",
        "paper": "Bilateral Filtering for Gray and Color Images",
        "paperUrl": "https://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/MANDUCHI1/Bilateral_Filtering.html",
        "chapter": "第3章 · 图像预处理", "branch": "图像处理",
        "tagline": "离得近、长得像才算邻居——既磨皮又保留轮廓",
        "analogy": "磨皮时，眼睛眉毛的线条不糊、雀斑给磨掉。算法问每个像素：「你身边离我近的、颜色也像我的像素有哪些？」同时用空间距离和颜色距离两个高斯权重相乘，离得远不算，颜色差得多也不算——于是边缘处两边颜色差大，权重为 0，不被糊掉。",
        "scene": "人像美颜磨皮、HDR 色调映射、卡通化（bilateral + 边缘增强）、去噪保边",
        "pros": "保边去噪、磨皮效果自然、参数直观",
        "cons": "O(r²) 复杂度比高斯慢很多、大核会卡",
        "params": "d（邻域直径）；sigmaColor（颜色高斯σ，越大越平滑）；sigmaSpace（空间σ，越大越糊）",
        "branch_label": "image-processing",
        "branch_id": "branch-image-processing",
        "skip_if_exist": True,
    },
    # ========== 边缘与特征补漏 ==========
    {
        "slug": "hough-circles",
        "name": "霍夫圆变换", "enName": "Hough Circle Transform", "year": 1975,
        "author": "Richard Duda, Peter Hart",
        "paper": "Use of the Hough Transformation to Detect Lines and Curves in Pictures",
        "paperUrl": "https://www.cse.unsw.edu.au/~cs4411/publications/papers/HoughTransform.pdf",
        "chapter": "第4章 · 基元检测", "branch": "特征检测",
        "tagline": "每个边缘点投票找圆心——硬币检测神器",
        "analogy": "像在一张黑纸上撒了很多硬币边缘的点。你让每个点都往自己可能是圆心的方向（沿梯度反方向）画一条线，所有线交叉最多的那个点就是真圆心。找到圆心再量半径。",
        "scene": "硬币/药片/圆盖计数、瞳孔检测、工业轴承检测、表盘仪表识别",
        "pros": "对部分缺失的圆依然鲁棒、简单直观",
        "cons": "三维参数空间太慢（OpenCV 用了霍夫梯度近似）、对同心圆和噪声敏感",
        "params": "dp（累加器分辨率反比，1=原分辨率）；minDist（两圆心最小距离）；param1（Canny 高阈值）；param2（累加器阈值，越大越严格）",
        "branch_label": "feature-detection",
        "branch_id": "branch-feature-detection",
    },
    {
        "slug": "connected-components",
        "name": "连通域分析", "enName": "Connected Component Analysis (CCA)", "year": 1968,
        "author": "Rosenfeld, Pfaltz",
        "paper": "Sequential Operations in Digital Picture Processing",
        "paperUrl": "https://dl.acm.org/doi/10.1145/321474.321478",
        "chapter": "第4章 · 基元检测", "branch": "图像分割",
        "tagline": "二值图里抱团的白色像素按家庭分组——OCR第一步",
        "analogy": "想象一群人站在广场上，你把相邻站着（8 邻域或 4 邻域）的人分到同一组，每个组就是一个「连通域」。每个组你都能量它的面积、周长、形心、外接矩形。",
        "scene": "OCR 字符切分、缺陷检测、细胞计数、车牌字符提取、二维码定位",
        "pros": "超快（线性两遍扫描）、每个域都有面积/形心/外接框属性",
        "cons": "必须先二值化、粘连字符分不开（需要分水岭）",
        "params": "connectivity（4 或 8）；ltype（输出标签类型）",
        "branch_label": "segmentation",
        "branch_id": "branch-segmentation",
    },
    {
        "slug": "distance-transform",
        "name": "距离变换", "enName": "Distance Transform", "year": 1966,
        "author": "Rosenfeld, Pfaltz",
        "paper": "Sequential Operations in Digital Picture Processing",
        "paperUrl": "https://dl.acm.org/doi/10.1145/321474.321478",
        "chapter": "第5章 · 目标表达与描述", "branch": "图像分割",
        "tagline": "到最近边界的距离图——分水岭和骨架提取的地基",
        "analogy": "一片草坪上撒了一些石头（前景像素），你给每根草都标一个数字：它离最近的石头有多远。越亮的地方代表越在物体内部，最亮的点就是物体的骨架/中心线。",
        "scene": "分水岭找种子（局部最大值）、骨架提取、形态学细化、机器人路径规划（A*代价地图）",
        "pros": "两遍扫描线性完成、结果直观",
        "cons": "只对二值图有效、对噪声敏感需要预处理",
        "params": "distanceType（L1/L2/C）；maskSize（3 或 5）",
        "branch_label": "segmentation",
        "branch_id": "branch-segmentation",
    },
    {
        "slug": "contour-fitting",
        "name": "轮廓拟合", "enName": "Contour Detection & Shape Fitting", "year": 1980,
        "author": "OpenCV / 多个作者",
        "paper": "Suzuki-Abe 1985: Topological Structural Analysis of Digitized Binary Images by Border Following",
        "paperUrl": "https://www.sciencedirect.com/science/article/pii/0734189X85900167",
        "chapter": "第5章 · 目标表达与描述", "branch": "特征检测",
        "tagline": "找出物体的外轮廓，再套上矩形/圆/椭圆——识别形状第一步",
        "analogy": "你把一张画着苹果的纸放到灯下，沿着光的边缘用铅笔描一圈，这就是轮廓。然后你给这个轮廓套最小外接矩形、最小外接圆、拟合椭圆，它是什么形状就一目了然了。",
        "scene": "形状识别、物体测量、工业零件尺寸检测、手势识别",
        "pros": "快速得到外轮廓和几何属性、面积周长矩凸包一把抓",
        "cons": "依赖二值化质量、对遮挡敏感",
        "params": "mode（RETR_EXTERNAL 只取外轮廓等）；method（CHAIN_APPROX_SIMPLE 压缩点）",
        "branch_label": "feature-detection",
        "branch_id": "branch-feature-detection",
    },
    {
        "slug": "brisk",
        "name": "BRISK 二进制鲁棒不变可伸缩关键点", "enName": "Binary Robust Invariant Scalable Keypoints",
        "year": 2011, "author": "Stefan Leutenegger, Margarita Chli, Roland Siegwart",
        "paper": "BRISK: Binary Robust Invariant Scalable Keypoints",
        "paperUrl": "https://www.robots.ox.ac.uk/~vgg/rg/papers/BRISK.pdf",
        "chapter": "第8章 · 局部特征", "branch": "特征检测",
        "tagline": "FAST+AGAST+方向+环形采样——比 ORB 还快一点的二进制特征",
        "analogy": "ORB 是把 FAST 和 BRIEF 拉到一起的小跑车，BRISK 就是对它做了升级——关键点用 AGAST 找得更快，采样改成一圈一圈的同心圆（省内存），方向用长点对梯度估计，还能做尺度金字塔。",
        "scene": "无人机/手机等嵌入式设备上的实时拼接、SLAM、AR",
        "pros": "比 ORB/SIFT 快、有旋转尺度不变、二进制描述子匹配快",
        "cons": "描述子长度 512 比特比 ORB 长、精度和 SIFT 仍有差距",
        "params": "thresh（FAST 阈值）；octaves（金字塔层数）；patternScale",
        "branch_label": "feature-detection",
        "branch_id": "branch-feature-detection",
    },
    {
        "slug": "freak",
        "name": "FREAK 视网膜采样描述子", "enName": "Fast Retina Keypoint", "year": 2012,
        "author": "Alexandre Alahi, Raphael Ortiz, Pierre Vandergheynst",
        "paper": "FREAK: Fast Retina Keypoint",
        "paperUrl": "https://www.ivpe.ru/papers/2012_FREAK.pdf",
        "chapter": "第8章 · 局部特征", "branch": "特征匹配",
        "tagline": "模仿人眼视网膜——中心密外围疏的二进制描述子",
        "analogy": "人眼看东西时，黄斑区（中心）看得最清楚，周围视杆细胞稀疏只看大轮廓。FREAK 就是这么采样的：关键点周围布点时，中心密密麻麻，越往外越稀疏，用环形对称点对的灰度差拼出 512 位二进制串，且自带方向估计。",
        "scene": "移动端识别、AR、实时 SLAM、低功耗视觉",
        "pros": "比 SIFT/SURF 快几十倍、有旋转尺度不变、人眼仿生",
        "cons": "专利问题小、参数固定难调",
        "params": "orientationNormalized；scaleNormalized；patternScale",
        "branch_label": "feature-matching",
        "branch_id": "branch-feature-matching",
    },
    {
        "slug": "akaze",
        "name": "AKAZE 加速 KAZE 特征", "enName": "Accelerated-KAZE", "year": 2013,
        "author": "Pablo F. Alcantarilla, J. Nuevo, Adrien Bartoli",
        "paper": "Fast Explicit Diffusion for Accelerated Features in Nonlinear Scale Spaces",
        "paperUrl": "https://www.bmva.org/bmvc/2013/Papers/paper0013/paper0013.pdf",
        "chapter": "第8章 · 局部特征", "branch": "特征检测",
        "tagline": "非线性扩散建金字塔——不糊边缘的 SIFT 替代品",
        "analogy": "SIFT 的高斯金字塔像磨砂玻璃一层一层糊上去；KAZE/AKAZE 用「非线性扩散」建尺度空间，边缘处糊得慢、平坦处糊得快——所以金字塔顶层边缘还在，特征点不会被抹掉。AKAZE 把 KAZE 加了 FED（快速显式扩散）加速到 SIFT 一个量级。",
        "scene": "高精度图像匹配、对边缘敏感的拼接、形变目标识别",
        "pros": "非线性尺度空间，边缘比 SIFT 好；二进制描述子 MLDB 匹配快；开源免费无专利",
        "cons": "比 ORB 慢、实现略复杂、老 OpenCV 版本支持差",
        "params": "descriptor_type（MLDB 二进制）；threshold；nOctaves",
        "branch_label": "feature-detection",
        "branch_id": "branch-feature-detection",
    },
    # ========== 纹理与描述 ==========
    {
        "slug": "gabor-filter",
        "name": "Gabor 滤波", "enName": "Gabor Filter", "year": 1946,
        "author": "Dennis Gabor（诺贝尔奖得主）",
        "paper": "Theory of Communication（原始）；1980s 引入视觉：Daugman",
        "paperUrl": "https://www.cl.cam.ac.uk/~jgd1000/slides/Daugman-slides.pdf",
        "chapter": "第7章 · 纹理分析", "branch": "图像处理",
        "tagline": "不同方向不同频率的纹理放大镜——仿人眼 V1 区",
        "analogy": "想象你拿一排梳子朝不同方向刮过纹理布：梳齿和纹理方向平行时阻力最小，垂直时阻力最大。Gabor 核就是一组方向（0/45/90/135°）不同频率的正弦波加高斯窗的「小梳子」，每个核只响应特定方向特定频率的纹理，拼起来就识别出纹理。",
        "scene": "纹理分类、虹膜识别（Daugman 用它）、指纹识别、边缘+纹理联合分析",
        "pros": "仿生、方向+频率双选择性、有生理学依据",
        "cons": "要算多组核（慢）、参数多需要调、对光照敏感",
        "params": "ksize；sigma；theta（方向）；lambda（波长）；gamma（纵横比）",
        "branch_label": "image-processing",
        "branch_id": "branch-image-processing",
    },
    # ========== 分割补漏 ==========
    {
        "slug": "region-growing",
        "name": "区域生长分割", "enName": "Region Growing", "year": 1978,
        "author": "Ron Ohlander, Keith Price, D. Raj Reddy",
        "paper": "Picture Segmentation Using a Recursive Region Splitting Method",
        "paperUrl": "https://dl.acm.org/doi/10.1145/359763.359779",
        "chapter": "第10章 · 图像分割", "branch": "图像分割",
        "tagline": "从种子开始拉帮结派——颜色/灰度相近就入伙",
        "analogy": "就像在地图上从一个城市出发，把相邻且地形相似的地方都吞并进来，直到遇到高山大海。算法从每个种子点开始，把周围和当前区域平均灰度差小于阈值的像素一个个拉进来。",
        "scene": "医学影像（器官分割）、卫星图像区域分类、种子点交互分割",
        "pros": "直观、能得到连通区域、适合交互式分割",
        "cons": "种子位置敏感、会漏洞/过度生长、慢",
        "params": "seed；threshold（灰度差阈值）；connectivity（4/8）",
        "branch_label": "segmentation",
        "branch_id": "branch-segmentation",
    },
    {
        "slug": "felzenszwalb-segmentation",
        "name": "Felzenszwalb 图分割", "enName": "Efficient Graph-Based Image Segmentation",
        "year": 2004, "author": "Pedro F. Felzenszwalb, Daniel P. Huttenlocher",
        "paper": "Efficient Graph-Based Image Segmentation",
        "paperUrl": "https://cs.brown.edu/people/pfelzens/papers/seg-ijcv.pdf",
        "chapter": "第10章 · 图像分割", "branch": "图像分割",
        "tagline": "最小生成树切边——比超像素更早的高效分割",
        "analogy": "把每个像素当节点，相邻像素用颜色差做边权建图，然后求最小生成树；接着从权重最小的边开始合并，用一个巧妙的阈值（Dif = 两区域内部差 / log(size)）决定是不是要切断这条边。结果是全局最优、快到接近线性。",
        "scene": "SLIC 之前常用的超像素前身、目标候选生成、交互式分割基底",
        "pros": "接近线性时间 O(N log N)、保留细节大区域、无参数阈值自适应",
        "cons": "边界略毛糙、小块多需要后处理、sigma/scale/minSize 需要调",
        "params": "sigma（高斯平滑）；k（尺度，越大区域越大）；minSize（最小区块像素数）",
        "branch_label": "segmentation",
        "branch_id": "branch-segmentation",
    },
    # ========== 背景减除与跟踪补漏 ==========
    {
        "slug": "knn-background",
        "name": "KNN 背景减除器", "enName": "K-Nearest Neighbors Background Subtractor",
        "year": 2012, "author": "Zoran Zivkovic（同 MOG2 作者）",
        "paper": "Improved Adaptive Gaussian Mixture Model for Background Subtraction",
        "paperUrl": "https://www.zoranz.net/Publications/zivkovic2004ICPR.pdf",
        "chapter": "第11章 · 运动分析", "branch": "目标检测",
        "tagline": "最近 K 个历史帧投票判断前景——动态背景更稳",
        "analogy": "MOG2 给每个像素建高斯混合模型（像分了几个颜色桶），KNN 更朴素：记住每个像素最近 N 帧的颜色，新像素来了和历史 K 个邻居比，若多数是背景色就判背景，否则前景。它对树叶晃动、水面波纹这种多模态背景更鲁棒。",
        "scene": "晃动树叶的室外监控、水面反光、喷泉、风扇转动",
        "pros": "无需维护高斯模型、对多模态背景更鲁棒、OpenCV 自带",
        "cons": "内存稍大（要存历史）、光线突变时适应慢",
        "params": "history（历史帧数，默认 500）；dist2Threshold（距离平方阈值）；detectShadows",
        "branch_label": "detection",
        "branch_id": "branch-detection",
    },
    {
        "slug": "vibe",
        "name": "ViBe 背景建模", "enName": "Visual Background Extractor", "year": 2011,
        "author": "Olivier Barnich, Marc Van Droogenbroeck",
        "paper": "ViBe: A Universal Background Subtraction Algorithm for Video Sequences",
        "paperUrl": "https://orbi.uliege.be/handle/2268/129031",
        "chapter": "第11章 · 运动分析", "branch": "目标检测",
        "tagline": "每像素存 20 个历史样本随机替换——一帧就能初始化",
        "analogy": "KNN 存历史帧，ViBe 给每个像素只存最近 20 个「记忆样本」。新像素来了和这 20 个样本比，有 2 个以上靠近就算背景；更新时随机替换一个旧样本，并随机扩散到邻居，这样像信息素一样慢慢渗透，特别抗抖动。",
        "scene": "嵌入式实时监控、摄像头第一帧就要开始检测、运动快的目标",
        "pros": "一帧即可初始化、极快（C 版上百 FPS）、抗抖动、实现简单",
        "cons": "有 ghost（物体挪走后残影）、专利需注意、OpenCV 官方不带需第三方实现",
        "params": "N（样本数，默认20）；R（距离半径）；#min（最小匹配数，默认2）；phi（更新速率，默认1/16）",
        "branch_label": "detection",
        "branch_id": "branch-detection",
    },
    {
        "slug": "mosse",
        "name": "MOSSE 最小平方和误差跟踪", "enName": "Minimum Output Sum of Squared Error",
        "year": 2010, "author": "David S. Bolme, J. Ross Beveridge, et al.",
        "paper": "Visual Object Tracking using Adaptive Correlation Filters",
        "paperUrl": "https://www.cs.colostate.edu/~vision/publications/Bolme_CVPR10.pdf",
        "chapter": "第11章 · 运动分析", "branch": "目标检测",
        "tagline": "首个相关滤波跟踪器——600+ FPS 的速度怪兽",
        "analogy": "KCF 之前的开山鼻祖：给目标训练一个滤波器模板，让它对目标区域的响应是一个尖峰（中心亮周围黑）；下一帧用这个模板卷积整张搜索区，最亮的点就是新位置。MOSSE 是单通道灰度的、最朴素的相关滤波，但速度飞快 600+ FPS。",
        "scene": "CPU 端极速跟踪、多目标跟踪预检测、资源受限设备",
        "pros": "CPU 600+ FPS、第一帧就能训练、对光照/尺度小变化鲁棒",
        "cons": "单通道灰度（比 KCF 粗糙）、尺度不变性差、无 HOG",
        "params": "learning_rate（更新率）；sigma（高斯响应σ）；PSR 失败检测阈值",
        "branch_label": "detection",
        "branch_id": "branch-detection",
    },
    {
        "slug": "camshift-thick",
        "name": "CamShift 连续自适应 Meanshift（加厚版）",
        "enName": "Continuously Adaptive Mean Shift", "year": 1998,
        "author": "Gary R. Bradski（OpenCV 创始人）",
        "paper": "Computer Vision Face Tracking For Use in a Perceptual User Interface",
        "paperUrl": "https://docs.opencv.org/3.4/db/df8/tutorial_py_meanshift.html",
        "chapter": "第11章 · 运动分析", "branch": "目标检测",
        "tagline": "Meanshift + 自动变窗口大小——手脸跟踪老将",
        "analogy": "Meanshift 像爬山：你站在颜色概率图上，往密度最大（概率最高）的地方挪，挪到山顶（收敛）就是目标中心。但 Meanshift 的窗口大小固定（人走近就套不住）。CamShift 多做一步：收敛后按目标颜色分布的二阶矩（长轴短轴方向）自动调整窗口大小和旋转角，所以走近走远旋转都跟得上。",
        "scene": "人脸识别初始化后跟踪、手势跟踪、HCI 交互界面、简单肤色跟踪",
        "pros": "自动适应窗口大小旋转、实现简单、OpenCV 自带",
        "cons": "必须先给颜色直方图（如 HSV 肤色）、光照变/相似背景就飘、容易跟丢",
        "params": "term_crit（迭代次数+收敛阈值）；hist（颜色直方图）；初始框",
        "branch_label": "detection",
        "branch_id": "branch-detection",
        "skip_if_exist": True,
    },
    # ========== 特征匹配补漏 ==========
    {
        "slug": "flann",
        "name": "FLANN 快速近邻匹配库", "enName": "Fast Library for Approximate Nearest Neighbors",
        "year": 2009, "author": "Marius Muja, David G. Lowe（SIFT 作者）",
        "paper": "Fast Approximate Nearest Neighbors with Automatic Algorithm Configuration",
        "paperUrl": "https://www.cs.ubc.ca/~lowe/papers/09muja.pdf",
        "chapter": "第13章 · 图像匹配", "branch": "特征匹配",
        "tagline": "KD-Tree + K-Means 树自动选最快方案——百万特征秒配",
        "analogy": "暴力匹配像在字典里一页页翻找；FLANN 先给字典建索引（KD-Tree 按坐标切分 / K-Means 树按聚类切分），然后从根节点一路比较跳下去，O(log N) 就找到最近邻居。它还会自动在几种索引里选最快的，不用你操心。",
        "scene": "大尺寸图像匹配（SIFT/SURF 128 维向量）、图像检索、大规模 3D 重建",
        "pros": "比 BF 暴力匹配快 10-100 倍、OpenCV 集成好、自动选参数",
        "cons": "近似匹配（可能不是绝对最近）、对二进制特征（ORB/BRIEF）效率一般（用 LSH 代替）",
        "params": "algorithm（KD-TREE=1 / KMEANS=2 / LSH=6 / AUTOTUNE=255）；trees；checks",
        "branch_label": "feature-matching",
        "branch_id": "branch-feature-matching",
    },
    # ========== 三维/几何补漏 ==========
    {
        "slug": "essential-matrix",
        "name": "本质矩阵与基础矩阵", "enName": "Essential Matrix E / Fundamental Matrix F",
        "year": 1981, "author": "H. Christopher Longuet-Higgins",
        "paper": "A Computer Algorithm for Reconstructing a Scene from Two Projections",
        "paperUrl": "https://www.nature.com/articles/293133a0",
        "chapter": "第14章 · 三维视觉", "branch": "几何视觉",
        "tagline": "两幅图点对的代数关系——立体视觉/三维重建的钥匙",
        "analogy": "你左眼看一个点、右眼看同一个点，这两个像素坐标之间不是乱的，它俩满足一个数学约束 x'^T F x = 0，其中 F 就是基础矩阵（Fundamental Matrix）；如果知道相机内参 K，就能得到本质矩阵 E = K'^T F K，再从 E 分解出两相机之间的旋转 R 和平移 t。这就是 3D 重建的第一步。",
        "scene": "双视图几何、运动恢复结构(SfM)、立体视觉标定、图像拼接的几何约束",
        "pros": "纯代数方法、8 对点就够（8点法）、无需相机标定（F 即可）",
        "cons": "对噪声和外点敏感（必须配 RANSAC）、只能恢复到尺度（平移 t 只差比例）",
        "params": "method（8点法/RANSAC/LMedS）；ransacReprojThreshold；confidence",
        "branch_label": "geometry",
        "branch_id": "branch-geometry",
    },
    {
        "slug": "triangulation",
        "name": "三角测量", "enName": "Triangulation", "year": 1827,
        "author": "高斯/传统几何",
        "paper": "经典几何；计算机视觉中 Hartley & Sturm 1997 给出最优解",
        "paperUrl": "https://users.cecs.anu.edu.au/~hartley/Papers/triangulation/triangulation.pdf",
        "chapter": "第14章 · 三维视觉", "branch": "几何视觉",
        "tagline": "两条视线相交定 3D 点——从两张 2D 图算出 3D 坐标",
        "analogy": "就像海上两艘船同时用探照灯照天上的一架飞机，两条光束的交点就是飞机的位置。你已知左右相机的位置姿态（R,t,K），加上同一物点在两张图上的像素坐标，解一个超定线性方程就能求出该点的 3D 坐标。",
        "scene": "双目深度估计、SfM 三维点云构建、AR 物体测量",
        "pros": "线性解法（DLT）速度快、闭合解无迭代",
        "cons": "对极几何必须准确、基线短误差大、对噪声敏感",
        "params": "projMatr1 / projMatr2（两个 3x4 投影矩阵）；projPoints1/2（对应点）",
        "branch_label": "geometry",
        "branch_id": "branch-geometry",
    },
    {
        "slug": "bundle-adjustment",
        "name": "光束法平差", "enName": "Bundle Adjustment (BA)",
        "year": "约 1950s 摄影测量；1999 Triggs 等现代综述",
        "author": "Bill Triggs, Philip McLauchlan, Richard Hartley, Andrew Fitzgibbon",
        "paper": "Bundle Adjustment — A Modern Synthesis",
        "paperUrl": "https://www.cs.cornell.edu/~snavely/bundler/bundler.pdf",
        "chapter": "第14章 · 三维视觉", "branch": "几何视觉",
        "tagline": "SfM 的最后一步——所有相机和所有 3D 点一起优化",
        "analogy": "你先通过本质矩阵估出了相机位姿、通过三角测量算出了 3D 点，但它们都是「大概值」。BA 就像你把所有相机和点都用弹簧连起来，来回微调每个点和相机的位置，让所有像素点的重投影误差总和最小——相当于全局最优的一次大联合优化。",
        "scene": "SfM/三维重建最终优化、SLAM 后端、卫星摄影测量",
        "pros": "全局最优、精度最高、稀疏结构能用 Levenberg-Marquardt 快速解",
        "cons": "大规模（千万点）需要稀疏矩阵和舒尔补、实现复杂（常用 Ceres/g2o）",
        "params": "初始相机参数、初始 3D 点、观测对应关系、迭代次数",
        "branch_label": "geometry",
        "branch_id": "branch-geometry",
    },
    # ========== 全局/描述 ==========
    {
        "slug": "haar-wavelet",
        "name": "Haar 小波特征", "enName": "Haar-like Features", "year": 2001,
        "author": "Paul Viola, Michael Jones",
        "paper": "Rapid Object Detection using a Boosted Cascade of Simple Features",
        "paperUrl": "https://www.cs.cmu.edu/~efros/courses/LBMV07/Papers/viola-cvpr-01.pdf",
        "chapter": "第6章 · 特征提取", "branch": "目标检测",
        "tagline": "黑白矩形求差做人脸检测——Viola-Jones 的地基",
        "analogy": "想象你拿两枚邮票（一黑一白并排贴在脸上）算「白区平均灰度减黑区平均灰度」。比如眼睛比脸颊黑，所以横跨眼睛的白-黑-白矩形差值很大；鼻子两侧也有特征。Viola-Jones 就是用上万种这种小矩形当特征，配合积分图秒算，再用 AdaBoost 选最有用的几百个串成级联。",
        "scene": "早期实时人脸检测（OpenCV 老款 haarcascade_frontalface）、简单行人检测",
        "pros": "积分图 O(1) 超快、级联检测实现在 CPU 上实时",
        "cons": "对侧脸/遮挡/光照差效果差、已被 HOG+SVM/DPM 再到深度学习超越",
        "params": "无（通过 AdaBoost 选 Haar 特征）；级联层数、检测最小尺寸",
        "branch_label": "detection",
        "branch_id": "branch-detection",
    },
]


def write_algo(a):
    slug = a["slug"]
    # 处理双边/CamShift加厚版
    real_slug = slug.replace("-thick", "")
    out = ALGO_DIR / real_slug
    if a.get("skip_if_exist") and out.exists():
        print(f"⏭  跳过（已存在）: {real_slug}")
        return
    out.mkdir(parents=True, exist_ok=True)

    # ---------- index.md ----------
    idx = f'''---
layout: doc
---

<AlgorithmCard
  name="{a["name"]}"
  enName="{a["enName"]}"
  chapter="{a["chapter"]}"
  branch="{a["branch"]}"
  year="{a["year"]}"
  author="{a["author"]}"
  paper="{a["paperUrl"]}"
  level="⭐⭐⭐"
  tagline="{a["tagline"]}"
  analogy="{a["analogy"]}"
  scene="{a["scene"]}"
  pros="{a["pros"]}"
  cons="{a["cons"]}"
  params="{a["params"]}"
/>

## 1. 一句话理解
{a["analogy"]}

## 2. 它解决什么问题？
在{a["scene"]}这些场景下，{a["name"]}（{a["enName"]}）是最常被第一个想到的传统 CV 算法。
它由 {a["author"]} 于 **{a["year"]}** 年提出，是「{a["chapter"]}」章节里的核心一员。

## 3. 本算法的 7 页学习路径

| 页码 | 主题 | 你会学到什么 |
|------|------|--------------|
| [第2页 · 原始论文](paper) | 论文导读 | 作者当年的动机、3 个最重要的贡献、后人的评价 |
| [第3页 · 核心概念](concepts) | 概念拆解 | 用大白话+图示讲透关键公式、符号、直觉 |
| [第4页 · 算法架构](architecture) | 流程总览 | 输入→输出的完整步骤、Mermaid 流程图、参数表 |
| [第5页 · 源码实现](source) | 代码实战 | OpenCV 调用版 + 手写最小版，复制就能跑 |
| [第6页 · 坑点陷阱](painpoints) | 踩坑手册 | 10 个新手最常掉进去的坑、原因与修复 |
| [第7页 · 调参口诀](tricks) | 实战经验 | 工业界调参速查表、与其他算法的组合套路 |

## 4. 一句话优缺点
- ✅ **优点**：{a["pros"]}
- ❌ **缺点**：{a["cons"]}

## 5. 前置依赖（你该先会哪些？）
{render_deps(a)}

## 6. 在线体验
<OpenCvPlayground algo="{real_slug}" />

> 🎮 上面是本算法的实时交互 Demo，拖张图片或打开摄像头，拖动滑块就能看到效果！
'''
    (out / "index.md").write_text(idx, encoding="utf-8")

    # ---------- paper.md ----------
    paper_md = f'''---
outline: deep
---

# 第 2 页 · 原始论文导读

## 论文信息卡

| 字段 | 内容 |
|------|------|
| 标题 | {a["paper"]} |
| 作者 | {a["author"]} |
| 发表年份 | {a["year"]} |
| 链接 | [{a["paperUrl"][:60]}...]({a["paperUrl"]}) |

## 1. 作者当年为什么要做这件事？
{render_motivation(a)}

## 2. 论文最核心的 3 个贡献

1. **{render_contribution1(a)}**
2. **{render_contribution2(a)}**
3. **{render_contribution3(a)}**

## 3. 公式里最关键的一句话
{render_key_formula(a)}

## 4. 实验结果长啥样？
论文里最惊艳的是——{render_experiment(a)}

## 5. 后来人怎么评价它？
{render_evaluation(a)}

## 6. 读原文的正确姿势
- 初读者：只看摘要、Intro、Fig.1、结论（10 分钟就能 get）
- 动手党：重点看算法 1（伪代码）和实验部分，对照实现
- 研究者：看 Related Work 了解它在谱系里的位置
'''
    (out / "paper.md").write_text(paper_md, encoding="utf-8")

    # ---------- concepts.md ----------
    concepts_md = f'''---
outline: deep
---

# 第 3 页 · 核心概念拆解

## 1. 生活比喻
{a["analogy"]}

## 2. 关键概念清单
{render_concepts(a)}

## 3. 最关键的公式（用大白话讲）
{render_formula_explain(a)}

## 4. 为什么它能 work？
{render_why_work(a)}

## 5. 它和类似算法到底差在哪？
{render_compare_table(a)}
'''
    (out / "concepts.md").write_text(concepts_md, encoding="utf-8")

    # ---------- architecture.md ----------
    arch_md = f'''---
outline: deep
---

# 第 4 页 · 算法架构与流程图

## 1. 完整流程（Mermaid）

```mermaid
{{flowchart LR}}
    A["输入图像"] --> B[步骤1: {render_step1(a)}]
    B --> C[步骤2: {render_step2(a)}]
    C --> D[步骤3: {render_step3(a)}]
    D --> E[步骤4: {render_step4(a)}]
    E --> F["输出结果"]
```

## 2. 每一步在干什么？

### 步骤 1：{render_step1(a)}
{render_step1_detail(a)}

### 步骤 2：{render_step2(a)}
{render_step2_detail(a)}

### 步骤 3：{render_step3(a)}
{render_step3_detail(a)}

### 步骤 4：{render_step4(a)}
{render_step4_detail(a)}

## 3. 参数表（论文建议 vs OpenCV 默认 vs 实战推荐）

| 参数 | 含义 | 论文建议 | OpenCV 默认 | 实战推荐 |
|------|------|----------|-------------|----------|
{render_param_table(a)}

## 4. 时间复杂度
{render_complexity(a)}

## 5. 边界情况与失败模式
{render_failure_modes(a)}
'''
    (out / "architecture.md").write_text(arch_md, encoding="utf-8")

    # ---------- source.md ----------
    src_md = f'''---
outline: deep
---

# 第 5 页 · 源码实现

## 1. OpenCV 一行调用（工业界首选）

```python
import cv2
import numpy as np

