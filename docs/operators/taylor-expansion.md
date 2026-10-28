---
title: 泰勒展开（亚像素定位） · 算子词典
outline: deep
---

# 🟣 泰勒展开（亚像素定位）（Taylor Expansion for Sub-pixel Refinement）

> **算子 ID**：`op-taylor-expansion` ｜ **类别**：statistical

「用抛物线找谷底」：你在一格一格的地图上找到了「附近最矮的地方」， 但真正的最低点可能在格子中间。怎么办？ 用多项式把那几个格子的高度拟合成一条平滑曲线，再求它的最低点在哪。 这样就能得到比「一个格子」精确得多的位置——精确到零点几个格子。 在图像里，这意味着特征点位置可以精确到亚像素。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="130" viewBox="0 0 380 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="130" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">泰勒展开：用抛物线逼近谷底</text>
  <path d="M40,100 Q120,30 200,90 Q280,110 340,80" fill="none" stroke="#ccc" stroke-width="2"/>
  <circle cx="200" cy="90" r="4" fill="#666"/>
  <path d="M160,60 Q200,90 240,60" fill="none" stroke="#4a90e2" stroke-width="2.5"/>
  <circle cx="200" cy="90" r="4" fill="#d44"/>
  <circle cx="215" cy="78" r="4" fill="#2a9d4a"/>
  <text x="50" y="120" font-size="12" fill="#666">真实曲线(灰色)</text>
  <text x="160" y="120" font-size="12" fill="#4a90e2">泰勒二次近似</text>
  <text x="250" y="55" font-size="12" fill="#d44">像素级</text>
  <text x="225" y="75" font-size="12" fill="#2a9d4a">亚像素精度</text>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=gauss" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
D(x) ≈ D + (∂D/∂x)ᵀx + ½xᵀ(∂²D/∂x²)x，极值点 x̂ = -(∂²D/∂x²)⁻¹(∂D/∂x)
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `邻域` | 拟合用的邻域大小 | 3×3×3（空间 + 尺度） | SIFT 在 DoG 金字塔中用它判断极值 |
| `对比度阈值` | 剔除低对比度点的阈值 | 0.03（SIFT 默认） | 越大剔除越多，越稳但可能漏 |



## OpenCV 调用

```python
import cv2
# → （SIFT 内部实现）
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览

- **时间复杂度**：O(n)
- **核可分离**：否
- **可就地计算**：否
- **抗噪能力**：🟡 中
- **边缘保持**：否

## 被哪些算法使用

- [→ algo-sift](/algorithms/sift/)


## 典型使用场景

- SIFT 的关键点亚像素定位（第 3 步）
- 剔除低对比度的不稳定特征点
- 亚像素级角点精化（cornerSubPix）


## 常见踩坑 🕳️

- ⚠️ 展开只用二阶项，对噪声敏感（所以还要做对比度筛选）
- ⚠️ 解出的偏移量如果超过 0.5 像素，说明该点不是真正的极值，应该丢弃


---

**上一级**：[← 算子词典总览](/operators/)
