# BoVW 调参技巧

## ① 词典大小 K：最该调的参数

**默认 1000**。从这里开始试：

| 场景 | 推荐 K |
|---|---|
| 快速原型 / <500 张图 | 500 |
| **通用甜点** | **1000~2000** |
| 数千张图 / 细粒度分类 | 4000 |
| 图像检索（需要区分度） | 10000~20000 |
| 加 SPM 时 | 可适度减小（每块都有直方图，独立统计更细） |

**心法**：K 从 1000 开始，按 ×2 递增（1000→2000→4000→8000），看验证集精度饱和在哪。

## ② 特征选择：SIFT vs ORB

| 场景 | 选什么 |
|---|---|
| **精度优先** | **SIFT**（BoVW 经典搭配） |
| 速度优先 | ORB（注意 Hamming 距离问题，或转 float） |
| 专利敏感 | ORB / AKAZE |
| 稠密采样分类 | Dense SIFT（VLFeat PHOW 风格） |

**强烈建议 BoVW 默认使用 SIFT**：传统流程里 SIFT 是经过 10 年验证的标准，ORB 在编码阶段距离度量问题多。

## ③ 每图特征点数量

| 场景 | 每图点数 |
|---|---|
| 快速原型 | 300 |
| **通用** | **500~1000** |
| 图像检索 / 精细分类 | 1000~2000 |
| Dense SIFT 网格步长 | 4~8 像素 |

```python
detector = cv2.SIFT_create(nfeatures=1000)  # 上限 1000 个
```

## ④ K-Means 配置

| 参数 | 推荐值 | 说明 |
|---|---|---|
| 初始化 | K-Means++ | 比随机初始化稳定 |
| attempts / n_init | 3 | 跑 3 次取最优 |
| batch_size (MiniBatch) | 2000~5000 | 大一点稳定，小一点快 |
| 最大迭代 | 100 | 足够 |
| 收敛阈值 | 1e-3 | 默认值够用 |

## ⑤ 编码方式：硬分配 vs 软分配

| 方法 | 精度 | 速度 | 适用 |
|---|---|---|---|
| 硬分配（默认） | 基准 | **快** | 通用、实时 |
| Top-3 软分配 | +1~3% | 慢 3 倍 | 精度优先 |
| Kernel Codebook | +2~5% | 慢 5~10 倍 | 竞赛/论文 |
| **VLAD / Fisher Vector** | **+5~15%** | 中 | **小样本强烈推荐** |

硬分配不够用时，优先考虑 VLAD/Fisher Vector 而不是自己写软分配。

## ⑥ 归一化 & 核技巧（零成本提升）

### 必做三步（训练和测试都要做）

```python
# 1) L1 归一化
hist = hist / (hist.sum() + 1e-9)
# 2) TF-IDF 加权
hist = hist * idf
hist = hist / (hist.sum() + 1e-9)  # 再次归一化
# 3) Hellinger 开方
hist = np.sqrt(hist)
```

这三步加起来，通常能让线性 SVM 精度提升 **5~10 个点**，是性价比最高的调优。

### 为什么不开方也能用 χ² 核？
可以，但 χ² 核 SVM 训练慢 N 倍。开方后用线性 SVM，效果接近 χ² 核，训练快 100 倍。

## ⑦ SPM（空间金字塔）配置

| levels | 分块数 | 总维度（K=1000） | 效果 |
|---|---|---|---|
| [1]（纯 BoVW） | 1 | 1000 | 基线 |
| [1, 2] | 1+4 = 5 | 5000 | 基础空间信息 |
| **[1, 2, 4]** | **1+4+16=21** | **21000** | **标准配置** |
| [1, 2, 4, 8] | 85 | 85000 | 细粒度，可能过拟合 |

**权重**：L0(1×1) 权重 1/4、L1(2×2) 1/4、L2(4×4) 1/2（论文默认）。

如果维度太高（21K 维）可以把 K 减半到 500，总维度 10500，速度快一倍，精度基本不掉。

## ⑧ SVM 调参

### 分类器选择
- **线性 SVM（LinearSVC）**：默认选择，快，适合高维稀疏直方图
- Histogram Intersection Kernel SVM：理论最优但训练慢
- KNN（k=1）：图像检索时用余弦相似度；分类不推荐
- 朴素贝叶斯：简单但精度差

### C 参数
| C | 效果 |
|---|---|
| 0.01 | 正则化强，保守 |
| **0.1** | **甜点** |
| 1 | 正常 |
| 10 | 易过拟合 |

```python
from sklearn.svm import LinearSVC
for C in [0.01, 0.1, 1, 10]:
    clf = LinearSVC(C=C, max_iter=3000)
    # 交叉验证选最优
```

### 多分类
- 默认 LinearSVC 用 One-vs-Rest，足够用
- 类别极不平衡时用 `class_weight='balanced'`

## ⑨ 典型场景参数模板

