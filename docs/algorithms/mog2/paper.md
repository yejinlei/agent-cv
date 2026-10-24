# 📄 原始论文

> **Zivkovic, Z. (2004).** *Improved adaptive Gaussian mixture model for background subtraction.* ICPR 2004.

## 论文一句话主张

> 「每个像素的高斯分量个数 K 不应该是固定的（如 Stauffer-Grimson 1999 固定 K=3~5），而应该根据该像素位置的动态变化**自动选择**——变化少的地方用 1 个就够，树叶摆动、水波的地方才需要多个。」

## 相对于 Stauffer-Grimson 1999 的改进

1. **K 自适应**：自动扔掉权重低的高斯，省内存省计算。
2. **学习率 α 在线估计**：不用手调，初入场景的"鬼影"消失更快。
3. **先验置信度**：加入了 Dirichlet 先验，对高斯权重做正则，更稳。
4. 这就是 OpenCV 里 `BackgroundSubtractorMOG2` 的直接实现，工业上用了 20 年。

## 更早 / 更新的亲戚

| 方法 | 年份 | 特点 |
| --- | --- | --- |
| Running Average（帧差） | 1980s | 简单 $B = (1-\alpha)B + \alpha I$，单高斯 |
| Stauffer-Grimson GMM | 1999 | K=3~5 固定 |
| **Zivkovic MOG2** | 2004 | **K 自适应 + 阴影检测**，OpenCV 默认 |
| KNN 背景 | 2010s | `cv2.createBackgroundSubtractorKNN()`，非参数核密度 |
| ViBe | 2011 | 随机采样，鬼影消失极快，但 OpenCV 没有内置 |
