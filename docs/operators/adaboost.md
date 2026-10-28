---
title: AdaBoost 集成学习 · 算子词典
outline: deep
---

# 🟣 AdaBoost 集成学习（AdaBoost）

> **算子 ID**：`op-adaboost` ｜ **类别**：statistical

「三个臭皮匠顶一个诸葛亮」：单个弱分类器只能比瞎猜好一点点， 但把很多个这样的弱分类器加权组合起来，就能变成一个强分类器。 做法是：每加一个新分类器，就把上一个分错的样本「加重权重」， 逼着新分类器去专心对付这些难样本。 最后投票时，谁平时更准，谁的票就更重。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="130" viewBox="0 0 380 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="130" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">AdaBoost：弱分类器加权投票</text>
  <g font-size="12" text-anchor="middle">
    <rect x="20" y="50" width="60" height="30" rx="4" fill="#e3f2fd" stroke="#4a90e2"/><text x="50" y="70">弱1×0.3</text>
    <rect x="90" y="50" width="60" height="30" rx="4" fill="#e3f2fd" stroke="#4a90e2"/><text x="120" y="70">弱2×0.5</text>
    <rect x="160" y="50" width="60" height="30" rx="4" fill="#e3f2fd" stroke="#4a90e2"/><text x="190" y="70">弱3×0.2</text>
    <rect x="230" y="50" width="60" height="30" rx="4" fill="#e3f2fd" stroke="#4a90e2"/><text x="260" y="70">弱4×0.7</text>
    <text x="310" y="70">…</text>
  </g>
  <line x1="30" y1="85" x2="30" y2="100" stroke="#333"/>
  <line x1="340" y1="85" x2="340" y2="100" stroke="#333"/>
  <line x1="30" y1="100" x2="340" y2="100" stroke="#333" marker-end="url(#adba)"/>
  <defs><marker id="adba" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#333"/></marker></defs>
  <rect x="130" y="105" width="110" height="20" rx="4" fill="#fde2e2" stroke="#d44"/><text x="185" y="120" font-size="12" text-anchor="middle" fill="#d44">强分类器(投票结果)</text>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=ransac" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
H(x) = sign( Σ_t α_t · h_t(x) )，α_t = ½ ln((1−e_t)/e_t)
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `弱分类器数量 T` | 集成的轮数 | 10–200 | 越多越准但越慢；级联检测里通常每级几十个 |
| `弱分类器类型` | 通常用单层决策树（决策树桩） | decision stump | 越简单越好，只要能比随机猜好 |
| `学习率/权重更新` | 错分样本的权重放大倍率 | 由误差率自动决定 | 误差率越低，该分类器的投票权重越大 |



## OpenCV 调用

```python
import cv2
# → cv2.ml.Boost_create
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览



## 被哪些算法使用

- [→ algo-viola-jones](/branches/detection/viola-jones)


## 典型使用场景

- 组合弱分类器成强分类器（Viola-Jones 级联的每一级训练）
- 作为通用集成学习 baseline（如 AdaBoost.M1）


## 常见踩坑 🕳️

- ⚠️ 对噪声样本与离群点敏感（AdaBoost 会不断给它们加权）
- ⚠️ 弱分类器太强反而容易过拟合


---

**上一级**：[← 算子词典总览](/operators/)
