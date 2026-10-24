# 调参技巧：AKAZE 加速 KAZE 特征

## 五字口诀

****非线性、FED 快、Hessian 顶、MLDB 比****

## 调参顺序（按这个顺序调，少走弯路）

1. **threshold 先设 0.001**，根据出点数再调
2. **diffusivity 默认 PM_G2**
3. **descriptor_type 用 MLDB**（二进制，匹配快）
4. **BFMatcher(NORM_HAMMING) + ratio test 0.75**
5. 速度要求高时 descriptor_size=256、UPRIGHT 版本

## 与其他算法的搭配组合

- **AKAZE + BF-Hamming + RANSAC**：高精度图像拼接首选
- **AKAZE + GMS matcher**：实时网格统计匹配，鲁棒快速
- **AKAZE + BoVW**：免费高重复率检索
- **AKAZE + 单应矩阵 + 图像拼接**：航拍/文档扫描的经典 pipeline

## 调优 Checklist

- [ ] 图像已做必要的预处理（灰度化 + 轻微高斯去噪（sigma=1））
- [ ] 核心参数已按场景粗调到合理区间
- [ ] 输出结果做了必要的后处理（ratio test + RANSAC）
- [ ] 速度/精度做了 benchmark