### 模板 A：10 类以内小样本图像分类（每类 50 张）
```python
detector = cv2.SIFT_create(nfeatures=800)
K = 1000
# 编码：硬分配
# 池化：L1 → TF-IDF → L1 → sqrt
# SPM：3 层 [1,2,4]
# 分类：LinearSVC(C=0.1)
# 预期精度：70%~85%
```

### 模板 B：图像检索（以图搜图）
```python
detector = cv2.SIFT_create(nfeatures=1500)
K = 10000                   # 词典大，区分度高
# 编码：硬分配 + TF-IDF
# 相似度：余弦相似度
# 索引：倒排索引（大规模）或 brute-force（<10000 图）
# 可选：重排用空间验证（RANSAC 单应矩阵）
```

### 模板 C：商标/Logo 识别（小目标、精确）
```python
detector = cv2.SIFT_create(nfeatures=2000)
K = 2000
# 预处理：去掉停用词（DF>0.8 的词）
# 编码：硬分配 + TF-IDF
# 分类：LinearSVC(C=1)，或直接用 FLANN 匹配+RANSAC 验证
```

### 模板 D：快速纹理分类（织物/材料）
```python
detector = cv2.SIFT_create(nfeatures=500)
K = 500
# 可选：LBP + HSV 颜色直方图 融合
# 池化：L1 → sqrt
# 不用 SPM（纹理是全局统计，空间不重要）
# 分类：LinearSVC(C=0.1) 或 KNN(k=3)
```

## ⑩ 超越 BoVW：升级路径

当纯 BoVW + SPM 精度不够时，按以下顺序升级（性价比递减）：

| 升级 | 精度提升 | 复杂度 |
|---|---|---|
| + Hellinger 开方 | +2~5% | 极低（一行代码） |
| + TF-IDF | +2~5% | 低 |
| + SPM | +5~15% | 中 |
| + Dense SIFT 替代兴趣点 | +3~8% | 中 |
| **VLAD 替代直方图** | **+5~10%** | 中 |
| **Fisher Vector 替代直方图** | **+10~15%** | 高 |
| 用 CNN 特征（VGG/ResNet fc） | +20~40% | 高（需 GPU） |
| 端到端训 CNN（ResNet/EfficientNet） | +30~50% | 高 |

### VLAD（Vector of Locally Aggregated Descriptors）
- K=64~256（小很多）
- 每个单词记录特征残差之和（D 维），总维度 K×D = 64×128 = 8192
- 精度比 BoVW 明显高，内存/速度更友好
- 工业上在深度学习之前是图像检索的主力

```python
# VLAD 编码（极简版）
def vlad_encode(des, codebook):
    K, D = codebook.shape
    vlad = np.zeros((K, D), np.float32)
    dists = np.linalg.norm(des[:, None] - codebook[None], axis=2)
    labels = dists.argmin(1)
    for i, d in enumerate(des):
        vlad[labels[i]] += d - codebook[labels[i]]  # 残差
    # 幂归一化 + L2 归一化
    vlad = np.sign(vlad) * np.sqrt(np.abs(vlad))
    vlad = vlad.flatten()
    vlad /= (np.linalg.norm(vlad) + 1e-9)
    return vlad
```

## ⑪ 与深度学习选型对照

| 需求 | 选什么 |
|---|---|
| **每类 <100 张样本，无 GPU** | **BoVW/SPM 或 VLAD + 线性 SVM** |
| 每类几百张、无 GPU | Fisher Vector + SVM |
| 每类几千张以上、有 GPU | ResNet/EfficientNet 微调 |
| 图像检索百万级 | SIFT + BoVW/IVFADC（倒排索引）或深度学习 DELG/DOLG |
| 工业可解释性要求 | BoVW（可反查单词和 patch） |
| 实时视频分类 | CNN/3D-CNN（BoVW 编一帧就要 0.1~0.3s） |
| 教学/入门 CV 分类概念 | **BoVW 是最佳教材** |

::: tip 什么时候还值得用 BoVW
1. **样本极少**（每类几十张）：小样本下 CNN 微调容易过拟合，BoVW+SVM 反而更稳
2. **无 GPU / 边缘设备**：ARM CPU 跑 BoVW 没问题
3. **需要可解释性**：能看"哪些视觉单词"判定了结果
4. **图像检索起步**：搭一个以图搜图 Demo，比 CNN 简单
5. **建立对「特征→编码→池化→分类」范式的理解**：理解 BoVW 再看 CNN 会顿悟
:::

## 速查表

| 参数 | 默认 | 推荐 |
|---|---|---|
| 特征 | SIFT | SIFT（精度）/ ORB（速度） |
| 词典 K | 1000 | 500~4000 |
| 每图点数 | 1000 | 500~2000 |
| 编码 | 硬分配 | 硬分配 |
| 归一化 | L1 | L1 → TF-IDF → L1 → sqrt |
| SPM | None | [1,2,4] 3 层 |
| SVM C | 1 | 0.1 |
| 近邻 | BF | K<2000 用 BF，否则 FLANN(checks=50) |
