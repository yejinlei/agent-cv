# 概念反向索引 · 一个术语跳所有提到它的地方

> 你看到一个陌生术语（比如"非极大值抑制"），不知道它在哪篇论文、哪个算法、哪个踩坑里出现？
> 在这一页直接 Ctrl+F 搜术语，**它在本站出现过的所有位置**都会列出来。

::: tip 使用方式
- 按主题浏览：下方 8 大类列出所有核心概念
- 按字母搜：浏览器 Ctrl+F，输入术语即可跳转
- 找到想去的地方 → 点链接直达
:::

---

## 1. 图像基础（Image Basics）

| 概念 | 是什么（一句话） | 算法/页面 |
|---|---|---|
| 卷积 (Convolution) | 核在图像上滑动求加权和 | [Sobel](/algorithms/sobel/) · [Canny](/algorithms/canny/) · [高斯模糊](/operators/gaussian-blur) |
| 图像梯度 (Gradient) | 像素灰度变化率，方向+大小 | [Sobel](/algorithms/sobel/) · [Canny](/algorithms/canny/concepts) · [HOG](/algorithms/hog-svm/) |
| 高斯模糊 | 用高斯核加权平均去噪 | [Canny](/algorithms/canny/concepts) · [高斯模糊算子](/operators/gaussian-blur) |
| 图像金字塔 | 多分辨率逐层降采样 | [SIFT](/algorithms/sift/concepts) · [ORB](/algorithms/orb/) · [Lucas-Kanade](/algorithms/lucas-kanade/) |
| 直方图均衡 (Histogram Equalization) | 拉伸灰度分布增强对比 | [算子词典·直方图](/operators/histogram) |
| CLAHE | 对比度受限自适应直方图均衡 | [工业缺陷案例](/cases/industrial-defect) |
| 色彩空间 (RGB/HSV/Lab) | 不同坐标系表示颜色 | [K-Means 分割](/algorithms/kmeans/concepts) · [CamShift](/algorithms/camshift/) · [GrabCut](/algorithms/grabcut/) |
| 积分图 (Integral Image) | O(1) 求任意矩形区域和 | [Viola-Jones](/algorithms/viola-jones/concepts) · [SURF](/algorithms/surf/concepts) |
| 二值化 (Thresholding) | 按阈值分成前景背景 | [Otsu](/algorithms/otsu/) · [自适应阈值](/operators/adaptive-threshold) |

---

## 2. 特征检测（Feature Detection）

| 概念 | 是什么（一句话） | 算法/页面 |
|---|---|---|
| 角点 (Corner) | 两个方向灰度都变化大的点 | [Harris](/algorithms/harris/) · [Shi-Tomasi](/algorithms/shi-tomasi/) · [FAST](/algorithms/fast/) |
| 结构张量 (Structure Tensor) | 邻域梯度自相关矩阵 | [Harris](/algorithms/harris/concepts) · [Shi-Tomasi](/algorithms/shi-tomasi/) |
| 自相关函数 (Auto-correlation) | 窗口小位移下的 SSD | [Harris](/algorithms/harris/concepts) |
| Harris 响应 R = det(M)−k·tr(M)² | 判断角点/边/平坦区 | [Harris](/algorithms/harris/) |
| 尺度空间 (Scale Space) | 多次高斯模糊模拟不同距离 | [SIFT](/algorithms/sift/concepts) · [SURF](/algorithms/surf/) · [MSER](/algorithms/mser/) |
| DoG（差分高斯） | 相邻高斯层相减，近似 LoG | [SIFT](/algorithms/sift/concepts) |
| LoG（拉普拉斯高斯） | 高斯二阶导找斑点 | [DoG 算子](/operators/dog) |
| Hessian 矩阵 | 二阶导构成的矩阵，检测斑点 | [SURF](/algorithms/surf/concepts) · [MSER](/algorithms/mser/) |
| 盒子滤波 (Box Filter) | 矩形核近似高斯，配积分图加速 | [SURF](/algorithms/surf/concepts) |
| 方向分配 (Orientation Assignment) | 给关键点一个主方向 | [SIFT](/algorithms/sift/concepts) · [ORB](/algorithms/orb/concepts) |
| 灰度质心法 (Intensity Centroid) | 用矩求角点方向（不统计直方图） | [ORB](/algorithms/orb/concepts) |
| FAST 决策树 | ID3 学出的快速角点判定树 | [FAST](/algorithms/fast/) |
| 最大稳定极值区域 (MSER) | 阈值变化下面积最稳定的区域 | [MSER](/algorithms/mser/) |
| 非极大值抑制 (NMS) | 同一位置只留响应最大的点 | [Canny](/algorithms/canny/concepts) · [NMS 算子](/operators/non-max-suppression) |
| 双阈值滞后 (Hysteresis) | 高阈值确定强边、低阈值延伸弱边 | [Canny](/algorithms/canny/concepts) · [双阈值算子](/operators/double-threshold) · [滞后跟踪](/operators/hysteresis-tracking) |

