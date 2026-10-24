#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量生成第二批补充算法：BRISK / AKAZE / CLAHE / Distance Transform /
Connected Components / Region Growing / Gabor / CSRT"""
import os, textwrap
from pathlib import Path

ROOT = Path("/home/user/workspace/7648064683708846935/agent-cv/docs/algorithms")

def wrap(s, indent=0):
    return textwrap.dedent(s).strip("\n")

def card(meta):
    return f"""<script setup>
import AlgorithmCard from '/.vitepress/components/AlgorithmCard.vue'
</script>

<AlgorithmCard
  name="{meta['name']}"
  enName="{meta['en']}"
  chapter="{meta['chapter']}"
  branch="{meta['branch']}"
  year="{meta['year']}"
  author="{meta['author']}"
  paper="{meta['paper']}"
  level="{meta['level']}"
  tagline="{meta['tagline']}"
  analogy="{meta['analogy']}"
  scene="{meta['scene']}"
  :pros={{{__import__('json').dumps(meta['pros'], ensure_ascii=False)}}}
  :cons={{{__import__('json').dumps(meta['cons'], ensure_ascii=False)}}}
/>
"""

def index_md(meta):
    return card(meta) + f"""

## 一分钟速览

**{meta['name']}**（{meta['en']}，{meta['year']}，{meta['author']}）
{meta['onesentence']}

<ChildPages />
"""

def paper_md(meta):
    return f"""# 论文精读：{meta['name']}

<script setup>
import {{ VPTeamPageTitle }} from 'vitepress/theme'
</script>

{card(meta)}

## 论文信息

| 项 | 内容 |
|---|---|
| 论文标题 | {meta['paper_title']} |
| 作者 | {meta['author']} |
| 发表年份/会议 | {meta['year']} |
| 引用数（约） | {meta['citations']} |
| 核心贡献 | {meta['contrib']} |
| OpenCV 实现 | `{meta['cv_func']}` |

## 论文为什么被写出来？

{meta['paper_why']}

## 核心创新点

{meta['paper_innov']}

## 论文里的关键结果

{meta['paper_result']}

## 论文的局限与后人改进

{meta['paper_limit']}

## 论文阅读建议

- 初读：只看 abstract + {meta['read_tip']}
- 精读：再看算法流程图与 {meta['read_tip2']}
- 工程落地：直接对照 OpenCV `{meta['cv_func']}` 源码，**不必复现论文**
"""

def concepts_md(meta):
    return f"""# 核心概念：{meta['name']}

{card(meta)}

{meta['concepts_body']}
"""

def architecture_md(meta):
    return f"""# 算法流程：{meta['name']}

{card(meta)}

## 整体流程图

```mermaid
flowchart TD
{meta['mermaid']}
```

## 步骤详解

{meta['steps_body']}

## 参数对照（论文 vs OpenCV 默认 vs 工程建议）

| 参数 | 论文建议 | OpenCV 默认 | 工程建议 | 调参影响 |
|---|---|---|---|---|
{meta['params_table']}

## 复杂度分析

{meta['complexity']}
"""

def source_md(meta):
    return f"""# 源码走读：{meta['name']}

{card(meta)}

## OpenCV 最简调用

```python
{meta['opencv_code']}
```

## 手写最小实现（理解原理）

```python
{meta['naive_code']}
```

## OpenCV 源码核心片段解读

{meta['source_insight']}
"""

def painpoints_md(meta):
    return f"""# 实战踩坑：{meta['name']}

{card(meta)}

## 最常见的 8 个坑

{meta['painpoints_body']}

## 失败案例诊断流程

```mermaid
flowchart LR
{meta['diag_mermaid']}
```
"""

def tricks_md(meta):
    return f"""# 调参技巧：{meta['name']}

{card(meta)}

## 五字口诀

**{meta['koujue']}**

## 调参顺序（按这个顺序调，少走弯路）

{meta['trick_order']}

## 与其他算法的搭配组合

{meta['combos']}

## 调优 Checklist

- [ ] 图像已做必要的预处理（{meta['checklist_pre']}）
- [ ] 核心参数已按场景粗调到合理区间
- [ ] 输出结果做了必要的后处理（{meta['checklist_post']}）
- [ ] 速度/精度做了 benchmark
"""

def build(meta):
    d = ROOT / meta['slug']
    d.mkdir(parents=True, exist_ok=True)
    (d / 'index.md').write_text(index_md(meta), encoding='utf-8')
    (d / 'paper.md').write_text(paper_md(meta), encoding='utf-8')
    (d / 'concepts.md').write_text(concepts_md(meta), encoding='utf-8')
    (d / 'architecture.md').write_text(architecture_md(meta), encoding='utf-8')
    (d / 'source.md').write_text(source_md(meta), encoding='utf-8')
    (d / 'painpoints.md').write_text(painpoints_md(meta), encoding='utf-8')
    (d / 'tricks.md').write_text(tricks_md(meta), encoding='utf-8')
    print(f"  ✓ {meta['slug']}")

# ============ 算法元数据 ============
ALGOS = []

# ---------- 1. BRISK ----------
ALGOS.append({
    "slug": "brisk",
    "name": "BRISK 二进制鲁棒不变可伸缩关键点",
    "en": "Binary Robust Invariant Scalable Keypoints",
    "year": "2011",
    "author": "Stefan Leutenegger / Margarita Chli / Roland Siegwart",
    "branch": "feature-detection",
    "paper": "BRISK (ICCV 2011)",
    "chapter": "ch08",
    "level": "mid",
    "paper_title": "BRISK: Binary Robust Invariant Scalable Keypoints",
    "citations": "~4500+",
    "contrib": "用 AGAST 角点（FAST 改良）+ 二进制均匀采样模式 + 短/长点对划分，兼顾尺度旋转不变性与速度",
    "cv_func": "cv2.BRISK_create()",
    "tagline": "FAST 找角点 + 同心圆圈采样 + 长短点对分工，速度比 SIFT 快一个量级还带尺度旋转",
    "analogy": "ORB 像一个快枪手：拔枪快、出弹快，但准星简单、打不远；BRISK 像一个特种兵：在战场上布好同心圆阵地（多层采样），远处点对用来估方向（长点对），近处点对用来拼指纹（短点对），512 位描述子比 ORB 的 256 位更抗噪。",
    "scene": "无人机航拍拼接、SLAM（尤其是 OKVIS 作者的成名作）、移动 AR、需要尺度不变但算力有限的嵌入式场景。",
    "pros": ["尺度+旋转不变", "二进制 512 位，汉明距离匹配快", "比 ORB 更稳、比 SIFT/SURF 快", "专利免费（可商用）", "OpenCV 原生支持"],
    "cons": ["速度略慢于 ORB（仍快于 SIFT）", "采样点固定模式参数多", "对极端视角变化弱于 AKAZE", "描述子更长（64 字节）"],
    "onesentence": "用 AGAST 在多尺度金字塔上找角点，再用精心设计的同心圆采样模式生成 512 位二进制描述子，长点对估朝向、短点对拼指纹，是「免费版 SIFT」的有力竞争者。",

    "paper_why": """2010–2011 这两年，二进制描述子爆发——BRIEF（2010）证明了「比像素大小」能打败浮点描述子，但它**没有尺度和旋转不变性**；ORB（2011）给 BRIEF 加了旋转，但尺度只靠简单金字塔，而且是 FAST 角点+BRIEF 的快速组合。作者希望在**不牺牲太多速度**的前提下，做出一个：

1. **真正的多尺度**检测（不只是金字塔上跑 FAST）
2. **旋转不变**（有方向估计算法）
3. **二进制**描述子（匹配快）
4. **对模糊、压缩噪声**更鲁棒

BRISK 就是在这样的动机下诞生的——它的名字里「Scalable」就是指尺度，「Invariant」就是指旋转。""",

    "paper_innov": """**创新 1：AGAST 角点检测器**
在 FAST 基础上扩展了决策树，训练了一个能在更多邻域配置下快速判定角点的加速版本（Adaptive and Generic Accelerated Segment Test），比 FAST 快约 15%。

**创新 2：同心圆环采样模式**
不是 BRIEF 的随机点对，而是在关键点周围构造**多层同心圆**（半径从 0 到约 21 像素），每层圆周均匀取 N 个点（总计 60 个采样点）。每个采样点用高斯核做模糊预处理，避免混叠。

**创新 3：短点对 / 长点对分工**
60 个采样点共有 C(60,2)=1770 对点对，按距离分两类：
- **长点对（距离 > 阈值 d_max=9.75px）**：用于估计关键点主方向（通过局部梯度平均）
- **短点对（距离 < 阈值 d_min=5.83px）**：共 512 对，按短点对结果组成 512 位二进制描述子
- 中间距离的点对**直接丢弃**（噪声大、贡献小）

**创新 4：尺度空间上的亚像素精定位**
在 n 个 octave 和 n-1 个 intra-octave 共 2n-1 层图像上找角点，再沿尺度轴做二次拟合，得到**亚像素 + 亚尺度**的精确定位。""",

    "paper_result": """在标准的 Mikolajczyk 数据集上：
- 匹配性能：略优于 ORB、SURF，接近 SIFT
- 速度：比 SIFT 快 **约 10×**，比 SURF 快约 5×，比 ORB 慢约 2–3×
- 旋转鲁棒：优于 ORB（因为方向估计基于更多点对）
- 模糊鲁棒：优于 BRIEF/ORB（采样点做了高斯平滑）""",

    "paper_limit": """- 采样模式是**硬编码**的同心圆，不是数据驱动学习的（后来 FREAK 用视网膜采样模式改进）
- 仍然是**角点**检测，对 blob 类关键点不如 SIFT/SURF/KAZE
- 描述子 512 位比 ORB 256 位长一倍，存储/带宽加倍
- 速度被后来的 AKAZE（非线性尺度空间）超越""",

    "read_tip": "看 Fig.2（同心圆采样图）和 Fig.3（长短点对划分）",
    "read_tip2": "方向估计的公式（6）和描述子生成（7）",

    "concepts_body": """## 1. AGAST 角点

FAST 的升级：FAST 的 ID3 决策树是在特定数据集上训练出来的，换到新场景可能不够快。AGAST 通过**决策树组合**，把两棵针对不同邻域配置的树融合，让角点判断速度更快、泛化更好。

> 生活比方：FAST 像一个只会背一套问答的考官；AGAST 像带了两套题库的考官，遇到不同类型的题都能快速切换。

## 2. 同心圆环采样模式

在关键点周围画若干个同心圆（从内到外共 4–6 层），每个圆上取 N 个均匀分布的点，对每个点做 σ 正比于圆半径的高斯模糊（越外圈越模糊），总共 60 个采样点。

这样的好处是：
- **覆盖均匀**：不遗漏任何方向
- **尺度对应**：模糊半径随位置变，相当于在特征空间做了尺度归一
- **容易旋转对齐**：圆周分布天然适合旋转

## 3. 长点对估计主方向

把所有**长距离**点对 (p_i, p_j) 的局部梯度 `g(p_i - p_j)` 按强度加权累加，得到一个全局方向向量，取其角度作为关键点主方向。然后**把整个采样图案按这个角度旋转**，再去比较短点对——这就是旋转不变性的来源。

## 4. 短点对生成二进制描述子

把采样图案旋转到主方向对齐后，对 512 个**短距离**点对逐一比较：若 `I(p_i^α) < I(p_j^α)` 取 1，否则取 0。512 个 bit 拼成一个 64 字节的描述子。

用短点对的原因：**短距离点对之间的像素差异更稳定**，不容易受全局光照影响；长距离的差更容易被视角/光照干扰。

## 5. 多尺度金字塔与亚尺度精定位

构造 n 个 octave（c_i，尺寸减半）+ n-1 个 intra-octave（d_i，位于 c_i 和 c_{i+1} 之间），共 2n-1 层。在每层跑 AGAST，然后做尺度方向的非极大值抑制，最后对响应值沿尺度轴做二次拟合，得到亚尺度精度。

## 6. 汉明距离匹配

和 ORB/BRIEF 一样，两个描述子的距离用 `popcount(xor(a,b))` 计算，CPU 上一条指令完成 64 位 popcount，**极快**。""",

    "mermaid": """
    A[输入图像] --> B[构造多尺度金字塔<br/>n octaves + n-1 intra-octaves]
    B --> C[每层跑 AGAST 角点检测]
    C --> D[跨层 NMS + 二次拟合<br/>亚像素+亚尺度定位]
    D --> E[在每个关键点周围<br/>画同心圆采样 60 点<br/>按半径做高斯模糊]
    E --> F[长点对梯度累加→主方向 θ]
    F --> G[旋转采样图案到 θ 对齐]
    G --> H[512 个短点对比大小→512位描述子]
    H --> I[输出关键点+描述子]
""",

    "steps_body": """### Step 1：构建尺度金字塔

建立 n 个 octave（每次下采样 2 倍，类似 SIFT），以及 n-1 个夹在中间的 intra-octave（下采样 1.5 倍左右），共 2n-1 层图像。在 OpenCV 实现中默认 n=4，共 7 层。

### Step 2：每层用 AGAST 找角点

AGAST 用训练好的决策树判断 Bresenham 圆上 16 个点的亮度，找出连续 N 个都比中心亮 t 档或暗 t 档的点，作为候选角点。比 FAST 快 ~15%，且支持多阈值。

### Step 3：跨尺度 NMS

对每个候选点，在同层 8 邻域 + 上下两层对应位置做 NMS，只保留**邻域里角点分数最大**的点。然后沿尺度轴做一维二次拟合，定位到亚尺度（不是离散层编号，而是连续的 σ 值）。

### Step 4：同心圆采样

在关键点的关键点尺度 σ 对应的半径上，画若干同心圆（默认 4–6 层），总共采样 60 个点，每个采样点做 σ_i 倍高斯模糊：

```
采样点位置：同心圆上均匀分布
每个点的模糊半径：σ_i = r_i · σ / 2（半径越大，模糊越狠）
```

### Step 5：长点对估主方向

遍历所有长距离点对（距离 > 9.75px），计算局部梯度 `(I_j - I_i) · (p_j - p_i) / |p_j - p_i|²`（其实就是把差值投影到点对方向），累加所有长点对贡献，得到一个 2D 向量 `g`，其角度就是主方向 θ。

### Step 6：旋转对齐 + 短点对比大小

把整个 60 点采样图案按主方向 θ 旋转，然后对预定义的 512 对**短距离**点对（距离 < 5.83px）逐一比较亮度，得到 512 个 bit。

### Step 7：输出

每个关键点带：位置 (x,y)、尺度 σ、方向 θ、响应值 score、512 位描述子。""",

    "params_table": """| thresh | 60–80 | 30 | 30（默认），高纹理场景调到 60 | 值越大，点越少、越可靠 |
| octaves | 4 | 4 | 3–4（嵌入式可 2） | 层数越多，尺度覆盖越广、速度越慢 |
| patternScale | 1.0 | 1.0 | 1.0 基本不改 | 采样图案相对关键点尺度的缩放 |""",

    "complexity": """- 检测：O(N · W · H)，N 为决策树深度（与 ORB 同量级）
- 描述子：每个关键点 O(60²)=O(3600) 次像素比较，比 ORB 多，但常数很小
- 匹配：512 位汉明距离 = 8 条 POPCNT 指令/对，超快
- 工程实测：640×480 图上 10–30ms（CPU 单线程），比 SIFT 快 10×""",

    "opencv_code": """import cv2
img = cv2.imread('scene.jpg', 0)

brisk = cv2.BRISK_create(thresh=30, octaves=4)
kps, des = brisk.detectAndCompute(img, None)

out = cv2.drawKeypoints(img, kps, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# 匹配
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)
matches = sorted(matches, key=lambda x: x.distance)
""",

    "naive_code": """import numpy as np, cv2

