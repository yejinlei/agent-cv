---
title: 本体实例索引
description: agent-cv 知识本体的全部实例清单（由 YAML 自动汇总）
---

# 本体实例索引

> 本页由 `ontology/instances/` 下的 YAML 实例汇总而成。
> 每个条目都是一个**可被校验、可被引用**的实体，
> 实体之间引用关系的一致性由 `python3 ontology/validate.py` 保证。

当前共 **175** 个实例，覆盖 10 类实体。运行校验脚本会同时检查：
字段类型是否合法、取值是否在枚举内、跨文件引用的 ID 是否存在。

```bash
python3 ontology/validate.py        # 校验全部实例
python3 ontology/validate.py ontology/instances/algorithms/canny.yaml   # 校验单个文件
```

## 一览

| 实体类型 | 数量 | 本体层 | 说明 |
| --- | --- | --- | --- |
| [算法 Algorithm](#算法-algorithm) | 19 | L3 | 一个完整算法，串联论文与算子 |
| [论文 Paper](#论文-paper) | 27 | L1 | 算法的原始文献出处 |
| [概念 Concept](#概念-concept) | 46 | L2 | 算法背后的原理概念 |
| [算子 Operator](#算子-operator) | 19 | L3 | 原子操作：一次卷积、一次阈值 |
| [应用 Application](#应用-application) | 8 | L4 | 算法用在哪儿 |
| [案例 CaseStudy](#案例-casestudy) | 3 | L4 | 可复现的工程落地记录 |
| [踩坑 PainPoint](#踩坑-painpoint) | 20 | L4 | 症状 → 根因 → 解法 |
| [技巧 Trick](#技巧-trick) | 15 | L4 | 工程技巧与调参经验 |
| [库 Library](#库-library) | 5 | L3 | 算法在工程中的承载者 |
| [章节 Chapter](#章节-chapter) | 13 | L0 | 纵轴学习路径的一章 |---

## 算法 Algorithm

L3 实现层的核心实体：一个完整算法，向上关联论文与概念，向下依赖算子。

| ID | 名称 | 年份 | 分支 | 原始论文 | 档案页 |
| --- | --- | --- | --- | --- | --- |
| `algo-hough` | 霍夫变换 | 1962 | 图像分割 | Hough 1962 | [打开档案](/algorithms/hough/) |
| `algo-sobel` | Sobel 边缘算子 | 1968 | 图像处理 | Sobel-Feldman 1968 | [打开档案](/algorithms/sobel/) |
| `algo-otsu` | Otsu 大津阈值法 | 1979 | 图像处理 | Otsu 1979 | [打开档案](/algorithms/otsu/) |
| `algo-epipolar` | 对极几何与基础矩阵 | 1981 | 几何视觉 | Longuet-Higgins 1981 | [打开档案](/algorithms/epipolar-geometry/) |
| `algo-homography` | 单应矩阵估计 | 1981 | 几何视觉 | Hartley-Zisserman 2003 | [打开档案](/branches/geometry/homography) |
| `algo-horn-schunck` | Horn-Schunck 稠密光流 | 1981 | 几何视觉 | Horn-Schunck 1981 | [打开档案](/branches/geometry/optical-flow) |
| `algo-lucas-kanade` | Lucas-Kanade 光流 | 1981 | 特征匹配 | Lucas-Kanade 1981 | [打开档案](/algorithms/lucas-kanade/) |
| `algo-optical-flow` | Lucas-Kanade 光流 | 1981 | 几何视觉 | Lucas-Kanade 1981 | [打开档案](/branches/geometry/optical-flow) |
| `algo-ransac` | RANSAC 随机采样一致 | 1981 | 特征匹配 | Fischler-Bolles 1981 | [打开档案](/algorithms/ransac/) |
| `algo-canny` | Canny 边缘检测 | 1986 | 特征检测 | Canny 1986 | [打开档案](/algorithms/canny/) |
| `algo-harris` | Harris 角点检测 | 1988 | 特征检测 | Harris-Stephens 1988 | [打开档案](/algorithms/harris/) |
| `algo-sift` | SIFT 尺度不变特征变换 | 1999 | 特征匹配 | Lowe 1999 | [打开档案](/algorithms/sift/) |
| `algo-zhang-calibration` | 张氏相机标定法 | 2000 | 几何视觉 | Zhang 2000 | [打开档案](/algorithms/zhang-calibration/) |
| `algo-viola-jones` | Viola-Jones 人脸检测 | 2001 | 传统检测 | Viola-Jones 2001 | [打开档案](/branches/detection/classic-detectors) |
| `algo-bovw` | 词袋模型 BoVW | 2004 | 传统检测 | Sivic-Zisserman 2003 | [打开档案](/branches/detection/bovw) |
| `algo-hog-svm` | HOG + SVM 行人检测 | 2005 | 传统检测 | Dalal-Triggs 2005 | [打开档案](/algorithms/hog-svm/) |
| `algo-surf` | SURF 加速稳健特征 | 2006 | 特征检测 | Bay-Tuytelaars 2006 | [打开档案](/versions/surf/) |
| `algo-dpm` | 可变形部件模型 DPM | 2008 | 传统检测 | Felzenszwalb-McAllester 2008 | [打开档案](/branches/detection/dpm) |
| `algo-orb` | ORB 实时特征点 | 2011 | 特征检测 | Rublee 2011 | [打开档案](/versions/orb/) |**演化关系**：Sobel → Canny；SIFT → SURF → ORB；SIFT → BoVW；Viola-Jones → HOG+SVM → DPM。
每条 `evolvedFrom` 都指向一个真实存在的算法实例，可在 [家族谱系](/global/family) 中查看完整脉络。

---

## 论文 Paper

L1 论文层：每条记录都给出可核验的出处（DOI 或公开链接），不允许凭印象写。

| ID | 标题 | 作者 | 年份 | 发表处 |
| --- | --- | --- | --- | --- |
| `paper-hough-1962` | Method and Means for Recognizing Complex Patterns | Paul V.C. Hough | 1962 | U.S. Patent 3069654 |
| `paper-sobel-1968` | A 3x3 Isotropic Gradient Operator for Image Processing | Irwin Sobel、Gary Feldman | 1968 | Stanford AI Project Technical Report |
| `paper-duda-hart-1972` | Use of the Hough Transformation to Detect Lines and Curves in Pictures | Richard O. Duda、Peter E. Hart | 1972 | Communications of the ACM, Vol.15 No.1 |
| `paper-kimme-circle-1975` | Finding Circles by an Array of Accumulators | C. Kimme、D. H. Ballard、J. Sklansky | 1975 | Communications of the ACM, Vol.18 No.2 |
| `paper-otsu-1979` | A Threshold Selection Method from Gray-Level Histograms | Nobuyuki Otsu | 1979 | IEEE Trans. Systems, Man, and Cybernetics |
| `paper-horn-schunck-1981` | Determining Optical Flow | Berthold K. P. Horn、Brian G. Schunck | 1981 | Artificial Intelligence |
| `paper-longuet-higgins-1981` | A Computer Algorithm for Reconstructing a Scene from Two Projections | H. Christopher Longuet-Higgins | 1981 | Nature |
| `paper-lucas-kanade-1981` | An Iterative Image Registration Technique with an Application to Stereo Vision | Bruce D. Lucas、Takeo Kanade | 1981 | IJCAI |
| `paper-ransac-1981` | Random Sample Consensus: A Paradigm for Model Fitting with Applications to Image Analysis and Automated Cartography | Martin A. Fischler、Robert C. Bolles | 1981 | Communications of the ACM |
| `paper-canny-1986` | A Computational Approach to Edge Detection | John F. Canny | 1986 | IEEE Transactions on Pattern Analysis and Machine Intelligence |
| `paper-harris-1988` | A Combined Corner and Edge Detector | Chris Harris、Mike Stephens | 1988 | Proc. 4th Alvey Vision Conference |
| `paper-hartley-1997` | In Defense of the Eight-Point Algorithm | Richard I. Hartley | 1997 | IEEE Trans. Pattern Analysis and Machine Intelligence |
| `paper-matas-ppht-1998` | Progressive Probabilistic Hough Transform | Jiri Matas、C. Galambos、J. Kittler | 1998 | BMVC 1998 / CVIU 2000, Vol.78 No.1 |
| `paper-lowe-1999` | Object Recognition from Local Scale-Invariant Features | David G. Lowe | 1999 | IEEE International Conference on Computer Vision (ICCV) |
| `paper-zhang-2000` | A Flexible New Technique for Camera Calibration | Zhengyou Zhang | 2000 | IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI) |
| `paper-viola-jones-2001` | Rapid Object Detection using a Boosted Cascade of Simple Features | Paul Viola、Michael Jones | 2001 | IEEE Conference on Computer Vision and Pattern Recognition (CVPR) |
| `paper-hartley-zisserman-2003` | Multiple View Geometry in Computer Vision (2nd Edition) | Richard Hartley、Andrew Zisserman | 2003 | Cambridge University Press |
| `paper-sivic-zisserman-2003` | Video Google: A Text Retrieval Approach to Object Matching in Videos | Josef Sivic、Andrew Zisserman | 2003 | ICCV 2003 |
| `paper-csurka-2004` | Visual Categorization with Bags of Keypoints | Gabriella Csurka、Christopher R. Dance、Lixin Fan、Jutta Willamowski、Cedric Bray | 2004 | ECCV 2004 Workshop on Statistical Learning in Computer Vision |
| `paper-lowe-2004` | Distinctive Image Features from Scale-Invariant Keypoints | David G. Lowe | 2004 | International Journal of Computer Vision |
| `paper-dalal-triggs-2005` | Histograms of Oriented Gradients for Human Detection | Navneet Dalal、Bill Triggs | 2005 | IEEE Conference on Computer Vision and Pattern Recognition (CVPR) |
| `paper-bay-2006` | SURF: Speeded Up Robust Features | Herbert Bay、Tinne Tuytelaars、Luc Van Gool | 2006 | European Conference on Computer Vision (ECCV) |
| `paper-surf-2006` | SURF: Speeded Up Robust Features | Herbert Bay、Tinne Tuytelaars、Luc Van Gool | 2006 | ECCV 2006 |
| `paper-felzenszwalb-2008-dpm` | A Discriminatively Trained, Multiscale, Deformable Part Model | Pedro F. Felzenszwalb、David McAllester、Deva Ramanan | 2008 | CVPR 2008 |
| `paper-felzenszwalb-2010-dpm` | Object Detection with Discriminatively Trained Part-Based Models | Pedro F. Felzenszwalb、Ross B. Girshick、David McAllester、Deva Ramanan | 2010 | IEEE TPAMI 2010 |
| `paper-orb-2011` | ORB: an efficient alternative to SIFT or SURF | Ethan Rublee、Vincent Rabaud、Kurt Konolige、Gary Bradski | 2011 | ICCV 2011 |
| `paper-rublee-2011` | ORB: An Efficient Alternative to SIFT or SURF | Ethan Rublee、Vincent Rabaud、Kurt Konolige、Gary Bradski | 2011 | IEEE International Conference on Computer Vision (ICCV) |每条论文实例都记录了 `contribution`（核心贡献）、`novelty`（新增点）、
`limitations`（局限）与 `influenced`（影响了谁）——这是「传承脉络」的原始数据。

---

## 概念 Concept

L2 理论层：算法背后的原理。每个概念的 `plainTalk` 字段都要求
「老奶奶也听得懂」，禁止出现公式；公式单独放在 `keyFormula`。

| ID | 概念 | 关联算法 |
| --- | --- | --- |
| `concept-anisotropy` | 各向异性（方向响应不均） | — |
| `concept-aperture-problem` | 孔径问题（Aperture Problem） | Lucas-Kanade 光流 |
| `concept-binary-descriptor` | 二进制描述子 | — |
| `concept-block-normalization` | 块内归一化 | — |
| `concept-brightness-constancy` | 亮度恒常性假设（Brightness Constancy） | Lucas-Kanade 光流、Horn-Schunck 稠密光流 |
| `concept-camera-model` | 针孔相机模型 | 张氏相机标定法 |
| `concept-cascade-classifier` | 级联分类器 | — |
| `concept-degenerate-configuration` | 退化配置（Degenerate Configuration） | — |
| `concept-dog` | 高斯差分（DoG） | — |
| `concept-double-threshold` | 双阈值与滞后连接 | — |
| `concept-epipolar-geometry` | 对极几何 | — |
| `concept-fast-detector` | FAST 角点判据 | — |
| `concept-fundamental-matrix` | 基础矩阵 F（Fundamental Matrix） | — |
| `concept-gaussian-blur` | 高斯模糊（高斯平滑） | Canny 边缘检测、SIFT 尺度不变特征变换、Lucas-Kanade 光流 |
| `concept-gradient-histogram-descriptor` | 梯度方向直方图描述子 | — |
| `concept-gradient-magnitude` | 梯度幅值与方向 | — |
| `concept-gradient-orientation-histogram` | 梯度方向直方图 | — |
| `concept-haar-feature` | Haar 特征 | — |
| `concept-hard-negative-mining` | 难例挖掘 | — |
| `concept-hessian-detector` | Hessian 行列式斑点检测 | — |
| `concept-histogram` | 直方图 | — |
| `concept-hog` | 方向梯度直方图 HOG | HOG + SVM 行人检测、可变形部件模型 DPM |
| `concept-homography` | 单应变换（投影变换） | — |
| `concept-hough-transform` | 霍夫变换 | 霍夫变换 |
| `concept-hysteresis` | 滞后效应（连通性） | — |
| `concept-inlier-outlier` | 内点与外点（Inlier / Outlier） | — |
| `concept-integral-image` | 积分图 | — |
| `concept-keypoint-localization` | 关键点定位 | — |
| `concept-kmeans` | K-Means 聚类 | 词袋模型 BoVW |
| `concept-lm-optimization` | Levenberg-Marquardt 非线性优化 | 张氏相机标定法 |
| `concept-non-maximum-suppression` | 非极大值抑制（NMS） | — |
| `concept-optical-flow` | 光流 | — |
| `concept-optimal-edge-criteria` | 最优边缘检测的三条判据 | — |
| `concept-orientation-assignment` | 方向分配（主方向） | — |
| `concept-otsu-threshold` | 最大类间方差判据 | — |
| `concept-parameter-space` | 参数空间 | 霍夫变换 |
| `concept-pyramid` | 图像金字塔 | SIFT 尺度不变特征变换、HOG + SVM 行人检测、可变形部件模型 DPM、Viola-Jones 人脸检测 |
| `concept-pyramidal-lk` | 金字塔 LK（Pyramidal Lucas-Kanade） | Lucas-Kanade 光流 |
| `concept-radial-distortion` | 径向畸变 | 张氏相机标定法 |
| `concept-ransac` | RANSAC 随机采样一致性 | — |
| `concept-reprojection-error` | 重投影误差 | 张氏相机标定法、RANSAC 随机采样一致 |
| `concept-scale-space` | 尺度空间 | — |
| `concept-sift` | SIFT 尺度不变特征变换 | SIFT 尺度不变特征变换、词袋模型 BoVW |
| `concept-sliding-window` | 滑动窗口 | — |
| `concept-svm-hyperplane` | SVM 超平面与支持向量 | — |
| `concept-triangulation` | 三角化（Triangulation） | — |---

## 算子 Operator

实现层的原子操作。与算法的区别在于：算子有明确的闭式定义（`formula`），
算法则是「多个算子按流程串起来」。

| ID | 算子 | 类别 | OpenCV 函数 |
| --- | --- | --- | --- |
| `op-adaboost` | AdaBoost 集成学习 | statistical | `cv2.ml.Boost_create` |
| `op-adaptive-threshold` | 自适应阈值 | point-operation | `cv2.adaptiveThreshold` |
| `op-canny-threshold` | Canny 双阈值与滞后跟踪 | edge | `cv2.Canny` |
| `op-corner-subpix` | 亚像素角点定位 | geometric | `cv2.cornerSubPix` |
| `op-dog` | 高斯差分（DoG） | filter | `（SIFT 内部实现，可手写为 GaussianBlur 相减）` |
| `op-double-threshold` | 双阈值判定 | point-operation | `（Canny 内部实现）` |
| `op-gaussian-blur` | 高斯模糊 | filter | `cv2.GaussianBlur` |
| `op-harris-response` | Harris 角点响应 | statistical | `cv2.cornerHarris` |
| `op-hessian` | Hessian 矩阵（二阶导数） | statistical | `cv2.cornerHarris（近似 Hessian 的响应）` |
| `op-histogram` | 直方图统计 | statistical | `cv2.calcHist` |
| `op-hough-vote` | 霍夫投票 | transform | `cv2.HoughLines / cv2.HoughLinesP / cv2.HoughCircles` |
| `op-hysteresis-tracking` | 滞后连接（边缘追踪） | edge | `（Canny 内部实现）` |
| `op-l2-normalization` | L2 归一化 | point-operation | `cv2.normalize(v, None, 1, 0, cv2.NORM_L2) 或 numpy 手算` |
| `op-lk-solve` | LK 最小二乘解 | statistical | `cv2.calcOpticalFlowPyrLK` |
| `op-non-max-suppression` | 非极大值抑制（边缘细化） | edge | `（Canny 内部实现，无独立函数）` |
| `op-separable-convolution` | 可分离卷积 | filter | `cv2.sepFilter2D` |
| `op-sobel` | Sobel 算子 | edge | `cv2.Sobel` |
| `op-svm-training` | SVM 训练 | statistical | `cv2.ml.SVM_create / sklearn.svm.SVC` |
| `op-taylor-expansion` | 泰勒展开（亚像素定位） | statistical | `（SIFT 内部实现）` |---

## 应用 Application

L4 实战层：算法用在哪儿。每个应用记录算法栈、硬件要求、约束与指标。

| ID | 应用场景 | 领域 | 需要 GPU | 算法栈 |
| --- | --- | --- | --- | --- |
| `app-document-scan` | 文档扫描与矫正 | 消费 | 否 | 高斯模糊 + Canny 边缘检测 + 单应矩阵估计 + 自适应阈值 |
| `app-edge-deployment` | 嵌入式边缘设备视觉 | 机器人 / IoT | 否 | Canny 边缘检测 + HOG + SVM 行人检测 |
| `app-industrial-defect` | 工业零件表面缺陷检测 | 工业制造 | 否 | 高斯模糊 + 直方图统计 + Canny 边缘检测 + HOG + SVM 行人检测 |
| `app-lane-detection` | 车道线检测 | 汽车 | 否 | 高斯模糊 + Canny 边缘检测 + 霍夫投票 + 霍夫变换 + RANSAC 随机采样一致 |
| `app-panorama` | 全景图像拼接 | 消费 | 否 | SIFT 尺度不变特征变换 + 单应矩阵估计 + L2 归一化 |
| `app-pedestrian-detection` | 行人检测 | 汽车 | 否 | Sobel 算子 + 直方图统计 + L2 归一化 + SVM 训练 + HOG + SVM 行人检测 |
| `app-security-surveillance` | 安防监控 | 安防 | 否 | Canny 边缘检测 + Viola-Jones 人脸检测 + Lucas-Kanade 光流 |
| `app-sfm-reconstruction` | 三维重建（SFM / 摄影测量） | 科研 | 否 | SIFT 尺度不变特征变换 + 单应矩阵估计 + 对极几何与基础矩阵 |**共同点**：8 个应用全部标注 `needsGPU: false`——这正是传统 CV 相对于
深度学习方案最硬的优势：**低算力、无 GPU、边缘设备可运行**。

---

## 案例 CaseStudy

L4 实战层中最"重"的实体：可复现的完整工程记录，
包含场景、流水线、硬件、参数、结果与经验教训。

### `case-industrial-defect` 产线零件表面缺陷检测

- **场景**：汽车零部件厂，30 件/分钟，无暑假工控机（i5，无 GPU）
- **亮点**：顶帽/黑帽变换分离局部亮暗异常，不依赖模板匹配
- **结果**：缺陷检出率 97.2%，单件耗时 180 ms
- **核心经验**：**光照比算法重要**——环形同轴光把划痕变成亮线，直接提升信噪比

详见 [实战案例：工业缺陷检测](/cases/industrial-defect)。

### `case-edge-deployment` 树莓派上的实时视觉部署

- **场景**：智能门禁，树莓派 4B（无 GPU），延迟 < 500 ms，功耗 < 5 W
- **亮点**：1080p 降到 640×480 后耗时降至约 1/5，而检测精度几乎不变
- **结果**：端到端约 220 ms，整机功耗约 3.5 W
- **核心经验**：**分辨率是第一优化旋钮**；用 OpenCV 内置函数而非 Python 循环

详见 [实战案例：边缘部署](/cases/edge-deployment)。

### `case-heritage` 文物数字化与档案扫描

- **场景**：3 万页民国报刊，泛黄、折痕、光照不均，需保留纸张质感
- **亮点**：先除法归一化消除光照，再用 CLAHE 局部增强，顺序不可颠倒
- **结果**：OCR 识别率由 76% 提升至 94%
- **核心经验**：**先归一再增强**；倾斜矫正用霍夫比用轮廓稳

---

## 踩坑 PainPoint

每条按「症状 → 根因 → 解法」组织，全部可定位到具体算法。

| ID | 症状 | 严重度 | 相关算法 |
| --- | --- | --- | --- |
| `pp-bovw-dict` | 视觉字典大小难选 | 中 | 词袋模型 BoVW |
| `pp-bovw-spatial` | 词袋丢失空间信息 | 高 | 词袋模型 BoVW |
| `pp-canny-aperture-size` | apertureSize 的效果没被理解 | 中 | Canny 边缘检测 |
| `pp-canny-not-blur` | 丢了 Canny 的第一步平滑 | 高 | Canny 边缘检测 |
| `pp-canny-threshold-guess` | Canny 阈值凭感觉设 | 高 | Canny 边缘检测 |
| `pp-dpm-part-tuning` | 部件数量与锚点难调 | 中 | 可变形部件模型 DPM |
| `pp-dpm-slow` | DPM 检测极慢 | 高 | 可变形部件模型 DPM |
| `pp-epipolar-no-normalize` | 不做归一化，八点法解出来的 F 完全不可用 | 高 | 对极几何与基础矩阵 |
| `pp-epipolar-planar-scene` | 对着平面拍，基础矩阵退化 | 中 | 对极几何与基础矩阵、单应矩阵估计 |
| `pp-epipolar-threshold` | RANSAC 阈值设错，内点被当外点清光 | 中 | 对极几何与基础矩阵、RANSAC 随机采样一致 |
| `pp-hog-scale-search` | 尺度步长太大导致漏检 | 中 | HOG + SVM 行人检测 |
| `pp-hog-very-slow` | HOG + 多尺度滑动极慢 | 高 | HOG + SVM 行人检测 |
| `pp-hog-window-mismatch` | HOG 窗口尺寸与训练时不一致 | 高 | HOG + SVM 行人检测 |
| `pp-ransac-no-refit` | 不做重拟合，精度停在几个像素 | 中 | RANSAC 随机采样一致 |
| `pp-ransac-threshold-unit` | 阈值单位与坐标单位不匹配，全部点被当成内点 | 高 | RANSAC 随机采样一致 |
| `pp-sift-patent` | SIFT 专利与许可证 | 高 | SIFT 尺度不变特征变换 |
| `pp-sift-ratio-test` | 不做 Lowe 比值检验 | 高 | SIFT 尺度不变特征变换 |
| `pp-sift-slow` | SIFT 慢到无法实时 | 高 | SIFT 尺度不变特征变换 |
| `pp-sobel-ddepth` | Sobel 用 CV_8U 导致一半梯度丢失 | 高 | Sobel 边缘算子 |
| `pp-viola-profile-face` | Viola-Jones 在侧脸和遮挡下失效 | 高 | Viola-Jones 人脸检测 |---

## 技巧 Trick

| ID | 技巧 | 难度 | 相关算法 |
| --- | --- | --- | --- |
| `trick-bovw-spm` | 空间金字塔匹配 SPM | 中 | 词袋模型 BoVW |
| `trick-bovw-tfidf` | TF-IDF 加权视觉词 | 易 | 词袋模型 BoVW |
| `trick-canny-for-drawing-contour` | Canny 用于提取可描线轮廓 | 中 | Canny 边缘检测 |
| `trick-canny-otsu-auto` | 用 Otsu 自动求 Canny 阈值 | 中 | Canny 边缘检测 |
| `trick-canny-threshold-ratio` | 双阈值按比例设定 | 易 | Canny 边缘检测 |
| `trick-dpm-hard-negative` | DPM 难例挖掘（Latent SVM + Hard Negative Mining） | 中 | 可变形部件模型 DPM、HOG + SVM 行人检测 |
| `trick-epipolar-model-select` | H 还是 F：用重投影误差自动选模型 | 中 | 对极几何与基础矩阵、单应矩阵估计 |
| `trick-epipolar-triangulation-filter` | 重建后按视差与重投影误差双向过滤 | 中 | 对极几何与基础矩阵 |
| `trick-hog-detection-window` | 检测窗口与多尺度策略 | 中 | HOG + SVM 行人检测 |
| `trick-hog-params` | HOG 参数的起点配置 | 中 | HOG + SVM 行人检测 |
| `trick-ransac-prescreen` | 先预筛提内点率，再跑 RANSAC | 易 | RANSAC 随机采样一致、SIFT 尺度不变特征变换 |
| `trick-sift-flann` | 用 FLANN 加速高维描述子匹配 | 中 | SIFT 尺度不变特征变换 |
| `trick-sift-lowe-ratio` | Lowe 比值阈值的取舍 | 易 | SIFT 尺度不变特征变换 |
| `trick-sobel-scale-abs` | Sobel 结果的正确处理链路 | 易 | Sobel 边缘算子 |
| `trick-viola-multi-scale` | Viola-Jones 多尺度与人脸检测配置 | 易 | Viola-Jones 人脸检测 |---

## 库 Library

| ID | 库 | 语言 | 定位 |
| --- | --- | --- | --- |
| `lib-numpy` | NumPy | Python | 所有图像算法的数值底座。 |
| `lib-opencv-cpp` | OpenCV (C++) | C++ | 嵌入式与高性能场景的 OpenCV 原始形态。 |
| `lib-opencv-python` | OpenCV (Python) | Python | 传统 CV 的通用工具箱：几乎所有经典算法都有实现。 |
| `lib-pillow` | Pillow (PIL) | Python | 图像读写与基础几何操作。 |
| `lib-scikit-image` | scikit-image | Python | 科研友好的图像处理库，算法实现贴近论文。 |---

## 章节 Chapter

L0 全局层的第 4 类实体：**纵轴学习路径**的一章，与横轴的 `Branch` 正交。
一章把散落在多个分支里的算法、概念、论文收拢成一条可顺序阅读的线索，
`prevChapter` / `nextChapter` 串成完整学习链。

| ID | 章 | 名称 | 抽象层次 | 核心问题 | 导览页 |
| --- | --- | --- | --- | --- | --- |
| `ch-03-preprocessing` | 3 | 图像预处理 | 低层 | 怎么把图"打扫干净"？ | [→](/chapters/ch03-preprocessing) |
| `ch-04-primitives` | 4 | 基元检测 | 低层 | 像素里哪些地方"有结构"？ | [→](/chapters/ch04-primitives) |
| `ch-05-segmentation` | 5 | 目标分割 | 中层 | 哪些像素属于同一个物体？ | [→](/chapters/ch05-segmentation) |
| `ch-06-representation` | 6 | 目标表达和描述 | 中层 | 怎么把一个目标变成一串数字？ | [→](/chapters/ch06-representation) |
| `ch-07-texture` | 7 | 纹理分析 | 中层 | 表面的"花纹手感"怎么量化？ | [→](/chapters/ch07-texture) |
| `ch-08-shape` | 8 | 形状分析 | 中层 | 物体的外形怎么描述和比较？ | [→](/chapters/ch08-shape) |
| `ch-09-stereo` | 9 | 立体视觉 | 高层 | 两张有视角差的图，怎么算出深度？ | [→](/chapters/ch09-stereo) |
| `ch-10-3d-recovery` | 10 | 三维景物恢复 | 高层 | 只有图像，怎么倒推出 3D 几何？ | [→](/chapters/ch10-3d-recovery) |
| `ch-11-motion` | 11 | 运动分析 | 高层 | 相邻帧之间，画面里的东西怎么动的？ | [→](/chapters/ch11-motion) |
| `ch-12-recognition` | 12 | 景物识别 | 高层 | 图像里有没有目标、在哪、是什么？ | [→](/chapters/ch12-recognition) |
| `ch-13-matching` | 13 | 广义匹配 | 高层 | 怎么建立两个实体之间的对应关系？ | [→](/chapters/ch13-matching) |
| `ch-14-activity` | 14 | 时空行为理解 | 高层 | 一段视频里的人在做什么动作？ | [→](/chapters/ch14-activity) |
| `ch-15-scene` | 15 | 场景解释 | 高层 | 这是什么场景？发生了什么？ | [→](/chapters/ch15-scene) |

**双轴关系**：横轴 [`Branch`](/branches/) 按算法家族切，纵轴 `Chapter` 按抽象层次切。
同一个算法可以同时挂在一条分支和一（多）个章下——例如 `algo-sift` 既属「特征匹配」分支，
又同时出现在第 4 章（关键点检测）和第 6 章（描述子）。

---

## 如何使用这些实例

**① 本地校验**（确认没有写错字段、没有悬空引用）：

```bash
cd ontology
pip install pyyaml jsonschema
python3 validate.py
```

**② 按 ID 交叉检索**：任何实例的 `id` 都可以在别的实例中被引用。
例如在 `algo-canny` 里看到 `painPoints: [pp-canny-threshold-guess]`，
去 `ontology/instances/painpoints/pp-canny-threshold-guess.yaml` 就能看到完整记录。

**③ 扩展本体**：新增一个算法只需
① 在 `instances/algorithms/` 下写 YAML；② 跑一次校验。
若引用了尚不存在的 ID，校验器会列为「悬空引用」并提示——
但**不会报错**，这是渐进式覆盖的设计：允许先建实例、再补文档。

## 相关页面

- [本体 Schema 规范](/ontology/schema)　— 每个字段的类型、枚举与含义
- [实体类型总览](/ontology/entity-types)　— 19 类实体的职责划分
- [关系与四层闭环](/ontology/relations)　— `evolvedFrom`、`dependsOn` 等 6 种关系
- [家族谱系](/global/family)　— 算法之间的演化脉络
