# BoVW 源码走读

## ① OpenCV 原生 BOW 模块（工业标准用法）

OpenCV 提供了完整的 BoW 工具链：
- `BOWKMeansTrainer`：K-Means 词典训练器
- `BOWImgDescriptorExtractor`：给定词典，把图像编码成直方图
- `BFMatcher` / `FlannBasedMatcher`：最近邻匹配器

### 完整分类 Pipeline

```python
import cv2
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.preprocessing import normalize

# ---------- 0) 参数 ----------
K = 1000                    # 词典大小
DETECTOR_NAME = "SIFT"      # SIFT / ORB / SURF

# ---------- 1) 构建检测器和匹配器 ----------
if DETECTOR_NAME == "SIFT":
    detector = cv2.SIFT_create(nfeatures=1000)
    norm = cv2.NORM_L2
elif DETECTOR_NAME == "ORB":
    detector = cv2.ORB_create(nfeatures=1000)
    norm = cv2.NORM_HAMMING
matcher = cv2.BFMatcher(norm)

# ---------- 2) 创建 BoW 训练器 ----------
bow_trainer = cv2.BOWKMeansTrainer(
    clusterCount=K,
    termCrit=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001),
    attempts=3,
    flags=cv2.KMEANS_PP_CENTERS
)

# ---------- 3) 提取特征喂给训练器 ----------
def add_img_to_trainer(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, des = detector.detectAndCompute(gray, None)
    if des is not None and len(des) > 0:
        bow_trainer.add(des.astype(np.float32))

for img, label in zip(train_imgs, train_labels):
    add_img_to_trainer(img)

# ---------- 4) 训练词典 ----------
print("聚类中...")
vocab = bow_trainer.cluster()
np.save("vocab.npy", vocab)

# ---------- 5) 创建 BoW 描述子提取器 ----------
bow_extract = cv2.BOWImgDescriptorExtractor(detector, matcher)
bow_extract.setVocabulary(vocab)

def img_to_hist(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    kp = detector.detect(gray)
    hist = bow_extract.compute(gray, kp)
    if hist is None:
        return np.zeros(K, np.float32)
    return hist.flatten()

# ---------- 6) 提取所有训练图的直方图 ----------
X_train = np.stack([img_to_hist(img) for img in train_imgs])
y_train = np.array(train_labels)

# 开方（Hellinger 核）
X_train = np.sqrt(X_train)

# ---------- 7) 训线性 SVM ----------
clf = LinearSVC(C=0.1, max_iter=2000)
clf.fit(X_train, y_train)

# ---------- 8) 测试 ----------
hist = img_to_hist(test_img)
hist = np.sqrt(hist)
pred = clf.predict(hist.reshape(1, -1))
print(f"预测类别: {pred}")
```

## ② 图像检索 Demo（Top-N 相似图）

```python
# 对数据库所有图像提前算 TF-IDF 直方图
from sklearn.feature_extraction.text import TfidfTransformer
tfidf = TfidfTransformer()
X_db = np.stack([img_to_hist(img) for img in db_imgs])
X_db = tfidf.fit_transform(X_db)  # 稀疏矩阵加速

# 查询
q = tfidf.transform(img_to_hist(query_img).reshape(1, -1))
from sklearn.metrics.pairwise import cosine_similarity
sims = cosine_similarity(q, X_db).flatten()
top5 = np.argsort(-sims)[:5]
print(f"最相似图像索引: {top5}, 相似度: {sims[top5]}")
```

## ③ numpy + sklearn 手写版本（不依赖 OpenCV BOW）

### 3.1 手写 Mini-Batch K-Means（原理版）

```python
import numpy as np

def mini_batch_kmeans(X, K, batch_size=2000, iters=50, n_init=3):
    """
    X: (N, D) 所有描述子
    K: 聚类数
    返回: (K, D) 簇心
    """
    best_inertia = float('inf')
    best_centers = None
    N, D = X.shape
    for init in range(n_init):
        # K-Means++ 初始化
        idx = np.random.choice(N, 1)
        centers = [X[idx[0]]]
        for _ in range(K-1):
            d2 = np.min(
                np.stack([np.sum((X - c)**2, axis=1) for c in centers], axis=1),
                axis=1
            )
            probs = d2 / d2.sum()
            centers.append(X[np.random.choice(N, p=probs)])
        centers = np.array(centers)

        # Mini-Batch 迭代
        counts = np.zeros(K)
        for it in range(iters):
            batch_idx = np.random.choice(N, batch_size, replace=False)
            batch = X[batch_idx]
            # 分配
            dists = np.linalg.norm(
                batch[:, None, :] - centers[None, :, :], axis=2
            )  # (B, K)
            labels = dists.argmin(axis=1)
            # 更新
            for k in range(K):
                mask = labels == k
                if mask.any():
                    eta = 1.0 / (counts[k] + mask.sum())
                    centers[k] = (1-eta)*centers[k] + eta*batch[mask].mean(0)
                    counts[k] += mask.sum()
        # 计算 inertia
        dists = np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2)
        inertia = dists.min(axis=1).sum()
        if inertia < best_inertia:
            best_inertia = inertia
            best_centers = centers.copy()
    return best_centers
```

