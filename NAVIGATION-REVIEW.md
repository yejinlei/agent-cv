# agent-cv 导航 / 内容架构问题清单与整改建议

> 扫描范围：`docs/.vitepress/config.mts`、`docs/index.md`、`docs/learning-path.md`、`docs/global/*.md`（family / evolutions / timeline / external-techniques / evolution-story）、`docs/ontology/schema.md`、`docs/playgrounds/index.md`、`docs/operators/index.md`、`docs/scenarios/index.md`、`docs/glossary.md`、`docs/versions/index.md`、`docs/legacy/index.md`、`docs/branches/`、`docs/chapters/`、`docs/cases/`、`docs/derivatives/`、`docs/math-lab/`、`docs/for-beginners/` 目录及入口页。

---

## 一、问题清单

### 1. 内容重复 / 同一信息多处冗余罗列

| # | 重复内容 | 出现位置 | 问题 |
|---|---|---|---|
| R1 | **"六大分支"（图像处理/特征检测/特征匹配/分割/检测/几何视觉）+ ⑦ 工程实现层** | ① 顶栏 nav「🧭 学习」下拉 55–62 行；② 首页「🗂️ 六大技术分支」整张卡片区（index.md 96–114）；③ 首页「双轴阅读方式」（index.md 88–94）；④ family.md 「一句话总览 + 六条主干的关系 + 分支谱系详解」三段（family.md 8–107）；⑤ `/branches/` 总览页；⑥ `/versions/index.md`「六大分支的版本索引」（versions/index.md 16–106）；⑦ `/learning-path.md` 末尾的双轴映射表（learning-path.md 106–126） | 同一组"六分支"清单以不同粒度被写了 **至少 6 次**。其中 versions/index.md 与 /algorithms/ 侧边栏几乎是重复罗列，family.md 自身就把这棵树用 mermaid 画了两遍（家族树 + 依赖关系）+ 分支详解，而 /branches/ 又重列一遍。**任何一次分支改名/增删，要同时改 6 处**，维护成本高且易漂移。 |
| R2 | **"纵轴 15 章 / 章节体系"** | ① 顶栏 nav 「🧭 学习」下拉 52–53 行；② 首页 features「学习路径（纵轴）」（index.md 30–31）；③ 首页「双轴阅读方式」（index.md 88–94）；④ `/learning-path.md` 学习路径总图 + 三层分章表 + 末尾推荐路径；⑤ `/chapters/` 总览页及侧边栏；⑥ `/versions/index.md` 与 /scenarios/ 里的"涉及章"列 | 章列表也重复 4 次以上，且 learning-path.md 与 /chapters/ 总览页功能高度重合（都在展示"第 X 章讲什么")。 |
| R3 | **"算法演化 / 痛点追踪链"** | ① family.md 末尾「全算法痛点追踪链」mermaid（family.md 251–269）+「经典算法版本逐项对比」大表（family.md 273–289）；② `/global/evolutions.md` 演化分支详解；③ `/global/evolution-story.md` 决策树 + 每个决策点叙事；④ `/global/timeline.md` 时间线 + 分期；⑤ `/versions/index.md` 「全算法对比大表」（versions/index.md 108–171） | **5 个页面同时在讲算法如何演化**：family.md 里有"演化表 + 对比大表"，evolutions.md 又做了一次分支演化，evolution-story.md 又用"决策"叙事重写一遍，timeline 按年份排，versions 又做版本索引。`family.md` 290 行里 60% 内容与其他页重复；**Sobel→Canny→Harris→SIFT→SURF→ORB、VJ→HOG→DPM→YOLO 这两条核心演化链在至少 4 页重复出现**。 |
| R4 | **"传统 CV → 深度学习传承"** | ① 顶栏「🧭 学习」下的「🧬 传承脉络」；② family.md 「与深度学习的关键接口」+「三代检测方法对比」+ 「传统 CV 被深度学习继承/改造/抛弃/解决什么痛点」四张表 + 最后一张三代对比 mermaid（family.md 108–245）；③ `/legacy/index.md` 整篇；④ index.md 「🔗 传统 CV 与深度学习的传承」mermaid（index.md 145–160）；⑤ /global/evolutions.md 末尾「与深度学习的交接」 | 五处都在讲 NMS→YOLO、金字塔→FPN、滑窗→Anchor。**family.md 这一节长达 135 行，几乎与 legacy/index.md 完全重复**（两张 mermaid 图结构一模一样）。 |
| R5 | **"59 个算法对比大表"** | ① 顶栏 nav 链接 `/versions/`（第 72 行）；② 首页按钮「📦 版本对比大表」（index.md 19–20）；③ family.md 「经典算法版本逐项对比」14 列大表（family.md 273–289）；④ /versions/index.md 「全算法对比大表」（versions/index.md 108–171） | 两张大表结构和字段高度相似，一处在 global/family.md（只列 14 个代表），一处在 versions/index.md（列 59 个），用户会困惑「到底看哪个」。family.md 末尾的 14 列短表完全可以删除，只留一个跳转到 /versions/ 的链接。 |
| R6 | **"核心算法直链"（Canny/Harris/SIFT/RANSAC/LK/VJ/张氏标定）** | ① 顶栏「🧭 学习」下拉「高频算法直达」65–71 行；② 首页 features 不直链、但首页「精选算法档案」三张卡（Canny/SIFT/HOG）直链（index.md 135–143）；③ /algorithms/ 侧边栏 50+ 个算法全列 | 顶栏直接列 7 个算法作为一级下拉项，**这些链接应该是"搜索+卡片直达"的事，不该占主导航位**。并且列表是硬编码的，新增算法就要改 nav。 |
| R7 | **"本体 / 知识图谱 / Schema"概念** | ① 首页「🕸️ 知识本体」段（index.md 162–170）；② 顶栏「🧰 工具」最末项「📐 本体 Schema」（config.mts 第 95 行，link `/ontology/schema`）；③ 侧边栏独立 `/ontology/` 分组；④ 各个 global/* 页（family/evolutions/timeline）反复自称为"本体"实体；⑤ /ontology/schema.md 本身 | "本体"这个概念对普通读者是个偏学术的词（OWL/Ontology），在首页、导航、正文里反复讲"本站是一个本体"，**新用户只会困惑"我要看算法，为什么反复告诉我这是本体"**。本体/Schema 是工程实现层概念，应降级为"关于本站"类内容。 |
| R8 | **"小白入门 5 页"** | ① 顶栏独立一级入口「🌱 小白入门」（config.mts 第 38 行）；② 首页 hero 第一个按钮（index.md 13–14）；③ 侧边栏独立 `/for-beginners/` 分组；④ glossary.md 开头「第一次来？先读小白入门」；⑤ /playgrounds/index.md、/operators/index.md 都提示"先看小白入门/原理实验室" | 入口层级过多；5 页内容本身是对其他内容的"白话导读"，并不是平行的第五大主模块。 |

---

### 2. 入口层级不合理

| # | 问题 | 涉及路径 | 说明 |
|---|---|---|---|
| L1 | **顶栏 4 个一级项里就有 1 个 ("🌱 小白入门") 是导读性质**，而真正承载内容的"章节 / 分支 / 算法档案 / 场景"全挤在「🧭 学习」一个巨型下拉里 | config.mts nav | 「🧭 学习」下拉 **共 29 个 items**，包含 5 个分隔线标题 + 6 个分支 + 7 个高频算法直链 + 数学实验室 + 章体系 + 全局视图。这是典型的"抽屉塞爆"——把所有东西都扔一个菜单里，新用户打开下拉会眩晕。顶栏一级菜单应该是 4–5 个**按用户意图**划分的分组，而不是"一个万能抽屉 + 其他零散入口"。 |
| L2 | **重要入口藏得太深**：实战案例 `/cases/`、衍生实现 `/derivatives/`、故障排查 `/global/troubleshooting`、对比矩阵 `/global/compare-matrix`、基准数据 `/global/benchmarks`、数据流全景 `/global/data-flow`、概念反向索引 `/global/concepts` | config.mts nav（藏在「🧰 工具」下拉最深处）、sidebar（/cases/、/derivatives/ 没有出现在任何主导航侧边栏分组里，只有切到该目录下才显示） | "故障排查手册"、"对比矩阵"、"基准数据"是工程师高频使用页，却在「🧰 工具」下拉的第 2/3 屏；/cases/ 实战案例只有 2 篇，但从首页 features 的「🛠️ 实战案例」卡片点过去**没有侧边栏**（因为 /cases/ 是 sidebar 的独立 key，且不与其他分组共存，见下文 S1）；/derivatives/ 更是几乎不可见。 |
| L3 | **`/algorithms/` 目录承担 59 个算法档案，但顶栏与侧边栏里"算法档案"入口不直接可见** | config.mts：/algorithms/ 没有独立 nav key；sidebar 第 308 行 `/algorithms/` 分组以"版本总览/对比大表（link `/versions/`）"起头，非常怪异——进入 /algorithms/ 页面时侧边栏显示的是"算法档案（完整版）"但第一项链接跳转到 `/versions/` | 算法档案是整个站**最深、最核心**的内容（59 个算法 × 7 页 = ~400 页），但主导航里它**只以"版本对比大表"和 7 个直链的形式出现**，没有"算法档案总览"的清晰入口。事实上 **`/algorithms/` 目录下根本没有 index.md**（ls 显示 algorithms 有 61 个子目录，没有 index.md），用户访问 `/algorithms/` 会 404 或跳到 /versions/。这是最严重的结构缺陷：**核心内容层没有总入口**。 |
| L4 | **`/math-lab/`（数学原理实验室，14 个互动 demo）入口等级偏低** | nav 里藏在「🧭 学习」第 50 行；首页上它是「🧪 数学概念互动实验室」单张卡（index.md 116–121），位置夹在"六分支卡"和"Playground"之间 | 对小白用户最友好、最有差异化的互动内容，应该与「真机实验室」并列为"动手玩"的两大入口，而不是被塞在"学习"抽屉里作为一行文字。 |
| L5 | **两个"实验室"（math-lab vs playgrounds）关系不清、入口分散** | `/math-lab/` vs `/playgrounds/`；playgrounds/index.md 用一张表专门解释"为什么有两个实验室"（playgrounds/index.md 41–52） | 连站点自己都要写一段 FAQ 解释两者差异，说明命名和入口有问题。应合并为一个「动手实验室」入口，内部再分"原理 Demo"和"真机 OpenCV"两个 Tab。 |
| L6 | **`/ontology/` 作为顶级 sidebar key，却只有 4 个页面，且对普通读者几乎无用** | config.mts sidebar `/ontology/`，145–155 行 | Schema/实体/关系/实例索引是**工程元信息**，放在与「章节体系」「六分支」平级的侧边栏是拔高了它的重要性。用户的主路径是"学算法"，不是"研究本站本体建模"。应挪到「关于 / 附录」。 |
| L7 | **顶栏用 emoji 过多，分隔线用「── xxx ──」伪装成分组，但其实下拉里没有分组能力，视觉噪声大** | config.mts 37–97 行 | 「── 一图看懂全貌 ──」「── 搞懂数学原理 ──」「── 按学习顺序 · 纵轴 ──」「── 按算法分支 · 横轴 ──」「── 高频算法直达 ──」……这是在用文字横线模拟子分组，但 VitePress nav 的 items 是扁平的，视觉上是一堆破折号。建议改用 VitePress 真正的嵌套分组能力。 |
| L8 | **`/glossary` 是单文件（glossary.md，716 行）**，但 nav 里叫「📖 术语表」，与 `/global/concepts`「概念反向索引」、`/operators/` 算子词典三者边界模糊 | config.mts nav 第 82、83 行 | glossary 是"按分类列术语"，concepts 是"反向索引"，operators 是"原子算子"，三个都是查东西但路径分散在 nav 三个位置（工具/查词）、sidebar 三个分组。 |

---

### 3. 命名不一致 / 边界模糊

| # | 问题 | 涉及名称 | 说明 |
|---|---|---|---|
| N1 | **链接 / 文件名 与 侧边栏文字不一致** | `/global/family-tree.md`（用户 query 里写的）实际文件是 `/global/family.md`；`/global/inheritance.md`（用户 query 里写的）实际文件是 `/legacy/index.md`；`/global/ontology-schema.md`（用户 query 里写的）实际是 `/ontology/schema.md` | 你（派发任务时）都把路径记错，恰好**证明命名本身不统一**：nav 里叫「🌳 算法家族树」（link `/global/family`，不是 family-tree）、叫「🧬 传承脉络」（link `/legacy/`，不是 global/inheritance）、叫「📐 本体 Schema」（link `/ontology/schema`，不在 global 下）。**建议把"传承脉络"与"知识本体"都收敛到 `/global/` 下，避免目录散落**。 |
| N2 | **"学习路径" vs "章节体系" vs "章体系导览" vs "章体系总览" vs "学习路径地图（双轴）"** | nav 中第 43、44、53 行；learning-path.md 标题；/chapters/ 侧边栏标题 "📚 章节体系（纵轴学习路径）" | 同一概念（"按章顺序学"）至少用了 5 个不同名字。建议统一叫「**系统学习路径**」或「**教程（纵轴）**」。 |
| N3 | **"全局"、"全球"、"家族"、"谱系"、"知识图谱"、"本体"几个词混用** | /global/ 目录名；nav 中"全局谱系"（sidebar 124 行）；family.md 标题"传统 CV 家族树"；index.md"🕸️ 知识本体"；schema.md"知识本体 Schema" | 对中文读者，"家族树 / 谱系 / 全局视图 / 知识图谱 / 本体"是 5 个不同的心理模型，却指向同一堆内容（family/evolutions/timeline/external-techniques/evolution-story）。建议这一块统一叫「**全局视图**」或「**知识图谱**」（二选一），内部再分"家族树 / 演化 / 时间线 / 外部影响"。 |
| N4 | **"经典算法速查 / 版本对比 / 算法档案 / 59 算法对比大表 / 高频算法直达"几种叫法** | /versions/ 标题"经典算法版本档案"；nav "📋 59 算法对比大表"（link /versions/）；home hero "📦 版本对比大表"；sidebar "/algorithms/" 组标题"算法档案（完整版）"，第一项又 link 回 /versions/ | 同一个概念（"59 个算法的完整 7 页档案 + 对比表"）被叫作版本 / 档案 / 对比大表 / 速查。建议统一为「**算法档案**」，"对比大表"是算法档案内部的一个 section，不是另一个页面/概念。 |
| N5 | **"真机实验室 / Playground / 真机实验 / 实验室 / 数学实验室 / 原理实验室"** | nav "🎮 真机实验室"；首页"🎮 真实算法 Playground"；playgrounds/index.md 里既有"真机实验室"又有"视频真机实验"又区分"原理实验室" | "实验室"至少指 2–3 种东西，新用户分不清。建议统一："🧪 **互动实验室**"（math-lab + playgrounds 合并为一个入口下两个 Tab）。 |
| N6 | **"算子" vs "算法" 边界没有在导航上给用户一眼看懂的入口** | /operators/ 算子词典 vs /algorithms/ 算法档案 | 作者自己清楚 "算法 = 算子的组合"，但 nav 上"算子词典"放在「🧰 工具」下，"算法档案"却在 nav 里连一个直接入口都没有（L3），用户路径不对称。 |
| N7 | **"工程实现层"作为"第七分支"，但它不是算法家族** | nav 第 62 行「🔧 工程实现层」混在 6 大分支列表里；sidebar /branches/ 分组里它也作为第 7 组出现 | 六大分支是按"算法家族"划分的，工程层是横切关注点（OpenCV API / 性能 / 管线），与前六者不是同构关系，**混在一起会让用户以为它也是第 7 个算法家族**。 |

---

### 4. 侧边栏在跨目录时的"断层 / 跳脱感"

VitePress sidebar 是按**路径前缀**匹配的。当前 config.mts 定义了以下 sidebar key：

```
/for-beginners   → 小白入门 5 页
/learning-path   → 只有一页（总览）
/global/         → 全局谱系 11 页
/ontology/       → 知识本体 4 页
/branches/       → 六大分支+工程层
/chapters/       → 15 章
/scenarios/      → 场景反查
/operators/      → 算子词典
/algorithms/     → 59 个算法
/versions/       → 版本对比（但内容全是跳 /algorithms/）
/cases/          → 实战案例
/legacy/         → 传承脉络
/derivatives/    → 衍生实现
```

| # | 问题 | 触发场景 | 说明 |
|---|---|---|---|
| S1 | **共 13 个 sidebar key，意味着有 13 个"世界"，用户在任意两个之间跳转，侧边栏会完全替换** | 比如从 `/branches/detection/viola-jones` 点「传承到 YOLO」跳到 `/legacy/`，侧边栏瞬间从"六大分支+59 算法"变成"传承脉络 3 页"，丢失上下文 | 尤其严重的几个跳转：① /scenarios/ → /cases/（场景页里的"配套案例"链接）；② /algorithms/*/ → /operators/*（算法页里引用算子）；③ /math-lab/ 没有自己的 sidebar key（math-lab 目录存在但 config.mts 里没配 sidebar，会走默认兜底——实际上 math-lab 没有被任何 sidebar 匹配，进入后侧边栏要么空白要么显示错误分组）；④ /chapters/ 与 /branches/ 是双轴，但互不在对方侧边栏里，用户读章节时完全看不到分支，反之亦然。 |
| S2 | **`/learning-path` 侧边栏只有 1 个 item（自己）** | 用户点"🧭 学习路径地图"进入后，侧边栏几乎是空的 | 学习路径是"总图页"，侧边栏应直接承接章节体系 / 六分支入口，而不是只有它自己。 |
| S3 | **`/versions/` sidebar 所有条目都跳 `/algorithms/`，一旦点击就切换到 `/algorithms/` sidebar** | /versions/index.md 里每个条目都是「（已升级为完整档案）」，链到 /algorithms/xxx/ | 这意味着 `/versions/` 的侧边栏是**一个永远把用户推走的中转页**——用户从 /versions/ 点任何条目都会离开这个 sidebar。这种分组毫无意义：要么把 /versions/ 合并为 /algorithms/ 的顶部"总览表"，要么让 /algorithms/ 和 /versions/ 共用一个 sidebar。 |
| S4 | **`/algorithms/` sidebar 没有分页/分组，59 个算法 + 6 个样板（Canny/SIFT/HOG/Harris/RANSAC/LK/张氏/霍夫/Sobel/Otsu/对极几何/VJ/BoVW/...）全部摊平**，长达 500+ 行 | config.mts 308–1017 行 | 用户滚动侧边栏时要在 50+ 个名字里找算法，没有按分支/按层级分组。事实上 59 个算法属于 6 个分支，但 sidebar 里并没有按分支分组。同时侧边栏第一项"版本总览/对比大表"指向 /versions/，又触发 S3 的跳脱。 |
| S5 | **`/math-lab/` 目录没有在 sidebar 中配置** | config.mts 里没有 `/math-lab/` 这一 sidebar key | 进入 math-lab 页面时，VitePress 会按最长前缀兜底，可能命中 `/` 根路径（没有配置根路径 sidebar），导致侧边栏完全消失——这是一个配置缺口。 |
| S6 | **根路径 `/`（首页 index.md）没有 sidebar 配置** | config.mts 100 行开始的 sidebar 没有 `/` key | 首页不显示侧边栏（首页 hero 不需要，可以接受），但从首页跳到任意二级页时侧边栏"突然出现"，视觉上有跳变——不算严重，但建议配一个简单的"首页"占位 key。 |
| S7 | **跨目录的"返回上级"路径不存在** | 例如从 /algorithms/canny/ 无法一眼回到 /versions/ 总表或 /branches/ 对应分支；从 /operators/gaussian-blur/ 无法一眼回到哪些算法用了它 | sidebar 只展示当前 key 下的内容，没有"上下文导航"组。建议每个算法页侧边栏顶部加 2–3 个面包屑式链接：「↰ 返回算法档案总表」「↰ 所属分支：② 特征检测」。 |
| S8 | **/global/ 和 /ontology/ 分成两个 sidebar key，但内容高度相关**（都是"全局/元信息"页） | /global/ 里有 family/evolutions/timeline/external-techniques/evolution-story，/ontology/ 里是 schema/entity-types/relations/instances | 读者视角"家族树"和"本体 Schema"都是"整体怎么组织知识"的元信息，却被分成两个侧边栏，切换时跳脱。建议合并。 |

