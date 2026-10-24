# 对极几何实战与踩坑

> 对极几何的坑非常「隐性」——代码跑通、数值出来，但结果是错的。这一页把最常见的 10 个坑一次性列清。

## 坑 1：不做归一化直接八点法 ⭐⭐⭐⭐⭐

```python
# ❌ 直接用原始像素坐标构造 A 矩阵
A = construct_A(pts1_pixel, pts2_pixel)   # 坐标量级数百上千

# ✅ 先 Hartley 归一化
p1n, T1 = normalize_points(pts1)
p2n, T2 = normalize_points(pts2)
```

**症状**：解出的 $F$ 完全不合理（对极线乱飞），内点率极低。

**原因**：9 个元素相乘到 $10^{12}$ 量级，矩阵条件数爆炸。

**注意**：`cv2.findFundamentalMat` **内部已经做了归一化**，所以用 OpenCV 不会踩这个坑——但你自己手写时必须记得。

**本体实体**：`pain-epipolar-no-normalize`

## 坑 2：忘了强制秩 2 ⭐⭐⭐⭐

```python
# ❌ SVD 解出 F 就直接用，没做秩约束
_, _, Vt = np.linalg.svd(A)
F = Vt[-1].reshape(3, 3)          # 这一步的 F 通常秩为 3

# ✅ 再 SVD 一次，最小奇异值置 0
U, S, Vt2 = np.linalg.svd(F)
S[-1] = 0
F = U @ np.diag(S) @ Vt2
```

**症状**：算出的对极线不交于同一个对极点，$Fe = 0$ 不成立。

**原因**：$F$ 理论上秩为 2（因为 $F = [\mathbf{t}]_\times R$，反对称矩阵秩 2），数值解得秩 3。

## 坑 3：所有点共面，还在求 F ⭐⭐⭐⭐⭐

```python
# ❌ 拍了一面墙（所有点共面），求 F —— 有无穷多解
F, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC, 1.0)
```

**症状**：$F$ 极度不稳定，换个随机种子结果就变。

**根因**：平面场景下 $F$ 退化，应该用单应 $H$。

**解决**：

```python
H, mask_H = cv2.findHomography(pts1, pts2, cv2.RANSAC, 3.0)
F, mask_F = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC, 1.0, 0.999)
if mask_H.mean() > 0.7:
    print("平面场景 → 用 H")
else:
    print("有深度变化 → 用 F")
```

**本体实体**：`pain-epipolar-planar`

## 坑 4：纯旋转运动 ⭐⭐⭐⭐

```python
# ❌ 相机原地转头（平移约 0）→ 无法恢复 t
```

**症状**：`recoverPose` 出来的 $t$ 数值极小、方向随机。

**根因**：**纯旋转时基线为 0**，对极几何退化。

**解决**：用单应 $H$；或拍摄时**确保有平移运动**。

## 坑 5：RANSAC 阈值理解错 ⭐⭐⭐⭐

```python
# ❌ 把 findFundamentalMat 的阈值当成"重投影误差"来设
F, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC, ransacReprojThreshold=10.0)

# ✅ 它是"点到对极线的距离"（像素），通常 0.5~2.0
F, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC, 1.0, 0.999)
```

| 阈值 | 效果 |
|---|---|
| 0.5 px | 严格，内点少 |
| **1.0 px** | **推荐** |
| 3.0 px | 宽松，内点多但可能混入外点 |

**关键**：`findFundamentalMat` 的阈值是**到极线的距离**，而 `findHomography` 的阈值是**重投影误差**——不是一回事。

**本体实体**：`pain-epipolar-threshold`

## 坑 6：匹配点分布不均 ⭐⭐⭐

```python
# ❌ 匹配点全挤在图像一角 → F 估计偏向局部
```

**症状**：远离匹配区的地方，对极线预测完全错误。

**解决**：

- 用 **RANSAC 前先做空间均匀化**，或
- 在整幅图上**分块取点**，保证点覆盖全图

## 坑 7：三角化出现负深度 ⭐⭐⭐⭐

```python
# ❌ 三角化得到一半的点 Z < 0（在相机后面）
```

**根因**：从 $E$ 分解的 4 组 $(R,t)$ 里**选错了**。

**解决**：用 `cv2.recoverPose`（自动选正深度解），或手动对 4 组都三角化、选深度全正的那组。

## 坑 8：不剔除三角化夹角过小的点 ⭐⭐⭐⭐

```python
# ❌ 所有三角化点都保留 —— 远距离点深度全不可信
pts3d = triangulate_all(pts1, pts2, R, t)

# ✅ 剔除夹角 < 2° 的点
keep = filter_by_triangulation_angle(pts3d, R, t, min_angle_deg=2.0)
```

**为什么**：深度误差 $\propto Z^2/(fB)$，夹角越小误差越大。

## 坑 9：F 与 E 混用 ⭐⭐⭐⭐

```python
# ❌ 用 findEssentialMat 求 E，却拿像素坐标直接代入 x'ᵀEx = 0
# ✅ E 用的是「归一化坐标」，像素坐标必须先乘 K⁻¹
pts1_norm = cv2.undistortPoints(pts1.reshape(-1,1,2), K, None).reshape(-1,2)
```

**混淆点**：

| 矩阵 | 坐标 |
|---|---|
| F | 像素坐标 |
| E | 归一化坐标（$K^{-1}p$） |

## 坑 10：以为重建完就结束 ⭐⭐⭐

```python
# ❌ 三角化出点云就交差
# ✅ 后面还有：BA 优化、外点剔除、尺度对齐、稠密重建
```

**正确的重建链条**：

```
匹配 → F/E → 位姿 → 三角化 → 夹角过滤 → 光束法平差（BA）→ 多视图扩展 → 稠密重建
```

## 踩坑速查表

| # | 症状 | 原因 | 修法 |
|---|---|---|---|
| 1 | F 完全不对 | 未归一化 | Hartley 归一化（OpenCV 内置） |
| 2 | 对极线不共点 | 未强制秩 2 | SVD 置零最小奇异值 |
| 3 | F 不稳定 | 点共面 | 改用 H |
| 4 | t 随机 | 纯旋转 | 用 H / 加平移 |
| 5 | 内点率异常 | 阈值理解错 | 阈值=极线距离，用 1.0 |
| 6 | 局部预测错 | 点分布不均 | 分块取点 |
| 7 | 负深度 | 解选错 | recoverPose / 选正深度 |
| 8 | 远处点乱 | 未过滤夹角 | 剔除 < 2° |
| 9 | E 算不对 | 坐标类型错 | 用归一化坐标 |
| 10 | 重建粗糙 | 缺 BA | 接光束法平差 |

## 诊断 Checklist

- [ ] 场景是**平面**吗？是就改 **H**？
- [ ] 相机有**平移**吗？（纯旋转会退化）
- [ ] 匹配点**分布均匀**吗？
- [ ] 用的是 **F（像素）** 还是 **E（归一化）**？坐标类型对吗？
- [ ] RANSAC 阈值设成 **极线距离 1.0** 了吗？
- [ ] 三角化后做过**深度为正**与**夹角过滤**吗？
- [ ] 接**光束法平差**了吗？

[← 上一篇：源码走读](./source) · [下一篇：调参技巧 →](./tricks)
