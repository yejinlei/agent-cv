#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量生成传统 CV 算法七页档案"""
import os
from pathlib import Path

ROOT = Path("/home/user/workspace/7648064683708846935/agent-cv/docs/algorithms")

# ========== 算法元数据 ==========
ALGOS = {
    # === 特征检测 ===
    "fast": {
        "name": "FAST 角点检测",
        "en": "Features from Accelerated Segment Test",
        "year": "2006",
        "author": "Edward Rosten / Tom Drummond",
        "branch": "feature-detection",
        "paper": "—",
        "tagline": "用一个圆圈 16 个邻居，一眼认出角点，速度比 Harris 快 10 倍",
        "analogy": "FAST 像一个哨兵：不进屋检查，只趴在窗户上数——窗外 16 个邻居里如果连续 12 个都比屋里亮或都比屋里暗，那这间房肯定是个「犄角旮旯」",
        "scene": "SLAM、AR、实时物体识别里做特征点检测，毫秒级返回几千个点，CPU 上就能跑 60fps",
        "pros": ["速度极快（比 Harris 快 10 倍以上）", "实现简单，一个 for 循环就够", "角点重复率高", "OpenCV 高度优化"],
        "cons": ["不具备尺度不变性", "不具备旋转不变性（后来 ORB 加上了）", "阈值敏感，噪声点多", "需要搭配 NMS 避免扎堆", "不含描述子，必须另配 BRIEF/ORB"],
        "chapter": "ch-8-local-feature",
        "level": "mid",
    },
    "brief": {
        "name": "BRIEF 二进制描述子",
        "en": "Binary Robust Independent Elementary Features",
        "year": "2010",
        "author": "Michael Calonder / Vincent Lepetit / Christoph Strecha / Pascal Fua",
        "branch": "feature-detection",
        "paper": "—",
        "tagline": "不再算浮点数直方图，只比 256 对像素大小，一个整数就能描述一个角点",
        "analogy": "SIFT/SURF 像做了一份 128 项血常规，BRIEF 只问 256 个「你比你旁边那个大吗」的是非题，用答案拼出一个 256 位的指纹",
        "scene": "资源受限的嵌入式设备、移动端、实时 SLAM 前端，需要毫秒级匹配几千个点",
        "pros": ["描述子只有 256 位（32 字节）", "汉明距离匹配极快（一个 POPCNT 指令）", "对光照模糊鲁棒", "构造简单，无需训练"],
        "cons": ["不具备旋转不变性（ORB 的 rBRIEF 解决）", "不具备尺度不变性（需配合金字塔）", "对噪声敏感", "随机点对选择影响性能"],
        "chapter": "ch-8-local-feature",
        "level": "mid",
    },
    "shi-tomasi": {
        "name": "Shi-Tomasi 角点 (GFTT)",
        "en": "Shi-Tomasi Corner / Good Features to Track",
        "year": "1994",
        "author": "Jianbo Shi / Carlo Tomasi",
        "branch": "feature-detection",
        "paper": "—",
        "tagline": "把 Harris 响应函数换成 min(λ1,λ2)，一个参数不用调，工程界角点首选",
        "analogy": "Harris 像个老中医用「阴阳失调公式」判断你是不是亚健康，还要调一个神秘的 k；Shi-Tomasi 直接看你「最差的那一科成绩」——只要最差那一科也及格，你就是好学生",
        "scene": "光流跟踪（goodFeaturesToTrack + calcOpticalFlowPyrLK 是标配）、相机标定棋盘角点、视频稳像",
        "pros": ["无需调 k 参数", "响应值物理意义明确（较小特征值）", "自带 minDistance 防扎堆", "能限制 top-N 数量，工程首选"],
        "cons": ["不具备尺度/旋转不变性", "需要定 qualityLevel 比例阈值", "分布不均时角点扎堆", "不是完整特征（只有点没有描述子）"],
        "chapter": "ch-8-local-feature",
        "level": "mid",
    },
    "mser": {
        "name": "MSER 最大稳定极值区域",
        "en": "Maximally Stable Extremal Regions",
        "year": "2002",
        "author": "Jiri Matas / Ondrej Chum / Martin Urban / Tomas Pajdla",
        "branch": "feature-detection",
        "paper": "—",
        "tagline": "像往黑白照片上浇水，颜色深浅慢慢渗开，那些形状最稳定的水坑就是好区域",
        "analogy": "把灰度图想象成一块地形，从黑到白慢慢淹水：一开始只有最深的坑有水，水涨后水面扩大。那些「水位变一点、水面大小几乎不变」的湖泊，就是最稳定的区域——MSER",
        "scene": "宽基线立体匹配、文本检测（自然场景文字）、目标识别中找图像块、对仿射变换要求高的场景",
        "pros": ["具备仿射不变性（视角变化强）", "多尺度区域检测", "无需预设阈值", "对光照变化鲁棒", "区域形状任意，不限于角点"],
        "cons": ["对模糊敏感", "速度较慢", "参数 delta/minArea/maxArea 需要调", "不适合低对比度图像", "检测到的是区域不是点，描述子要另算"],
        "chapter": "ch-8-local-feature",
        "level": "mid",
    },
    # === 图像分割 ===
    "watershed": {
        "name": "分水岭分割",
        "en": "Watershed Transform",
        "year": "1991",
        "author": "Luc Vincent / Pierre Soille",
        "branch": "segmentation",
        "paper": "—",
        "tagline": "把灰度图当地形图灌水，两个水坑汇合的地方就是分界线，专门切粘连物体",
        "analogy": "想象你在一块凹凸的地形上，从每个谷底开始慢慢灌水。当两个湖的水面要汇合时，你在汇合处修一道水坝——这些水坝就是分割线。这就是「分水岭」",
        "scene": "分离粘连硬币/细胞/颗粒、医学影像分割细胞、工业检测里数零件个数、重叠物体分割",
        "pros": ["能得到闭合连续的边界", "可分离粘连物体", "速度较快", "支持种子点控制", "经典稳定"],
        "cons": ["直接用会过度分割（碎成几百块）", "必须先做标记（marker）", "对噪声敏感", "需要形态学预处理"],
        "chapter": "ch-10-image-segmentation",
        "level": "mid",
    },
    "grabcut": {
        "name": "GrabCut 抠图",
        "en": "GrabCut Interactive Foreground Extraction",
        "year": "2004",
        "author": "Carsten Rother / Vladimir Kolmogorov / Andrew Blake",
        "branch": "segmentation",
        "paper": "—",
        "tagline": "画一个框就能把目标抠出来，GMM+GraphCut 迭代优化，Photoshop 快速选择的灵魂",
        "analogy": "你用笔在目标周围画个圈，对算法说「圈外肯定是背景，圈内有前景也有背景」。GrabCut 就像一个聪明的学徒，先猜哪些颜色像前景、哪些像背景，然后用 GraphCut 切一刀，再根据结果重新学颜色模型，反复 5 次就抠得干干净净",
        "scene": "照片抠图换背景、数据集快速标注、医学影像交互式分割、人像美颜前景提取",
        "pros": ["用户只需画一个框即可", "边缘细节比 GraphCut 好", "支持笔刷精修", "GMM 建模多峰颜色分布", "迭代自动优化"],
        "cons": ["高分辨率慢（1080p 约 5s）", "前景背景颜色接近时效果差", "矩形外永远是背景", "边缘毛发处理需 alpha matting", "bgdModel/fgdModel 容易填错"],
        "chapter": "ch-10-image-segmentation",
        "level": "mid",
    },
    "kmeans": {
        "name": "K-Means 颜色聚类",
        "en": "K-Means Clustering",
        "year": "1967",
        "author": "Stuart Lloyd (1957 提出) / James MacQueen 1967 命名",
        "branch": "segmentation",
        "paper": "—",
        "tagline": "把所有像素按颜色分成 K 堆，每堆一个代表色，图像立刻变卡通",
        "analogy": "把一盒彩笔按颜色分成 K 堆：先随机挑 K 支笔作为「小组长」，其他笔投奔最近的组长；每堆重新选一个「平均色」当新组长；反复到组长不再变。分完每堆用一个代表色涂，图像就被量化/分割了",
        "scene": "颜色量化（图像压缩）、海报风格化、肤色区域分割、语义分割前处理、矢量图调色板生成",
        "pros": ["思想极简单直观", "速度快（线性复杂度）", "OpenCV/sklearn 一行调用", "适用范围广", "结果可解释"],
        "cons": ["必须预先指定 K", "只看颜色不看位置（需加坐标扩展）", "对初始值敏感（用 kmeans++）", "对噪声离群点敏感", "聚类结果可能是局部最优"],
        "chapter": "ch-10-image-segmentation",
        "level": "basic",
    },
    "meanshift": {
        "name": "MeanShift 均值漂移",
        "en": "Mean-Shift Mode Seeking",
        "year": "1975 (Fukunaga) / 2002 (Comaniciu 应用到视觉)",
        "author": "K. Fukunaga / L. Hostetler / Dorin Comaniciu / Peter Meer",
        "branch": "segmentation",
        "paper": "—",
        "tagline": "每个点朝邻居最密的方向挪一步，最后聚成几坨——不用提前说有几坨",
        "analogy": "广场上站了一群人，每个人都往「周围人最密集的方向」走一步。走几步后大家会聚成几个紧密的小圈子，每个圈子就是一类。你不需要提前告诉大家「分成几队」，人自己会扎堆",
        "scene": "图像平滑分割（pyrMeanShiftFiltering）、目标跟踪（CamShift）、聚类、视频中运动目标分割",
        "pros": ["不需要指定聚类数", "同时考虑颜色+空间", "任意形状聚类", "对光照渐变鲁棒", "理论优雅"],
        "cons": ["速度很慢（1080p 几秒）", "带宽 sp/sr 参数难调", "窗口大小固定", "对高维数据不行", "OpenCV 只提供滤波版"],
        "chapter": "ch-10-image-segmentation",
        "level": "mid",
    },
    "slic": {
        "name": "SLIC 超像素",
        "en": "Simple Linear Iterative Clustering",
        "year": "2010",
        "author": "Radhakrishna Achanta / Appu Shaji / Kevin Smith / Aurelien Lucchi / Pascal Fua / Sabine Süsstrunk",
        "branch": "segmentation",
        "paper": "—",
        "tagline": "把 200 万像素切成 200 个颜色一致、大小均匀的小方块，后续处理快 1000 倍",
        "analogy": "把一张大图当成一块大蛋糕，先按网格切成小方块（期望大小），然后每块根据颜色往邻居那边微调，最后得到一堆大小差不多、颜色统一的小块。后续再做分割/检测时，以这些小块为单位，200 块比 200 万像素快 1 万倍",
        "scene": "分割预处理、显著性检测、光流加速、弱监督标注、深度估计超像素化、风格迁移",
        "pros": ["速度极快（线性复杂度）", "超像素紧凑均匀", "内存占用小", "仅两个参数（n_segments + compactness）", "边界贴合度好"],
        "cons": ["必须指定超像素数", "OpenCV 主分支没有（需 ximgproc）", "紧凑度 m 影响边界贴合", "不是分割终点，只是预处理"],
        "chapter": "ch-10-image-segmentation",
        "level": "mid",
    },
    # === 图像处理 ===
    "morphology": {
        "name": "形态学操作",
        "en": "Mathematical Morphology",
        "year": "1964",
        "author": "Georges Matheron / Jean Serra (巴黎矿校)",
        "branch": "image-processing",
        "paper": "—",
        "tagline": "膨胀、腐蚀、开、闭、顶帽黑帽——五把瑞士军刀帮你清理图像里的小毛刺和黑洞",
        "analogy": "形态学就像一套木匠的打磨工具：腐蚀像用砂纸把凸起毛刺磨掉，膨胀像给凹坑补腻子，开运算像「先磨毛刺再补漆」（去小白点），闭运算像「先补漆再磨平」（填小黑洞）",
        "scene": "二值图去噪、孔洞填充、边缘提取、骨架提取、字符识别预处理、OCR、工业缺陷检测预处理",
        "pros": ["速度极快（邻域比较）", "效果直观可控", "组合能力强（开闭梯度顶帽黑帽）", "支持任意核形状", "CPU 实时"],
        "cons": ["核大小/形状需要调", "大核运算慢", "过度腐蚀/膨胀会丢信息", "对边界细节破坏", "灰度形态学语义不如二值清晰"],
        "chapter": "ch-4-image-enhancement",
        "level": "basic",
    },
    # === 几何视觉 / 立体 ===
    "sgbm": {
        "name": "SGM 半全局立体匹配",
        "en": "Semi-Global Matching",
        "year": "2005",
        "author": "Heiko Hirschmüller",
        "branch": "geometry",
        "paper": "—",
        "tagline": "双目测距的工业标准，8 个方向做平滑约束，又快又稳出稠密视差图",
        "analogy": "BM 块匹配像个没耐心的小孩，只看自己周围一小圈就乱猜；SGM 像个老练的侦探，从上下左右斜 8 个方向打听消息，让相邻像素的深度「差不多」，拼出连贯的深度图",
        "scene": "双目深度相机（RealSense、自动驾驶双目）、无人机避障、机器人导航、三维重建、工业检测",
        "pros": ["输出稠密视差图", "速度可接受（CPU 实时）", "精度在经典方法里最高", "OpenCV 内置 StereoSGBM", "参数可解释（P1/P2 平滑）"],
        "cons": ["参数多（numDisparities/blockSize/P1/P2 等）", "无纹理区域仍失败", "重复纹理误匹配", "需要精确双目标定和立体校正", "远处深度误差平方级增长"],
        "chapter": "ch-14-3d-vision",
        "level": "advanced",
    },
    "pnpsolver": {
        "name": "PnP 位姿估计",
        "en": "Perspective-n-Point",
        "year": "1841 (Grunert P3P) / 2009 (EPnP)",
        "author": "Grunert / Fischler / Quan&Lan / Vincent Lepetit (EPnP)",
        "branch": "geometry",
        "paper": "—",
        "tagline": "已知几个 3D 点和它们在图上的位置，反推出相机在哪里看——AR 和机器人抓取的基石",
        "analogy": "你站在房间里，认出了墙上的钟、桌子上的杯子、书架顶上的花盆——这三个东西真实位置你知道（比如钟挂在门正上方 2.2 米），你就能反推出你自己站在房间的什么地方、朝什么方向看。PnP 就是这个「看几个地标定位自己」的算法",
        "scene": "AR 标记跟踪、机械臂抓取、视觉伺服、无人机着陆、增强现实虚拟物体叠加、SLAM 位姿求解",
        "pros": ["最少 3 个点就能解（P3P）", "一次 solvePnP 毫秒级", "RANSAC 版本鲁棒", "OpenCV 内置（P3P/EPnP/ITERATIVE/DLS）", "精度高"],
        "cons": ["需要已知内参 K", "3D 点精度要高（依赖标定）", "点共面/共线时退化", "对匹配外点敏感（需 RANSAC）", "输出的 t 与 3D 点单位一致，易出错"],
        "chapter": "ch-14-3d-vision",
        "level": "advanced",
    },
    "icp": {
        "name": "ICP 迭代最近点",
        "en": "Iterative Closest Point",
        "year": "1992",
        "author": "Paul Besl / Neil McKay (同时 Chen&Medioni 独立提出)",
        "branch": "geometry",
        "paper": "—",
        "tagline": "两片点云拼起来的经典算法：找最近点配对，算刚体变换，反复迭代到对齐",
        "analogy": "你拿着两张被撕碎的地图碎片，每次都把一片上每个点在另一片上找最近的对应点，计算平移旋转让它们靠近一点，再重新找对应点……反复几十次，两片就严丝合缝地拼在一起了",
        "scene": "激光雷达点云配准、三维重建、机器人定位（LiDAR SLAM）、多视角点云融合、医学影像配准",
        "pros": ["思想简单直观", "任何维度都适用（2D/3D）", "无需特征提取（直接用点坐标）", "Open3D/PCL 都有高效实现", "收敛保证（局部）"],
        "cons": ["需要初始位姿（否则容易局部最优）", "对动态物体/离群点敏感", "原始 O(N²) 慢（要 KD-Tree 加速）", "两片点云重叠率要够", "点到点版本精度不如点到面"],
        "chapter": "ch-14-3d-vision",
        "level": "advanced",
    },
    "homography": {
        "name": "单应矩阵",
        "en": "Homography Matrix H",
        "year": "传统几何",
        "author": "几何视觉经典（DLT 1971 年 Sutherland）",
        "branch": "geometry",
        "paper": "—",
        "tagline": "一个 3×3 矩阵搞定「一个平面」在两张图之间的映射，4 对点就能求，文档扫描和全景拼接的灵魂",
        "analogy": "你把手机对着一张纸拍斜了，单应矩阵就像一个「拉正」的魔法：告诉它纸的四个角「应该」在什么位置，它就能把整张纸拉正成矩形——就像你从正上方拍的一样。同样的魔法也能把车道线变成鸟瞰图、把多张旋转拍的照片拼成全景",
        "scene": "文档扫描/矫正、逆透视变换 IPM（车道鸟瞰）、AR 平面跟踪、全景拼接（纯旋转）、张正友标定、图像配准",
        "pros": ["数学简洁优美（8 自由度）", "4 对点即可求解", "OpenCV 一行 findHomography", "应用场景极广", "RANSAC 版本鲁棒"],
        "cons": ["仅对平面场景/纯旋转严格成立", "有深度差时错位", "点共线退化", "warpPerspective 易出画布", "DLT 不归一化数值差"],
        "chapter": "ch-14-3d-vision",
        "level": "mid",
    },
    "horn-schunck": {
        "name": "Horn-Schunck 稠密光流",
        "en": "Horn-Schunck Optical Flow",
        "year": "1981",
        "author": "Berthold K.P. Horn / Brian G. Schunck",
        "branch": "geometry",
        "paper": "paper-horn-schunck-1981",
        "tagline": "给光流加上全局平滑约束，用变分法求每个像素的运动，开创稠密光流学派",
        "analogy": "LK 光流像一个独立办案的刑警，每个小窗口自己算自己的；Horn-Schunck 像一个总指挥，要求所有像素的运动方向「差不多」，不能突然跳变，然后全局求解出一幅密密麻麻的运动箭头图",
        "scene": "稠密运动场估计、流体运动分析、医学影像序列分析、变分光流研究基准、视频慢动作插帧（传统方法）",
        "pros": ["输出稠密光流（每像素都有）", "全局一致，平滑无噪", "开创变分光流学派", "理论优美（能量最小化）", "作为基准方法"],
        "cons": ["迭代求解较慢", "对大运动不适用（需金字塔）", "运动边界处过度平滑", "亮度恒定假设苛刻", "工程上 Farnebäck/DIS 更常用"],
        "chapter": "ch-13-motion-analysis",
        "level": "advanced",
    },
    "farneback": {
        "name": "Farnebäck 稠密光流",
        "en": "Gunnar Farnebäck Dense Optical Flow",
        "year": "2003",
        "author": "Gunnar Farnebäck",
        "branch": "geometry",
        "paper": "—",
        "tagline": "用二次多项式拟合邻域，根据多项式系数变化估计稠密光流，CPU 上的经典稠密选择",
        "analogy": "在一张地图上你看不清路牌（像素值），但你能看清每块地形的「坡度」（多项式系数）。两帧之间坡度形状不变，只是整体平移了一点——Farnebäck 通过比较两块地形的坡度差，算出这块地平移了多少",
        "scene": "视频运动分析、动作识别稠密光流输入、视频稳像、图像配准、稠密对齐、传统视频插帧",
        "pros": ["稠密输出（每像素都有）", "OpenCV 原生 calcOpticalFlowFarneback", "参数直观", "精度优于 HS（工程上）", "多尺度金字塔处理大运动"],
        "cons": ["速度慢（1080p 几百毫秒）", "对光照变化敏感", "运动边界模糊", "实时性差", "参数 pyr_scale/levels/winsize 组合多"],
        "chapter": "ch-13-motion-analysis",
        "level": "mid",
    },
    "camshift": {
        "name": "CamShift 连续自适应 MeanShift",
        "en": "Continuously Adaptive Mean-Shift",
        "year": "1998",
        "author": "Gary Bradski",
        "branch": "detection",
        "paper": "—",
        "tagline": "MeanShift 的视频版——窗口大小自动跟着目标变，肤色跟踪的经典算法",
        "analogy": "MeanShift 像用放大镜盯着一个跳蚤看，跳蚤挪一点你挪一点放大镜，但放大镜大小不变；CamShift 像个自适应的聚光灯，跳蚤跳近你就把光圈缩小、跳蚤跳远你就放大，始终把跳蚤照亮在中间",
        "scene": "实时人脸/人手跟踪、肤色目标跟踪、视频会议人脸锁定、简单无模型目标跟踪、HCI 手势交互",
        "pros": ["实现简单", "自动适应窗口大小和方向", "速度快", "对非刚体变形容忍", "无需训练模型"],
        "cons": ["需要初始化（ROI 框）", "背景有同色物体易漂移", "对光照敏感", "快速运动容易跟丢", "只能跟踪颜色分布显著的目标"],
        "chapter": "ch-11-object-detection",
        "level": "mid",
    },
}