---

### 5. 首页（index.md）引导问题

| # | 问题 | 位置 | 说明 |
|---|---|---|---|
| H1 | **Hero 行动按钮 5 个、主次不清**：2 个 brand + 3 个 alt | index.md 11–26 | 新用户第一眼看到 5 个按钮，两个蓝的优先级相同（"小白入门"和"开始学习路径"），三个灰的里又有"Canny 样板"这种直达单个算法的低优先级入口。**首屏最多给 2 个明确的行动**：① 我是新手 → 入门；② 我想系统学 → 学习路径；③ 我要找算法 → 算法档案/实验室可以放在下方 feature 卡片里。 |
| H2 | **首屏之后，信息流顺序混乱**：features（6 格）→ "这是什么" → "四层闭环" → "全景家族树"（FamilyTree 组件）→ "双轴阅读方式" → "六大技术分支"（6 张 AlgorithmCard）→ "数学实验室" → "真机 Playground" → "精选算法档案" → "传承与深度学习" → "知识本体" | index.md 28–170 | 出现**重复层级跳跃**：features 里已经说了「学习路径 / 技术分支 / 论文精读 / 源码走读 / 实战案例 / 传承脉络」，但下面又用整块篇幅重新讲"双轴"和"六分支"和"精选算法"。家族树组件直接插在中间，**用户刚看完"四层闭环"就被一张超大的图打断**。 |
| H3 | **"这是什么" + "四层闭环" 位置太靠前、偏抽象** | index.md 49–77 | 新用户还没搞清楚"这个站能帮我做什么"，就被 L1→L2→L3→L4 的本体论四段论和 mermaid 图轰炸。"本体"、"可校验"、"建模"这些词应该放到「关于本站」页，或放到页面下方。 |
| H4 | **"全景家族树"组件 `<FamilyTree />` 与下方"六大技术分支"6 张卡内容重复** | index.md 79–114 | FamilyTree 画的就是六分支的树，紧接着下面又用 6 张卡片把六分支讲一遍，一次交互一次卡片，信息密度翻倍但信息增量为零。 |
| H5 | **两个"实验室"入口（math-lab 和 playgrounds）被六大分支卡片隔开** | index.md 116–128 | 数学实验室在六分支之前？不，看顺序：六分支卡片 → 数学实验室 → 真机实验室。这两个强互动入口被拆成两处，且真机实验室在精选算法档案之前还是之后都显得"突然冒出来"。 |
| H6 | **"精选算法档案"只放了 3 张卡（Canny/SIFT/HOG），但首页 hero 里已经有"Canny 样板"单独按钮** | index.md 25–26、130–143 | Canny 重复出现两次。 |
| H7 | **"🕸️ 知识本体"段落放最底部，但使用了"站点最大差异化"这种强烈措辞** | index.md 162–170 | 这一段是**作者视角的价值主张**（"我们做了本体建模"），不是**用户视角的价值**（"你能在这里学到什么"）。放最末没问题，但措辞应改为"附录：关于本站知识组织方式"。 |
| H8 | **新用户"第一步该去哪"不明确** | index.md 整体 | hero 同时推"小白入门（5 页看懂）"和"开始学习路径"，这两个入口面向同一人群（新手）但路径不同，且没解释"5 页看完之后去哪"。建议把"小白入门"明确为「5 分钟了解 CV 是什么（快速科普）」，"学习路径"明确为「系统学习教程（按章走）」，用一句话区分。 |
| H9 | **缺少"老用户/有明确目的"的快速入口区** | index.md | 工程师常用的"按场景反查 / 算子词典 / 算法对比 / 真机实验室"没有组成一个"我要找 XX"的快捷区，而是散落在 features 和下方段落里。 |

