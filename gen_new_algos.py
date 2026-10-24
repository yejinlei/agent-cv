#!/usr/bin/env python3
"""新增 4 个高频算法完整 7 页：bilateral / mog2 / kcf / lbp。
沿用 SURF/ORB 档案风格——生活化比方 + Mermaid + OpenCV/手写代码 + 调参口诀。
"""
import os, sys
sys.path.insert(0, ".")

OUT_DIR = "docs/algorithms"

def build_algo(name, pages):
    """pages: dict {filename: content}"""
    d = os.path.join(OUT_DIR, name)
    os.makedirs(d, exist_ok=True)
    for fn, content in pages.items():
        path = os.path.join(d, fn)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  wrote {path}")

# ============ 1. 双边滤波 bilateral ============
def bilateral():
    idx = '''---
title: 双边滤波 Bilateral Filter (1998)
outline: deep
---

# 双边滤波 Bilateral Filter (1998)

<AlgorithmCard
  name="双边滤波"
  enName="Bilateral Filter"
  year="1998"
  chapter="第3章 · 图像预处理"
  branch="图像处理"
  level="低层"
  tagline="保边去噪的"近邻兄弟"滤镜"
  analogy="给照片磨皮：离得近的像素才影响它，而且只让颜色差不多的互相匀一匀——色斑去掉了，但眼睛、睫毛、皮肤皱纹这种边缘给你留着。"
  scene="人像美颜磨皮、HDR 色调映射的 base/detail 分解、卡通化、去噪同时保边"
  :pros='["去噪同时保留边缘（高斯做不到）", "单参数可控、无需 GPU", "基础版线性复杂度可实时"]'
  :cons='["比高斯慢一个量级", "核大了会产生伪影", "不能处理强椒盐噪声"]'
  paper="https://people.csail.mit.edu/sparis/publi/2008/fnt/Paris_08_Bilateral_Filtering.pdf"
/>

## 一句话速记

把普通高斯滤波「只看像素离得多近」升级成「**既看离得多近、又看颜色差多大**」——近+像的邻居才被加权进来，**跨边缘的像素自动被降权**，所以边缘保住了。

## 七页导航

| 页面 | 讲什么 |
| --- | --- |
| [📄 原始论文](./paper) | Tomasi & Manduchi 1998 — 原文主张与公式 |
| [💡 核心概念](./concepts) | 高斯 vs 双边：空间高斯 × 值域高斯的乘积核 |
| [🏗 算法流程](./architecture) | O(1) 双边滤波加速 / 引导滤波对比 |
| [💻 源码实现](./source) | OpenCV 调用 + 手写最小版 |
| [🔥 踩坑清单](./painpoints) | 「磨皮过头的假面感」是怎么来的 |
| [⚙ 调参口诀](./tricks) | sigmaSpace / sigmaColor 怎么选 |

## 适用场景速查

✅ 人像美颜磨皮、皮肤处理
✅ HDR Tone Mapping 中的 Base/Detail 分解（Durand 2002）
✅ 卡通/插画滤镜（edge-aware smooth）
✅ 作为深度图/光流图的后处理

❌ 强椒盐噪声（用中值先顶一下）
❌ 实时视频超大核（用导向滤波替代）
'''

    paper_md = '''# 📄 原始论文

> **Tomasi, C., & Manduchi, R. (1998).** *Bilateral filtering for gray and color images.* ICCV 1998.

## 论文一句话主张

> 「不要让空间邻近但亮度差异大的像素互相平滑，因为它们大概率在边缘两侧。」

在此之前的平滑滤波——高斯、均值、盒滤波——都**只看空间距离**，所以它们必然会把边缘模糊掉。Tomasi 提出给每个像素再加一个「值域高斯」权重：和中心像素颜色越接近，权重越大；色差越大，权重指数衰减到 0。

## 核心贡献

1. 首次把「空间邻近度」和「亮度相似度」结合成一个**非线性、保边、非迭代**的滤波器。
2. 公式优雅简单，和高斯滤波只差一个值域乘积项。
3. 直接催生了 2000 年代的 Edge-Preserving Filter 家族：**引导滤波 (He 2010)、Domain Transform (Gastal 2011)、Recursive Bilateral** 全是它的后代。

## 原始公式

$$
I^{BF}[p] = \\frac{1}{W_p}\\sum_{q\\in\\Omega} I[q]\\cdot G_{\\sigma_s}(\\|p-q\\|)\\cdot G_{\\sigma_r}(|I[p]-I[q]|)
$$

- $G_{\\sigma_s}$：空间高斯，离得越远权重越小（和普通高斯一样）
- $G_{\\sigma_r}$：值域高斯，颜色差越大权重越小（双边独有）
- $W_p$：归一化系数

## 论文遗留问题 / 后世解法

- **原版 O(r²)**：核半径 r 平方复杂度。→ Porikli 2008 O(1) 双边、Yang 2009 双边网格加速。
- **灰度偏移**：值域只看亮度，彩色图会偏色。→ 转 CIELAB 空间做双边。
- **大核慢**：→ 引导滤波 Guided Filter O(N) 完美替代。
'''

    concepts = '''# 💡 核心概念

## 为什么高斯会糊边？

普通高斯核：「**离得近就拉一把**」——边缘左边的白像素和右边的黑像素因为位置近，互相取平均，边缘就被抹成灰色了。

```mermaid
graph LR
  A[白像素] --位置近、亮度差大--> B[黑像素]
  B -.被平均成灰.-> C[边缘糊掉]
```

## 双边 = 空间高斯 × 值域高斯

```mermaid
flowchart LR
  subgraph 权重计算
    S[空间距离 ||p-q||] --> GS["G<sub>σs</sub> 空间高斯"]
    C[色差 |I[p]-I[q]|] --> GR["G<sub>σr</sub> 值域高斯"]
    GS --> W["w = Gs × Gr（乘积）"]
    GR --> W
  end
  W --> OUT["加权求和 → I'[p]"]
```

关键直觉：
- **边缘两侧**的像素空间上近，但色差大 → $G_{\\sigma_r} \\approx 0$ → 权重≈0 → 不参与平均 ✅
- **平坦区域**色差小 → $G_{\\sigma_r} \\approx 1$ → 退化成普通高斯 ✅

## 三个 σ 怎么区分

| 参数 | 控制什么 | 小值 | 大值 |
| --- | --- | --- | --- |
| `d`（核直径） | 看多大邻域 | 只磨细噪点 | 大面积色块化 |
| `sigmaColor` | 颜色相似度阈值 | 色差很小才被拉平（磨皮轻） | 差很多也拉平（磨皮重） |
| `sigmaSpace` | 空间扩散范围 | 局部影响 | 大范围融合 |

经验法则：**`sigmaColor` 和 `sigmaSpace` 一般设成一样大**（比如 75/75），视觉最舒服。

## 双边 vs 高斯 vs 中值 vs 引导

| 算子 | 保边 | 去椒盐 | 速度 | 灰度偏移 |
| --- | --- | --- | --- | --- |
| 高斯 | ❌ | ❌ | ⚡⚡⚡ | 无 |
| 中值 | 半保边 | ✅ | ⚡⚡ | 无 |
| **双边** | ✅ | ❌ | ⚡ | 轻微 |
| 引导滤波 | ✅ | ❌ | ⚡⚡⚡ | 无（O(N)） |
'''

    arch = '''# 🏗 算法流程

## 原始版双边滤波流程（逐像素）

```mermaid
flowchart TD
  S[输入图像 I] --> K[对每个像素 p]
  K --> N[取 p 周围 d×d 邻域 Ω]
  N --> C1[对每个邻居 q：算空间权重 Gσs||p-q||]
  N --> C2[对每个邻居 q：算值域权重 Gσr|Ip-Iq|]
  C1 --> W[w = Gs × Gr，累加权重总和 Wp]
  C2 --> W
  W --> S2["I'[p] = Σ I[q]·w / Wp"]
  S2 --> NEXT{还有像素?}
  NEXT --是--> K
  NEXT --否--> OUT[输出保边去噪图]
```

## O(1) 加速思路（Porikli 2008 核心 idea）

原始双边核 $G_{\\sigma_s}(\\cdot)\\cdot G_{\\sigma_r}(\\cdot)$ 是非线性的、不能分离，但可以**按亮度值分箱**，对每个箱做一次盒滤波/高斯滤波，最后插值回来——这就是"双边网格 Bilateral Grid"的核心思想，把 O(r²) 降到 O(1) 常数时间。

工程上 OpenCV 里的 `cv2.bilateralFilter` 用的就是快速近似，比手写循环快 50 倍。

## 一个典型例子：人像磨皮流水线

```mermaid
flowchart LR
  A[原图] --> B[双边滤波 大核<br/>d=15 σ=75/75]
  B --> C[Detail = 原图 - 滤波结果]
  C --> D[把 Detail 减半再叠加回去]
  D --> E[皮肤光滑 皱纹保留✅]
```

这就是"自然磨皮"——只抹平色斑低频，保留皮肤纹理高频。**直接把整张图高斯糊掉会变成假面**。
'''

    source = '''# 💻 源码实现

## ① OpenCV 一行调用

```python
import cv2
img = cv2.imread("portrait.jpg")
# d=核直径(常用 -1 自动由 sigmaSpace 算); sigmaColor=75; sigmaSpace=75
smooth = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
```

## ② 人像磨皮完整流水线

```python
import cv2, numpy as np

def beauty_face(img, d=15, sigma=75, detail_keep=0.5):
    """磨皮：强双边 + 细节回注"""
    blur = cv2.bilateralFilter(img, d=d, sigmaColor=sigma, sigmaSpace=sigma)
    detail = img.astype(np.float32) - blur.astype(np.float32)
    out = blur.astype(np.float32) + detail * detail_keep  # 保留一半高频
    return np.clip(out, 0, 255).astype(np.uint8)

img = cv2.imread("face.jpg")
res = beauty_face(img, d=21, sigma=90, detail_keep=0.4)
cv2.imwrite("face_beauty.jpg", res)
```

## ③ 手写最小版（理解原理，不用于生产）

```python
import numpy as np, cv2

def bilateral_filter_naive(img, d=5, sigma_s=10, sigma_r=30):
    h, w = img.shape[:2]
    pad = d // 2
    I = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_REFLECT).astype(np.float32)
    out = np.zeros_like(I)
    # 预计算空间高斯
    yy, xx = np.mgrid[-pad:pad+1, -pad:pad+1]
    gs = np.exp(-(xx*xx + yy*yy) / (2*sigma_s*sigma_s))
    for y in range(pad, h+pad):
        for x in range(pad, w+pad):
            patch = I[y-pad:y+pad+1, x-pad:x+pad+1]
            diff = patch - I[y, x]
            if img.ndim == 3:
                gr = np.exp(-np.sum(diff*diff, axis=2) / (2*sigma_r*sigma_r))
            else:
                gr = np.exp(-diff*diff / (2*sigma_r*sigma_r))
            w = gs * gr
            if img.ndim == 3:
                out[y, x] = np.sum(patch * w[..., None], axis=(0,1)) / np.sum(w)
            else:
                out[y, x] = np.sum(patch * w) / np.sum(w)
    return out[pad:h+pad, pad:w+pad].astype(np.uint8)
```

**注意**：这个手写版比 OpenCV 慢 1000 倍，仅供理解；生产一定要用 `cv2.bilateralFilter`。
'''

    pain = '''# 🔥 踩坑清单

## 坑 1：sigmaColor 过大 → 假面人

很多人磨皮一把梭 `sigmaColor=150`，结果皮肤和五官糊成一块。**sigmaColor 超过 100 基本就没"保边"了**，退化成类高斯的大色块。

> 🔧 修：人像 50~80，风景 30~50，想要卡通感可以到 100+。

## 坑 2：d 太大非常慢

`d=-1` 时 OpenCV 会根据 sigmaSpace 自动推导 d，sigmaSpace>100 时 d 会到 20+，性能剧降。

> 🔧 修：实时视频用 d=5~9，离线处理可以到 15。

## 坑 3：彩色图直接 BGR 上双边 → 边缘有彩边

BGR 三个通道是强相关的，每个通道独立做双边会把彩色边缘的邻域错位加权。

> 🔧 修：转 CIELAB 空间（`cv2.cvtColor(..., COLOR_BGR2LAB)`），对 L 通道做双边再转回来，色彩更稳。

## 坑 4：把双边当中值用（防椒盐）

双边对椒盐噪声完全没辙——噪点和周围色差巨大，值域权重为 0，**噪点原样保留**。

> 🔧 修：椒盐噪点先用 `cv2.medianBlur(img, 3)` 顶一下，再双边。

## 坑 5：HDR base/detail 分解 halo

用双边做 base 层时，sigma 设小了边缘周围会出光晕（halo）。

> 🔧 修：sigma_r 取到对比度的 ~20%，或者直接换成引导滤波（guided filter），halo 天生更小。
'''

    tricks = '''# ⚙ 调参口诀

## 口诀

> **d 小快、σ 配平；色空同大、CIELAB 先行；椒盐先中值、磨皮半高保。**

## 常用配方速查表

| 场景 | d | sigmaColor | sigmaSpace | 备注 |
| --- | --- | --- | --- | --- |
| 实时去噪 | 5 | 25 | 25 | 视频 30fps 可跑 |
| 人像轻磨皮 | 9 | 50 | 50 | 最常用 |
| 人像强磨皮 | 15 | 75 | 75 | 磨掉色斑 |
| 卡通化滤镜 | -1 | 150 | 150 | 大色块感 |
| HDR base 层 | -1 | 30 | 100 | 配合 detail 增强 |
| 深度图后处理 | 7 | 20 | 20 | 小核填平视差空洞 |

## 5 条黄金法则

1. **sigmaColor 与 sigmaSpace 尽量相等**：数值一起调，不要一个大一个小，会出现奇怪的方向性模糊。
2. **d 用 -1 让 OpenCV 算**：d 和 sigmaSpace 不匹配会退化。
3. **彩色图一律 LAB 空间做**：避免色边。
4. **要保留纹理就回注 detail**：`out = blur + k*(img-blur), k∈[0.2,0.6]`。
5. **追求极致速度用引导滤波**：`cv2.ximgproc.guidedFilter`，O(N)，效果几乎一样。

## 替代物的选择开关

- **要快、大核** → 引导滤波 Guided Filter
- **要结构导向** → 双边网格 / Domain Transform
- **要完全保边** → 非局部均值 NLM（`cv2.fastNlMeansDenoisingColored`）
- **要磨皮到卡通** → 双边 + 边缘检测叠加描线
'''
    return {"index.md": idx, "paper.md": paper_md, "concepts.md": concepts,
            "architecture.md": arch, "source.md": source, "painpoints.md": pain, "tricks.md": tricks}