def brisk_describe_naive(img, kp, pattern_radii, short_pairs, n_rots=36):
    \"\"\"极简版 BRISK 描述子（教学用，不做亚像素插值、不做多尺度）\"\"\"
    x, y = int(kp.pt[0]), int(kp.pt[1])
    half = 25
    patch = img[max(0,y-half):y+half+1, max(0,x-half):x+half+1]
    if patch.shape[0] < 2*half+1 or patch.shape[1] < 2*half+1:
        return None

    # 简化：采样 60 个点沿 4 个圆
    pts = []
    for r in [4, 8, 13, 20]:
        for i in range(15):
            ang = i * 2 * np.pi / 15
            px = int(round(half + r * np.cos(ang)))
            py = int(round(half + r * np.sin(ang)))
            pts.append((px, py))

    # 用 dx,dy 简单估方向（跳过真正的长点对）
    gx = cv2.Sobel(patch, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(patch, cv2.CV_32F, 0, 1, ksize=3)
    ang = np.arctan2(gy[half, half], gx[half, half])
    cos_a, sin_a = np.cos(-ang), np.sin(-ang)

    # 旋转采样点
    rot_pts = []
    for (px, py) in pts:
        dx, dy = px - half, py - half
        rx = int(round(half + dx*cos_a - dy*sin_a))
        ry = int(round(half + dx*sin_a + dy*cos_a))
        rot_pts.append((rx, ry))

    # 比 512 个短点对（这里简化为前 512 对近邻）
    des = 0
    bit = 0
    for i in range(len(rot_pts)):
        for j in range(i+1, len(rot_pts)):
            if bit >= 256: break
            xi, yi = rot_pts[i]
            xj, yj = rot_pts[j]
            if 0 <= xi < patch.shape[1] and 0 <= yi < patch.shape[0] and 0 <= xj < patch.shape[1] and 0 <= yj < patch.shape[0]:
                if patch[yi, xi] < patch[yj, xj]:
                    des |= (1 << bit)
            bit += 1
    return des
""",

    "source_insight": """OpenCV 的 BRISK 源码在 `modules/features2d/src/brisk.cpp`，关键结构：

- `BriskScaleSpace::constructPyramid()`：建 octave/intra-octave 金字塔
- `BriskScaleSpace::getKeypoints()`：每层跑 AGAST，通过 `AgastDetector9_16` 类
- `BriskLayer::getAgastPoints()`：调用 AGAST 决策树
- `BriskDescriptors::computeDescriptors()`：这是**核心**——它预先生成了所有 1770 对点对的采样 offset 列表（`shortPairs`/`longPairs`），方向估计和描述子生成都用同一个积分循环，非常快。

一个工程细节：OpenCV 的 BRISK 对采样点做了**整数坐标预计算**（因为旋转角度离散化为 1024 个方向，每个方向预存 60 个采样点的整数偏移），这样运行时只需要查表 + 加法就能定位像素，没有浮点插值开销。""",

    "painpoints_body": """### 1. 阈值太低导致「满天星」
默认 thresh=30 在高纹理图上能出几千个点，RANSAC 匹配会慢到离谱。
**修法**：调到 60–80，或配合 `response` 排序只取 top-N。

### 2. 没做金字塔导致「尺度变了就找不到」
**修法**：octaves 至少设为 3（默认 4），金字塔是尺度不变的基础。

### 3. 误把 BRISK 当成「比 ORB 快」
BRISK **不比 ORB 快**——描述子更长、采样更复杂。它是「比 ORB 鲁棒」。追求速度用 ORB，追求鲁棒性用 BRISK/AKAZE。

### 4. 匹配时没用 crossCheck / ratio test
二进制描述子虽然快，但**误匹配率高于 SIFT**。**修法**：BFMatcher 设 `crossCheck=True`，或用 KNN + Lowe ratio test（ratio=0.8）。

### 5. 模糊图上点太多但都不准
BRISK 的采样点做了高斯模糊，比 ORB 抗模糊，但**严重失焦时**还是会产生很多不稳定点。**修法**：先加轻微高斯模糊再检测，或提高 thresh。

### 6. 跨大视角匹配失败
BRISK 只有旋转+尺度不变，**没有仿射不变**。视角变化 >45° 建议用 ASIFT 或 AKAZE。

### 7. 内存/存储忽略描述子长度
512 位 = 64 字节/点，1000 个点就是 64KB——没什么；但如果要做大规模检索（词袋），注意比 ORB（32 字节）大了一倍。

### 8. 搭配 BFMatcher 而不是 FLANN
FLANN 的 LSH 索引支持汉明距离，但配置复杂；点数 <10000 时 BFMatcher 反而更快。**修法**：点数少直接用 BF，点数大用 FLANN-LSH。""",

    "diag_mermaid": """
    A[点太多/匹配乱] --> B{thresh 设了吗}
    B -- 低 --> C[提高 thresh 到 60+]
    B -- 已高 --> D{octaves 几层}
    D -- <3 --> E[加到 3–4 层]
    D -- 够 --> F[加 ratio test/crossCheck]
    G[点太少] --> H{thresh 太高?}
    H -- 是 --> I[降到 20–30]
    H -- 否 --> J[图像太光滑<br/>先做锐化/CLAHE]
    K[匹配错配多] --> L[用 KNN+ratio test 0.75]
""",

    "koujue": """**角要快、圈要圆、长定方向短拼串**""",

    "trick_order": """1. **先调 thresh**：控制点的数量和质量平衡
2. **再调 octaves**：决定尺度覆盖范围（3–4）
3. **配 BFMatcher(NORM_HAMMING, crossCheck=True)** 做初筛
4. **加 ratio test** 清掉误匹配
5. **用 RANSAC**（findHomography / findFundamentalMat）做几何校验""",

    "combos": """- **BRISK + Hamming BF + RANSAC**：SLAM/图像拼接的标配前端
- **BRISK + BoVW**：图像检索（词袋），描述子 64 字节，存词袋直方图时注意开销
- **BRISK + GMS**：Grid-based Motion Statistics 快速剔除误匹配
- **BRISK + 光流**：先用 BRISK 找初始点，再用 LK 光流做连续帧跟踪，比逐帧重提快""",

    "checklist_pre": """灰度化 + CLAHE 弱增强（可选）""",
    "checklist_post": """RANSAC 几何校验""",
})

# ---------- 2. AKAZE ----------
ALGOS.append({
    "slug": "akaze",
    "name": "AKAZE 加速 KAZE 特征",
    "en": "Accelerated-KAZE",
    "year": "2013",
    "author": "Pablo F. Alcantarilla / Jesús Nuevo / Adrien Bartoli",
    "branch": "feature-detection",
    "paper": "AKAZE (BMVC 2013)",
    "chapter": "ch08",
    "level": "mid",
    "paper_title": "Fast Explicit Diffusion for Accelerated Features in Nonlinear Scale Spaces",
    "citations": "~2500+",
    "contrib": "用 FED（Fast Explicit Diffusion）快速求解非线性扩散滤波，构造非线性尺度空间，再配 M-LDB 二进制描述子，比 KAZE 快两个量级且性能相当",
    "cv_func": "cv2.AKAZE_create()",
    "tagline": "用非线性扩散替代高斯金字塔，边缘保留得更好；描述子是改进版二进制 LDB，免费且比 SIFT 鲁棒",
    "analogy": "SIFT/SURF/ORB/BRISK 的尺度金字塔都用**高斯模糊**——相当于给照片蒙一层毛玻璃，细节和边缘一起糊掉；KAZE/AKAZE 用**非线性扩散**——像让墨水在宣纸上晕开，**边缘处不晕、平坦处才晕**，所以尺度空间里的边缘一直锐利。",
    "scene": "需要高重复率、对边缘细节敏感的场景：文档拼接、低光照图像匹配、航拍拼接、对精度要求高的 SLAM。",
    "pros": ["非线性尺度空间，边缘保留好", "重复率高于 ORB/BRISK", "M-LDB 二进制描述子匹配快", "专利免费（KAZE 也是免费）", "OpenCV 原生支持"],
    "cons": ["比 ORB 慢（但比 SIFT/KAZE 快）", "非线性扩散需要迭代求解（有一定开销）", "参数比 ORB 多", "在非常简单的场景优势不明显"],
    "onesentence": "用 FED 快速求解非线性扩散方程建立尺度空间，Hessian 检测关键点，再用 Modified-LDB 二进制描述子，是目前 OpenCV 里**性能最好且专利免费**的特征检测器之一。",

    "paper_why": """SIFT（2004）用 DoG 近似 LoG 建立尺度空间，本质是**线性**高斯金字塔——边缘和细节一起被平滑。KAZE（2012，作者和 AKAZE 同一团队）首次把**非线性扩散**用于建立尺度空间：让扩散只在区域内部进行，边缘处不扩散，这样每一层的边缘都锐利，关键点的定位精度和重复率显著提升。

但 KAZE 有一个大问题：求解非线性扩散方程用的是**AOS（Additive Operator Splitting）**，需要解三对角线性方程组，**很慢**——比 SIFT 还慢，工程上很难用。

AKAZE 的贡献就是：
1. 用 **FED（Fast Explicit Diffusion）** 代替 AOS，速度快几个量级，还能更好地并行
2. 提出 **M-LDB（Modified-Local Difference Binary）** 描述子，比 SURF 的 M-SURF 描述子和 KAZE 原版浮点描述子快得多""",

    "paper_innov": """**创新 1：非线性扩散滤波（Perona-Malik 方程）**

尺度空间 L^t 的演化用非线性 PDE：
$$\\frac{\\partial L}{\\partial t} = \\operatorname{div}\\big(c(x,y,t) \\cdot \\nabla L\\big)$$

传导函数 c 用 Perona-Malik 形式：$c = \\exp(-|\\nabla L_\\sigma|^2 / \\lambda^2)$，**梯度大的地方（边缘）传导系数小，几乎不扩散；梯度小的地方（平坦区）传导系数接近 1，自由扩散**。

**创新 2：FED 快速显式扩散**

AOS 求解非线性方程每步都要解线性方程组 O(N)，但常数大。FED 借鉴了循环超松弛思想，用**M 个显式小步长循环**代替一个隐式大步，**完全可并行**（只需逐像素算术，无需求解方程组），总速度比 AOS 快一个量级。

**创新 3：M-LDB 二进制描述子**

原版 LDB（Local Difference Binary）在每个 grid cell 里比较平均灰度、水平梯度、垂直梯度，得到二值串。M-LDB 做了两点改进：
- **尺度感知**：采样步长随关键点尺度变化
- **旋转不变**：沿主方向把 grid 旋转对齐
- 描述子长度 486 位（OpenCV 默认 486，也可配 256/512）""",

    "paper_result": """在 Mikolajczyk + Oxford 数据集上：
- 检测重复率：优于 SIFT/SURF/ORB/BRISK，和 KAZE 持平
- 描述子 mAP：接近 SIFT，优于 ORB/BRISK
- 速度：比 KAZE 快约 **20×–50×**，比 SIFT 快约 3×–5×，比 ORB 慢约 2–3×
- 对模糊、压缩、旋转的鲁棒性显著优于 ORB/BRISK""",

    "paper_limit": """- 非线性扩散迭代次数需要调（ncycles=4 默认够用）
- 速度仍不如 ORB，高帧率场景不适合
- 描述子 486 位不是 8 的整数倍，汉明距离计算要注意对齐（OpenCV 内部处理了）
- 对非常大尺度变化（>4×）略弱于 SIFT""",

    "read_tip": "Section 2（FED 算法）和 Section 3（M-LDB 描述子）",
    "read_tip2": "补充材料里的 FED 步数设计",

    "concepts_body": """## 1. 非线性扩散（Nonlinear Diffusion）

传统高斯模糊是**各向同性**扩散：所有方向都糊。非线性扩散让扩散系数**随局部梯度变化**——边缘处梯度大，扩散慢；平坦处梯度小，扩散快。这就是「保边滤波」的数学基础。

> 生活比方：想象在一块布上滴一滴墨水，放在桌面上会均匀晕开（高斯）；放在有折痕的布上，墨水会沿着折痕**停留**，只在平坦布面晕开——这就是非线性扩散，折痕就是图像里的边缘。

## 2. Perona-Malik 方程

经典的保边扩散 PDE：$\\partial_t L = \\operatorname{div}(g(|\\nabla L|) \\nabla L)$，其中 g(|∇L|) 是一个关于梯度模长的递减函数。当梯度很大时 g→0（边缘停下），梯度很小时 g→1（内部自由扩散）。

## 3. FED（Fast Explicit Diffusion）

FED 做的事：把一个大时间步 T 拆成 M 个小循环，每个循环里用一系列**逐渐增大的显式步长**做迭代，最大步长可以突破显式欧拉方法的稳定上限。具体：

- 每个 FED cycle 包含 n 步（n 由扩散时间决定）
- 每步的步长 $\\tau_i = \\tau_{max} / (2 \\cos^2 \\frac{\\pi (2i+1)}{4n})$
- 总共 n 个显式步，无需解方程组，**纯像素级算术**，可并行

这是 AKAZE 比 KAZE 快几十倍的关键。

## 4. Hessian 关键点检测

和 SIFT/SURF 在 DoG/DoH 上找极值点类似，AKAZE 在非线性尺度空间上用**尺度归一化的 Hessian 行列式**做响应：
$$\\text{det}(H_{norm}) = \\sigma^2 (L_{xx} L_{yy} - L_{xy}^2)$$
在 3×3×3 的时空邻域里做 NMS。

## 5. M-LDB 描述子

LDB 把关键点周围区域分成 grid（默认 4×4 共 16 个 cell），对每个 cell 计算三个量：
- 平均灰度
- x 方向平均梯度
- y 方向平均梯度

然后对相邻 cell 的这三个量做**二元比较**（谁大谁小），拼出二值串。M-LDB 把 grid 做成尺度自适应，并在主方向上做旋转。""",

    "mermaid": """
    A[输入图像] --> B[构造非线性尺度空间<br/>FED 求解 Perona-Malik PDE<br/>O 个 octave × S 个 sublevel]
    B --> C[每层算 Hessian 行列式]
    C --> D[3×3×3 NMS + 亚像素精定位]
    D --> E[60°扇形滑动窗口<br/>求主方向（Haar 小波响应）]
    E --> F[主方向上构建 M-LDB grid<br/>分 2×2/3×3/4×4 多尺度子格]
    F --> G[每个 cell 比灰度+dx+dy<br/>拼出 486 位二进制描述子]
    G --> H[输出关键点+描述子]
""",

    "steps_body": """### Step 1：输入与初始高斯平滑
输入灰度图，先做一次 σ=1.0 的高斯平滑，消掉像素噪声。

### Step 2：FED 构建非线性尺度空间
默认 4 个 octave，每个 octave 4 个 sublevel，共 16 层。每层对应一个进化时间 t_i = \\frac{1}{2} σ_i²（σ_i 是该层尺度）。
对相邻两层，用 FED 算法跑若干次 diffusion cycle，构造出 L^{t_i}。每一步里要：
1. 用 Scharr 核算当前层的梯度 Lx, Ly
2. 算传导系数 c = exp(-|∇L_σ|² / λ²)（λ 是对比度参数，默认 0.001）
3. 用 FED 步长做一次显式更新

### Step 3：Hessian 检测
在每一层算 Lxx, Lyy, Lxy（Scharr/Sobel），构造 det(H_norm) = σ²(Lxx·Lyy - Lxy²)。
在每个点 (x,y,σ) 的 3×3×3 邻域里做非极大值抑制，再做二次拟合（D. Brown 方法）得到亚像素、亚尺度位置。

### Step 4：主方向估计
和 SURF 类似：在关键点周围一个 6σ 半径的圆内，每 5°（共 72 个方向）用扇形 Haar 小波响应累加，找响应最大的方向作为主方向。

### Step 5：M-LDB 描述子
把关键点附近 24σ×24σ 的区域按主方向旋转对齐，分成多尺度 grid（2×2, 3×3, 4×4 合共 4+9+16=29 个 cell），对每个 cell 计算：
- V：平均灰度
- Dx：平均水平梯度
- Dy：平均垂直梯度

然后对相邻 cell 逐对比较 V/Dx/Dy，得到 3 × (sum over pairs) 个 bit。默认 486 位。

### Step 6：输出
关键点 + 486 位描述子。""",

    "params_table": """| descriptor_type | M-LDB | AKAZE_DESCRIPTOR_MLDB | MLDB（默认），若要浮点可选 MLDB_UPRIGHT/KAZE_UPRIGHT | 二进制匹配快 |
| descriptor_size | 0 | 0（=全 486 位） | 0 / 256 / 512 | 越大越鲁棒、越大越慢 |
| threshold | 0.001 | 0.001 | 0.0005–0.002 | Hessian 响应阈值，越小点越多 |
| nOctaves | 4 | 4 | 4 | octave 数，控制尺度范围 |
| nOctaveLayers | 4 | 4 | 4 | 每 octave 层数 |
| diffusivity | PM_G2 | DIFF_PM_G2 | 默认 | 传导函数，G2 保边效果最好 |""",

    "complexity": """- FED 构建尺度空间：O(N_iter · W · H)，每像素只做加减乘，常数小
- 检测：与 SIFT 同量级
- 描述子：每个关键点 O(grid²) 次比较，和 BRISK 同量级
- 实测：640×480 图 20–60ms（CPU 单线程），比 SIFT 快 3–5×，比 KAZE 快 20×""",

    "opencv_code": """import cv2
img = cv2.imread('scene.jpg', 0)

akaze = cv2.AKAZE_create(
    descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB,
    descriptor_size=0,       # 0 = full 486 bits
    threshold=0.001,
    nOctaves=4,
    nOctaveLayers=4,
)
kps, des = akaze.detectAndCompute(img, None)

bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
matches = bf.knnMatch(des1, des2, k=2)
good = [m for m,n in matches if m.distance < 0.75 * n.distance]
""",

    "naive_code": """import numpy as np, cv2

def perona_malik_diffuse(img, iters=10, lam=0.15, k=0.03):
    \"\"\"极简 Perona-Malik 各向异性扩散（教学用，单 octave 单层）\"\"\"
    L = img.astype(np.float32) / 255.0
    for _ in range(iters):
        n = L[:-2,1:-1] - L[1:-1,1:-1]
        s = L[2:,1:-1]  - L[1:-1,1:-1]
        e = L[1:-1,2:]  - L[1:-1,1:-1]
        w = L[1:-1,:-2] - L[1:-1,1:-1]
        c_n = np.exp(-(n**2)/(k*k))
        c_s = np.exp(-(s**2)/(k*k))
        c_e = np.exp(-(e**2)/(k*k))
        c_w = np.exp(-(w**2)/(k*k))
        L[1:-1,1:-1] += lam*(c_n*n + c_s*s + c_e*e + c_w*w)
    return (np.clip(L,0,1)*255).astype(np.uint8)

def akaze_naive_demo(img_path):
    img = cv2.imread(img_path, 0)
    L2 = perona_malik_diffuse(img, iters=5, k=0.05)
    L4 = perona_malik_diffuse(img, iters=20, k=0.05)
    return L2, L4  # 对应两个尺度层
""",

    "source_insight": """OpenCV AKAZE 源码在 `modules/features2d/src/akaze.cpp`：

- `AKAZE::Compute_Nonlinear_Scale_Space()`：构造非线性尺度空间，内部调用 `fed_tvL1()` / `fed_g2()` / `fed_pm1()` / `fed_pm2()`（四种 diffusivity）
- `nldf_evolution_*()` 系列函数：单步 FED 更新，纯浮点像素循环，可 SIMD 优化
- `AKAZE::Compute_Detector_Hessian()`：每层算 Hessian 行列式
- `AKAZE::Compute_Main_Orientation_SURF()`：Haar 响应扇形滑动窗口
- `AKAZE::Compute_Descriptors_MLDB()`：M-LDB 描述子，按 grid 比 V/dx/dy

一个重要细节：OpenCV 默认把 diffusivity 设为 `DIFF_PM_G2`（g_2 = 1/(1 + |∇L|²/k²)），这是保边最强的选项，**不要随便改成 DIFF_PM_G1**，后者对噪声更敏感。""",

    "painpoints_body": """### 1. threshold 设得太小导致点爆炸
threshold 默认 0.001，模糊图上可能出几千个点。**修法**：调到 0.002–0.005，或响应排序 top-N。

### 2. 把 AKAZE 当"免费版 SIFT"期望过高
AKAZE 重复率优于 ORB/BRISK，但**对极端旋转+尺度+视角变化**仍略弱于 SIFT。不要期望一个二进制描述子全面打赢 128 维浮点。

### 3. descriptor_size=0 与自定义 size 混用
0 代表全 486 位；设置 256/512 会截取前若干 bit，性能略有下降但内存省。注意 486 不是 8 的倍数，某些自定义汉明距离计算要注意尾部。

### 4. diffusivity 选错
DIFF_WEICKERT / DIFF_CHARBONNIER 对特定场景好，但默认 PM_G2 是最稳的。除非你清楚区别，不要改。

### 5. 错用 NORM_L2 匹配
AKAZE 默认输出二进制描述子，必须用 `NORM_HAMMING`（不是 NORM_L2）。只有选了 `DESCRIPTOR_KAZE`（浮点）才用 NORM_L2。

### 6. 主方向估计不稳导致"匹配抖动"
主方向用的是 SURF 风格 Haar 响应，对**低纹理区域**会不稳定。**修法**：只对 response 大的点保留，或用 UPRIGHT 版本（无旋转不变）匹配特定场景。

### 7. 速度不达预期
AKAZE 默认参数比 ORB 慢 2–3×。要加速：nOctaves=3, nOctaveLayers=3, threshold=0.003；或改用 UPRIGHT 描述子（AKAZE_DESCRIPTOR_MLDB_UPRIGHT）。

### 8. 与 FLANN 搭配不当
二进制描述子用 `FlannBasedMatcher` 时必须配 LSH index params，否则默认 KDTREE 会把二进制当浮点、效果极差。""",

    "diag_mermaid": """
    A[点多/慢] --> B{threshold?}
    B -- <0.001 --> C[调到 0.001–0.003]
    B -- 正常 --> D{nOctaves?}
    D -- >4 --> E[降到 4]
    D -- 正常 --> F[响应排序取 top-N]
    G[匹配乱] --> H{NORM_HAMMING 用了吗?}
    H -- 否 --> I[换 NORM_HAMMING]
    H -- 是 --> J[加 ratio test 0.75]
    K[边缘点多但定位不准] --> L[threshold 调大 + 响应过滤]
""",

    "koujue": """**非线性、FED 快、Hessian 顶、MLDB 比**""",

    "trick_order": """1. **threshold 先设 0.001**，根据出点数再调
2. **diffusivity 默认 PM_G2**
3. **descriptor_type 用 MLDB**（二进制，匹配快）
4. **BFMatcher(NORM_HAMMING) + ratio test 0.75**
5. 速度要求高时 descriptor_size=256、UPRIGHT 版本""",

    "combos": """- **AKAZE + BF-Hamming + RANSAC**：高精度图像拼接首选
- **AKAZE + GMS matcher**：实时网格统计匹配，鲁棒快速
- **AKAZE + BoVW**：免费高重复率检索
- **AKAZE + 单应矩阵 + 图像拼接**：航拍/文档扫描的经典 pipeline""",

    "checklist_pre": """灰度化 + 轻微高斯去噪（sigma=1）""",
    "checklist_post": """ratio test + RANSAC""",
})

# ---------- 3. CLAHE ----------
ALGOS.append({
    "slug": "clahe",
    "name": "CLAHE 限制对比度自适应直方图均衡",
    "en": "Contrast Limited Adaptive Histogram Equalization",
    "year": "1994",
    "author": "Karel Zuiderveld",
    "branch": "image-processing",
    "paper": "Graphics Gems IV (1994)",
    "chapter": "ch03",
    "level": "low",
    "paper_title": "Contrast Limited Adaptive Histogram Equalization",
    "citations": "~10000+",
    "contrib": "把图像切成 tile，每个 tile 内做直方图均衡，但对直方图做 clip 限制对比度，避免噪声被放大；tile 之间用双线性插值消除网格边界",
    "cv_func": "cv2.createCLAHE(clipLimit, tileGridSize)",
    "tagline": "每个小格子自己拉对比度，超过阈值的部分切下来平均分给所有人，既增强细节又不放大噪声",
    "analogy": "普通直方图均衡像给整个房间装一个总调光开关：亮的地方太亮，暗的地方太暗。普通 AHE 像给每平米装一个小开关，但暗部噪声也被放大成雪花。CLAHE 给每个小开关加了「功率上限」：你不能把噪声拉到和信号一样亮，超过的功率平均分给大家——细节出来了，噪声还在底。",
    "scene": "医学影像（X 光、CT、眼底照）、低光照/逆光图像增强、人脸识别预处理、OCR 文档增强、车牌识别前处理。",
    "pros": ["局部增强，能照顾暗部细节", "clipLimit 限制噪声放大", "双线性插值无网格边界", "速度快、无 GPU 依赖", "OpenCV 原生、一个 API 搞定"],
    "cons": ["clipLimit 要根据噪声调", "tileGridSize 影响局部性", "对彩色图要转到 LAB 空间处理 L 通道", "过度增强会产生「脏脏」的对比度"],
    "onesentence": "把图像分成 8×8 的小 tile，每个 tile 内做带 clip 限制的直方图均衡，再用双线性插值拼回去——一个被工业界用了 30 年仍在首选的**对比度增强**算法。",

    "paper_why": """直方图均衡（HE）是最早的图像增强方法：把灰度直方图强制拉平，让对比度最大化。但它有两个问题：
1. **全局**：对整张图做，亮区更亮、暗区更暗，局部细节照顾不到
2. **过度增强**：在接近平坦的区域（比如天空、皮肤），直方图的少数峰值被强力拉大，**噪声被放大**到肉眼可见

AHE（Adaptive HE，1970s 起）解决了全局问题——把图切成小 tile 分别均衡。但 AHE 在**暗区**会把噪声放大到离谱。

Pizer et al.（1987）提出 CLAHE 的雏形——在 AHE 的基础上对每个 tile 的直方图加 clip。Zuiderveld 1994 年在 Graphics Gems IV 上给出了一个**80 行 C 语言**的极简实现，成为工程界事实上的标准。""",

    "paper_innov": """**创新 1：分块处理**
把图像均匀划分成 M×N 个 tile（OpenCV 默认 8×8），每个 tile 独立计算直方图和映射函数（CDF）。

**创新 2：Clip Limit（对比度限制）**
对每个 tile 的直方图 h，计算 clipLimit（典型值 2–4 倍平均像素数）：
- 超过 clipLimit 的 bin 把超出部分「切下来」
- 把切下来的总像素数 **平均分配**到所有 256 个 bin
- 重复一次直至没有 bin 超限（其实一次就差不多）

这步让平坦区的直方图不会被拉到极端，噪声也就不会被暴力放大。

**创新 3：双线性插值拼接**
在 tile 边界处，如果直接用相邻 tile 各自的映射会出现「网格边」。CLAHE 对每个像素，取它所在的 **4 个相邻 tile** 的映射结果做双线性插值，整张图无缝衔接。""",

    "paper_result": """- 在医学影像（乳腺 X 光、眼底照）上，CLAHE 让结节/病灶可见度提升显著
- 在人脸/低光照增强上，比全局 HE 少出现「过曝脸」
- 速度：800×600 图约 5–10ms（CPU 单线程），完全实时""",

    "paper_limit": """- clipLimit 仍需手动调，没有数据驱动的自适应方法
- 对高动态范围场景（同时存在强光和极暗）仍不够
- tileGridSize 固定，图像内容变化大时不够灵活
- 后来出现 AGCWD、Retinex、Zero-DCE 等更强的增强算法，但 CLAHE 因简单快速仍在工业首选""",

    "read_tip": "直接读 Graphics Gems IV 第 VIII.5 节，只有 8 页",
    "read_tip2": "Zuiderveld 给出的 `ClipHistogram` 和 `Interpolate` 函数，代码本身就是论文",

    "concepts_body": """## 1. 全局直方图均衡（HE）回顾

把灰度图的累积分布函数（CDF）当成映射函数：$T(r) = 255 \\cdot \\sum_{i=0}^{r} p(i)$，把原像素值 r 映射到 T(r)。好处是整体对比度最大；坏处是**对局部不管用**——大块亮区占据直方图大部分时，暗部被压成一条线。

## 2. 自适应直方图均衡（AHE）

把图像分成 M×N 块，每块各自做 HE，结果是局部对比度确实提升，但**均匀区域里噪声被强力放大**——因为一个本来很平坦的块，CDF 很陡，一个像素值抖动都会被映射成很大跨度。

## 3. Clip Limit：切掉超额直方图

每个 tile 平均像素数 = tileW × tileH / 256。CLAHE 规定每个 bin 不能超过 `clipLimit × avgPixels`（clipLimit 典型 2–4）。超额的部分被平均洒给所有 bin，效果：
- 陡峭的峰被削平 → 映射函数斜率变小 → 噪声不会被放大
- 平均分配给所有 bin → 整体亮度不漂移

## 4. 双线性插值

4 个相邻 tile（左上、右上、左下、右下）各有自己的映射函数。对 tile 内部的像素 (x,y)，根据它距离 4 个 tile 中心的权重，做双线性插值得到最终灰度，消除网格感。

## 5. 彩色图处理

CLAHE 通常**不直接对 RGB 三通道各做一遍**（会造成色偏）。正确做法：转到 LAB / YCrCb 空间，只对 L（亮度）/Y 通道做 CLAHE，再转回 RGB。""",

    "mermaid": """
    A[输入灰度图] --> B[分成 tileGridSize × tileGridSize 个块<br/>默认 8×8]
    B --> C[每个 tile 算灰度直方图]
    C --> D[Clip：超过 clipLimit 的部分切下<br/>均分给所有 bin]
    D --> E[每个 tile 算 CDF 作为映射函数]
    E --> F[对每个像素，取相邻 4 tile 的映射结果<br/>双线性插值]
    F --> G[边缘像素（tile 边界外）用最近 tile 的映射<br/>不插值]
    G --> H[输出增强后图像]
""",

    "steps_body": """### Step 1：tile 初始化
把图像切成 tiles（默认 8×8，即每 tile 约 (H/8)×(W/8)）。图像尺寸不是 tile 倍数时做 reflect padding。

### Step 2：逐 tile 计算直方图
对每个 tile 统计 0–255 灰度的出现次数 h[i]，共 256 个 bin。

### Step 3：Clip
1. 计算 `limit = clipLimit × tileSize × tileSize / 256`
2. 累加所有 bin 中超出 limit 的部分，得 totalExcess
3. 每个 bin 裁剪到 min(h[i], limit)
4. 把 totalExcess 平均分给 256 个 bin（加 incr = totalExcess / 256）
5. 再迭代一轮，把因平均分配后仍可能超限的 bin 再次裁剪、剩余均摊

### Step 4：映射函数
对每个 tile 计算 CDF：`LUT[i] = sum_{k=0}^{i} h_clipped[k]`，归一化到 [0,255] 作为映射表。

### Step 5：双线性插值
对像素 (x,y)，找出它所在 tile 的左上角 (i0,j0)、右下角 (i1,j1)：
- 距离左上角 (x_frac, y_frac) 作为权重
- 四个 tile 的映射结果分别为 v00, v10, v01, v11
- 最终值 = 双线性插值：`(1-yf)[(1-xf)v00 + xf·v10] + yf·[(1-xf)v01 + xf·v11]`

### Step 6：边界处理
图像边缘（不足 4 个 tile 邻居的像素）直接用最近 tile 的映射，不插值。""",

    "params_table": """| clipLimit | 2–4（推荐） | 2.0 | 2.0（图像噪声大→3–4，干净→1.5–2） | 越大对比度越强，越容易放大噪声 |
| tileGridSize | (8,8) | (8,8) | (8,8) 通用，(4,4) 局部性更强，(16,16) 更接近全局 HE | tile 越小，局部增强越狠 |""",

    "complexity": """- 直方图统计：O(W·H)
- Clip + CDF：每个 tile O(256)，总 O(tile²·256) = O(W·H)
- 双线性插值：O(W·H)
- 整体 O(W·H)，常数极小，640×480 图 <5ms""",

    "opencv_code": """import cv2
img = cv2.imread('lowlight.jpg')
# 彩色图：转到 LAB 只增强 L 通道
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
l2 = clahe.apply(l)
lab2 = cv2.merge([l2, a, b])
out = cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)
""",

    "naive_code": """import numpy as np, cv2

