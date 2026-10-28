---
title: Hessian 矩阵（二阶导数） · 算子词典
outline: deep
---

# 🟣 Hessian 矩阵（二阶导数）（Hessian Matrix）

> **算子 ID**：`op-hessian` ｜ **类别**：statistical

「看一个地方是凸的还是凹的、还是像马鞍」： 二阶导数告诉你「坡度在往哪个方向变化」。 如果两个方向都在变陡（都是正的），这里是「坑底」； 两个方向都在变缓（都是负的），这里是「山顶」； 一正一负，就是「马鞍」。 在图像里，「山顶」和「坑底」就是很稳定的特征点（斑点）， 而马鞍对应边缘——所以要避开它。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="150" viewBox="0 0 380 150" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="150" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">Hessian 矩阵：看曲面的凹凸</text>
  <g transform="translate(50,40)">
    <path d="M0,80 Q40,10 80,80" fill="none" stroke="#e87a4a" stroke-width="2"/>
    <circle cx="40" cy="10" r="4" fill="#d44"/>
    <text x="10" y="105" font-size="12" fill="#e87a4a">极小值(斑点)</text>
  </g>
  <g transform="translate(160,40)">
    <path d="M0,20 Q40,90 80,20" fill="none" stroke="#4a90e2" stroke-width="2"/>
    <circle cx="40" cy="90" r="4" fill="#4a90e2"/>
    <text x="10" y="115" font-size="12" fill="#4a90e2">极大值</text>
  </g>
  <g transform="translate(270,40)">
    <path d="M0,80 Q40,45 80,10 Q40,90 80,80" fill="none" stroke="#9b59b6" stroke-width="2"/>
    <circle cx="40" cy="45" r="4" fill="#9b59b6"/>
    <text x="10" y="115" font-size="12" fill="#9b59b6">马鞍(边)</text>
  </g>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=harris" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
H = [[Ixx, Ixy], [Ixy, Iyy]]，det(H) = Ixx·Iyy - Ixy²
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `σ` | 求导前的高斯平滑尺度 | 1.0–2.0 | 越大越稳定但越模糊 |
| `det(H)` | 行列式 | 越大越可能是斑点中心 | det(H) 大 = 两个方向的曲率都大 = 好特征点 |



## OpenCV 调用

```python
import cv2
# → cv2.cornerHarris（近似 Hessian 的响应）
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览

- **时间复杂度**：O(n · k²)
- **核可分离**：否
- **可就地计算**：否
- **抗噪能力**：🔴 低
- **边缘保持**：是

## 被哪些算法使用

- [→ algo-sift](/algorithms/sift/)
- [→ algo-surf](/branches/feature-detection/blobs#surf)


## 典型使用场景

- 斑点检测（斑点 = det(H) 极大值）
- 角点检测（Harris 用类似思路）
- SURF 用 Hessian 行列式做尺度空间检测
- 剔除边缘响应点（在 SIFT 中判断是否落在边缘）


## 常见踩坑 🕳️

- ⚠️ 二阶导数对噪声极其敏感，必须先高斯平滑
- ⚠️ 只取 det(H) 会同时在斑点中心和边缘都响应，需要额外约束


---

**上一级**：[← 算子词典总览](/operators/)
