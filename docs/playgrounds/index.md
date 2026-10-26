---
title: 🎮 真机实验室（OpenCV.js 39 种算法在线跑）
---

# 🎮 真机实验室

> **在你浏览器里真机跑 OpenCV 算法**——不用装 OpenCV、不用写代码、不用上传图片到任何服务器。底层是 OpenCV.js（WebAssembly 版 OpenCV），**全部计算在你电脑/手机本地完成**。

<div class="tip custom-block">
  <p>📚 <b>看不懂公式/参数什么意思？</b> 先去 <a href="/agent-cv/math-lab/">🧪 原理实验室（看不懂公式点这）</a>——那里用合成示意图、拖动滑块把"卷积/梯度/高斯/霍夫/角点/RANSAC/光流"的数学原理讲清楚，再回这里跑真实算法。</p>
</div>

## 玩法

1. 左边选一张**内置示例图**（13 种常见场景：街景/人脸/行人/棋盘格/硬币/文档/纹理/水果/连续帧…），或点「📂 上传图片」用自己的照片；
2. 中间选**算法**（39 种，覆盖六大分支），拖动滑块调参数，结果会实时刷新；
3. 右边看到**处理结果**和**毫秒级耗时**；
4. 每个算法下方自动生成**实时联动的 Python / C++ / JavaScript 代码**，拖参数时代码里的参数值同步更新——可以直接复制到自己项目里。

<ClientOnly>
  <OpencvPlayground />
</ClientOnly>

## 为什么有两个"实验室"？

| | 🧪 原理实验室 | 🎮 真机实验室（本页） |
|---|---|---|
| **目标** | 搞懂"为什么"——数学原理 | 看见"什么样"——真算法效果 |
| **数据** | 合成小图（几个点/一条线） | 真实照片 |
| **依赖** | 纯 Canvas，**秒开**，不用下载任何东西 | OpenCV.js（约 11 MB，首次加载需几秒） |
| **代码** | 没有代码，只有数学直观 | 实时生成 Python/C++/JS 代码可复制 |
| **建议顺序** | 🟢 小白先看这里 | 原理懂了再来这里跑 |
| **对应关系** | 14 个原理 tab ↔ 本页 39 个算法 | 每个算法页底部也有同款实验室 |

<div class="warning custom-block">
  <p><b>提示</b>：每个算法的档案页（例如 <a href="/agent-cv/algorithms/sobel/">Sobel</a>、<a href="/agent-cv/algorithms/canny/">Canny</a>、<a href="/agent-cv/algorithms/harris/">Harris</a>、<a href="/agent-cv/algorithms/hough/">霍夫直线</a>、<a href="/agent-cv/algorithms/ransac/">RANSAC</a>、<a href="/agent-cv/algorithms/lucas-kanade/">Lucas-Kanade</a>）底部都会嵌入一个<b>自动选中该算法</b>的紧凑版实验室——看完原理直接动手，不用再切回本页。</p>
</div>