# ============ 2. MOG2 背景减除 ============
def mog2():
    idx = '''---
title: MOG2 背景减除 (2004)
outline: deep
---

# MOG2 混合高斯背景建模 (2004)

<AlgorithmCard
  name="MOG2 背景减除"
  enName="Gaussian Mixture Background Subtraction"
  year="2004"
  chapter="第11章 · 运动分析"
  branch="几何视觉"
  level="中层"
  tagline="自动区分"背景"和"入侵者"的视频哨兵"
  analogy="保安大爷盯着小区大门：先看几天记住「平时这里应该长什么样」（背景模型），一旦有和背景不一样的东西进来，立即报警（前景）。他不指望背景永远不变——树叶晃、光线变暗他会慢慢更新记忆；但突然跑过一个人，立刻标红。"
  scene="监控里的运动目标检测、流量统计、入侵检测、自动停车杆触发、人流统计"
  :pros='["无需任何标注，开机就能跑", "自动适应光照缓慢变化", "MOG2 会自动选择高斯个数，比 MOG1 省参数", "CPU 实时，树莓派都能跑"]'
  :cons='["突然光照突变（开灯/闪电）会误检", "树叶/水面等周期运动容易长期被当背景漏检", "静态放置的物体（被扔下的包）会逐渐"融入"背景", "鬼影（ghost）: 初始帧里的东西走了，会留几秒假前景"]'
  paper="https://ieeexplore.ieee.org/document/1333992"
/>

## 一句话速记

对每个像素位置，维护**K 个高斯分布**描述「这个位置过去都出现过什么颜色」；新来的像素如果匹配不上任何一个高斯，就判为前景；匹配上的则慢慢更新高斯参数。

## 七页导航

| 页面 | 讲什么 |
| --- | --- |
| [📄 原始论文](./paper) | Zivkovic 2004 — Adaptive GMM for BGS |
| [💡 核心概念](./concepts) | 单高斯→GMM，为什么要混合？|
| [🏗 算法流程](./architecture) | 学习率、阴影检测、K 自动选择 |
| [💻 源码实现](./source) | cv2.createBackgroundSubtractorMOG2 + 形态学后处理 |
| [🔥 踩坑清单](./painpoints) | 鬼影、水波纹、开灯爆闪 |
| [⚙ 调参口诀](./tricks) | history/varThreshold/shadow 怎么调 |

## 何时别用它

❌ 相机本身在动（云台/车载）→ 整张图都是前景，用帧差+光流代替
❌ 需要精确轮廓的分割任务 → 只是运动掩码，不是语义分割
❌ 需要识别目标类别 → 后面要接分类器/YOLO
'''

    paper_md = '''# 📄 原始论文

> **Zivkovic, Z. (2004).** *Improved adaptive Gaussian mixture model for background subtraction.* ICPR 2004.

## 论文一句话主张

> 「每个像素的高斯分量个数 K 不应该是固定的（如 Stauffer-Grimson 1999 固定 K=3~5），而应该根据该像素位置的动态变化**自动选择**——变化少的地方用 1 个就够，树叶摆动、水波的地方才需要多个。」

## 相对于 Stauffer-Grimson 1999 的改进

1. **K 自适应**：自动扔掉权重低的高斯，省内存省计算。
2. **学习率 α 在线估计**：不用手调，初入场景的"鬼影"消失更快。
3. **先验置信度**：加入了 Dirichlet 先验，对高斯权重做正则，更稳。
4. 这就是 OpenCV 里 `BackgroundSubtractorMOG2` 的直接实现，工业上用了 20 年。

## 更早 / 更新的亲戚

| 方法 | 年份 | 特点 |
| --- | --- | --- |
| Running Average（帧差） | 1980s | 简单 $B = (1-\\alpha)B + \\alpha I$，单高斯 |
| Stauffer-Grimson GMM | 1999 | K=3~5 固定 |
| **Zivkovic MOG2** | 2004 | **K 自适应 + 阴影检测**，OpenCV 默认 |
| KNN 背景 | 2010s | `cv2.createBackgroundSubtractorKNN()`，非参数核密度 |
| ViBe | 2011 | 随机采样，鬼影消失极快，但 OpenCV 没有内置 |
'''

    concepts = '''# 💡 核心概念

## 帧差法为什么不够？

最朴素的「当前帧 - 上一帧 = 前景」只能看到**刚在动的东西**。停下来的人立刻消失；而且树叶一直抖，永远是前景。

## 混合高斯的思路：一个像素不是「一个背景」，而是「多种背景」

想象一个被风吹的树叶像素：**1/3 时间是树叶绿，1/3 时间是天空蓝，1/3 时间是墙皮灰**——三种颜色都"正常"，所以它的背景模型应该是**3 个高斯叠加**。

```mermaid
graph LR
  subgraph 像素值分布
    G1[高斯1: 树叶绿 μ1 σ1]
    G2[高斯2: 天空蓝 μ2 σ2]
    G3[高斯3: 墙皮灰 μ3 σ3]
    P[新像素值] --> M{离哪个高斯近?}
    M -->|2.5σ内| FG[匹配到 → 背景]
    M -->|都不沾| BG[都不沾 → 前景⚠]
  end
```

## 三个核心参数

| 参数 | 含义 | 小 | 大 |
| --- | --- | --- | --- |
| `history` | 用多少帧学背景 | 学得快、忘得快（车开过几秒就融入背景） | 学得慢但稳 |
| `varThreshold` | 多大偏差算匹配 | 严格（轻微变动都判前景） | 宽松（抖动被容忍） |
| `detectShadows` | 是否标记阴影 | — | 开后阴影用灰色 (value=127) 标记，不混进前景 |

## 学习率 α 的直觉

$$
\\mu \\leftarrow (1-\\alpha)\\mu + \\alpha x
$$

α 越大 → "忘得快"，新背景立刻记住，鬼影消失快；但缓慢停在场景里的入侵者也会被逐渐当成背景。
'''

    arch = '''# 🏗 算法流程

```mermaid
flowchart TD
  S[第 t 帧 I_t] --> INIT{已有背景模型?}
  INIT --否--> INITM[用第一帧初始化 K 个高斯]
  INIT --是--> MATCH
  INITM --> MATCH[对每个像素 x]
  MATCH --> TEST[对 K 个高斯: |I[x]-μ_k|<2.5σ_k ?]
  TEST --匹配到一个--> UPD[更新该高斯的 μ,σ,权重 w]
  TEST --一个都没匹配--> NEW[若 K<上限: 新建一个高斯<br/>否则替换权重最小的]
  UPD --> RANK[按 w/σ 从大到小排序高斯]
  NEW --> RANK
  RANK --> TH[取前 B 个: Σw > T → 这 B 个是"背景高斯"]
  TH --> JUDGE{x 落在前 B 个里?}
  JUDGE --是--> BGM[前景掩码=0 背景]
  JUDGE --否--> FGM[前景掩码=255 运动物体]
  FGM --> SH{阴影检测开?}
  SH --是且亮度低于背景--> SHD[掩码=127 阴影]
  SH --否--> END
  BGM --> END[输出 fgMask]
  SHD --> END
```

## 后处理必备 3 步（裸 MOG2 掩码噪声很大）

```mermaid
flowchart LR
  A[MOG2 原始掩码] --> B[开运算 MORPH_OPEN 3x3<br/>去椒盐噪声]
  B --> C[闭运算 MORPH_CLOSE 7x7<br/>填洞]
  C --> D[找轮廓 findContours<br/>过滤掉小于 100 像素的小块]
  D --> E[干净的运动区域框]
```

没有后处理的 MOG2 掩码基本没法用——满屏雪花。

## 阴影检测原理（MOG2 的杀手锏）

阴影不会改变颜色**色调**，只会让亮度变暗。所以 MOG2 检查「新像素是不是比背景暗了 0.5~0.8 倍，但色相差不多」——是就是阴影，标成 127 灰色而不是 255 白色。**不要把阴影当运动目标**。
'''

    source = '''# 💻 源码实现

## ① 最小可运行版（10 行就动起来）

```python
import cv2

cap = cv2.VideoCapture(0)  # 或视频文件路径
bg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=32, detectShadows=True)

while True:
    ok, frame = cap.read()
    if not ok: break
    mask = bg.apply(frame)            # 0=背景 127=阴影 255=前景
    cv2.imshow("mask", mask)
    if cv2.waitKey(30) == 27: break
cap.release(); cv2.destroyAllWindows()
```

## ② 工业版：后处理 + 画框

```python
import cv2, numpy as np

bg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=36, detectShadows=True)
cap = cv2.VideoCapture("surveillance.mp4")

while True:
    ok, frame = cap.read()
    if not ok: break

    mask = bg.apply(frame)
    # 1. 把阴影（127）先折成 0，我们只关心真正的前景
    mask[mask == 127] = 0
    # 2. 开运算去噪
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3)))
    # 3. 闭运算填洞
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7)))
    # 4. 连通域过滤小噪声
    num, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    out = frame.copy()
    for i in range(1, num):
        x, y, w, h, area = stats[i]
        if area < 200: continue
        cv2.rectangle(out, (x,y), (x+w,y+h), (0,255,0), 2)

    cv2.imshow("motion", out)
    if cv2.waitKey(30) == 27: break
cap.release(); cv2.destroyAllWindows()
```

## ③ MOG2 vs KNN 对比

```python
bg_mog2 = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=36)
bg_knn  = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400)
```
- **室内固定场景**：MOG2 更稳，误检少；
- **动态背景（树叶、喷泉、水波）**：KNN 更鲁棒，因为非参数；
- **嵌入式/低算力**：MOG2 略快。
'''

    pain = '''# 🔥 踩坑清单

## 坑 1：开头 N 帧全是白色（鬼影）

开机头几帧背景模型还没学好，第一帧里的东西如果移动了，原位置会被标记成前景"鬼影"持续 N/α 帧。

> 🔧 修：
> - 前 30~60 帧不要显示/不要触发报警，只学习；
> - 换 `BackgroundSubtractorKNN`，鬼影消失快得多；
> - 或用 `bg.apply(frame, learningRate=0.01)` 在启动阶段给个较大学习率。

## 坑 2：开灯/关灯瞬间全屏白

光照突变，每个像素都和背景差巨大，全部判前景。

> 🔧 修：
> - 这种帧直接丢：`mask.mean() > 200` 时跳过；
> - 或加 `learningRate=0.5` 让它快速适应一帧；
> - 用 HSV 的 V 通道单独做鲁棒性判断。

## 坑 3：树叶摆动/喷泉永远是前景

这是所有单像素 BGS 的通病——高频周期运动学不进去。

> 🔧 修：
> - 换 `createBackgroundSubtractorKNN` 或上 ViBe；
> - 用形态学开运算 + 大核闭运算硬填；
> - 用更大的 history（1500+），让模型有机会覆盖所有可能颜色。

## 坑 4：扔下的包慢慢消失（静态物体被"吸收"）

α 一直大于 0，静止不动的新东西时间久了会被融入背景。

> 🔧 修：
> - 做"驻留检测"：对每一个前景连通域累计生存时间，超过阈值就报警；
> - 或定期重置被遮挡区域的模型。

## 坑 5：阴影和人一起被框起来

阴影被当成前景的一部分，框会拉得很大。

> 🔧 修：
> - 一定要开 `detectShadows=True`；
> - 对 mask 做 `mask[mask==127]=0` 把阴影位清掉再找轮廓。
'''

    tricks = '''# ⚙ 调参口诀

## 口诀

> **history 随帧长，36 方差最平常；阴影开 127 标，开 3 闭 7 框不飘。**

## 参数速查表

| 场景 | history | varThreshold | detectShadows |
| --- | --- | --- | --- |
| 室内/门口短触发 | 200 | 25 | True |
| 室外慢车道/人流 | 1000 | 36 | True |
| 低光/噪点多 | 500 | 64 | False |
| 水波/树叶动态 | 2000 | 64 | True |
| 高速运动（赛车） | 100 | 16 | False |

## 5 条经验法则

1. **history = 帧率 × 你希望"多久能被学成背景"的秒数**。要让停下来的人 5 秒后报警，设成 `fps*10` 以上。
2. **varThreshold 白天 25~40，晚上/噪点 50~80**。太小全是雪花，太大漏检。
3. **阴影检测永远开着**——代价几乎为 0，收益巨大。
4. **后处理三步永远要做**：去阴影 → 开运算 → 闭运算 → 连通域过滤，少一步效果都差一大截。
5. **帧太大先降采样**：720p 降到 480p 再做 BGS，速度提升 2 倍，精度几乎不掉。

## 选型开关

- **固定相机 + 实时监控** → MOG2 默认
- **动态背景（树叶/水/雨）** → KNN / ViBe
- **运动相机/云台** → 不要用 BGS，改帧差+光流
- **需要语义（分人/车）** → BGS 只当前级候选框，后面接 YOLO/HOG+SVM
'''
    return {"index.md": idx, "paper.md": paper_md, "concepts.md": concepts,
            "architecture.md": arch, "source.md": source, "painpoints.md": pain, "tricks.md": tricks}


