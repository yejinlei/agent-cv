# BoVW 实战踩坑

## 坑 1：词典太大或太小

### 症状
- **K=100**：分类精度只有 50%~60%，所有图看起来都"差不多"
- **K=50000**：训练极慢（K-Means 跑几小时），每个图像直方图几乎全 0（过拟合），新图全是未见过的组合

### 根因
- K 太小：视觉单词太"粗"，不同模式被合并到同一个词
- K 太大：视觉单词太"细"，每个词只对应少数特征，泛化性差

### 推荐 K 值

| 训练图数量 | 推荐 K |
|---|---|
| <500 张 | 500~1000 |
| 500~5000 张 | **1000~4000** |
| 5000~50000 张 | 4000~10000 |
| >50000 张 | 10000~20000 |

心法：**先试 1000**，精度不够加 K；速度不够减 K。

## 坑 2：词典"污染"——背景特征太多

### 症状
- 分类器对"天空、草地、墙面"这种背景词响应强
- 同类物体背景不同就分错（比如猫放草地上 vs 放地毯上）

### 根因
训练图里背景区域的 SIFT 点往往比目标多，K-Means 会把大量簇心分配给背景模式，"物体词"占比反而少。

### 避坑
1. **用标注的 bbox 提特征**：只在目标区域提 SIFT，不要在整张图上提
2. **降采样背景点**：每张图限制特征点上限，并使用响应强度排序保留前 N 个强点
3. **TF-IDF 加权**：降权常见背景词
4. **Stop-word removal**：去掉在 >80% 图像里都出现的"停用词"（非常类似文本里去掉"的/是"这种词）

```python
# 简单停用词去除
df = (hist_train > 0).sum(0)
stop_words = df > 0.8 * len(X_train)
X_train[:, stop_words] = 0
X_test[:, stop_words] = 0
```

## 坑 3：SIFT/ORB 返回 None（图太糊/太小）

### 症状
```
AttributeError: 'NoneType' object has no attribute 'astype'
```
或直方图全 0。

### 根因
- 图太小、对比度太低、全黑/全白，SIFT 检不出关键点
- ROI 裁切后区域小于 16×16

### 避坑
```python
_, des = detector.detectAndCompute(gray, None)
if des is None or len(des) < 5:
    # 没有特征点：回退到密集网格采样（dense SIFT）
    kp = [cv2.KeyPoint(x, y, 8)
          for y in range(8, gray.shape[0], 8)
          for x in range(8, gray.shape[1], 8)]
    _, des = detector.compute(gray, kp)
```
密集采样（Dense SIFT/PHOW）在分类任务里往往比兴趣点 SIFT 更稳定，是 VLFeat 工具包的默认选项。

## 坑 4：没做 L1 归一化，图大/图小直方图不一致

### 症状
- 同一场景拍特写和远景，直方图差异很大（特写点数多，词频绝对值大）
- 分类器偏向"图大"的那一类别

### 根因
没做归一化时，直方图值是绝对词频，跟图里总点数有关。

### 避坑
```python
hist = hist / (hist.sum() + 1e-9)  # L1 归一化
```
SVM 之前一定要 L1 或 L2 归一化。

## 坑 5：没开 Hellinger 核，线性 SVM 效果差

### 症状
线性 SVM 精度比 kernel SVM 差一大截，但 kernel SVM 训练又很慢。

### 根因
直方图相交核 / χ² 核是 BoVW 经典选择，但线性 SVM 最快。简单的数学变换能让线性 SVM 逼近核 SVM 效果。

### 避坑（**Hellinger 核技巧**）
```python
X_train = np.sqrt(X_train)  # 逐元素开方
X_test  = np.sqrt(X_test)
# 此时线性内积 ≈ Hellinger 核（Bhattacharyya 系数）
clf = LinearSVC(C=0.1).fit(X_train, y_train)
```
这是 Winn et al. 2005 证明的经典 trick，几乎零代价，稳定提升 2~5 个点。

## 坑 6：SIFT 描述子是 uint8/int16，没转 float32 就 K-Means

### 症状
```
cv2.error: ... in kmeans
```
或者 K-Means 结果奇怪，聚类不收敛。

### 根因
OpenCV 的 SIFT 默认返回 `float32`，ORB 返回 `uint8`。混用类型会导致 K-Means 崩溃或精度问题。

### 避坑
```python
des = des.astype(np.float32)  # 进 K-Means 前统一转 float32
codebook = codebook.astype(np.float32)
```

