#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二批：watershed, grabcut, kmeans, meanshift, slic"""
import sys
sys.path.insert(0, "/home/user/workspace/7648064683708846935/agent-cv")
from generate_algos3 import build_algo

build_algo(
    "watershed",
    meta=dict(
        name="分水岭分割", en="Watershed Transform",
        branch="segmentation", year="1991", author="Luc Vincent / Pierre Soille",
        chapter="ch-10-image-segmentation", level="mid",
        tagline="把灰度图当地形图灌水，两个水坑汇合的地方就是分界线，专门切粘连物体",
        analogy="想象你在一块凹凸的地形上，从每个谷底开始慢慢灌水。当两个湖的水面要汇合时，你在汇合处修一道水坝——这些水坝就是分割线",
        scene="分离粘连硬币/细胞/颗粒、医学影像分割细胞、工业检测数零件、重叠物体分割",
        pros=["闭合连续边界","分离粘连物体","速度较快","支持种子点控制"],
        cons=["直接用会过度分割","必须先做标记","对噪声敏感","需要形态学预处理"]),
    concepts=[
        ("地形模型",
         "把灰度图看作地形图：**像素越亮海拔越高，越暗海拔越低**。局部极小值就是「谷底」（盆地），局部极大值是「山峰」。",
         None),
        ("灌水模拟",
         "从每个谷底开始向水平面里灌水。水位慢慢升高，水从盆地漫出来。当两个不同盆地的水即将汇合时，在那里建一道「坝」——**这些坝就是分水岭线**。",
         "flowchart TB\n  A[\"局部极小值（种子）\"] --> B[\"水位上升\"]\n  B --> C{\"两盆地水要汇合?\"}\n  C -->|\"是\"| D[\"建水坝（分水岭线）✅\"]\n  C -->|\"否\"| B"),
        ("过度分割问题",
         "真实图像里局部极小值极多（噪声就会产生很多假谷底），直接分水岭会把图碎成几百上千个没用的小区域。这就是分水岭最大的坑——**过度分割（over-segmentation）**。",
         None),
        ("标记分水岭（Marker-controlled）",
         "解决过度分割的关键：**只允许用户标记的「确定前景」和「确定背景」位置作为灌水起点**，其他地方不允许自发灌水。这就是 OpenCV 的 `cv2.watershed` 用的版本，工程上唯一可用的分水岭。",
         None),
        ("距离变换",
         "标记分水岭常用**距离变换**自动找前景种子：对二值前景图做距离变换（每个前景像素到最近背景的距离），距离变换的局部峰值就是「确定前景中心」（硬币圆心、细胞中心）。",
         None),
    ],
    arch_steps=[
        ("二值化", "Otsu 或阈值法把图转成二值"),
        ("形态学开运算去噪", "morphologyEx OPEN 去掉小亮点噪声"),
        ("确定背景", "对开运算结果做 dilate，膨胀后的区域 = 确定背景"),
        ("距离变换找前景", "distanceTransform + 阈值（>0.5*maxDist）得到确定前景"),
        ("找未知区域", "未知区域 = 背景 - 前景（分水岭会在这里画线）"),
        ("connectedComponents 标记", "给前景区域标不同 label，背景标 1，未知标 0"),
        ("watershed", "cv2.watershed(img, markers)，返回的 markers=-1 即为边界线"),
    ],
    opencv='''img = cv2.imread("coins.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
# 去噪
kernel = np.ones((3,3), np.uint8)
opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
# 确定背景
sure_bg = cv2.dilate(opening, kernel, iterations=3)
# 距离变换找确定前景
dist = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
_, sure_fg = cv2.threshold(dist, 0.5*dist.max(), 255, cv2.THRESH_BINARY)
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)
# 标记
_, markers = cv2.connectedComponents(sure_fg)
markers = markers + 1                    # 背景=1
markers[unknown==255] = 0                # 未知=0
markers = cv2.watershed(img, markers)
# 边界=-1，画红
img[markers==-1] = [0,0,255]
cv2.imwrite("watershed.jpg", img)''',
    numpy_impl='''# 分水岭核心实现复杂（优先队列泛洪），这里展示距离变换
def distance_transform_me(binary):
    """简化的距离变换：对每个前景点，到最近背景点的欧氏距离"""
    from scipy.ndimage import distance_transform_edt
    return distance_transform_edt(binary)
# 真正的分水岭算法建议直接用 OpenCV（基于 Vincent-Soille 浸没算法，1000 行代码级别）''',
    pitfalls=[
        ("直接 watershed 不做标记，结果碎成渣", "直接传二值图或空 markers 给 watershed，结果到处是 -1 的边界，图像像被乱刀切碎。",
         "**一定要做 marker-controlled**：确定前景、确定背景、未知区域。只允许从确定种子开始灌水。"),
        ("Otsu 二值化效果差", "光照不均导致二值化后物体粘连或破碎。",
         "二值化前先做**自适应阈值**或**背景校正**：`cv2.adaptiveThreshold`。"),
        ("距离变换阈值选错", "阈值 0.5*maxDist 时前景区域很小或很大，分割不准。",
         "0.4–0.7 之间调整，或用 `peak_local_max`（skimage）找真正的峰值。"),
        ("markers 没加 1", "OpenCV 要求：背景必须是 1，前景从 2 开始，0 是未知。直接 connectedComponents 输出（背景=0）会出错。",
         "**一定要 markers = markers + 1**，然后把 unknown 置 0。"),
        ("直接传灰度图给 watershed", "watershed 需要彩色原图（3 通道）和 markers（int32），传灰度图会报错。",
         "第一参数必须是**原始彩色图**（用于梯度），markers 是 `int32` 类型。"),
        ("重叠物体没有任何凹点", "完全重叠的圆饼或颗粒，距离变换只找出一个峰，无法分开。",
         "这种情况需要用凹点检测、或者深度学习实例分割。"),
    ],
    koujue="""分水岭要想不碎，标记一定要给对；
先二值再开运算去噪，膨胀三下当背景；
距离变换找峰值，零点五成确定前景；
背景减前景得未知，connectedComponents 加一；
markers 是 int32、img 是彩图，边界返回负一；
硬币细胞颗粒物，粘连物体专用器。""",
    params=[
        ("morph kernel", "形态学核大小", "3", "去噪强", "保留细边界"),
        ("distanceMask", "距离变换掩码", "5（DIST_L2_5）", "精确但慢", "快"),
        ("distThresh", "前景阈值比例", "0.5", "前景小、过分割少", "前景大、可能粘"),
        ("dilateIter", "背景膨胀次数", "3", "背景多", "背景少"),
    ],
    tips=[
        ("交互式分水岭",
         "用户手动点前景种子时，可以跳过距离变换，直接让用户用鼠标在每个目标中心点一下，然后构造 markers：\n```python\n# 鼠标点击回调里\ncv2.circle(markers_img, (x,y), 5, label_id, -1)\n```"),
        ("后处理 - 填洞",
         "分水岭后每个独立区域（markers 值 ≥2）就是一个分割实例。直接遍历 markers 取值即可，不需要额外连通域。"),
        ("与 HoughCircles 对比",
         "圆形物体分割（硬币）：HoughCircles 直接找圆更简单；形状不规则的粘连物体（细胞、颗粒）必须用 watershed。"),
    ],
    perf=[
        ("cv2.watershed (640×480)", "~10 ms", "CPU 单线程"),
        ("完全流程（含距离变换）", "~20 ms", "640×480"),
    ],
    notes=""
)

