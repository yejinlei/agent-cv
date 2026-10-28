---
title: L2 归一化 · 算子词典
outline: deep
---

# 🟡 L2 归一化（L2 Normalization）

> **算子 ID**：`op-l2-normalization` ｜ **类别**：point-operation

「把一盏灯泡的亮度整体调成固定的」： 一个向量除以它自己的「长度」，结果向量的长度就变成 1，但各分量的比例不变。 在特征描述子里，这样做的好处是： 如果现场光线整体变亮一倍，所有梯度都乘 2， 但归一化之后还是同一个向量——于是「光线变化」就被自动消掉了。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="130" viewBox="0 0 380 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="130" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">L2 归一化：把向量拉到单位长度</text>
  <line x1="60" y1="100" x2="150" y2="50" stroke="#4a90e2" stroke-width="3" marker-end="url(#narr)"/>
  <circle cx="60" cy="100" r="50" fill="none" stroke="#ccc" stroke-dasharray="3"/>
  <line x1="230" y1="100" x2="270" y2="60" stroke="#2a9d4a" stroke-width="3" marker-end="url(#narr)"/>
  <circle cx="230" cy="100" r="50" fill="none" stroke="#ccc" stroke-dasharray="3"/>
  <text x="70" y="80" font-size="12" fill="#4a90e2">原向量(长短不一)</text>
  <text x="230" y="80" font-size="12" fill="#2a9d4a">归一化后(都长1)</text>
  <text x="15" y="122" font-size="12" fill="#666">除以自身长度→消除整体亮暗影响</text>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=hist" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
v' = v / ||v||₂ = v / sqrt(Σvi²)
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `epsilon` | 防止除零的小量 | 1e-6 | 避免全零向量导致 NaN |



## OpenCV 调用

```python
import cv2
# → cv2.normalize(v, None, 1, 0, cv2.NORM_L2) 或 numpy 手算
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览

- **时间复杂度**：O(n)
- **核可分离**：否
- **可就地计算**：是 ✅（省内存）
- **抗噪能力**：🟢 高
- **边缘保持**：否

## 被哪些算法使用

- [→ algo-hog-svm](/algorithms/hog-svm/)
- [→ algo-sift](/algorithms/sift/)


## 典型使用场景

- HOG 的块内归一化（消除光照整体缩放）
- SIFT 描述子归一化 + 幅值截断（消除光照变化）
- 特征向量标准化（机器学习预处理）


## 常见踩坑 🕳️

- ⚠️ 忘了加 epsilon 会除零
- ⚠️ 只对梯度向量做归一化还不够（SIFT 还要截断大值，以抗局部强光）


---

**上一级**：[← 算子词典总览](/operators/)