---

## 二、整改建议

### 建议 A：精简顶栏方案（一级菜单 5 项）

原则：① 一级菜单按**用户意图**组织（学/查/玩/关于），不按内部结构组织；② 下拉采用**嵌套分组**而非破折号伪分组；③ 高频算法直链从主导航移除（改由搜索 + 算法档案首页承担）。

```
🌱 入门           → /for-beginners/      （保留独立一级：5 页快速科普，新手唯一入口）
📚 学习           → [下拉分组]
🎯 查资料         → [下拉分组]           （原"🧰 工具"改名为"查资料"，语义更清晰）
🧪 动手玩         → [下拉分组]           （合并 math-lab + playgrounds）
ℹ️ 关于           → [下拉分组]           （原"全局视图/本体/传承/衍生/案例"等元信息集中于此）
```

#### 「📚 学习」下拉分组（3 组，不超过 12 项）：

```
── 阅读路径 ──
  🧭 学习路径总图          → /learning-path
  📚 按章教程（纵轴15章）  → /chapters/
  🌿 算法分支（横轴6族）   → /branches/

── 算法档案 ──
  📄 59 个算法档案总览     → /algorithms/            ← 补建 /algorithms/index.md！
  📊 算法对比大表          → /versions/#comparison   ← 作为锚点
  🔧 工程实现层            → /branches/engineering/

── 延伸阅读 ──
  🧬 传统 CV → 深度学习传承 → /legacy/
```

