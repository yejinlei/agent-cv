---
outline: deep
---

## 🧪 原理互动演示

<AlgoVisualizer type="flann" />


# 第 3 页 · 核心概念

<div class="tip custom-block"><p>🧪 公式看不懂？去 <a href="/math-lab/">原理实验室</a> 拖动滑块直观体验卷积/梯度/高斯/霍夫/角点/RANSAC/光流等核心概念；看完原理再去本页底部 <a href="./source">源码/真机实验室</a> 亲手调参数。</p></div>


## 先用生活直觉理解

你在图书馆找一本最接近某主题的书。暴力法是走遍每一排书架；FLANN 是先用「分区索引」直接跳到可能的那几排，找到「差不多最好」的就走。偶尔不是最优，但快得多——匹配几千个特征点的时候，这点误差根本不重要。

**典型应用**：大规模特征匹配（SLAM、全景拼接、图像检索）、SIFT/SURF 描述子匹配、点云配准

```mermaid
flowchart LR
  A["输入"] --> B["核心处理"] --> C["输出"]
```

## 概念逐个拆解

### 概念 1：什么是最近邻搜索

给定一个查询特征，在库里找与它最相似的那个。匹配两张图就是让彼此的特征互为最近邻。

### 概念 2：暴力匹配 vs 索引

暴力匹配逐个算距离 O(N²)；索引法只查最可能的分支，把 N² 降到接近 N·log N。

```mermaid
flowchart LR
  A["BF: 逐点比"] --> B["O(N^2)"]
  C["FLANN: 索引"] --> D["≈O(N logN)"]
```

### 概念 3：KD-Tree 与 LSH

浮点描述子（SIFT/SURF）用 KD-Tree 按维度切分空间；二进制描述子（ORB/BRIEF）用 LSH 做哈希分桶。

### 概念 4：近似换速度

checks 参数控制搜索多少个节点。设小则快但漏，设大则准但慢——典型的时间换精度旋钮。

## 和其他算法的关系

| 关系 | 算法 | 说明 |
|------|------|------|
| 前置依赖 | 特征检测 + 描述子（SIFT/SURF/ORB） | 通常先做这些再做本算法 |
| 同类对比 | BFMatcher 暴力匹配 | 解决同类问题，各有取舍 |
| 下游常用 | 比率测试、RANSAC 几何验证、单应估计 | 本算法结果常交给它们处理 |

::: tip 记忆锚点
记住「浮点描述子用 KD-Tree（trees/checks），二进制描述子用 LSH」。
:::

<!-- AUTO-EXTENSION-2 -->

## 🧓 大白话：FLANN = "高维向量快速查找的图书馆"

暴力匹配（BFMatcher）要把查询点和数据库里**每个描述子**都算一次距离，10 万个描述子就是 10 万次计算——这在图像检索（几千张图）里根本不能用。

**FLANN（Fast Library for Approximate Nearest Neighbors）** 不是一种算法，是**一整套近似最近邻查找方法的库**：
- **随机 kd 树**：低维（<100）浮点描述子（SIFT/SURF）最快；
- **层次 k-means 树**：高维浮点描述子；
- **LSH（Locality Sensitive Hashing）**：二值描述子（ORB/BRISK/AKAZE）专用；
- **自动选择**：FLANN 会根据你的数据自动选最快的索引方式。

"近似" 是指——不保证找到绝对最近邻，但**速度快 10~1000 倍，且 95%+ 情况下找到的就是真最近邻**。

## 关键参数

| 参数 | 含义 | 调大 | 调小 |
| --- | --- | --- | --- |
| `checks` | 搜索时检查多少叶子 | 更准但慢 | 更快但可能漏 |
| `trees` | kd 树数量 | 更准，内存多 | 快但粗糙 |
| `table_number`/`key_size`（LSH）| 哈希表数量/键长 | 更准 | 更快 |

**实战口诀**：
> **SIFT/SURF 用 KDTree，ORB/AKAZE 用 LSH；checks 从 100 起步，不够准往上加。**

> ⚠️ 注意：OpenCV.js 构建不包含 FlannBasedMatcher，网页端匹配请用 BFMatcher + crossCheck。
