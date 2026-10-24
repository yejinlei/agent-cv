---
outline: deep
---

# 第 2 页 · 论文溯源

## 论文名片

| 项目 | 内容 |
|------|------|
| 标题 | **Bundle Adjustment — A Modern Synthesis** |
| 作者 | Photogrammetry 领域起源 / Triggs et al. 2000 总结 |
| 年份 | 1958 |
| 发表 | Vision Algorithms: Theory and Practice, 2000（Triggs 等综述） |
| 原文 | [https://www.cs.cornell.edu/courses/cs4670/2015fa/lectures/lec25_ba.pdf](https://www.cs.cornell.edu/courses/cs4670/2015fa/lectures/lec25_ba.pdf) |
| 一句话贡献 | 系统总结光束法平差的现代实现，阐明其目标函数、稀疏结构与 LM 优化框架。 |

## 1. 当时的问题

SfM 由多步估计串成，每步误差累积导致最终模型不一致（漂移、错位）。如何联合优化全部参数使整体最优，且计算上可行，是长期难题。

## 2. 核心思想

把所有待估参数（相机位姿、3D 点、内参）凑成一个巨大的最小二乘问题，目标是让每个 3D 点投回每张照片的位置尽量贴近观测像素。用 Levenberg-Marquardt 迭代求解，并利用「点与相机之间稀疏相连」的结构（Schur 补）大幅降维。

```mermaid
flowchart LR
  A["初始位姿+点云"] --> B["计算重投影误差"]
  B --> C["LM迭代更新"]
  C --> D{"收敛?"}
  D -- 否 --> B
  D -- 是 --> E["优化后模型"]
```

## 3. 关键贡献

- 给出 BA 的**统一数学表述**与 LM 求解框架
- 阐明**稀疏雅可比与 Schur 补**带来的计算可行性
- 引入鲁棒损失函数处理外点
- 成为 SfM/摄影测量现代实现的参考规范

## 4. 核心公式（看懂思路即可）

min Σ_i Σ_j ρ( ‖ x_ij − π(K_i, R_i, t_i, X_j) ‖² )，其中 x_ij 为观测像素、π 为投影函数、X_j 为 3D 点、ρ 为鲁棒损失（如 Huber）。

## 5. 实验结果

在标准 SfM 数据集上，BA 可把重投影误差从数像素降到亚像素级，显著提升重建精度与全局一致性。

## 6. 局限与争议

计算量与内存开销大；依赖良好初值；对误匹配敏感；需专门优化库与稀疏结构利用。

## 7. 历史影响

成为所有 SfM（COLMAP/Bundler）与 SLAM（ORB-SLAM/g2o/Ceres）系统的标配后端，是「传统三维重建精度天花板」的技术根基。

## 8. 一句话总结

> 把「所有相机 + 所有点」一起最小二乘，用稀疏结构撑起计算可行性——这是三维重建精度的护城河。
