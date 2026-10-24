---
layout: doc
outline: deep
---

# 🎮 在线交互 Playground

在浏览器里**真机运行传统 CV 算法**——不用装 OpenCV、不用写代码、不用上传图片到任何服务器。
底层是 **OpenCV.js（WebAssembly 版 OpenCV）**，全部计算在你的电脑/手机本地完成。

::: tip 玩法
1. 左边选一张**示例图**，或点「上传图片」用自己的照片
2. 中间选**算法**（共 39 种，覆盖六大分支），拖动滑块调参
3. 右边**实时**看到结果和处理耗时

所有算法基于 OpenCV.js 的官方函数，可直接对应到各算法档案第 5 页的 Python 代码。
:::

<OpencvPlayground />

## 支持的算法一览

Playground 覆盖了本站六大分支里可由 OpenCV.js 直接实现的核心算法：

| 分组 | 算法 | 对应档案 |
|------|------|----------|
| **图像预处理** | 灰度化、高斯滤波、中值滤波、双边滤波、直方图均衡、CLAHE、锐化、Gabor 纹理、LBP、Haar 小波一级分解 | [高斯](/algorithms/gaussian-blur/) · [中值](/algorithms/median-filter/) · [双边](/algorithms/bilateral/) · [CLAHE](/algorithms/clahe/) · [Gabor](/algorithms/gabor/) · [LBP](/algorithms/lbp/) · [Haar 小波](/algorithms/haar-wavelet/) |
| **边缘与基元** | Sobel、Laplacian、Canny、阈值/Otsu、自适应阈值、形态学、霍夫直线、霍夫圆、Harris、Shi-Tomasi、FAST、BRISK、AKAZE、MSER、SimpleBlob、ORB、轮廓逼近 | [Canny](/algorithms/canny/) · [霍夫圆](/algorithms/hough-circles/) · [形态学](/algorithms/morphology/) · [FAST](/algorithms/fast/) · [BRISK](/algorithms/brisk/) · [AKAZE](/algorithms/akaze/) · [MSER](/algorithms/mser/) · [轮廓拟合](/algorithms/contour-fitting/) |
| **图像分割** | K-Means、颜色阈值 inRange、距离变换、连通域、分水岭 | [K-Means](/algorithms/kmeans/) · [分水岭](/algorithms/watershed/) · [连通域](/algorithms/connected-components/) |
| **匹配与几何** | 模板匹配、ORB+BFMatcher 特征匹配、RANSAC 单应校正、LK 稀疏光流、稠密光流、梯度热力图 | [FLANN](/algorithms/flann/) · [单应矩阵](/algorithms/homography/) · [Lucas-Kanade](/algorithms/lucas-kanade/) · [Farnebäck](/algorithms/farneback/) |
| **传统目标检测** | Viola-Jones 人脸检测（Haar + AdaBoost 级联） | [Viola-Jones](/algorithms/viola-jones/) |

::: details 为什么个别算法不在 Playground 里
像 Felzenszwalb 图分割、FLANN 近似最近邻、光束法平差、三角化这类算法，OpenCV.js 官方构建**没有暴露对应函数**（该构建精简掉了 features2d/calib3d 的部分接口）。
它们在各自的算法档案里给出了完整 Python 实现与原理讲解，可以直接在本地 OpenCV 环境复现。
:::

## 为什么用 OpenCV.js？

- **零部署**：纯前端，静态托管即可（本站正是发布在 GitHub Pages）
- **隐私安全**：图片不出浏览器，适合处理敏感图像
- **可复现**：参数面板里的调用方式与各算法档案第 5 页完全一致
- **低门槛**：没有 GPU、没有 Python 环境也能动手体验传统 CV

## 性能参考

| 算法 | 480×480 典型耗时 | 说明 |
|------|------------------|------|
| 灰度化 / 阈值 | < 1 ms | 逐像素运算 |
| 高斯 / 中值 / 双边滤波 | 2 ~ 15 ms | 双边最慢 |
| Canny / Sobel | 3 ~ 8 ms | 多阶段梯度运算 |
| 霍夫圆 | 20 ~ 60 ms | 与半径范围强相关 |
| K-Means（K=6） | 30 ~ 80 ms | 迭代聚类 |

::: warning 首次加载
OpenCV.js 约 11 MB，首次打开需要几秒下载（浏览器会缓存）。加载完成后所有操作都是本地瞬时完成。
:::