build_algo(
    "grabcut",
    meta=dict(
        name="GrabCut 抠图", en="GrabCut Interactive Foreground Extraction",
        branch="segmentation", year="2004", author="C. Rother / V. Kolmogorov / A. Blake",
        chapter="ch-10-image-segmentation", level="mid",
        tagline="画一个框就能把目标抠出来，GMM+GraphCut 迭代优化，Photoshop 快速选择的灵魂",
        analogy="你用笔在目标周围画个圈，对算法说「圈外肯定是背景，圈内有前景也有背景」。GrabCut 就像一个聪明的学徒，先猜哪些颜色像前景，再用 GraphCut 切一刀，反复 5 次抠得干干净净",
        scene="照片抠图换背景、数据集快速标注、医学影像交互式分割、人像美颜前景提取",
        pros=["用户只需画一个框","边缘细节比 GraphCut 好","支持笔刷精修","GMM 建模多峰颜色分布"],
        cons=["高分辨率慢","前景背景颜色接近时效果差","矩形外永远是背景","边缘毛发需 matting"]),
    concepts=[
        ("GMM 高斯混合模型",
         "前景/背景各用 5 个高斯分量建模颜色分布（RGB 三维）。每个高斯是一个椭球云团，描述「这一类颜色」。每个像素属于哪个高斯，由当前分割结果动态决定。",
         "flowchart LR\n  A[\"像素 RGB\"] --> B[\"前景 GMM<br/>5 个高斯\"]\n  A --> C[\"背景 GMM<br/>5 个高斯\"]\n  B --> D[\"属于前景的概率\"]\n  C --> E[\"属于背景的概率\"]"),
        ("GraphCut 最小割",
         "把每个像素看作图的节点，加两个虚拟节点 S（前景源）和 T（背景汇）。S 到像素连边权重 = 该像素属于前景的概率；T 到像素连边权重 = 属于背景的概率；相邻像素之间连边权重 = 颜色相似度。求最小割——割断的边总权重最小，即得到最优分割。",
         None),
        ("迭代优化",
         "GMM 和分割互相改进：初始 GMM（基于框内外）→ GraphCut 得到初始分割 → 用分割结果重新训练 GMM → 再 GraphCut……迭代 5 次左右收敛。",
         "flowchart TB\n  A[\"框初始化\"] --> B[\"初始化 GMM\"]\n  B --> C[\"GraphCut 最小割\"]\n  C --> D[\"更新 GMM 参数\"]\n  D -->|\"迭代 5 次\"| C\n  D -->|\"收敛\"| E[\"输出 mask\"]"),
        ("mask 四值",
         "OpenCV 的 mask 用 4 个值：0=确定背景（GC_BGD）、1=确定前景（GC_FGD）、2=可能背景（GC_PR_BGD）、3=可能前景（GC_PR_FGD）。**用户画框时框内=3，框外=0**。",
         None),
    ],
    arch_steps=[
        ("用户输入", "用户画一个矩形框包围目标，框外=确定背景，框内=可能前景"),
        ("初始化 GMM", "框外像素训练背景 GMM，框内像素训练前景 GMM（各 5 个高斯分量，用 K-Means 初始化）"),
        ("迭代开始", "对每个像素，判断它属于 GMM 哪个分量，算属于前景/背景的概率"),
        ("建图", "构造 S-T 图：t-link 权重 = 数据项（GMM 概率的负对数），n-link 权重 = 平滑项（相邻像素颜色对比度）"),
        ("最小割", "用 max-flow/min-cut 算法分割，得到新的 mask"),
        ("更新 GMM", "用新 mask 重新估计 GMM 分量参数"),
        ("收敛判断", "能量变化小于阈值或达到迭代次数，停止；输出 mask"),
    ],
    opencv='''img = cv2.imread("person.jpg")
mask = np.zeros(img.shape[:2], np.uint8)
bgd = np.zeros((1,65), np.float64)
fgd = np.zeros((1,65), np.float64)
rect = (100, 50, 400, 600)   # (x, y, w, h) 略大于目标
cv2.grabCut(img, mask, rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
# mask 中 0 和 2 是背景，1 和 3 是前景
fg_mask = np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
result = cv2.bitwise_and(img, img, mask=fg_mask)
cv2.imwrite("grabcut.jpg", result)''',
    numpy_impl='''# GrabCut 的核心是 GMM + max-flow/min-cut，完整实现较复杂（~500 行），
# 这里给 GMM 训练简化版
from sklearn.mixture import GaussianMixture
def train_gmm(pixels, n_components=5):
    gmm = GaussianMixture(n_components=n_components, covariance_type='full')
    gmm.fit(pixels)
    return gmm
# 实际工程请直接用 cv2.grabCut，它用的是 Kolmogorov 的 max-flow 实现''',
    pitfalls=[
        ("框画太小", "目标边缘被切成确定背景，怎么迭代都回不来。",
         "**框要比目标大 5–15%**；不要紧贴目标。"),
        ("前景背景颜色接近", "人和背景都是白墙，GrabCut 会把部分前景当背景或反之。",
         "**手动标注**（GC_INIT_WITH_MASK）：用前景笔刷画几笔确认为前景、背景笔刷确认背景，再跑。"),
        ("GrabCut 太慢（1080p 5s）", "迭代 5 次大图像耗时数秒。",
         "**先降分辨率 0.25x 跑 GrabCut**，把 mask 上采样回原尺寸，再在原分辨率上 `GC_INIT_WITH_MASK iters=2` 精修——能提速 10 倍。"),
        ("bgdModel/fgdModel 形状错", "报错 Expected 65 columns 或 dtype 不对。",
         "必须是 **`np.zeros((1,65), np.float64)`**，每次处理新图重置。"),
        ("忘了三通道", "传灰度图进去报错。",
         "GrabCut 需要 **3 通道 BGR** 图。灰度图先 `cvtColor(gray, COLOR_GRAY2BGR)`。"),
        ("mask 值混淆", "前景背景判反，输出完全反色。",
         "前景判据：`(mask==1)|(mask==3)` 即 `(GC_FGD)|(GC_PR_FGD)`。"),
    ],
    koujue="""框要画大一点点，小了目标边缘永远救不回；
bgd/fgd 形状 1 行 65 列，类型必须 float64；
迭代五次是默认，高精度加到十次也还行；
大图像先缩到四分之一，粗分割再上采样精修；
颜色相近加手动笔刷，rect 不行换 mask；
头发丝别指望 GrabCut，close-form matting 才是王。""",
    params=[
        ("iterCount", "迭代次数", "5", "更精确但慢", "快但粗糙"),
        ("rect", "初始框(x,y,w,h)", "目标大 10%", "—", "—"),
        ("mode", "初始化模式", "GC_INIT_WITH_RECT", "—", "—"),
    ],
    tips=[
        ("先粗后精加速",
         "```python\nsmall = cv2.resize(img, None, fx=0.25, fy=0.25)\nsmall_rect = (rect[0]//4, rect[1]//4, rect[2]//4, rect[3]//4)\ncv2.grabCut(small, mask_s, small_rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)\nmask = cv2.resize(mask_s, (w, h), interpolation=cv2.INTER_NEAREST)\ncv2.grabCut(img, mask, None, bgd, fgd, 2, cv2.GC_INIT_WITH_MASK)\n```"),
        ("手动笔刷精修",
         "```python\n# 用户在 UI 画红线=前景，蓝线=背景\nmask[user_fg_stroke > 0] = cv2.GC_FGD\nmask[user_bg_stroke > 0] = cv2.GC_BGD\ncv2.grabCut(img, mask, None, bgd, fgd, 3, cv2.GC_INIT_WITH_MASK)\n```"),
        ("边缘柔化（抗锯齿）",
         "```python\n# GrabCut 二值 mask 边缘硬，用导向滤波柔化\nalpha = cv2.ximgproc.guidedFilter(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), fg_mask, 8, 1e-3)\n```"),
    ],
    perf=[
        ("GrabCut iters=5 (320×240)", "~150 ms", "CPU"),
        ("GrabCut iters=5 (640×480)", "~600 ms", "CPU"),
        ("GrabCut iters=5 (1920×1080)", "~5 s", "CPU，需降采样优化"),
    ],
    notes=""
)

