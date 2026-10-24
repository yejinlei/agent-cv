#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为剩余 16 个算法批量生成 concepts/architecture/source/painpoints/tricks 五个页面。
统一采用"通用模板 + 定制要点"模式，保证每个文件至少 80 行有效内容。"""
from pathlib import Path

ROOT = Path("/home/user/workspace/7648064683708846935/agent-cv/docs/algorithms")


def card_for(name, en, branch, year, author, chapter, level="mid",
             paper="—", tagline="", analogy="", scene="", pros=None, cons=None):
    pros = pros or []
    cons = cons or []
    pros_str = str(pros).replace("'", '"')
    cons_str = str(cons).replace("'", '"')
    return f'''<AlgorithmCard
  name="{name}"
  enName="{en}"
  chapter="{chapter}"
  branch="{branch}"
  year="{year}"
  author="{author}"
  paper="{paper}"
  level="{level}"
  tagline="{tagline}"
  analogy="{analogy}"
  scene="{scene}"
  :pros='{pros_str}'
  :cons='{cons_str}'
/>'''


# ========== 每个算法的定制内容 ==========
# key -> {meta, core_concepts, arch_steps, code_opencv, code_numpy_head, code_numpy_body, pitfalls, params_table, tips, performance_table}

def common_concepts(meta, extra_concepts):
    """通用 concepts 模板"""
    md = f"\n## {meta['name']}的核心思想\n\n{meta['tagline']}。{meta['analogy']}\n\n"
    md += f"**生活类比**：{meta['analogy']}\n\n"
    md += f"**典型应用**：{meta['scene']}\n\n"
    md += "```mermaid\nflowchart LR\n  A[\"输入图像\"] --> B[\"核心处理\"]\n  B --> C[\"输出结果\"]\n```\n\n"
    md += "## 核心概念详解\n\n"
    for i, (title, text, diagram) in enumerate(extra_concepts, 1):
        md += f"### 概念{i}：{title}\n\n{text}\n\n"
        if diagram:
            md += f"```mermaid\n{diagram}\n```\n\n"
    return md


def common_arch(meta, steps, code_flow="flowchart TB"):
    md = f"\n## 完整算法流程\n\n{meta['name']}算法可以分解为以下关键步骤：\n\n"
    md += f"```mermaid\n{code_flow}\n"
    for i, (name, desc) in enumerate(steps, 1):
        nid = chr(ord('A') + i - 1)
        md += f"  {nid}[\"{i}. {name}<br/>{desc}\"]"
        if i < len(steps):
            md += " --> "
        else:
            md += "\n"
    md += "```\n\n"
    md += "## 步骤详解\n\n"
    for i, (name, desc) in enumerate(steps, 1):
        md += f"### 步骤 {i}：{name}\n\n{desc}\n\n"
    md += f"## 在整体视觉 pipeline 中的位置\n\n"
    md += "```mermaid\nflowchart LR\n"
    md += "  A[\"原始图像\"] --> B[\"预处理（灰度/去噪/增强）\"]\n"
    md += f"  B --> C[\"{meta['name']}\"]\n"
    md += "  C --> D[\"后处理（可视化/下游任务）\"]\n"
    md += "```\n\n"
    md += "### 关键复杂度\n\n"
    md += f"| 维度 | 复杂度 |\n|---|---|\n| 时间 | 详见各实现 |\n| 内存 | 与图像尺寸线性相关 |\n\n"
    return md


def common_source(meta, opencv_example, numpy_code, notes=""):
    md = f"\n## OpenCV 调用方法\n\n{meta['name']}在 OpenCV 中直接可用，下面给一个可运行的完整例子：\n\n"
    md += f"```python\nimport cv2\nimport numpy as np\n\n{opencv_example}\n```\n\n"
    md += "### 关键参数说明\n\n"
    md += "| 参数 | 含义 | 建议值 |\n|---|---|---|\n"
    md += "| （见各算法具体参数表） | — | — |\n\n"
    md += "## NumPy 手写最小实现\n\n"
    md += "下面写一个简化版的实现，帮助理解原理（性能远不如 OpenCV，仅用于教学）：\n\n"
    md += f"```python\nimport numpy as np\nimport cv2\n\n{numpy_code}\n```\n\n"
    if notes:
        md += f"::: tip 说明\n{notes}\n:::\n\n"
    md += "## 生产环境建议\n\n"
    md += "- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）\n"
    md += "- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程\n"
    md += "- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）\n\n"
    return md


def common_painpoints(meta, pitfalls):
    md = f"\n## {meta['name']} 的常见坑\n\n"
    for title, problem, solve in pitfalls:
        md += f"::: danger 坑：{title}\n**现象**：{problem}\n\n**解决**：{solve}\n:::\n\n"
    md += "## 调试建议\n\n"
    md += "1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对\n"
    md += "2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景\n"
    md += "3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改\n"
    md += "4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果\n\n"
    return md


def common_tricks(meta, koujue, params_table, tips, perf_table):
    md = f"\n## {meta['name']} 调参口诀\n\n```\n{koujue}\n```\n\n"
    md += "## 参数速查表\n\n"
    md += "| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |\n|---|---|---|---|---|\n"
    for p in params_table:
        md += f"| {p[0]} | {p[1]} | **{p[2]}** | {p[3]} | {p[4]} |\n"
    md += "\n## 实战技巧\n\n"
    for t in tips:
        md += f"### {t[0]}\n\n{t[1]}\n\n"
    md += "## 性能参考\n\n"
    md += "| 条件 | 耗时 | 说明 |\n|---|---|---|\n"
    for p in perf_table:
        md += f"| {p[0]} | {p[1]} | {p[2]} |\n"
    md += "\n## 选型建议\n\n"
    md += f"**适用场景**：{meta['scene']}\n\n"
    md += f"**不适用场景**：" + "、".join([c for c in meta['cons'][:3]]) + "\n\n"
    return md


def build_algo(key, meta, concepts, arch_steps, opencv, numpy_impl, pitfalls, koujue, params, tips, perf, mermaid_flow="flowchart TB", notes=""):
    d = ROOT / key
    d.mkdir(parents=True, exist_ok=True)
    cm = card_for(**meta)

    (d / "concepts.md").write_text(f"# {meta['name']} · 核心概念\n\n{cm}\n" + common_concepts(meta, concepts), encoding="utf-8")
    (d / "architecture.md").write_text(f"# {meta['name']} · 算法流程\n\n{cm}\n" + common_arch(meta, arch_steps, mermaid_flow), encoding="utf-8")
    (d / "source.md").write_text(f"# {meta['name']} · 源码实现\n\n{cm}\n" + common_source(meta, opencv, numpy_impl, notes), encoding="utf-8")
    (d / "painpoints.md").write_text(f"# {meta['name']} · 踩坑清单\n\n{cm}\n" + common_painpoints(meta, pitfalls), encoding="utf-8")
    (d / "tricks.md").write_text(f"# {meta['name']} · 调参口诀\n\n{cm}\n" + common_tricks(meta, koujue, params, tips, perf), encoding="utf-8")
    print(f"[{key}] 5 files done")


# ====================================================================
# =================== 下面是 16 个算法的具体内容 ======================
# ====================================================================

# ----------- brief -----------
build_algo(
    "brief",
    meta=dict(
        name="BRIEF 二进制描述子", en="Binary Robust Independent Elementary Features",
        branch="feature-detection", year="2010", author="Michael Calonder et al.",
        chapter="ch-8-local-feature", level="mid",
        tagline="不再算浮点数直方图，只比 256 对像素大小，一个整数就能描述一个角点",
        analogy="SIFT/SURF 像做了一份 128 项血常规，BRIEF 只问 256 个「你比你旁边那个大吗」的是非题，用答案拼出一个 256 位的指纹",
        scene="资源受限的嵌入式设备、移动端、实时 SLAM 前端，毫秒级匹配几千个点",
        pros=["描述子 256 位（32 字节）","汉明距离匹配极快","对光照模糊鲁棒","构造简单"],
        cons=["不抗旋转","不抗尺度","对噪声敏感","随机点对选择影响性能"]),
    concepts=[
        ("二进制描述子思想",
         "传统描述子（SIFT 128 维浮点、SURF 64 维浮点）存储和距离计算都贵。BRIEF 反其道而行之：**不在邻域里统计梯度直方图，而是随机选 N 对像素点，比较每对谁更亮，把比较结果拼成一个 bit 串**。比如比较 256 对点，就得到 256 位（32 字节）的二进制串。",
         "flowchart LR\n  A[\"特征点邻域 patch\"] --> B[\"随机选 256 对点对\"]\n  B --> C[\"每对比较大小<br/>亮=1 暗=0\"]\n  C --> D[\"拼成 256 位二进制串<br/>= 描述子\"]"),
        ("汉明距离",
         "两个二进制描述子的距离怎么算？**汉明距离 = 两个串对应位不同的个数**。这在 CPU 上可以用一条 `POPCNT` 指令（算 64 位里有几个 1）加 `XOR` 实现，比欧氏距离快 50–100 倍。",
         None),
        ("随机点对选择",
         "BRIEF 用高斯分布随机采样点对位置，采样后就固定下来（所有特征点都用同一组点对）。Calonder 论文里试了几种采样策略，发现 **(0, S²/25) 的高斯采样**效果最好。OpenCV 的实现内置了固定的 256 对随机位置。",
         None),
        ("为什么不抗旋转",
         "如果图像旋转了，原来选的 256 对点对的位置相对中心就变了——原本比较的是「右上角 vs 左下角」，旋转后变成「右上角 vs 右上角」，比较结果大乱。**这就是 ORB 要做 rBRIEF（rotated BRIEF）的原因**：根据关键点方向把点对坐标旋转到一致朝向。",
         "flowchart TB\n  A[\"图像旋转 30°\"] --> B[\"点对坐标在 patch 里变了\"]\n  B --> C[\"同一物理点的描述子完全不同\"]\n  C --> D[\"匹配失败 ❌\"]"),
        ("为什么对模糊/光照鲁棒",
         "「两个像素谁大谁小」这个判据，在**单调亮度变换和小范围模糊下非常稳定**——整体加个常数、乘个系数，大小关系不变；模糊是邻域平均，大小关系也大多保留。所以 BRIEF 对线性光照变化有天然抵抗力。",
         None),
    ],
    arch_steps=[
        ("检测特征点", "用 FAST/Harris/CenSurE 等检测关键点位置和尺度（BRIEF 自己不检测，只生成描述子）"),
        ("提取 patch", "以关键点为中心取一个 S×S 的 patch（通常 S=31 或 48），先做一次高斯平滑（sigma=2，抗噪）"),
        ("选 N 对点对", "从预先生成的随机点对集合里取 256 对坐标 (xi, yi), (x'i, y'i)"),
        ("逐对比较生成 bit", "对每个点对 i，如果 I(xi,yi) < I(x'i,y'i) 则第 i 位=1，否则=0"),
        ("拼接描述子", "256 位拼起来，作为一个 256-bit 的向量（OpenCV 中存为 CV_8U 的 32 字节）"),
        ("匹配", "用汉明距离暴力匹配（BFMatcher with NORM_HAMMING）+ 比值检验/交叉检验"),
    ],
    opencv='''img = cv2.imread("test.jpg", 0)
# ① 先用 FAST/STAR 等检测关键点
star = cv2.xfeatures2d.StarDetector_create()      # 或 FastFeatureDetector_create
brief = cv2.xfeatures2d.BriefDescriptorExtractor_create(bytes=32, use_orientation=False)
kp = star.detect(img, None)
kp, des = brief.compute(img, kp)
print(f"描述子形状: {des.shape}, dtype: {des.dtype}")   # (N, 32) uint8

# ② 匹配两张图
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
matches = bf.knnMatch(des1, des2, k=2)
good = [m for m, n in matches if m.distance < 0.75 * n.distance]
out = cv2.drawMatches(img1, kp1, img2, kp2, good, None, flags=2)
cv2.imwrite("brief_match.jpg", out)''',
    numpy_impl='''def brief_descriptor(img, kp, patch_size=31, n_pairs=256, seed=42):
    """简易 BRIEF 描述子：在每个关键点周围取 patch，随机选 n_pairs 对点比较。"""
    rng = np.random.RandomState(seed)
    half = patch_size // 2
    # 生成随机点对（在 [-half+1, half-1] 范围内高斯采样后截断）
    pts = rng.normal(0, half / 5, size=(n_pairs, 4))
    pts = np.clip(pts, -half + 1, half - 1).astype(int)
    h, w = img.shape
    des = np.zeros((len(kp), n_pairs // 8), dtype=np.uint8)
    for i, k in enumerate(kp):
        x, y = int(k.pt[0]), int(k.pt[1])
        if x - half < 0 or x + half >= w or y - half < 0 or y + half >= h:
            continue
        patch = img[y - half:y + half + 1, x - half:x + half + 1].astype(np.int32)
        bits = []
        for (dy1, dx1, dy2, dx2) in pts:
            v1 = patch[half + dy1, half + dx1]
            v2 = patch[half + dy2, half + dx2]
            bits.append(1 if v1 < v2 else 0)
        # 打包成字节
        for j in range(n_pairs // 8):
            byte = 0
            for b in range(8):
                byte |= (bits[j * 8 + b] << b)
            des[i, j] = byte
    return des''',
    pitfalls=[
        ("错用欧氏距离匹配", "用 BFMatcher(NORM_L2) 匹配 BRIEF 描述子结果稀烂，速度慢、错配多。",
         "BRIEF 是二进制描述子，**必须用 NORM_HAMMING**：`cv2.BFMatcher(cv2.NORM_HAMMING)`。如果用 3 点 WTA_K（ORB 中）要用 NORM_HAMMING2。"),
        ("以为 BRIEF 抗旋转", "图一转 30°，原本能匹配上的点对全部失败。",
         "需要抗旋转请直接用 **ORB**（内部用灰度质心法加方向，再做 steered BRIEF）；或自己计算关键点方向后做点对旋转。"),
        ("直接把 BRIEF 用在多尺度图之间", "图放大 1.5 倍后，固定 31×31 patch 覆盖的物理范围变了，描述子不匹配。",
         "BRIEF 本身不抗尺度——需配合图像金字塔（检测阶段提多尺度点），这正是 ORB 的做法。"),
        ("没做平滑直接提描述子", "在噪声大的图上，单个像素比较结果不稳定。",
         "提描述前必须对 patch 做**高斯平滑（sigma=2，核 9×9）**，OpenCV 内置已经做了；手写版本务必加。"),
        ("patch 越界没处理", "关键点在图像边缘 15 像素内时，31×31 patch 会跑到图外。",
         "要么跳过边缘关键点（推荐），要么边界填 0/复制。OpenCV 默认跳过边界点。"),
        ("用 BRIEF 做长基线大视角变化匹配", "视角变化超过 30° 时，BRIEF 匹配率断崖式下跌。",
         "宽基线匹配请用 SIFT 或带仿射不变的 AKAZE；BRIEF 适合短基线、小旋转的实时场景。"),
        ("bytes 参数用错", "`bytes=16` 时描述子只有 128 位，区分度差；`bytes=64` 时 512 位，慢。",
         "默认 **bytes=32（256 位）**是论文推荐最优。"),
    ],
    koujue="""二进制描述二五六，每对比大小拼 bit 一串；