def clahe_naive(img, clipLimit=2.0, tileGridSize=(8,8)):
    \"\"\"极简 CLAHE（教学用：单通道灰度，无边界插值优化）\"\"\"
    h, w = img.shape
    th, tw = tileGridSize
    tile_h, tile_w = h // th, w // tw
    out = np.zeros_like(img)
    LUTs = {}

    # 每个 tile 算 clipped CDF
    for i in range(th):
        for j in range(tw):
            tile = img[i*tile_h:(i+1)*tile_h, j*tile_w:(j+1)*tile_w]
            hist, _ = np.histogram(tile.flatten(), 256, [0,256])
            limit = int(clipLimit * tile_h * tile_w / 256)
            excess = 0
            for k in range(256):
                if hist[k] > limit:
                    excess += hist[k] - limit
                    hist[k] = limit
            inc = excess // 256
            hist += inc
            cdf = np.cumsum(hist).astype(np.float32)
            cdf = 255 * (cdf - cdf.min()) / (cdf.max() - cdf.min() + 1e-6)
            LUTs[(i,j)] = cdf.astype(np.uint8)

    # 最近邻插值版（简化，略去双线性）
    for i in range(th):
        for j in range(tw):
            tile = img[i*tile_h:(i+1)*tile_h, j*tile_w:(j+1)*tile_w]
            out[i*tile_h:(i+1)*tile_h, j*tile_w:(j+1)*tile_w] = LUTs[(i,j)][tile]
    return out
