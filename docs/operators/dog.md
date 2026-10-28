---
title: 高斯差分（DoG） · 算子词典
outline: deep
---

# 🔵 高斯差分（DoG）（Difference of Gaussians）

> **算子 ID**：`op-dog` ｜ **类别**：filter

「用两个不同模糊程度的照片相减」：把同一张图模糊一次得到 A，模糊得更厉害一次得到 B， 然后 A 减 B。结果里留下的，正好是「那种大小的细节」—— 比这个尺寸小的细节被 A 的模糊抹掉了，比这个尺寸大的细节在相减时抵消了。 所以 DoG 就像一个「只认某个尺寸」的筛子，专门筛出特定大小的斑点。 它便宜得惊人：只是两次模糊再加一次减法，却近似了很贵的拉普拉斯算子。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="130" viewBox="0 0 380 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="130" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">DoG = Gaussian(σ₁) − Gaussian(σ₂)</text>
  <path d="M30,100 Q80,40 130,100" fill="none" stroke="#4a90e2" stroke-width="2"/>
  <path d="M140,100 Q190,60 240,100" fill="none" stroke="#e87a4a" stroke-width="2"/>
  <path d="M250,100 Q280,80 310,90 Q330,70 350,100" fill="none" stroke="#9b59b6" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="60" y="35" font-size="12" fill="#4a90e2">小σ(细节)</text>
  <text x="170" y="55" font-size="12" fill="#e87a4a">大σ(轮廓)</text>
  <text x="270" y="75" font-size="12" fill="#9b59b6">相减→斑点</text>
  <text x="15" y="120" font-size="12" fill="#666">两次模糊相减，只保留"特定大小"的特征 → 尺度空间</text>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=gauss" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
DoG(x,y,σ) = (G(x,y,kσ) - G(x,y,σ)) * I(x,y) ≈ (k-1)σ²∇²G * I
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `k` | 相邻尺度的比例 | 2^(1/s)，s 为每 octave 的层数（SIFT 用 s=3，k≈1.26） | k 越接近 1，近似越准，但层数越多越慢 |
| `σ` | 基础尺度 | 1.6（SIFT 默认） | 决定检测的最细特征尺寸 |



## OpenCV 调用

```python
import cv2
# → （SIFT 内部实现，可手写为 GaussianBlur 相减）
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览

- **时间复杂度**：O(n · k²)（两次高斯）
- **核可分离**：是 ✅（可加速）
- **可就地计算**：否
- **抗噪能力**：🟢 高
- **边缘保持**：否

## 被哪些算法使用

- [→ algo-sift](/algorithms/sift/)


## 典型使用场景

- 尺度空间的极值检测（SIFT 的第一步）
- 斑点检测（Blob Detection）
- 低成本近似 LoG


## 常见踩坑 🕳️

- ⚠️ 直接用 LoG 会慢很多，DoG 是它的高效近似
- ⚠️ k 取值不当会导致尺度采样不足、遗漏特征点
- ⚠️ 相减时若用 uint8 会截断负值，必须用浮点


---

**上一级**：[← 算子词典总览](/operators/)
