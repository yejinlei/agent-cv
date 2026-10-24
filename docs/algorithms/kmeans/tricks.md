# K-Means 颜色聚类 · 调参口诀

<AlgorithmCard
  name="K-Means 颜色聚类"
  enName="K-Means Clustering"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="1967"
  author="Stuart Lloyd / James MacQueen"
  paper="—"
  level="basic"
  tagline="把所有像素按颜色分成 K 堆，每堆一个代表色，图像立刻变卡通"
  analogy="把一盒彩笔按颜色分成 K 堆：先随机挑 K 支笔当组长，其他笔投奔最近的组长；每堆重新选平均色当新组长；反复到组长不再变"
  scene="颜色量化、海报风格化、肤色区域分割、语义分割前处理、调色板生成"
  :pros='["思想极简单", "速度快", "OpenCV/sklearn 一行调用", "适用范围广"]'
  :cons='["必须指定 K", "只看颜色不看位置", "对初始值敏感", "对噪声敏感"]'
/>

## K-Means 颜色聚类 调参口诀

```
K 值八是常用点，海报效果四到八；
数据必须 float32，uint8 直接报错；
初始化用 kmeans++，随机初始化常炸锅；
只看颜色碎一地，加上 XY 分块聚；
迭代十次足够收敛，精度设 1.0 不算差；
要固定结果设随机种子，setRNGSeed 传 42。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| K | 聚类数 | **8** | 颜色多样 | 块状风格化 |
| max_iter | 最大迭代 | **10** | 更精确 | 快 |
| epsilon | 收敛精度 | **1.0** | 精确 | 快 |
| attempts | 尝试次数（选最佳） | **10** | 更稳 | 快 |

## 实战技巧

### K 的选择（肘部法）

```python
inertia = []
for K in range(2,16):
    r,l,c = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
    inertia.append(r)  # compactness
# 画 inertia vs K，找拐点
```

### 生成调色板

```python
# center 就是 K 个调色板色（BGR）
palette = center.reshape(1, K, 3)
cv2.imwrite('palette.jpg', cv2.resize(palette, (K*50, 50), interpolation=cv2.INTER_NEAREST))
```

### Lab 空间聚类更符合人眼

在 Lab 颜色空间（而非 BGR）做 K-Means 聚类，结果更符合人类感知：
```python
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
Z = lab.reshape(-1,3).astype(np.float32)
```

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| cv2.kmeans K=8 (640×480) | ~50 ms | CPU |
| 5 维 (K=8) | ~150 ms | CPU |
| kmeans++ 初始化开销 | < 1 ms | 几乎可忽略 |

## 选型建议

**适用场景**：颜色量化、海报风格化、肤色区域分割、语义分割前处理、调色板生成

**不适用场景**：必须指定 K、只看颜色不看位置、对初始值敏感