""",

    "source_insight": """OpenCV CLAHE 在 `modules/imgproc/src/clahe.cpp`，核心类 `CLAHE_Impl`：

- `CLAHE_Impl::apply()`：入口，分 tile、并行处理
- `CLAHE_Impl::calcLUT()`：对每个 tile 算 clip + CDF，用 `cv::parallel_for_` 并行
- `CLAHE_Impl::interpolate`：双线性插值的四种情况（tile 内部/边界/四角），SSE/AVX 优化过
- Clip 循环用了个小技巧：不是「一次裁剪+均摊」，而是循环「裁剪→均摊→再裁剪」到没有 bin 超限（通常 2–3 次收敛）""",

    "painpoints_body": """### 1. 直接对 RGB 三通道做 CLAHE 导致色偏
**修法**：转到 LAB/YCrCb，只对 L/Y 做，再转回。

### 2. clipLimit 太大把噪声放大成颗粒
医学/低照度图默认 2.0 合适；如果图像本身有胶片颗粒/高 ISO 噪声，**先去噪再 CLAHE**（cv2.fastNlMeansDenoising），或 clipLimit 降到 1.5。

### 3. tileGridSize 太小出网格
tileGridSize=(2,2) 这种太小的值会出现明显的格子。**修法**：默认 8×8，至少 4×4。

### 4. 过度增强让图像「发灰」
CLAHE 让暗部亮起来的同时，也会让亮部的纯黑/纯白变灰。**修法**：CLAHE 后再做一次 gamma 校正（gamma=0.8–0.9）恢复对比度。

### 5. 逆光场景人脸局部过曝
逆光只照亮半边脸，CLAHE 可能把暗面拉出来但把亮面压灰。**修法**：配合 MOG2/人脸检测只对 ROI 做 CLAHE，或使用 Retinex。

### 6. 8-bit 假设
OpenCV CLAHE 只支持 8-bit 单通道。16-bit 医学影像要自己实现或用 `cv2.normalize` 先转 8-bit。

### 7. clipLimit=1 就是 AHE，噪声爆炸
不要把 clipLimit 设到 1 以下。

### 8. 彩色增强后饱和度降低
LAB 只增强 L 通道会让饱和度看起来变低。**修法**：CLAHE 后对 a/b 通道做轻微（×1.1–1.2）的饱和度增强。""",

    "diag_mermaid": """
    A[噪声放大/颗粒感] --> B{clipLimit 太大?}
    B -- >3 --> C[降到 2.0]
    B -- 正常 --> D[先做去噪再 CLAHE]
    E[色偏/颜色怪] --> F{是否对 RGB 做了?}
    F -- 是 --> G[转 LAB 只增强 L]
    H[网格感] --> I{tileGridSize 太小?}
    I -- <4x4 --> J[设为 8x8]
    K[发灰/对比度低] --> L[加 gamma=0.8 校正]
""",

    "koujue": """**分块均、Clip 限、插值拼、只做 L**""",

    "trick_order": """1. 转单通道（或 LAB 的 L 通道）
2. **clipLimit=2.0、tileGridSize=(8,8)** 作为起点
3. 观察暗部噪声和亮部对比度，clipLimit 1.5–4.0 调整
4. 需要更强局部增强时 tileGridSize 改 (4,4)，弱一些用 (16,16)
5. 事后配合 gamma/饱和度调整""",

    "combos": """- **CLAHE + 高斯去噪**：低照度增强标配
- **CLAHE + Canny**：边缘检测前增强，暗部边缘出得来
- **CLAHE + 人脸检测**：Haar/LBP 人脸检测前做，逆光下召回率提升显著
- **CLAHE + OCR（Tesseract）**：低质量文档扫描必做
- **CLAHE + LBP/HOG**：特征提取前做光照归一化""",

    "checklist_pre": """灰度化（或转 LAB/L 通道）""",
    "checklist_post": """gamma/饱和度微调（可选）""",
})

print(f"已定义 {len(ALGOS)} 个算法")

# ---------- 4. 距离变换 ----------
ALGOS.append({
    "slug": "distance-transform",
    "name": "距离变换",
    "en": "Distance Transform",
    "year": "1966",
    "author": "Azriel Rosenfeld / John Pfaltz / Gunilla Borgefors",
    "branch": "image-processing",
    "paper": "Rosenfeld & Pfaltz 1966 / Borgefors 1986",
    "chapter": "ch03",
    "level": "low",
    "paper_title": "Sequential Operations in Digital Picture Processing (Rosenfeld 1966)",
    "citations": "~10000+",
    "contrib": "对二值图的每个前景点，计算它到最近背景点的距离；用两次扫描（左上→右下 + 右下→左上）的倒角距离近似欧氏距离，O(N) 复杂度",
    "cv_func": "cv2.distanceTransform()",
    "tagline": "给二值图每个像素发一张「到最近墙有多远」的地图，中心最远、边缘最近；分水岭、骨架、点匹配都要靠它",
    "analogy": "想象在一个漆黑的迷宫里（白色=能走，黑色=墙），给每个位置标出「离最近一堵墙有几步」：墙根是 0，走廊中间是大数字，大厅正中央是最大的数。画成热力图，最亮的地方就是「整个区域的脊梁」——这就是距离变换。",
    "scene": "分水岭分割的种子生成、目标骨架提取、二值图匹配（chamfer matching）、形态学细化、医学影像中心线提取、文字识别的字宽估计。",
    "pros": ["O(N) 复杂度（两次扫描）", "结果稳定、可解释", "是分水岭、骨架、匹配等算法的基础", "OpenCV 一行调用"],
    "cons": ["输入必须是干净的二值图（0/1 或 0/255）", "不同距离类型精度不同（L1/L2/C）", "边界条件要注意", "距离类型选错会导致结果偏差"],
    "onesentence": "对二值图做两次反向扫描，用 3×3 邻域最小距离递推，得到每个前景点到最近背景的距离图——形态学、分割、匹配的底层积木。",

    "paper_why": """距离变换最早在 1966 年 Rosenfeld & Pfaltz 的经典论文里作为一种「序贯操作」提出。当时的问题：二值图像里每个像素到最近 0 像素的距离，若暴力算对每个前景像素搜索全图是 O(N²·N) = O(N³)，太慢。

Rosenfeld 发现：用**两次光栅扫描**（top-down left-to-right，再接 bottom-up right-to-left），配合 3×3 邻域里递推，就能在线性时间里得到**城市块距离（L1）**或**棋盘距离（L∞）**的精确距离变换。

1986 年 Borgefors 提出了**倒角距离（Chamfer Distance）**——用一个 3×3 或 5×5 的局部权重模板（比如 3/4 权重，或 5/7/11），两次扫描可以得到**欧氏距离的近似**，误差 <2%。这是现在工业界用得最多的形式。""",

    "paper_innov": """**创新 1：两次扫描算法**
对距离图 D 初始化：背景点 D=0，前景点 D=+∞。
- 第一遍：从上到下、从左到右，用 3×3 邻域中**左上半部分**的像素递推 D[i][j]
- 第二遍：从下到上、从右到左，用 3×3 邻域中**右下半部分**的像素递推

两遍结束 D[i][j] 就是精确（L1/L∞）或近似（chamfer）距离。

**创新 2：倒角距离权重**
Borgefors 3×3 模板：正上/正下/正左/正右的权重是 3，对角是 4（最后整体除以 3），等价于近似 (|dx|+|dy|) + (√2-2)·min(|dx|,|dy|) ，欧氏距离误差约 5%。
5×5 模板：3/4/5，误差约 2%。

**创新 3：标签距离变换**
不仅要最近距离，还要最近背景点/前景标签是谁——Danielsson 1980 年提出 4SED/8SED 算法，存 (dx, dy) 向量，能还原精确欧氏距离，OpenCV 的 DIST_L2 就是这个。""",

    "paper_result": """- 复杂度：两次扫描 O(N)，比暴力搜索快 N 倍
- Chamfer 3×4 误差 <5%，5×7×11 误差 <2%
- Danielsson 8SED 精确到像素级欧氏距离
- 实际应用：分水岭算法 99% 的实现都依赖距离变换""",

    "paper_limit": """- 两次扫描是近似（对欧氏距离），精确欧氏距离需要更复杂的 Saito / Felzenszwalb 算法
- 二值图输入，对噪声敏感（一个孤立黑点会在周围产生小坑）
- 各向同性距离变换的并行化需要特殊处理""",

    "read_tip": "Borgefors 1986 论文（只有 8 页）",
    "read_tip2": "看 OpenCV `distanceTransform` 的源码，30 分钟就能吃透",

    "concepts_body": """## 1. 距离的定义

| 距离名 | 公式 | 别名 | 直观理解 |
|---|---|---|---|
| L1 | $|dx| + |dy|$ | 城市块/曼哈顿 | 只能横竖走 |
| L2 | $√(dx²+dy²)$ | 欧氏 | 直线距离 |
| L∞ | $max(|dx|,|dy|)$ | 棋盘 | 王棋一步能到 |
| C | 3/4 倒角 | Chamfer | 横竖 3、对角 4 近似 L2 |

## 2. 两次扫描递推的核心思想

如果一个像素 (i,j) 的最近背景点是它自己（它自己就是背景），D=0；否则它的最近距离 = 1 + min{邻居们的最近距离}。但这需要迭代多轮。两次扫描的巧妙在于：

- **第一遍（左上→右下）**：利用「已经扫过」的左上邻居，把左上方向的距离信息传过来
- **第二遍（右下→左上）**：反过来利用右下邻居传右下方向信息

两遍之后信息就传遍整张图了。

## 3. 距离变换 vs 骨架化

距离变换局部最大值连起来就是「骨架」（skeleton / medial axis）：
- **距离局部极大**：比所有 8 邻域都大的点
- 骨架上每个点的距离值 = 它所在位置的「宽度半径」，也就是「这根血管有多粗」

## 4. 标签距离变换（带索引）

DIST_LABEL_PIXEL / DIST_LABEL_CCOMP 选项不仅给距离，还告诉你最近的 0 像素是哪个标签/哪个连通域——这就是**分水岭算法找种子**的核心。""",

    "mermaid": """
    A[输入二值图<br/>0=背景 255=前景] --> B[初始化 D：背景=0，前景=+∞]
    B --> C[第一遍扫描<br/>从上到下、从左到右<br/>min(D[i][j], D[i-1][j]+a, D[i-1][j-1]+b, D[i][j-1]+a)]
    C --> D[第二遍扫描<br/>从下到上、从右到左<br/>min(D[i][j], D[i+1][j]+a, D[i+1][j+1]+b, D[i][j+1]+a)]
    D --> E[若为 L2 标签距离，同步更新 (dx,dy) 向量]
    E --> F[输出 float32 距离图<br/>+ 可选标签图]
""",

    "steps_body": """### Step 1：输入二值化
把图像变成 0/255 的二值图（0=背景、255=前景）。注意：距离变换「关心的是前景到背景的距离」，别搞反。

### Step 2：初始化距离图
- D[y,x] = 0 如果 img[y,x] == 0（背景点）
- D[y,x] = +∞（一个很大的数，比如 W+H）如果 img[y,x] > 0（前景点）

### Step 3：第一遍扫描（Forward Pass）
从 (1,1) 走到 (H-2, W-2)：
```
D[y,x] = min(
  D[y,x],
  D[y-1,x]   + a,   // 上
  D[y-1,x-1] + b,   // 左上
  D[y,x-1]   + a,   // 左
  D[y-1,x+1] + b,   // 右上（5×5 模板用）
)
```
- L1: a=1, b=2
- C 3×4: a=3, b=4（最后除以 3）
- L2 (Danielsson): 存 (dx, dy) 向量而非标量，距离最后算 √(dx²+dy²)

### Step 4：第二遍扫描（Backward Pass）
从 (H-2, W-2) 走回 (1,1)：
```
D[y,x] = min(
  D[y,x],
  D[y+1,x]   + a,
  D[y+1,x+1] + b,
  D[y,x+1]   + a,
  D[y+1,x-1] + b,
)
```

### Step 5：归一化
如果是 chamfer，整体除以权重分母（3/5）得到实际距离。如果是 L2，算 sqrt(dx²+dy²)。

### Step 6：可选 —— 标签图
若要「最近背景点属于哪个连通域」，同步维护 label 数组，在每次更新 D 时继承对应邻居的 label。""",

    "params_table": """| distanceType | DIST_L2 (推荐) | DIST_L2 | DIST_L2 | L1/C 快但不精确，L2 精确 |
| maskSize | 3 / 5 / PRECISE | 5 | 5（PRECISE 最准但慢） | 邻域大小 |
| labelType | — | 无 | DIST_LABEL_CCOMP（分水岭常用） | 是否输出标签 |""",

    "complexity": """- 两次扫描都是 O(W·H)
- 每像素做 3–5 次比较 + 加法，常数极小
- 640×480 图 < 2ms""",

    "opencv_code": """import cv2, numpy as np
img = cv2.imread('binary.png', 0)
_, bw = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

# 距离变换（L2，5×5 mask）
dist = cv2.distanceTransform(bw, cv2.DIST_L2, 5)
cv2.normalize(dist, dist, 0, 1.0, cv2.NORM_MINMAX)

# 带标签（用于分水岭种子）
dist, labels = cv2.distanceTransform(bw, cv2.DIST_L2, 5, cv2.DIST_LABEL_CCOMP)
""",

    "naive_code": """import numpy as np, cv2

def dt_l1(binary):
    \"\"\"极简 L1 距离变换（两次扫描，教学用）\"\"\"
    h, w = binary.shape
    INF = w + h
    D = np.where(binary > 0, INF, 0).astype(np.int32)

    # Forward
    for y in range(1, h):
        for x in range(1, w):
            D[y, x] = min(D[y, x], D[y-1, x]+1, D[y, x-1]+1, D[y-1, x-1]+2)
    for y in range(1, h):
        for x in range(w-2, -1, -1):
            D[y, x] = min(D[y, x], D[y-1, x+1]+2)

    # Backward
    for y in range(h-2, -1, -1):
        for x in range(w-2, -1, -1):
            D[y, x] = min(D[y, x], D[y+1, x]+1, D[y, x+1]+1, D[y+1, x+1]+2)
    for y in range(h-2, -1, -1):
        for x in range(1, w):
            D[y, x] = min(D[y, x], D[y+1, x-1]+2)
    return D
""",

    "source_insight": """OpenCV `distanceTransform` 在 `modules/imgproc/src/distransform.cpp`：

- `cv::distTransform()` 入口，先判断 distanceType / maskSize
- L1/L2/C 分别走不同的特化：
  - `DTL1Body`：8 邻域 L1，简单 int 版本
  - `DTOperator_3x3` / `DTOperator_5x5`：Chamfer 距离（模板权重数组）
  - `DistTransform::operator()`：Danielsson 8SED 精确欧氏距离，维护 (dx,dy) 向量而不是标量
- 全部用 `parallel_for_` 分块并行
- 一个有意思的细节：Danielsson 算法不是简单的"两次扫描就完事"，它对边角误差有 4 次扫描的修正版本（OpenCV 用了 8 扫描的更稳定实现）""",

    "painpoints_body": """### 1. 前景背景搞反
距离变换默认算的是「非零像素到零像素的距离」。很多人 THRESH_BINARY_INV 之后忘了图已经反了，距离图全是 0。
**修法**：打印 D.max()，如果是 0 就知道前景背景反了。

### 2. 二值图没做干净（有噪点）
一个孤立白噪点在黑色背景上会产生一个距离 =1 的小峰，后续分水岭/骨架提取会多出一条小刺。**修法**：做距离变换前先开运算（morphologyEx MORPH_OPEN）去掉孤立点。

### 3. 用 DIST_L1 然后以为是欧氏距离
DIST_L1 算的是曼哈顿距离，圆会显示成菱形；DIST_L2 才是真实圆形。**修法**：需要圆形距离图（比如找最大内切圆）必须用 DIST_L2。

### 4. distanceTransform 返回的是 float32，忘记归一化直接 imshow
直接 imshow 会溢出/全白。**修法**：用 `cv2.normalize(dist, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)`。

