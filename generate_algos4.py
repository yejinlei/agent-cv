#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""剩余 15 个算法批量生成（在 generate_algos3.py 的 build_algo 基础上直接生成所有）"""
import sys
sys.path.insert(0, "/home/user/workspace/7648064683708846935/agent-cv")
from generate_algos3 import build_algo

# ===== shi-tomasi =====
build_algo(
    "shi-tomasi",
    meta=dict(
        name="Shi-Tomasi 角点 (GFTT)", en="Shi-Tomasi / Good Features to Track",
        branch="feature-detection", year="1994", author="Jianbo Shi / Carlo Tomasi",
        chapter="ch-8-local-feature", level="mid",
        tagline="把 Harris 响应函数换成 min(λ1,λ2)，一个参数不用调，工程界角点首选",
        analogy="Harris 像个老中医用「阴阳失调公式」判断亚健康，还要调一个神秘的 k；Shi-Tomasi 直接看你「最差的那一科成绩」——只要最差那一科也及格，你就是好学生",
        scene="光流跟踪（goodFeaturesToTrack+calcOpticalFlowPyrLK 是标配）、相机标定棋盘角点、视频稳像",
        pros=["无需调 k 参数","响应值物理意义明确","自带 minDistance 防扎堆","能限制 top-N 数量"],
        cons=["不具尺度/旋转不变","需要定 qualityLevel","分布不均时扎堆","不含描述子"]),
    concepts=[
        ("角点的数学条件",
         "Harris 在自相关矩阵 M 上定义响应 R=det(M)-k·trace(M)²，其中 k 是个 0.04–0.06 的经验值。Shi-Tomasi 观察发现：**角点的本质就是 M 的两个特征值都足够大**——那直接让 R = min(λ₁, λ₂) 不就行了？这样既不用调 k，响应值也有明确物理意义：较小的那个特征值代表「最弱方向上的纹理强度」。",
         "flowchart TB\n  A[\"自相关矩阵 M<br/>两个特征值 λ₁, λ₂\"] --> B{\"λ₁, λ₂ 都大?\"}\n  B -->|\"是\"| C[\"✅ 角点<br/>R = min(λ₁,λ₂) 大\"]\n  B -->|\"λ 一大一小\"| D[\"边缘\"]\n  B -->|\"都小\"| E[\"平坦\"]"),
        ("质量等级 qualityLevel",
         "OpenCV 的 `goodFeaturesToTrack` 不直接让你设阈值，而是让你给一个**比例**：`qualityLevel=0.01` 表示「只保留响应值 > 最强点响应×1% 的点」。这种设计自动适应图像对比度，不用手动调绝对阈值。",
         None),
        ("最小距离 minDistance",
         "角点扎堆是所有角点检测的通病。Shi-Tomasi 直接提供 `minDistance` 参数，保证返回的角点之间至少相隔这么多像素——按响应从强到弱依次选取，近距离弱响应点会被抑制。",
         None),
        ("为什么是光流首选",
         "LK 光流可解的条件是 $A^TA$ 可逆（即两个特征值都足够大），这**正好**就是 Shi-Tomasi 的判据！所以 Shi-Tomasi 角点就是天生为光流准备的——能被稳定跟踪的点。",
         None),
    ],
    arch_steps=[
        ("算梯度 Ix, Iy", "对整张图用 Sobel 算子算 x、y 方向梯度"),
        ("算自相关矩阵 M", "在 blockSize×blockSize 窗口内，用高斯加权求和 Ix², IxIy, Iy²"),
        ("算响应 R = min(λ₁,λ₂)", "不必真的求特征值，用公式可直接算较小特征值"),
        ("阈值化", "以最强响应 × qualityLevel 为阈值，低于阈值的点淘汰"),
        ("NMS + minDistance", "按响应降序遍历，距离已选点 < minDistance 的点剔除"),
        ("返回 top-N", "最多返回 maxCorners 个角点"),
    ],
    opencv='''img = cv2.imread("test.jpg", 0)
corners = cv2.goodFeaturesToTrack(
    img,
    maxCorners=200,        # 最多返回角点数
    qualityLevel=0.01,     # 质量等级（比例）
    minDistance=10,        # 最小间距（像素）
    blockSize=3,           # 邻域窗口大小
    useHarrisDetector=False,  # False=Shi-Tomasi；True=Harris
    k=0.04                 # Harris 时的 k，Shi-Tomasi 忽略
)
color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
for c in corners:
    x, y = c.ravel().astype(int)
    cv2.circle(color, (x, y), 3, (0,0,255), -1)
cv2.imwrite("shitomasi.jpg", color)
print(f"检测到 {len(corners)} 个角点")''',
    numpy_impl='''def shi_tomasi(img, max_corners=200, quality=0.01, min_dist=10, block=3):
    """简化版 Shi-Tomasi 角点检测"""
    # ① Sobel 梯度
    Ix = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    Iy = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
    Ixx = cv2.GaussianBlur(Ix*Ix, (block, block), 0)
    Ixy = cv2.GaussianBlur(Ix*Iy, (block, block), 0)
    Iyy = cv2.GaussianBlur(Iy*Iy, (block, block), 0)
    # ② 算 min(λ1,λ2)（用简化公式避免求特征值）
    # λ = (trace - sqrt(trace^2 - 4*det)) / 2
    trace = Ixx + Iyy
    det = Ixx * Iyy - Ixy * Ixy
    discriminant = np.maximum(trace*trace - 4*det, 0)
    lam_min = (trace - np.sqrt(discriminant)) / 2
    # ③ 阈值化
    thresh = lam_min.max() * quality
    candidates = np.argwhere(lam_min > thresh)
    # ④ 按响应降序，做 minDistance 抑制
    vals = lam_min[candidates[:,0], candidates[:,1]]
    order = np.argsort(-vals)
    kept = []
    for idx in order:
        y, x = candidates[idx]
        ok = True
        for (ky, kx) in kept:
            if (y-ky)**2 + (x-kx)**2 < min_dist**2:
                ok = False; break
        if ok:
            kept.append((y, x))
            if len(kept) >= max_corners:
                break
    return np.array(kept).reshape(-1, 1, 2).astype(np.float32)''',
    pitfalls=[
        ("qualityLevel 太高导致点太少", "qualityLevel=0.1 或更大时，弱纹理区域一个点都检测不到。",
         "默认从 **0.01** 起步；弱纹理/模糊图降到 0.005。"),
        ("minDistance 太小导致角点扎堆", "minDistance=3 时，一个角点周围能出 5、6 个点。",
         "光流跟踪建议 **10**；标定建议 20–30；想多点设为 5。"),
        ("直接拿 Shi-Tomasi 点做长时跟踪", "光流有累计漂移，跟踪 100 帧后点会跑到同一处。",
         "必须做 **前向后向一致性检验**，并每 20–30 帧重检测一次点。"),
        ("以为 Shi-Tomasi 有尺度不变", "图放大后点完全对不上。",
         "Shi-Tomasi 固定窗口，**没有尺度不变性**。多尺度场景用 SIFT/ORB。"),
        ("在强噪声图上直接检测", "噪声会被 Sobel 放大，出现大量假角点。",
         "检测前先高斯模糊（sigma=1）：`gray = cv2.GaussianBlur(gray, (3,3), 1.0)`。"),
        ("useHarrisDetector 参数理解错", "以为 True 时 Harris 更好；实际上光流场景 Shi-Tomasi 更合适。",
         "光流/跟踪永远用 `useHarrisDetector=False`（默认）。"),
    ],
    koujue="""最小特征值当判据，k 参数不再要；
quality 是比例不是值，百分之一是起点；
minDistance 十像素，跟踪标定都够用；
block 大小 3 默认，纹理弱时加大到 5；
为光流量身定做，好特征就叫 goodFeaturesToTrack；
点集要定期重检测，长时跟踪记得加 FB 校验。""",
    params=[
        ("maxCorners", "最多返回角点数", "200", "覆盖全图但计算量大", "速度快但可能漏"),
        ("qualityLevel", "质量比例阈值", "0.01", "点少质量高", "点多噪声多"),
        ("minDistance", "最小间距（像素）", "10", "分布均匀", "可能扎堆"),
        ("blockSize", "梯度窗口大小", "3", "抗噪性好", "定位更准"),
    ],
    tips=[
        ("亚像素精化（标定必备）",
         "`goodFeaturesToTrack` 的精度是整像素，标定板需要亚像素精度：\n```python\ncriteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 40, 0.001)\ncorners_sub = cv2.cornerSubPix(gray, corners, (5,5), (-1,-1), criteria)\n```\n精度能到 0.1 像素。"),
        ("配合 LK 光流的标准流程",
         "```python\np0 = cv2.goodFeaturesToTrack(prev, 200, 0.01, 10)\np1, st, err = cv2.calcOpticalFlowPyrLK(prev, curr, p0, None, winSize=(21,21), maxLevel=3)\ngood = p1[st==1]\n# 每 30 帧重检测一次\n```"),
        ("网格均匀化",
         "如果全图角点分布不均，把图分 4×4 网格，每格独立 `goodFeaturesToTrack` 取 25 个点，共 400 点全图均匀分布。"),
    ],
    perf=[
        ("Shi-Tomasi 检测 (640×480)", "~10 ms", "200 个角点"),
        ("Harris", "~20 ms", "同规模"),
        ("FAST", "~3 ms", "数千角点，不含 NMS 排序"),
    ],
    notes=""
)

