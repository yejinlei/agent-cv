---
title: Sobel 算子 · 算子词典
outline: deep
---

# 🟢 Sobel 算子（Sobel Operator）

> **算子 ID**：`op-sobel` ｜ **类别**：edge

「找明暗突变处」：比较每个像素跟它左右邻居谁亮谁暗， 亮度差得多的地方就是「竖着的边」，上下差得多的地方就是「横着的边」。 它像个左右（或上下）比较的秤，能让边缘的地方数值变大、 平坦的地方数值接近零。 因为它带了一点点模糊（中心权重更大），所以比「硬相减」对噪点更宽容。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="150" viewBox="0 0 380 150" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="150" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">Sobel Gx (水平方向边缘检测)</text>
  <g font-family="monospace" font-size="14" text-anchor="middle">
    <rect x="20" y="40" width="36" height="30" fill="#fde2e2" stroke="#d44"/><text x="38" y="60">-1</text>
    <rect x="56" y="40" width="36" height="30" fill="#fff" stroke="#ccc"/><text x="74" y="60">0</text>
    <rect x="92" y="40" width="36" height="30" fill="#e2f4e2" stroke="#4a4"/><text x="110" y="60">+1</text>
    <rect x="20" y="70" width="36" height="30" fill="#f8b3b3" stroke="#d44"/><text x="38" y="90">-2</text>
    <rect x="56" y="70" width="36" height="30" fill="#fff" stroke="#ccc"/><text x="74" y="90">0</text>
    <rect x="92" y="70" width="36" height="30" fill="#b7e9b7" stroke="#4a4"/><text x="110" y="90">+2</text>
    <rect x="20" y="100" width="36" height="30" fill="#fde2e2" stroke="#d44"/><text x="38" y="120">-1</text>
    <rect x="56" y="100" width="36" height="30" fill="#fff" stroke="#ccc"/><text x="74" y="120">0</text>
    <rect x="92" y="100" width="36" height="30" fill="#e2f4e2" stroke="#4a4"/><text x="110" y="120">+1</text>
  </g>
  <g>
    <line x1="150" y1="85" x2="200" y2="85" stroke="#333" stroke-width="2" marker-end="url(#arr)"/>
    <defs><marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#333"/></marker></defs>
  </g>
  <rect x="210" y="45" width="150" height="85" fill="#fff" stroke="#ddd"/>
  <line x1="260" y1="50" x2="260" y2="125" stroke="#333" stroke-width="3"/>
  <text x="285" y="85" font-size="13" fill="#444">竖直边→亮</text>
  <text x="285" y="105" font-size="13" fill="#444">左右差大=边</text>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=grad" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
Gx = [[-1,0,1],[-2,0,2],[-1,0,1]] * I,  Gy = Gxᵀ * I
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `ddepth` | 输出数据类型 | cv2.CV_16S（避免负值被截断）/ cv2.CV_32F | 用 CV_8U 会丢掉负梯度的一半信息 |
| `ksize` | 核大小 | 3（最常用） | 1 表示用 3×1 或 1×3 核（更快），越大越平滑 |
| `dx / dy` | 求导的阶数 | (1,0) 求 x 方向 / (0,1) 求 y 方向 | 决定求的是哪种边缘 |



## OpenCV 调用

```python
import cv2
# → cv2.Sobel
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览

- **时间复杂度**：O(n · k²)
- **核可分离**：是 ✅（可加速）
- **可就地计算**：否
- **抗噪能力**：🟡 中
- **边缘保持**：是

## 被哪些算法使用

- [→ algo-canny](/algorithms/canny/)
- [→ algo-hog-svm](/algorithms/hog-svm/)


## 典型使用场景

- 边缘检测的第一步（求梯度）
- HOG 特征中的梯度计算
- 纹理分析


## 常见踩坑 🕳️

- ⚠️ ddepth 用 CV_8U → 负梯度被截断成 0，一半边缘丢失
- ⚠️ 忘了对结果取绝对值（cv2.convertScaleAbs）
- ⚠️ x/y 方向搞反（dx=1 求的是竖直边缘）


---

**上一级**：[← 算子词典总览](/operators/)
