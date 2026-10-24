#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第三批续：homography, horn-schunck, farneback, camshift"""
import sys
sys.path.insert(0, "/home/user/workspace/7648064683708846935/agent-cv")
from generate_algos3 import build_algo

build_algo(
    "homography",
    meta=dict(
        name="单应矩阵", en="Homography Matrix H",
        branch="geometry", year="传统几何", author="射影几何经典",
        chapter="ch-14-3d-vision", level="mid",
        tagline="一个 3×3 矩阵搞定「一个平面」在两张图之间的映射，4 对点就能求，文档扫描和全景拼接的灵魂",
        analogy="你把手机对着一张纸拍斜了，单应矩阵就像一个拉正的魔法：告诉它纸的四个角应该在什么位置，它就能把整张纸拉正成矩形——就像你从正上方拍的一样",
        scene="文档扫描/矫正、逆透视变换 IPM（车道鸟瞰）、AR 平面跟踪、全景拼接（纯旋转）、张正友标定、图像配准",
        pros=["数学简洁(8自由度)","4对点可求","OpenCV一行findHomography","应用极广","RANSAC鲁棒"],
        cons=["仅平面/纯旋转成立","有深度差时错位","点共线退化","warpPerspective易出画布","DLT需归一化"]),
    concepts=[
        ("单应关系",
         "如果两张图对应的是**同一平面**（墙面、纸张、地面），或者相机做**纯旋转**（绕光心），那么图 1 和图 2 之间的点对满足 p' ≅ H·p，其中 H 是 3×3 矩阵（8 自由度，因为尺度等价），≅ 是齐次等比关系。",
         "flowchart LR\n  A[\"图 1 上的点 p\"] -->|\"p' ≅ H p\"| B[\"图 2 上的点 p'\"]\n  C[\"平面场景/纯旋转\"] --> A\n  C --> B"),
        ("齐次坐标",
         "单应在齐次坐标下是线性的。2D 像素 (x,y) 写成 3 维齐次向量 (x,y,1)，H 乘完得到 (wx',wy',w)，除以 w 得到真实坐标 (x',y')。所以 H 有 9 个元素但只有 8 个自由度（整体缩放等价）。",
         None),
        ("DLT（直接线性变换）",
         "每对点对给出 2 个方程，4 对点（8 个方程）解 8 个未知量。实际用更多点 + SVD 求最小二乘解。归一化 DLT（先对点做平移缩放归一化）数值稳定得多。",
         None),
        ("适用场景的两个条件",
         "H 严格成立只有两种情况：① 场景是平面（所有点在一个平面上）；② 相机绕光心纯旋转（无平移）。一旦有深度差或平移平移，用 H 映射会产生视差错位。",
         None),
    ],
    arch_steps=[
        ("检测匹配特征点", "SIFT/ORB 检测 + BFMatcher 匹配 + Lowe ratio test"),
        ("RANSAC 求 H", "cv2.findHomography(pts1, pts2, RANSAC, 5.0) 返回 H 和内点 mask"),
        ("分解验证", "可选：分解 H 得到法向量 n 和距离 d（多解，需消歧）"),
        ("warpPerspective", "用 H 把图 1 变换到图 2 坐标系（或反过来）"),
        ("边界处理", "自动计算 warp 后的画布大小和偏移，避免图像被截断"),
    ],
    opencv='''# 文档矫正：四个角点拉正为矩形
img = cv2.imread("doc.jpg")
h, w = 500, 400   # 目标矩形
pts_src = np.array([[120,30],[580,50],[560,470],[100,460]], dtype=np.float32)  # 文档四角
pts_dst = np.array([[0,0],[w,0],[w,h],[0,h]], dtype=np.float32)
H = cv2.getPerspectiveTransform(pts_src, pts_dst)
doc = cv2.warpPerspective(img, H, (w, h))
cv2.imwrite("doc_rectified.jpg", doc)

# 图像配准 + RANSAC
# 假设 kp1/kp2/des1/des2 是 ORB 检测结果
bf = cv2.BFMatcher(cv2.NORM_HAMMING)
matches = bf.knnMatch(des1, des2, k=2)
good = [m for m,n in matches if m.distance<0.75*n.distance]
pts1 = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
pts2 = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
H, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 5.0)
aligned = cv2.warpPerspective(img1, H, (img2.shape[1], img2.shape[0]))''',
    numpy_impl='''def homography_dlt(pts1, pts2):
    """直接线性变换求单应矩阵（pts1, pts2: Nx2, N>=4）"""
    n = len(pts1)
    A = []
    for i in range(n):
        x, y = pts1[i]; xp, yp = pts2[i]
        A.append([-x,-y,-1,0,0,0, x*xp,y*xp,xp])
        A.append([0,0,0,-x,-y,-1, x*yp,y*yp,yp])
    A = np.array(A)
    _, _, Vt = np.linalg.svd(A)
    H = Vt[-1].reshape(3,3)
    return H / H[2,2]''',
    pitfalls=[
        ("以为任何情况都能用 H 配准", "两张图拍的是 3D 场景（非平面），有平移时 warp 后近处歪了。",
         "H **只对平面/纯旋转严格成立**。3D 场景有视差时必须用基础矩阵 F 或三维重建。"),
        ("warpPerspective 之后图像被裁", "直接用原图尺寸 warp，图跑到画面外。",
         "计算 H 后的四个新角点，取最小最大坐标决定新画布大小，然后加平移矩阵。"),
        ("findHomography 不用 RANSAC", "有几个误匹配时 H 完全错。",
         "**永远用 cv2.RANSAC**，阈值 3–5 像素。"),
        ("点共线退化", "4 个点都在一条线上，H 矩阵解不出来。",
         "选 4 个点要**四个角、不共线、尽量分散**。"),
        ("齐次坐标 w 被忽略", "手算 H·p 时忘了除以第三维 w，结果坐标错。",
         "OpenCV warpPerspective 内部做了齐次归一化；自己算时记得除以最后一维。"),
    ],
    koujue="""平面或是纯旋转，单应矩阵才成立；
四个点对就能解，RANSAC 抗错配；
warpPerspective 拉正图，文档扫描全靠它；
DLT 求 H 用 SVD，记得归一化数值更稳；
点不共线分散排，一条直线求不出来；
IPM 逆透视车道鸟瞰，张正友标定每步都用它。""",
    params=[
        ("ransacReprojThreshold", "RANSAC 重投影阈值(px)", "5.0", "严", "宽松"),
        ("method", "求解方法", "RANSAC", "—", "—"),
    ],
    tips=[
        ("文档扫描自动检测四角",
         "```python\n# 找最大四边形做文档角点\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\ncanny = cv2.Canny(cv2.GaussianBlur(gray,(5,5),0), 30, 100)\ncnt = max(cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0], key=cv2.contourArea)\neps = 0.02*cv2.arcLength(cnt, True)\napprox = cv2.approxPolyDP(cnt, eps, True)\n# approx 4个点即四角\n```"),
        ("IPM 逆透视（车道鸟瞰）",
         "预先标定好地面的 4 个点（路面上已知间距的梯形），求 H 映射到俯视矩形，即可做车道线检测。"),
        ("全景拼接",
         "相机绕光心旋转拍摄多张照片，相邻两张用 H 拼接即可（OpenCV Stitcher 自动处理）。"),
    ],
    perf=[
        ("findHomography RANSAC (100点)", "< 5 ms", "CPU"),
        ("warpPerspective", "~5 ms/MPix", "CPU"),
    ],
    notes=""
)