# ===== MSER =====
build_algo(
    "mser",
    meta=dict(
        name="MSER 最大稳定极值区域", en="Maximally Stable Extremal Regions",
        branch="feature-detection", year="2002", author="Jiri Matas et al.",
        chapter="ch-8-local-feature", level="mid",
        tagline="像往黑白照片上浇水，颜色深浅慢慢渗开，那些形状最稳定的水坑就是好区域",
        analogy="把灰度图想象成一块地形，从黑到白慢慢淹水：一开始只有最深的坑有水，水涨后水面扩大。那些「水位变一点、水面大小几乎不变」的湖泊，就是最稳定的区域——MSER",
        scene="宽基线立体匹配、文本检测（自然场景文字）、目标识别、对仿射变换要求高的场景",
        pros=["仿射不变性","多尺度区域检测","无需预设阈值","对光照鲁棒","形状任意"],
        cons=["对模糊敏感","速度较慢","参数 delta/minArea/maxArea 要调","不适合低对比度"]),
    concepts=[
        ("极值区域 Extremal Region",
         "极值区域 = 图像中**所有像素都比边界外暗**（或亮）的连通区域。随着二值化阈值从 0 升到 255，极值区域会逐渐长大、合并。",
         None),
        ("稳定度 q(i)",
         "MSER 的核心量：**区域面积在阈值变化时的相对变化率**。q(i) = |R(i+Δ) - R(i-Δ)| / |R(i)|，其中 R(i) 是阈值为 i 时的区域像素集合。q 越小说明这个区域越「稳定」——水位变了水面几乎不变。",
         "flowchart LR\n  A[\"阈值 i\"] -->|\"Δ=5\"| B[\"R(i-Δ), R(i), R(i+Δ)\"]\n  B --> C[\"q = 面积变化率\"]\n  C --> D{\"q 极小?\"}\n  D -->|\"是\"| E[\"✅ MSER 区域\"]"),
        ("为什么仿射不变",
         "因为 MSER 基于**区域拓扑关系**（连通性）和**相对亮度顺序**，而不是绝对像素位置或灰度值。仿射变换（拉伸/旋转/倾斜）不会改变连通关系，也不会改变局部亮度排序——所以同一个区域无论怎么透视变形，都会被检测到。",
         None),
        ("MSER 区域→特征点",
         "MSER 输出的是区域（像素集合），不是点。使用时通常取每个 MSER 区域的**重心+等效椭圆（二阶矩）**作为仿射协变区域，再归一化成 41×41 patch 提 SIFT 描述子。",
         None),
    ],
    arch_steps=[
        ("像素按灰度排序", "把所有像素按灰度值从小到大排序（BINSORT，O(n)）"),
        ("灌水（并查集合并）", "从阈值 0 开始逐步提高，每加一级把该灰度像素加入并查集，和相邻的已加入像素合并"),
        ("记录区域面积", "每个连通分量在每个阈值下记录面积"),
        ("算稳定度 q(i)", "对每个连通分量在每个阈值 i 算 q(i)"),
        ("选局部极小值", "q(i) 的局部极小值对应的区域 = MSER（排除过小/过大区域）"),
        ("后处理", "拟合椭圆/重心，和父/子区域去重（避免重复检测嵌套区域）"),
    ],
    opencv='''img = cv2.imread("text.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
mser = cv2.MSER_create(
    _delta=5,               # 阈值变化步长
    _min_area=60,           # 最小区域（像素）
    _max_area=14400,        # 最大区域（像素，= 图像 5%）
    _max_variation=0.25,    # 最大面积变化率（越大容忍越多变）
    _min_diversity=0.2      # 子区域多样性阈值
)
regions, bboxes = mser.detectRegions(gray)
# 绘制
vis = img.copy()
for region in regions:
    hull = cv2.convexHull(region.reshape(-1, 1, 2))
    cv2.polylines(vis, [hull], True, (0,255,0), 1)
cv2.imwrite("mser.jpg", vis)
print(f"检测到 {len(regions)} 个 MSER 区域")''',
    numpy_impl='''# MSER 的完整实现较复杂（需要并查集+分量面积跟踪），这里给出核心"灌水"框架
class MSERSimple:
    def __init__(self, delta=5, min_area=60, max_area=14400, max_var=0.25):
        self.delta, self.min_area, self.max_area = delta, min_area, max_area
        self.max_var = max_var
    def detect(self, gray):
        h, w = gray.shape
        # 按灰度分组像素
        pixels_by_val = [[] for _ in range(256)]
        for y in range(h):
            for x in range(w):
                pixels_by_val[gray[y, x]].append((y, x))
        # 并查集（简易版，省略）
        parent = {}
        area = {}
        def find(p):
            while parent[p] != p:
                parent[p] = parent[parent[p]]; p = parent[p]
            return p
        # 逐阈值灌水
        history = {}   # root -> {threshold: area}
        for t in range(256):
            for (y, x) in pixels_by_val[t]:
                p = (y, x); parent[p] = p; area[p] = 1
                for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ny, nx = y+dy, x+dx
                    if (ny, nx) in parent:
                        rp, rq = find(p), find((ny, nx))
                        if rp != rq:
                            parent[rq] = rp; area[rp] += area[rq]
                r = find(p)
                history.setdefault(id(r), []).append((t, area[r]))
        # 简化：真正 MSER 还要跟踪区域演化和 q(i)，这里省略
        return []
mser = MSERSimple()''',
    pitfalls=[
        ("参数默认值在小图上检不出", "640×480 图上默认 _min_area=60、_max_area=14400（占 5%）可能导致重要区域被过滤。",
         "根据图像大小调整 min/max 面积。一般 min_area ≈ 图像面积的 0.01%。"),
        ("在模糊图上 MSER 数量爆炸", "图像模糊后稳定区域边界不再清晰，出现大量小而杂的区域。",
         "**不要在严重模糊图上直接用 MSER**；先适度锐化，或提高 _max_variation 到 0.5。"),
        ("嵌套区域重复检测", "一个大字被检测为一个区域，字内部的孔洞也被检测为一个区域，导致同一位置多个框。",
         "用 `_min_diversity=0.5` 或在 bboxes 上做 NMS 去重。"),
        ("低对比度图像检不出", "光照均匀、对比度低时，区域面积随阈值变化快，没有稳定区。",
         "先做直方图均衡：`gray = cv2.equalizeHist(gray)`。"),
        ("只拿 MSER 当区域没提描述子", "MSER 只给连通区域，直接当特征用会发现没法匹配。",
         "把每个 MSER 区域仿射归一化到 41×41 patch，然后提 SIFT/ROOT-SIFT 描述子。"),
    ],
    koujue="""delta 设 5 是默认，步长太大稳定点难寻；
min_area 六十、max 万一四，看图像尺寸来调整；
max_variation 零点二五，太大出一堆小区域；
文字检测天然擅长，自然场景文字它称王；
仿射不变是绝活，宽基线匹配都选它；
输出是区域不是点，记得拟合椭圆再提描述。""",
    params=[
        ("_delta", "阈值步长", "5", "稳定但数量少", "数量多但噪声大"),
        ("_min_area", "最小区域面积", "60", "去噪", "检小目标"),
        ("_max_area", "最大区域比例", "5% 图像", "去大区域（天空）", "允许大目标"),
        ("_max_variation", "最大 q 值", "0.25", "只保留稳定的", "容忍不稳定"),
    ],
    tips=[
        ("文本检测经典组合",
         "MSER + 几何过滤（宽高比、面积、占空比）+ 纹理过滤（笔画宽度）是 OpenCV3 text 模块和传统场景文本检测的经典组合：\n```python\n# OpenCV 文本检测 API（需 opencv-contrib）\nswt = cv2.text.createStrokeWidthTransform()\nerd = cv2.text.createERFilterNM1()```"),
        ("颜色 MSER",
         "对彩色图，在 RGB 三通道分别跑 MSER 然后合并，能检测更多彩色区域。"),
        ("转换为仿射协变区域",
         "```python\nfor region in regions:\n    (x,y),(w,h),angle = cv2.fitEllipse(region)\n    # 然后用这个椭圆做仿射归一化到圆形 patch\n```"),
    ],
    perf=[
        ("MSER detectRegions (640×480)", "~50–100 ms", "CPU 单线程"),
        ("vs SIFT (同样图)", "~200 ms", "SIFT 检测+描述"),
    ],
    notes="工程上 MSER 在 OpenCV 主模块可用，但自然场景文本检测的完整 pipeline 建议用 opencv-contrib 的 `text` 模块。"
)

