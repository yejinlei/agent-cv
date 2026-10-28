---
title: 双阈值判定 · 算子词典
outline: deep
---

# 🟡 双阈值判定（Double Threshold）

> **算子 ID**：`op-double-threshold` ｜ **类别**：point-operation

「两道门槛筛选」：设一个高门槛和一个低门槛。 比高门槛还强的（很明显的边缘），直接确定是边缘； 比低门槛还弱的（很淡的痕迹），直接扔掉； 介于两者之间的（不太确定的），先放着，等后面看它旁边有没有确定边缘再决定。 就像筛米：大石头直接扔，好米直接留，中间大小的要看它周围是什么。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="130" viewBox="0 0 380 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="130" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">双阈值：强/弱/无关 三档分类</text>
  <line x1="60" y1="40" x2="60" y2="100" stroke="#333"/>
  <line x1="60" y1="100" x2="350" y2="100" stroke="#333"/>
  <line x1="180" y1="40" x2="180" y2="100" stroke="#d44" stroke-dasharray="3"/>
  <line x1="270" y1="40" x2="270" y2="100" stroke="#2a9d4a" stroke-dasharray="3"/>
  <text x="170" y="118" font-size="12" fill="#d44">低阈值</text>
  <text x="260" y="118" font-size="12" fill="#2a9d4a">高阈值</text>
  <rect x="60" y="40" width="120" height="60" fill="#eee" opacity=".7"/><text x="100" y="75" font-size="13" fill="#888">置零</text>
  <rect x="180" y="40" width="90" height="60" fill="#ffe08a" opacity=".7"/><text x="205" y="75" font-size="13" fill="#a07820">弱边</text>
  <rect x="270" y="40" width="80" height="60" fill="#f5b3b3" opacity=".7"/><text x="295" y="75" font-size="13" fill="#d44">强边</text>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=thresh" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
strong: M ≥ T_high;  weak: T_low ≤ M < T_high;  reject: M < T_low
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `T_high` | 高阈值 | T_low 的 2–3 倍 | 越高越保守，可能漏掉弱边缘 |
| `T_low` | 低阈值 | Canny 中常取 T_high 的 1/2 或 1/3 | 越低越敏感，可能引入噪声 |



## OpenCV 调用

```python
import cv2
# → （Canny 内部实现）
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览

- **时间复杂度**：O(n)
- **核可分离**：否
- **可就地计算**：否
- **抗噪能力**：🟢 高
- **边缘保持**：是

## 被哪些算法使用

- [→ algo-canny](/algorithms/canny/)


## 典型使用场景

- Canny 的第三、四步（阈值 + 滞后连接）
- 任何「需要在噪声和漏检之间权衡」的判定
- 目标检测中的置信度筛选（两个阈值 + 中间区域待定）


## 常见踩坑 🕳️

- ⚠️ 两个阈值都要调，比单阈值更难（但效果更好）
- ⚠️ T_high 与 T_low 的比例比绝对数值更重要


---

**上一级**：[← 算子词典总览](/operators/)