build_algo(
    "horn-schunck",
    meta=dict(
        name="Horn-Schunck 稠密光流", en="Horn-Schunck Optical Flow",
        branch="geometry", year="1981", author="Berthold Horn / Brian Schunck",
        chapter="ch-13-motion-analysis", level="advanced", paper="paper-horn-schunck-1981",
        tagline="给光流加全局平滑约束，用变分法求每个像素运动，开创稠密光流学派",
        analogy="LK 光流像独立办案的刑警，每个小窗口自己算自己的；Horn-Schunck 像一个总指挥，要求所有像素运动方向差不多，全局求解出密密麻麻的运动箭头图",
        scene="稠密运动场估计、流体运动分析、医学影像序列、变分光流研究基准、视频慢动作插帧（传统方法）",
        pros=["稠密输出(每像素)","全局一致平滑","变分学派开创者","理论优美","基准方法"],
        cons=["迭代慢","大运动不适用(需金字塔)","运动边界过度平滑","亮度恒定假设苛刻","工程上Farneback/DIS更常用"]),
    concepts=[
        ("亮度恒定+小运动+空间平滑",
         "同一点亮度不变 I(x,y,t)=I(x+u,y+v,t+1)，小运动允许泰勒展开 I_x·u+I_y·v+I_t=0，空间平滑要求相邻像素 (u,v) 差不多。",
         None),
        ("能量函数",
         "HS 定义能量：$E = \\int\\int (I_x u+I_y v+I_t)^2 + \\alpha^2(||\\nabla u||^2 + ||\\nabla v||^2) dxdy$。第一项是亮度恒定误差（数据项），第二项是平滑约束（正则项），α 控制平滑强度。",
         None),
        ("欧拉-拉格朗日方程",
         "对能量函数求变分等于零，得到两个耦合的偏微分方程，用迭代方法（高斯-赛德尔迭代）求解：$u^{k+1}=\\bar{u}^k - I_x(I_x\\bar{u}^k+I_y\\bar{v}^k+I_t)/(α²+I_x²+I_y²)$，v 类似。",
         "flowchart TB\n  A[\"初始化 u=0,v=0\"] --> B[\"算 Ix,Iy,It\"]\n  B --> C[\"计算 u,v 的邻域均值\"]\n  C --> D[\"高斯-赛德尔迭代更新 u,v\"]\n  D -->|\"未收敛\"| C\n  D -->|\"收敛\"| E[\"稠密光流场 (u,v) ✅\"]"),
        ("α 参数",
         "α 越大，平滑项权重越大，光流越平滑但边界越糊；α 越小，数据项主导，光流越锐利但越噪。α² 取 100（α=10）左右是常见选择。",
         None),
        ("与 LK 的区别",
         "LK 是局部方法（窗口内常数流），HS 是全局方法（全图平滑）；LK 产稀疏流（只在角点），HS 产稠密流（每像素）；LK 线性方程直接解，HS 迭代求解。",
         None),
    ],
    arch_steps=[
        ("图像预处理", "转为浮点、高斯平滑去噪"),
        ("时空梯度", "Ix=∂I/∂x, Iy=∂I/∂y（Sobel）, It=I_t+1 - I_t（帧差）"),
        ("初始化", "u=0, v=0 全图"),
        ("迭代更新", "反复做 u,v 的高斯-赛德尔更新（上百次）"),
        ("多尺度金字塔（可选）", "为处理大运动，构建图像金字塔从粗到细做 warp 迭代"),
    ],
    opencv='''# OpenCV 主模块无直接 HS API，可用 cv2.calcOpticalFlowFarneback（同属稠密光流）
# 下面用 scipy/手写实现（教学演示）
import cv2, numpy as np
def horn_schunck(I1, I2, alpha=10, n_iter=100):
    I1 = I1.astype(np.float32)/255
    I2 = I2.astype(np.float32)/255
    # 时空梯度
    Ix = cv2.Sobel(I1, cv2.CV_32F, 1, 0, ksize=3) / 8
    Iy = cv2.Sobel(I1, cv2.CV_32F, 0, 1, ksize=3) / 8
    It = cv2.GaussianBlur(I2-I1, (3,3), 1)
    u = np.zeros_like(I1); v = np.zeros_like(I1)
    k = np.array([[1,1,1],[1,0,1],[1,1,1]], np.float32)/8
    a2 = alpha*alpha
    for _ in range(n_iter):
        u_avg = cv2.filter2D(u, -1, k)
        v_avg = cv2.filter2D(v, -1, k)
        num = Ix*u_avg + Iy*v_avg + It
        den = a2 + Ix*Ix + Iy*Iy
        u = u_avg - Ix*num/den
        v = v_avg - Iy*num/den
    return u, v
img1 = cv2.imread("f1.jpg", 0); img2 = cv2.imread("f2.jpg", 0)
u, v = horn_schunck(img1, img2, alpha=10, n_iter=200)
# 可视化 HSV 色轮
mag, ang = cv2.cartToPolar(u, v)
hsv = np.zeros((*img1.shape,3), np.uint8)
hsv[...,0] = ang*180/np.pi/2; hsv[...,1] = 255
hsv[...,2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
flow_rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
cv2.imwrite("hs_flow.jpg", flow_rgb)''',
    numpy_impl='''# 见上方 horn_schunck 函数（已为 numpy 实现）''',
    pitfalls=[
        ("直接用 HS 处理大运动", "物体移动超过 3–5 像素，结果完全是噪声。",
         "必须做**金字塔多尺度 coarse-to-fine**；或使用更鲁棒的算法（Farnebäck、DIS）。"),
        ("迭代次数不够", "n_iter=10 时光流还没收敛，结果很噪。",
         "单尺度 **n_iter=100–200**；多尺度每层 30–50 次。"),
        ("α 太小全是噪声", "α=1 时光流像麻点；α=100 过度平滑。",
         "典型 α=10–20；根据图像噪声调整。"),
        ("没做高斯预平滑", "梯度估计受噪声影响严重。",
         "梯度估计前先做 3×3 高斯平滑；或用 Sobel 核（自带平滑）。"),
    ],
    koujue="""alpha 十左右是默认，越大越平滑小越细；
迭代一百次起步，少了不收敛；
IxIy  Sobel 核除以八，It  是两帧差；
邻域平均用拉普拉斯核，高斯赛德尔迭代；
大运动一定要金字塔，不然结果全是瞎猜；
HS 是教学基准多，工程请用 Farneback 或 DIS。""",
    params=[
        ("alpha", "平滑强度", "10", "平滑", "保留细节"),
        ("n_iter", "迭代次数", "100", "收敛好", "快"),
        ("pyramid levels", "金字塔层数", "3", "处理大运动", "快"),
    ],
    tips=[
        ("HSV 色轮可视化",
         "色调=方向，饱和度=255，明度=幅度。这种可视化能一眼看出光流的方向和大小分布。"),
        ("稠密光流 vs 稀疏光流选择",
         "| 任务 | 选谁 |\n|---|---|\n| 跟踪目标位置 | LK 稀疏光流 |\n| 视频稳像 | LK 或 Farneback |\n| 动作识别输入 | Farneback 稠密 |\n| 变分光流研究 | HS/TV-L1 |\n| 实时 VO | 稀疏特征+LK |"),
    ],
    perf=[
        ("HS n_iter=100 (640×480)", "~3-5 s", "纯 Python，慢"),
        ("C++ 优化版", "~100 ms", "CPU"),
        ("Farneback (640×480)", "~200 ms", "OpenCV C++"),
    ],
    notes=""
)

