# Horn-Schunck 稠密光流

<AlgorithmCard
  name="Horn-Schunck 稠密光流"
  enName="Horn-Schunck Optical Flow"
  chapter="第11章 · 运动分析"  chapterLink="/chapters/ch11-motion"
  branch="geometry"
  year="1981"
  author="Berthold K.P. Horn / Brian G. Schunck"
  paper="https://scholar.google.com/scholar?q=Determining+Optical+Flow"
  level="advanced"
  tagline="给光流加上全局平滑约束，用变分法求每个像素的运动，开创稠密光流学派"
  analogy="LK 光流像一个独立办案的刑警，每个小窗口自己算自己的；Horn-Schunck 像一个总指挥，要求所有像素的运动方向「差不多」，不能突然跳变，然后全局求解出一幅密密麻麻的运动箭头图"
  scene="稠密运动场估计、流体运动分析、医学影像序列分析、变分光流研究基准、视频慢动作插帧（传统方法）"
  :pros='["输出稠密光流（每像素都有）", "全局一致，平滑无噪", "开创变分光流学派", "理论优美（能量最小化）", "作为基准方法"]'
  :cons='["迭代求解较慢", "对大运动不适用（需金字塔）", "运动边界处过度平滑", "亮度恒定假设苛刻", "工程上 Farnebäck/DIS 更常用"]'
/>

## 一句话理解

给光流加上全局平滑约束，用变分法求每个像素的运动，开创稠密光流学派。LK 光流像一个独立办案的刑警，每个小窗口自己算自己的；Horn-Schunck 像一个总指挥，要求所有像素的运动方向「差不多」，不能突然跳变，然后全局求解出一幅密密麻麻的运动箭头图。

```mermaid
flowchart LR
  A["输入图像"] --> B["Horn-Schunck 稠密光流"]
  B --> C["输出结果"]
```

## 生活类比

LK 光流像一个独立办案的刑警，每个小窗口自己算自己的；Horn-Schunck 像一个总指挥，要求所有像素的运动方向「差不多」，不能突然跳变，然后全局求解出一幅密密麻麻的运动箭头图

## 它解决什么问题

稠密运动场估计、流体运动分析、医学影像序列分析、变分光流研究基准、视频慢动作插帧（传统方法）。

在传统 CV 的六分支体系中，Horn-Schunck 稠密光流 属于 **geometry** 分支，主要解决的是该分支中给光流加上全局平滑约束，用变分法求每个像素的运动，开创稠密光流学派的问题。

## 核心优点

- ✅ **输出稠密光流（每像素都有）**
- ✅ **全局一致，平滑无噪**
- ✅ **开创变分光流学派**
- ✅ **理论优美（能量最小化）**
- ✅ **作为基准方法**

## 它的短板

- ⚠️ 迭代求解较慢
- ⚠️ 对大运动不适用（需金字塔）
- ⚠️ 运动边界处过度平滑
- ⚠️ 亮度恒定假设苛刻
- ⚠️ 工程上 Farnebäck/DIS 更常用

## 本算法档案包含 7 个页面

| 页面 | 内容 |
|---|---|
| [论文故事](/algorithms/horn-schunck/paper) | 作者、发表时间、核心贡献、为什么它会被提出 |
| [核心概念](/algorithms/horn-schunck/concepts) | 用生活比方讲清它依赖的关键概念 |
| [算法流程](/algorithms/horn-schunck/architecture) | 一步步走通算法全流程，配 mermaid 图 |
| [源码实现](/algorithms/horn-schunck/source) | OpenCV 调用 + NumPy 手写最小实现 |
| [踩坑清单](/algorithms/horn-schunck/painpoints) | 新手最常犯的 N 个错误 |
| [调参口诀](/algorithms/horn-schunck/tricks) | 参数怎么选、实战技巧、性能优化 |

## 相关链接

- 返回 [六大分支总览](/branches/)
- [Horn-Schunck 稠密光流所在分支](/branches/geometry/)
- [算法档案总览](/algorithms/)