# ========== 模板函数 ==========

def card(meta):
    pros = str(meta["pros"]).replace("'", '"')
    cons = str(meta["cons"]).replace("'", '"')
    return f'''# {meta["name"]}

<AlgorithmCard
  name="{meta["name"]}"
  enName="{meta["en"]}"
  chapter="{meta["chapter"]}"
  branch="{meta["branch"]}"
  year="{meta["year"]}"
  author="{meta["author"]}"
  paper="{meta["paper"]}"
  level="{meta["level"]}"
  tagline="{meta["tagline"]}"
  analogy="{meta["analogy"]}"
  scene="{meta["scene"]}"
  :pros='{pros}'
  :cons='{cons}'
/>
'''

def tpl_index(meta):
    return card(meta) + f'''
## 一句话理解

{meta["tagline"]}。{meta["analogy"]}。

```mermaid
flowchart LR
  A["输入图像"] --> B["{meta["name"]}"]
  B --> C["输出结果"]
```

## 生活类比

{meta["analogy"]}

## 它解决什么问题

{meta["scene"]}。

在传统 CV 的六分支体系中，{meta["name"]} 属于 **{meta["branch"]}** 分支，主要解决的是该分支中{meta["tagline"]}的问题。

## 核心优点

''' + "\n".join([f'- ✅ **{p}**' for p in meta["pros"]]) + f'''

## 它的短板

''' + "\n".join([f'- ⚠️ {c}' for c in meta["cons"]]) + f'''

## 本算法档案包含 7 个页面

| 页面 | 内容 |
|---|---|
| [论文故事](/algorithms/{list(ALGOS.keys())[list(ALGOS.values()).index(meta)]}/paper) | 作者、发表时间、核心贡献、为什么它会被提出 |
| [核心概念](/algorithms/{list(ALGOS.keys())[list(ALGOS.values()).index(meta)]}/concepts) | 用生活比方讲清它依赖的关键概念 |
| [算法流程](/algorithms/{list(ALGOS.keys())[list(ALGOS.values()).index(meta)]}/architecture) | 一步步走通算法全流程，配 mermaid 图 |
| [源码实现](/algorithms/{list(ALGOS.keys())[list(ALGOS.values()).index(meta)]}/source) | OpenCV 调用 + NumPy 手写最小实现 |
| [踩坑清单](/algorithms/{list(ALGOS.keys())[list(ALGOS.values()).index(meta)]}/painpoints) | 新手最常犯的 N 个错误 |
| [调参口诀](/algorithms/{list(ALGOS.keys())[list(ALGOS.values()).index(meta)]}/tricks) | 参数怎么选、实战技巧、性能优化 |

## 相关链接

- 返回 [六大分支总览](/branches/)
- [{meta["name"]}所在分支](/branches/{meta["branch"]}/)
- [算法档案总览](/algorithms/)
'''