build_algo(
    "farneback",
    meta=dict(
        name="Farnebäck 稠密光流", en="Gunnar Farnebäck Dense Optical Flow",
        branch="geometry", year="2003", author="Gunnar Farnebäck",
        chapter="ch-13-motion-analysis", level="mid",
        tagline="用二次多项式拟合邻域，根据多项式系数变化估计稠密光流，CPU 上的经典稠密选择",
        analogy="在一张地图上你看不清路牌（像素值），但你能看清每块地形的坡度（多项式系数）。两帧之间坡度形状不变，只是整体平移了一点——Farnebäck 通过比较两块地形的坡度差算出平移",
        scene="视频运动分析、动作识别稠密光流输入、视频稳像、图像配准、稠密对齐、传统视频插帧",
        pros=["稠密输出","OpenCV原生calcOpticalFlowFarneback","参数直观","精度优于HS(工程上)","多尺度金字塔"],
        cons=["速度慢(1080p几百ms)","光照敏感","运动边界模糊","实时性差","参数组合多"]),
    concepts=[
        ("多项式展开",
         "每个像素邻域（约 11×11）用**二次多项式**近似：$f(x) \\approx x^T A x + b^T x + c$，其中 A 是 2×2 对称矩阵（描述邻域曲面曲率），b 是 2×1 向量（梯度），c 是常数。",
         None),
        ("根据多项式系数变化求位移",
         "理想情况下，运动 d 会让多项式变换成可观测的形式，通过比较两帧的 A 和 b，能解析地解出每个像素的位移 d（d = -½A⁻¹(Δb)）。",
         "flowchart LR\n  A[\"帧 1: 邻域二次多项式(A1,b1)\"] --> C[\"多项式系数差 → 解析位移 d\"]\n  B[\"帧 2: 邻域二次多项式(A2,b2)\"] --> C\n  C --> D[\"稠密光流场 (u,v) ✅\"]"),
        ("多尺度金字塔 coarse-to-fine",
         "多项式展开假设小运动，直接用在大运动上失败。Farnebäck 构建高斯金字塔，从最粗层开始估计光流，上采样作为下一层先验——逐层精修。",
         None),
        ("邻域融合",
         "每个像素的位移估计会在邻域内做加权平均（用多项式拟合的确定性作为权重），增加鲁棒性。",
         None),
    ],
    arch_steps=[
        ("金字塔构建", "构建 n 层高斯金字塔，pyr_scale=0.5（每层缩小一半）"),
        ("多项式展开", "在每层每个像素邻域拟合二次多项式"),
        ("粗层估计", "在最粗层估计初始光流（假设为 0）"),
        ("上采样 warp", "光流上采样到下一层，对 I2 做 warp 补偿"),
        ("逐层精修", "每一层在 warp 后重新估计位移增量，累加到光流"),
        ("最终输出", "到最细层后输出每像素 (u,v)"),
    ],
    opencv='''prev = cv2.imread("f1.jpg", 0)
curr = cv2.imread("f2.jpg", 0)
flow = cv2.calcOpticalFlowFarneback(
    prev, curr, None,
    pyr_scale=0.5, levels=3, winsize=15,
    iterations=3, poly_n=5, poly_sigma=1.2, flags=0
)
# flow shape (h,w,2): flow[...,0]=u, flow[...,1]=v
mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
hsv = np.zeros((*prev.shape,3), np.uint8)
hsv[...,0] = ang*180/np.pi/2
hsv[...,1] = 255
hsv[...,2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
cv2.imwrite("farneback.jpg", rgb)''',
    numpy_impl='''# Farnebäck 多项式展开较复杂，这里给出调用接口与 HSV 可视化
# 工程直接用 cv2.calcOpticalFlowFarneback
# 如需手写需实现：高斯导数滤波 → 二次多项式拟合 → 邻域融合 → 多尺度 warp''',
    pitfalls=[
        ("winsize 太小", "winsize=5 噪声多；winsize=30 运动边界模糊。",
         "**winsize=15**（默认附近）；快速运动加大到 21–30。"),
        ("poly_n/poly_sigma 不匹配", "poly_n=5 时 sigma=1.1–1.2；poly_n=7 时 sigma=1.5。",
         "OpenCV 默认 poly_n=5, poly_sigma=1.2 是论文推荐组合，一般不用改。"),
        ("levels 太少处理不了大运动", "快速运动物体光流全错。",
         "levels=3 能处理到 8 像素位移；更大位移加 levels 到 5。"),
        ("把 Farneback 当实时用", "1080p 几百毫秒，没法 30fps。",
         "实时请用 `cv2.DISOpticalFlow_create()`（2016 年，4ms/帧）。"),
    ],
    koujue="""pyr_scale 零点五，每层缩一半；
levels 三是默认，大运动加到五；
winsize 十五起，大运动加大到二十一；
iterations 每层三，多加几次精度提升；
poly_n 五 sigma 一点二，默认组合论文推；
HSV 色轮可视化，色调表方向明度表大小；
要实时用 DIS，Dense Inverse Search 四毫秒一帧。""",
    params=[
        ("pyr_scale", "金字塔缩放比例", "0.5", "金字塔高", "精度高"),
        ("levels", "金字塔层数", "3", "处理大运动", "快"),
        ("winsize", "平均窗口大小", "15", "平滑鲁棒", "保留细节"),
        ("iterations", "每层迭代数", "3", "精", "快"),
        ("poly_n", "多项式邻域大小", "5", "—", "—"),
        ("poly_sigma", "多项式高斯 sigma", "1.2", "—", "—"),
    ],
    tips=[
        ("实时替代：DIS 光流",
         "```python\ndis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)\nflow = dis.calc(prev, curr, None)\n```\n速度提升 50–100 倍，精度略降。"),
        ("光流用于视频稳像",
         "估计帧间全局运动（取光流中位数作为相机运动），反向做仿射变换补偿即可。"),
        ("光流外点过滤",
         "用光流做跟踪时，对 mag 取阈值去掉过大位移（通常是遮挡或误匹配）。"),
    ],
    perf=[
        ("Farneback (640×480)", "~200 ms", "CPU C++"),
        ("Farneback (1920×1080)", "~1.5 s", "CPU"),
        ("DIS (640×480)", "~5 ms", "CPU"),
    ],
    notes=""
)

