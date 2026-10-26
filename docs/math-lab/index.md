---
title: 数学概念互动实验室
editLink: false
---

# 🧪 传统CV 数学概念互动实验室

> 面向CV小白：**所有晦涩数学概念和算法原理，拖动滑块就能看效果**。不用背公式，玩两遍就懂。

每一个概念都是**纯Canvas原生实现**，不需要加载OpenCV.js，秒开无卡顿。点击上方标签页切换不同概念。

<MathVisualizer />

---

## 💡 学习建议

按照下面顺序玩，从最简单到最复杂，传统CV的数学基础就全懂了：

1. **像素矩阵** → 先搞懂"图像到底是什么"
2. **邻域与距离** → 为什么算法总说"周围3×3"
3. **卷积** → 90%传统算法的底层操作
4. **高斯分布** → 为什么"权重中间大周围小"
5. **梯度/边缘** → 边缘检测的数学本质
6. **阈值分割** → 最基础的"前景背景分离"
7. **形态学运算** → 二值图的"橡皮擦"
8. **直方图** → 怎么让暗图自动变亮
9. **颜色空间** → 为什么HSV做颜色分割更好
10. **Harris角点** → "什么是特征点"的数学定义
11. **霍夫变换** → 怎么从一堆点里找出直线/圆
12. **傅里叶频域** → 低频和高频到底是什么
13. **RANSAC** → 为什么它不怕错点/噪声
14. **Lucas-Kanade光流** → 怎么追踪物体移动

---

## 🎯 看懂原理了？去真机实验室跑真实照片

下面每个互动 tab 讲的都是「数学直觉」——用的是合成小图。想在真实照片上看到效果、想调参数、想复制代码去用，点这里：

<div style="display:flex; gap:16px; flex-wrap:wrap; margin: 16px 0">
  <a href="/playgrounds/" style="flex:1; min-width:240px; padding:18px; border-radius:12px; background:linear-gradient(135deg,var(--vp-c-brand-soft),var(--vp-c-brand-1)); color:#fff; text-decoration:none; font-weight:600">
    🎮 真机实验室（OpenCV.js 39 种算法在线跑）<br/>
    <small style="opacity:.85">真实照片 · 可调参数 · 自动生成 Python/C++/JS 代码</small>
  </a>
</div>

每个算法档案页（如 <a href="/algorithms/sobel/source">Sobel 源码页</a>）底部也会自动嵌入一个"选中该算法"的同款实验室，看完原理直接动手，不用切页面。