# ============ 3. KCF 跟踪 ============
def kcf():
    idx = '''---
title: KCF 核相关滤波跟踪 (2015)
outline: deep
---

# KCF 核相关滤波跟踪 (2015)

<AlgorithmCard
  name="KCF 跟踪"
  enName="Kernelized Correlation Filter"
  year="2015"
  chapter="第11章 · 运动分析"
  branch="目标检测"
  level="中层"
  tagline="速度快到 CPU 上能跟100个目标的"跟踪小钢炮""
  analogy="你在人群里追一个穿红衣服的朋友：不去"扫描全图找红衣人"，而是记住"他在这"的模板，下一帧拿模板在附近做"相关性匹配"——哪里最像就是他。KCF 把这个滑动匹配用循环矩阵+核技巧+FFT 加速到了几千 FPS。"
  scene="单目标跟踪（人/车/无人机/小球）、短时跟踪、ROI 跟踪辅助标注、云台自动追随"
  :pros='["CPU 实时 100~300 FPS，比 MOSSE 稳、比深度学习轻", "HOG+CN 多特征对光照/形变鲁棒", "代码量小，OpenCV 自带", "数学优雅：岭回归→循环矩阵→傅里叶对角化"]'
  :cons='["不能解决目标被遮挡（跟丢后不会重找）", "尺度变化敏感（原论文不处理尺度）", "一旦漂移很难自救", "出画面/全遮挡就永久跟丢"]'
  paper="https://arxiv.org/abs/1404.7584"
/>

## 一句话速记

跟踪 = **在线岭回归**问题。用循环移位构造"虚拟负样本"，在傅里叶域把所有循环移位一次性算出来，加核技巧做非线性边界，速度飙升。

## 七页导航

| 页面 | 讲什么 |
| --- | --- |
| [📄 原始论文](./paper) | Henriques et al. 2015 — KCF/CSK |
| [💡 核心概念](./concepts) | 岭回归 + 循环矩阵 + 核技巧 + FFT |
| [🏗 算法流程](./architecture) | 训练→检测→更新闭环 |
| [💻 源码实现](./source) | OpenCV TrackerKCF + 初始化、失败检测 |
| [🔥 踩坑清单](./painpoints) | 遮挡、漂移、尺度、出画面 |
| [⚙ 调参口诀](./tricks) | KCF vs CSRT vs MOSSE 怎么选 |

## 跟踪器家族速查

| 算法 | 年份 | 速度 | 精度 | 特点 |
| --- | --- | --- | --- | --- |
| MOSSE | 2010 | 700 FPS | 低 | 最小相关滤波器，灰度 |
| CSK | 2012 | 300 FPS | 中 | KCF 前身，加核但灰度 |
| **KCF** | **2015** | **150 FPS** | **中高** | **HOG 特征 + 高斯核** |
| DSST | 2014 | 80 FPS | 高 | KCF + 尺度估计 |
| CSRT | 2018 | 30 FPS | 高 | 通道+空间可靠性，最稳 |
'''

    paper_md = '''# 📄 原始论文

> **Henriques, J. F., Caseiro, R., Martins, P., & Batista, J. (2015).**
> *High-speed tracking with kernelized correlation filters.* IEEE TPAMI 2015.

## 论文一句话主张

> 「传统检测式跟踪（TLD、Struck）采样大量候选框是冗余的——所有候选框其实都是原始样本的循环移位。**利用循环矩阵在傅里叶域可对角化**的性质，可以把训练和检测都变成一次元素乘，速度提升几个数量级。」

## 核心贡献

1. 指出"滑动窗口的所有候选 patch"在频域里是循环矩阵，一 FFT 就全部搞定；
2. 引入核技巧（高斯核/多项式核），把线性相关滤波升级到非线性；
3. 把 CSK 的单通道灰度升级到多通道 HOG，精度显著提升同时速度不掉；
4. 开源代码后被 OpenCV 直接收录，成为默认推荐跟踪器。

## 衍生算法

- **DSST** (Danelljan 2014)：KCF + 独立的尺度滤波器，解决 KCF 不抗尺度的问题。
- **fDSST**：DSST 的快速版，用 PCA 降维特征。
- **SRDCF / CSR-DCF**：加空间正则/可靠性，抑制边缘效应。
- **CSRT / CSR-DCF**（OpenCV 4.0+ 默认推荐）：通道+空间可靠性，精度最高但慢。
'''

    concepts = '''# 💡 核心概念

## 跟踪问题可以当"在线二分类/回归"来做

- **训练**：把第一帧框内目标当正样本，周围当负样本，训练一个分类器；
- **检测**：下一帧在原位置附近滑窗，分类器响应最高的地方就是新位置；
- **更新**：在新位置采样新样本，更新分类器；
- 循环往复。

## 循环移位 —— 免费造样本

```
原始样本:  [a b c d]
右移1位:  [d a b c]
右移2位:  [c d a b]
右移3位:  [b c d a]
```

所有循环移位构成的矩阵叫**循环矩阵 C(x)**，它有一个神仙性质：

$$
C(x) = F^H \\cdot \\text{diag}(\\hat{x}) \\cdot F
$$

即：所有循环矩阵都能被**傅里叶矩阵 F 对角化**。这意味着任何涉及循环矩阵的运算（卷积、相关、岭回归解）都能在傅里叶域用**元素乘/除**代替矩阵乘法——复杂度从 O(n³) 降到 O(n log n)。

## 核相关滤波（Kernelized CF）

岭回归闭式解 $w = (X^\\top X + \\lambda I)^{-1} X^\\top y$，加核技巧映射到高维空间 $\\varphi(x)$，可以证明在傅里叶域里：

$$
\\hat{\\alpha} = \\frac{\\hat{y}}{\\hat{k}^{xx} + \\lambda}
$$

- $\\hat{y}$：期望输出（高斯峰值）
- $\\hat{k}^{xx}$：核相关（在傅里叶域）
- $\\lambda$：正则化

检测时响应图：

$$
\\hat{f}(z) = \\hat{k}^{xz} \\odot \\hat{\\alpha}
$$

峰值位置就是新目标位置。**全是 FFT + 元素乘**，CPU 飞一样。

## HOG 特征为什么比灰度好？

灰度对光照太敏感，31 维 HOG（每 cell 9 个 bin，4 个归一化方向）能编码边缘结构，对轻微变形/光照变化鲁棒。KCF 用 HOG 版本通常叫 KCF_HOG，比灰度 CSK 精度高 30% 以上。
'''

    arch = '''# 🏗 算法流程

```mermaid
flowchart TD
  INIT[第1帧: 用户框选 ROI] --> F1[提取 HOG 特征 x]
  F1 --> Y[构造标签 y: 中心1边缘0的高斯图]
  Y --> TRAIN["岭回归训练: α = F⁻¹(ŷ / (k̂ˣˣ + λ))"]
  TRAIN --> LOOP[下一帧图像 z]

  LOOP --> F2[在预测位置周围提取搜索窗的 HOG 特征 z]
  F2 --> DET["计算响应图 f(z) = F⁻¹(k̂ˣᶻ ⊙ α̂)"]
  DET --> PEAK[找响应图峰值位置]
  PEAK --> PSR{PSR 峰值旁瓣比 > 阈值?}
  PSR --否--> LOST[判定为跟丢，停止更新]
  PSR --是--> UPD[以新位置提取 x_new，更新 α 和 x]
  UPD --> LOOP
```

## 关键术语解释

- **PSR（Peak-to-Sidelobe Ratio）**：响应峰值减去旁瓣均值再除以旁瓣标准差。PSR>10 高置信度，<5 基本跟丢。用来判断要不要更新模型，**防漂移关键指标**。
- **搜索窗**：通常是目标大小的 2.5 倍，上下左右都给点冗余，让 KCF 在这个窗口里找。
- **学习率 interp_factor**：`new_template = (1-η)*old + η*new`，η 越大模型跟目标变化快，但越容易漂移。

## 为什么不抗尺度？

原始 KCF 的检测窗口大小是固定的。目标走近/走远，HOG cell 尺寸不变，响应峰值就会下降甚至漂移。DSST 单独训一个一维的"尺度相关滤波器"——在新位置切 33 个不同尺度，挑响应最高的——但 OpenCV 的 KCF 没内置这个。
'''

    source = '''# 💻 源码实现

## ① OpenCV 一行调用（最简单）

```python
import cv2

cap = cv2.VideoCapture(0)
ok, frame = cap.read()
bbox = cv2.selectROI("select", frame, False)  # 手动框选

tracker = cv2.TrackerKCF_create()
tracker.init(frame, bbox)

while True:
    ok, frame = cap.read()
    if not ok: break
    ok, bbox = tracker.update(frame)
    if ok:
        x, y, w, h = [int(v) for v in bbox]
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
    else:
        cv2.putText(frame, "LOST", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    cv2.imshow("KCF", frame)
    if cv2.waitKey(30) == 27: break
cap.release(); cv2.destroyAllWindows()
```

## ② 带 PSR 跟丢检测的工业版

```python
import cv2, numpy as np

class KCFTracker:
    def __init__(self):
        self.tracker = cv2.TrackerKCF_create()
        self.lost_frames = 0
        self.max_lost = 20  # 连丢 20 帧就放弃

    def init(self, frame, bbox):
        self.tracker.init(frame, bbox)
        self.bbox = bbox

    def update(self, frame):
        ok, bbox = self.tracker.update(frame)
        if ok:
            self.lost_frames = 0
            self.bbox = bbox
            return True, bbox
        else:
            self.lost_frames += 1
            if self.lost_frames > self.max_lost:
                return False, None  # 真丢了，建议重新检测
            return True, self.bbox  # 暂用旧位置
```

## ③ 多目标跟踪的朴素扩展

```python
trackers = []
# 每检测到一个新目标，就 new 一个 TrackerKCF 并 init
# 每帧 update 所有 tracker，超过 N 帧失败就销毁
# 每隔几秒重跑一次检测器把新目标加进来——这就是 SORT/DeepSORT 的雏形
```

## ④ KCF vs CSRT vs MOSSE 切换

```python
tracker_mosse = cv2.legacy.TrackerMOSSE_create()   # 700 FPS，最快但飘
tracker_kcf   = cv2.TrackerKCF_create()           # 150 FPS，性价比
tracker_csrt  = cv2.TrackerCSRT_create()          # 30 FPS，最稳
```
'''

    pain = '''# 🔥 踩坑清单

## 坑 1：目标被挡了一下，跟到别人身上（漂移）

KCF 的在线更新是"新位置一定是正样本"——一旦误跟到干扰物，模型会逐渐把干扰物学进去，**正反馈漂移**。

> 🔧 修：
> - 一定要做 PSR 跟丢检测，PSR<6 就**停止更新**（但仍用上一次的位置预测）；
> - 降低学习率 `interp_factor`（默认 0.02，可以降到 0.005）；
> - 遮挡超过 30 帧就放弃，重跑检测器。

## 坑 2：目标越走越近，框越跟越小（尺度问题）

KCF 原算法无尺度估计。

> 🔧 修：
> - 简单场景用 CSRT 代替；
> - 或者自己做尺度金字塔：在新位置抽 3~5 个 scale（0.85/0.95/1.0/1.05/1.15），分别算响应，取最大的；
> - 用 `cv2.TrackerKCF_create()` 不支持，但 dlib 里的 `correlation_tracker` 内置了尺度。

## 坑 3：目标出画面又回来，再也认不回来

KCF 没有重检测模块，出画面就永久丢。

> 🔧 修：
> - 配合一个检测器（YOLO/HOG+SVM）做"TLD 式"：跟踪+检测并行，检测到高置信目标时重初始化跟踪器；
> - 这就是 SORT/DeepSORT 做的事。

## 坑 4：第一帧框得不准，后面永远跟不准

KCF 的"初始模板"就是第一帧框出来的 patch，框歪了模板就歪。

> 🔧 修：
> - 用检测器的 bbox 而不是手工框；
> - 初始化后给它 5~10 帧"预热"时间再正式使用。

## 坑 5：快速运动 + 低帧率（如手机视频 15fps）跟丢

因为 KCF 只在搜索窗（目标 2.5 倍大小）内找，目标一帧飞出搜索窗就完了。

> 🔧 修：
> - 扩大 padding（OpenCV 里可以设 `detect_thresh` / `padding`）；
> - 或换成 CSRT 处理大位移；
> - 提高帧率是根本。
'''

    tricks = '''# ⚙ 调参口诀

## 口诀

> **KCF 快 CSRT 稳，MOSSE 跑上无人机；PSR 小于六别更新，学习率小不漂移。**

## 选型开关

| 场景 | 推荐跟踪器 |
| --- | --- |
| 嵌入式/无人机/极高速 | MOSSE |
| CPU 实时单目标平衡 | **KCF** |
| 尺度变化/旋转/最稳精度 | CSRT |
| 有 GPU / 多人脸/长时 | MedianFlow + YOLO 重检测 |
| 多目标且要 ID 保持 | DeepSORT（KCF/卡尔曼+ReID）|

## KCF 的关键参数（OpenCV）

| 参数 | 默认 | 建议 | 说明 |
| --- | --- | --- | --- |
| `sigma` | 0.2 | 0.2~0.5 | 高斯核带宽，越大容忍形变越多 |
| `lambda` | 0.0001 | 1e-4 | 正则项，越大越保守 |
| `interp_factor` | 0.02 | 0.005~0.02 | 学习率，越大跟得快但易飘 |
| `resize` | True | True | 是否缩小到固定大小加速 |
| `detect_threshold` | 0.5 | 0.4~0.6 | 响应峰值阈值 |

## 5 条黄金法则

1. **永远做 PSR 跟丢判断**，不要盲目 update。
2. **第一帧框要严**——宁可框紧一点，不要带太多背景。
3. **学习率不要大于 0.02**，否则漂移是早晚的事。
4. **遮挡期停止更新**，比加复杂特征管用。
5. **KCF 是短时跟踪器**，长时间跑必须配检测器。
'''
    return {"index.md": idx, "paper.md": paper_md, "concepts.md": concepts,
            "architecture.md": arch, "source.md": source, "painpoints.md": pain, "tricks.md": tricks}


