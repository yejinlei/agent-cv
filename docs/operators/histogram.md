---
title: 直方图统计 · 算子词典
outline: deep
---

# 🟣 直方图统计（Histogram）

> **算子 ID**：`op-histogram` ｜ **类别**：statistical

「数一数每种亮度有多少个像素」：把 0–255 的亮度做成 256 个格子， 遍历每个像素，看它落在哪个格子，格子里的计数器加一。 最后得到一张柱状图：横轴是亮度，纵轴是这个亮度的像素个数。 它能一眼看出「这张照片是偏暗还是偏亮、对比度够不够」。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="150" viewBox="0 0 380 150" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="150" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">直方图：每种亮度有多少像素</text>
  <line x1="30" y1="130" x2="370" y2="130" stroke="#333"/>
  <line x1="30" y1="130" x2="30" y2="40" stroke="#333"/>
  <g fill="#4a90e2">
    <rect x="40" y="120" width="5" height="10"/>
    <rect x="50" y="110" width="5" height="20"/>
    <rect x="60" y="95" width="5" height="35"/>
    <rect x="70" y="75" width="5" height="55"/>
    <rect x="80" y="60" width="5" height="70"/>
    <rect x="90" y="55" width="5" height="75"/>
    <rect x="100" y="50" width="5" height="80"/>
    <rect x="110" y="55" width="5" height="75"/>
    <rect x="120" y="70" width="5" height="60"/>
    <rect x="130" y="90" width="5" height="40"/>
    <rect x="140" y="110" width="5" height="20"/>
    <rect x="150" y="120" width="5" height="10"/>
  </g>
  <text x="60" y="148" font-size="11" fill="#666">暗</text><text x="140" y="148" font-size="11" fill="#666">亮</text>
  <text x="200" y="80" font-size="13" fill="#666">横轴=亮度值 0~255</text>
  <text x="200" y="100" font-size="13" fill="#666">纵轴=该亮度的像素个数</text>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=hist" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
h(v) = #{ (x,y) | I(x,y) = v }
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `bins` | 格子数 | 256（灰度） | 越少越粗但越稳 |
| `range` | 统计范围 | [0, 256) | 决定哪些值被计入 |



## OpenCV 调用

```python
import cv2
# → cv2.calcHist
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览

- **时间复杂度**：O(n)
- **核可分离**：否
- **可就地计算**：否
- **抗噪能力**：🟢 高
- **边缘保持**：否

## 被哪些算法使用

- [→ algo-hog-svm](/algorithms/hog-svm/)
- [→ algo-otsu](/branches/image-processing/thresholding#otsu)
- [→ algo-canny](/algorithms/canny/)


## 典型使用场景

- 图像统计与可视化
- 直方图均衡化（增强对比度）
- Otsu 自动阈值
- HOG 的梯度方向直方图（是「方向」的直方图）
- 反向投影做目标跟踪


## 常见踩坑 🕳️

- ⚠️ 直方图相同的两张图可能完全不同（丢失空间信息）
- ⚠️ 用于「方向」统计时要注意分箱的循环性（0° 和 360° 是同一个方向）


---

**上一级**：[← 算子词典总览](/operators/)