### 3.2 手写硬分配编码器

```python
def encode_hist_hard(des, codebook):
    """
    des: (n, D)  一幅图的描述子
    codebook: (K, D)  词典
    返回: (K,) L1 归一化直方图
    """
    K = len(codebook)
    if des is None or len(des) == 0:
        return np.zeros(K, np.float32)
    # 暴力最近邻（K<2000 时可接受；K 大时用 KD-Tree）
    dists = np.linalg.norm(des[:, None, :] - codebook[None, :, :], axis=2)
    labels = dists.argmin(axis=1)
    hist = np.bincount(labels, minlength=K).astype(np.float32)
    hist /= (hist.sum() + 1e-9)
    return hist
```

### 3.3 SPM 编码器（手写）

```python
def encode_spm(img, detector, codebook, levels=[(1, 0.25), (2, 0.25), (4, 0.5)]):
    """
    levels: [(n, weight), ...]
    返回: (K * (1²+2²+4²),) = 21K 维向量
    """
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    parts = []
    for n, weight in levels:
        gh, gw = h // n, w // n
        for i in range(n):
            for j in range(n):
                patch = gray[i*gh:(i+1)*gh, j*gw:(j+1)*gw]
                _, des = detector.detectAndCompute(patch, None)
                sub = encode_hist_hard(des, codebook)
                parts.append(sub * weight)
    return np.hstack(parts)
```

## ④ 用 FLANN 加速最近邻编码

K 很大（>2000）或描述子数量大时，暴力法 O(N·K) 太慢，用 FLANN：

```python
import cv2
flann = cv2.FlannBasedMatcher(
    indexParams=dict(algorithm=1, trees=5),         # KD-Tree
    searchParams=dict(checks=50)
)
# codebook 作为 "训练集" 喂给 FLANN（要存在数组里）
# knnMatch 的 query = des, train = codebook
matches = flann.knnMatch(des.astype(np.float32),
                         codebook.astype(np.float32), k=1)
labels = [m[0].trainIdx for m in matches]
```

## ⑤ 训练一个完整的 Caltech-101 子集

```python
# 以 Caltech-101 数据集中 5 类为例
import os, glob
categories = ["airplanes", "Motorbikes", "faces", "watch", "Leopards"]
train_imgs = []
train_labels = []
for lab, cat in enumerate(categories):
    for fp in glob.glob(f"101_ObjectCategories/{cat}/*.jpg")[:50]:
        img = cv2.imread(fp)
        if img is not None:
            train_imgs.append(img)
            train_labels.append(lab)

# 按前面的完整 pipeline 训完后，测试集见下
acc = (clf.predict(X_test) == y_test).mean()
print(f"5 类准确率: {acc:.2%}")  # 典型结果 80%~90%
```

## ⑥ 可视化：哪些视觉单词贡献了判定

BoVW 的好处是**可解释**——训练完线性 SVM 后，可以看每个单词的权重：

```python
# clf.coef_ 形状 (n_classes, K)，每类 K 个权重
for ci, cat in enumerate(categories):
    top_words = np.argsort(-clf.coef_[ci])[:20]
    print(f"\n类别 {cat} 的 Top-20 判别单词: {top_words}")
    # 可以用这些单词的簇心，反查哪些 SIFT 描述子属于它，
    # 再把原 patch 拼出来可视化（需要在训练时保存每个单词对应的原始 patch）
```

## OpenCV BOW 模块源码位置

- `modules/features2d/src/bagofwords.cpp`：
  - `BOWKMeansTrainer::cluster`：K-Means 聚类实现
  - `BOWImgDescriptorExtractor::compute`：给定关键点和词典，算直方图
- 关键点检测和描述子计算复用 `SIFT/SURF/ORB` 等实现
- 匹配部分复用 `BFMatcher/FlannBasedMatcher`
