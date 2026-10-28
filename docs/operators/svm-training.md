---
title: SVM 训练 · 算子词典
outline: deep
---

# 🟣 SVM 训练（Support Vector Machine Training）

> **算子 ID**：`op-svm-training` ｜ **类别**：statistical

「画一条最宽的分界线」：给你一堆「是行人」和「不是行人」的特征向量， 要画一条线把它们分开。但能分开的线有无数条，选哪条？ 选那条「离两边最近的点都尽量远」的—— 就像在两队人中间画线，要画在最宽敞的地方，不要贴着谁。 特别的是，决定这条线的只有「最靠近它的那几个点」（支持向量）， 其他点离多远都无所谓。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="150" viewBox="0 0 380 150" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="150" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">SVM：离两边最远的分界线</text>
  <g>
    <circle cx="70" cy="120" r="6" fill="#4a90e2"/>
    <circle cx="100" cy="90" r="6" fill="#4a90e2"/>
    <circle cx="130" cy="110" r="6" fill="#4a90e2"/>
    <circle cx="250" cy="50" r="6" fill="#d44"/>
    <circle cx="290" cy="80" r="6" fill="#d44"/>
    <circle cx="320" cy="60" r="6" fill="#d44"/>
    <line x1="50" y1="100" x2="350" y2="50" stroke="#333" stroke-width="2"/>
    <line x1="60" y1="115" x2="340" y2="70" stroke="#999" stroke-dasharray="4"/>
    <line x1="55" y1="85" x2="345" y2="35" stroke="#999" stroke-dasharray="4"/>
    <text x="200" y="140" font-size="12" fill="#666">间隔最大化→最稳的分法</text>
  </g>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=ransac" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
max 2/||w|| s.t. y_i(wᵀx_i + b) ≥ 1
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `C` | 正则化参数（惩罚错分的强度） | 1–100 | C 大 = 更严格地分对训练集（易过拟合）；C 小 = 容忍一些错分 |
| `kernel` | 核函数 | linear（HOG 用线性）/ rbf | 非线性核能处理更复杂的分界，但更慢 |
| `gamma` | RBF 核的宽度 | 'scale'（自动） | 越大越容易过拟合 |



## OpenCV 调用

```python
import cv2
# → cv2.ml.SVM_create / sklearn.svm.SVC
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览

- **时间复杂度**：训练 O(n²–n³)，预测 O(#支持向量)
- **核可分离**：否
- **可就地计算**：否
- **抗噪能力**：🟡 中
- **边缘保持**：否

## 被哪些算法使用

- [→ algo-hog-svm](/algorithms/hog-svm/)


## 典型使用场景

- HOG 特征的分类（行人检测的经典组合）
- 任何「高维特征 + 小样本」的分类任务
- 难例挖掘（Hard Negative Mining）


## 常见踩坑 🕳️

- ⚠️ 特征必须归一化/标准化，否则量纲大的特征主导结果
- ⚠️ HOG+SVM 用线性核就够了（高维特征下线性通常足够）
- ⚠️ 正负样本比例失衡时需要用不同的 C 或加权


---

**上一级**：[← 算子词典总览](/operators/)
