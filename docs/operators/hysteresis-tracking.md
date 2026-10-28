---
title: 滞后连接（边缘追踪） · 算子词典
outline: deep
---

# 🟢 滞后连接（边缘追踪）（Hysteresis Tracking）

> **算子 ID**：`op-hysteresis-tracking` ｜ **类别**：edge

「顺藤摸瓜」：双阈值筛完，还剩一些「不太确定的弱边缘」。 现在从每个「确定边缘」出发，沿着它往外走， 只要碰到「弱边缘」，就把它也确认为边缘，并继续从它往外走。 这样一条断断续续的线，会从某个确定点开始一路被连起来。 好处是：孤立的弱边缘（多半是噪声）不会凭空被留下， 而属于同一条真实边缘的弱部分都被接上了。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="130" viewBox="0 0 380 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="130" fill="#f7f9fb"/>
  <text x="15" y="22" font-size="13" fill="#333">滞后连接：强边拉着弱边上岸</text>
  <g stroke-width="3" fill="none">
    <path d="M40,80 L80,80 L120,70" stroke="#d44"/>
    <path d="M120,70 L160,65" stroke="#d4b840" stroke-dasharray="3"/>
    <path d="M160,65 L200,55 L240,50" stroke="#d44"/>
    <path d="M240,50 L280,55" stroke="#d4b840" stroke-dasharray="3"/>
    <path d="M280,55 L320,70" stroke="#d44"/>
  </g>
  <text x="50" y="110" font-size="12" fill="#d44">强边(保留)</text>
  <text x="130" y="110" font-size="12" fill="#d4b840">弱边(连接上强边才留)</text>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=grad" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
弱边缘 e 被保留 ⟺ e 与某个强边缘 8-连通可达
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `连通性` | 邻域连接方式 | 8-连通 | 8 连通比 4 连通更容易把线连起来 |



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

- Canny 的最后一步（把弱边缘接上强边缘）
- 任何「区域生长」类算法
- 连通域分析


## 常见踩坑 🕳️

- ⚠️ 若低阈值过低，弱边缘太多，会把不相关的线也连起来
- ⚠️ 实现时要用队列/递归遍历，注意栈深度（大图递归会爆栈）


---

**上一级**：[← 算子词典总览](/operators/)
