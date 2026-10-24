#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为第三批 14 个新算法补齐本体实例：算法 / 论文 / 概念。"""
import io, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ontology", "instances")

ALGOS = [
    dict(slug="gaussian-blur", name="高斯滤波", nameEn="Gaussian Blur",
         year=1990, branch="branch-image-processing", layer="L2",
         plainTalk="给图像蒙一层半透明的磨砂玻璃，每个像素都去问邻居『你们平均是多少』，结果画面变柔和、噪点被抹平；摄影师在镜头前贴的柔焦镜就是这个效果。",
         concepts=["concept-gaussian-blur", "concept-image-pyramid"],
         tags=["classic-cv", "filter", "linear", "denoise", "separability"],
         papers=["paper-lindeberg-1990-scale-space"],
         evolvedFrom=None, dependsOn=[], replacedBy=[], inheritedBy=["CNN 卷积核初始化为高斯核"],
         status="stable"),
    dict(slug="median-filter", name="中值滤波", nameEn="Median Filter",
         year=1979, branch="branch-image-processing", layer="L2",
         plainTalk="把每个像素和周围一圈邻居的数值排队，取站在正中间的那个来替换它；就像一群人身高各不相同，你只报中间那个人的身高，偶尔窜出来的『大高个』（椒盐噪声）自然被忽略，所以专治白点黑点。",
         concepts=["concept-median-filter"],
         tags=["classic-cv", "filter", "nonlinear", "denoise", "salt-pepper"],
         papers=["paper-huang-1979-median"],
         evolvedFrom=None, dependsOn=["op-median-blur"], replacedBy=[], inheritedBy=[],
         status="stable"),
    dict(slug="hough-circles", name="霍夫圆变换", nameEn="Hough Circle Transform",
         year=1972, branch="branch-feature-detection", layer="L2",
         plainTalk="桌上一堆散落的圆点，你要找出它们属于哪些圆。每个人拿把尺子猜一个圆心，猜中的人举表投票，票最多的圆心就是真正的圆心——这就是霍夫圆变换：让每个边缘点去给『可能的圆心』投票，票仓最高的位置即圆心。",
         concepts=["concept-hough-transform", "concept-parameter-space"],
         tags=["classic-cv", "shape", "voting", "circle"],
         papers=["paper-duda-hart-1972-hough"],
         evolvedFrom="algo-hough", dependsOn=[], replacedBy=[], inheritedBy=[],
         status="stable"),
    dict(slug="contour-fitting", name="轮廓拟合与多边形逼近", nameEn="Contour Fitting & Polygon Approximation",
         year=1973, branch="branch-feature-detection", layer="L2",
         plainTalk="沿着物体边缘走一圈会留下密密麻麻的点，就像手绘地图上无数个脚印。多边形逼近就是只保留几个拐弯处的大转角，把上千个脚印压缩成几个关键顶点，圆滑的轮廓也能用最少的笔画勾勒出来。",
         concepts=["concept-contour-approximation"],
         tags=["classic-cv", "shape", "contour", "simplification"],
         papers=["paper-douglas-peucker-1973"],
         evolvedFrom=None, dependsOn=["op-find-contours"], replacedBy=[], inheritedBy=[],
         status="stable"),
    dict(slug="freak", name="FREAK 仿生二进制描述子", nameEn="Fast Retina Keypoint",
         year=2012, branch="branch-feature-detection", layer="L2",
         plainTalk="模仿人眼视网膜的构造：越靠中心的地方看得越清楚、采样越密，往外就越来越粗。FREAK 沿着这种『由密到疏』的采样图案比较亮度，用一串 0/1 描述关键点长相，又快又省内存。",
         concepts=["concept-binary-descriptor", "concept-concentric-pattern"],
         tags=["classic-cv", "feature", "binary-descriptor", "bio-inspired"],
         papers=["paper-alahi-2012-freak"],
         evolvedFrom="algo-brisk", dependsOn=[], replacedBy=[], inheritedBy=[],
         status="stable"),
    dict(slug="felzenszwalb-segmentation", name="高效图分割 Felzenszwalb", nameEn="Efficient Graph-Based Segmentation",
         year=2004, branch="branch-segmentation", layer="L2",
         plainTalk="把像素想象成一个个小岛，岛与岛之间用桥连着，桥的宽窄代表两边颜色差多少。算法总是先在最相似的岛之间搭桥合并，一旦遇到颜色差异太大的『深沟』就停下来断开，于是画面自动被切成语义相近的一块块。",
         concepts=["concept-union-find", "concept-superpixel", "concept-graph-cut"],
         tags=["classic-cv", "segmentation", "graph", "greedy"],
         papers=["paper-felzenszwalb-2004-graph"],
         evolvedFrom=None, dependsOn=[], replacedBy=[], inheritedBy=["选择性搜索 Selective Search"],
         status="stable"),
    dict(slug="knn-background", name="KNN 背景建模", nameEn="K-Nearest Neighbors Background Subtraction",
         year=2006, branch="branch-image-processing", layer="L2",
         plainTalk="给每个像素位置长期记账：它过去出现过哪些颜色，都存一小本档案。新来一个像素，就翻档案看它是否属于『常见的老颜色』，属于就认定是背景，突然冒出的陌生颜色才判定为前景运动物体。",
         concepts=["concept-background-model"],
         tags=["classic-cv", "background-subtraction", "video", "non-parametric"],
         papers=["paper-zivkovic-2006-knn-bg"],
         evolvedFrom="algo-mog2", dependsOn=[], replacedBy=[], inheritedBy=[],
         status="stable"),
    dict(slug="vibe", name="ViBe 背景建模", nameEn="ViBe Background Subtraction",
         year=2011, branch="branch-image-processing", layer="L2",
         plainTalk="跟邻居借样本来描述背景：每个像素不只看自己，还随机从隔壁像素借几个历史颜色当模板。新像素只要和模板里任意几个相近就算背景，模板还会随机换掉旧样本——像同学之间不断交换笔记，既不占内存又能适应光线缓慢变化。",
         concepts=["concept-background-model"],
         tags=["classic-cv", "background-subtraction", "video", "sample-based"],
         papers=["paper-barnich-2011-vibe"],
         evolvedFrom="algo-mog2", dependsOn=[], replacedBy=[], inheritedBy=[],
         status="stable"),
    dict(slug="mosse", name="MOSSE 相关滤波跟踪", nameEn="Minimum Output Sum of Squared Error Tracking",
         year=2010, branch="branch-detection", layer="L3",
         plainTalk="先在目标上盖一个『印章』（滤波器），然后在下一帧整幅画面里翻找，哪里盖出的印迹最亮最像，就说明目标跑到哪里了；而且印章能根据新画面自我微调，越跟越准，还能跑到 600 帧以上。",
         concepts=["concept-correlation-filter", "concept-circulant-matrix"],
         tags=["classic-cv", "tracking", "correlation-filter", "real-time"],
         papers=["paper-bolme-2010-mosse"],
         evolvedFrom="algo-camshift", dependsOn=[], replacedBy=["algo-kcf", "algo-csrt"], inheritedBy=[],
         status="stable"),
    dict(slug="flann", name="FLANN 快速最近邻搜索", nameEn="Fast Library for Approximate Nearest Neighbors",
         year=2009, branch="branch-feature-matching", layer="L3",
         plainTalk="面对成千上万个特征点，要找出最像的那一个。FLANN 不比所有人逐一对照，而是先按特征相似度建一棵会自我修剪的目录树，只翻最有可能的几页，用『差不多最像』换来几十倍的搜索速度。",
         concepts=["concept-nearest-neighbor"],
         tags=["classic-cv", "matching", "approximate-nn", "kdtree"],
         papers=["paper-muja-2009-flann"],
         evolvedFrom=None, dependsOn=["op-bfmatcher"], replacedBy=[], inheritedBy=[],
         status="stable"),
    dict(slug="essential-matrix", name="本质矩阵与八点法", nameEn="Essential Matrix & Eight-Point Algorithm",
         year=1981, branch="branch-geometry", layer="L3",
         plainTalk="同一张照片从两个略微不同的位置各拍一张，画面里的对应点之间藏着一个固定的数学约束。本质矩阵就是把这个约束写成一张 3×3 的小表格，只要给出八对以上的对应点，就能解出两张照片之间的相机相对位置和朝向。",
         concepts=["concept-epipolar-geometry", "concept-fundamental-matrix"],
         tags=["classic-cv", "geometry", "slam", "epipolar"],
         papers=["paper-longuet-higgins-1981"],
         evolvedFrom="algo-epipolar-geometry", dependsOn=["algo-homography"], replacedBy=[],
         inheritedBy=[], status="stable"),
    dict(slug="triangulation", name="三角化重建", nameEn="Triangulation",
         year=1997, branch="branch-geometry", layer="L3",
         plainTalk="两只眼睛看同一个点，各自的视线方向不同；两条视线在空间里相交的地方，就是物体真正的三维位置。三角化就是拿两个相机的位置和两条视线，用几何求出这个交点坐标，把平面照片还原成立体坐标。",
         concepts=["concept-triangulation", "concept-reprojection-error"],
         tags=["classic-cv", "geometry", "3d-reconstruction", "slam"],
         papers=["paper-hartley-1997-triangulation"],
         evolvedFrom="algo-epipolar-geometry", dependsOn=["algo-essential-matrix"], replacedBy=[],
         inheritedBy=[], status="stable"),
    dict(slug="bundle-adjustment", name="光束法平差 BA", nameEn="Bundle Adjustment",
         year=1958, branch="branch-geometry", layer="L3",
         plainTalk="把所有相机的位姿和所有空间点的坐标当成一整副拼图，反复微调每一块，直到每个三维点重新投影回每张照片的位置都尽量贴合。它像团队一起对齐一张巨幅照片墙，让整体误差最小、结构最稳。",
         concepts=["concept-lm-optimization", "concept-reprojection-error"],
         tags=["classic-cv", "geometry", "slam", "optimization"],
         papers=["paper-triggs-2000-ba"],
         evolvedFrom="algo-zhang-calibration", dependsOn=["algo-triangulation"], replacedBy=[],
         inheritedBy=[], status="stable"),
    dict(slug="haar-wavelet", name="Haar 小波变换", nameEn="Haar Wavelet Transform",
         year=1989, branch="branch-image-processing", layer="L2",
         plainTalk="把一块豆腐先切成两半比大小，再各切两半继续比，最后把每层的『差异』和最后的『平均』都记下来。Haar 小波就是这种一层层切分图像的记录方式：大部分差异都很小，可以丢掉，于是图像被高效压缩，边缘信息还留在差异里。",
         concepts=["concept-wavelet", "concept-image-pyramid"],
         tags=["classic-cv", "transform", "multiresolution", "compression"],
         papers=["paper-mallat-1989-wavelet"],
         evolvedFrom=None, dependsOn=[], replacedBy=[], inheritedBy=["Haar-like 特征"],
         status="stable"),
]

