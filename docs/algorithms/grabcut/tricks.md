# GrabCut 抠图 · 调参口诀

<AlgorithmCard
  name="GrabCut 抠图"
  enName="GrabCut Interactive Foreground Extraction"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="2004"
  author="C. Rother / V. Kolmogorov / A. Blake"
  paper="—"
  level="mid"
  tagline="画一个框就能把目标抠出来，GMM+GraphCut 迭代优化，Photoshop 快速选择的灵魂"
  analogy="你用笔在目标周围画个圈，对算法说「圈外肯定是背景，圈内有前景也有背景」。GrabCut 就像一个聪明的学徒，先猜哪些颜色像前景，再用 GraphCut 切一刀，反复 5 次抠得干干净净"
  scene="照片抠图换背景、数据集快速标注、医学影像交互式分割、人像美颜前景提取"
  :pros='["用户只需画一个框", "边缘细节比 GraphCut 好", "支持笔刷精修", "GMM 建模多峰颜色分布"]'
  :cons='["高分辨率慢", "前景背景颜色接近时效果差", "矩形外永远是背景", "边缘毛发需 matting"]'
/>

## GrabCut 抠图 调参口诀

```
框要画大一点点，小了目标边缘永远救不回；
bgd/fgd 形状 1 行 65 列，类型必须 float64；
迭代五次是默认，高精度加到十次也还行；
大图像先缩到四分之一，粗分割再上采样精修；
颜色相近加手动笔刷，rect 不行换 mask；
头发丝别指望 GrabCut，close-form matting 才是王。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| iterCount | 迭代次数 | **5** | 更精确但慢 | 快但粗糙 |
| rect | 初始框(x,y,w,h) | **目标大 10%** | — | — |
| mode | 初始化模式 | **GC_INIT_WITH_RECT** | — | — |

## 实战技巧

### 先粗后精加速

```python
small = cv2.resize(img, None, fx=0.25, fy=0.25)
small_rect = (rect[0]//4, rect[1]//4, rect[2]//4, rect[3]//4)
cv2.grabCut(small, mask_s, small_rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
mask = cv2.resize(mask_s, (w, h), interpolation=cv2.INTER_NEAREST)
cv2.grabCut(img, mask, None, bgd, fgd, 2, cv2.GC_INIT_WITH_MASK)
```

### 手动笔刷精修

```python
# 用户在 UI 画红线=前景，蓝线=背景
mask[user_fg_stroke > 0] = cv2.GC_FGD
mask[user_bg_stroke > 0] = cv2.GC_BGD
cv2.grabCut(img, mask, None, bgd, fgd, 3, cv2.GC_INIT_WITH_MASK)
```

### 边缘柔化（抗锯齿）

```python
# GrabCut 二值 mask 边缘硬，用导向滤波柔化
alpha = cv2.ximgproc.guidedFilter(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), fg_mask, 8, 1e-3)
```

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| GrabCut iters=5 (320×240) | ~150 ms | CPU |
| GrabCut iters=5 (640×480) | ~600 ms | CPU |
| GrabCut iters=5 (1920×1080) | ~5 s | CPU，需降采样优化 |

## 选型建议

**适用场景**：照片抠图换背景、数据集快速标注、医学影像交互式分割、人像美颜前景提取

**不适用场景**：高分辨率慢、前景背景颜色接近时效果差、矩形外永远是背景

