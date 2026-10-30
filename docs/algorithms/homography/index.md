---
layout: doc
---

# 单应矩阵

<AlgorithmCard
  name="单应矩阵"
  enName="Homography Matrix H"
  chapter="第13章 · 广义匹配"  chapterLink="/chapters/ch13-matching"
  branch="geometry"
  year="传统几何"
  author="几何视觉经典（DLT 1971 年 Sutherland）"
  paper="https://www.cambridge.org/core/books/multiple-view-geometry-in-computer-vision/0B6F289C78B2B23F596CAA76D3D43F7A"
  level="mid"
  tagline="一个 3×3 矩阵搞定「一个平面」在两张图之间的映射，4 对点就能求，文档扫描和全景拼接的灵魂"
  analogy="你把手机对着一张纸拍斜了，单应矩阵就像一个「拉正」的魔法：告诉它纸的四个角「应该」在什么位置，它就能把整张纸拉正成矩形——就像你从正上方拍的一样。同样的魔法也能把车道线变成鸟瞰图、把多张旋转拍的照片拼成全景"
  scene="文档扫描/矫正、逆透视变换 IPM（车道鸟瞰）、AR 平面跟踪、全景拼接（纯旋转）、张正友标定、图像配准"
  :pros='["数学简洁优美（8 自由度）", "4 对点即可求解", "OpenCV 一行 findHomography", "应用场景极广", "RANSAC 版本鲁棒"]'
  :cons='["仅对平面场景/纯旋转严格成立", "有深度差时错位", "点共线退化", "warpPerspective 易出画布", "DLT 不归一化数值差"]'
/>

## 一句话理解

一个 3×3 矩阵搞定「一个平面」在两张图之间的映射，4 对点就能求，文档扫描和全景拼接的灵魂。你把手机对着一张纸拍斜了，单应矩阵就像一个「拉正」的魔法：告诉它纸的四个角「应该」在什么位置，它就能把整张纸拉正成矩形——就像你从正上方拍的一样。同样的魔法也能把车道线变成鸟瞰图、把多张旋转拍的照片拼成全景。

```mermaid
flowchart LR
  A["输入图像"] --> B["单应矩阵"]
  B --> C["输出结果"]
```

## 生活类比

你把手机对着一张纸拍斜了，单应矩阵就像一个「拉正」的魔法：告诉它纸的四个角「应该」在什么位置，它就能把整张纸拉正成矩形——就像你从正上方拍的一样。同样的魔法也能把车道线变成鸟瞰图、把多张旋转拍的照片拼成全景

## 它解决什么问题

文档扫描/矫正、逆透视变换 IPM（车道鸟瞰）、AR 平面跟踪、全景拼接（纯旋转）、张正友标定、图像配准。

在传统 CV 的六分支体系中，单应矩阵 属于 **geometry** 分支，主要解决的是该分支中一个 3×3 矩阵搞定「一个平面」在两张图之间的映射，4 对点就能求，文档扫描和全景拼接的灵魂的问题。

## 核心优点

- ✅ **数学简洁优美（8 自由度）**
- ✅ **4 对点即可求解**
- ✅ **OpenCV 一行 findHomography**
- ✅ **应用场景极广**
- ✅ **RANSAC 版本鲁棒**

## 它的短板

- ⚠️ 仅对平面场景/纯旋转严格成立
- ⚠️ 有深度差时错位
- ⚠️ 点共线退化
- ⚠️ warpPerspective 易出画布
- ⚠️ DLT 不归一化数值差

## 本算法档案包含 7 个页面

| 页面 | 内容 |
|---|---|
| [论文故事](/algorithms/homography/paper) | 作者、发表时间、核心贡献、为什么它会被提出 |
| [核心概念](/algorithms/homography/concepts) | 用生活比方讲清它依赖的关键概念 |
| [算法流程](/algorithms/homography/architecture) | 一步步走通算法全流程，配 mermaid 图 |
| [源码实现](/algorithms/homography/source) | OpenCV 调用 + NumPy 手写最小实现 |
| [踩坑清单](/algorithms/homography/painpoints) | 新手最常犯的 N 个错误 |
| [调参口诀](/algorithms/homography/tricks) | 参数怎么选、实战技巧、性能优化 |

## 相关链接

- 返回 [六大分支总览](/branches/)
- [单应矩阵所在分支](/branches/geometry/)
- [算法档案总览](/algorithms/)


---

## 🚀 动手体验（浏览器里直接玩，不用装环境）

> 下面这些组件都在**你的浏览器本地运行**，不上传任何图片、也不用安装 OpenCV 或写代码。

### 🎮 再跑真机：在浏览器里真跑 单应矩阵

换成你自己的照片也行；下面还会**实时生成**对应的 Python / C++ / JavaScript 代码，拖参数时代码同步更新。

<ClientOnly>
  <OpencvPlayground initial-algo="homography" compact />
</ClientOnly>

> 想换示例图、上传自己的照片、或切换别的算法？去 [🎮 真机实验室](/playgrounds/)；想看完整的 14 个数学原理互动？去 [🧪 原理实验室](/math-lab/)。
