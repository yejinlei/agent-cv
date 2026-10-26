# ⚙ 调参口诀

## 口诀

> **d 小快、σ 配平；色空同大、CIELAB 先行；椒盐先中值、磨皮半高保。**

## 常用配方速查表

| 场景 | d | sigmaColor | sigmaSpace | 备注 |
| --- | --- | --- | --- | --- |
| 实时去噪 | 5 | 25 | 25 | 视频 30fps 可跑 |
| 人像轻磨皮 | 9 | 50 | 50 | 最常用 |
| 人像强磨皮 | 15 | 75 | 75 | 磨掉色斑 |
| 卡通化滤镜 | -1 | 150 | 150 | 大色块感 |
| HDR base 层 | -1 | 30 | 100 | 配合 detail 增强 |
| 深度图后处理 | 7 | 20 | 20 | 小核填平视差空洞 |

## 5 条黄金法则

1. **sigmaColor 与 sigmaSpace 尽量相等**：数值一起调，不要一个大一个小，会出现奇怪的方向性模糊。
2. **d 用 -1 让 OpenCV 算**：d 和 sigmaSpace 不匹配会退化。
3. **彩色图一律 LAB 空间做**：避免色边。
4. **要保留纹理就回注 detail**：`out = blur + k*(img-blur), k∈[0.2,0.6]`。
5. **追求极致速度用引导滤波**：`cv2.ximgproc.guidedFilter`，O(N)，效果几乎一样。

## 替代物的选择开关

- **要快、大核** → 引导滤波 Guided Filter
- **要结构导向** → 双边网格 / Domain Transform
- **要完全保边** → 非局部均值 NLM（`cv2.fastNlMeansDenoisingColored`）
- **要磨皮到卡通** → 双边 + 边缘检测叠加描线

<!-- AUTO-EXTENSION -->

## 🎯 参数速查卡

| 场景 | d | σColor | σSpace | 备注 |
| --- | --- | --- | --- | --- |
| 人脸磨皮（轻） | -1 | 30 | 30 | 几乎看不出来 |
| 人脸磨皮（中） | -1 | 50 | 50 | 美颜 App 典型值 |
| 人脸磨皮（强） | -1 | 75 | 75 | 卡通化效果 |
| 去 JPEG 块效应 | -1 | 20 | 20 | 弱保边平滑 |
| HDR 色调映射 | -1 | 20 | 100 | 大半径小色差 |
| 卡通化（Cartoon） | -1 | 100 | 100 | 迭代 3~5 次后再 edge |

### 美颜典型管线（3 行代码效果拉满）

```python
# 1. 磨皮（双边）
smooth = cv2.bilateralFilter(img, -1, 50, 50)
# 2. 细节增强（原图 - 磨皮 = 细节，加回去）
detail = cv2.addWeighted(img, 1.5, smooth, -0.5, 0)
# 3. 美白（简单 gamma）
result = np.clip(np.power(detail/255., 0.85)*255, 0, 255).astype('uint8')
```
