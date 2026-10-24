# 算法流程：连通域分析（Two-Pass）

## 整体流程图

```mermaid
flowchart TD

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

```

## 步骤详解

### Step 1：输入
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
N = 标签总数（含背景 label=0）。

## 参数对照（论文 vs OpenCV 默认 vs 工程建议）

| 参数 | 论文建议 | OpenCV 默认 | 工程建议 | 调参影响 |
|---|---|---|---|---|
| connectivity | 8 | 8 | 4（细粒度分离）/8（抗噪） | 连通性选择 |
| ltype | CV_32S | CV_32S | CV_32S（标签多）/CV_16U（标签<65536） | 标签图类型 |
| ccltype | CCL_DEFAULT | CCL_DEFAULT | CCL_DEFAULT/CCL_SAUF/CCL_BBDT | 具体算法，默认选最快的 |

## 复杂度分析

- 两遍扫描都是 O(W·H)
- 每次 find/union 均摊 O(α(N)) ≈ O(1)
- 现代 SAUF 实现：640×480 图约 0.1–0.3ms
