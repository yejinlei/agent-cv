# 调参技巧：BRISK 二进制鲁棒不变可伸缩关键点

## 五字口诀

****角要快、圈要圆、长定方向短拼串****

## 调参顺序（按这个顺序调，少走弯路）

1. **先调 thresh**：控制点的数量和质量平衡
2. **再调 octaves**：决定尺度覆盖范围（3–4）
3. **配 BFMatcher(NORM_HAMMING, crossCheck=True)** 做初筛
4. **加 ratio test** 清掉误匹配
5. **用 RANSAC**（findHomography / findFundamentalMat）做几何校验

## 与其他算法的搭配组合

- **BRISK + Hamming BF + RANSAC**：SLAM/图像拼接的标配前端
- **BRISK + BoVW**：图像检索（词袋），描述子 64 字节，存词袋直方图时注意开销
- **BRISK + GMS**：Grid-based Motion Statistics 快速剔除误匹配
- **BRISK + 光流**：先用 BRISK 找初始点，再用 LK 光流做连续帧跟踪，比逐帧重提快

## 调优 Checklist

- [ ] 图像已做必要的预处理（灰度化 + CLAHE 弱增强（可选））
- [ ] 核心参数已按场景粗调到合理区间
- [ ] 输出结果做了必要的后处理（RANSAC 几何校验）
- [ ] 速度/精度做了 benchmark

<!-- AUTO-EXTENSION -->

## 🎯 参数建议

- `thresh`（AGAST 阈值）：默认 30；低一点关键点多（适合匹配稀疏场景），高一点关键点少但质量高；
- `octaves`：默认 4；大尺度变化（无人机拍摄）设 6~8；
- `patternScale`：默认 1.0；图像分辨率高（>1080p）可设到 1.2~1.5 让采样更大范围。

**BRISK 描述子 512 bit**，匹配必须用 **HAMMING 距离**，BFMatcher 或 FlannBasedMatcher(LSH) 都可以。
