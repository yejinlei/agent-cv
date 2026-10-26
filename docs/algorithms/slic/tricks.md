# SLIC 超像素 · 调参口诀

<AlgorithmCard
  name="SLIC 超像素"
  enName="Simple Linear Iterative Clustering"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="2010"
  author="R. Achanta et al."
  paper="—"
  level="mid"
  tagline="把 200 万像素切成 200 个颜色一致、大小均匀的小方块，后续处理快 1000 倍"
  analogy="把一张大图当大蛋糕，先按网格切小方块，然后每块根据颜色微调，最后得到一堆大小差不多、颜色统一的小块"
  scene="分割预处理、显著性检测、光流加速、弱监督标注、深度估计超像素化、风格迁移"
  :pros='["速度极快", "超像素紧凑均匀", "内存小", "仅 2 参数", "边界贴合好"]'
  :cons='["必须指定超像素数", "OpenCV 主分支没有", "紧凑度 m 影响边界", "不是分割终点"]'
/>

## SLIC 超像素 调参口诀

```
超像素两百个起头，按目标复杂度往上加；
紧凑度 m 十是默认，要贴边减小要方正加；
sigma 一高斯平滑先，抗噪声；
OpenCV 主模块没有它，skimage 或 contrib 才是家；
距离公式色加空间，m 除以 S 来加权；
局部搜索两倍 S，线性复杂度飞快跑。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| n_segments | 期望超像素数 | **200** | 细 | 粗 |
| compactness (m) | 紧凑度 | **10** | 方正 | 贴边界 |
| sigma | 预处理高斯 sigma | **1** | 平滑 | 保留细节 |
| max_iter | 迭代次数 | **10** | 精确 | 快 |

## 实战技巧

### SLIC 后接其他算法

```python
# 以超像素为单元做后续处理
sp_vals = [image[segments==i].mean(0) for i in range(segments.max()+1)]
# K-Means 在超像素上做 → 最终分割，速度快 100 倍
```

### 边界可视化

`skimage.segmentation.mark_boundaries` 能直接画出超像素边缘，适合 debug。

### enforce_connectivity

skimage 有 `enforce_connectivity=True` 参数（默认），自动把过小孤立区域合并到邻居。

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| skimage SLIC (640×480, K=200) | ~50 ms | CPU |
| opencv-contrib SLIC | ~10 ms | CPU C++ 优化 |

## 选型建议

**适用场景**：分割预处理、显著性检测、光流加速、弱监督标注、深度估计超像素化、风格迁移

**不适用场景**：必须指定超像素数、OpenCV 主分支没有、紧凑度 m 影响边界

<!-- AUTO-EXTENSION-2 -->

## 🎯 参数

- `region_size`（S）：期望超像素边长，典型 10~50 像素；
- `ruler`（m）：空间距离权重，典型 10~30；大了超像素更方整但贴边差，小了贴边但形状乱。

```python
slic = cv2.ximgproc.createSuperpixelSLIC(img, region_size=20, ruler=20.0)
slic.iterate(10)
slic.enforceLabelConnectivity(50)
labels = slic.getLabels()
```
