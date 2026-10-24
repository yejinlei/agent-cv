#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 17 个算法补充 concepts/architecture/source/painpoints/tricks 五个页面"""
import os
from pathlib import Path

ROOT = Path("/home/user/workspace/7648064683708846935/agent-cv/docs/algorithms")

# 由于每个算法的 concepts/source 等差异极大，我直接为每个算法写详细内容字典
# 格式：CONTENT[key] = { "concepts": "...", "architecture": "...", "source": "...", "painpoints": "...", "tricks": "..." }
# 全部以完整 markdown 正文（不含最顶部重复标题，直接从 ## 标题开始，但需要带顶部 card）

# ========== 工具函数 ==========
def card_for(key, name, en, branch, year, author, chapter="ch-8-local-feature", level="mid",
             paper="—", tagline="", analogy="", scene="", pros=None, cons=None):
    pros = pros or []
    cons = cons or []
    pros_str = str(pros).replace("'", '"')
    cons_str = str(cons).replace("'", '"')
    return (f'''<AlgorithmCard
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
/>''')

# 简单写：统一用「标题 + 核心段落 + mermaid + 代码 + 坑表 + 口诀表」的模式，
# 每个算法给出定制化的内容文本。我分 17 块写。

CONTENT = {}

# ============================ FAST ============================
CONTENT["fast"] = dict(
    card=dict(name="FAST 角点检测", en="Features from Accelerated Segment Test", branch="feature-detection",
              year="2006", author="Edward Rosten / Tom Drummond", chapter="ch-8-local-feature", level="mid",
              tagline="用一个圆圈 16 个邻居，一眼认出角点，速度比 Harris 快 10 倍",
              analogy="FAST 像一个哨兵：不进屋检查，只趴在窗户上数——窗外 16 个邻居里如果连续 12 个都比屋里亮或都比屋里暗，那这间房肯定是个「犄角旮旯」",
              scene="SLAM、AR、实时物体识别里做特征点检测，毫秒级返回几千个点，CPU 上就能跑 60fps",
              pros=["速度极快（比 Harris 快 10 倍以上）","实现简单","角点重复率高","OpenCV 高度优化"],
              cons=["不具备尺度不变性","不具备旋转不变性","阈值敏感","需要 NMS","不含描述子"]),
    concepts_md=r'''
## 核心概念 1：角点的「圆周判据」

FAST 的核心洞察非常简单：

> **如果一个像素周围一圈（半径 3，16 个像素）中，存在连续 N 个像素都比它亮（或暗）超过阈值 t，那它就是角点。**

```mermaid
flowchart LR
  P["中心像素 p"] --> C["半径 3 的圆<br/>16 个邻居"]
  C --> D{"是否有连续 12 个<br/>都比 p+t 亮<br/>或都比 p-t 暗?"}
  D -->|"是"| E["✅ 是角点"]
  D -->|"否"| F["❌ 不是角点"]
```

**生活比方**：你站在圆圈中心看周围 16 个人。如果连续 12 个人都穿黑衣服，或者连续 12 个都穿白衣服，那说明你站在"一块颜色突变的边界点"上——就是角点。

**为什么 N=12**：经验值，也叫 FAST-12；也有 FAST-9（9/16 连续，更灵敏）和 FAST-5（5/8 连续，更快）。

## 核心概念 2：两步加速——先筛 4 点再扫 16 点

如果逐个像素老老实实检查 16 个邻居，还是不够快。FAST 用一个**闪电式初筛**：

```mermaid
flowchart TB
  A["① 先查对称 4 点<br/>上下左右 1/5/9/13"] --> B{"至少 3 个<br/>满足亮/暗条件?"}
  B -->|"否"| C["❌ 直接淘汰<br/>（约 90% 像素在此结束）"]
  B -->|"是"| D["② 再完整检查 16 个点"]
```

**这步初筛能过滤掉 90% 以上的非角点**，是 FAST 飞快的关键——它和 Viola-Jones 级联的思想一脉相承：**先用极便宜的特征快速排除大多数负样本**。

## 核心概念 3：ID3 决策树——把判断压缩到平均 2.7 次比较

Rosten 的关键创新：**用 ID3 决策树自动学习出一个最优的像素检查顺序**。

- 在训练集（~10000 张标注过的角点/非角点 patch）上跑 ID3
- 决策树的每个节点是"检查某个邻居像素比中心亮/暗/相似"
- 叶子节点给出"是/否角点"的判断

结果：判断一个像素是否是角点，**平均只需 ~3 次比较**——这比硬编码顺序快得多。

## 核心概念 4：非极大值抑制（NMS）——角点扎堆怎么办

FAST 在一个真正的角点周围，往往会检测出好几个相邻点（因为它们的邻域都满足条件）。

**解决**：对每个角点算一个**响应分数**（比如最大的连续像素和中心的差值和 V=sum|I(p)-I(x)|），然后在 3×3 邻域内只保留分数最大的那个。

```mermaid
flowchart LR
  A["检测到一堆相邻候选点"] --> B["每个点算响应分数 V"]
  B --> C["3×3 NMS"]
  C --> D["只保留分数最大的那个"]
```

## 核心概念 5：FAST 的天然缺陷

| 缺失的能力 | 说明 | 如何补 |
|---|---|---|
| **方向** | 不知道角点的朝向，无法应对旋转 | ORB 用灰度质心法 |
| **尺度** | 只有一个检测窗口，不抗缩放 | 多尺度金字塔 |
| **描述子** | 只告诉你"这里是角点"，没说"长什么样" | 配 BRIEF/ORB 描述子 |

## 相关链接

- [FAST 论文故事](/algorithms/fast/paper)
- [角点检测分支](/branches/feature-detection/corners)
- [ORB 完整档案（FAST+BRIEF 升级版）](/algorithms/orb/)
''',
    architecture_md=r'''
## FAST 算法完整流程

```mermaid
flowchart TB
  A["输入灰度图"] --> B["遍历每个像素 p<br/>（跳过边界 3 像素）"]
  B --> C["① 初筛<br/>检查圆周 1/5/9/13 四个点"]
  C --> D{"至少 3 个满足<br/>|I(x)-I(p)|>t?"}
  D -->|"否"| Z["跳过"]
  D -->|"是"| E["② 完整圆周检查<br/>判断是否有连续 12 个亮/暗"]
  E --> F{"满足连续 N?"}
  F -->|"否"| Z
  F -->|"是"| G["③ 记录为候选角点<br/>响应 V = sum \|I(x)-I(p)\|"]
  G --> H["④ 3×3 非极大值抑制"]
  H --> I["输出最终角点坐标+响应"]
```

## 步骤详解

### 步骤 0：选择 FAST 变种

| 变种 | 连续点数 | 圆周点数 | 特点 |
|---|---|---|---|
| FAST-5-8 | 5 | 8 | 最快，误检多 |
| FAST-7-12 | 7 | 12 | 折中 |
| **FAST-9-16** | **9** | **16** | **OpenCV 默认，推荐** |
| FAST-12-16 | 12 | 16 | 最严格，漏检多 |

### 步骤 1：四像素初筛

对于候选中心 p，先只检查圆周上**上下左右四个对称点**：
- 位置：p 坐标 (x,y) → (x-3,y)、(x+3,y)、(x,y-3)、(x,y+3)
- 如果这 4 个点中**至少 3 个**都比 I(p)+t 亮，或都比 I(p)-t 暗，才值得继续查 16 点
- 否则直接淘汰

### 步骤 2：完整 16 点检查

顺时针编号 1–16（从 (x+3,y) 开始）。判断是否存在长度 ≥ N 的连续弧段，满足所有像素亮度都 > I(p)+t 或都 < I(p)-t。

**高效实现小技巧**：不必真的遍历所有可能起始位置。只要看到连续 N 个就可以停。

### 步骤 3：非极大值抑制

- 对每个候选角点算响应分数：$V = \max\left(\sum_{x\in S_{bright}} |I(x)-I(p)| - t, \sum_{x\in S_{dark}} |I(p)-I(x)| - t\right)$
- 在 3×3 邻域内，只保留 V 最大的候选
- 这一步去掉"一个真角点周围检测出 7、8 个假角点"的问题

### 步骤 4：（可选）网格均匀化

FAST 检测出的点容易扎堆在纹理丰富区域。工程上常做：

```mermaid
flowchart LR
  A["原始 FAST 角点"] --> B["把图像分成 10×10 网格"]
  B --> C["每格保留响应前 N 个"]
  C --> D["全图分布均匀的角点"]
```

## 复杂度分析

| 环节 | 复杂度（每像素） |
|---|---|
| 初筛 | O(1)——4 次比较 |
| 完整检查（通过初筛的 ~10%） | O(16)，平均 ~2.7 次（决策树） |
| 总体 | **接近 O(1)** |

所以整张图的时间复杂度是 **O(W×H)**，与图像大小线性关系。

## 与其他角点检测的关系

```mermaid
flowchart LR
  FAST -->|"加方向（灰度质心）+多尺度"| oFAST
  BRIEF -->|"加方向旋转"| rBRIEF
  oFAST --> ORB
  rBRIEF --> ORB
  FAST --> AGAST["AGAST（自适应决策树）"]
```

- **FAST 本身只是检测器**，不产描述子
- **ORB = oFAST（带方向的 FAST） + rBRIEF（旋转 BRIEF）**
- **AGAST** 是 FAST 的加速版，自适应决策树，再快 ~30%

## 相关链接

- [FAST 核心概念](/algorithms/fast/concepts)
- [FAST 源码实现](/algorithms/fast/source)
- [ORB 完整档案](/algorithms/orb/)
''',
    source_md=r'''
## OpenCV 调用

### 基本调用

```python
import cv2

img = cv2.imread("test.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 创建 FAST 检测器
fast = cv2.FastFeatureDetector_create(
    threshold=20,                  # 亮度差阈值（越大点越少、越严格）
    nonmaxSuppression=True,        # 开 NMS（强烈建议 True）
    type=cv2.FAST_FEATURE_DETECTOR_TYPE_9_16  # FAST-9-16（默认）
)

# 检测
kp = fast.detect(gray, None)
print(f"检测到 {len(kp)} 个角点")

# 可视化
out = cv2.drawKeypoints(img, kp, None, color=(0, 0, 255))
cv2.imshow("FAST", out)
cv2.waitKey(0)
```

### 参数表

| 参数 | 含义 | 建议值 |
|---|---|---|
| `threshold` | 中心与邻居的亮度差阈值 | **10–30**；↓点多（有噪声），↑点少（漏检） |
| `nonmaxSuppression` | 非极大值抑制 | **True**（False 会出一堆扎堆点） |
| `type` | FAST 变种 | `TYPE_9_16`（推荐）、`TYPE_7_12`、`TYPE_5_8` |

### 常用变种枚举

```python
cv2.FAST_FEATURE_DETECTOR_TYPE_5_8     # FAST-5-8（最快）
cv2.FAST_FEATURE_DETECTOR_TYPE_7_12    # FAST-7-12
cv2.FAST_FEATURE_DETECTOR_TYPE_9_16    # FAST-9-16（默认推荐）
```

## NumPy 手写最小实现（FAST-12）

下面写一个简化但可运行的 FAST-12，帮你吃透算法：

```python
import numpy as np
import cv2

def is_fast_corner(img, y, x, threshold=20, N=12):
    """
    判断 (x,y) 是否是 FAST 角点。
    使用固定的 16 个邻居位置（半径 3）。
    """
    p = int(img[y, x])
    t = threshold
    bright = 0
    dark = 0
    # 圆周 16 点坐标（顺时针，从右开始）
    circle = [
        (0, 3), (1, 3), (2, 2), (3, 1), (3, 0), (3, -1), (2, -2), (1, -3),
        (0, -3), (-1, -3), (-2, -2), (-3, -1), (-3, 0), (-3, 1), (-2, 2), (-1, 3)
    ]
    # 初筛：先查 1,5,9,13（索引 0,4,8,12）
    pre = [0, 4, 8, 12]
    bright_pre = 0
    dark_pre = 0
    for i in pre:
        dy, dx = circle[i]
        v = int(img[y + dy, x + dx])
        if v > p + t:
            bright_pre += 1
        elif v < p - t:
            dark_pre += 1
    if bright_pre < 3 and dark_pre < 3:
        return False, 0
    # 完整扫描 16 点，找最长连续亮/暗
    max_consec = 0
    cur_b = 0
    cur_d = 0
    # 为处理环形连续，把 16 点复制一份接在后面
    vals = []
    for dy, dx in circle:
        v = int(img[y + dy, x + dx])
        if v > p + t:
            vals.append(1)   # 亮
        elif v < p - t:
            vals.append(-1)  # 暗
        else:
            vals.append(0)   # 相似
    vals += vals  # 复制一次
    for v in vals:
        if v == 1:
            cur_b += 1
            cur_d = 0
        elif v == -1:
            cur_d += 1
            cur_b = 0
        else:
            cur_b = cur_d = 0
        max_consec = max(max_consec, cur_b, cur_d)
    if max_consec >= N:
        # 响应分数（简易）
        V = 0
        for i, (dy, dx) in enumerate(circle):
            V += abs(int(img[y + dy, x + dx]) - p) - t
        return True, V
    return False, 0


def fast_detect(img, threshold=20, N=12, nms=True):
    h, w = img.shape
    corners = []
    for y in range(3, h - 3):
        for x in range(3, w - 3):
            ok, V = is_fast_corner(img, y, x, threshold, N)
            if ok:
                corners.append((y, x, V))
    if not nms:
        return [(y, x) for y, x, _ in corners]
    # 3×3 NMS：对同一块只留 V 最大
    keep = {}
    for y, x, V in corners:
        key = (y // 3, x // 3)
        if key not in keep or V > keep[key][2]:
            keep[key] = (y, x, V)
    return [(y, x) for y, x, _ in keep.values()]


# 使用
img = cv2.imread("test.jpg", 0)
pts = fast_detect(img, threshold=20, N=9)
color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
for y, x in pts:
    cv2.circle(color, (x, y), 3, (0, 0, 255), -1)
cv2.imshow("my FAST", color)
cv2.waitKey(0)
```

::: tip 注意
- 手写版是教学用，速度很慢（双重 for 循环），生产请用 OpenCV
- OpenCV 的 FAST 是用 C + SIMD 优化过的，比纯 Python 快几百倍
- 实际工程直接 `cv2.FastFeatureDetector_create()` 即可
:::

## FAST + 光流的标准组合

FAST 最常见的搭档是 LK 光流（稀疏光流跟踪）：

```python
# 初始化：第一帧提 FAST 角点
fast = cv2.FastFeatureDetector_create(threshold=20)
p0 = np.array([k.pt for k in fast.detect(prev_gray)], dtype=np.float32).reshape(-1, 1, 2)

# 逐帧 LK 跟踪
for frame in video:
    p1, st, err = cv2.calcOpticalFlowPyrLK(prev_gray, frame_gray, p0, None,
                                            winSize=(21, 21), maxLevel=3)
    good = p1[st == 1]
    # ... 使用 good 做 VO/SLAM
```

**这是 VINS-Mono、ORB-SLAM 前端的基本流程**。

## 相关链接

- [FAST 算法流程](/algorithms/fast/architecture)
- [FAST 调参口诀](/algorithms/fast/tricks)
- [Shi-Tomasi 角点（gFTT）](/algorithms/shi-tomasi/)
- [Lucas-Kanade 光流](/algorithms/lucas-kanade/)
''',
    painpoints_md=r'''
## FAST 的常见坑

::: danger 坑 1：threshold 太低，检测出海量噪声点
**现象**：`threshold=5` 或 `10` 时，一张图检测出几万个点，其中大部分是噪声。

**原因**：FAST 判据只看圆周 16 点，低阈值时任何微小纹理都能通过。

**解决**：
- 日常场景 `threshold=20` 起步
- 高对比纹理图 `threshold=30–40`
- 模糊图 `threshold=10–15`
- 配合 NMS（`nonmaxSuppression=True`）
:::

::: danger 坑 2：忘了开 NMS，角点扎堆
**现象**：同一个真实角点周围检测出 7、8 个紧挨的点。

**解决**：**`nonmaxSuppression=True`**（默认就是 True，别手动关）。
:::

::: danger 坑 3：以为 FAST 有尺度不变性
**现象**：图像放大 2 倍后，FAST 角点完全对不上。

**真相**：FAST 的半径固定是 3 像素，**没有尺度不变性**。

**解决**：
- 需要尺度不变性时，用 **ORB**（FAST + 图像金字塔）或 SIFT/SURF
- 或自己构建金字塔，在每层分别检测
:::

::: danger 坑 4：以为 FAST 有旋转不变性
**现象**：图像旋转后，同一点检测不出来，或者描述子匹配失败。

**真相**：纯 FAST **没有方向**，不抗旋转。

**解决**：
- 需要旋转不变性时，用 **ORB**（它给 FAST 加了灰度质心法的方向）
- 或者自己加方向分配（见 ORB 的 oFAST）
:::

::: danger 坑 5：直接用 FAST 做匹配失败
**现象**：两张图提了 FAST 点，却没法匹配。

**根因**：**FAST 只给"点"，不给"描述子"**——你不知道两个点"长得像不像"。

**解决**：必须搭配描述子：

| 组合 | 特点 |
|---|---|
| FAST + BRIEF | 快，但无旋转不变 |
| **FAST + rBRIEF = ORB** | **工业首选**，有旋转+尺度 |
| FAST + SIFT 描述子 | 精度高，慢 |

```python
# 推荐直接用 ORB
orb = cv2.ORB_create()
kp, des = orb.detectAndCompute(gray, None)
```
:::

::: danger 坑 6：FAST 点分布不均
**现象**：所有角点集中在墙角、纹理区域，墙面、天空一个点没有。

**解决（网格配额法）**：

```python
def grid_fast(img, grid=(4, 4), per_cell=25, threshold=20):
    h, w = img.shape
    fast = cv2.FastFeatureDetector_create(threshold=threshold)
    all_kp = []
    gh, gw = h // grid[0], w // grid[1]
    for i in range(grid[0]):
        for j in range(grid[1]):
            roi = img[i*gh:(i+1)*gh, j*gw:(j+1)*gw]
            kp = fast.detect(roi, None)
            kp = sorted(kp, key=lambda k: k.response, reverse=True)[:per_cell]
            for k in kp:
                k.pt = (k.pt[0] + j*gw, k.pt[1] + i*gh)
            all_kp.extend(kp)
    return all_kp
```
:::

::: danger 坑 7：FAST 在边界、模糊图上乱点
**现象**：图像边缘 3 像素内、失焦模糊区域会出一堆无意义点。

**解决**：
- 遍历时跳过图像边框（手写实现）
- OpenCV 版本自动处理边框
- 检测前先做轻微高斯模糊（`sigma=1`）去除噪声
:::

## 相关链接

- [FAST 源码实现](/algorithms/fast/source)
- [FAST 调参口诀](/algorithms/fast/tricks)
''',
    tricks_md=r'''
## FAST 调参口诀

```
threshold 二十是起步，模糊图降十、清晰图三十补；
NMS 永远开 True，关闭就成马蜂窝；
FAST-9-16 是默认，想要更快 5-8、更准 12-16 换；
只检测不提描述，匹配还得 BRIEF/ORB 组合组；
点太密用网格配额，每格上限二十五；
想跨尺度加金字塔，想抗旋转用 ORB 一键补。
```

## 参数选择指南

| 场景 | threshold | N | NMS | 推荐搭配 |
|---|---|---|---|---|
| 实时 SLAM/VO（30fps） | **20** | 9 | ✅ | ORB 描述子 |
| 高速目标检测（60fps） | 30 | 12 | ✅ | AGAST + BRIEF |
| 图像配准（精度优先） | 10–15 | 9 | ✅ | SIFT 描述子 |
| 嵌入式/MCU | 20 | 9 | ✅ | BRIEF（32 字节） |
| 图像分割/角点可视化 | 20–30 | 9 | ✅ | — |

## 实战技巧

### ① 前置高斯模糊稳定检测

```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (3, 3), 1.0)   # 轻微去噪
kp = fast.detect(gray, None)
```

**好处**：抑制高频噪声，FAST 点更稳定。**sigma 不能太大**（>1.5 会把角点糊掉）。

### ② 限制总点数 + 选响应最强的

```python
kp = fast.detect(gray, None)
kp = sorted(kp, key=lambda k: k.response, reverse=True)[:500]   # 取前 500
```

### ③ 做 LK 光流时如何选点

```python
# 不要直接用 FAST 点做 LK，用 goodFeaturesToTrack 更稳
# 但如果要速度，FAST + LK 可以这样配：
p0 = cv2.goodFeaturesToTrack(gray, maxCorners=200, qualityLevel=0.01, minDistance=10)
# 这就是 Shi-Tomasi（见 /algorithms/shi-tomasi/）
```

### ④ 检测后需要均匀分布的话用 cv2.KeyPoint 转换

```python
def nms_kp(kp, dist_thresh=10):
    """对 KeyPoint 列表按响应排序，做距离 NMS"""
    kp_sorted = sorted(kp, key=lambda k: k.response, reverse=True)
    keep = []
    for k in kp_sorted:
        x1, y1 = k.pt
        ok = True
        for kk in keep:
            x2, y2 = kk.pt
            if (x1-x2)**2 + (y1-y2)**2 < dist_thresh**2:
                ok = False
                break
        if ok:
            keep.append(k)
    return keep
```

### ⑤ FAST 不适合的场景

| 场景 | 原因 | 替代 |
|---|---|---|
| 鱼眼/广角畸变严重 | 圆周 3 像素畸变后形状变了 | 先去畸变再检测 |
| 大幅缩放匹配 | 无尺度不变 | ORB/SIFT |
| 大幅旋转匹配 | 无方向 | ORB/SIFT |
| 低光照/强噪声 | 阈值难选 | FAST+高斯模糊 或 SIFT |

## 性能参考（1920×1080 灰度，CPU）

| 方法 | 耗时 | 点数 |
|---|---|---|
| Harris | ~50 ms | 数千 |
| Shi-Tomasi | ~30 ms | ~200（受 maxCorners 限制） |
| **FAST-9-16** | **~4–6 ms** | 数千 |
| AGAST | ~3–5 ms | 数千 |
| ORB（检测+描述） | ~15 ms | 500 |
| SIFT | ~200 ms | 数千 |

**FAST 是 CPU 实时场景唯一选择**。

## 相关链接

- [FAST 源码实现](/algorithms/fast/source)
- [FAST 踩坑清单](/algorithms/fast/painpoints)
- [ORB 完整档案（FAST+方向+描述+尺度）](/algorithms/orb/)
'''
)


def build_full_md(key):
    """构造一个算法的 concepts/architecture/source/painpoints/tricks 五个 md 文件内容"""
    c = CONTENT[key]
    card_md = f"# {c['card']['name']}\n\n" + card_for(key, **c['card'])

    files = {}
    files["concepts.md"] = card_md + "\n" + c["concepts_md"].strip() + "\n"
    files["architecture.md"] = card_md + "\n" + c["architecture_md"].strip() + "\n"
    files["source.md"] = card_md + "\n" + c["source_md"].strip() + "\n"
    files["painpoints.md"] = card_md + "\n" + c["painpoints_md"].strip() + "\n"
    files["tricks.md"] = card_md + "\n" + c["tricks_md"].strip() + "\n"
    return files


def main():
    # 先跑 FAST 验证
    for key in ["fast"]:
        d = ROOT / key
        files = build_full_md(key)
        for fname, content in files.items():
            (d / fname).write_text(content, encoding="utf-8")
        print(f"[{key}] concepts/arch/src/pain/tricks done")

if __name__ == "__main__":
    main()
