# 🏗 算法流程

```mermaid
flowchart TD
  S[输入灰度图] --> PRE{彩色?}
  PRE --是--> GRAY[转灰度 + 可选直方图均衡]
  PRE --否--> CIRC
  GRAY --> CIRC["对每个像素取圆形邻域 (P=8,R=1)<br/>双线性插值得 P 个邻居"]
  CIRC --> BIN[邻居-中心阈值 → P 位二进制]
  BIN --> DEC[映射为 0~P²-1 的十进制码]
  DEC --> UNI{Uniform 模式?}
  UNI --跳变≤2--> BINID[映射到 0~57]
  UNI --否--> BIN58["归到 58 号「非均匀」桶"]
  BINID --> CELL[图像切成 K×K 个 cell]
  BIN58 --> CELL
  CELL --> HIS[每个 cell 统计 59 维 LBP 直方图]
  HIS --> NORM[L2/Hellinger 归一化]
  NORM --> CONCAT[所有 cell 直方图拼起来]
  CONCAT --> FEAT[输出全局纹理特征向量]
```

## LBP 人脸识别的经典设置

- 图像对齐 + 裁剪到 128×128
- 分成 **8×8 = 64 个 cell**（每 cell 16×16 像素）
- 每个 cell 59 维 Uniform LBP 直方图
- 总特征维度 = 64 × 59 = **3776 维**
- 卡方距离 / 直方图交做匹配，或送 SVM 训练多类分类器

这就是 2004 年 Ahonen LBP-Face 在 FERET 库上刷 SOTA 的完整配置。诺基亚 N95 的人脸识别用的就是它——在 ARM9 上 200ms 跑一帧。

## 多尺度 LBP

为了捕捉不同尺度的纹理，通常同时算 (P=8,R=1)、(P=16,R=2)、(P=24,R=3) 三个尺度，把它们的直方图拼起来。这样细纹理、中纹理、粗纹理都覆盖到。