## 坑 7：训练集/测试集用了不同的预处理

### 症状
- 训练集做了直方图均衡，测试时忘了做 → 精度骤降
- 训练时是彩色图灰度化，测试时用了二值图

### 避坑
**统一预处理 pipeline**：训练和测试用完全相同的灰度化、尺寸、直方图均衡化步骤。最好写成一个函数：

```python
def preprocess(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)          # 可选
    return gray
```

## 坑 8：K-Means 用全量数据训练导致内存爆炸

### 症状
- 10 万张图，每张 1000 个 SIFT 点 → 1 亿个 128 维向量 → 50+ GB 内存，K-Means 直接 OOM

### 根因
K-Means 不需要所有数据，用**代表性子集**就够了。

### 避坑
1. **随机采样**：从所有描述子中随机抽 50 万~100 万训练，精度几乎不降
2. **每张图限点数**：每图最多 200~500 个点
3. **Mini-Batch K-Means**：不加载全部数据到内存

```python
# 每张图取前 300 个点 + 全库随机采样到 50 万
max_pts_per_img = 300
sample_size = 500000
all_des = []
for des in image_descriptors:
    if len(des) > max_pts_per_img:
        idx = np.random.choice(len(des), max_pts_per_img, replace=False)
        des = des[idx]
    all_des.append(des)
all_des = np.vstack(all_des)
if len(all_des) > sample_size:
    idx = np.random.choice(len(all_des), sample_size, replace=False)
    all_des = all_des[idx]
```

## 坑 9：新类别加入必须重训词典

### 症状
- 加一个新类别，直接训 SVM → 效果很差
- 用旧词典编码新类别图，词频分布异常

### 根因
旧词典里没有新类别的典型模式，新类别的特征都被"硬塞"给最近但不相关的旧词。

### 避坑
- 加入新类别时：**新类特征 + 旧词典**→ 可以重新跑一次 K-Means（从旧簇心初始化，做增量聚类）
- 或者从头重训（代价大但最干净）
- 工程上：一次性收集所有类别数据再建词典；增量类别用 Fisher Vector 等更适合增量的方法

## 坑 10：只用整图 BoVW 不做 SPM，空间信息全丢

### 症状
- 上下结构错配的图被当成同一类（比如"天空+草地"和"草地+天空"分不出来）
- 自然场景分类效果差

### 根因
纯 BoVW 是"Bag"，完全不看位置。

### 避坑
**SPM（空间金字塔）几乎是必加项**——21 块的 SPM + BoVW 是 2006~2012 年的标配，能稳定提升 10+ 个点，代码量只多几十行。

## 坑 11：FLANN 参数错导致最近邻不准

### 症状
- 用 FLANN 编码比用 BF 精度低 5~10 个点
- 某些特征被分到奇怪的词

### 根因
FLANN 是近邻近似算法，`checks` 参数太小会不精确。

### 避坑
```python
flann = cv2.FlannBasedMatcher(
    dict(algorithm=1, trees=5),
    dict(checks=50)     # 默认 32，开到 50~100 精度接近 BF
)
```
K<2000 时直接用 BFMatcher 更简单，精度也最可靠。

## 坑 12：ORB 描述子和 K-Means 距离不匹配

### 症状
用 ORB（二进制 uint8 描述子）+ 默认 L2 K-Means，效果很差。

### 根因
ORB 描述子是二进制，应该用 **Hamming 距离**；而 sklearn KMeans 默认用 L2。

### 避坑
1. **ORB 转 float 用 L2**（简单但次优）：
   ```python
   des = des.astype(np.float32)
   ```
2. **自定义 K-Means 用 Hamming 距离**（复杂）
3. **直接用 SIFT** 最省心（float 描述子、L2 原生支持、精度高）：BoVW 传统上都是 SIFT，工程上默认选 SIFT。

## 常见错误速查表

| 错误 | 原因 | 解法 |
|---|---|---|
| K-Means OOM | 描述子太多 | 随机采样 + MiniBatch |
| des 是 None | 图像无特征点 | 回退 dense grid |
| 直方图全 0 | 词典没加载 / 描述子类型错 | 检查 setVocabulary、dtype |
| SVM 精度低 | 没归一化/没开方/没 TF-IDF | L1→sqrt→SVM |
| 新类别效果差 | 词典没更新 | 重训词典或做增量 K-Means |
| 上下结构混淆 | 没做 SPM | 加 3 层 SPM |
| BF 太慢 | K 太大 | 换 FLANN（checks=50+） |