PAPERS = [
    dict(slug="lindeberg-1990-scale-space", pid="paper-lindeberg-1990-scale-space",
         title="Scale-Space for Discrete Signals",
         authors=["Tony Lindeberg"],
         year=1990, venue="IEEE Transactions on Pattern Analysis and Machine Intelligence",
         venueType="journal", doi="10.1109/34.56208", citationCount=3200,
         contribution="把高斯核从「随手拿来平滑」提升为尺度空间唯一的正规化核，为高斯滤波、多尺度金字塔与 SIFT 奠定了数学根据。",
         keyInsight="只有当平滑核是高斯时，尺度空间才满足因果性——不会凭空造出新的极值结构。",
         novelty=["离散尺度空间公理化", "高斯核唯一性证明", "尺度归一化微分算子"],
         limitations=["只讨论线性尺度空间", "未涉及各向异性扩散"],
         relatedAlgorithms=["algo-gaussian-blur", "algo-sift", "algo-akaze"],
         readStatus="skimmed", tags=["classic", "scale-space", "gaussian"]),
    dict(slug="huang-1979-median", pid="paper-huang-1979-median",
         title="A Fast Two-Dimensional Median Filtering Algorithm",
         authors=["Thomas S. Huang", "George J. Yang", "Gregory Y. Tang"],
         year=1979, venue="IEEE Transactions on Acoustics, Speech, and Signal Processing",
         venueType="journal", doi="10.1109/TASSP.1979.1163188", citationCount=1400,
         contribution="给出二维中值滤波的快速实现，把朴素排序的复杂度从 O(k²logk) 降到与窗口尺寸近似线性，使中值滤波真正可用于图像。",
         keyInsight="滑动窗口之间大量像素重叠，可以复用上一步的排序结果，只需增删列。",
         novelty=["基于直方图的增量中值更新", "二维滑动窗口快速实现"],
         limitations=["大窗口或浮点图像仍偏慢", "对高斯噪声效果一般"],
         relatedAlgorithms=["algo-median-filter"],
         readStatus="skimmed", tags=["classic", "median", "nonlinear-filter"]),
    dict(slug="duda-hart-1972-hough", pid="paper-duda-hart-1972-hough",
         title="Use of the Hough Transformation to Detect Lines and Curves in Pictures",
         authors=["Richard O. Duda", "Peter E. Hart"],
         year=1972, venue="Communications of the ACM",
         venueType="journal", doi="10.1145/361237.361242", citationCount=9000,
         contribution="把霍夫变换从直线推广到任意参数化曲线（含圆），并给出极坐标参数化，成为形状检测的通用投票框架。",
         keyInsight="曲线检测 = 参数空间里的峰值查找：每个边缘点都为所有可能曲线投票。",
         novelty=["极坐标 ρ-θ 参数化", "圆/椭圆等任意曲线推广", "累加器峰值检测"],
         limitations=["参数维度升高时内存与计算量爆炸", "需要预设半径范围"],
         relatedAlgorithms=["algo-hough", "algo-hough-circles"],
         readStatus="skimmed", tags=["classic", "hough", "shape"]),
    dict(slug="douglas-peucker-1973", pid="paper-douglas-peucker-1973",
         title="Algorithms for the Reduction of the Number of Points Required to Represent a Digitized Line or its Caricature",
         authors=["David H. Douglas", "Thomas K. Peucker"],
         year=1973, venue="Cartographica: The International Journal for Geographic Information and Geovisualization",
         venueType="journal", doi="10.3138/FM57-6770-U75U-7727", citationCount=4200,
         contribution="提出道格拉斯-普克折线简化算法，用递归分治在给定误差内用最少顶点近似曲线，成为轮廓逼近与地图综合的经典方法。",
         keyInsight="距离首末连线最远的点一定是必须保留的拐点，递归切分即可得到最简表示。",
         novelty=["递归分治简化", "误差带阈值控制", "与 Ramer 独立提出"],
         limitations=["需自定误差阈值", "对闭合轮廓需特殊处理", "不自带形状语义"],
         relatedAlgorithms=["algo-contour-fitting"],
         readStatus="skimmed", tags=["classic", "contour", "simplification"]),
    dict(slug="alahi-2012-freak", pid="paper-alahi-2012-freak",
         title="FREAK: Fast Retina Keypoint",
         authors=["Alexandre Alahi", "Raphael Ortiz", "Pierre Vandergheynst"],
         year=2012, venue="IEEE Conference on Computer Vision and Pattern Recognition (CVPR)",
         venueType="conference", doi="10.1109/CVPR.2012.6247715", citationCount=2100,
         contribution="提出仿视网膜的采样图案与二进制描述子 FREAK，用级联比较在极低算力下端到端匹配，适合移动与嵌入式设备。",
         keyInsight="人眼视网膜中央密集、周边稀疏的采样分布，正是高效特征描述的好模板。",
         novelty=["仿视网膜同心采样图案", "级联式粗到精比较", "仅需几十字节描述子"],
         limitations=["旋转不变性弱于 SIFT/SURF", "尺度空间靠外部检测器提供"],
         relatedAlgorithms=["algo-freak", "algo-brisk", "algo-orb"],
         readStatus="skimmed", tags=["classic", "binary-descriptor", "bio-inspired"]),
    dict(slug="felzenszwalb-2004-graph", pid="paper-felzenszwalb-2004-graph",
         title="Efficient Graph-Based Image Segmentation",
         authors=["Pedro F. Felzenszwalb", "Daniel P. Huttenlocher"],
         year=2004, venue="International Journal of Computer Vision",
         venueType="journal", doi="10.1023/B:VISI.0000022288.19776.0e", citationCount=8000,
         contribution="提出基于最小生成树的贪心图分割，用自适应阈值在近线性时间内得到感知一致的超像素，是选择性搜索与语义分割前处理的基石。",
         keyInsight="两个区域是否合并，应由「区域内差异」与「区域间差异」的相对大小决定，而非固定阈值。",
         novelty=["自适应合并判据", "并查集近线性实现", "无需预设区域数量"],
         limitations=["参数 k 需手调", "小区域易被吞并或碎化", "对噪声敏感"],
         relatedAlgorithms=["algo-felzenszwalb-segmentation", "algo-slic", "algo-kmeans"],
         readStatus="skimmed", tags=["classic", "segmentation", "graph"]),
    dict(slug="zivkovic-2006-knn-bg", pid="paper-zivkovic-2006-knn-bg",
         title="Efficient Adaptive Density Estimation per Image Pixel for the Task of Background Subtraction",
         authors=["Zoran Zivkovic", "Ferdinand van der Heijden"],
         year=2006, venue="Pattern Recognition Letters",
         venueType="journal", doi="10.1016/j.patrec.2005.11.005", citationCount=2600,
         contribution="用每像素保留的最近样本做非参数密度估计（KNN 背景建模），无需假设高斯分布即可适应多模态背景。",
         keyInsight="背景像素的颜色分布未知，与其硬套高斯，不如直接记住它最近出现过的样本。",
         novelty=["非参数 KNN 密度估计", "样本缓存与自适应更新", "与 MOG 的高斯假设对比"],
         limitations=["内存随样本数增长", "对突然的光照变化需配合阴影抑制"],
         relatedAlgorithms=["algo-knn-background", "algo-mog2", "algo-vibe"],
         readStatus="skimmed", tags=["classic", "background-subtraction", "knn"]),
    dict(slug="barnich-2011-vibe", pid="paper-barnich-2011-vibe",
         title="ViBe: A Universal Background Subtraction Algorithm for Video Sequences",
         authors=["Olivier Barnich", "Marc Van Droogenbroeck"],
         year=2011, venue="IEEE Transactions on Image Processing",
         venueType="journal", doi="10.1109/TIP.2010.2101613", citationCount=2400,
         contribution="提出样本一致性背景建模 ViBe，用每像素一组历史样本与随机邻居传播，实现内存小、速度快、无需训练的背景减除。",
         keyInsight="背景模型不必独立建模，随机借用空间邻居的样本即可兼顾精度与内存。",
         novelty=["样本一致性判据", "随机邻域样本传播", "随机更新策略与保守更新"],
         limitations=["初始帧含运动物体易留鬼影", "对相机抖动敏感"],
         relatedAlgorithms=["algo-vibe", "algo-knn-background", "algo-mog2"],
         readStatus="skimmed", tags=["classic", "background-subtraction", "sample-based"]),
    dict(slug="bolme-2010-mosse", pid="paper-bolme-2010-mosse",
         title="Visual Object Tracking using Adaptive Correlation Filters",
         authors=["David S. Bolme", "J. Ross Beveridge", "Bruce A. Draper", "Yui Man Lui"],
         year=2010, venue="IEEE Conference on Computer Vision and Pattern Recognition (CVPR)",
         venueType="conference", doi="10.1109/CVPR.2010.5539960", citationCount=3000,
         contribution="提出最小输出平方误差相关滤波 MOSSE，用少量样本在频域训练跟踪滤波器，达到 600+ FPS 的实时稳健跟踪。",
         keyInsight="相关滤波可以在频域里一秒解出最优滤波器，跟踪难题变成一次除法。",
         novelty=["MOSSE 频域闭式解", "PSR 峰值旁瓣比置信度", "仿射与光照的在线自适应"],
         limitations=["对快速运动/严重遮挡鲁棒性弱", "尺度变化需额外处理"],
         relatedAlgorithms=["algo-mosse", "algo-kcf", "algo-csrt"],
         readStatus="skimmed", tags=["classic", "tracking", "correlation-filter"]),
    dict(slug="muja-2009-flann", pid="paper-muja-2009-flann",
         title="Fast Approximate Nearest Neighbors with Automatic Algorithm Configuration",
         authors=["Marius Muja", "David G. Lowe"],
         year=2009, venue="International Conference on Computer Vision Theory and Applications (VISAPP)",
         venueType="conference", doi="10.5220/0001787803310340", citationCount=3800,
         contribution="提出 FLANN 库与自动参数配置：为给定数据与精度目标自动挑选最优近似最近邻算法与参数，把特征匹配从暴力搜索解放出来。",
         keyInsight="没有万能的最邻近算法——让算法自己交叉验证挑选，比人工调参更稳。",
         novelty=["自动算法/参数配置", "随机 kd-tree 森林", "优先级搜索"],
         limitations=["近似性带来少量漏配", "建库有一次性开销"],
         relatedAlgorithms=["algo-flann", "algo-sift", "algo-orb"],
         readStatus="skimmed", tags=["classic", "ann", "kd-tree"]),
    dict(slug="longuet-higgins-1981", pid="paper-longuet-higgins-1981",
         title="A Computer Algorithm for Reconstructing a Scene from Two Projections",
         authors=["H. Christopher Longuet-Higgins"],
         year=1981, venue="Nature",
         venueType="journal", doi="10.1038/293133a0", citationCount=2700,
         contribution="提出八点法，用八对以上对应点线性求解本质矩阵，从两张投影重建场景，是运动恢复结构（SfM）的开山之作。",
         keyInsight="两视图之间的几何约束可写成一个 3×3 矩阵，八对点就足以线性解出。",
         novelty=["本质矩阵概念", "八点线性求解", "两视图重建流程"],
         limitations=["对噪声与错误匹配敏感", "需后续非线性优化精化"],
         relatedAlgorithms=["algo-essential-matrix", "algo-epipolar-geometry", "algo-homography"],
         readStatus="skimmed", tags=["classic", "sfm", "epipolar"]),
    dict(slug="hartley-1997-triangulation", pid="paper-hartley-1997-triangulation",
         title="Triangulation",
         authors=["Richard I. Hartley", "Peter Sturm"],
         year=1997, venue="Computer Vision and Image Understanding",
         venueType="journal", doi="10.1006/cviu.1997.0547", citationCount=2500,
         contribution="系统比较多种三角化方法，提出归一化 DLT 与最优几何三角化，为三维点重建给出可复现的标准解法。",
         keyInsight="三角化不应简单求两条射线的交点，而应在代数或几何误差意义下求最优逼近。",
         novelty=["多视图三角化统一框架", "最优几何三角化解法", "误差与退化分析"],
         limitations=["最优解法计算量较大", "病态配置下仍不稳定"],
         relatedAlgorithms=["algo-triangulation", "algo-essential-matrix", "algo-bundle-adjustment"],
         readStatus="skimmed", tags=["classic", "triangulation", "3d"]),
    dict(slug="triggs-2000-ba", pid="paper-triggs-2000-ba",
         title="Bundle Adjustment — A Modern Synthesis",
         authors=["Bill Triggs", "Philip F. McLauchlan", "Richard I. Hartley", "Andrew W. Fitzgibbon"],
         year=2000, venue="Vision Algorithms: Theory and Practice (IWVA)",
         venueType="conference", doi="10.1007/3-540-44480-7_21", citationCount=5200,
         contribution="系统总结光束法平差的理论与实现，明确 LM 优化、稀疏结构与鲁棒核的工程要点，成为 SfM/SLAM 的标准参考。",
         keyInsight="BA 是稀疏最小二乘问题：利用雅可比矩阵的稀疏块结构，才能让百万级变量的优化跑得动。",
         novelty=["稀疏 LM 框架综述", "鲁棒损失与初始化策略", "协方差与不确定性分析"],
         limitations=["对初始化与异常值敏感", "大规模场景需分块或滑动窗口"],
         relatedAlgorithms=["algo-bundle-adjustment", "algo-triangulation", "algo-icp"],
         readStatus="skimmed", tags=["classic", "slam", "optimization", "lsq"]),
    dict(slug="mallat-1989-wavelet", pid="paper-mallat-1989-wavelet",
         title="A Theory for Multiresolution Signal Decomposition: The Wavelet Representation",
         authors=["Stéphane G. Mallat"],
         year=1989, venue="IEEE Transactions on Pattern Analysis and Machine Intelligence",
         venueType="journal", doi="10.1109/34.192463", citationCount=12000,
         contribution="提出多分辨率分析与快速小波变换（Mallat 算法），把滤波器组与正交小波统一，奠定小波在图像压缩与多尺度分析中的地位。",
         keyInsight="多尺度分解可以由一对低通/高通滤波器的迭代下采样实现，等价于金字塔的推广。",
         novelty=["多分辨率分析理论框架", "快速小波变换 Mallat 算法", "正交小波基构造"],
         limitations=["正交小波的相位与边界处理需注意", "对非平稳纹理的解释有限"],
         relatedAlgorithms=["algo-haar-wavelet", "algo-gaussian-blur"],
         readStatus="skimmed", tags=["classic", "wavelet", "multiresolution"]),
]