---

## 3. 特征描述与匹配（Descriptor & Matching）

| 概念 | 是什么（一句话） | 算法/页面 |
|---|---|---|
| 描述子 (Descriptor) | 关键点附近的"身份指纹" | [SIFT](/algorithms/sift/) · [SURF](/algorithms/surf/) · [BRIEF](/algorithms/brief/) · [ORB](/algorithms/orb/) |
| SIFT 128 维梯度直方图 | 4×4 子区域 × 8 方向 bin | [SIFT](/algorithms/sift/concepts) |
| SURF 64 维 Haar 小波 | 4×4 子区域 × 4 个 Haar 响应 | [SURF](/algorithms/surf/concepts) |
| BRIEF 二进制描述子 | 随机点对灰度比较得到 0/1 串 | [BRIEF](/algorithms/brief/) |
| rBRIEF（steer BRIEF） | 学习出"相关性低+方差高"的点对 | [ORB](/algorithms/orb/concepts) |
| 汉明距离 (Hamming Distance) | 两个二进制串不同 bit 数 | [BRIEF](/algorithms/brief/) · [ORB](/algorithms/orb/) |
| 暴力匹配 (Brute-Force) | 所有点对两两算距离 | [描述子匹配](/branches/feature-matching/descriptors) |
| FLANN / KD-Tree 近邻 | 近似最近邻加速大库匹配 | [描述子匹配](/branches/feature-matching/descriptors) |
| Lowe 比率检验 (Ratio Test) | 最近/次近距离 < 0.8 才接受 | [SIFT](/algorithms/sift/tricks) · [RANSAC](/algorithms/ransac/) |
| K-D Tree | 多维数据快速近邻查询结构 | [SIFT/SURF 匹配实现](/algorithms/sift/source) |

---

## 4. 几何估计（Geometric Estimation）

| 概念 | 是什么（一句话） | 算法/页面 |
|---|---|---|
| RANSAC | 随机采样一致，剔除外点 | [RANSAC](/algorithms/ransac/) |
| 单应矩阵 (Homography) | 两视图间平面-平面的 3×3 变换 | [单应矩阵](/algorithms/homography/) |
| 基础矩阵 / 本质矩阵 | 两视图间极几何约束 | [对极几何](/algorithms/epipolar-geometry/) |
| 三角化 (Triangulation) | 由两视图 2D 点还原 3D 点 | [对极几何](/algorithms/epipolar-geometry/) |
| PnP (Perspective-n-Point) | 已知 3D-2D 对应求相机位姿 | [EPnP](/algorithms/pnpsolver/) |
| EPnP | 4 个虚拟控制点表示的 O(n) PnP | [PnP 求解器](/algorithms/pnpsolver/) |
| P3P | 3 点求解位姿（多解） | [PnP 求解器](/algorithms/pnpsolver/) |
| DLT (Direct Linear Transform) | 线性代数直接求投影矩阵 | [张氏标定](/algorithms/zhang-calibration/) |
| 对极约束 x'ᵀFx = 0 | 同一 3D 点在两视图的约束 | [对极几何](/algorithms/epipolar-geometry/) |
| ICP | 迭代最近点点云配准 | [ICP](/algorithms/icp/) |
| SVD 刚体变换 | 两组对应点求 R、t 的闭式解 | [ICP](/algorithms/icp/concepts) |
| KD-Tree 加速近邻 | 点云最近点查找 | [ICP](/algorithms/icp/source) |
| 张氏棋盘格标定 | 平面棋盘多视角求内外参 | [张氏标定](/algorithms/zhang-calibration/) |
| 径向畸变 / 切向畸变 | 镜头畸变成像误差 | [相机几何](/branches/geometry/camera-geometry) · [张氏标定](/algorithms/zhang-calibration/concepts) |