> 移除项：原 nav 里 7 个高频算法直链（Canny/Harris/SIFT/RANSAC/LK/VJ/张氏）、"🗺️ 学习路径地图（双轴）"与"🧭 学习路径"的重复项、"🌳 算法家族树 / ⏳ 演进时间线"移到"ℹ️ 关于 / 全局视图"。

#### 「🎯 查资料」下拉（3 组，约 12 项）：

```
── 按用途查 ──
  🎯 场景反查（要做XX用哪个算法）→ /scenarios/
  🌳 算法选型决策树             → /global/choose-algorithm
  💼 实战案例                   → /cases/

── 按概念查 ──
  🧱 算子词典                   → /operators/
  📖 术语表                     → /glossary
  🔍 概念反向索引               → /global/concepts

── 对比与参考 ──
  📊 算法对比矩阵               → /global/compare-matrix
  📏 基准数据                   → /global/benchmarks
  🌊 数据流全景                 → /global/data-flow
  🚨 故障排查手册               → /global/troubleshooting
```

#### 「🧪 动手玩」下拉（2 项，直接并列）：

```
🧪 原理实验室（拖滑块懂数学）   → /math-lab/
🎮 真机实验室（OpenCV.js 跑）  → /playgrounds/
```

> 两个实验室在顶栏就并排放，用户一眼看出区别；playgrounds/index.md 里那段"为什么有两个实验室"的 FAQ 可以保留为页内说明，但不需要作为导航设计缺陷的补丁。