build_algo(
    "kmeans",
    meta=dict(
        name="K-Means 颜色聚类", en="K-Means Clustering",
        branch="segmentation", year="1967", author="Stuart Lloyd / James MacQueen",
        chapter="ch-10-image-segmentation", level="basic",
        tagline="把所有像素按颜色分成 K 堆，每堆一个代表色，图像立刻变卡通",
        analogy="把一盒彩笔按颜色分成 K 堆：先随机挑 K 支笔当组长，其他笔投奔最近的组长；每堆重新选平均色当新组长；反复到组长不再变",
        scene="颜色量化、海报风格化、肤色区域分割、语义分割前处理、调色板生成",
        pros=["思想极简单","速度快","OpenCV/sklearn 一行调用","适用范围广"],
        cons=["必须指定 K","只看颜色不看位置","对初始值敏感","对噪声敏感"]),
    concepts=[
        ("聚类中心",
         "每个类有一个「代表色」（质心），所有像素根据颜色距离（欧氏距离）投奔最近的质心。每次迭代重新计算质心（取该类所有像素的平均色）。",
         None),
        ("K-Means++ 初始化",
         "随机初始化容易把多个初始中心挤到同一种颜色上，导致局部最优。K-Means++ 让初始中心**尽量分散**：第一个随机选，后续每个中心以「与已有中心距离平方成正比的概率」采样。代价几乎为零，效果显著改善。",
         None),
        ("特征空间扩展",
         "标准 K-Means 只在 (R,G,B) 三维聚类，同一种颜色分散在不同位置会被聚成同一类。可以加空间坐标 (x,y) 变成 5 维，但要归一化坐标到 0–255 范围。",
         None),
        ("停止条件",
         "达到最大迭代次数（如 10）或中心移动距离 < 精度（如 1.0）即停止。通常 5–10 次迭代就能收敛。",
         None),
    ],
    arch_steps=[
        ("特征准备", "像素 reshape 成 (N, 3) 浮点；可选：加 (x,y) 变成 5 维，归一化"),
        ("初始化中心", "用 kmeans++ 选 K 个初始中心"),
        ("分配", "每个像素归到最近的中心（按欧氏距离）"),
        ("更新中心", "每个类重新算均值作为新中心"),
        ("收敛判断", "中心移动 < epsilon 或达到最大迭代次数"),
        ("重建图像", "每个像素用其所在类的中心色替换，reshape 回图像形状"),
    ],
    opencv='''img = cv2.imread("scene.jpg")
Z = img.reshape((-1,3)).astype(np.float32)
K = 8
criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
ret, label, center = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
center = np.uint8(center)
res = center[label.flatten()].reshape(img.shape)
cv2.imwrite(f"kmeans_K{K}.jpg", res)
# 含空间坐标的 5 维版本
h, w = img.shape[:2]
ys, xs = np.mgrid[0:h, 0:w]
feat = np.stack([ys/h*255, xs/w*255, img[...,0], img[...,1], img[...,2]],
                axis=2).reshape(-1,5).astype(np.float32)
ret, label5, center5 = cv2.kmeans(feat, K, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
res5 = np.uint8(center5[label5.flatten(), 2:]).reshape(img.shape)''',
    numpy_impl='''def kmeans_numpy(X, K, max_iter=10, tol=1e-4, seed=42):
    rng = np.random.default_rng(seed)
    # kmeans++ 初始化
    idx = rng.choice(len(X), 1)
    centers = [X[idx[0]]]
    for _ in range(K-1):
        d2 = np.min([np.sum((X - c)**2, axis=1) for c in centers], axis=0)
        probs = d2 / d2.sum()
        idx = rng.choice(len(X), 1, p=probs)
        centers.append(X[idx[0]])
    centers = np.array(centers)
    for it in range(max_iter):
        # 分配
        d = np.linalg.norm(X[:,None] - centers[None], axis=2)
        labels = d.argmin(axis=1)
        # 更新
        new_centers = np.array([X[labels==k].mean(0) for k in range(K)])
        if np.linalg.norm(new_centers - centers) < tol:
            break
        centers = new_centers
    return labels, centers''',
    pitfalls=[
        ("忘了转 float32", "`cv2.kmeans` 报 Unsupported depth/format 错误。",
         "Z 必须是 `np.float32`，不能是 uint8。"),
        ("K 值选得离谱", "K=2 时只剩两种颜色，K=32 时和原图差不多看不出差别。",
         "图像风格化 **K=4–8**；颜色量化 **K=16–64**；二分类 K=2。"),
        ("每次结果不一样", "kmeans 随机初始化，同样参数两次结果不同。",
         "设随机种子：`cv2.setRNGSeed(42)`；用 `KMEANS_PP_CENTERS` 稳定性更好。"),
        ("直接 3 维 K-Means 颜色碎", "同色物体分散在不同位置聚在一起后分割不连贯。",
         "加空间坐标变成 5 维，或先用 SLIC 超像素再聚类。"),
        ("不做 kmeans++", "用 KMEANS_RANDOM_CENTERS 可能得到空类、效果差。",
         "**永远用 `cv2.KMEANS_PP_CENTERS`**（默认）。"),
    ],
    koujue="""K 值八是常用点，海报效果四到八；
数据必须 float32，uint8 直接报错；
初始化用 kmeans++，随机初始化常炸锅；
只看颜色碎一地，加上 XY 分块聚；
迭代十次足够收敛，精度设 1.0 不算差；
要固定结果设随机种子，setRNGSeed 传 42。""",
    params=[
        ("K", "聚类数", "8", "颜色多样", "块状风格化"),
        ("max_iter", "最大迭代", "10", "更精确", "快"),
        ("epsilon", "收敛精度", "1.0", "精确", "快"),
        ("attempts", "尝试次数（选最佳）", "10", "更稳", "快"),
    ],
    tips=[
        ("K 的选择（肘部法）",
         "```python\ninertia = []\nfor K in range(2,16):\n    r,l,c = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_PP_CENTERS)\n    inertia.append(r)  # compactness\n# 画 inertia vs K，找拐点\n```"),
        ("生成调色板",
         "```python\n# center 就是 K 个调色板色（BGR）\npalette = center.reshape(1, K, 3)\ncv2.imwrite('palette.jpg', cv2.resize(palette, (K*50, 50), interpolation=cv2.INTER_NEAREST))\n```"),
        ("Lab 空间聚类更符合人眼",
         "在 Lab 颜色空间（而非 BGR）做 K-Means 聚类，结果更符合人类感知：\n```python\nlab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)\nZ = lab.reshape(-1,3).astype(np.float32)\n```"),
    ],
    perf=[
        ("cv2.kmeans K=8 (640×480)", "~50 ms", "CPU"),
        ("5 维 (K=8)", "~150 ms", "CPU"),
        ("kmeans++ 初始化开销", "< 1 ms", "几乎可忽略"),
    ],
    notes=""
)