# ===== morphology =====
build_algo(
    "morphology",
    meta=dict(
        name="形态学操作", en="Mathematical Morphology",
        branch="image-processing", year="1964", author="G. Matheron / J. Serra",
        chapter="ch-4-image-enhancement", level="basic",
        tagline="膨胀、腐蚀、开、闭、顶帽黑帽——五把瑞士军刀帮你清理图像里的小毛刺和黑洞",
        analogy="形态学就像一套木匠的打磨工具：腐蚀像用砂纸把凸起毛刺磨掉，膨胀像给凹坑补腻子，开运算像「先磨毛刺再补漆」（去小白点），闭运算像「先补漆再磨平」（填小黑洞）",
        scene="二值图去噪、孔洞填充、边缘提取、骨架提取、字符识别预处理、OCR、工业缺陷检测",
        pros=["速度极快","效果直观可控","组合能力强","支持任意核形状","CPU 实时"],
        cons=["核大小/形状需调","大核慢","过度腐蚀/膨胀丢信息","对边界细节破坏"]),
    concepts=[
        ("结构元素（核）",
         "形态学操作需要一个「形状模板」叫结构元素（structuring element），像一个印章盖到图像上滑动，根据核覆盖下像素的关系决定输出。核可以是矩形、椭圆、十字，甚至任意形状。**核形状和大小决定了操作效果**。",
         "flowchart LR\n  A[\"输入图像\"] --> C[\"结构元素 B<br/>（矩形/椭圆/十字）\"]\n  C --> D[\"逐像素滑动操作\"]\n  A --> D\n  D --> E[\"输出图像\"]"),
        ("腐蚀 Erosion",
         "对每个像素，取核覆盖范围内**最小值**作为输出。对二值图：核必须完全落在前景里，该像素才保留为前景——**缩小白块、消除小白点**。",
         None),
        ("膨胀 Dilation",
         "对每个像素，取核覆盖范围内**最大值**作为输出。对二值图：只要核有一部分碰着前景，该像素就扩成前景——**放大白块、填补小黑洞**。",
         None),
        ("开运算 Opening",
         "**先腐蚀后膨胀**。作用：**消除小亮斑、断开细连接、平滑大区域边界**，但总体形状和面积基本不变。",
         "flowchart LR\n  A[\"原图\"] -->|\"腐蚀\"| B[\"小亮点消失<br/>主体缩小\"]\n  B -->|\"膨胀\"| C[\"主体恢复大小<br/>亮点没回来<br/>= 开运算 ✅\"]"),
        ("闭运算 Closing",
         "**先膨胀后腐蚀**。作用：**填充小黑洞、连接相邻物体、弥合小缺口**，同样基本不改变主体面积。",
         None),
        ("其他衍生操作",
         "- **形态学梯度** = 膨胀 - 腐蚀 → 提取边缘\n- **顶帽 Top-Hat** = 原图 - 开运算 → 提取**比周围亮的小元素**\n- **黑帽 Black-Hat** = 闭运算 - 原图 → 提取**比周围暗的小元素**\n- **击中击不中 Hit-Miss** → 匹配指定像素模式（角点、端点）",
         None),
    ],
    arch_steps=[
        ("选结构元素", "根据要处理的目标形状选矩形（MORPH_RECT）、椭圆（MORPH_ELLIPSE）或十字（MORPH_CROSS），确定核大小（奇数）"),
        ("锚点", "默认核中心为锚点，也可自定义"),
        ("边界处理", "图像边界外像素填充常数（默认 0 或复制边界）"),
        ("邻域 min/max", "腐蚀取邻域 min；膨胀取邻域 max"),
        ("组合运算", "开=腐+膨；闭=膨+腐；梯度=膨-腐；顶帽=原-开；黑帽=闭-原"),
        ("迭代次数", "可连续多次迭代，效果类似用更大的核，但速度更快"),
    ],
    opencv='''img = cv2.imread("text.jpg", 0)
_, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

# 结构元素
kernel_rect = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
kernel_cross = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

# 基础操作
eroded = cv2.erode(binary, kernel_rect, iterations=1)
dilated = cv2.dilate(binary, kernel_rect, iterations=1)
opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_ellipse)
closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_ellipse)
gradient = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel_rect)
tophat = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel_rect)
blackhat = cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel_rect)''',
    numpy_impl='''def binary_erode(binary, k):
    \"\"\"二值图腐蚀（简易版）\"\"\"
    h, w = binary.shape
    kh, kw = k.shape
    pad_y, pad_x = kh//2, kw//2
    padded = np.pad(binary, ((pad_y,pad_y),(pad_x,pad_x)), mode='constant')
    out = np.zeros_like(binary)
    for y in range(h):
        for x in range(w):
            patch = padded[y:y+kh, x:x+kw]
            # 腐蚀：kernel 覆盖的所有点都必须是 255
            if np.all(patch[k == 1] == 255):
                out[y, x] = 255
    return out

def binary_dilate(binary, k):
    h, w = binary.shape
    kh, kw = k.shape
    pad_y, pad_x = kh//2, kw//2
    padded = np.pad(binary, ((pad_y,pad_y),(pad_x,pad_x)), mode='constant')
    out = np.zeros_like(binary)
    for y in range(h):
        for x in range(w):
            patch = padded[y:y+kh, x:x+kw]
            # 膨胀：kernel 覆盖范围有任意一个 255 即可
            if np.any(patch[k == 1] == 255):
                out[y, x] = 255
    return out''',
    pitfalls=[
        ("核大小选错，要么过度腐蚀要么没效果", "核 3×3 没效果，换成 11×11 后目标整个被腐蚀没了。",
         "从 **3×3** 起步，先看效果；需要更强时加 iterations 而不是直接换大核。"),
        ("开/闭运算顺序搞反", "想填小黑洞做了开运算，结果小亮点也被消掉；想去掉小亮点做了闭运算，黑洞没填上。",
         "口诀：**开=去亮刺（先腐后膨），闭=填黑洞（先膨后腐）**。"),
        ("在灰度图上乱用二值形态学参数", "以为形态学只能处理二值图。",
         "形态学可以直接处理灰度图！腐蚀=局部 min，膨胀=局部 max。常用于亮度峰值提取、暗细节增强。"),
        ("忘了迭代次数参数", "要做较强腐蚀时手动调大核导致速度慢。",
         "用 `iterations=3` 连续做三次 3×3 腐蚀，比一次 9×9 腐蚀更快、效果类似。"),
        ("边界处理导致边缘黑边", "腐蚀后图像边缘出现一圈白边或黑边。",
         "OpenCV 默认 `BORDER_CONSTANT`，可改用 `borderType=cv2.BORDER_REPLICATE`。"),
    ],
    koujue="""腐蚀取最小、膨胀取最大，先腐后膨是开、先膨后腐是闭；
开去掉亮刺、闭填好黑洞，顶帽提亮、黑帽提暗；
核形状看目标：方块用矩形、圆用椭圆、十字对十字线；
核大小 3 起步，不够加 iterations 不要直接上大核；
灰度图也能做，最小最大当滤波；
OCR 之前闭一开，文字笔画变干净。""",
    params=[
        ("kernel shape", "核形状", "RECT/ELLIPSE", "—", "—"),
        ("kernel size", "核大小（奇数）", "3", "处理大块", "保留细节"),
        ("iterations", "迭代次数", "1", "效果强", "温和"),
    ],
    tips=[
        ("OCR 预处理经典流程",
         "```python\ngray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)\n# 去掉小噪声点 + 填充字符内部小洞\nk = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))\nbinary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, k)   # 去噪点\nbinary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, k)  # 填洞\n```"),
        ("背景不均匀校正（顶帽）",
         "```python\n# 不均匀光照背景：用大核做闭运算得到背景\nbg = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT,(31,31)))\ncorrected = cv2.subtract(gray, bg)   # 顶帽效果\n```"),
        ("提取水平/垂直线",
         "用长条形核提取某个方向的线：\n```python\n# 水平线\nh_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30,1))\nhorizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_kernel)\n# 垂直线\nv_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,30))\nvertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, v_kernel)\n```"),
    ],
    perf=[
        ("3×3 腐蚀/膨胀", "~1 ms/MPix", "CPU SIMD 优化"),
        ("开/闭运算", "~2 ms/MPix", "腐蚀+膨胀各一次"),
        ("大核 (21×21)", "~10 ms/MPix", "可用多次 3×3 替代"),
    ],
    notes=""
)

print("batch1 done: shi-tomasi, mser, morphology")
