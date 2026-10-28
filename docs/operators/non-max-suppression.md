---
title: 非极大值抑制（边缘细化） · 算子词典
outline: deep
---

# 🟢 非极大值抑制（边缘细化）（Non-Maximum Suppression (edge thinning)）

> **算子 ID**：`op-non-max-suppression` ｜ **类别**：edge

「把粗线削成细线」：Sobel 找出来的边缘往往有好几像素宽（像粗马克笔画的线）， 而真正的边缘应该只有一条线（像铅笔）。NMS 的做法是： 沿着边缘的垂直方向看，只保留最亮的那个点，其他「旁边稍微暗一点」的点全部抹掉。 结果就是粗管变成细线，而且位置最准。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="130" viewBox="0 0 380 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="130" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">非极大值抑制：粗边 → 单线</text>
  <rect x="25" y="40" width="150" height="30" fill="url(#nms-g)"/>
  <defs><linearGradient id="nms-g"><stop offset="0" stop-color="#eee"/><stop offset=".5" stop-color="#333"/><stop offset="1" stop-color="#eee"/></linearGradient></defs>
  <text x="70" y="90" font-size="13" fill="#666">抑制前：一条粗带</text>
  <line x1="220" y1="55" x2="360" y2="55" stroke="#000" stroke-width="2"/>
  <text x="250" y="90" font-size="13" fill="#666">抑制后：精准的单像素线</text>
  <text x="15" y="120" font-size="12" fill="#666">梯度方向上只保留最大值，其余置零</text>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=grad" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
保留 (x,y) 当且仅当 M(x,y) ≥ M(x±1,y±1) 沿梯度方向上
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `梯度方向` | 先算梯度方向，再沿该方向比较 | 量化为 4 个方向（0°/45°/90°/135°） | 方向量化越细越准，但更慢 |
| `邻域` | 比较范围 | 两侧各 1 个像素 | 范围越大线越细，但可能断开 |



## OpenCV 调用

```python
import cv2
# → （Canny 内部实现，无独立函数）
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览

- **时间复杂度**：O(n)
- **核可分离**：否
- **可就地计算**：否
- **抗噪能力**：🟡 中
- **边缘保持**：是

## 被哪些算法使用

- [→ algo-canny](/algorithms/canny/)


## 典型使用场景

- 边缘细化为单像素宽
- 目标检测中的候选框去重（同名但含义不同，见下）


## 常见踩坑 🕳️

- ⚠️ 注意区分：目标检测里的 NMS 是「框去重」，边缘检测里的 NMS 是「线细化」，同名不同物
- ⚠️ 方向量化太粗 → 边缘出现锯齿


---

**上一级**：[← 算子词典总览](/operators/)