---

## 5. 光流与立体（Optical Flow & Stereo）

| 概念 | 是什么（一句话） | 算法/页面 |
|---|---|---|
| 光流约束方程 Ix·u + Iy·v + It = 0 | 灰度不变假设 | [Horn-Schunck](/algorithms/horn-schunck/concepts) · [Lucas-Kanade](/algorithms/lucas-kanade/concepts) |
| 孔径问题 (Aperture Problem) | 小窗口只能看到法向运动 | [Lucas-Kanade](/algorithms/lucas-kanade/painpoints) |
| LK 局部恒流假设 | 邻域内光流一致 | [Lucas-Kanade](/algorithms/lucas-kanade/concepts) |
| HS 全局平滑假设 | 邻域光流应变化小 | [Horn-Schunck](/algorithms/horn-schunck/concepts) |
| Farnebäck 多项式展开 | 局部二次多项式拟合估计位移 | [Farnebäck](/algorithms/farneback/) |
| 视差 (Disparity) | 同一 3D 点在左右图的坐标差 | [SGBM](/algorithms/sgbm/) |
| 极线校正 (Stereo Rectification) | 把双目变成水平平行、视差只在 x 方向 | [SGBM](/algorithms/sgbm/concepts) |
| 代价体 (Cost Volume) | 每个像素每个视差的匹配代价 | [SGBM](/algorithms/sgbm/architecture) |
| 视差代价 (SAD/SSD/NCC/MI) | 左右图邻域匹配程度度量 | [SGBM](/algorithms/sgbm/source) |
| SGM 半全局匹配 | 多方向 1D DP 聚合代价 | [SGBM](/algorithms/sgbm/) |
| P1/P2 惩罚项 | 小/大视差变化的平滑代价 | [SGBM](/algorithms/sgbm/tricks) |
| WLS 滤波 | 视差图后处理边缘保持平滑 | [SGBM](/algorithms/sgbm/tricks) |

---

## 6. 图像分割（Segmentation）

| 概念 | 是什么（一句话） | 算法/页面 |
|---|---|---|
| 形态学操作 (膨胀/腐蚀/开/闭) | 用结构元素对形状做"加/减" | [形态学](/algorithms/morphology/) |
| 连通域 (Connected Components) | 像素相邻同区域标记 | [形态学](/algorithms/morphology/source) |
| 距离变换 (Distance Transform) | 到最近背景点的距离 | [分水岭](/algorithms/watershed/concepts) |
| 分水岭 (Watershed) | 梯度地形集水盆浸没分割 | [分水岭](/algorithms/watershed/) |
| 标记控制分水岭 | 人工给 marker 避免过分割 | [分水岭](/algorithms/watershed/tricks) |
| K-Means 聚类 | 颜色/特征空间迭代聚类 | [K-Means](/algorithms/kmeans/) |
| Mean Shift | 密度梯度上升找模态聚类 | [Mean Shift](/algorithms/meanshift/) |
| SLIC 超像素 | LabXY 5 维 K-Means 局部超像素 | [SLIC](/algorithms/slic/) |
| 高斯混合模型 (GMM) | 多高斯加权拟合颜色分布 | [GrabCut](/algorithms/grabcut/concepts) |
| Graph Cut 能量最小化 | 图割求最小割=最小能量 | [GrabCut](/algorithms/grabcut/concepts) |
| 反投影 (Back Projection) | 概率密度映射回图像 | [CamShift](/algorithms/camshift/concepts) |