#### 「ℹ️ 关于」下拉（元信息，低频访问）：

```
── 知识图谱 ──
  🌳 算法家族树       → /global/family
  ⏳ 发展时间线       → /global/timeline
  📖 演进故事         → /global/evolution-story
  🔀 技术演化事件     → /global/evolutions
  🌐 外部技术影响     → /global/external-techniques

── 本站架构 ──
  📐 知识本体 Schema  → /ontology/schema
  🔀 衍生实现（OpenCV/HALCON/嵌入式）→ /derivatives/
  🐙 GitHub           → https://github.com/...
```

> **关键合并动作**：
> - 原「🧰 工具」里除"查词"和"选型对比"的 5 项（benchmarks/compare-matrix/data-flow/troubleshooting/evolution-story/external-techniques）拆到"查资料"或"关于"；
> - **原 nav 的"学习"下拉从 29 项减到 9 项**；
> - 本体 Schema 从首页和主导航的显眼位置降级到"关于本站架构"。

---

### 建议 B：侧边栏分组方案（从 13 个独立 key → 5 个稳定侧栏）

核心思想：**减少 sidebar key 数量，让用户在同一条任务线上时侧边栏不跳变**；跨任务线时用顶部面包屑而非完全重置。

#### B1. `/for-beginners/` → 新手世界（保留独立侧边栏）

