---
title: 高斯模糊 · 算子词典
outline: deep
---

# 🔵 高斯模糊（Gaussian Blur）

> **算子 ID**：`op-gaussian-blur` ｜ **类别**：filter

「给照片磨皮」：让每个像素跟它周围的邻居「平均一下」， 但离得近的邻居说话权重大、离得远的权重小——权重按一个钟形曲线分配。 结果是照片变得柔和，噪点（那些突兀的小点）被抹掉了。 就像隔着磨砂玻璃看东西，细节糊了，但脏点也看不见了。



<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fafbfc;margin:12px 0;">

<svg width="380" height="130" viewBox="0 0 380 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="130" fill="#f7f9fb"/>
  <text x="20" y="22" font-size="13" fill="#333">高斯核 3×3 权重（σ=1）</text>
  <g font-family="monospace" font-size="16" text-anchor="middle">
    <rect x="40" y="40" width="60" height="60" fill="#fffbe6" stroke="#e8cc6a"/><text x="70" y="78">0.07</text>
    <rect x="100" y="40" width="60" height="60" fill="#fff1b3" stroke="#e8cc6a"/><text x="130" y="78">0.12</text>
    <rect x="160" y="40" width="60" height="60" fill="#fffbe6" stroke="#e8cc6a"/><text x="190" y="78">0.07</text>
    <rect x="40" y="100" width="60" height="20" fill="#fff1b3" stroke="#e8cc6a"/>
    <rect x="40" y="40" width="0" height="60"/>
    <rect x="40" y="100" width="60" height="20" display="none"/>
  </g>
  <!-- 重新画3行 -->
  <g font-family="monospace" font-size="16" text-anchor="middle">
    <rect x="40" y="40" width="60" height="30" fill="#fffbe6" stroke="#d4b840"/><text x="70" y="60">0.07</text>
    <rect x="100" y="40" width="60" height="30" fill="#fff3c2" stroke="#d4b840"/><text x="130" y="60">0.12</text>
    <rect x="160" y="40" width="60" height="30" fill="#fffbe6" stroke="#d4b840"/><text x="190" y="60">0.07</text>
    <rect x="40" y="70" width="60" height="30" fill="#fff3c2" stroke="#d4b840"/><text x="70" y="90">0.12</text>
    <rect x="100" y="70" width="60" height="30" fill="#ffe482" stroke="#d4b840"/><text x="130" y="90">0.20</text>
    <rect x="160" y="70" width="60" height="30" fill="#fff3c2" stroke="#d4b840"/><text x="190" y="90">0.12</text>
    <rect x="40" y="100" width="60" height="25" fill="#fffbe6" stroke="#d4b840"/><text x="70" y="118" font-size="14">0.07</text>
    <rect x="100" y="100" width="60" height="25" fill="#fff3c2" stroke="#d4b840"/><text x="130" y="118" font-size="14">0.12</text>
    <rect x="160" y="100" width="60" height="25" fill="#fffbe6" stroke="#d4b840"/><text x="190" y="118" font-size="14">0.07</text>
  </g>
  <text x="250" y="55" font-size="13" fill="#444">中间权重最大(0.20)</text>
  <text x="250" y="78" font-size="13" fill="#444">越往外权重越小</text>
  <text x="250" y="101" font-size="13" fill="#444">权重和=1 → 不改变亮度</text>
</svg>

<p style="margin:8px 0 0;font-size:13px;color:#555;">
👉 <a href="/agent-cv/math-lab/?tab=gauss" target="_blank">去「原理实验室」拖滑块亲手调这个算子 ▸</a>
</p>
</div>



## 数学形式

$$
G(x,y;σ) = (1/(2πσ²)) · exp(-(x²+y²)/(2σ²))
$$

::: info 📐 公式怎么看
公式只是「精确表达」，真正理解要靠上面的白话比喻。如果公式让你头大，可以跳过——**会调参比会推公式重要**。
:::


## 参数与调参

| 参数 | 含义 | 典型值 | 怎么影响结果 |
|---|---|---|---|
| `ksize` | 卷积核大小（必须是奇数） | 3×3 / 5×5 / 9×9 | 越大越模糊 |
| `sigmaX` | X 方向标准差 | 0（由 ksize 自动推算）或 1.0–3.0 | 越大越模糊，细节丢失越多 |



## OpenCV 调用

```python
import cv2
# → cv2.GaussianBlur
```

::: tip
具体参数见下方「参数与调参」表。
:::


## 属性速览

- **时间复杂度**：O(n · k²)，可分离时为 O(n · 2k)
- **核可分离**：是 ✅（可加速）
- **可就地计算**：是 ✅（省内存）
- **抗噪能力**：🟢 高
- **边缘保持**：否

## 被哪些算法使用

- [→ algo-canny](/algorithms/canny/)
- [→ algo-sift](/algorithms/sift/)


## 典型使用场景

- 去除高斯噪声
- 降采样前的抗混叠
- 边缘检测的前置平滑（Canny 第一步）
- 尺度空间的构造（SIFT 的每个 octave）


## 常见踩坑 🕳️

- ⚠️ ksize 用偶数 → OpenCV 直接报错
- ⚠️ sigma 设太大 → 细小特征全丢
- ⚠️ 先边缘检测后模糊 → 完全错误，顺序反了


---

**上一级**：[← 算子词典总览](/operators/)