### 5. maskSize=3 在大物体中心距离偏大/偏小
3×3 chamfer 误差 5%。找圆形种子（分水岭）建议 maskSize=5 或 DIST_LABEL_CCOMP。

### 6. 没注意边界像素
边界的前景点只有部分邻居参与递推，结果可能偏小。**修法**：输入前加 BORDER_CONSTANT 做 1 像素 0 padding。

### 7. 骨架化后没有剪枝
直接从距离图取局部极大当骨架，会有很多小毛刺。**修法**：骨架后做形态学细化剪枝，或使用 Hilditch/Zhang-Suen 细化算法。

### 8. 距离变换当「宽度测量」忘了校准
DIST_L2 的输出单位是像素，但如果是倾斜拍摄，像素宽度不等于物理宽度。**修法**：要物理测量先做透视矫正/相机标定。""",

    "diag_mermaid": """
    A[距离图全 0] --> B{前景背景反了?}
    B -- 是 --> C[THRESH_BINARY_INV 互换]
    D[有很多小亮点] --> E[二值图有噪声<br/>先开运算去孤立点]
    F[圆显示成菱形] --> G[换 DIST_L2]
    H[边界不准] --> I[maskSize 改 5/PRECISE<br/>加 1px padding]
    I --> J
""",

    "koujue": """**两遍扫、邻居小、分正反、L2 圆**""",

    "trick_order": """1. **二值化必须干净**：先开运算去噪
2. **distanceType=DIST_L2, maskSize=5** 作为默认
3. 输出后做 normalize 到 [0,255] 再可视化
4. 做种子提取：在 dist 上再做一次阈值化（0.7*max）+ dilate 得确定前景
5. 做骨架：取 localMax 或直接 distanceTransform→skeletonize""",

    "combos": """- **距离变换 + 阈值 → 分水岭种子**：是分水岭分割的标准前处理
- **距离变换 + 骨架化**：提取血管/文字/字符笔画骨架
- **距离变换 + Chamfer Matching**：二值图形状匹配
- **距离变换 + 最大极值 → 最大内切圆**：检测圆形物体中心""",

    "checklist_pre": """二值化 + 开运算去噪""",
    "checklist_post": """normalize 归一化到 [0,1] 或 [0,255]""",
})

# ---------- 5. 连通域分析 ----------
ALGOS.append({
    "slug": "connected-components",
    "name": "连通域分析（Two-Pass）",
    "en": "Connected Components Labeling",
    "year": "1966 / 2008 / 2016",
    "author": "Rosenfeld / Wu et al. / Grana et al.",
    "branch": "image-processing",
    "paper": "Rosenfeld 1966 / Wu-Lin 2009 BBDT / Grana 2016 SAUF",
    "chapter": "ch03",
    "level": "low",
    "paper_title": "Connected Components Labeling (综述)",
    "citations": "经典算法，累计引用巨大",
    "contrib": "两遍扫描：第一遍给每个前景点贴临时标签并用并查集合并等价类；第二遍把每个标签替换成等价类根；OpenCV 的 `connectedComponentsWithStats` 还直接输出每个域的面积、外接框、质心",
    "cv_func": "cv2.connectedComponents / cv2.connectedComponentsWithStats",
    "tagline": "把二值图里「连在一起」的白像素涂成同一种颜色，一次遍历打完标签，还给每个斑点亮出户口本（面积、框、质心）",
    "analogy": "想象一张地图上有很多群岛，你坐直升机沿海岸线飞一圈：遇到一个没被标记的岛屿，就给它插一面旗子，之后所有连在一起的陆地都插同样颜色的旗子——最后每个岛都有一个专属颜色和档案（多大、在哪、中心在哪）。",
    "scene": "OCR 字符分割（先找字块再识别）、细胞计数、缺陷检测（数有几个瑕疵）、文字块分割、背景减除后找前景目标、任意二值图里的「物件个数统计」。",
    "pros": ["O(N) 线性时间（Two-Pass 现代算法极快）", "直接给出面积/外接框/质心", "OpenCV 一行调用", "比 findContours 更适合「数个数」场景", "支持 4-连通/8-连通"],
    "cons": ["输入必须是干净的二值图", "大图像会产生很多临时标签，需要并查集优化", "不提供轮廓点（需要轮廓还是用 findContours）", "不区分孔洞（8-连通下背景和孔洞连通）"],
    "onesentence": "第一遍扫描用并查集合并等价标签，第二遍把所有标签换成等价类根标签，同时统计每个标签的面积/框/质心——是工业界「数个数/筛大小」最高频的底层操作。",

    "paper_why": """连通域标记是图像处理最古老的问题之一（1966 年 Rosenfeld 就在论文里系统讨论）。早期算法包括：
- **递归填充法**：遇到未标记点就 flood fill，但递归深度大时会栈溢出
- **逐行扫描 + 等价表**：就是 Two-Pass 的雏形

经典 Two-Pass 在 1980s 定型，但标签合并的实现效率不高。2000 年后一系列优化：
- **Wu et al. 2009**：BBDT 算法，用决策树优化邻域访问顺序
- **Grana et al. 2010/2016**：SAUF/SAUF-RemSP 算法，每行只做一次扫描、条件跳转最优，是当前 OpenCV 使用的算法，640×480 图 0.1ms 量级。""",

    "paper_innov": """**经典 Two-Pass 算法**：
1. 第一遍：从左到右、从上到下扫。对每个前景点，看**左、左上、上、右上**（4 连通只看左+上）四个邻居：
   - 邻居都没标签：分配新标签
   - 邻居有标签：取最小的那个贴上，把邻居之间的标签等价关系记进并查集
2. 第二遍：再扫一遍，把每个标签替换成并查集的根标签，并累加该标签的面积、bbox 等统计信息。

**BBDT/SAUF 优化**：
- 把 4 个邻居的 2^4=16 种「是否是前景点」组合做成决策树，每种组合走不同的代码路径，避免冗余判断
- 标签数组用 int 连续存储，缓存友好
- OpenCV 实现用了 ORC 掩码（Decision Tree）+ 块操作""",

    "paper_result": """- 速度：640×480 图 0.1ms（SAUF），比 findContours 快 5–10×
- 结果：每个连通域一个唯一 label，附带 stats（面积/外接框）和 centroid
- 工程上 90% 的「数个数/筛选」场景都能用它替代 findContours""",

    "paper_limit": """- 只能处理二值图
- 孔洞处理需要小心：前景用 8-连通时背景必须用 4-连通才能正确区分孔洞（否则孔洞会和外部背景连通）
- 不提供轮廓形状点（要形状用 findContours）""",

    "read_tip": "Wu et al. 2009《Optimizing two-pass connected-component labeling algorithms》",
    "read_tip2": "直接看 OpenCV `connectedComponents.cpp` 源码，非常精炼",

    "concepts_body": """## 1. 4-连通 vs 8-连通

- **4-连通**：只认上下左右四个邻居是连通的（斜着不算）
- **8-连通**：认 8 个邻居（含斜对角）

> 坑点：**选哪个会影响结果**——两个斜对角相邻的方块，8-连通算一个，4-连通算两个。

**孔洞处理的黄金法则**：前景用 8-连通时，背景用 4-连通；前景 4-连通时，背景 8-连通。否则会出现「孔洞被当成背景连通到外面」的问题。

## 2. 并查集（Union-Find / Disjoint Set Union）

用于管理标签等价类的数据结构，支持：
- `find(x)`：找 x 的根（路径压缩）
- `union(x,y)`：合并 x 和 y（按大小合并）

均摊复杂度 O(α(N))，α 是反阿克曼函数，几乎常数。

## 3. stats 字段说明

OpenCV `connectedComponentsWithStats` 返回的 stats 矩阵每行对应一个 label（label=0 是背景），字段：
| 字段 | 含义 |
|---|---|
| CC_STAT_LEFT | 外接框左 x |
| CC_STAT_TOP | 外接框上 y |
| CC_STAT_WIDTH | 宽 |
| CC_STAT_HEIGHT | 高 |
| CC_STAT_AREA | 面积（像素数）|

centroids 矩阵每行是 (cx, cy) 质心坐标。

## 4. connectedComponents vs findContours vs contours hierarchy

- **connectedComponents**：数个数、取 bbox、筛面积最快，但不给轮廓点
- **findContours**：给轮廓坐标链、能做形状匹配、可提取层级（外轮廓/孔洞）
- 经验：**先 connectedComponents 过滤大小，再对保留的域用 findContours 取轮廓**""",

    "mermaid": """
    A[输入二值图<br/>0=背景/其他=前景] --> B[初始化 labels=0<br/>next_label=1<br/>UF 并查集空]
    B --> C[第一遍扫描<br/>逐像素 左上→右下]
    C --> D{是前景?}
    D -- 否 --> E[labels=0 跳过]
    D -- 是 --> F[看左/左上/上/右上邻居]
    F --> G{邻居有标签?}
    G -- 都没有 --> H[分配新 label<br/>next_label++]
    G -- 有 --> I[取最小邻居标签<br/>并 union 所有等价标签]
    H --> J[贴到当前像素]
    I --> J
    J --> K[扫完全图]
    K --> L[第二遍扫描<br/>每个 label → find(label) 根]
    L --> M[累加每个根标签的<br/>面积/bbox/质心]
    M --> N[输出 labels 图 + stats + centroids]
""",

    "steps_body": """### Step 1：输入
接收 CV_8U 二值图，0=背景，非 0=前景。通常是阈值化后的结果。

### Step 2：第一遍扫描 + 标签分配
初始化 labels 全 0，next_label=1。对每个 (y,x)：
- 若 img[y,x] == 0：labels[y,x] = 0，跳过
- 否则看邻居（4/8 连通对应邻居集）：
  - 收集所有邻居中 labels > 0 的值
  - 若没有邻居标签：labels[y,x] = next_label，next_label++
  - 若有邻居标签：取 min(neighbors_labels) 贴给当前点，并用 UF.union() 把所有邻居标签之间互相合并

### Step 3：标签压缩（路径压缩）
第一遍结束后对所有 labels 做 `find()` 路径压缩，让每个标签直接指向根。同时可以**重编号**（把根标签映射到 0,1,2,...连续 ID），避免标签稀疏。

### Step 4：第二遍扫描 + 统计
再遍历一次图像，对每个前景点，取 root = find(labels[y,x])：
- 面积 stats[root][AREA] += 1
- bbox 扩展：更新 LEFT=min(LEFT,x)、TOP=min(TOP,y)、WIDTH/HEIGHT
- 质心累加：centroids[root].x += x; centroids[root].y += y

### Step 5：质心归一化
centroids 每个域的 (sum_x / area, sum_y / area) 才是真正的质心坐标。

### Step 6：输出
- labels：CV_32S 单通道标签图（每个像素值是所属域的 ID）
- stats：(N,5) float64 矩阵
- centroids：(N,2) float64 矩阵
N = 标签总数（含背景 label=0）。""",

    "params_table": """| connectivity | 8 | 8 | 4（细粒度分离）/8（抗噪） | 连通性选择 |
| ltype | CV_32S | CV_32S | CV_32S（标签多）/CV_16U（标签<65536） | 标签图类型 |
| ccltype | CCL_DEFAULT | CCL_DEFAULT | CCL_DEFAULT/CCL_SAUF/CCL_BBDT | 具体算法，默认选最快的 |""",

    "complexity": """- 两遍扫描都是 O(W·H)
- 每次 find/union 均摊 O(α(N)) ≈ O(1)
- 现代 SAUF 实现：640×480 图约 0.1–0.3ms""",

    "opencv_code": """import cv2, numpy as np
img = cv2.imread('binary.png', 0)
_, bw = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

n, labels, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)
# n = 域个数（含背景）
# labels = (H,W) int32 标签图
# stats[i] = [left, top, width, height, area]
# centroids[i] = [cx, cy]

# 可视化：给每个域涂随机颜色
vis = np.zeros((*bw.shape, 3), dtype=np.uint8)
for i in range(1, n):
    vis[labels == i] = np.random.randint(0, 255, 3)

# 筛面积：只保留 100–10000 的域
keep = [i for i in range(1,n) if 100 < stats[i, cv2.CC_STAT_AREA] < 10000]
""",

    "naive_code": """import numpy as np

class DSU:
    def __init__(self, n):
        self.p = list(range(n))
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra

def cc_two_pass(bw, conn=8):
    h, w = bw.shape
    labels = np.zeros((h,w), dtype=np.int32)
    uf = DSU(h*w)
    nxt = 1
    for y in range(h):
        for x in range(w):
            if bw[y,x] == 0: continue
            neighbors = []
            if conn == 8:
                if y>0 and x>0 and labels[y-1,x-1]: neighbors.append(labels[y-1,x-1])
            if y>0 and labels[y-1,x]: neighbors.append(labels[y-1,x])
            if conn==8 and y>0 and x<w-1 and labels[y-1,x+1]: neighbors.append(labels[y-1,x+1])
            if x>0 and labels[y,x-1]: neighbors.append(labels[y,x-1])
            if not neighbors:
                labels[y,x] = nxt; nxt += 1
            else:
                m = min(neighbors); labels[y,x] = m
                for n in neighbors: uf.union(m, n)
    # 第二遍
    for y in range(h):
        for x in range(w):
            if labels[y,x]:
                labels[y,x] = uf.find(labels[y,x])
    return labels, nxt
""",

    "source_insight": """OpenCV 连通域源码在 `modules/imgproc/src/connectedcomponents.cpp`：

- `cv::connectedComponents_sub1`：入口，按 ltype/ccltype 分派
- `CCL_SAUF<>`、`CCL_BBDT<>`、`CCL_GRANA<>` 等模板特化
- SAUF（Scan Array Union Find）：Grana 2010 算法，每个像素用一棵 16 叶决策树决定如何处理邻居（0=全 0、1=只有左、…、15=四个邻居全前景点），是当前最快算法
- stats 累加用了向量化：`LabelStatistics::addBlock()` 一次性加一块，减少逐像素判断""",

    "painpoints_body": """### 1. 二值图没做干净导致「碎片域」爆炸
阈值没调好，前景/背景边缘出现很多 1–2 像素的小碎片，connectedComponents 会返回几千个 label，后续处理极慢。
**修法**：先做 MORPH_OPEN（开运算）去掉小噪点，然后再连通域。

### 2. 忘记 label 0 是背景
直接 `for i in range(n)` 遍历会把背景当一个「大物体」。**修法**：从 i=1 开始遍历。

### 3. 4-连通 / 8-连通 选错
OCR 字符分割时，两个笔画斜对角相邻用 8-连通会连在一起（如"明"的日和月之间有个对角点就连成一个了），导致字被错误合并。**修法**：文字分割常用 4-连通，或加形态学闭运算补断裂。

### 4. 孔洞被算成独立域（错用 8+8）
前景 8-连通 + 没有对背景单独处理时，孔洞会被标成独立的前景标签。**修法**：要识别孔洞，再跑一次反向（背景作为前景）的连通域，或用 findContours + RETR_CCOMP 带层级。

### 5. ltype=CV_8U 溢出
如果图中有超过 255 个连通域，CV_8U 标签会溢出（最多 255）。**修法**：默认用 CV_32S。

### 6. 阈值用 THRESH_BINARY 而对象是黑底白字？
连通域关心的是「非零像素」，黑底白字 THRESH_BINARY 是正确的；白底黑字要 THRESH_BINARY_INV，否则整个白纸当成一个大域。

### 7. connectedComponents 没有轮廓信息
筛完大小之后想画轮廓/做形状分析——**修法**：对每个保留 label 用 `(labels==i).astype(np.uint8)*255` 生成 mask，再 `findContours(mask, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)`。

### 8. 速度变慢原因：图太大且域太多
4K 图上几千个域时，输出的 stats/centroids 会有几千行，但是算法本身仍是 O(N)。要加速：先 resize 到 1/2、二值化+腐蚀去小斑，再做。""",

    "diag_mermaid": """
    A[域太多/小碎片] --> B[先 MORPH_OPEN 去噪]
    C[背景被当成一个大域] --> D[从 i=1 开始遍历<br/>不要包含 label=0]
    E[字符粘连] --> F[换 4-连通<br/>或先腐蚀后连通域]
    G[想要轮廓] --> H[connectedComponents 筛大小+<br/>findContours 取轮廓]
    I[标签溢出] --> J[ltype 用 CV_32S]
""",

    "koujue": """**二值净、两趟扫、从 1 数、按面筛**""",

    "trick_order": """1. 二值化必须干净（先开运算）
