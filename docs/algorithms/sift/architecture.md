# SIFT 算法流程

> 把 SIFT 拆成五个阶段，每一步的输入输出都讲清楚。

## 总流程图

```mermaid
flowchart TB
  IN["输入：灰度图"] --> S1

  subgraph S1["① 尺度空间构建"]
    GAUSS["高斯金字塔<br/>O 组 × S 层"]
    DOG["DoG 金字塔<br/>相邻层相减"]
    GAUSS --> DOG
  end
  S1 --> S2

  subgraph S2["② 极值检测与定位"]
    EXT["26 邻域极值"]
    SUB["亚像素精确定位"]
    REJ["剔除低对比度 + 边缘点"]
    EXT --> SUB --> REJ
  end
  S2 --> S3

  subgraph S3["③ 方向分配"]
    ORI["梯度方向直方图<br/>取主方向"]
  end
  S3 --> S4

  subgraph S4["④ 描述子生成"]
    DESC["4×4×8 = 128 维<br/>归一化"]
  end
  S4 --> S5

  subgraph S5["⑤ 匹配（可选）"]
    MATCH["最近邻/次近邻比<br/>+ RANSAC"]
  end
  S5 --> OUT["输出：匹配点对"]
```

## 阶段 ①：尺度空间构建

### 高斯金字塔参数

| 参数 | 论文建议 | OpenCV 默认 | 说明 |
|---|---|---|---|
| octaves（组数） | 由图像尺寸决定 | 自动（`log2(min(w,h))-3`） | 每组图像降采样一半 |
| scales per octave（每组层数） | 3 | 3 | 至少 3 层才能找极值 |
| initial sigma | 1.6 | 1.6 | 第一层的模糊程度 |
| assumed blur | 0.5 | — | 假设相机自身模糊 |

### 构建过程

```mermaid
flowchart TB
  I["输入图 I"] --> UP["若需要，先放大 1 倍<br/>使初始 sigma = 1.6"]
  UP --> G1["G(σ) := 用 sigma 模糊"]
  G1 --> LOOP["每组内按 k = 2^(1/S) 递增 sigma"]
  LOOP --> GEN["生成 S+3 层高斯图"]
  GEN --> DOGSUB["相邻层相减 → S+2 层 DoG"]
  DOGSUB --> DOWN["取第 S 层（σ=2σ0）<br/>降采样一半"]
  DOWN --> NEXT["进入下一组"]
  NEXT --> LOOP
```

**关键数值**：

- 每组生成 **S + 3** 层高斯图（多 3 层是为了在组边界处也能找极值）
- 相减得到 **S + 2** 层 DoG
- 每组只有**中间的 S 层**能找到极值（首尾层不能，因为没有上下邻居）

::: tip 为什么要多生成 3 层
找极值需要「上下各一层」。组内首层没有「上一层」，末层没有「下一层」，所以能在组内找极值的只有中间 $S$ 层。
为了保证「中间 S 层的尺度覆盖连续」，必须多生成几层来补齐邻居。
:::

### 尺度计算

每层的尺度：

$$
\sigma_o = 2^{o} \cdot \sigma_0, \quad o = 0, 1, \ldots, O-1
$$

组内层的尺度：

$$
\sigma_{o,s} = 2^{o} \cdot k^{s} \cdot \sigma_0, \quad k = 2^{1/S}
$$

## 阶段 ②：极值检测与定位

### 26 邻域极值检测

```mermaid
flowchart TB
  P["DoG 金字塔中<br/>点 (x, y, s)"] --> CMP["与 26 个邻居比较"]
  CMP --> R1{"大于所有邻居?"}
  CMP --> R2{"小于所有邻居?"}
  R1 -->|是| MAX["极大值候选"]
  R2 -->|是| MIN["极小值候选"]
  R1 -->|否| REJ["不是极值"]
  R2 -->|否| REJ
```

**注意**：只比较**组内**的相邻层，不跨组。

### 亚像素定位

```python
# 伪代码示意
for each candidate:
    # 迭代求解极值偏移
    for iter in range(max_iter=5):
        D = value at (x, y, s)
        dD = gradient of D         # 一阶偏导
        ddD = hessian of D          # 二阶偏导
        offset = -solve(ddD, dD)    # 求解偏移

        if abs(offset) < 0.5:       # 收敛
            break
        x += round(offset[0])
        y += round(offset[1])
        s += round(offset[2])

    x_hat = x + offset             # 亚像素坐标
```

### 两点剔除

```mermaid
flowchart TB
  K["亚像素定位后的点"] --> C1{"|D(x_hat)| < 0.04?"}
  C1 -->|是| D1["剔除：对比度太低"]
  C1 -->|否| C2{"Tr(H)²/Det(H) ≥ 12.1?"}
  C2 -->|是| D2["剔除：边缘响应"]
  C2 -->|否| KEEP["保留为关键点"]

  C1 -->|否| C2
```

**OpenCV 默认参数**：

| 参数 | 默认值 | 含义 |
|---|---|---|
| `contrastThreshold` | 0.04 | 低于此值的点被剔除 |
| `edgeThreshold` | 10 | 边缘响应阈值（$r = 10$） |