---

## 7. 经典检测（Classical Detection）

| 概念 | 是什么（一句话） | 算法/页面 |
|---|---|---|
| Haar-like 特征 | 相邻矩形灰度差 | [Viola-Jones](/algorithms/viola-jones/concepts) |
| 积分图加速 | 任意矩形和 O(1) | [Viola-Jones](/algorithms/viola-jones/concepts) |
| AdaBoost 级联 | 弱分类器串联，简单样本早拒识 | [Viola-Jones](/algorithms/viola-jones/concepts) · [AdaBoost](/operators/adaboost) |
| 滑动窗口 (Sliding Window) | 不同尺度窗口逐位置滑检 | [Viola-Jones](/branches/detection/sliding-window) |
| HOG (方向梯度直方图) | 单元格 9 bin 梯度方向统计 | [HOG+SVM](/algorithms/hog-svm/concepts) |
| Block 归一化 | 单元格内 L2/Hysteresis 归一化 | [HOG+SVM](/algorithms/hog-svm/concepts) |
| 线性 SVM | 最大间隔分类器 | [HOG+SVM](/algorithms/hog-svm/) · [SVM 训练](/operators/svm-training) |
| 难负例挖掘 | 把误检的负样本加回训练集再训 | [HOG+SVM](/algorithms/hog-svm/tricks) |
| DPM 可变形部件模型 | 根滤波器+部件滤波器+形变代价 | [DPM](/algorithms/dpm/) |
| Latent SVM | 隐变量（部件位置）+ 结构 SVM | [DPM](/algorithms/dpm/concepts) |
| BoVW 词袋模型 | 局部特征聚类成视觉词做全局表示 | [BoVW](/algorithms/bovw/) |

---

## 8. 工程踩坑索引（跨案例聚合）

| 坑 | 典型场景 | 排查页 |
|---|---|---|
| 边缘粗、不连续 | Canny 双阈值没调好 | [Canny 调参](/algorithms/canny/tricks) · [故障排查·阈值](/global/troubleshooting) |
| 二值化全白/全黑 | 光照不均用了固定阈值 | [Otsu 调参](/algorithms/otsu/tricks) |
| 角点跑飞 | KLT 光流窗口太小/金字塔没开 | [Lucas-Kanade 踩坑](/algorithms/lucas-kanade/painpoints) |
| 匹配全是错对 | 比例检验没开/外点太多没上 RANSAC | [SIFT 调参](/algorithms/sift/tricks) · [RANSAC](/algorithms/ransac/) |
| 分水岭全是马赛克 | 没给 marker 直接跑 | [Watershed 调参](/algorithms/watershed/tricks) |
| GrabCut 抠不干净 | 前景背景颜色相近 | [GrabCut 踩坑](/algorithms/grabcut/painpoints) |
| 立体视差全黑/雪花 | 最小/最大视差范围错、相机没校正 | [SGBM 踩坑](/algorithms/sgbm/painpoints) |
| ICP 越配越飞 | 没初值/重合率太低 | [ICP 踩坑](/algorithms/icp/painpoints) |
| 标定重投影误差大 | 标定板拍得太少/角点模糊 | [张氏标定调参](/algorithms/zhang-calibration/tricks) |
| HOG 行人误检太多 | 没做难负例挖掘、尺度没覆盖 | [HOG+SVM 踩坑](/algorithms/hog-svm/painpoints) |

---

## 三张索引页联动

- 概念按**主题**看 → 这一页
- 概念按**算法**看 → 每个算法的 `concepts.md`
- 概念按**算子**看 → [算子词典](/operators/)
- 概念按**场景**看 → [场景反查](/scenarios/)
- 遇到问题 → [故障排查手册](/global/troubleshooting)
