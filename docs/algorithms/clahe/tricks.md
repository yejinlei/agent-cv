# 调参技巧：CLAHE 限制对比度自适应直方图均衡

## 五字口诀

****分块均、Clip 限、插值拼、只做 L****

## 调参顺序（按这个顺序调，少走弯路）

1. 转单通道（或 LAB 的 L 通道）
2. **clipLimit=2.0、tileGridSize=(8,8)** 作为起点
3. 观察暗部噪声和亮部对比度，clipLimit 1.5–4.0 调整
4. 需要更强局部增强时 tileGridSize 改 (4,4)，弱一些用 (16,16)
5. 事后配合 gamma/饱和度调整

## 与其他算法的搭配组合

- **CLAHE + 高斯去噪**：低照度增强标配
- **CLAHE + Canny**：边缘检测前增强，暗部边缘出得来
- **CLAHE + 人脸检测**：Haar/LBP 人脸检测前做，逆光下召回率提升显著
- **CLAHE + OCR（Tesseract）**：低质量文档扫描必做
- **CLAHE + LBP/HOG**：特征提取前做光照归一化

## 调优 Checklist

- [ ] 图像已做必要的预处理（灰度化（或转 LAB/L 通道））
- [ ] 核心参数已按场景粗调到合理区间
- [ ] 输出结果做了必要的后处理（gamma/饱和度微调（可选））
- [ ] 速度/精度做了 benchmark

<!-- AUTO-EXTENSION -->

## 🎯 参数速查卡

| 场景 | clipLimit | tileGridSize | 备注 |
| --- | --- | --- | --- |
| 通用 | 2.0 | (8,8) | 论文默认值 |
| 人脸（自然） | 2.0 | (8,8) | 先做再上 LBP/HOG |
| 医学 X 光 | 3.0 | (8,8) | 肺纹理要明显 |
| 红外热成像 | 4.0 | (16,16) | 信噪比低，大 tile |
| 文档扫描 | 1.5 | (8,8) | 文字要黑，纸要白 |
| 弱光夜景增强 | 3.0~4.0 | (8,8) | 先去噪再 CLAHE |

### 必知 5 条

1. **必须在 Lab 空间的 L 通道做**：`cv2.cvtColor(img, COLOR_BGR2LAB)`，拆分 L/a/b，只对 L 做 CLAHE，再合回去；直接对 RGB 做颜色会飘；
2. **clipLimit 不是越大越好**：>4.0 基本等于没裁剪，噪声暴增；
3. **tileGridSize 8×8 是甜点**：4×4 过度增强，16×16 退化成全局 HE；
4. **CLAHE 永远放在去噪之后、特征提取之前**；
5. **做匹配任务时**（光流、特征匹配、立体匹配），CLAHE 是提升低光匹配率性价比最高的一步。

### 三行黄金代码

```python
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
l,a,b = cv2.split(lab)
l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(l)
result = cv2.cvtColor(cv2.merge([l,a,b]), cv2.COLOR_LAB2BGR)
```