build_algo(
    "camshift",
    meta=dict(
        name="CamShift 连续自适应 MeanShift", en="Continuously Adaptive Mean-Shift",
        branch="detection", year="1998", author="Gary Bradski",
        chapter="ch-11-object-detection", level="mid",
        tagline="MeanShift 的视频版——窗口大小自动跟着目标变，肤色跟踪的经典算法",
        analogy="MeanShift 像用放大镜盯跳蚤，大小不变；CamShift 像自适应聚光灯，跳蚤跳近光圈小、跳远光圈大，始终把跳蚤照亮在中间",
        scene="实时人脸/人手跟踪、肤色目标跟踪、视频会议人脸锁定、简单无模型跟踪、HCI 手势交互",
        pros=["实现简单","自适应窗口大小","速度快","非刚体变形容忍","无需训练"],
        cons=["需初始化ROI","同色背景易漂移","光照敏感","快速运动易丢","只能跟踪颜色显著目标"]),
    concepts=[
        ("反向投影图 Back Projection",
         "先算目标 ROI 的颜色直方图（通常在 HSV 的 H 通道，即色调直方图），然后把整张图的每个像素替换为「它的颜色在目标直方图中出现的概率」——得到的就是反向投影图（越亮的像素越像目标颜色）。",
         "flowchart LR\n  A[\"ROI 目标区域\"] --> B[\"H 通道直方图\"]\n  C[\"全图\"] --> D[\"反向投影<br/>像素=该颜色的概率\"]\n  B --> D"),
        ("MeanShift 找峰值",
         "在反向投影图上，从初始窗口位置开始：① 算窗口内质心（0阶矩+1阶矩）；② 把窗口中心移到质心；③ 重复直到中心移动 < ε，收敛到密度峰值。",
         None),
        ("CamShift 自适应",
         "CamShift = 先跑 MeanShift 收敛，再根据窗口内 0/1/2 阶矩计算目标的新位置、大小和方向，把窗口更新为匹配目标的椭圆；然后下一帧用新窗口作为初始继续。",
         None),
        ("颜色空间选择",
         "用 HSV 的 H 通道（色调）做直方图，能部分抵抗光照变化（V 亮度不影响 H）。但要注意排除低饱和度像素（S 太小 H 不稳定）。",
         None),
    ],
    arch_steps=[
        ("初始化 ROI", "第一帧手动或检测（如人脸检测）给一个初始矩形窗口"),
        ("算目标直方图", "取 ROI 的 H 通道，做归一化直方图"),
        ("反向投影", "对当前帧做 calcBackProject 得到概率图"),
        ("MeanShift 迭代", "从当前窗口位置开始，移动到质心直到收敛"),
        ("更新窗口", "用 0/1/2 阶矩算新的中心、尺寸、方向"),
        ("下一帧", "用新窗口作为下一帧初始位置"),
    ],
    opencv='''cap = cv2.VideoCapture(0)
ret, frame = cap.read()
r, h, c, w = 200, 100, 300, 100   # 初始 ROI
track_window = (c, r, w, h)
roi = frame[r:r+h, c:c+w]
hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv_roi, np.array([0,60,32]), np.array([180,255,255]))
roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0,180])
cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
term = (cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT, 10, 1)
while True:
    ret, frame = cap.read()
    if not ret: break
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv], [0], roi_hist, [0,180], 1)
    ret, track_window = cv2.CamShift(dst, track_window, term)
    pts = cv2.boxPoints(ret).astype(int)
    cv2.polylines(frame, [pts], True, (0,0,255), 2)
    cv2.imshow("CamShift", frame)
    if cv2.waitKey(30)==27: break
cap.release(); cv2.destroyAllWindows()''',
    numpy_impl='''def meanshift_step(prob, window):
    """一次 MeanShift 更新"""
    x,y,w,h = window
    roi = prob[y:y+h, x:x+w]
    M00 = roi.sum()
    if M00 < 1e-6: return window, False
    ys, xs = np.indices(roi.shape)
    cx = x + (xs*roi).sum()/M00
    cy = y + (ys*roi).sum()/M00
    nw = (int(cx-w/2), int(cy-h/2), w, h)
    return nw, abs(nw[0]-x)+abs(nw[1]-y) > 1''',
    pitfalls=[
        ("不做低饱和度过滤", "肤色跟踪时头发、阴影这些低饱和度像素污染直方图，跟踪漂移到背景。",
         "建直方图时必须用 inRange **过滤 S<60 或 V<32 的像素**。"),
        ("H 通道 0–180 范围搞错", "calcHist 和 calcBackProject 范围用 0–255，直方图错位。",
         "OpenCV H 通道范围是 **0–179**，histSize=180, ranges=[0,180]。"),
        ("目标快速运动丢了跟不回来", "目标一帧移出窗口，CamShift 永远跟在空地方。",
         "CamShift 没有重检测机制。丢了要靠外部检测器重新初始化；或用**卡尔曼滤波**预测位置。"),
        ("背景有肤色物体干扰", "后面的人肤色被跟踪，窗口直接漂走。",
         "CamShift 只看颜色，没有其他信息。鲁棒方案是 **CamShift + 光流/边缘/运动检测** 多线索融合，或换 KCF/深度学习跟踪器。"),
        ("窗口大小不收敛", "窗口越来越大最终包住整个人。",
         "CamShift 大小受直方图影响，若背景颜色相似会扩散。实际工程要给窗口大小加 clamp（如最小 20×20、最大 300×300）。"),
    ],
    koujue="""颜色跟踪 HSV 通道，色调 H 建直方图；
低饱和暗像素先 mask 掉，S 六十 V 三十二起；
直方图归一化到零到二五五，反向投影才准确；
CamShift 返回旋转矩形，boxPoints 画出来才漂亮；
同色背景会漂移，多线索融合才牢靠；
丢了不会自动找回，配个检测器做初始化；
教学演示很拿手，产品级用 KCF 或深度跟踪。""",
    params=[
        ("histogram bins", "H 通道 bin 数", "180", "精细", "泛化"),
        ("termination maxCount", "MeanShift 最大迭代", "10", "精", "快"),
        ("termination epsilon", "收敛阈值(px)", "1", "精", "快"),
    ],
    tips=[
        ("肤色 HSV 范围",
         "不同种族肤色范围有差别，常用范围：\n```\nH: 0–20 (部分人 0–40)\nS: 60–255 (排除灰色)\nV: 32–255 (排除暗黑)\n```"),
        ("与 Kalman 滤波结合",
         "用 Kalman 预测目标位置作为 CamShift 初始窗口，抗快速运动和短暂遮挡，工业中常见组合。"),
        ("初始化自动人脸检测",
         "```python\nface_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')\nfaces = face_cascade.detectMultiScale(gray)\n# 取第一个人脸作为 track_window\n```"),
    ],
    perf=[
        ("CamShift 每帧", "~1 ms", "CPU，30fps+"),
    ],
    notes=""
)

print("homography, horn-schunck, farneback, camshift done")