::: warning 注意 OpenCV 的 edgeThreshold 语义
OpenCV 里 `edgeThreshold = 10` 表示 $r = 10$，判据是：
$$
\frac{\text{Tr}(H)^2}{\text{Det}(H)} \geq \frac{(r+1)^2}{r} = \frac{121}{10} = 12.1
$$
**数值越大，剔除越宽松（保留的边缘点越多）。** 这个方向和 `contrastThreshold` 相反，容易搞混。
:::

## 阶段 ③：方向分配

```mermaid
flowchart TB
  K["关键点 (x, y, σ)"] --> W["取窗口<br/>半径 = 1.5σ（按当前尺度）"]
  W --> G["计算窗口内每个像素的<br/>梯度幅值 m 与方向 θ"]
  G --> H["按 36 个 bin 统计直方图<br/>幅值 × 高斯权重 加权"]
  H --> S["直方图平滑"]
  S --> P["找主峰 → 主方向"]
  P --> M{"是否存在次峰<br/>≥ 主峰 80%?"}
  M -->|是| EXTRA["额外生成<br/>同位置同尺度同描述子<br/>不同方向的关键点"]
  M -->|否| DONE["完成"]
```

**直观展示**：

| 情况 | 结果 |
|---|---|
| 单一主峰 | 1 个关键点，1 个方向 |
| 有两个并强的主方向 | 2 个关键点（位置尺度相同，方向不同） |
| 主峰很弱 | 仍然接受（没有最低阈值约束） |

## 阶段 ④：描述子生成

```mermaid
flowchart TB
  K["关键点 + 主方向 θ"] --> R["按 −θ 旋转坐标轴<br/>使主方向对齐 x 轴"]
  R --> WIN["取 16×16 邻域<br/>像素步长 = σ"]
  WIN --> BLK["分成 4×4 个区块<br/>每区块 4×4 像素"]
  BLK --> H8["每个像素梯度<br/>三线性插值到 8 方向"]
  H8 --> V["4×4×8 = 128 维向量"]
  V --> N1["归一化到单位长度"]
  N1 --> TR["分量 > 0.2 截断为 0.2"]
  TR --> N2["再次归一化"]
  N2 --> OUT["最终 128 维描述子"]
```

**三线性插值**：每个像素的梯度贡献会按距离权重分配到：

- 相邻的 **2 个方向 bin**
- 相邻的 **x 方向 2 个区块列**
- 相邻的 **y 方向 2 个区块行**

这样避免区块边界的突变，让描述子更平滑、更鲁棒。

## 阶段 ⑤：匹配

### 最近邻 / 次近邻比

```mermaid
flowchart TB
  D1["图 A 的某个描述子"] --> S["在 图 B 里找<br/>最近的 K 个描述子"]
  S --> N1["最近邻距离 d1"]
  S --> N2["次近邻距离 d2"]
  N1 --> R{"d1 / d2 < 0.8?"}
  N2 --> R
  R -->|是| M["接受为匹配"]
  R -->|否| X["丢弃（不独特）"]
```

### 匹配后处理：RANSAC

```mermaid
flowchart LR
  ML["初始匹配点对<br/>含大量错误"] --> RANSAC["RANSAC<br/>求单应矩阵 H"] --> INLIER["内点 = 正确匹配<br/>外点 = 误匹配"]
```

详见 [特征匹配分支](/branches/feature-matching/robust-estimation)。

## 数据流转示例

假设输入一张 **512×512** 灰度图：

| 阶段 | 数据 | 规模 |
|---|---|---|
| 输入 | 灰度图 | 512 × 512 |
| ① 高斯金字塔 | O ≈ 7 组，每组 S+3 = 6 层 | 约 42 张图 |
| ① DoG 金字塔 | 每组 S+2 = 5 层 | 约 35 张图 |
| ② 关键点 | 位置 + 尺度 | 典型 1000–5000 个 |
| ③ 方向 | 关键点方向 | 与关键点数同量级 |
| ④ 描述子 | 128 维向量 | 1000–5000 × 128 |
| ⑤ 匹配 | 匹配点对 | 视场景，几十到几百对 |

## 复杂度分析

| 阶段 | 时间复杂度 | 说明 |
|---|---|---|
| ① 尺度空间 | $O(N \log N)$ | N 为像素数，多尺度卷积 |
| ② 极值检测 | $O(N)$ | 每个 DoG 点常数次比较 |
| ③ 方向分配 | $O(K \cdot w^2)$ | K 为关键点数，w 为窗口 |
| ④ 描述子 | $O(K \cdot 16^2)$ | 每个关键点处理 16×16 邻域 |
| ⑤ 匹配 | $O(K_A \cdot K_B)$ | 暴力匹配；用 KD 树可降到 $O(K \log K)$ |

**整体**：主要在 ① 和 ④，1080p 图 CPU 上约数百毫秒。

## 与本体实例的对应

```yaml
- id: algo-sift
  type: Algorithm
  stages:
    - order: 1
      name: "尺度空间构建"
      operators: ["op-gaussian-blur", "op-dog"]
    - order: 2
      name: "极值检测与定位"
      operators: ["op-extremum-3d", "op-subpixel-refine"]
    - order: 3
      name: "方向分配"
      operators: ["op-gradient-histogram"]
    - order: 4
      name: "描述子生成"
      operators: ["op-descriptor-128d"]
    - order: 5
      name: "匹配"
      operators: ["op-nn-ratio-test", "op-ransac"]
```