build_algo(
    "meanshift",
    meta=dict(
        name="MeanShift 均值漂移", en="Mean-Shift Mode Seeking",
        branch="segmentation", year="1975/2002", author="K. Fukunaga / D. Comaniciu / P. Meer",
        chapter="ch-10-image-segmentation", level="mid",
        tagline="每个点朝邻居最密的方向挪一步，最后聚成几坨——不用提前说有几坨",
        analogy="广场上站了一群人，每个人都往「周围人最密集的方向」走一步。走几步后大家会聚成几个紧密的小圈子，每个圈子就是一类",
        scene="图像平滑分割（pyrMeanShiftFiltering）、目标跟踪（CamShift）、聚类、运动目标分割",
        pros=["无需指定聚类数","同时考虑颜色+空间","任意形状聚类","对光照鲁棒"],
        cons=["速度很慢","带宽 sp/sr 参数难调","窗口大小固定","高维不行"]),
    concepts=[
        ("密度梯度上升",
         "MeanShift 的本质是**核密度估计的梯度上升**：对每个点，计算它周围窗口内所有点的加权平均位置（均值漂移向量），然后让这个点移动到均值位置——不断迭代直到收敛到局部密度峰值。所有收敛到同一峰值的点归为一类。",
         "flowchart LR\n  A[\"当前点 x\"] --> B[\"算窗口内加权均值 m(x)\"]\n  B --> C[\"x ← m(x)\"]\n  C -->|\"未收敛\"| B\n  C -->|\"收敛\"| D[\"到达密度峰值（模式）\"]"),
        ("空间-颜色联合空间",
         "图像分割用的 MeanShift 在 5 维空间（x,y,L,a,b 或 x,y,R,G,B）里漂移，但空间维和颜色维的尺度不同，用两个带宽参数控制：sp 控制空间窗口半径，sr 控制颜色窗口半径。",
         None),
        ("金字塔加速",
         "直接对原图像素做 MeanShift 太慢（O(N²)）。`pyrMeanShiftFiltering` 采用金字塔策略：先在小尺度图像上做漂移，然后上采样回大尺度做少量迭代精修——速度快很多。",
         None),
        ("MeanShift vs K-Means",
         "K-Means 要预设 K，每个类形状倾向球状；MeanShift 不需要 K，能聚任意形状类，自动发现聚类数，但速度慢很多。",
         None),
    ],
    arch_steps=[
        ("图像转 Lab", "先转 Lab 颜色空间（欧氏距离更符合感知）"),
        ("构建金字塔", "按 maxLevel 构建高斯金字塔"),
        ("在最粗层漂移", "对每个像素：在 (sp,sr) 窗口内求颜色加权均值 → 移动到均值位置，重复直到收敛"),
        ("上采样", "收敛结果上采样到下一层作为初始值"),
        ("逐层精修", "每层再做几次迭代精修"),
        ("重建", "最终每个像素的颜色值被替换为它收敛到的模式颜色，产生分割效果"),
    ],
    opencv='''img = cv2.imread("scene.jpg")
# MeanShift 滤波（颜色平滑+分割）
shifted = cv2.pyrMeanShiftFiltering(
    img,
    sp=15,      # 空间窗口半径
    sr=30,      # 颜色窗口半径
    maxLevel=1
)
# 再做一次连通域合并
gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
n, labels, stats, _ = cv2.connectedComponentsWithStats(thresh)
print(f"MeanShift 后共 {n-1} 个连通区域")
cv2.imwrite("meanshift.jpg", shifted)''',
    numpy_impl='''def meanshift_vectorized(points, bandwidth, max_iter=20, tol=1e-3):
    """点集上的 MeanShift 聚类（演示用）"""
    X = points.astype(np.float32)
    for _ in range(max_iter):
        new_X = np.zeros_like(X)
        for i, x in enumerate(X):
            # 找带宽内的邻居
            dists = np.linalg.norm(X - x, axis=1)
            neighbors = X[dists < bandwidth]
            if len(neighbors) == 0:
                new_X[i] = x
                continue
            # 高斯核加权
            w = np.exp(-0.5 * (dists[dists<bandwidth]/bandwidth)**2)
            new_X[i] = (neighbors * w[:,None]).sum(0) / w.sum()
        if np.linalg.norm(new_X - X) < tol:
            break
        X = new_X
    return X''',
    pitfalls=[
        ("1080p 图跑几秒", "pyrMeanShiftFiltering 在 1080p 上耗时 2–3 秒，没法实时。",
         "先降采样到 480p，处理完上采样标签；或改用 SLIC（快 10–50 倍）。"),
        ("sp/sr 参数没调好", "sp=30 大块糊成一片；sp=5 碎成小颗粒。sr=60 颜色被平滑得没细节。",
         "从 **sp=10–20, sr=20–40** 起步，根据效果微调。"),
        ("只滤波不做连通域", "pyrMeanShiftFiltering 只做颜色平滑（同一区域颜色变一致），不直接输出标签。",
         "滤波后必须再用 `connectedComponents` 或阈值+连通域取得具体分割。"),
        ("以为 meanShift 跟踪很鲁棒", "MeanShift/CamShift 跟踪在背景有同色物体时严重漂移。",
         "对跟踪而言 MeanShift 适合肤色、固定颜色目标；更复杂场景用 KCF/深度学习跟踪器。"),
    ],
    koujue="""空间半径 sp 十到二十，太大糊一片太小碎；
颜色半径 sr 二到四十，越大平滑越狠；
金字塔一层是默认，加层提速但精度降；
滤波后还得连通域，不然只有颜色齐；
大图像记得先缩小，不然几秒跑不完；
想自动找类数用它，已知类数直接 K-Means。""",
    params=[
        ("sp", "空间窗口半径", "15", "区域连贯但慢", "细节多可能过分割"),
        ("sr", "颜色窗口半径", "30", "颜色平滑强", "保留颜色变化"),
        ("maxLevel", "金字塔层数", "1", "快但粗糙", "慢但精"),
    ],
    tips=[
        ("MeanShift 后接 Canny 做闭合边缘",
         "```python\nshifted = cv2.pyrMeanShiftFiltering(img, 15, 30)\nedges = cv2.Canny(shifted, 50, 150)\n# edges 会很干净，因为 MeanShift 已经把同区域颜色平滑\n```"),
        ("用 MeanShift 做视频背景消除",
         "MeanShift 能把运动前景变成颜色一致的块，后续帧差+连通域即可检运动。"),
    ],
    perf=[
        ("pyrMeanShiftFiltering (320×240)", "~100 ms", "CPU"),
        ("pyrMeanShiftFiltering (640×480)", "~400 ms", "CPU"),
        ("pyrMeanShiftFiltering (1920×1080)", "~3 s", "CPU，需降分辨率"),
    ],
    notes=""
)