CONCEPTS = [
    dict(cid="concept-median-filter", name="中值滤波", layer="L1",
         plainTalk="把邻域内的数值排队取中间那个，而不是取平均。极端值（如白点、黑点）排在队首队尾，永远轮不到它当代表，所以去椒盐噪声不糊边。",
         formal="对邻域窗口内像素灰度排序后取第 (k²+1)/2 个值作为输出，是一类秩排序（rank-order）非线性滤波。",
         usedBy=["algo-median-filter"], docsPath="/algorithms/median-filter/concepts",
         tags=["filter", "nonlinear", "rank-order"]),
    dict(cid="concept-contour-approximation", name="轮廓逼近", layer="L1",
         plainTalk="用尽量少的顶点去描出一条曲线或物体边界的过程。就像画简笔画——只保留拐弯处的关键点，其它点丢掉，形状看起来还一样。",
         formal="在给定最大偏差 ε 的约束下求折线最少顶点表示，常用道格拉斯-普克递归分治或最小误差多边形拟合。",
         usedBy=["algo-contour-fitting"], docsPath="/algorithms/contour-fitting/concepts",
         tags=["contour", "simplification", "shape"]),
    dict(cid="concept-wavelet", name="小波变换", layer="L1",
         plainTalk="一种『层层切分』的分析工具：先看大尺度的整体趋势，再看局部细节差异，每层都记下平均与差异。图像里大部分差异都很小，可以丢掉，因此既能压缩又能保留边缘。",
         formal="用一族在时间/空间上可平移、可伸缩的基函数（母小波的平移缩放）分解信号，得到多分辨率的时频（空间-频率）表示。",
         usedBy=["algo-haar-wavelet"], docsPath="/algorithms/haar-wavelet/concepts",
         tags=["transform", "multiresolution", "frequency"]),
    dict(cid="concept-nearest-neighbor", name="最近邻搜索", layer="L1",
         plainTalk="在一大堆东西里找出跟目标最像的那一个。数据集越大，一个个比对就越慢，所以要靠索引结构（如 kd 树）来少翻几页就找到答案。",
         formal="在度量空间中给定查询点 q，寻找使距离 d(q,x) 最小的 x；近似最近邻（ANN）在允许小误差的前提下换取亚线性查询复杂度。",
         usedBy=["algo-flann"], docsPath="/algorithms/flann/concepts",
         tags=["matching", "search", "index"]),
]