2. connectivity 选对（字符 4、一般 8）
3. `connectedComponentsWithStats` 一次性拿所有信息
4. **按面积过滤** stats[i, CC_STAT_AREA]，保留目标大小范围
5. 需要形状再对每个 mask 用 findContours""",

    "combos": """- **MOG2 → 连通域 → 按面积筛**：视频监控里数前景目标
- **阈值化 → 连通域 → OCR**：字符分割先把每个字切出来
- **阈值化 → 连通域 → 按圆度筛**：检测圆形/球形缺陷
- **连通域筛选 → GrabCut 初始化**：用连通域 bbox 作为 GrabCut 输入""",

    "checklist_pre": """二值化 + 开运算去噪""",
    "checklist_post": """按面积/宽高比过滤""",
})

# ---------- 6. 区域生长 ----------
ALGOS.append({
    "slug": "region-growing",
    "name": "区域生长分割",
    "en": "Region Growing",
    "year": "1994",
    "author": "Rolf Adams / Leanne Bischof (Seeded Region Growing)",
    "branch": "segmentation",
    "paper": "Adams & Bischof, TPAMI 1994",
    "chapter": "ch10",
    "level": "mid",
    "paper_title": "Seeded Region Growing",
    "citations": "~4200+",
    "contrib": "从用户给定（或自动选取）的种子点出发，把邻域中与区域均值差异小于阈值的像素归并进来，动态更新区域均值，直到所有像素被分配到某个区域；是分水岭之前最经典的交互式分割方法",
    "cv_func": "无 OpenCV 原生 API（需手写或用 skimage.segmentation.random_walker / morphology.watershed 间接替代）",
    "tagline": "几颗种子丢进图里，像水一样往四周漫，只灌和自己「颜色相近」的地方，最后把图切成几块",
    "analogy": "想象你在山顶泼几杯染料（不同颜色），染料顺着山坡往下流，只往颜色和自己差不多的地方跑（因为颜色差大代表「不是同一个物体」），最后不同色块自然分出了边界——这就是区域生长。",
    "scene": "医学影像分割（肿瘤/器官）、交互式抠图（用户点几下就能分出物体）、遥感影像地块分割、工业检测里颜色一致区域的提取。",
    "pros": ["原理直观，容易解释给非技术同事", "交互式（种子由用户指定）", "能处理任意形状区域", "边界闭合", "对初始种子鲁棒性较好"],
    "cons": ["需要种子点（人工或自动）", "阈值/相似性准则选择敏感", "串行算法较慢（BFS 按像素优先级）", "对噪声敏感（需要预处理）", "容易漏过分水岭式的细长连接"],
    "onesentence": "从种子出发用优先级队列向外扩散，每次把最像当前区域的邻域像素吸进来，动态更新区域统计量，直到所有像素都被吸进某个区域——最直觉也最经典的区域分割算法。",

    "paper_why": """传统分割方法有两类：
1. **基于边缘**（Canny/Sobel + 边缘连接）：边缘不闭合时区域不完整
2. **基于阈值/区域分裂合并**：全局阈值对光照不均鲁棒差；分裂合并是自顶向下，粒度粗

Adams & Bischof 1994 年提出 Seeded Region Growing（SRG），核心思想：让用户给几颗种子，然后区域自动向外扩张，每次扩张选「最像」区域的那个邻域像素。关键贡献：
- 用边界像素和各区域均值的**差**作为优先级，构成 priority queue
- 每次取最小差的像素归并，更新区域均值
- 天然避免了区域重叠，保证分割闭合""",

    "paper_innov": """**创新 1：优先级队列驱动的有序扩张**

不像简单 BFS/FloodFill（按队列先后），SRG 用**最小堆**，每次弹出「和最近区域差异最小」的像素。这样边界总是沿着「最像的方向」推进，不会一口气吃进异类像素。

**创新 2：动态区域统计量**

每次归并一个像素，区域的均值/方差实时更新（增量公式）：
$$\\mu_{new} = \\frac{n\\mu_{old} + x}{n+1}, \\quad n_{new} = n+1$$
这样不需要重新遍历区域就能保持统计量准确。

**创新 3：局部相似性判据**

像素 x 对区域 R_i 的相似度 = $\\delta(x, R_i) = |I(x) - \\mu_{R_i}|$（灰度）或（彩色）$||I(x) - \\mu_{R_i}||_2$。
如果邻域像素同时属于多个区域的候选，把它放进堆里所有区域的条目，取到它时如果它已经被别的区域占了就跳过。

**创新 4：边界自动形成**

当两个扩张波前相遇时，它们之间形成自然边界，无需额外处理。""",

    "paper_result": """在医学影像（脑部 MRI）上，SRG 只需要用户在白质、灰质、脑脊液各点一颗种子，就能把三大组织分出，结果比阈值法和边缘法干净得多。""",

    "paper_limit": """- 初始种子位置敏感（种子放错区域结果就错）
- 相似性阈值无自适应
- 串行堆算法时间复杂度 O(N log N)，大数据慢
- 灰度均匀性假设成立时效果好，纹理区域差
- 被后来的 GrabCut（2004）、随机游走（Random Walker，2006）部分取代""",

    "read_tip": "Adams & Bischof 1994 TPAMI 原文（只有 13 页）",
    "read_tip2": "重点看 Section II（算法）和 Fig.2（扩张过程示意）",

    "concepts_body": """## 1. 种子点（Seed）

分割的起点，可以是：
- **人工交互**：用户鼠标点击
- **自动种子**：通过阈值、连通域、形态学、距离变换峰值等方法自动选
种子的位置和数量决定了最终分割的块数——一个种子对应一个区域。

## 2. 相似性准则

区域生长的核心是「什么样的像素算自己人」：
- **灰度差**：|I(x) - μ| < T（最简单）
- **颜色差**（彩色）：||I(x) - μ|| < T（LAB 空间欧氏距离最好）
- **纹理差**：用局部纹理特征（LBP/方差）
- **边缘阻挡**：梯度大的地方停止生长（避免越界）

## 3. 邻域定义

- 4 邻域：上下左右（慢，但边界更稳）
- 8 邻域：含对角（快，能沿对角生长）

## 4. 优先级队列（最小堆）

heap 里存 (δ, x, y, region_id)，每次 pop 最小 δ 的像素，尝试归并。如果该像素还没被分配，就标为 region_id，并把它的 4/8 邻居压入堆。

## 5. 与 Flood Fill 的区别

Flood Fill：固定阈值，BFS 顺序不讲究，一个种子只能填一个连通块。
Region Growing：动态阈值（相对区域均值），多种子同时扩张，按相似性优先级推进，是「多区域竞争」。

## 6. 与分水岭的关系

分水岭是**地形灌水**，所有极小值同时开始灌；区域生长是**指定种子灌水**，种子由人/算法指定，避免过分割。""",

    "mermaid": """
    A[输入灰度/彩色图] --> B[用户/自动放置种子<br/>每个种子=一个区域]
    B --> C[初始化：种子标 region_id<br/>区域均值 μ=种子灰度<br/>邻域像素入优先队列]
    C --> D{堆非空?}
    D -- 是 --> E[pop δ 最小的像素]
    E --> F{像素已被分配?}
    F -- 是 --> D
    F -- 否 --> G[标为对应 region<br/>更新区域 μ/n]
    G --> H[把它的 4/8 邻域未分配像素<br/>按 δ 压入堆]
    H --> D
    D -- 否 --> I[所有像素分配完毕<br/>输出 label 图]
""",

    "steps_body": """### Step 1：预处理
- 高斯平滑去噪（σ=1–2），避免噪声让生长乱跳
- 必要时做 CLAHE 增强对比度
- 彩色图建议转 LAB 空间（欧氏距离感知均匀）

### Step 2：放置种子
- 人工：用户点击
- 自动：距离变换局部极大（和分水岭类似）、阈值确定的前景/背景硬区域、或网格采样

### Step 3：初始化数据结构
- `labels[y,x] = -1`（未分配），种子点 labels=region_id
- `region_mean[i]` = 种子灰度，`region_count[i]` = 1
- 优先队列（heapq）：把种子的 4/8 邻居按 (|I-μ|, x, y, region_id) 压入
- `in_heap[y,x]` 标记避免重复入堆

### Step 4：主循环
```
while heap 非空:
    delta, x, y, rid = heappop(heap)
    if labels[y,x] != -1: continue     # 已被其他区域抢走
    labels[y,x] = rid
    更新 region_mean[rid]（增量公式）
    更新 region_count[rid]
    for (nx, ny) in 4/8 neighbors:
        if labels[ny,nx] == -1 and not in_heap:
            d = abs(I[ny,nx] - region_mean[rid])
            heappush(heap, (d, nx, ny, rid))
            in_heap[ny,nx] = True
```

### Step 5：后处理（可选）
- 过小区域合并到邻居
- 闭运算填小缝""",

    "params_table": """| 邻域 connectivity | 8 | — | 8（默认速度快），4 边界更稳 | 生长邻域 |
| 相似性度量 | 灰度差 | — | LAB 颜色欧氏距离（彩色） | 准则选择 |
| 阈值（如果用固定阈值） | — | 无（优先级不需要） | 通常不需要，靠堆自动 | SRG 本质无阈值 |
| 种子数 | ≥2 | — | 目标数 +1（含背景） | 决定分割块数 |""",

    "complexity": """- 每个像素入堆一次，每次 push/pop O(log N)
- 总复杂度 O(N log N)，N=像素数
- 512×512 图纯 Python 约 5–20s，C++ 实现约 50–200ms""",

    "opencv_code": """# OpenCV 没有直接的 SRG API，可用 floodFill 或 watershed 替代。
# 若要真正 SRG，建议用 skimage 或自己实现（见 naive code）。
import cv2, numpy as np
# 近似：用 floodFill（单一阈值，BFS 顺序）做单区域生长：
img = cv2.imread('scene.jpg')
mask = np.zeros((img.shape[0]+2, img.shape[1]+2), np.uint8)
seed_pt = (100, 100)
lo = (20, 20, 20); up = (20, 20, 20)
cv2.floodFill(img, mask, seed_pt, (0,255,0), lo, up,
              flags=cv2.FLOODFILL_FIXED_RANGE)
""",

    "naive_code": """import numpy as np, cv2, heapq

def region_growing(img, seeds, conn=8):
    \"\"\"
    img: 单通道灰度图 (H,W) float32
    seeds: [(x,y, region_id), ...]
    返回 labels 图
    \"\"\"
    h, w = img.shape
    labels = -np.ones((h,w), dtype=np.int32)
    in_heap = np.zeros((h,w), dtype=bool)
    mean = {}; count = {}
    heap = []

    if conn == 8:
        dy = [-1,-1,-1,0,0,1,1,1]; dx = [-1,0,1,-1,1,-1,0,1]
    else:
        dy = [-1,1,0,0]; dx = [0,0,-1,1]

    for (sx, sy, rid) in seeds:
        labels[sy, sx] = rid
        mean[rid] = float(img[sy, sx])
        count[rid] = 1
        for j in range(len(dx)):
            ny, nx = sy+dy[j], sx+dx[j]
            if 0<=ny<h and 0<=nx<w and labels[ny,nx]==-1 and not in_heap[ny,nx]:
                d = abs(float(img[ny,nx]) - mean[rid])
                heapq.heappush(heap, (d, nx, ny, rid))
                in_heap[ny,nx] = True

    while heap:
        d, x, y, rid = heapq.heappop(heap)
        if labels[y,x] != -1: continue
        labels[y,x] = rid
        # 更新均值
        count[rid] += 1
        mean[rid] = (mean[rid]*(count[rid]-1) + float(img[y,x]))/count[rid]
        for j in range(len(dx)):
            ny, nx = y+dy[j], x+dx[j]
            if 0<=ny<h and 0<=nx<w and labels[ny,nx]==-1 and not in_heap[ny,nx]:
                nd = abs(float(img[ny,nx]) - mean[rid])
                heapq.heappush(heap, (nd, nx, ny, rid))
                in_heap[ny,nx] = True
    return labels
""",

    "source_insight": """OpenCV 没有直接的 SRG 实现，但 ITK（医学影像库）里有非常成熟的 `itk::RegionGrowingImageFilter` 家族：
- `itk::ConnectedThresholdImageFilter`：固定阈值 flood fill
- `itk::ConfidenceConnectedImageFilter`：动态统计量（均值±σ·倍数）
- `itk::VectorConfidenceConnected`：彩色/多通道版本

另外 OpenCV 的 `cv::watershed` 和 `cv::floodFill` 可以覆盖 SRG 的大部分用例：
- 单区域固定阈值生长 → floodFill
- 多种子竞争扩张 → watershed（把种子当 marker）""",

    "painpoints_body": """### 1. 没去噪就直接生长，边界到处漏
噪声像素会把区域均值慢慢拉偏，最后长到别的区域里。**修法**：先做 σ=1–2 的高斯模糊。

### 2. 种子点放错位置
种子必须放在**区域内部**（别放边界上）。如果种子放错了一块阴影，那块阴影会被单独分出。**修法**：提供交互允许用户删除错误种子/新增种子。

### 3. 用 BFS 代替优先队列
简单 BFS（队列先进先出）没有优先级，早进队的像素即使差异大也会被先归并，边界会不规则。**修法**：必须用 heap 按 δ 排序。

### 4. 区域均值不更新
始终用初始种子灰度做阈值，区域长着长着就长不动（因为区域本身灰度是渐变的）。**修法**：每次归并用增量公式更新均值。

### 5. 跨边缘漏长（边缘梯度小的时候）
物体内部有弱纹理，区域生长可能跨过弱边缘长到背景。**修法**：加「边缘阻挡」——梯度 magnitude 大的地方不入堆；或改用 watershed。

### 6. 纯 Python 实现太慢
heapq 处理 512×512=26 万像素在 Python 里 10s+。**修法**：用 C++/Cython/Numba，或直接换 watershed（OpenCV 优化过，ms 级）。

### 7. 彩色图用灰度差
RGB 空间的差不感知均匀。**修法**：转 LAB，用 E = √((L1-L2)² + (a1-a2)² + (b1-b2)²)。

### 8. 长到最后有孤立小孔
未被分配的孤立像素（最后才遇到）会被标为它最后被推入的 region，可能错。**修法**：主循环结束后，对 -1 像素做一次最近邻填充或中值滤波。""",

    "diag_mermaid": """
    A[边界乱穿] --> B[先高斯去噪<br/>或加边缘阻挡]
    C[结果太碎] --> D{种子太多?}
    D -- 是 --> E[减少种子]
    D -- 否 --> F[后处理合并小区域]
    G[长到一半停住] --> H{区域均值更新了吗?}
    H -- 否 --> I[改用增量均值更新]
    J[太慢] --> K[换 C++ 实现<br/>或用 watershed 替代]
""",

    "koujue": """**种子稳、均值跟、堆排序、遇边停**""",

    "trick_order": """1. **高斯平滑**（σ=1.5）预处理
2. 种子放在区域内部，每种颜色一个种子 + 一个背景种子
3. LAB 空间 + 颜色欧氏距离（彩色）
4. 8 邻域 heap 生长
5. 结果做闭运算合小孔""",

    "combos": """- **自动种子 + 区域生长**：先用 Otsu/距离变换找硬前景/背景当种子，再 SRG