- 仅包含 5 页入门。
- 末页（p5-when-to-use）结尾处**显式链接到「学习路径」**，作为新手出口。
- 其他任何页面不进入此 sidebar。

#### B2. `/learning-path` 不再单独作为 sidebar key，合并入「学习」主侧栏

把 `/learning-path`、`/chapters/`、`/branches/`、`/branches/engineering/` 合并到**一个 sidebar key `/learn/`**（注意：需要让这些路径共享一个 sidebar。由于 VitePress 按前缀匹配，可以把 learning-path 挪到 `/learn/learning-path.md`、chapters 保持但在 config 里做多个 key 指向同一 sidebar 配置——或简单地把 learning-path 改为 `/chapters/learning-path` 并配置 `/chapters/` 和 `/branches/` 都使用同一组 sidebar 项）。具体结构：

```
📚 学习
├─ 🧭 学习路径总图        → /learning-path
├─ 📖 推荐阅读路径       → /learning-path#recommended （锚点）
│
├─ ── 教程纵轴 · 15 章 ──
│  ├─ 预备知识（第 1–2 章）→ /chapters/ch01-foundation
│  ├─ 🟦 低层视觉
│  │   ├─ 第3章 图像预处理 → /chapters/ch03-preprocessing
│  │   └─ 第4章 基元检测   → /chapters/ch04-primitives
│  ├─ 🟩 中层视觉
│  │   └─ ...（第5–8章）
│  └─ 🟥 高层视觉
│      └─ ...（第9–15章）
│
├─ ── 技术横轴 · 6 大分支 ──
│  ├─ ① 图像处理           → /branches/image-processing/
│  ├─ ② 特征检测           → /branches/feature-detection/
│  ├─ ③ 特征匹配           → /branches/feature-matching/
│  ├─ ④ 图像分割           → /branches/segmentation/
│  ├─ ⑤ 目标检测           → /branches/detection/
│  └─ ⑥ 几何视觉           → /branches/geometry/
│
└─ ── 工程横切层 ──
    └─ 🔧 工程实现         → /branches/engineering/
```

> 这样用户读章节、读分支、读学习路径，**侧边栏始终稳定**，能看到"双轴"全貌。

#### B3. `/algorithms/` 与 `/versions/` 合并为一个 sidebar key `/algorithms/`

- **必须补建 `/algorithms/index.md`**（现在没有，是 404 风险），作为"算法档案总览"，把 /versions/index.md 的"六大分支版本索引 + 全算法对比大表"**全部搬过来**，/versions/ 路径做跳转或直接废除。
- 侧边栏按分支分组（不再摊平 59 个算法）：

```
📄 算法档案
├─ 📊 总览与对比大表       → /algorithms/
├─ 🔵 图像处理（N 个）     → 折叠组：...算法列表
├─ 🟢 特征检测（N 个）     → 折叠组
├─ 🟠 特征匹配（N 个）     → 折叠组
├─ 🟣 图像分割（N 个）     → 折叠组
├─ 🔴 目标检测与跟踪（N个）→ 折叠组
└─ 🩵 几何视觉（N 个）     → 折叠组
```

- 每个算法子页**侧边栏顶部**加 3 个面包屑：「↰ 档案总览」「↰ 所属分支：② XXX」「↰ 对应章节：第 X 章」。
- 废除独立的 /versions/ sidebar key（避免 S3 的跳脱）。

#### B4. `/scenarios/`、`/operators/`、`/cases/`、`/glossary`、`/global/concepts` 等"工具/查资料"类页面合并为一个 sidebar key `/reference/`

```
🎯 查资料
├─ 🎯 场景反查             → /scenarios/
│   └─ ...6 个场景子页
├─ 🧱 算子词典             → /operators/
│   └─ ...14 个算子
├─ 📖 术语表               → /glossary
├─ 🔍 概念反向索引         → /global/concepts
├─ 🌳 算法选型决策树       → /global/choose-algorithm
├─ 📊 对比矩阵             → /global/compare-matrix
├─ 📏 基准数据             → /global/benchmarks
├─ 🌊 数据流全景           → /global/data-flow
├─ 🚨 故障排查手册         → /global/troubleshooting
└─ 💼 实战案例
    ├─ 案例总览            → /cases/
    ├─ 工业零件缺陷检测    → /cases/industrial-defect
    └─ 嵌入式边缘部署      → /cases/edge-deployment
```

> 这样用户从"我要做缺陷检测"跳到"工业缺陷案例"侧边栏不跳变（解决 S1 的 scenarios↔cases 断层）。

#### B5. `/math-lab/`、`/playgrounds/` 合并为一个 sidebar key `/labs/`

```
🧪 动手实验室
├─ 🏠 实验室总览           → /labs/（或保留 math-lab 作为默认）
├─ 🧪 原理实验室           → /math-lab/
│   └─ ...14 个原理 tab（可以在一页内用 tab 组件，不必拆多页）
└─ 🎮 真机实验室           → /playgrounds/
    └─ ...39 算法工作台 + 6 个视频实验
```

