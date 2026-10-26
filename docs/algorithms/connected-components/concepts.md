# 核心概念：连通域分析（Two-Pass）

<div class="tip custom-block"><p>🧪 公式看不懂？去 <a href="/math-lab/">原理实验室</a> 拖动滑块直观体验卷积/梯度/高斯/霍夫/角点/RANSAC/光流等核心概念；看完原理再去本页底部 <a href="./source">源码/真机实验室</a> 亲手调参数。</p></div>


## 1. 4-连通 vs 8-连通

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
- 经验：**先 connectedComponents 过滤大小，再对保留的域用 findContours 取轮廓**


---

## 🧪 原理可视化

看不懂上面的公式？下面这个互动组件把「邻域与距离」画出来了——拖动滑块，看每一步怎么算。

<ClientOnly>
  <MathVisualizer initial-tab="neighbor" compact />
</ClientOnly>

> 想看它在真实照片上的实际效果？回到 [本算法首页](./index) 或去 [🎮 真机实验室](/playgrounds/)。

<!-- AUTO-EXTENSION -->

## 🧓 大白话：连通域分析 = "把黑白色块一个个标出来"

二值化之后图上有很多白色"块"，连通域分析就是给**每个互相连接的白色块一个编号**，顺便统计它的面积、外接矩形、重心、圆形度等属性。这是**所有机器视觉项目必用的基础工具**——数米粒、数硬币、OCR 字符切分、缺陷检测、细胞计数，第一个想到的都是它。

**"连通"的定义**：
- **4-连通**：只认上下左右相邻；
- **8-连通**：对角也算相连。**默认用 8-连通**，更符合直觉。

## 为什么不用 findContours？

| 方法 | 输出 | 适用 |
| --- | --- | --- |
| `findContours` | 轮廓点集 | 要形状、周长、精确边界时 |
| **`connectedComponentsWithStats`** | 标签图+面积+外接矩形+重心 | **要统计数量、筛选大小、画色块** |

两个方法常常配合：先用连通域做大小过滤（去掉太小/太大的噪声块），再对保留的块做 `findContours` 算形状。