# ============ 4. LBP 纹理 ============
def lbp():
    idx = '''---
title: LBP 局部二值模式 (1996)
outline: deep
---

# LBP 局部二值模式 Local Binary Pattern (1996)

<AlgorithmCard
  name="LBP 局部二值模式"
  enName="Local Binary Pattern"
  year="1996"
  chapter="第7章 · 纹理分析"
  branch="图像处理"
  level="中层"
  tagline="30 年前就跑在诺基亚手机上的"人脸识别纹理特征""
  analogy="你和朋友约着在咖啡馆见面，他说"我穿格子衬衫、戴黑框眼镜、留寸头"——这三个都是**局部对比**（头发比额头深、镜框比皮肤深、格子是明暗交替），不管他走到明处暗处、远看近看，这些"谁比谁亮"的关系都不变。LBP 就是给每个像素问一圈邻居"你比我亮还是暗"，串成一个 8 位二进制数，整张图就变成一张「纹理身份证」。"
  scene="人脸识别（经典 LBP+SVM）、纹理分类、工业缺陷检测、纸张/织物/木材分级、医学影像病灶识别"
  :pros='["对光照单调变化几乎免疫（只比较相对亮度）", "计算极快（每个像素就是8次比较，纯整数运算）", "小样本就够（比 HOG 需要的数据少）", "特征维度可控制（59 维 uniform LBP 是工业标准）"]'
  :cons='["对方向敏感（图歪了直方图就变）", "大尺度纹理要多分辨率扩展", "对噪声敏感（一个噪点翻转一个bit）", "被深度网络全面超越（但在嵌入式/小样本里仍有市场）"]'
  paper="https://ieeexplore.ieee.org/document/5763036"
/>

## 一句话速记

每个像素拿周围 8 个邻居比一下——比我亮记 1，比我暗记 0——拼成一个 8-bit 数（0~255），这就是该像素的 LBP 编码；把图像分 cell，统计每个 cell 的 LBP 直方图，拼起来就是纹理描述子。

## 七页导航

| 页面 | 讲什么 |
| --- | --- |
| [📄 原始论文](./paper) | Ojala et al. 1996 — 多分辨率 LBP |
| [💡 核心概念](./concepts) | 编码规则、旋转不变、Uniform 模式 |
| [🏗 算法流程](./architecture) | 圆形邻域 + 多尺度 + 块直方图 |
| [💻 源码实现](./source) | skimage LBP + 人脸分类 pipeline |
| [🔥 踩坑清单](./painpoints) | 噪声、分块、归一化 |
| [⚙ 调参口诀](./tricks) | P/R 怎么选、59 维为什么是魔法数 |

## LBP vs HOG vs SIFT 一句话区分

| 特征 | 编码什么 | 光照鲁棒 | 速度 | 经典用途 |
| --- | --- | --- | --- | --- |
| LBP | **纹理/局部对比** | ★★★ 单调不变性 | ⚡⚡⚡ | 人脸、纹理分类 |
| HOG | **边缘方向** | ★★ | ⚡⚡ | 行人、目标检测 |
| SIFT | **关键点+方向直方图** | ★★★（含归一化） | ⚡ | 图像匹配 |
'''

    paper_md = '''# 📄 原始论文

> **Ojala, T., Pietikäinen, M., & Harwood, D. (1996).**
> *A comparative study of texture measures with classification based on featured distributions.* Pattern Recognition 1996.
>
> 扩展版：Ojala et al. (2002) *Multiresolution gray-scale and rotation invariant texture classification with local binary patterns.* IEEE TPAMI.

## 论文一句话主张

> 「纹理分类不需要复杂滤波器组——只需要统计**局部二值模式**的出现频率，就能超过当时所有主流纹理特征（Gabor、MRF 等），而且快上百倍。」

## 历史地位

- 1996 原始 LBP（3×3 正方形邻域，256 维）。
- 2002 提出**圆形邻域（P,R）**、**旋转不变 LBP**、**Uniform LBP（59 维）**，成为工业标准。
- 2004 Ahonen 将 LBP 用到人脸识别（LBP Face），**在 FERET 人脸库上刷到 SOTA**，推动了整个"局部特征→人脸识别"方向。
- 2010 年代虽然被深度学习超过，但在**嵌入式设备、工业质检、小样本**场景仍被广泛使用。

## 衍生家族

| 变种 | 干什么 |
| --- | --- |
| 原始 LBP(8,1) | 3×3 8 邻居，256 维 |
| **LBP(P,R)** | 圆形邻域，P 点半径 R |
| **Uniform LBP_u2** | 只保留跳变≤2次的模式，58+1=59 维 |
| **Rotation Invariant LBP_ri** | 循环移位取最小值，36 维 |
| MB-LBP | 基于区域均值而不是单点，更抗噪 |
| LBP-TOP | 三正交平面，视频里的动态纹理 |
'''

    concepts = '''# 💡 核心概念

## 基础 LBP 编码

对每个像素 g_c，和 8 个邻居 g_0..g_7 比大小：

$$
\\text{LBP} = \\sum_{p=0}^{7} s(g_p - g_c) \\cdot 2^p,\\quad s(x)=\\begin{cases}1 & x\\geq 0\\\\0 & x<0\\end{cases}
$$

```mermaid
graph LR
  subgraph 3x3 邻域
    A["6"] --">=7→1"--> C["7<br/>中心"]
    B["9"] --> C
    D["5"] --> C
    E["3"] --"<7→0"--> C
    F["8"] --> C
    G["4"] --> C
    H["7"] --> C
    I["6"] --> C
  end
  C --> CODE[二进制 11010001 = 0xD1]
```

这个数天然对**光照单调变换**（如整张图 +20、×1.5）免疫——因为邻居之间的大小关系不变。这是 LBP 最核心的魅力。

## Uniform LBP（59 维魔法数）

256 种 8-bit 模式里，大部分模式都很少见。统计发现：**从 0 到 1 的「跳变」次数 ≤ 2** 的模式只有 58 种（比如 00000000、11111111、00001111、11000000……），它们覆盖了自然图像 90% 以上的 LBP 编码。剩下 198 种全部归到一个"非均匀"桶里，**总共 59 维**。

这就是著名的 `n_bins=59` 的来源。59 维直方图比 256 维小 4 倍，抗噪性还更好。

## 旋转不变 LBP

同一个纹理转个角度，LBP 会变成循环移位后的另一个数（如 11000000 → 01100000 → 00110000…）。**取这 8 个循环移位里的最小值**作为编码，就得到旋转不变版本——36 个 unique 值。但人脸识别里通常不用旋转不变，因为人脸本来就是正的。
'''

    arch = '''# 🏗 算法流程

```mermaid
flowchart TD
  S[输入灰度图] --> PRE{彩色?}
  PRE --是--> GRAY[转灰度 + 可选直方图均衡]
  PRE --否--> CIRC
  GRAY --> CIRC["对每个像素取圆形邻域 (P=8,R=1)<br/>双线性插值得 P 个邻居"]
  CIRC --> BIN[邻居-中心阈值 → P 位二进制]
  BIN --> DEC[映射为 0~P²-1 的十进制码]
  DEC --> UNI{Uniform 模式?}
  UNI --跳变≤2--> BINID[映射到 0~57]
  UNI --否--> BIN58[归到 58 号"非均匀"桶]
  BINID --> CELL[图像切成 K×K 个 cell]
  BIN58 --> CELL
  CELL --> HIS[每个 cell 统计 59 维 LBP 直方图]
  HIS --> NORM[L2/Hellinger 归一化]
  NORM --> CONCAT[所有 cell 直方图拼起来]
  CONCAT --> FEAT[输出全局纹理特征向量]
```

## LBP 人脸识别的经典设置

- 图像对齐 + 裁剪到 128×128
- 分成 **8×8 = 64 个 cell**（每 cell 16×16 像素）
- 每个 cell 59 维 Uniform LBP 直方图
- 总特征维度 = 64 × 59 = **3776 维**
- 卡方距离 / 直方图交做匹配，或送 SVM 训练多类分类器

这就是 2004 年 Ahonen LBP-Face 在 FERET 库上刷 SOTA 的完整配置。诺基亚 N95 的人脸识别用的就是它——在 ARM9 上 200ms 跑一帧。

## 多尺度 LBP

为了捕捉不同尺度的纹理，通常同时算 (P=8,R=1)、(P=16,R=2)、(P=24,R=3) 三个尺度，把它们的直方图拼起来。这样细纹理、中纹理、粗纹理都覆盖到。
'''

    source = '''# 💻 源码实现

## ① skimage 一行算 LBP 图

```python
import cv2, numpy as np
from skimage.feature import local_binary_pattern

img = cv2.imread("face.jpg", 0)
radius = 1
n_points = 8 * radius
lbp = local_binary_pattern(img, n_points, radius, method="uniform")
# lbp 的值是 0~58（59 个 uniform 类）
```

## ② 完整 LBP 人脸识别 pipeline

```python
import cv2, numpy as np
from skimage.feature import local_binary_pattern
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def lbp_histogram(img, cell_size=(16,16), n_points=8, radius=1):
    lbp = local_binary_pattern(img, n_points, radius, method="uniform")
    h, w = img.shape
    ch, cw = cell_size
    cells_y, cells_x = h//ch, w//cw
    feats = []
    for i in range(cells_y):
        for j in range(cells_x):
            cell = lbp[i*ch:(i+1)*ch, j*cw:(j+1)*cw]
            hist, _ = np.histogram(cell.ravel(), bins=59, range=(0,59))
            hist = hist.astype(np.float32)
            hist /= (hist.sum() + 1e-6)
            feats.append(hist)
    return np.concatenate(feats)

# 假设 X: list of gray images (128x128), y: labels
X = np.array([lbp_histogram(img) for img in faces_gray])
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2)
clf = LinearSVC(C=1.0)
clf.fit(Xtr, ytr)
print("acc:", accuracy_score(yte, clf.predict(Xte)))
```

## ③ 工业缺陷检测（对比法）

```python
def defect_score(test_img, ref_texture_hist):
    """测试图和参考纹理的 LBP 直方图卡方距离，越大越可能缺陷"""
    h = lbp_histogram(test_img)
    return 0.5 * np.sum((h - ref_texture_hist)**2 / (h + ref_texture_hist + 1e-6))
```

## ④ 手写 LBP 编码（理解原理）

```python
def naive_lbp(img):
    h, w = img.shape
    out = np.zeros((h-2, w-2), dtype=np.uint8)
    for i in range(1, h-1):
        for j in range(1, w-1):
            c = img[i, j]
            code = 0
            code |= (img[i-1,j-1] >= c) << 7
            code |= (img[i-1,j  ] >= c) << 6
            code |= (img[i-1,j+1] >= c) << 5
            code |= (img[i  ,j+1] >= c) << 4
            code |= (img[i+1,j+1] >= c) << 3
            code |= (img[i+1,j  ] >= c) << 2
            code |= (img[i+1,j-1] >= c) << 1
            code |= (img[i  ,j-1] >= c) << 0
            out[i-1, j-1] = code
    return out
```
'''

    pain = '''# 🔥 踩坑清单

## 坑 1：LBP 图一塌糊涂——忘了转灰度

彩色图直接进 LBP 是无意义的（而且很多库直接报错）。

> 🔧 修：必须 `cv2.cvtColor(img, COLOR_BGR2GRAY)`。

## 坑 2：光照不均 → 直方图分布塌缩

半边暗半边亮时，亮部全是 0/255，暗部噪声翻转 bit。

> 🔧 修：先做 CLAHE 直方图均衡 `cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)`。

## 坑 3：没归一化，直方图大小不一致

face 大小不一样直接拼直方图会导致距离不可比。

> 🔧 修：所有训练图先对齐+裁剪到固定大小（如 128×128）；每个 cell 直方图都 L1/L2 归一化。

## 坑 4：噪声导致 bit 翻转，特征全乱

单像素噪声翻转一个 bit，在 8 个 bit 里占 1/8，影响巨大。

> 🔧 修：
> - 先做一次小核高斯（`sigma=0.8`）；
> - 用 MB-LBP（区域均值对比）而不是单点对比；
> - 用 Uniform LBP（把大部分跳变多的"噪声模式"都归到一起了）。

## 坑 5：人脸对不齐，准确率掉成渣

LBP 对位置敏感——鼻子的 cell 和眼睛的 cell 不是一个分布。

> 🔧 修：必须先用 Haar/LBF 人脸关键点对齐，再裁到标准框（两眼距离 40 像素、眼在固定行）。
'''

    tricks = '''# ⚙ 调参口诀

## 口诀

> **R1P8 小纹理，R2P16 看大形；59 维 uniform，卡方比距离；先均衡、再分块、归一化莫忘记。**

## 常用参数

| 场景 | P（点数） | R（半径） | cell 大小 | bins |
| --- | --- | --- | --- | --- |
| 人脸精细 | 8 | 1 | 16×16 | 59 |
| 纹理分类 | 8+16+24 | 1+2+3 | 多尺度拼接 | 59×3 |
| 缺陷检测 | 8 | 1 | 8×8 | 256（不用 uniform，让异常模式可见）|
| 大像素低分辨率 | 8 | 2 | 32×32 | 59 |

## 59 个 uniform 模式为什么是 58+1？

- 全 0 模式 1 个（00000000）
- 全 1 模式 1 个（11111111）
- 有 1 个 1 的模式：8 个（1 在哪一位）×2（1 是一段/0 是一段）= 8×2=16
- 有 2 个连续 1 的模式：8×2=16
- …直到 7 个连续 1：8×2=16
- 实际：8 个位置，1~7 个连续 1，每个可以从"亮"开始或"暗"开始 → 8×7=56
- 合计 1+1+56 = **58** 个 uniform，剩下 198 个归为第 59 类"非均匀"。

## 5 条黄金法则

1. **人脸识别 P=8,R=1 就够**，多尺度对人脸提升有限。
2. **CLAHE 一定要放在 LBP 前**，不然光照一塌糊涂。
3. **直方图用卡方距离或 Hellinger 距离**，不要用欧氏距离（直方图不在线性空间）。
4. **训练样本至少对齐到两眼水平**，否则维度再好都没用。
5. **做缺陷检测时别用 uniform**——缺陷就是非均匀模式，你把它合并掉就看不见了。
'''
    return {"index.md": idx, "paper.md": paper_md, "concepts.md": concepts,
            "architecture.md": arch, "source.md": source, "painpoints.md": pain, "tricks.md": tricks}


if __name__ == "__main__":
    os.chdir("/home/user/workspace/7648064683708846935/agent-cv")
    for name, fn in [("bilateral", bilateral), ("mog2", mog2), ("kcf", kcf), ("lbp", lbp)]:
        print(f"=== Building {name} ===")
        build_algo(name, fn())
    print("\\nAll 4 new algorithms written.")
