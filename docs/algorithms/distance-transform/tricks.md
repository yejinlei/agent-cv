# 调参技巧：距离变换

## 五字口诀

****两遍扫、邻居小、分正反、L2 圆****

## 调参顺序（按这个顺序调，少走弯路）

1. **二值化必须干净**：先开运算去噪
2. **distanceType=DIST_L2, maskSize=5** 作为默认
3. 输出后做 normalize 到 [0,255] 再可视化
4. 做种子提取：在 dist 上再做一次阈值化（0.7*max）+ dilate 得确定前景
5. 做骨架：取 localMax 或直接 distanceTransform→skeletonize

## 与其他算法的搭配组合

- **距离变换 + 阈值 → 分水岭种子**：是分水岭分割的标准前处理
- **距离变换 + 骨架化**：提取血管/文字/字符笔画骨架
- **距离变换 + Chamfer Matching**：二值图形状匹配
- **距离变换 + 最大极值 → 最大内切圆**：检测圆形物体中心

## 调优 Checklist

- [ ] 图像已做必要的预处理（二值化 + 开运算去噪）
- [ ] 核心参数已按场景粗调到合理区间
- [ ] 输出结果做了必要的后处理（normalize 归一化到 [0,1] 或 [0,255]）
- [ ] 速度/精度做了 benchmark

<!-- AUTO-EXTENSION -->

## 🎯 典型三步用法

```python
# 1. 二值化（前景是 255）
_, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
# 2. 距离变换，归一化到 0~1
dist = cv2.distanceTransform(bw, cv2.DIST_L2, 5)
cv2.normalize(dist, dist, 0, 1.0, cv2.NORM_MINMAX)
# 3. 再阈值化——得到确定前景（峰值区域）
_, sure_fg = cv2.threshold(dist, 0.5*dist.max(), 255, 0)
```

这正是 Watershed 分割里"找确定前景"的标准套路——距离变换在 Watershed 里几乎是必用前处理。