def w(path, text):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", os.path.relpath(path))


def q(v):
    v = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return '"' + v + '"'


def ylist(items, indent="  "):
    return "".join(f"{indent}- {x}\n" for x in items)


def gen_algo(a):
    lines = []
    lines.append(f"id: algo-{a['slug']}\n")
    lines.append("type: Algorithm\n")
    lines.append(f"name: {q(a['name'])}\n")
    lines.append(f"nameEn: {q(a['nameEn'])}\n")
    lines.append(f"year: {a['year']}\n")
    lines.append(f"branch: {a['branch']}\n")
    lines.append(f"status: {a['status']}\n")
    lines.append(f"docsPath: /algorithms/{a['slug']}/\n")
    lines.append(f"plainTalk: {q(a['plainTalk'])}\n")
    lines.append("concepts:\n" + ylist(a["concepts"]))
    lines.append("tags:\n" + ylist(a["tags"]))
    lines.append("papers:\n" + ylist(a["papers"]))
    if a["evolvedFrom"]:
        lines.append(f"evolvedFrom: {a['evolvedFrom']}\n")
    else:
        lines.append("evolvedFrom: null\n")
    lines.append("replacedBy:" + ("\n" + ylist(a["replacedBy"]) if a["replacedBy"] else " []\n"))
    lines.append("dependsOn:" + ("\n" + ylist(a["dependsOn"]) if a["dependsOn"] else " []\n"))
    lines.append("inheritedBy:" + ("\n" + ylist(a["inheritedBy"]) if a["inheritedBy"] else " []\n"))
    lines.append("painPoints: []\n")
    lines.append("tricks: []\n")
    lines.append(f"layer: {a['layer']}\n")
    return "".join(lines)