build_algo(
    "slic",
    meta=dict(
        name="SLIC 超像素", en="Simple Linear Iterative Clustering",
        branch="segmentation", year="2010", author="R. Achanta et al.",
        chapter="ch-10-image-segmentation", level="mid",
        tagline="把 200 万像素切成 200 个颜色一致、大小均匀的小方块，后续处理快 1000 倍",
        analogy="把一张大图当大蛋糕，先按网格切小方块，然后每块根据颜色微调，最后得到一堆大小差不多、颜色统一的小块",
        scene="分割预处理、显著性检测、光流加速、弱监督标注、深度估计超像素化、风格迁移",
        pros=["速度极快","超像素紧凑均匀","内存小","仅 2 参数","边界贴合好"],
        cons=["必须指定超像素数","OpenCV 主分支没有","紧凑度 m 影响边界","不是分割终点"]),
    concepts=[
        ("超像素",
         "超像素 = 一组视觉上相似、位置相近的像素组成的小区域。用几百个超像素代替几百万个像素做后续处理，计算量降几个数量级，同时保留边缘结构。",
         "flowchart LR\n  A[\"原图 200 万像素\"] --> B[\"SLIC\"]\n  B --> C[\"200 个超像素\"]\n  C --> D[\"后续分割/检测/光流<br/>快 1000 倍\"]"),
        ("五维 LabXY 空间",
         "SLIC 在 (L, a, b, x, y) 五维空间做 K-Means 聚类：三个颜色通道加两个空间坐标。颜色距离和空间距离用不同权重平衡。",
         None),
        ("紧凑度 m",
         "距离定义 D = d_color + (m/S)·d_spatial，其中 S 是超像素期望边长（S=sqrt(N/K)）。m 控制「形状方正 vs 贴紧边界」：m 小→形状不规则但贴边界；m 大→超像素方正。",
         None),
        ("局部搜索",
         "标准 K-Means 在全图搜最近中心，SLIC 只在中心周围 2S×2S 区域搜索——复杂度从 O(NKI) 降到 O(NI)，即**线性复杂度**。",
         None),
    ],
    arch_steps=[
        ("初始化中心", "按 S 间隔在网格上采样 K 个初始聚类中心，微调到 3×3 邻域内梯度最低点"),
        ("分配", "对每个中心，在 2S×2S 范围内把像素归到最近的中心（LabXY 距离）"),
        ("更新", "重新计算每个类的平均 (L,a,b,x,y) 作为新中心"),
        ("收敛", "重复分配-更新直到残差 < 阈值（通常 10 次迭代内收敛）"),
        ("后处理", "连通域增强，消除过小孤立区域（合并到最近邻超像素）"),
    ],
    opencv='''# SLIC 在 opencv-contrib 的 ximgproc 模块，或直接用 skimage
from skimage.segmentation import slic, mark_boundaries
from skimage import img_as_float
image = img_as_float(cv2.imread("scene.jpg")[:,:,::-1])  # BGR→RGB
segments = slic(image, n_segments=200, compactness=10, sigma=1, start_label=0)
boundaries = mark_boundaries(image, segments, color=(1,0,0))
# OpenCV contrib 版本（如果装了）
# slic = cv2.ximgproc.createSuperpixelSLIC(img, region_size=20, ruler=10)
# slic.iterate(10); labels = slic.getLabels()''',
    numpy_impl='''def slic_simple(img_lab, K=200, m=10, iters=10):
    """简化 SLIC"""
    h, w = img_lab.shape[:2]
    N = h*w
    S = int((N/K)**0.5)
    # 初始化中心
    centers = []
    for y in range(S//2, h, S):
        for x in range(S//2, w, S):
            centers.append([img_lab[y,x,0],img_lab[y,x,1],img_lab[y,x,2],y,x])
    centers = np.array(centers, dtype=np.float64)
    labels = -np.ones((h,w), dtype=np.int32)
    dist = np.full((h,w), np.inf)
    for it in range(iters):
        for i, c in enumerate(centers):
            yc, xc = int(c[3]), int(c[4])
            for y in range(max(0,yc-2*S), min(h,yc+2*S+1)):
                for x in range(max(0,xc-2*S), min(w,xc+2*S+1)):
                    dlab = np.sqrt(np.sum((img_lab[y,x]-c[:3])**2))
                    dxy = np.sqrt((y-c[3])**2+(x-c[4])**2)
                    D = dlab + (m/S)*dxy
                    if D < dist[y,x]:
                        dist[y,x] = D
                        labels[y,x] = i
        # 更新中心
        for i in range(len(centers)):
            mask = labels==i
            if mask.sum()==0: continue
            ys, xs = np.where(mask)
            centers[i,3] = ys.mean(); centers[i,4] = xs.mean()
            centers[i,:3] = img_lab[ys,xs].mean(0)
    return labels''',
    pitfalls=[
        ("n_segments 设得太大或太小", "设 10000 个超像素和像素级差不多没意义；设 10 个就是大色块。",
         "通常 **200–1000** 个超像素够用；一般经验：**每超像素 ~500–1000 像素**。"),
        ("compactness m 理解错", "m=1 超像素完全贴边界但形状破碎；m=50 几乎是方块。",
         "默认 **m=10** 是论文推荐；要形状方正 m=20–40；要贴边界 m=1–5。"),
        ("以为 OpenCV 主模块有 SLIC", "`import cv2; cv2.SLIC_create` 报错。",
         "需要 `opencv-contrib-python`：`cv2.ximgproc.createSuperpixelSLIC`；或者用 `skimage.segmentation.slic`。"),
        ("没转 Lab 直接 RGB 算", "用 RGB 空间算欧氏距离不符合人眼感知。",
         "SLIC 论文用 CIELAB，**务必先 BGR→Lab**（skimage 内部会处理）。"),
    ],
    koujue="""超像素两百个起头，按目标复杂度往上加；
紧凑度 m 十是默认，要贴边减小要方正加；
sigma 一高斯平滑先，抗噪声；
OpenCV 主模块没有它，skimage 或 contrib 才是家；
距离公式色加空间，m 除以 S 来加权；
局部搜索两倍 S，线性复杂度飞快跑。""",
    params=[
        ("n_segments", "期望超像素数", "200", "细", "粗"),
        ("compactness (m)", "紧凑度", "10", "方正", "贴边界"),
        ("sigma", "预处理高斯 sigma", "1", "平滑", "保留细节"),
        ("max_iter", "迭代次数", "10", "精确", "快"),
    ],
    tips=[
        ("SLIC 后接其他算法",
         "```python\n# 以超像素为单元做后续处理\nsp_vals = [image[segments==i].mean(0) for i in range(segments.max()+1)]\n# K-Means 在超像素上做 → 最终分割，速度快 100 倍\n```"),
        ("边界可视化",
         "`skimage.segmentation.mark_boundaries` 能直接画出超像素边缘，适合 debug。"),
        ("enforce_connectivity",
         "skimage 有 `enforce_connectivity=True` 参数（默认），自动把过小孤立区域合并到邻居。"),
    ],
    perf=[
        ("skimage SLIC (640×480, K=200)", "~50 ms", "CPU"),
        ("opencv-contrib SLIC", "~10 ms", "CPU C++ 优化"),
    ],
    notes=""
)

print("batch2 done: watershed, grabcut, kmeans, meanshift, slic")