- **Watershed + SRG 混合**：watershed 容易过分割，SRG 可做区域合并
- **SRG + GrabCut**：SRG 粗分，GrabCut 精修边界
- **SRG + 医学影像**：ITK 里的 ConfidenceConnected 是临床常用工具""",

    "checklist_pre": """高斯平滑 + （彩色时）转 LAB""",
    "checklist_post": """小区域合并 + 形态学闭运算""",
})

print(f"已追加 3 个算法，累计 {len(ALGOS)} 个")

# ---------- 7. Gabor 滤波 ----------
ALGOS.append({
    "slug": "gabor",
    "name": "Gabor 滤波器",
    "en": "Gabor Filter / Gabor Wavelet",
    "year": "1946 / 1980s",
    "author": "Dennis Gabor (1946) / Daugman (1985) / Jain et al. (1990s)",
    "branch": "image-processing",
    "paper": "Daugman 1985 / Bovik et al. 1990",
    "chapter": "ch07",
    "level": "mid",
    "paper_title": "Uncertainty relation for resolution in space... (Daugman 1985)",
    "citations": "~20000+",
    "contrib": "用高斯包络调制的复正弦平面波作为卷积核，在空间域和频率域同时达到不确定性原理下界，是提取局部方向/尺度纹理特征的最佳基；被用于指纹识别、虹膜识别、纹理分类、边缘检测",
    "cv_func": "cv2.getGaborKernel() + cv2.filter2D()",
    "tagline": "一块带方向和纹路频率的「放大镜」，旋转不同角度扫一遍图，就能把对应方向的纹理抓出来",
    "analogy": "想象你拿一把梳子去刮不同方向的木纹：梳子方向和木纹平行时阻力最大（响应强），垂直时没感觉。Gabor 核就是这样一把梳子——一个特定方向、特定频率的「纹路探针」，通常要做 8 个方向 × 5 个频率共 40 个核组成 Gabor 滤波器组，才能把图像里各个方向、粗细的纹理全抓出来。",
    "scene": "指纹识别（核心）、虹膜识别（Daugman 用的就是它）、纹理分类、布匹/纸张缺陷检测、文档/车牌识别前处理、人脸识别（弹性图匹配）、边缘检测（多方向）。",
    "pros": ["时频局部化最优（不确定性原理下界）", "方向选择性强、尺度选择性强", "类似生物视觉 V1 区简单细胞感受野", "OpenCV 直接生成核", "对光照/对比度局部鲁棒"],
    "cons": ["需要一个滤波器组（几十核），计算量大", "参数多（波长/方向/相位/带宽/纵横比）", "输出是多维特征（每个像素 40 维响应）", "非旋转不变（需要做多个方向）"],
    "onesentence": "Gabor 核 = 高斯窗口 × 复正弦波；用不同方向/尺度组成滤波器组，卷积后每个像素得到一个响应向量，就是该点的「纹理指纹」——是工业纹理分析和生物识别的黄金标准。",

    "paper_why": """1946 年物理学家 Dennis Gabor（后来全息术诺贝尔奖得主）提出把信号分解成「时间-频率原子」的思想，这是 Gabor 变换的源头。

1985 年 John Daugman 把它扩展到 2D，并证明：2D Gabor 函数是**空间域-频率域联合不确定性下界的唯一解**——也就是说，它是「在空间上够局部、在频率上够尖锐」的最优折中，数学上找不到更好的。

Daugman 立刻把它用在了**虹膜识别**上（1993 年专利），成了虹膜识别的工业标准。Bovik、Clark、Geisler（1990）把 Gabor 引入纹理分析；Jain 等人在 90 年代把它用到指纹识别。从此 Gabor 成了生物识别和纹理分析的标配。""",

    "paper_innov": """**核心公式**：2D Gabor 核是高斯包络乘平面波：

