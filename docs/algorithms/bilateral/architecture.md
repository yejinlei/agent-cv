# 🏗 算法流程

## 原始版双边滤波流程（逐像素）

```mermaid
flowchart TD
  S[输入图像 I] --> K[对每个像素 p]
  K --> N[取 p 周围 d×d 邻域 Ω]
  N --> C1[对每个邻居 q：算空间权重 Gσs||p-q||]
  N --> C2[对每个邻居 q：算值域权重 Gσr|Ip-Iq|]
  C1 --> W[w = Gs × Gr，累加权重总和 Wp]
  C2 --> W
  W --> S2["I'[p] = Σ I[q]·w / Wp"]
  S2 --> NEXT{还有像素?}
  NEXT --是--> K
  NEXT --否--> OUT[输出保边去噪图]
```

## O(1) 加速思路（Porikli 2008 核心 idea）

原始双边核 $G_{\sigma_s}(\cdot)\cdot G_{\sigma_r}(\cdot)$ 是非线性的、不能分离，但可以**按亮度值分箱**，对每个箱做一次盒滤波/高斯滤波，最后插值回来——这就是"双边网格 Bilateral Grid"的核心思想，把 O(r²) 降到 O(1) 常数时间。

工程上 OpenCV 里的 `cv2.bilateralFilter` 用的就是快速近似，比手写循环快 50 倍。

## 一个典型例子：人像磨皮流水线

```mermaid
flowchart LR
  A[原图] --> B[双边滤波 大核<br/>d=15 σ=75/75]
  B --> C[Detail = 原图 - 滤波结果]
  C --> D[把 Detail 减半再叠加回去]
  D --> E[皮肤光滑 皱纹保留✅]
```

这就是"自然磨皮"——只抹平色斑低频，保留皮肤纹理高频。**直接把整张图高斯糊掉会变成假面**。
