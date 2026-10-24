---
title: 术语表
---

# 📖 传统 CV 术语表

> 遇到陌生词？按分类查。每个术语给出**白话解释 + 一个最小例子 + 相关算法跳转**。
>
> 第一次来？建议先读 [🐣 小白入门 5 页](/for-beginners/)，再把本表当字典查。

## 分类导航

- [🖼️ 一、图像基础](#一图像基础)
- [🔧 二、像素运算与滤波](#二像素运算与滤波)
- [📐 三、边缘 / 角点 / 斑点](#三边缘--角点--斑点)
- [🔑 四、关键点与描述子](#四关键点与描述子)
- [🧩 五、图像分割](#五图像分割)
- [🎯 六、目标检测](#六目标检测)
- [📷 七、相机与几何](#七相机与几何)
- [🎬 八、视频与运动](#八视频与运动)
- [⚙️ 九、工程与性能](#九工程与性能)
- [🧠 十、分类器与机器学习](#十分类器与机器学习)
- [🔗 十一、与深度学习的衔接](#十一与深度学习的衔接)

---

## 一、图像基础

### 像素（Pixel）

图像的最小单位。一张灰度图就是一个 H×W 的矩阵，矩阵里每个元素就是一个像素，值 0–255（0 黑，255 白）。

```python
img[y, x]  # 取第 y 行、第 x 列的像素值（注意 OpenCV 是 y 在前）
```

### 通道（Channel）

彩色图每个像素有 3 个数，分别代表 R（红）、G（绿）、B（蓝）三个通道。OpenCV 默认读进来是 **BGR** 顺序，不是 RGB——这是新手最容易踩的坑之一。还有第 4 个通道 Alpha 表示透明度，传统 CV 算法大多不用。

::: tip 白话
一张彩色照片其实是叠在一起的三张灰度图——一张只看红多少，一张只看绿多少，一张只看蓝多少。
:::

### 灰度图（Grayscale）

每个像素只有一个数 0–255，表示亮度。传统 CV 里大部分算法**先转灰度再处理**，因为颜色通常不关键，明暗变化才是。

```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
```

### HSV / HSL 色彩空间

RGB 是"硬件友好"的颜色表示，HSV（色相 Hue、饱和度 Saturation、明度 Value）是"人眼友好"的表示。**做颜色分割（比如找红色物体）时转 HSV 再按 H 阈值分割比 RGB 稳得多**——因为光照变化主要影响 V，不影响 H。

```python
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))  # 提取红色范围
```

### 直方图（Histogram）

统计图像里像素值的分布——比如"0 有几个、1 有几个……255 有几个"。直方图均衡化就是把直方图拉平，让亮的更亮、暗的更暗，增强对比度。

```python
hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
```

→ 关联算子：[histogram](/operators/histogram)

### ROI（Region of Interest，感兴趣区域）

图像里你真正关心的那块区域。先找到 ROI 再处理，能大幅节省算力。

```python
roi = img[100:300, 200:400]  # 裁剪矩形区域
```

### 图像金字塔（Image Pyramid）

把同一张图反复下采样（缩小），得到不同分辨率的一组图，叠起来像金字塔。**用来做多尺度检测**——比如人脸近看很大、远看很小，在不同层上滑窗就能覆盖各种尺寸。

- **高斯金字塔**：每一层用上一层高斯模糊后下采样
- **拉普拉斯金字塔**：用来保存高斯金字塔丢失的高频信息（图像重建用）

→ 关联论文：[Lowe 1999 尺度空间]<!-- /algorithms/sift/paper -->；关联深度学习：FPN（特征金字塔网络）

---

## 二、像素运算与滤波

### 卷积（Convolution）

拿一个小矩阵（叫核/kernel/模板）在图像上滑动，每个位置"对应位置相乘再求和"，得到一张新图。**传统 CV 里 90% 的操作都可以写成卷积**——模糊、锐化、边缘检测都是不同的核。

```python
# 手写一个 3x3 均值模糊
kernel = np.ones((3,3), np.float32) / 9
dst = cv2.filter2D(img, -1, kernel)
```

::: tip 白话
卷积就是拿一块"小抹布"在图片上挨个格子擦过去，每个格子用抹布上的权重算新值。抹布形状不同（核不同），效果就不同——模糊、锐化、找边全靠换抹布。
:::

### 核 / Kernel / 模板 / 掩模

就是上面说的"小矩阵"。不同核对应不同效果：

| 核 | 效果 |
|---|---|
| 全 1/9 | 均值模糊 |
| 高斯 | 高斯模糊（中心权重大）|
| Sobel Gx | 找水平边缘 |
| Sobel Gy | 找垂直边缘 |
| Laplacian | 找各方向边缘 |

→ 关联算子：[gaussian-blur](/operators/gaussian-blur)、[sobel](/operators/sobel)

### 滤波 / 平滑（Filtering / Smoothing）

去掉噪点、让图变柔和的操作。常用四种：

- **均值滤波**：邻域平均，简单但会模糊边缘
- **高斯滤波**：按高斯分布加权平均，边缘保持更好，**最常用**
- **中值滤波**：取邻域中位数，**去椒盐噪声（黑白噪点）神器**
- **双边滤波**：既考虑空间距离又考虑像素差，**去噪同时保边**

```python
blur = cv2.GaussianBlur(img, (5,5), 1.4)    # 高斯
med  = cv2.medianBlur(img, 5)               # 中值
bi   = cv2.bilateralFilter(img, 9, 75, 75)  # 双边
```

### 阈值化 / 二值化（Thresholding / Binarization）

把灰度图变成"只有黑和白"的图：像素值大于阈值设白（255），否则设黑（0）。

- **全局阈值**：全图用同一个数 `cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)`
- **自适应阈值**：每个小区域单独算阈值，适合光照不均 `cv2.adaptiveThreshold`
- **Otsu 阈值**：自动找到使类内方差最小的阈值，适合双峰直方图 `cv2.THRESH_OTSU`

→ 关联算法：[Otsu](/branches/image-processing/thresholding)；关联算子：[adaptive-threshold](/operators/adaptive-threshold)

### 形态学操作（Morphology）

针对二值图的"形状操作"，基于两个基本操作：

- **腐蚀（Erosion）**：拿一个小方块（结构元素）在图上滑，只有方块下全白才留白——白色区域"变瘦"，去小白点
- **膨胀（Dilation）**：方块下只要有一个白就设白——白色区域"变胖"，填小洞

组合操作：
- **开运算**（先腐蚀后膨胀）：去小白点/毛刺
- **闭运算**（先膨胀后腐蚀）：填小黑洞
- **形态学梯度**（膨胀减腐蚀）：提取轮廓
- **顶帽/黑帽**：提取比周围亮/暗的小斑块

```python
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
eroded  = cv2.erode(binary, kernel)
dilated = cv2.dilate(binary, kernel)
opened  = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
```

### 连通域 / Connected Components

二值图里"连在一起的白色像素"算一个区域，可以分别编号、统计面积、位置。Blob 分析的基础。

```python
num, labels, stats, centroids = cv2.connectedComponentsWithStats(binary)
# stats[i] 包含第 i 个连通域的 x, y, w, h, area
```

---

## 三、边缘 / 角点 / 斑点

### 梯度（Gradient）

像素值沿 x、y 方向变化的速度。**梯度大 = 像素值跳变剧烈 = 很可能是边缘**。对连续函数梯度是导数，对图像就是相邻像素差（Sobel、Prewitt、Roberts 算子算的就是这个）。

::: tip 白话
想象你站在山上，地面高度就是像素值。梯度指向"坡度最陡往上"的方向，大小就是坡度有多陡。平地梯度 = 0（蓝色天空、白墙），悬崖边上梯度极大（物体轮廓）。
:::

### 边缘（Edge）

亮度剧烈变化的位置，通常对应物体的轮廓、纹理边界、阴影边。边缘是零维以上的"线"特征。

### Canny 边缘检测

1986 年 John Canny 提出的多阶段边缘检测流水线：高斯模糊 → Sobel 算梯度 → 非极大值抑制 → 双阈值 → 滞后跟踪。40 年来仍是工业界默认选择。

```python
edges = cv2.Canny(cv2.GaussianBlur(gray, (5,5), 1.4), 50, 150)
```

→ 关联算法：[Canny 完整档案](/algorithms/canny/)

### 非极大值抑制（NMS, Non-Maximum Suppression）

**广义**：在一堆候选里只留局部最大的，压掉它周围的次大值。
- 在 Canny 里：沿梯度方向只留梯度最大的那个像素，把粗边压成 1 像素细边
- 在目标检测里：多个重叠框只留置信度最高的那个，压掉 IoU 大的重复框

→ 关联算子：[non-max-suppression](/operators/non-max-suppression)

::: warning 易错
NMS 是跨多个场景的通用概念，不要只把它当"YOLO 后处理"。它最早来自 Canny（1986），比深度学习早 30 年。
:::

### 双阈值 + 滞后跟踪（Double Threshold + Hysteresis）

Canny 最后两步：
- 梯度幅值 > 高阈值 → **强边**，直接保留
- 梯度幅值 < 低阈值 → 丢弃（是噪声）
- 介于两者之间 → **弱边**，如果它的 8 邻域内连着强边就留，否则丢弃

"滞后"指的是"弱边的去留取决于它和强边的连接关系"——这样边能连成连贯的轮廓。

→ 关联算子：[double-threshold](/operators/double-threshold)、[hysteresis-tracking](/operators/hysteresis-tracking)

### 角点（Corner）

两个方向梯度都很大的点（也就是"窗口往任何方向挪都会大变"）。角点是很稳定的"点特征"，可以用来做匹配、跟踪。

经典算法：Harris 角点（1988）、Shi-Tomasi（1994，改进 Harris，光流跟踪首选）、FAST（2006，极快，用于 ORB）。

```python
corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
```

### 斑点（Blob）

局部区域里"亮度与周围明显不同的一块"，比角点大、有面积。典型检测方法：LoG（Laplacian of Gaussian）、DoG（Difference of Gaussian，SIFT 用的）、MSER（最大稳定极值区域）。

### 亚像素精度（Sub-pixel Accuracy）

边缘/角点的"真位置"不一定落在像素网格整数坐标上。用插值和拟合可以把定位精度做到 0.01–0.1 像素，**这是工业测量（比如量螺丝直径）的关键技术**。

```python
cv2.cornerSubPix(gray, corners, (5,5), (-1,-1), criteria)
```

HALCON 商业库比 OpenCV 在亚像素精度上强很多，这也是工业界愿意付费的原因之一。

### 霍夫变换（Hough Transform）

在参数空间里"投票"检测特定形状的经典方法：
- **霍夫直线**：把每个边缘点投到 (ρ, θ) 参数空间，得票多的就是直线
- **霍夫圆**：投到 (cx, cy, r) 三维参数空间找圆
- **广义霍夫变换**：可以检测任意形状

```python
lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50)
```

**典型场景**：车道线检测、圆检测（找瓶盖、硬币、瞳孔）、直线测量。

---

## 四、关键点与描述子

### 关键点（Keypoint / Interest Point）

图像里"位置稳定、可重复检测"的点——通常是角点、斑点。只存坐标（x, y），还可能带尺度、方向。

### 描述子（Descriptor）

描述关键点"周围长什么样"的向量。两张图里同一个物理点的描述子应该很接近，不同点的描述子应该差很远。
- SIFT 描述子：128 维浮点向量
- SURF：64 维
- ORB(BRIEF)：256 位二进制串
- AKAZE：61/128 字节二进制

```python
sift = cv2.SIFT_create()
kps, descs = sift.detectAndCompute(gray, None)
# descs.shape == (len(kps), 128)，每一行是一个关键点的 128 维描述子
```

::: tip 白话
关键点说"这儿有个值得记住的点（坐标是...）"，描述子说"这附近长什么样（一堆数字）"。两张图比对时，先各自找出关键点、算出描述子，再按描述子"找最近的"做匹配。
:::

### 尺度不变性（Scale Invariance）

同一场景在相机前移（拍近、物体变大）或后移（拍远、物体变小）后，算法仍然能找到同一个物理点。**SIFT 第一个完美解决这个问题**——用图像金字塔 + DoG 找跨尺度极值。

### 旋转不变性（Rotation Invariance）

相机绕光轴旋转（图被转了个角度）后，算法仍能找到同一个物理点。**SIFT 给每个关键点分配主方向，再相对主方向计算描述子**，达成旋转不变。

### 光照不变性 / 鲁棒性

光照亮一点暗一点、加个偏色，描述子变化不大。SIFT 通过梯度方向（而不是梯度绝对值）+ 描述子归一化实现光照鲁棒。

### 最近邻匹配 / 次近邻比（NN / NNDR）

描述子匹配的两个规则：
- **最近邻（NN）**：描述子距离最小的那个配对
- **次近邻比（Lowe's ratio test）**：最近距离 / 次近距离 < 0.75–0.8，才认为匹配是对的——如果两个候选距离差不多，说明这个点"不独特"，容易配错，丢弃

```python
bf = cv2.BFMatcher(cv2.NORM_L2)
matches = bf.knnMatch(des1, des2, k=2)
good = [m for m, n in matches if m.distance < 0.75 * n.distance]
```

### SIFT / SURF / ORB / BRISK / AKAZE 对比

| 算法 | 年份 | 描述子类型 | 尺度/旋转不变 | 速度 | 专利 |
|---|---|---|---|---|---|
| SIFT | 2004 | 128 维浮点 | ✅/✅ | 🐢慢 | 原专利于 2020 年到期 |
| SURF | 2006 | 64 维浮点 | ✅/✅ | 🚶中 | 曾有专利 |
| BRIEF | 2010 | 256 bit 二进制 | ❌/❌ | ⚡️极快 | 无 |
| ORB | 2011 | 256 bit 二进制 | ✅/✅ | ⚡️极快 | 无（OpenCV 主推）|
| BRISK | 2011 | 512 bit 二进制 | ✅/✅ | ⚡️快 | 无 |
| FREAK | 2012 | 512 bit 二进制 | ✅/✅ | ⚡️快 | 无 |
| AKAZE | 2013 | 二进制 | ✅/✅ | ⚡️快 | 无（非线性尺度空间）|

**2026 年工业首选**：**ORB**（免费、快、够用）；专利问题消失后 **SIFT** 在精度要求高的场景回潮；**AKAZE** 在非线性尺度变化场景表现好。

→ 关联算法：[SIFT](/algorithms/sift/)

---

## 五、图像分割

### 二值分割 / Threshold Segmentation

最简单的分割：阈值化后连通域就是物体。适合背景简单、光照可控的工业场景。

### 边缘分割

Canny 出边缘 → 霍夫直线/圆 → 或边缘围成的轮廓。

### 区域分割

- **区域生长（Region Growing）**：从种子点向外扩张，相似的像素吞并
- **分水岭（Watershed）**：把图像当海拔图，从谷底开始灌水，水相遇的地方就是分割边界。能处理**互相接触的物体**（比如一堆粘在一起的硬币），但容易过分割
- **GrabCut (2004)**：用户给一个矩形框，算法用高斯混合模型 + 图割迭代优化，自动把前景抠出来——Windows/Office 里"移除背景"就是类似技术

```python
# GrabCut：用矩形框抠前景
mask = np.zeros(img.shape[:2], np.uint8)
bgdModel = np.zeros((1,65), np.float64)
fgdModel = np.zeros((1,65), np.float64)
rect = (50, 50, 450, 290)
cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
```

### 轮廓（Contour）

边缘"连成一条闭合曲线"就是轮廓。OpenCV `findContours` 能找到所有外轮廓和内轮廓，可以按面积、周长、圆度筛选。

```python
contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for c in contours:
    area = cv2.contourArea(c)
    perimeter = cv2.arcLength(c, True)
```

### 过分割 / 欠分割

- **过分割**：一个物体被切成好几块（阈值太严、分水岭种子太多）
- **欠分割**：多个物体被粘成一块（阈值太松、物体接触）

---

## 六、目标检测

### 滑动窗口（Sliding Window）

传统检测的基础范式：固定大小的窗口在图像里按步长扫，每个位置过一遍分类器"这是不是目标"。多尺度要做图像金字塔。**速度慢**是硬伤。

### 积分图（Integral Image / Summed Area Table）

Viola-Jones 提出的天才数据结构：先预处理一张"积分图"，其中每个像素值等于原图左上角到该点的矩形和。这样**任意矩形区域的像素和只要 4 次查表就能算出**，Haar 特征瞬间变快。

```
ii[y, x] = sum_{y'≤y, x'≤x} img[y', x']
矩形 (x1,y1)-(x2,y2) 的和 = ii[y2,x2] - ii[y1-1,x2] - ii[y2,x1-1] + ii[y1-1,x1-1]
```

### Haar 特征

Viola-Jones 用的简单特征：相邻矩形区域像素和之差，用来捕捉"眼睛比脸颊暗""鼻梁比两侧亮"这类模式。因为有积分图，数十万 Haar 特征都能瞬间算完。

### 级联分类器（Cascaded Classifier）

Viola-Jones 的灵魂：不是用一个大分类器判一次，而是**多级串联漏斗**：
- 第 1 级用 2 个简单特征快速毙掉 50% 窗口
- 第 2 级用 10 个特征再毙 30%
- ...
- 最后一级用 200+ 特征做最终判定

平均每个窗口只算了几个特征就被毙掉，整体速度比单分类器快几十倍，2001 年就在 Pentium III 上跑 30 FPS 人脸检测。

→ 关联算法：[Viola-Jones](/branches/detection/viola-jones)

### AdaBoost（Adaptive Boosting）

把一堆"比瞎猜好一点"的弱分类器（比如单个 Haar 特征 + 一个阈值）加权组合成强分类器。每一轮**提高被前一轮错分样本的权重**，让下一轮的弱分类器更关注难样本。

→ 关联算子：[adaboost](/operators/adaboost)

### SVM（Support Vector Machine，支持向量机）

在特征空间里找一个**间隔最大**的超平面，把正负样本分开。HOG 检测的标配分类器；核技巧（Kernel Trick）可以处理线性不可分的情况。HOG+线性SVM 是 2005–2012 年行人检测的黄金组合。

### HOG（Histogram of Oriented Gradients）

方向梯度直方图。把窗口切成 8×8 的 cell，每个 cell 统计 9 个方向的梯度直方图；2×2 的 cell 组成一个 block 做归一化；整窗 3780 维向量送 SVM。

→ 关联算法：[HOG+SVM](/algorithms/hog-svm/)

### DPM（Deformable Part Model，可变形部件模型）

2008–2010 年 Felzenszwalb 提出，HOG 的升级版：**根滤波器（整个人）+ 部件滤波器（头/手/腿）+ 部件变形代价**——部件可以相对根有位移，代价按弹簧模型计算，能处理"弯腰的行人""抬腿的人"这类形变。DPM 是深度学习之前检测的顶峰，也是 R-CNN 的直接先驱。

→ 关联算法：[DPM](/branches/detection/dpm)

### BoVW / Bag of Visual Words（视觉词袋）

把 SIFT/HOG 这种局部特征当"视觉单词"，先对一堆描述子做 K-means 聚类得到"词典"，再把每张图的特征映射到单词、统计词频直方图——最后用 SVM 分类。2004–2012 年是**通用图像分类**的主流方案（你可以把它想象成"把图像当文本，用 TF-IDF 做分类"）。

→ 关联算法：[BoVW](/branches/detection/bovw)

### IoU（Intersection over Union，交并比）

两个框的交集面积 / 并集面积。0 = 不相交，1 = 完全重合。用来衡量"预测框和真值框重合度"，也是 NMS 的判据。

```
IoU = (A ∩ B).area / (A ∪ B).area
```

### bbox（Bounding Box，边界框）

用 `(x, y, w, h)` 或 `(x1, y1, x2, y2)` 表示的矩形框，把物体框在里面。目标检测的输出形式。

### 混淆矩阵 / 精确率 / 召回率

- **TP（真阳性）**：是目标，检测对了
- **FP（假阳性）**：不是目标，报成目标（误检）
- **FN（假阴性）**：是目标，没检出来（漏检）
- **TN（真阴性）**：不是目标，没报（检测里通常不关心）
- **精确率 Precision** = TP/(TP+FP)：报出来的里面多少是对的
- **召回率 Recall** = TP/(TP+FN)：应该找出来的里面找出来多少

### mAP（mean Average Precision）

检测任务的核心指标：每一类画 PR 曲线（精确率-召回率）、算曲线下面积 AP，再对所有类别取平均。传统检测和深度学习检测都用它。

### FPPW / FPPI

- **FPPW**（False Positives Per Window）：每窗口误报率，早期行人检测（HOG 时代）用
- **FPPI**（False Positives Per Image）：每张图误报数，更贴近实际使用

### 难例挖掘 / HNM（Hard Negative Mining）

训练分类器时，那些"被错分成正样本的负样本"就是难例（Hard Negative）。主动把这些难例挖出来加入训练集再训练，可以显著降低误检率。HOG+SVM 和 DPM 都依赖这个技巧。

---

## 七、相机与几何

### 针孔相机模型（Pinhole Camera Model）

最基本的相机模型：光从物体穿过"光心"投到成像平面。三个关键概念：
- **焦距 f**：光心到成像平面的距离，决定视角大小
- **光心 (cx, cy)**：主点，光轴与成像平面交点（理想情况下在图像中心）
- **投影公式**：`x_img = f · X / Z + cx`，`y_img = f · Y / Z + cy`——三维点 (X,Y,Z) 投到图像坐标

### 内参 / 外参（Intrinsics / Extrinsics）

- **内参矩阵 K**（3×3）：相机自身的参数，不随位置变
  ```
  K = [[fx, 0, cx],
       [0, fy, cy],
       [0,  0,  1]]
  ```
- **外参 [R|t]**（3×4）：相机在世界坐标系中的旋转 R 和平移 t，把世界坐标点变到相机坐标系

### 畸变（Distortion）

镜头不是完美的针孔，会让图像变形：
- **径向畸变**：离中心越远变形越大（桶形畸变/枕形畸变），用 k1, k2, k3 校正
- **切向畸变**：镜头和成像面不平行造成，用 p1, p2 校正

### 标定（Calibration）

求相机内参和畸变系数的过程。最经典的方法是**张正友标定法 (Zhang 2000)**：拍多张不同角度的棋盘格，检测棋盘角点，解方程求内参。OpenCV 里一整套函数都有。

```python
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, size, None, None)
```

### 对极几何 / 极线约束（Epipolar Geometry）

同一个 3D 点在两张图里的投影之间的几何关系：**左图上的一个点，它在右图里的对应点一定在对应的极线上**——这把二维搜索降为一维搜索，立体匹配速度大幅提升。

### 基础矩阵 F / 本质矩阵 E

- **基础矩阵 F（3×3）**：两张未标定图像之间的对极约束关系
- **本质矩阵 E（3×3）**：已知内参时的对极几何关系，`E = K'^T · F · K`；从 E 可以分解出两个相机之间的 R 和 t

### 单应矩阵（Homography, H）

当被拍摄物体都在同一个平面上（比如桌面、墙面、文档），两张图之间的投影变换可以用一个 3×3 的单应矩阵描述，只有 8 个自由度。**图像拼接、文档矫正、广告牌替换**都用它。

```python
H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
warped = cv2.warpPerspective(img, H, (w, h))
```

### 立体视觉 / 视差 / 深度

双目相机（左右两个相机）拍同一场景：
- **视差 d**：同一个 3D 点在左图和右图 x 坐标的差
- **深度 Z** = f · B / d（B 是基线——两个相机光心的距离）——视差越大物体越近，视差越小物体越远
- **立体匹配**就是找右图里哪个点和左图每个点对应

### 视差图 / 深度图（Disparity / Depth Map）

每个像素一个值，表示该像素的视差或深度。立体匹配算法（SGM、BM、SGBM）输出视差图，再换算成深度图。

```python
stereo = cv2.StereoSGBM_create(minDisparity=0, numDisparities=64, blockSize=9)
disparity = stereo.compute(imgL, imgR)
```

### PnP（Perspective-n-Point）

已知 3D 点在世界坐标里的位置、以及它们在图像里的 2D 投影，求相机的外参（R, t）。**AR 把虚拟物体叠加到现实世界、机器人定位、无人机降落**都靠它。常用解法：P3P、EPnP、UPnP。

### ICP（Iterative Closest Point）

两组点云之间的配准算法：迭代找最近点对 → 估计变换（R,t）→ 应用变换 → 直到收敛。3D 重建、SLAM 后端优化的核心。

### SfM（Structure from Motion，运动恢复结构）

从一堆不同角度拍的照片，自动算出每张照片的相机位姿，同时重建出场景的三维点云。流程：特征提取（SIFT）→ 特征匹配 → 几何验证 → 稀疏重建 → 稠密重建。COLMAP 是目前最好的开源 SfM 工具之一。

### SLAM（Simultaneous Localization and Mapping）

机器人/AR/无人机一边移动一边建地图，同时知道自己在地图里的位置。经典视觉 SLAM（ORB-SLAM、LSD-SLAM、DSO）大量使用传统 CV 的特征点、RANSAC、PnP、Bundle Adjustment。

### BA（Bundle Adjustment，光束法平差）

SfM/SLAM 的最后一步：把所有相机位姿和三维点坐标当作变量，最小化**重投影误差**（3D 点重投影到图像上的位置和观测位置的差），是一个大规模非线性最小二乘问题。

---

## 八、视频与运动

### 光流（Optical Flow）

相邻两帧视频里，每个像素的运动矢量（往哪移、移了多少）。两个前提（亮度恒定、小运动）。

- **稀疏光流（Lucas-Kanade, 1981）**：只跟踪关键点（如 Shi-Tomasi 角点）的运动，速度快，KLT 跟踪器
- **稠密光流（Farneback 2003 / Horn-Schunck 1981）**：算每个像素的运动，慢但信息全

```python
# 稀疏光流：跟踪前一帧的角点
p1, st, err = cv2.calcOpticalFlowPyrLK(prev_gray, gray, p0, None)
# 稠密光流：每个像素都算
flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
```

### 背景建模 / 背景减除（Background Subtraction）

固定摄像头下，先"学"出一帧背景图，然后把当前帧和背景对比，差异大的就是运动物体。常用算法：MOG2（自适应高斯混合）、KNN、GMG。

```python
bg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50)
fgmask = bg.apply(frame)  # 前景 mask
```

**典型应用**：安防监控里检测"有没有人闯入"、交通流量统计。

### 帧差法

相邻两帧直接做差，绝对值大于阈值的像素判为"运动区域"。简单但帧间间隔太小、目标太慢时容易丢失内部。

### Meanshift / Camshift 跟踪

MeanShift：沿颜色直方图概率密度的"梯度上升"方向迭代找到目标新位置。CamShift 是 Meanshift 的自适应版本，窗口大小随目标大小变化。

### Kalman 滤波

根据过去的运动状态预测下一时刻位置，并把预测和观测融合得到最优估计。跟踪、传感器融合、控制里广泛使用。

---

## 九、工程与性能

### FPS（Frames Per Second）

每秒处理帧数。实时视频一般需要 ≥25 FPS。

### 延迟（Latency）

从输入到输出的时间。**工业高速产线比 FPS 更在意延迟**——因为物体在高速运动，延迟 10ms 就可能拍糊。

### 亚像素（Sub-pixel）

见上文角点部分。工业测量核心。

### ROI 处理

只在 ROI 里做重算法（如 HOG/SIFT），其他区域跳过，能显著提速。

### 图像金字塔加速

先在低分辨率层粗检，找到疑似区域后再到高分辨率层精检。这是 Viola-Jones、DPM 都用的加速手段，后来被 FPN 继承。

### 量化 / 定点化

把浮点运算（float32）改成定点整数（int8/uint16），能在 MCU/FPGA 上跑快很多，但要注意精度损失。SIFT 的 128 维描述子从 float32 改成 binary（ORB 的 256 bit）速度能快两个数量级。

### 二值描述子（Binary Descriptor）

BRIEF/ORB/BRISK/FREAK 这类描述子不是浮点向量，而是 0/1 比特串。匹配时用**汉明距离**（XOR 后数 1 的个数），CPU 一条 POPCNT 指令就能算，比 L2 距离快几个数量级——这是 ORB 在嵌入式端流行的核心原因。

### O(1) 复杂度

不管输入多大，计算时间恒定。积分图就是典型——任意矩形和都是 4 次查表，与矩形大小无关。

---

## 十、分类器与机器学习

### 弱分类器 / 强分类器

- **弱分类器**：比瞎猜好一点（50%+ε 准确率），比如"一个 Haar 特征 + 一个阈值"
- **强分类器**：多个弱分类器加权组合后准确率很高

AdaBoost/GentleBoost/RealBoost 都是把弱分类器组强的方法。

### 线性可分 / 核技巧

- **线性可分**：存在一个超平面（二维下是直线）能把正负样本分开
- **核技巧**：把数据映射到高维空间，在那里线性可分——SVM 的核心武器。线性 SVM 就够时尽量用线性，快

### K-Means 聚类

给定 K 个类别，迭代地把样本分给最近的聚类中心、更新中心，直到收敛。BoVW 用它来"学视觉词典"；图像分割里也用（颜色聚类）。

### 决策树 / 随机森林

- **决策树**：一串 if-else 判据组成的树
- **随机森林**：多棵决策树投票，防止过拟合。HOG 时代也有人用随机森林替代 SVM

### 维度灾难（Curse of Dimensionality）

维度越高，数据越"稀疏"，需要的样本量指数级增长，距离度量也失去意义。这就是为什么 SIFT 128 维已经算高维，要做降维/聚类（BoVW 把局部特征聚类成 1000 个视觉词，再用词袋表示图）。

### PCA（主成分分析）

把高维数据线性投影到低维、保留最多方差的降维方法。特征脸（Eigenfaces）人脸识别就是 PCA + 最近邻。

### LDA（线性判别分析）

找一个投影方向，让投影后类内距离最小、类间距离最大——有监督降维。

---

## 十一、与深度学习的衔接

### CNN（Convolutional Neural Network，卷积神经网络）

核心是**可学习的卷积核**——传统 CV 的卷积核是人设计的（Sobel、Gaussian），CNN 的卷积核是通过反向传播**从数据里学出来的**。AlexNet (2012) 是分水岭。

### 感受野（Receptive Field）

输出特征图上的一个像素，在输入图上"看到"多大区域。传统 CV 里的"卷积核大小 + 金字塔层数"本质就是感受野；CNN 的深度堆叠就是为了扩大感受野。

### Anchor / 先验框

YOLOv2/SSD/Faster R-CNN 里预设的"不同尺寸/比例的候选框"。思想直接源自传统检测的**滑动窗口 + 多尺度**——只不过传统方法每个位置都要分类，Anchor 让网络直接预测相对 Anchor 的偏移。

### FPN（Feature Pyramid Network）

CNN 不同层的特征图对应不同尺度，加上自顶向下融合形成特征金字塔。思想直接继承自传统 CV 的**图像金字塔**，只不过把"分别在不同分辨率图上跑检测"换成了"不同层级特征融合后做检测"。

### NMS（后处理）

YOLO/Faster R-CNN 输出后要去重框——用的就是 NMS，算法本身和 Canny 里的 NMS 是**同一个思想**（局部最大保留，邻域抑制）。后来有 Soft-NMS、DIoU-NMS 等变体。

### RPN（Region Proposal Network）

Faster R-CNN 用来替代 Selective Search 的候选框生成模块。传统方法的 Selective Search（基于图像分割）→ RPN（用网络直接预测候选框），速度大幅提升。

### SuperPoint / SuperGlue

- **SuperPoint**（2018）：用 CNN 自动学"什么是好关键点、好描述子"，替代手工设计的 SIFT
- **SuperGlue**（2020）：用图神经网络做特征匹配，替代最近邻匹配
- 它们是"SIFT 思想的深度学习版"，传统几何视觉在深度学习时代的延续

### 可微传统算子

让传统 CV 算子（比如 NMS、RANSAC、双目匹配）变得"可导"，从而可以嵌入神经网络里端到端训练。代表工作：Soft-NMS、DeepLM、可微 RANSAC（NG-RANSAC）等。

---

## 还需要补充？

这个术语表会随着算法档案补全持续扩充。遇到新词你希望解释清楚：

- 📮 在 GitHub 提 issue 告诉我
- 或者在现有算法页里给术语加链接、改解释

传统 CV 50 年积累了大量术语，本表优先覆盖**工业场景常用 + 新手上路必遇**的词，学术冷门词在对应算法页里解释。
