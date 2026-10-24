# 📄 原始论文

> **Henriques, J. F., Caseiro, R., Martins, P., & Batista, J. (2015).**
> *High-speed tracking with kernelized correlation filters.* IEEE TPAMI 2015.

## 论文一句话主张

> 「传统检测式跟踪（TLD、Struck）采样大量候选框是冗余的——所有候选框其实都是原始样本的循环移位。**利用循环矩阵在傅里叶域可对角化**的性质，可以把训练和检测都变成一次元素乘，速度提升几个数量级。」

## 核心贡献

1. 指出"滑动窗口的所有候选 patch"在频域里是循环矩阵，一 FFT 就全部搞定；
2. 引入核技巧（高斯核/多项式核），把线性相关滤波升级到非线性；
3. 把 CSK 的单通道灰度升级到多通道 HOG，精度显著提升同时速度不掉；
4. 开源代码后被 OpenCV 直接收录，成为默认推荐跟踪器。

## 衍生算法

- **DSST** (Danelljan 2014)：KCF + 独立的尺度滤波器，解决 KCF 不抗尺度的问题。
- **fDSST**：DSST 的快速版，用 PCA 降维特征。
- **SRDCF / CSR-DCF**：加空间正则/可靠性，抑制边缘效应。
- **CSRT / CSR-DCF**（OpenCV 4.0+ 默认推荐）：通道+空间可靠性，精度最高但慢。