- **给 /math-lab/ 补 sidebar 配置**（解决 S5）。

#### B6. `/global/`、`/ontology/`、`/legacy/`、`/derivatives/` 合并为一个 sidebar key `/about/`

```
ℹ️ 关于本站 / 知识全局
├─ 🌳 算法家族树           → /global/family
├─ ⏳ 发展时间线           → /global/timeline
├─ 📖 演进故事             → /global/evolution-story
├─ 🔀 技术演化事件         → /global/evolutions
├─ 🌐 外部技术影响         → /global/external-techniques
├─ 🧬 传承脉络（→ 深度学习）→ /legacy/
│   ├─ NMS → YOLO
│   └─ 图像金字塔 → FPN
├─ 🔀 衍生实现             → /derivatives/
└─ 📐 知识本体 Schema      → /ontology/schema
    ├─ 实体类型详解
    ├─ 关系定义
    └─ 实例索引
```

> 关键动作：**把 /legacy/ 和 /ontology/ 挪到「关于」分组**，不再与主学习路径并列。解决 S8（global/ontology 跳脱），并把"本体"降级为附录级内容。

> 备注：VitePress 的 sidebar 按"路径前缀匹配"机制，要让不同物理目录共享同一 sidebar，要么把物理目录重组（推荐，更干净），要么在 config.mts 里把同一个 sidebar 数组对象赋给多个 key（VitePress 支持）。物理目录重组建议：
>
> ```
> docs/
>   learn/           ← 新建，包含 learning-path.md（从根挪入）
>   chapters/        ← 保持
>   branches/        ← 保持（learn sidebar 同时匹配 /learn/ /chapters/ /branches/）
>   algorithms/      ← 保持，补 index.md
>   reference/       ← 新建，把 /scenarios /operators /cases /glossary 挪入
>   labs/            ← 新建，把 /math-lab /playgrounds 挪入
>   about/           ← 新建，把 /global /legacy /ontology /derivatives 挪入
>   for-beginners/   ← 保持
> ```
>
> 如果不打算移动物理文件，也可以在 config.mts 里用 sidebar 多 key 同一配置的方式实现"视觉上的合并"，物理路径保持不变。

---

### 建议 C：首页信息架构整改

目标：**首屏明确两类用户的第一步；首屏以下"价值 → 内容 → 互动 → 延伸"四段式**，消除重复。

#### C1. Hero 区整改

- **保留 3 个按钮，主次明确**：
  - 主按钮（brand）：🌱 **5 分钟看懂 CV** → /for-beginners/（明确"快速科普"）
  - 次按钮（brand）：📚 **开始系统学习** → /learning-path（明确"按教程走"）
  - 文字链接（alt，放在按钮下方小字）：我已经知道要找什么 → [🎯 按场景查] / [📄 算法档案] / [🧪 动手玩]
- **删除**：「版本对比大表」「六分支总览」「Canny 样板」三个按钮——版本对比/六分支都是二级页概念，Canny 是单个算法，都不该占 hero 位。

#### C2. Hero 下方重排 6 段（建议顺序）

1. **「这是什么」+ 一句定位**（精简版，2–3 句话）
   - 删去"本体论研究站"等元叙事，只说：**"传统计算机视觉（1963–2012）系统化学习站——从论文到实战，覆盖 59 个经典算法、14 个核心算子、6 大技术族"**。
   - "四层闭环 L1→L2→L3→L4" mermaid **保留**但缩成小图，并加一句"每个算法都走这四层"即可。

2. **「你想怎么学？」三选一卡片组**（替代现有 features 6 格，features 里的 6 个卖点拆到对应卡片里）：
   - 📚 **系统学习**：按章顺读，从像素到场景（15 章教程 + 六分支）→ /learning-path
   - 🎯 **按任务查**：工业缺陷 / OCR / 人脸 / 拼接…（场景反查 + 算子词典 + 对比表）→ /scenarios/
   - 🧪 **动手体验**：拖滑块懂原理 + 浏览器跑 OpenCV → /labs/
   - 这 3 张卡**首屏即达**，是真正的分流路口。

3. **「算法家族树」**（保留 `<FamilyTree />` 组件）
   - **删除**下方重复的"🗂️ 六大技术分支"6 张 AlgorithmCard——家族树交互组件已经表达了六分支，再用 6 张静态卡片重复一次是冗余。
   - 家族树下方只留一个"📄 查看 59 个算法完整档案 →"的链接卡。

4. **「🧪 两个实验室」并排卡片组**（math-lab + playgrounds 并列，不再被其他内容隔开）：
   - 左卡：原理实验室（拖滑块，不用装东西）
   - 右卡：真机实验室（OpenCV.js，真实跑）
   - 两卡之间一句话区分"先玩原理、再跑真机"。

5. **「传统 CV → 深度学习」传承段**（精简）
   - **保留**index.md 中现有的 mermaid（NMS→YOLO 等），**删除**"被继承/改造/抛弃/解决了什么硬伤"四张对照表（这些表在 family.md 和 /legacy/ 已经写过了）。
   - 只留一句话结论 + 链接「🧬 完整传承脉络 →」。

6. **「精选内容」或「精选算法」**（可选，保留 3 张卡）
   - Canny / SIFT / HOG 三张卡保留，作为新用户"试读样板"。

7. **附录：关于本站的知识组织（原"🕸️ 知识本体"段）**
   - 降级为末尾小字/折叠 section，标题改为「📐 附录：本站的知识组织方式」，链接到 /about/（原 ontology/schema）。
   - **从首页主要视觉流里移除**"本体""Schema""可校验""实体类型"这些词。