def gen_paper(p):
    lines = []
    lines.append(f"id: {p['pid']}\n")
    lines.append("type: Paper\n")
    lines.append(f"title: {q(p['title'])}\n")
    lines.append("authors:\n" + ylist(p["authors"]))
    lines.append(f"year: {p['year']}\n")
    lines.append(f"venue: {q(p['venue'])}\n")
    lines.append(f"venueType: {p['venueType']}\n")
    lines.append(f"contribution: {q(p['contribution'])}\n")
    lines.append(f"keyInsight: {q(p['keyInsight'])}\n")
    lines.append("novelty:\n" + ylist(p["novelty"]))
    lines.append("limitations:\n" + ylist(p["limitations"]))
    lines.append("relatedAlgorithms:\n" + ylist(p["relatedAlgorithms"]))
    lines.append("influencedBy: []\n")
    lines.append("influenced: []\n")
    lines.append(f"readStatus: {p['readStatus']}\n")
    lines.append("tags:\n" + ylist(p["tags"]))
    lines.append(f"doi: {p['doi']}\n")
    lines.append(f"citationCount: {p['citationCount']}\n")
    return "".join(lines)


def gen_concept(c):
    lines = []
    lines.append(f"id: {c['cid']}\n")
    lines.append("type: Concept\n")
    lines.append(f"name: {q(c['name'])}\n")
    lines.append(f"layer: {c['layer']}\n")
    lines.append(f"plainTalk: {q(c['plainTalk'])}\n")
    lines.append(f"formal: {q(c['formal'])}\n")
    lines.append("usedBy:\n" + ylist(c["usedBy"]))
    lines.append(f"docsPath: {c['docsPath']}\n")
    lines.append("tags:\n" + ylist(c["tags"]))
    return "".join(lines)


if __name__ == "__main__":
    for a in ALGOS:
        w(os.path.join(ROOT, "algorithms", f"algo-{a['slug']}.yaml"), gen_algo(a))
    for p in PAPERS:
        w(os.path.join(ROOT, "papers", f"{p['slug']}.yaml"), gen_paper(p))
    for c in CONCEPTS:
        w(os.path.join(ROOT, "concepts", f"{c['cid']}.yaml"), gen_concept(c))
    print("done")