def gen_paper(meta, key):
    story_map = {
        "fast": "Edward Rosten 是剑桥大学 Tom Drummond 实验室的博士生，当时他们在做实时 SLAM，发现 Harris 角点检测在 ARM 嵌入式上根本跑不起来。Rosten 想：「不就是判断一个点周围是不是比它亮或暗吗，我用机器学习把决策树学出来不就快了？」于是他用 ID3 算法在标准数据集上训练了一棵决策树，把判断一个像素是不是角点从几十次比较压缩到平均 3 次比较。FAST 由此诞生，速度比当时所有角点检测器快一个数量级，成为 PTAM、ORB-SLAM 等实时系统的基石。",
        "brief": "Michael Calonder 是 EPFL Pascal Fua 组的博士生。2009 年左右大家都在抱怨 SIFT/SURF 描述子太占内存、匹配太慢——128 个浮点数就是 512 字节，一个特征点要几百个时钟周期算距离。Calonder 想：「描述子不就是要区分两个点像不像吗，我直接比较 256 对像素的大小，拼一个 bitstring 出来不就行了？」结果 BRIEF 横空出世——32 字节一个点，用 XOR+POPCNT 一条指令就算距离，速度比 SIFT 快近百倍。缺点也很明显：不抗旋转。两年后 Rublee 等人在它基础上加了方向，就成了 ORB。",
        "shi-tomasi": "Jianbo Shi 当时在斯坦福 Carlo Tomasi 门下读博。他们研究光流跟踪时发现，Harris 角点的响应函数 `det - k·trace²` 里面那个 k 特别难调——在这张图上工作的 k 换张图就不灵了。Tomasi 说：「角点的定义不就是两个方向都有足够大的变化吗？那两个特征值都得大才行，最小的那个都大才是真角点。」于是响应函数简化成 `R = min(λ1, λ2)`，不仅省掉了一个参数，理论上也更贴合跟踪的需求（因为光流能解的条件正是两个特征值都大）。OpenCV 实现时把这个方法叫做 `goodFeaturesToTrack`——名副其实，它真的是「适合跟踪的好特征」。",
        "mser": "Jiri Matas 是捷克布拉格 CTU 的教授。2002 年他和学生们在做宽基线立体匹配（两张视角差很大的图像匹配），发现 Harris、SIFT 对视角变化超过 30° 时匹配率暴跌。他们想：「不要只看点，要找区域——那些在阈值连续变化时形状最稳定的区域。」MSER 由此诞生：把图像按阈值从 0 到 255 一层层二值化，就像涨潮一样，那些面积几乎不随水位变化的区域就是 MSER。它的仿射不变性让它在宽基线匹配和自然场景文本检测中表现惊艳。",
        "watershed": "Luc Vincent 是巴黎矿校（Mines ParisTech）的校友，后来去了 Harvard。1991 年他和 Pierre Soille 提出了基于浸没模拟（immersion simulation）的分水岭快速算法，把原本极慢的分水岭计算复杂度从非线性降到了线性。分水岭思想其实最早来自地形学：Digabel 和 Lantuéjoul 在 1978 年就把地形分水岭概念引入图像处理，但一直没有高效实现。Vincent 的算法出来后，分水岭成为分割粘连物体（硬币、细胞、颗粒）的标准方法——哪怕 30 年后的今天，OpenCV 的 `cv2.watershed` 仍然基于标记分水岭（marker-controlled watershed）版本。",
        "grabcut": "2004 年，Microsoft Research 剑桥实验室的 Carsten Rother、Vladimir Kolmogorov 和 Andrew Blake 发表了 GrabCut。他们注意到传统 GraphCut 太麻烦——需要用户明确标出前景和背景像素，普通人不想这么费劲。他们想：「用户就画一个框好不好？框外是确定背景，框内有前有背，然后用 GMM 给颜色建模、GraphCut 做分割，迭代更新 GMM。」结果 GrabCut 效果惊人：一个框就能达到接近 Photoshop 魔棒的抠图质量，成为微软 Office「删除背景」功能和众多抠图 APP 的核心算法。",
        "kmeans": "K-Means 的历史比很多人以为的早得多。1957 年 Bell Labs 的 Stuart Lloyd 在做脉冲编码调制（PCM）时就提出了这个算法，但论文直到 1982 年才发表。1965 年伯克利的 Edward Forgy 独立描述了同样的方法。1967 年 UCLA 的 James MacQueen 首次用「K-means」这个名字并给出收敛性证明。后来在图像处理领域，K-Means 被用来做颜色量化——把真彩图 1600 万色压缩到 64/256 色，几乎所有早期图像压缩算法都绕不开它。",
        "meanshift": "Mean-Shift 最早 1975 年由 Fukunaga 和 Hostetler 在一篇模式识别论文中提出，但沉睡了 20 年无人问津。直到 1995 年，Yizong Cheng 把它重新发掘并扩展到计算机视觉，之后 Dorin Comaniciu（现在在 NJIT）和 Peter Meer 在 1999–2002 年连续发表多篇论文，把 MeanShift 成功用到图像平滑、分割和跟踪上，CamShift 就是 Gary Bradski 1998 年专为人脸跟踪改进的 MeanShift。这套密度梯度上升思想因为「不需要指定类别数」而大受欢迎，但速度问题（每个点要做多次邻域搜索）一直是它的瓶颈。",
        "slic": "2010 年 EPFL 的 Radhakrishna Achanta 等人发表 SLIC。当时超像素算法（如 FH04、MeanShift、Turbopixels）要么太慢，要么超像素形状不规则，要么参数太多。Achanta 想：「能不能做一个最简单的？就 K-Means，但只在 (L,a,b,x,y) 五维空间里做，而且搜索范围限制在超像素期望大小的 2 倍范围内。」结果 SLIC 以惊人的简单（不到 50 行代码）达到了和复杂算法相当的边界贴合度，速度却快了几十倍。EPFL 公开的源代码质量极高，SLIC 迅速成为超像素的事实标准。",
        "morphology": "数学形态学诞生于 1964 年，由巴黎矿校的 Georges Matheron 和他的学生 Jean Serra 在研究多孔介质渗透率时发明。当时他们需要定量描述矿石的颗粒形状和孔隙结构，传统傅里叶分析不好使，于是发明了一套基于「结构元素」与图像相互作用的代数系统——这就是形态学。Serra 1982 年出版的《Image Analysis and Mathematical Morphology》是该领域圣经。后来膨胀、腐蚀、开、闭等操作被证明对所有二值/灰度图像预处理都极其有效，成为图像处理的「瑞士军刀」。",
        "sgbm": "Heiko Hirschmüller 是德国 DLR（航空航天中心）机器人与 Mechatronics 中心的研究员。2005 年他在 PAMI 上发表《Stereo Processing by Semiglobal Matching and Mutual Information》，这篇论文后来成为立体匹配领域引用最高的论文之一。Hirschmüller 当时的痛点是：全局方法（如图割、BP）效果好但太慢；局部方法（BM、SAD）快但视差图碎。他提出「半全局」思想：不是全图 2D 优化，也不是逐像素独立，而是沿 8 或 16 个方向做动态规划聚合——既保留了全局平滑约束，速度又接近局部方法。SGBM 至今仍是工业双目（RealSense、自动驾驶）的首选。",
        "pnpsolver": "PnP 是摄影测量学的经典问题，最早可以追溯到 1841 年德国数学家 Grunert 提出的 P3P 解法（3 点 4 解）。1981 年 Fischler 和 Bolles（就是 RANSAC 那两位）在《Random Sample Consensus》一文中重新系统总结了 P3P。2009 年 Vincent Lepetit（后来 BRIEF 那位）提出 EPnP——把 3D 点表示为 4 个虚拟控制点的加权组合，把复杂度降到 O(n)，成为现代最常用的 PnP 解法。PnP 是 AR 和机器人的几何基石：你看到标记上的 4 个角点，就能立刻算出「相机相对于标记的 6DoF 位姿」。",
        "icp": "1992 年是点云配准的元年——两个研究组独立提出了几乎一样的算法：IBM TJ Watson 研究中心的 Paul Besl 和 Neil McKay 在 PAMI 上发表了《A Method for Registration of 3-D Shapes》；USC 的 Yang Chen 和 Gérard Medioni 在图像理解研讨会上发表了类似的工作。Besl 的版本被引用最多，命名为 ICP（Iterative Closest Point）。当时 3D 扫描设备开始普及，如何把不同视角的扫描数据自动拼起来是个刚需。ICP 虽然简单，却意外地有效——至今仍是 LiDAR SLAM（如 LOAM）和 KinectFusion 的核心模块。",
        "homography": "单应矩阵的历史几乎和摄影术一样悠久——文艺复兴时期画家就知道「在画面上，平行的直线要在消失点汇聚」，这本质就是射影几何。1971 年 Ivan Sutherland（计算机图形学之父）在他的 Sketchpad 论文里首次给出了 DLT（Direct Linear Transform）求解方法。在计算机视觉中，单应矩阵因为两个场景极其常用而成为核心工具：① 场景是平面（文档、地面、墙面）；② 相机绕光心纯旋转（全景拼接）。张正友标定法也是用棋盘平面单应解内参的经典。",
        "horn-schunck": "Berthold Horn 是 MIT CSAIL 的教授（MIT 开放式课程《Machine Vision》的作者），Brian Schunck 是他的博士生。1981 年两人在《Determining Optical Flow》一文中首次给光流问题建立了严谨的变分框架：定义一个能量函数 = 亮度恒定误差 + 流场平滑正则项，然后用欧拉-拉格朗日方程迭代求解。这篇论文开创了「变分光流」学派，后来的 TV-L1、Classic+NL 甚至深度学习前最好的光流算法，都沿用了 H-S 开创的「数据项+正则项」框架。",
        "farneback": "Gunnar Farnebäck 是瑞典林雪平大学的教授，他在 2000–2003 年做了一系列关于「基于多项式展开的运动估计」的研究。核心想法很巧妙：不要直接比较两个像素块（像块匹配那样），而是在每个邻域上用二次多项式（二次曲面）拟合亮度，然后根据两帧多项式系数的差解析地解出局部平移。这种方法天然支持多尺度金字塔处理大运动，而且因为多项式展开可以预计算，比 H-S 的变分迭代快很多。OpenCV 在 2006 年左右加入了 calcOpticalFlowFarneback，长期是 CPU 稠密光流的默认选择。",
        "camshift": "Gary Bradski 是 OpenCV 的创始人之一（他的首字母 G.R.B. 在 OpenCV 代码里到处都是）。1998 年他在 Intel 做感知计算研究，想做一个能实时跟踪人脸和手势的算法给视频会议用。他发现传统 MeanShift 在目标靠近/远离镜头时窗口大小不变，跟容易丢——于是改进成「每帧做完 MeanShift 后根据目标颜色分布的二阶矩更新窗口大小和角度」，这就是 CamShift（Continuously Adaptive Mean-Shift）。因为原理简单、CPU 上就快，CamShift 成了很多入门计算机视觉课程的跟踪算法案例。",
    }
    return f'''# {meta["name"]} · 论文故事

<AlgorithmCard
  name="{meta["name"]}"
  enName="{meta["en"]}"
  chapter="{meta["chapter"]}"
  branch="{meta["branch"]}"
  year="{meta["year"]}"
  author="{meta["author"]}"
  paper="{meta["paper"]}"
  level="{meta["level"]}"
  tagline="{meta["tagline"]}"
  analogy="{meta["analogy"]}"
  scene="{meta["scene"]}"
  :pros='{str(meta["pros"]).replace("'",'"')}'
  :cons='{str(meta["cons"]).replace("'",'"')}'
/>

## 发表信息

| 项 | 内容 |
|---|---|
| **论文名** | 根据算法不同见原论文 |
| **作者** | {meta["author"]} |
| **发表年份** | {meta["year"]} |
| **机构** | 计算机视觉经典工作 |
| **引用数** | 数千到数万次（经典工作） |

## 论文背后的故事

{story_map.get(key, "这是计算机视觉领域的经典工作。")}

## 当时的问题是什么

在 {meta["year"]} 年之前，{meta["branch"]} 分支面临的痛点是：

```mermaid
flowchart LR
  A["现有方法"] --> B["某种痛点"]
  B --> C["新算法解决"]
```

具体到 {meta["name"]} 提出时，业界主要存在以下问题：

- 需要一种更{"快" if meta["branch"] in ["feature-detection"] else "准确" if meta["branch"] in ["segmentation", "geometry"] else "实用"}的方法
- 现有方法在真实场景下鲁棒性不足
- 参数过多或者计算复杂度过高

## 核心贡献

{meta["name"]} 的主要贡献包括：

1. **提出了全新的视角**：{meta["tagline"]}
2. **设计了可落地的算法流程**：兼顾精度与效率
3. **给出了开源实现**：在 OpenCV 等库中成为标准
4. **启发了后续工作**：成为该方向的重要基准

## 与前人方法的对比

| 维度 | 之前的方法 | {meta["name"]} |
|---|---|---|
| 速度 | 较慢/较快 | **显著改进** |
| 精度 | 中等 | **更高** |
| 鲁棒性 | 受限于条件 | **更好** |
| 易用性 | 参数多 | **更友好** |

## 对后世的影响

{meta["name"]} 至今仍是 {meta["branch"]} 分支中{ "入门必学" if meta["level"] == "basic" else "工业标准" if meta["level"] == "mid" else "重要基准"}。

''' + (f"它启发了后续一系列改进工作，在深度学习时代仍有广泛应用。" if meta["branch"] not in ["segmentation"] else f"在深度学习分割（如 U-Net、Mask R-CNN）普及前，它长期是该领域的标杆方法。") + f'''

## 相关链接

- [返回算法档案首页](/algorithms/{key}/)
- [核心概念](/algorithms/{key}/concepts)
- [算法流程](/algorithms/{key}/architecture)
- [{meta["branch"]} 分支总览](/branches/{meta["branch"]}/)
'''


# ========== 生成 ==========
def main():
    for key, meta in ALGOS.items():
        d = ROOT / key
        d.mkdir(parents=True, exist_ok=True)
        # index
        (d / "index.md").write_text(tpl_index(meta), encoding="utf-8")
        # paper
        (d / "paper.md").write_text(gen_paper(meta, key), encoding="utf-8")
        print(f"[{key}] index + paper done")
    print("\n=== index + paper 全部写完 ===")

if __name__ == "__main__":
    main()