#### C3. 首页要删除/合并的块

| 原块 | 处理 |
|---|---|
| features 6 格（学习路径/技术分支/论文精读/源码走读/实战/传承） | **删除**，功能由"三选一卡"承接，"论文精读/源码走读"等四层闭环信息移到 C2 第 1 段 |
| 「四层闭环」mermaid 后的大段 FamilyTree 组件 + 六分支 6 张卡 | 保留 FamilyTree、**删除六分支 6 张卡**（冗余） |
| 「双轴阅读方式」段落（index.md 85–94） | **精简为一句注脚**或挪到 /learning-path 页首，首页不重复解释"双轴"概念 |
| 「精选算法档案」下方的"🔗 传统 CV 与深度学习的传承"整段（含 4 张对照表） | mermaid 保留，4 张表删除（与 /legacy/ 和 family.md 重复） |
| 「🕸️ 知识本体」段 | 降级为附录链接 |

---

## 三、具体路径级"必改项"清单（按优先级）

**P0 · 结构性缺陷（不改会持续让新用户迷路）**

1. **补建 `/algorithms/index.md`**（目前该目录无 index，是最严重缺口）；把 /versions/index.md 的版本索引和全算法对比大表迁入作为其内容；然后将 /versions/ 改为 redirect（或废除，/versions/ 路径保留做跳转）。
2. **给 `/math-lab/` 补 sidebar 配置**（否则进入后侧边栏消失）。
3. **统一"本体/家族/谱系/知识图谱"命名**：
   - 目录层面：把 /legacy/ 和 /ontology/ 都归拢到一个"关于/全局"分组（物理目录 /about/ 或逻辑 sidebar 分组）；
   - 文案层面：对用户只露出一个名字（建议「**全局视图**」），"本体/Ontology/Schema"这组词仅出现在附录页。
4. **把 /algorithms/ 侧边栏里 59 个算法按六大分支折叠分组**，删除所有条目标题里的"（已升级为完整档案）"冗余后缀（既然已全部升级，就不需要标注了）。

**P1 · 冗余清理（降低维护成本和阅读噪声）**

5. **删除 family.md 末尾的「经典算法版本逐项对比」14 列大表**（family.md 273–289），改为链接「完整对比见 /algorithms/#comparison」。
6. **合并 /global/evolutions.md 与 /global/evolution-story.md**：evolutions.md 是"结构化分支演化表"，evolution-story.md 是"决策点叙事"，两者内容 70% 重合，建议保留 evolution-story（叙事更友好），把 evolutions.md 里的表格合并进来；或反过来 evolutions 保留结构化内容，evolution-story 的"决策 1…决策 13"作为子页面/折叠 section。
7. **清理 family.md 108–245 行「与深度学习的关键接口 + 三代对比 + 继承/改造/抛弃/解决痛点」四表**（135 行），这些内容与 /legacy/index.md 几乎逐段重复，建议 family.md 只留一张 mermaid + 链接「详看 /legacy/」。
8. **清理首页 hero 冗余按钮**（见 C1），删除"Canny 样板"按钮。
9. **删除顶栏「🧭 学习」下拉里的 7 个"高频算法直达"直链**（Canny/Harris/SIFT/RANSAC/LK/VJ/张氏），它们是硬编码、会过时、挤占导航位；由搜索 + 算法档案总览承担。

**P2 · 体验优化**

10. **把"工程实现层"从"六分支"列表里独立出来**，命名为「🔧 工程横切层」（强调"横切"而非"第 7 分支"）。
11. **统一 "学习路径/章节体系/章体系" 命名**为「**教程（纵轴）**」或「**系统学习路径**」。
12. **两个实验室（math-lab / playgrounds）在导航上永远并排出现**，不要拆分到不同菜单。
13. **首页增加"老用户快速入口"小文字区**：算子词典 / 对比矩阵 / 故障排查 / 场景反查 4 个文字链接。
14. **为 /algorithms/*/ 子页在侧边栏顶部加面包屑**（档案总表 / 所属分支 / 对应章节），解决"从算法页回不去"的问题。
15. **把「🌱 小白入门」首按钮的文字改为**「🌱 **5 分钟看懂 CV**」（比"小白入门（5 页看懂）"更具象）；「🧭 开始学习路径」改为「📚 **系统学习（15 章教程）**」，两者的用户画像清晰区分。

---

## 四、一句话总结

**当前站点的核心内容（59 算法 × 7 页 + 15 章 + 6 分支 + 算子词典 + 场景反查 + 两个实验室）已经非常扎实，但导航犯了"作者视角组织"的典型毛病——把内部知识结构（本体/六分支/15章/演化/版本/传承）直接暴露给用户，导致同一个概念在顶栏、首页、多个侧边栏、多个页面之间重复 4–6 次，而真正的用户意图入口（学/查/玩/入门）反而被淹没。**

整改的核心动作只有三个：

1. **顶栏从 4 项（其中 1 项巨型 29 项下拉）改为 5 项（入门/学习/查资料/动手玩/关于）**，一级菜单按用户意图切分；
2. **侧边栏从 13 个独立"世界"合并为 5 个（新手/学习/算法档案/查资料/动手玩/关于）**，消除跨目录跳脱，算法档案按分支折叠分组并补建总入口；
3. **首页从"作者讲本体+双轴+六分支+传承+家族树重复 3 遍"改为"一句定位 + 三个入口卡 + 家族树 + 两实验室 + 传承 + 附录"**，首屏给出清晰的第一步分流。
