# 核心概念：CLAHE 限制对比度自适应直方图均衡

<div class="tip custom-block"><p>🧪 公式看不懂？去 <a href="/math-lab/">原理实验室</a> 拖动滑块直观体验卷积/梯度/高斯/霍夫/角点/RANSAC/光流等核心概念；看完原理再去本页底部 <a href="./source">源码/真机实验室</a> 亲手调参数。</p></div>


## 1. 全局直方图均衡（HE）回顾

把灰度图的累积分布函数（CDF）当成映射函数：$T(r) = 255 \cdot \sum_{i=0}^{r} p(i)$，把原像素值 r 映射到 T(r)。好处是整体对比度最大；坏处是**对局部不管用**——大块亮区占据直方图大部分时，暗部被压成一条线。

## 2. 自适应直方图均衡（AHE）

把图像分成 M×N 块，每块各自做 HE，结果是局部对比度确实提升，但**均匀区域里噪声被强力放大**——因为一个本来很平坦的块，CDF 很陡，一个像素值抖动都会被映射成很大跨度。

## 3. Clip Limit：切掉超额直方图

每个 tile 平均像素数 = tileW × tileH / 256。CLAHE 规定每个 bin 不能超过 `clipLimit × avgPixels`（clipLimit 典型 2–4）。超额的部分被平均洒给所有 bin，效果：
- 陡峭的峰被削平 → 映射函数斜率变小 → 噪声不会被放大
- 平均分配给所有 bin → 整体亮度不漂移

## 4. 双线性插值

4 个相邻 tile（左上、右上、左下、右下）各有自己的映射函数。对 tile 内部的像素 (x,y)，根据它距离 4 个 tile 中心的权重，做双线性插值得到最终灰度，消除网格感。

## 5. 彩色图处理

CLAHE 通常**不直接对 RGB 三通道各做一遍**（会造成色偏）。正确做法：转到 LAB / YCrCb 空间，只对 L（亮度）/Y 通道做 CLAHE，再转回 RGB。


---

## 🧪 原理可视化

看不懂上面的公式？下面这个互动组件把「直方图」画出来了——拖动滑块，看每一步怎么算。

<ClientOnly>
  <MathVisualizer initial-tab="hist" compact />
</ClientOnly>

> 想看它在真实照片上的实际效果？回到 [本算法首页](./index) 或去 [🎮 真机实验室](/playgrounds/)。

<!-- AUTO-EXTENSION -->

## 🧓 大白话解释 CLAHE：局部聪明的对比度增强

普通直方图均衡（HE）是"整张图一把抓"——有一个地方太亮或太暗，整张图都被它带歪。自适应直方图均衡（AHE）把图切成小块，每块自己均衡，但**小块里出现一个特别亮的噪声点，这一块就被放大得特别夸张**（噪声爆炸）。

**CLAHE** = AHE + **对比度裁剪（Contrast Limited）**：
- 每个小块里，超过阈值的像素"溢出量"**重新均匀分给所有 bin**，不让某几个 bin 独占对比度；
- 最后双线性插值拼接块与块，消除块边界。

打比方：HE 像把全国贫富差距一次性拉平（结果一线城市房价暴涨）；AHE 像每个城市自己调（结果某村出了个亿万富翁把全村人均拉高）；**CLAHE 像每个城市都设个"首富上限"，多出来的钱平分给全村**。

## 🔍 效果对比

<div style="text-align:center">
<svg xmlns="http://www.w3.org/2000/svg" width="720" height="160" style="background:#fafbfc;border-radius:12px;border:1px solid #eaecef">
  <g transform="translate(20,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">原图（逆光）</text>
    <rect x="20" y="30" width="160" height="120"/>
    <defs><linearGradient id="dark" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset="0.6" stop-color="#333"/><stop offset="1" stop-color="#fff"/></linearGradient></defs>
    <rect x="20" y="30" width="160" height="120" fill="url(#dark)"/>
    <text x="100" y="100" text-anchor="middle" font-size="11" fill="#fff">脸全黑，背景过曝</text>
  </g>
  <g transform="translate(260,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">普通 HE</text>
    <rect x="20" y="30" width="160" height="120"/>
    <rect x="20" y="30" width="160" height="120" fill="#888"/>
    <text x="100" y="100" text-anchor="middle" font-size="11" fill="#fff">噪声放大，背景发灰</text>
  </g>
  <g transform="translate(500,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#27ae60">CLAHE</text>
    <rect x="20" y="30" width="160" height="120"/>
    <rect x="20" y="30" width="160" height="120" fill="#b4a090"/>
    <circle cx="70" cy="80" r="15" fill="#d4a373"/>
    <text x="100" y="140" text-anchor="middle" font-size="11" fill="#333">脸清晰了，背景自然</text>
  </g>
</svg>
</div>
