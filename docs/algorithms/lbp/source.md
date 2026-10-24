# 💻 源码实现

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