$$g(x,y) = \\exp\\left(-\\frac{x'^2 + \\gamma^2 y'^2}{2\\sigma^2}\\right) \\cdot \\exp\\left(i\\left(2\\pi\\frac{x'}{\\lambda} + \\psi\\right)\\right)$$

其中：
- $x' = x\\cos\\theta + y\\sin\\theta$（旋转坐标，θ=方向）
- $y' = -x\\sin\\theta + y\\cos\\theta$
- λ = 波长（正弦波周期，像素）
- θ = 方向（0~π）
- ψ = 相位偏移（0/π 实部取中心/边缘；π/2 虚部）
- σ = 高斯包络带宽
- γ = 空间纵横比（默认 0.5，椭圆）

**Gabor 滤波器组**：通常构造：
- 方向：8 个（0°, 22.5°, 45°, ..., 157.5°）
- 尺度/波长：5 个（3, 5, 9, 15, 25 像素等对数分布）
共 40 个核，每个像素得到 40 个响应值作为纹理特征。""",

    "paper_result": """- 指纹识别：用 8 方向 Gabor 增强指纹纹路（Hong & Jain 1998），这是 FBI 指纹系统的标准
- 虹膜识别：Daugman 的 Gabor 相位编码达到 FAR<1/10^6
- 纹理分类：在 Brodatz 纹理库上达到 95%+ 准确率（SVM + Gabor 响应均值方差）""",

    "paper_limit": """- 参数多，调起来繁琐
- 40 个核卷积计算量大（虽可用 FFT 加速）
- 不具备旋转不变性（除非对响应取方向 max）
- 被深度学习模型（CNN）大幅超越，但在小样本/无 GPU 场景仍是首选
- 对纹理的「语义」理解不如 LBP 简单、不如 CNN 强""",

    "read_tip": "Daugman 1985 的 uncertainty relation 论文",
    "read_tip2": "Jain et al.《Filter-based Fingerprint Matching》——最经典的 Gabor 应用论文",

    "concepts_body": """## 1. 不确定性原理

信号处理有一个基本下界：一个信号不能同时在时间（空间）域和频率域都无限窄。数学上：
$$\\Delta x \\cdot \\Delta f \\geq \\frac{1}{4\\pi}$$

Gabor 函数是**唯一达到等号**的基，因此它是「局部纹理」的最优探针——这就是它在生物视觉里被采用的根本原因。

## 2. 五个参数的物理意义

| 参数 | 含义 | 典型值 |
|---|---|---|
| λ (lambda) | 正弦波波长（像素），决定纹路**粗细** | 3–25 |
| θ (theta) | 核的方向，决定**响应哪方向**的纹路 | 0~π，多取 8 方向 |
| ψ (psi) | 相位偏移，0 为对称中心响应，π/2 为边缘响应 | 0（实部余弦）或 π/2（虚部正弦） |
| σ (sigma) | 高斯包络的宽度，决定感受野大小 | ≈0.56λ（与带宽 1 octave 对应） |
| γ (gamma) | 核的纵横比，1=圆，<1=沿 y' 方向扁 | 0.5（椭圆，类似视觉皮层细胞）|

## 3. 实部 vs 虚部 vs 幅值

Gabor 核是复数，滤波后得到复响应：
- 实部（cos 部分）：对称中心响应，类似 blob 检测
- 虚部（sin 部分）：边缘响应，类似方向边缘检测器
- 幅值（magnitude）：√(Re² + Im²)，相位无关，纹理分析最常用

## 4. Gabor 滤波器组设计

方向通常 0°–180° 等分 8 或 6 个（因为 180° 以上是重复）；尺度（波长）按对数等比（例如 λ_k = λ_{min} · s^k，s=√2 倍频）。总核数 = #方向 × #尺度。

## 5. Gabor vs LBP

- **Gabor**：多尺度多方向，对细纹理、边缘方向性敏感，维度高
- **LBP**：单尺度（可多尺度），只编码局部符号差，维度低、计算快
- 工程上经常：**Gabor 做特征，LBP 做快速预筛**，或两者结合。

## 6. Gabor 与生物视觉

哺乳动物 V1 区简单细胞（simple cell）的感受野形状和 Gabor 函数高度吻合——也就是说，Gabor 不是人工设计的，而是**进化出来的最优解**，这一点让它在神经科学/视觉模型中有特殊地位。""",

    "mermaid": """
    A[输入灰度图] --> B[设计 Gabor 滤波器组<br/>n 方向 × m 尺度]
    B --> C[对每个核 ksize×ksize<br/>cv2.getGaborKernel 生成实部]
    C --> D[每个核对图像做 cv2.filter2D 卷积]
    D --> E[得到 n×m 张响应图]
    E --> F{应用?}
    F -- 纹理分类 --> G[每个响应图算均值+方差<br/>拼成特征向量→SVM]
    F -- 指纹增强 --> H[沿局部脊线方向的核响应做二值化<br/>得到增强纹路]
    F -- 边缘检测 --> I[取多方向响应的 max<br/>得到多方向边缘]
""",

    "steps_body": """### Step 1：设计滤波器组参数
- 方向：θ = k·π/8（k=0..7，共 8 方向）
- 波长：λ = [3, 5, 9, 15, 25]（共 5 尺度）
- 其他：ψ=0（实部余弦），γ=0.5，σ=0.56·λ（带宽约 1 倍频）
- ksize：通常设为奇数，约 6σ 大小（例如 31×31）

### Step 2：生成每个核
```python
cv2.getGaborKernel((ksize, ksize), sigma, theta, lambd, gamma, psi, ktype=cv2.CV_32F)
```
返回一个 (ksize,ksize) float32 核，已经过零均值归一化（可直接 filter2D）。

### Step 3：卷积
对每个核 `g`：`resp = cv2.filter2D(img, cv2.CV_32F, g)`
- 输出 CV_32F 响应图，正值代表「同相位匹配」，负值代表反相位匹配
- 若只关心能量，取 np.abs(resp)

### Step 4：特征提取
- **纹理分类**：每个响应图分块（如 16×16 block）算 mean 和 std，拼成向量送分类器
- **指纹增强**：根据局部脊线方向选择对应 θ 的核做增强
- **边缘检测**：对每个像素取多方向响应的 max，即「最佳朝向的边缘」

### Step 5：归一化
由于不同尺度的核响应幅度不同，通常对每个响应图做 L2 归一化或 z-score 归一化，再拼接。""",

    "params_table": """| ksize | 31×31 | — | 6σ+1（奇数） | 核大小，过小截断高斯 |
| sigma | 0.56λ | 自动 | 0.56λ（1 octave） | 高斯包络，大→感受野大 |
| theta | 8 方向均分 | 0 | 0~π 取 8 或 6 个 | 方向采样 |
| lambd | 3,5,9,15,25 | 11 | 按倍频程 | 波长（纹路粗细）|
| gamma | 0.5 | 1.0 | 0.5 | 椭圆纵横比，越扁越方向敏感 |
| psi | 0 或 π/2 | 0 | 0（实部，blob）/π/2（虚部，边缘）| 相位 |""",

    "complexity": """- 单个核卷积：O(ksize² · W · H)，但 filter2D 内部用 separable / FFT 优化
- 40 个核的 Gabor 组：640×480 图在 OpenCV 上约 50–100ms
- FFT 卷积可降到 O(n_m_log_n · W · H)""",

    "opencv_code": """import cv2, numpy as np
img = cv2.imread('fingerprint.jpg', 0)

# 构建 Gabor 滤波器组（8 方向 × 5 尺度）
def build_gabor_bank():
    bank = []
    for theta in np.arange(0, np.pi, np.pi/8):
        for lambd in [3,5,9,15,25]:
            ksize = 31
            sigma = 0.56 * lambd
            gamma = 0.5
            k = cv2.getGaborKernel((ksize,ksize), sigma, theta, lambd, gamma, 0, ktype=cv2.CV_32F)
            bank.append(k)
    return bank

bank = build_gabor_bank()
responses = [cv2.filter2D(img, cv2.CV_32F, k) for k in bank]

# 取多方向 max（多方向边缘）
multi_edge = np.max([np.abs(r) for r in responses], axis=0)

# 纹理特征：每张响应图的 mean + std
feat = []
for r in responses:
    feat.extend([r.mean(), r.std()])
feat = np.array(feat)   # 80 维向量
""",

    "naive_code": """import numpy as np

def gabor_kernel(ksize=31, sigma=4.0, theta=0, lambd=10, gamma=0.5, psi=0):
    \"\"\"手写 Gabor 核（教学用，可与 cv2.getGaborKernel 对照）\"\"\"
    ax = np.arange(-ksize//2+1, ksize//2+1)
    xx, yy = np.meshgrid(ax, ax)
    x_prime = xx*np.cos(theta) + yy*np.sin(theta)
    y_prime = -xx*np.sin(theta) + yy*np.cos(theta)
    gauss = np.exp(-(x_prime**2 + (gamma*y_prime)**2) / (2*sigma**2))
    sinusoid = np.cos(2*np.pi*x_prime/lambd + psi)   # 实部
    return gauss * sinusoid
""",

    "source_insight": """OpenCV `cv::getGaborKernel` 在 `modules/imgproc/src/gabor.cpp`，代码非常短（约 50 行）：
1. 按公式算旋转后的 x'/y' 坐标（meshgrid）
2. 计算高斯项和正弦项逐像素相乘
3. 做 DC 校正：减去均值，让核零均值（避免响应受灰度整体偏移影响）
4. 归一化 L1 或 L2

注意：OpenCV 默认返回**实部（余弦）**。若要复数值响应，需要分别取 psi=0 和 psi=π/2 生成两个核，分别卷积得到 Re 和 Im，再取幅值。""",

    "painpoints_body": """### 1. ksize 太小导致核被截断
高斯尾部被截断会产生频谱旁瓣、响应畸变。**修法**：ksize ≈ 6σ+1（奇数）。

### 2. 没做 DC 校正导致对灰度整体偏移敏感
OpenCV 的 getGaborKernel 已经做了 DC 校正（核均值为 0），自己写核时容易忘——结果整体亮度高的地方响应都大，不像纹理响应。

### 3. 用浮点响应直接阈值化
Gabor 响应有正有负，阈值前必须取 np.abs() 或平方。**修法**：对实部/虚部分别取模。

### 4. 只用一个方向/一个尺度，结果没意义
单 Gabor 核只对特定方向/粗细的纹理响应；你必须用**滤波器组**。

### 5. 把 Gabor 当万能特征
Gabor 在规则纹理（指纹/虹膜/织物）上效果极好，但对**物体识别**、**自然场景**这种纹理不统一的任务，不如 SIFT/CNN。

### 6. 没归一化就拼特征向量
大尺度 λ 的核响应幅度天然大于小尺度，不做归一化分类器会偏向大尺度。**修法**：每个响应图做 z-score 或归一化到 [0,1]。

### 7. 直接用彩色图
Gabor 是单通道算子。彩色图通常转灰度再做；或对 L 通道做。

### 8. 太慢没做 FFT 加速
40 核 + 大 ksize 在大图上会慢。**修法**：用 cv2.createGaussianKernel 那种 separable 不行（Gabor 不可分）；可以用 `cv2.filter2D` 内部做 DFT（大核时 OpenCV 会自动用 DFT），或自己用 np.fft.fft2 乘频域核。""",

    "diag_mermaid": """
    A[响应一片白/一片黑] --> B[核没 DC 校正<br/>或没做归一化]
    C[响应全是水平/垂直条纹] --> D[方向没采样够<br/>至少 6–8 个方向]
    E[粗纹理抓不到] --> F[加大 lambd<br/>加更大尺度的核]
    G[细纹理抓不到] --> H[减小 lambd 到 3–5]
    I[太慢] --> J[用 FFT 卷积<br/>或减少核数量]
""",

    "koujue": """**波长细、方向八、σ 配 λ、零均归**""",

    "trick_order": """1. 灰度化 + 直方图均衡/CLAHE
2. **方向 8 个、尺度 5 个**作为默认组
3. ksize = 6σ+1（奇数），sigma=0.56λ
4. 取 abs() 作为响应幅度
5. 每通道 z-score 归一化后再拼特征""",

    "combos": """- **Gabor + SVM**：经典纹理分类 pipeline（Brodatz、KTH-TIPS）
- **Gabor 增强 + 细化 + 特征点**：指纹识别（Hong-Jain 1998）
- **Gabor 幅值图 + LBP**：多特征融合纹理分类
- **多方向 Gabor max**：Canny 的替代方案（多尺度多方向边缘）""",

    "checklist_pre": """灰度化 + CLAHE/归一化增强""",
    "checklist_post": """归一化响应，再做分类/检测""",
})

# ---------- 8. CSRT 跟踪 ----------
ALGOS.append({
    "slug": "csrt",
    "name": "CSRT 通道与空间可靠性跟踪",
    "en": "Channel and Spatial Reliability Tracking (Discriminative Correlation Filter with Channel and Spatial Reliability)",
    "year": "2017",
    "author": "Alan Lukežič / Tomáš Vojíř / Luka Čehovin / Jiří Matas / Matej Kristan",
    "branch": "detection",
    "paper": "CVPR 2017",
    "chapter": "ch14",
    "level": "mid",
    "paper_title": "Discriminative Correlation Filter with Channel and Spatial Reliability",
    "citations": "~1200+",
    "contrib": "在 KCF/MOSSE 相关滤波基础上引入「空间可靠性图」（让目标边界不规则的区域被掩膜掉）和「通道可靠性权重」（让不可靠通道被降权），大幅提升遮挡、形变、非矩形目标场景下的鲁棒性",
    "cv_func": "cv2.TrackerCSRT_create()",
    "tagline": "KCF 的进化版——不只认矩形框，还学会了「这个形状里哪部分是目标、哪部分应该被忽略、哪个特征通道更可信」，精度是 OpenCV 传统跟踪器里最高的一档",
    "analogy": "KCF 像你拿一张**矩形便利贴**在画面上找相似位置，贴到哪里响应最大就说目标在那；但如果目标是个走路的人，便利贴矩形里有一半是背景，模板会越跟越飘。CSRT 学会了两件事：①在便利贴上画一个**不规则的遮罩**（空间可靠性），只学目标本身的像素；②多通道（HoG+Colornames）投票时，给「靠谱的通道」更多权重（通道可靠性）。",
    "scene": "视频中单个目标的长时跟踪，尤其是目标**非矩形**（如行人、动物）、有**遮挡**（过柱子/过人）、有**形变**（转身、弯腰）的场景；速度稍慢于 KCF，但精度显著更高。",
    "pros": ["精度是 OpenCV 传统跟踪器里最高的一档（VOT 2016/2017 冠军）", "支持非矩形空间掩膜", "多通道可靠性加权", "对遮挡/形变比 KCF 鲁棒", "OpenCV contrib 原生支持"],
    "cons": ["速度比 KCF 慢（CPU 约 25–50 FPS vs KCF 150+ FPS）", "需要 opencv-contrib-python 才有 TrackerCSRT", "参数比 KCF 多", "长时全遮挡仍会飘（需配检测器重检）"],
    "onesentence": "在 DCF 框架里引入空间可靠性图（基于前景/背景颜色分割自动估计）和通道可靠性（基于 PSR 峰值旁瓣比），把 KCF 从「矩形刚性模板」升级为「感知形状和通道质量的鲁棒跟踪器」——是 OpenCV 里传统单目标跟踪的首选精度型算法。",

    "paper_why": """KCF/DCF 类相关滤波跟踪器（2010–2015）已经非常快、也较鲁棒，但有两个根本性限制：

1. **空间假设**：它们都用矩形框循环移位训练，但**矩形框包含大量背景**（尤其目标是非刚性的，比如人走路时矩形框一半是背景），这些背景像素被错误地当成目标学习进去，导致模板漂移。
2. **通道等权**：KCF 多通道特征（如 31 维 HoG）所有通道直接相加，但有些通道在当前帧是噪声（比如模糊时高频通道没用），不应一视同仁。

CSRT（DCF-CSR）就是解决这两个问题的：
- **空间可靠性（Spatial Reliability）**：用颜色直方图前景/背景分割 + 边界先验，估计一个**二值或软掩膜**，只在掩膜区域学习 DCF
- **通道可靠性（Channel Reliability）**：根据每个通道的 PSR（Peak-to-Sidelobe Ratio）和学习曲线中的波动性，**给每个通道一个权重**，在检测响应加权求和时降权不可靠通道

CSRT 在 VOT 2016/2017 实时赛道拿了冠军。""",

    "paper_innov": """**创新 1：空间可靠性图自动估计**
用目标框内/外的颜色直方图（类似 Staple 跟踪器的颜色模型）做前/背景概率图，再结合空间先验（目标中心附近属于前景概率高），构造一个 [0,1] 的软掩膜 m[p]。滤波学习只在 m 加权区域进行。

**创新 2：掩膜约束下的 DCF 求解**
KCF 是在矩形整框上解闭式解：$\\hat{w} = \\frac{\\hat{x}^* \\odot \\hat{y}}{\\hat{x}^* \\odot \\hat{x} + \\lambda}$。CSRT 引入空间掩膜后，问题变成 $\\min_w ||m \\odot (w \\star x) - y||^2 + \\lambda||w||^2$，无法用简单的元素除法，需要用**迭代共轭梯度（CG）法**在频域求解。

**创新 3：通道可靠性权重**
对每个通道 d，计算两个质量指标：
- **PSR（Peak-to-Sidelobe Ratio）**：当前帧检测峰的尖锐度
- **平均约束满足度**：该通道在历史学习中对目标的一致性

两个指标加权得到 $w_d$，在最终响应图 $R = \\sum_d w_d R_d$ 时使用。如果某个通道突然失效（被遮挡/模糊），它的权重会在几帧内自动降到 0。

**创新 4：多特征融合**
默认用 HoG（31 维）+ Colornames（11 维）共 42 通道特征，也可以加入灰度、raw pixel。空间掩膜本身基于颜色直方图。""",

    "paper_result": """- VOT 2016 EAO：0.346（比 KCF 0.286 提升 ~20%）
- VOT 2017 实时赛道冠军
- 速度：CPU 单线程约 15–40 FPS（取决于参数），仍属实时
- 对形变、遮挡、旋转的鲁棒性显著优于 KCF/DSST/MOSSE""",

    "paper_limit": """- 迭代 CG 求解比 KCF 闭式解慢 3–5×
- 颜色直方图在目标颜色和背景相似时失效，掩膜不准
- 长时全遮挡（>10 帧）还是会丢（需要重检测模块，ATOM/DiMP 等后来做了）
- 需要 opencv-contrib，正式 OpenCV 主仓库没有""",

    "read_tip": "CVPR 2017 原文 + 作者补充材料（有 CG 求解公式）",
    "read_tip2": "Staple tracker（2016）是 CSRT 的颜色模块前作，建议一起看",

    "concepts_body": """## 1. 相关滤波回顾（DCF/KCF）

MOSSE/KCF 的核心：训练一个相关滤波器 w，让它和目标 patch 的卷积在目标中心响应 1、其他位置响应 0（高斯理想响应）。因为循环矩阵对角化，可以用 FFT 快速求解。问题是它假设**矩形 patch 全部是目标**。

## 2. 空间可靠性图 m[p]

- **颜色前/背景模型**：把目标框内像素和周围背景像素做颜色直方图，用贝叶斯公式算每个像素属于前景的概率
- **空间先验**：离框中心越近，属于前景的先验概率越高
- 两者相乘得到软掩膜 m，再用 Epanechnikov 核加权（中心权重高）

m 是一张 0–1 的图，0 表示「这像素肯定是背景，不要学」，1 表示「这像素是目标，重点学」。

## 3. 通道可靠性权重 w_d

每个特征通道（比如 HoG 的第 d 个 bin）单独算出响应图 R_d，然后加权和 $R = \\sum w_d R_d$。w_d 由两部分乘积：
- **PSR（Peak-to-Sidelobe Ratio）**：峰值 / 旁瓣均值，峰越尖锐 w 越大
- **学习稳定性**：通道历史滤波器与当前滤波器的差异，差异大说明该通道在"飘"，降权

## 4. 掩膜 DCF 的共轭梯度求解

引入掩膜 m 后损失函数的傅里叶域解不再是元素相除。作者发现每次跟踪更新只变化几帧，用**共轭梯度法**在傅里叶域做几次迭代（约 5 次）就能收敛，比直接求逆快。

## 5. 多特征（HoG + Colornames）

- **HoG**：捕捉形状/边缘，对光照鲁棒
- **Colornames**：颜色命名特征（将 RGB 映射到 11 种语义颜色），对形变鲁棒
两者互补，融合是 CSRT 精度高的一个重要原因。

## 6. 更新策略

- 检测：在新帧上以当前位置为中心取 patch，算各通道响应 → 加权 → 找峰值新位置
- 更新：每帧用学习率 η（默认 0.02）更新滤波器、颜色模型、通道可靠性统计""",

    "mermaid": """
    A[初始帧 ROI 框] --> B[提取 HoG + Colornames 多通道特征]
    B --> C[前景/背景颜色直方图<br/>估计空间可靠性掩膜 m]
    C --> D[共轭梯度法迭代求解<br/>带掩膜的 DCF 滤波器 w_d]
    D --> E[进入下一帧]
    E --> F[在预估位置取 patch<br/>多通道特征]
    F --> G[各通道做相关运算得 R_d]
    G --> H[按通道可靠性 w_d 加权<br/>得到最终响应 R]
    H --> I[亚像素峰值定位<br/>更新尺度]
    I --> J[在线更新 w_d/颜色模型/可靠性]
    J --> E
""",

    "steps_body": """### Step 1：初始化
- 第一帧用户框选 ROI
- 提取颜色前景/背景直方图（在 ROI 内/外采样）
- 提取 HoG + Colornames 特征
- 构造初始空间掩膜 m（初始时是 Epanechnikov 椭圆，然后用颜色概率调整）
- CG 法求解初始滤波器 w_d

### Step 2：跟踪（每帧）
1. **位置预测**：从上一帧位置为中心取略大的 patch
2. **特征提取**：HoG + Colornames（可加灰度）
3. **通道响应**：每个通道 d，用当前 w_d 做相关（频域相乘）得到 R_d
4. **通道可靠性估计**：算每个 R_d 的 PSR 和稳定性，得到 w_d
5. **加权求和**：R = Σ w_d R_d，找亚像素峰值位置
6. **尺度估计**（可选）：类似 DSST 的多尺度搜索
7. **模型更新**：以学习率 η 在线更新滤波器、颜色直方图、通道可靠性

### Step 3：空间掩膜更新
- 每 N 帧（默认 4）重新估计颜色直方图
- 结合当前新位置的像素更新前景/背景模型
- 重新计算 m 并 CG 迭代求解 w

### Step 4：失败检测（可选）
- 如果最终响应 R 的 PSR 低于阈值（比如 5–8），判定为"跟踪丢失"
- 可触发重检测模块""",

    "params_table": """| padding | 3.0 | 3.0 | 2–4 | 搜索区域大小相对目标的倍数，大了易漂移、小了跟不住快目标 |
| template_size | 32 | 32 | 32–64 | 模板大小（像素），越大特征越细 |
| gsl_sigma | 1.0 | 1.0 | 1.0 | 空间可靠性高斯带宽 |
| hog_orientations | 9 | 9 | 9 | HoG 方向 bin 数 |
| num_hog_channels_used | 18 | 18 | 18（取前 18 通道）| HoG 使用通道数 |
| histogram_bins | 16 | 16 | 16 | 颜色直方图 bin 数 |
| filter_lr | 0.02 | 0.02 | 0.01（稳）~0.05（快适应）| 滤波器学习率 |
| admm_iterations | 4 | 4 | 4–6 | CG/ADMM 迭代次数，越多越准越慢 |""",

    "complexity": """- 检测：C 通道 FFT + 频域相乘，O(C · K · log K)（K 是模板像素数）
- 更新：CG 迭代 ~4 次，每次 O(C · K · log K)
- 实测 CPU：640×480 上 ~25–50 FPS，略慢于 KCF（150 FPS）但明显快于深度学习跟踪器""",

    "opencv_code": """import cv2
tracker = cv2.TrackerCSRT_create()
# 调参（可选）
tracker.setParams(
    padding=3.0,
    template_size=32,
    gsl_sigma=1.0,
    filter_lr=0.02,
)
cap = cv2.VideoCapture('video.mp4')
ok, frame = cap.read()
bbox = cv2.selectROI('select', frame, False)
tracker.init(frame, bbox)

while True:
    ok, frame = cap.read()
    if not ok: break
    ok, bbox = tracker.update(frame)
    if ok:
        x,y,w,h = [int(v) for v in bbox]
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
    cv2.imshow('CSRT', frame)
    if cv2.waitKey(30) & 0xFF == 27: break
""",

    "naive_code": """import numpy as np, cv2

# 简化版 CSRT 核心思想演示：空间掩膜 + 通道加权
def cos_window(sz):
    h, w = sz
    c = np.hanning(w)[None,:] * np.hanning(h)[:,None]
    return c.astype(np.float32)

def train_dcf_with_mask(x, y, m, lam=0.01, iters=4):
    \"\"\"带掩膜 DCF 简化版（CG 迭代示意，非真正 CSRT）\"\"\"
    # x: (C,H,W) features, m: (H,W) mask, y: (H,W) label
    C, H, W = x.shape
    Xf = np.fft.fft2(x, axes=(1,2))
    Yf = np.fft.fft2(y)
    Wf = np.zeros_like(Xf)
    r = Yf - np.einsum('chw,chw->hw', np.conj(Xf), Wf) - lam*Wf[0]
    p = r.copy()
    for _ in range(iters):
        Ap = np.einsum('chw,chw->hw', np.conj(Xf), p) * Xf/Xf.shape[0] + lam*p
        alpha = np.sum(r*np.conj(r)) / (np.sum(p*np.conj(Ap)) + 1e-8)
        Wf = Wf + alpha*p
        r_new = r - alpha*Ap
        beta = np.sum(r_new*np.conj(r_new)) / (np.sum(r*np.conj(r)) + 1e-8)
        p = r_new + beta*p
        r = r_new
    return Wf
""",

    "source_insight": """OpenCV CSRT 源码在 `opencv_contrib/modules/tracking/src/trackerCSRT.cpp`：

- `TrackerCSRTImpl::initImpl()`：初始化，构造 `CSRTFilter`、`ScaleEstimator`、`Histogram`
- `TrackerCSRTImpl::updateImpl()`：每帧更新主循环
- `CSRTFilter::detect()`：在多通道特征上做相关，加权求和
- `CSRTFilter::update()`：调用 `StandardCGImpl::update()` 做共轭梯度迭代
- `SpatialMask::estimateMask()`：根据颜色直方图 + 高斯先验算空间掩膜
- `ChannelReliability::computeReliability()`：按 PSR + 学习稳定性算 w_d

OpenCV 版本比论文稍简化（比如没完全用 ADMM，用了简化 CG），但精度仍然显著高于 KCF。""",

    "painpoints_body": """### 1. 没有安装 opencv-contrib-python
`cv2.TrackerCSRT_create` 只在 contrib 里。**修法**：`pip install opencv-contrib-python`。

### 2. 速度比预期慢（<20 FPS）
原因可能是 padding 过大（默认 3.0 取了 9 倍面积）或 template_size 过大。**修法**：padding=2.0，template_size=24，速度能翻倍但精度略降。

### 3. 目标与背景颜色相似时跟踪飘
空间掩膜依赖颜色直方图区分前/背景，颜色相近时掩膜失效，退化成接近 KCF 的矩形模板。**修法**：调大 filter_lr 快速适应，或改用 DeepSORT/Transformer 跟踪器。

### 4. 长时完全遮挡后跟丢
CSRT 本身没有重检测模块，遮挡超过十几帧滤波器会被污染。**修法**：结合检测器（如 YOLO）做 tracking-by-detection，响应 PSR 低于阈值触发重检。

### 5. 第一帧 bbox 框得太大/太小
CSRT 依赖初始框内/外像素建立颜色直方图，框得不准颜色模型就错。**修法**：bbox 尽量紧贴目标，留 5–10 像素余量即可（padding 参数会扩展）。

### 6. 快速运动目标跟丢
padding=3.0 默认能覆盖单帧 ±1 倍目标尺寸的运动；更快运动需 padding=4–5，但背景干扰增大。**修法**：加大 padding 或用 Kalman 滤波做运动预测。

### 7. 多目标跟踪直接套 CSRT 会慢
CSRT 是单目标跟踪器。**修法**：多目标用 `cv2.MultiTracker_create()` 管理多个 CSRT 实例，但注意 N 个实例速度 ×1/N。

### 8. 尺度变化大时没开尺度估计
默认 scale 估计是开的，但如果显式关了（use_scale=false），大小变化大就会跟丢。""",

    "diag_mermaid": """
    A[跟丢/飘移] --> B{颜色相似?}
    B -- 是 --> C[加大 padding + filter_lr<br/>或换融合跟踪]
    B -- 否 --> D{遮挡?}
    D -- 长时 --> E[配合检测器重检]
    D -- 短时 --> F[正常（CSRT 能扛）]
    G[速度太慢] --> H[padding 降到 2.0<br/>template_size 降到 24]
    I[初始化后立即飘] --> J[初始 bbox 没框准<br/>重新选择 ROI]
""",

    "koujue": """**掩膜滤、通道权、CG 迭、学习稳**""",

    "trick_order": """1. **初始框要紧贴目标**（不要框太多背景）
2. padding=2.5–3.0（默认 3.0）作为起点
3. filter_lr=0.02 通用；快速变化场景调到 0.03–0.05
4. 开多尺度（默认开）
5. 跟踪失败检测：PSR < 7 视为丢失，触发重检""",

    "combos": """- **YOLO 检测 + CSRT 跟踪**：tracking-by-detection，检测每 N 帧做一次，中间用 CSRT 跟（工业常用）
- **CSRT + Kalman Filter**：卡尔曼滤波做运动预测，解决快速运动
- **CSRT 多实例 + MultiTracker**：多目标跟踪（10 个以内目标可实时）
- **CSRT + ReID**：长时跟踪跨遮挡重识别""",

    "checklist_pre": """装 opencv-contrib-python；初始 bbox 紧贴目标""",
    "checklist_post": """失败检测 + 周期重检""",
})

print(f"累计 {len(ALGOS)} 个算法")