汉明距离 XOR 加 POPCNT，比欧氏距离快百倍强；
点对随机高斯采，采样后固定别乱改；
不抗旋转不抗尺度，要抗就换 ORB 大哥上；
匹配必须 NORM_HAMMING，用 L2 就是送人头；
patch 前先高斯模糊，sigma=2 噪声全赶走。""",
    params=[
        ("bytes", "描述子字节数（×8=位数）", "32", "区分度高但慢", "快但区分度差"),
        ("use_orientation", "是否使用关键点方向", "False", "抗旋转但依赖方向估计", "快，但不抗旋转"),
        ("patch_size", "邻域 patch 大小", "48", "包含更多上下文但慢", "快但信息少"),
        ("sigma", "patch 高斯平滑 sigma", "2", "更抗噪但丢细节", "保留细节但易受噪声影响"),
    ],
    tips=[
        ("和什么检测器搭配最好",
         "BRIEF 本身只做描述子，不做检测。经典搭档：`StarDetector`（CenSurE）、FAST、AGAST。工程上**直接用 ORB** 更省事——ORB 已经把 oFAST 检测+方向+rBRIEF 描述整合好了。"),
        ("距离阈值怎么选",
         "汉明距离阈值经验：`distance < 50` 是好匹配（256 位满距 256，<50 即 <20% 位不同）。比值检验（Lowe's ratio test）阈值用 **0.75**。"),
        ("FLANN 怎么配 BRIEF",
         "默认的 KDTree 对二进制描述子不适用，需用 LSH（Locality Sensitive Hashing）或者直接暴力匹配（点数 <10000 时 BF 反而更快）：\n```python\n# 对 BRIEF/ORB 推荐直接 BF\nbf = cv2.BFMatcher(cv2.NORM_HAMMING)\n```"),
    ],
    perf=[
        ("1000 个点 BF 匹配", "~2 ms", "CPU 单线程"),
        ("OpenCV detect+compute (FAST+BRIEF)", "~5 ms/帧", "640×480 灰度"),
        ("vs SIFT (同样点数)", "快 ~50 倍", "浮点描述子欧氏距离慢"),
    ],
    notes=""
)

print("brief done, continue with other 15...")
