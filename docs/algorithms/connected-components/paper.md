# 论文精读：连通域分析（Two-Pass）

## 论文信息

| 项 | 内容 |
|---|---|
| 论文标题 | Connected Components Labeling (综述) |
| 作者 | Rosenfeld / Wu et al. / Grana et al. |
| 发表年份/会议 | 1966 / 2008 / 2016 |
| 引用数（约） | 经典算法，累计引用巨大 |
| 核心贡献 | 两遍扫描：第一遍给每个前景点贴临时标签并用并查集合并等价类；第二遍把每个标签替换成等价类根；OpenCV 的 `connectedComponentsWithStats` 还直接输出每个域的面积、外接框、质心 |
| OpenCV 实现 | `cv2.connectedComponents / cv2.connectedComponentsWithStats` |

## 论文为什么被写出来？

连通域标记是图像处理最古老的问题之一（1966 年 Rosenfeld 就在论文里系统讨论）。早期算法包括：
- **递归填充法**：遇到未标记点就 flood fill，但递归深度大时会栈溢出
- **逐行扫描 + 等价表**：就是 Two-Pass 的雏形

经典 Two-Pass 在 1980s 定型，但标签合并的实现效率不高。2000 年后一系列优化：
- **Wu et al. 2009**：BBDT 算法，用决策树优化邻域访问顺序
- **Grana et al. 2010/2016**：SAUF/SAUF-RemSP 算法，每行只做一次扫描、条件跳转最优，是当前 OpenCV 使用的算法，640×480 图 0.1ms 量级。

## 核心创新点

**经典 Two-Pass 算法**：
1. 第一遍：从左到右、从上到下扫。对每个前景点，看**左、左上、上、右上**（4 连通只看左+上）四个邻居：
   - 邻居都没标签：分配新标签
   - 邻居有标签：取最小的那个贴上，把邻居之间的标签等价关系记进并查集
2. 第二遍：再扫一遍，把每个标签替换成并查集的根标签，并累加该标签的面积、bbox 等统计信息。

**BBDT/SAUF 优化**：
- 把 4 个邻居的 2^4=16 种「是否是前景点」组合做成决策树，每种组合走不同的代码路径，避免冗余判断
- 标签数组用 int 连续存储，缓存友好
- OpenCV 实现用了 ORC 掩码（Decision Tree）+ 块操作

## 论文里的关键结果

- 速度：640×480 图 0.1ms（SAUF），比 findContours 快 5–10×
- 结果：每个连通域一个唯一 label，附带 stats（面积/外接框）和 centroid
- 工程上 90% 的「数个数/筛选」场景都能用它替代 findContours

## 论文的局限与后人改进

- 只能处理二值图
- 孔洞处理需要小心：前景用 8-连通时背景必须用 4-连通才能正确区分孔洞（否则孔洞会和外部背景连通）
- 不提供轮廓形状点（要形状用 findContours）

## 论文阅读建议

- 初读：只看 abstract + Wu et al. 2009《Optimizing two-pass connected-component labeling algorithms》
- 精读：再看算法流程图与 直接看 OpenCV `connectedComponents.cpp` 源码，非常精炼
- 工程落地：直接对照 OpenCV `cv2.connectedComponents / cv2.connectedComponentsWithStats` 源码，**不必复现论文**
