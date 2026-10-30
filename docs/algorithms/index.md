---
layout: doc
title: 算法档案总览
---

# 📄 算法档案总览

这里是 agent-cv 收录的全部传统 CV 算法档案，按**六大分支**折叠分组。每个算法都配有 7 页深度拆解：论文溯源 → 核心概念 → 算法架构 → 源码走读 → 实战踩坑 → 调参口诀。

> 🎮 想直接在浏览器里调参看效果？去 [🎮 真机实验室](/playgrounds/)；看不懂公式？去 [🧪 原理实验室](/math-lab/)；想按"我要做XX"找算法？去 [🎯 场景反查](/scenarios/)。

## 🔵 ① 图像处理（像素 → 像素）
- [Gaussian Blur 高斯模糊](/algorithms/gaussian-blur/) · 低通滤波，去噪平滑
- [Bilateral Filter 双边滤波](/algorithms/bilateral/) · 保边去噪
- [Median Filter 中值滤波](/algorithms/median-filter/) · 去椒盐噪声
- [CLAHE 限制对比度自适应直方图均衡](/algorithms/clahe/) · 局部对比度增强
- [Threshold 二值化阈值](/algorithms/threshold/) · 一刀切
- [Adaptive Threshold 自适应阈值](/algorithms/adaptive-threshold/) · 局部阈值
- [Otsu 大津法](/algorithms/otsu/) · 自动找阈值
- [Morphology 形态学操作](/algorithms/morphology/) · 腐蚀/膨胀/开/闭
- [Distance Transform 距离变换](/algorithms/distance-transform/) · 到最近边界的距离
- [Connected Components 连通域分析](/algorithms/connected-components/) · 找图里每个"块"
- [Contour Fitting 轮廓拟合](/algorithms/contour-fitting/) · 多边形/椭圆/外接圆逼近

## 🟢 ② 特征检测（像素 → 关键点）
- [Canny 边缘检测](/algorithms/canny/) · 最经典的边缘链路
- [Sobel / Prewitt / Roberts 一阶边缘算子](/algorithms/sobel/)
- [LoG 拉普拉斯高斯](/algorithms/log/) · 斑点/边缘
- [Harris 角点](/algorithms/harris/) · 自相关矩阵判角点
- [Shi-Tomasi (GFTT) 好跟踪角点](/algorithms/shi-tomasi/)
- [FAST 高速角点](/algorithms/fast/) · 机器学习+亮度比较
- [SIFT 尺度不变特征](/algorithms/sift/) · DoG 金字塔 + 主方向 + 128 维
- [SURF 加速稳健特征](/algorithms/surf/) · 积分图+Haar小波
- [FREAK 视网膜采样模式](/algorithms/freak/) · 生物启发二进制描述子
- [BRIEF 二进制描述子](/algorithms/brief/) · 随机点对比较
- [ORB 实时特征点](/algorithms/orb/) · oFAST + rBRIEF
- [BRISK 二进制鲁棒不变可伸缩关键点](/algorithms/brisk/)
- [AKAZE 加速 KAZE](/algorithms/akaze/) · 非线性尺度空间
- [MSER 最大稳定极值区域](/algorithms/mser/)
- [Gabor 滤波器组](/algorithms/gabor/) · 方向+频率
- [Haar 小波](/algorithms/haar-wavelet/)

## 🟠 ③ 特征匹配（关键点 → 对应关系）
- [Hough 直线/圆检测](/algorithms/hough/) · 投票法找形状
- [FLANN 快速近似最近邻](/algorithms/flann/) · KD 树/层次 KMeans
- [RANSAC 随机采样一致性](/algorithms/ransac/) · 抗外点鲁棒估计
- [Template Matching 模板匹配](/algorithms/template-matching/) · 滑动窗口找原型
- [BoVW 词袋模型](/algorithms/bovw/) · 视觉词包

## 🟣 ④ 图像分割（像素 → 区域）
- [GrabCut 交互式抠图](/algorithms/grabcut/) · 高斯混合 + 图割
- [Watershed 分水岭](/algorithms/watershed/) · 浸水筑坝
- [SLIC 超像素](/algorithms/slic/) · KMeans 聚类
- [Felzenszwalb 基于图的高效分割](/algorithms/felzenszwalb-segmentation/) · 最小生成树
- [Region Growing 区域生长](/algorithms/region-growing/) · 从种子往外扩
- [K-Means 颜色聚类](/algorithms/kmeans/)

## 🔴 ⑤ 目标检测与跟踪（区域 → 目标）
- [Viola-Jones 人脸检测](/algorithms/viola-jones/) · Haar+积分图+AdaBoost+级联
- [HOG+SVM 行人检测](/algorithms/hog-svm/) · 方向梯度直方图 + 支持向量机
- [DPM 可变形部件模型](/algorithms/dpm/) · HOG 扩展 + 部件弹簧模型
- [Haar Cascade 级联分类器](/algorithms/haar-cascade/)
- [MeanShift 均值漂移跟踪](/algorithms/meanshift/) · 颜色直方图反向投影
- [CamShift 连续自适应 MeanShift](/algorithms/camshift/)
- [KCF 核相关滤波](/algorithms/kcf/) · 循环矩阵+HOG+核技巧
- [CSRT 判别式通道与空间可靠性跟踪](/algorithms/csrt/)
- [MOSSE 最小输出平方和误差](/algorithms/mosse/) · 快速相关滤波
- [MOG2 自适应高斯混合背景减除](/algorithms/mog2/)
- [KNN 背景建模](/algorithms/knn-background/)
- [ViBe 视觉背景提取](/algorithms/vibe/)

## 🩵 ⑥ 几何视觉与运动（2D→3D、帧→运动）
- [Zhang 张氏相机标定](/algorithms/zhang-calibration/) · 棋盘格+LM
- [Homography 单应矩阵](/algorithms/homography/) · 4对点+DLT
- [Essential Matrix 本质矩阵](/algorithms/essential-matrix/) · 5点/8点法
- [Triangulation 三角化](/algorithms/triangulation/) · 从双视角反投影求3D
- [PnP 位姿估计](/algorithms/pnpsolver/) · 2D-3D对应求相机位姿
- [Epipolar Geometry 对极几何](/algorithms/epipolar-geometry/) · 极线/极点/基础矩阵
- [Bundle Adjustment 光束法平差](/algorithms/bundle-adjustment/)
- [Stereo BM/SGBM 立体匹配](/algorithms/stereo-bm/) · 块匹配/半全局匹配
- [ICP 迭代最近点](/algorithms/icp/) · 点云配准
- [Lucas-Kanade (KLT) 稀疏光流](/algorithms/lucas-kanade/) · 邻域一致 + 金字塔
- [Farnebäck 稠密光流](/algorithms/farneback/) · 二次多项式展开
- [Horn-Schunck 稠密光流](/algorithms/horn-schunck/) · 全局平滑约束
- [Phase Correlation 相位相关](/algorithms/phase-correlate/)
