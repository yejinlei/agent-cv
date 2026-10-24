# agent-cv · 传统计算机视觉本体论研究站

> 一个对标 [agent-yolo](https://yejinlei.github.io/agent-yolo/) 的传统 CV 知识工程。
> 用知识本体（JSON Schema + YAML）驱动内容，覆盖 1963–2012 年非深度学习视觉技术栈。

## 这是什么

agent-yolo 研究的是**一个算法家族的版本迭代**（YOLOv1 → YOLOv26）。
agent-cv 研究的是**整个传统视觉技术体系**——从 Larry Roberts 的边缘检测到 AlexNet 前夜，
六大技术分支的横向谱系与纵向演化。

## 六大分支（横轴）

| 分支 | 内容 |
|---|---|
| ① 图像处理 | 滤波、阈值、形态学 |
| ② 特征检测 | 边缘、角点、斑点 |
| ③ 特征匹配 | 描述子、鲁棒估计 |
| ④ 图像分割 | 区域聚类、交互式分割 |
| ⑤ 传统检测 | 滑动窗口、Viola-Jones、HOG+SVM、DPM、BoVW |
| ⑥ 几何视觉 | 标定、对极几何、立体视觉、光流 |

另设第 7 条**横跨所有分支**的线：**🔧 工程实现层**（OpenCV API 速查 / 性能与算力账本 / 产线工程化管线）。

## 双轴结构

| 轴 | 切法 | 适合 | 入口 |
|---|---|---|---|
| **纵轴 · 章节体系** | 按抽象层次（低层 → 中层 → 高层），对齐章毓晋《计算机视觉教程》（预备篇 + 第 3–15 章） | 系统学习 | [章体系导览](/chapters/) |
| **横轴 · 技术分支** | 按算法家族（图像处理 / 特征检测 / …） | 检索与对比 | [分支总览](/branches/) |
| **反查 · 场景入口** | 按"我要做什么" | 直接落地 | [场景反查](/scenarios/) |

章与分支正交：`algo-sift` 既属"特征匹配"分支，又同时出现在第 4 章（关键点）与第 6 章（描述子）。

## 知识链路

每个算法都按「论文 → 理论 → 实现 → 实战」组织：

```
algorithms/<name>/
├── index.md          总览：一句话是什么 + 解决什么问题
├── paper.md          论文精读：原始论文的核心思想
├── concepts.md       核心概念：预备知识与关键公式
├── architecture.md   算法流程：分几步，每步在做什么
├── source.md         源码走读：OpenCV 实现的关键代码
├── painpoints.md     实战踩坑：实际使用会踩什么坑
└── tricks.md         调参技巧：每个参数什么意思
```

已收录：**59 个算法**，每个算法 7 页完整档案（总览 / 论文 / 概念 / 流程 / 源码 / 踩坑 / 调参），
覆盖六大分支——从 Sobel 边缘到光束法平差 BA。

## 在线交互 Playground

浏览器里**真机运行**传统 CV 算法，不需要装 OpenCV、不需要 Python、图片不上传服务器：

- 底层是 **OpenCV.js（WebAssembly）**，全部计算在你本机完成
- 支持 **39 种算法**：滤波/增强、边缘与基元、特征检测、图像分割、特征匹配与几何、Viola-Jones 人脸检测
- 可切示例图、上传自己的照片、拖滑条调参、实时看耗时

入口：[🎮 交互 Playground](/playgrounds/)

## 技术栈

| 能力 | 方案 |
|---|---|
| 文档 | **VitePress 1.6.4**（Markdown 原生） |
| 谱系图 | D3.js |
| 流程图 | Mermaid |
| 公式 | KaTeX |
| 本体 | JSON Schema + YAML 实例 |
| 部署 | GitHub Pages |

与 agent-yolo 完全对齐，**零学习成本迁移**。

## 本地运行

```bash
npm install
npm run docs:dev        # 开发预览：http://localhost:5173
npm run docs:build      # 构建
npm run docs:preview    # 预览构建产物
```

## 目录结构

```
agent-cv/
├── docs/
│   ├── index.md                    首页
│   ├── learning-path.md            学习路径（双轴总图）
│   ├── glossary.md                 术语表
│   ├── global/                     系列演化（家族树/时间线/演化事件/外部影响）
│   ├── ontology/                   本体（Schema/实体类型/关系/**实例索引**）
│   ├── chapters/                   纵轴：预备篇 + 第 3–15 章导览（14 页）
│   ├── scenarios/                  场景反查（缺陷/测量/OCR/车牌/人脸/全景）
│   ├── algorithms/                 算法档案（Canny / SIFT / HOG+SVM）
│   ├── branches/                   六大分支 + 工程实现层
│   ├── legacy/                     传承脉络（传统 CV → 深度学习）
│   ├── cases/                      实战案例
│   └── .vitepress/                 配置与主题
└── ontology/
    ├── schema/                     19 个 JSON Schema
    ├── instances/                  123 个 YAML 实例（10 类实体）
    └── validate.py                 校验器
```

## 知识本体

用 **JSON Schema + YAML** 而不是 OWL：够用、可校验、开发者友好。
四层闭环把「论文 → 理论 → 实现 → 实战」串成可机读的引用网络：

```
L0 全局层    Family / Evolution / Timeline / Chapter（纵轴章节）
L1 论文层    Paper（出处可核验）
L2 理论层    Concept（老奶奶也听得懂的通俗解释）
L3 实现层    Algorithm / Operator / Library
L4 实战层    Application / CaseStudy / PainPoint / Trick
```

当前规模：**297 个实例，覆盖 10 类实体**（算法 60 / 论文 69 / 概念 80 /
算子 24 / 应用 8 / 案例 3 / 踩坑 20 / 技巧 15 / 库 5 / **章节 13**）。

校验本体一致性：

```bash
cd ontology
pip install pyyaml jsonschema
python3 validate.py
```

校验器会检查：字段类型、枚举取值、跨文件引用的 ID 是否存在。
设计上采用**渐进式覆盖**——被引用但尚无实例的 ID 只列为「悬空引用」提示，
不算校验失败；而填错字段（如把年份写成字符串）会直接报错。

在线浏览全部实例：[本体实例索引](/ontology/instances)

## 本地运行与部署

```bash
npm install            # 安装依赖（国内可加 --registry=https://registry.npmmirror.com）
npm run docs:dev       # 本地开发：http://localhost:5173/agent-cv/
npm run docs:build     # 构建静态站点到 docs/.vitepress/dist
npm run docs:preview   # 本地预览构建产物
```

部署到 **GitHub Pages（无服务器）**：仓库已带好
`.github/workflows/deploy.yml`，只需在仓库 Settings → Pages 里把 Source 选为
**GitHub Actions**，之后每次 push 到 `main` 自动构建发布。

::: tip 注意 base 路径
`docs/.vitepress/config.mts` 里的 `base` 为 `/agent-cv/`，对应仓库名。
如果你的仓库名不同，请同步修改这一行，否则静态资源会 404。
:::

> Playground 用到的 `docs/public/lib/opencv.js`（约 11 MB）与 Haar 人脸模型
> 会随仓库一起提交，克隆时体积偏大；它们是 Playground 能离线运行的唯一依赖。

## 与 agent-yolo 的差异

| 维度 | agent-yolo | agent-cv |
|---|---|---|
| 研究对象 | 单一算法家族 | **整个技术体系** |
| 组织方式 | 按版本迭代 | **按技术分支** |
| 主线 | 纵向演化 | **横向谱系 + 纵向历史** |
| 时间跨度 | 2015–2026 | **1963–2012** |
| 硬件定位 | GPU 必需 | **CPU 可跑、边缘可用** |

## 为什么要做这个

1. **传统 CV 至今不可替代**：低算力、无 GPU、可解释、小样本
2. **知识正在流失**：经典算法的"为什么"被"调 API"淹没
3. **传承脉络清晰**：多尺度金字塔 → FPN、NMS → YOLO 的检测头
4. **工程实用**：工业缺陷检测、边缘部署等场景，传统 CV 依然是性价比之王

## License

MIT
