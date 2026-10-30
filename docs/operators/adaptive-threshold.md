---
title: 自适应阈值 · 算子词典
outline: deep
---

# 🟡 自适应阈值（Adaptive Threshold）

> **算子 ID**：`op-adaptive-threshold` ｜ **类别**：point-operation

全局阈值像「全班统一划一条及格线」，可如果卷子一半亮一半暗就不公平了。 自适应阈值的做法是「给每个同学单独划一条线」： 对图上每一个像素，都去看它周围一小圈邻居的平均亮度，再决定它是黑还是白。 于是光照不均匀的图像也能被正确二值化。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="130" viewBox="0 0 380 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="130" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">自适应阈值：每个点看邻居及格线</text>
  <defs><linearGradient id="adg" x1="0" x2="1"><stop offset="0" stop-color="#444"/><stop offset=".5" stop-color="#ccc"/><stop offset="1" stop-color="#888"/></linearGradient></defs>
  <rect x="20" y="45" width="150" height="60" fill="url(#adg)"/>
  <text x="60" y="80" font-size="12" fill="#fff">光照不均匀</text>
  <path d="M200,45 Q230,60 270,75 Q310,85 350,105" stroke="#d44" stroke-dasharray="3" fill="none"/><text x="230" y="40" font-size="11" fill="#d44">局部阈值(动态)</text>
  <text x="200" y="120" font-size="12" fill="#666">每个像素按邻域均值单独决定阈值</text>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=thresh" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
T(x,y) = mean(邻域) − C  或  T(x,y) = gaussian(邻域) − C
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `blockSize` | 邻域大小（必须为奇数） | 11–51 | 太小会引入噪声，太大会退化成全局阈值 |
| `C` | 从局部均值中减去的常数 | 2–10（常取正数） | 越大留下的白区越少，抑制噪声 |
| `method` | 邻域均值或高斯加权 | MEAN_C / GAUSSIAN_C | 高斯加权对中心更敏感，边缘更平滑 |



## OpenCV 调用

```python
import cv2
# → cv2.adaptiveThreshold
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览

| 属性 | 值 |
|---|---|
| 类型 | 局部自适应阈值 |
| 复杂度 | O(N)，每个像素做局部均值/加权均值 |
| 抗光照不均 | ✅ 强（每个块自己定阈值） |
| 常用核大小 | blockSize = 11~51（必须是奇数） |
| 常用偏移C | 2~10（块均值减去C作为局部阈值） |
| OpenCV 调用 | `cv2.adaptiveThreshold(img,255,ADAPTIVE_THRESH_GAUSSIAN_C,THRESH_BINARY,blockSize,C)` |

## 被哪些算法使用

- [→ 文档/阴影场景二值化](/scenarios/ocr-document/)
- [→ 工业/尺寸测量预处理](/scenarios/measurement/)
- Canny 算法的「双阈值」用的是硬阈值，本算子主要用于光照不均场景


## 典型使用场景

- 文档扫描：阴影、折痕下的文字二值化
- 工业缺陷检测：光照不均表面的缺陷提取
- 车牌/字符识别的预处理


## 常见踩坑 🕳️

- ⚠️ blockSize 必须是奇数，否则 OpenCV 直接报错
- ⚠️ blockSize 过大时局部性消失，退化成全局阈值（不如直接用 Otsu）
- ⚠️ 对纯色区域会产生大量噪点（因为没有真实的局部对比）


---

**上一级**：[← 算子词典总览](/operators/)
