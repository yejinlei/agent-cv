#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补齐算法的七页档案模板（自包含，富内容版）。"""
from pathlib import Path

ROOT = Path("/home/user/workspace/7648064683708846935/agent-cv/docs/algorithms")


def card(m):
    pros = str(m["pros"]).replace("'", '"')
    cons = str(m["cons"]).replace("'", '"')
    return f'''<AlgorithmCard
  name="{m['name']}"
  enName="{m['en']}"
  chapter="{m['chapter']}"
  chapterLink="{m['chapterLink']}"
  branch="{m['branch']}"
  year="{m['year']}"
  author="{m['author']}"
  paper="{m['paperUrl']}"
  level="{m['level']}"
  tagline="{m['tagline']}"
  analogy="{m['analogy']}"
  scene="{m['scene']}"
  :pros='{pros}'
  :cons='{cons}'
/>'''


def tpl_index(m, one_line, why, scene_story, pages_hint):
    return f'''---
layout: doc
---

{card(m)}

## 一句话理解

> {one_line}

## 为什么需要它？

{why}

## 生活场景

{scene_story}

## 七页速览

| 页面 | 内容 | 你会得到什么 |
|------|------|--------------|
| [第1页 · 总览](index) | 你现在看的 | 快速判断「要不要用它」 |
| [第2页 · 论文溯源](paper) | 原始论文 | {pages_hint[0]} |
| [第3页 · 核心概念](concepts) | 原理直觉 | {pages_hint[1]} |
| [第4页 · 算法架构](architecture) | 流程图与步骤 | {pages_hint[2]} |
| [第5页 · 源码实现](source) | 可跑代码 | {pages_hint[3]} |
| [第6页 · 踩坑清单](painpoints) | 新手陷阱 | {pages_hint[4]} |
| [第7页 · 调参口诀](tricks) | 实战经验 | {pages_hint[5]} |

::: tip 阅读建议
第一次接触请按 1 → 3 → 4 顺序读，先建立直觉再看流程；要动手就直接跳到第 5 页抄代码。
:::
'''


def tpl_paper(m, d):
    return f'''---
outline: deep
---

# 第 2 页 · 论文溯源

## 论文名片

| 项目 | 内容 |
|------|------|
| 标题 | **{d['title']}** |
| 作者 | {m['author']} |
| 年份 | {m['year']} |
| 发表 | {d['venue']} |
| 原文 | [{m['paperUrl']}]({m['paperUrl']}) |
| 一句话贡献 | {d['oneline']} |

## 1. 当时的问题

{d['problem']}

## 2. 核心思想

{d['idea']}

```mermaid
{d['idea_flow']}
```

## 3. 关键贡献

{d['contrib']}

## 4. 核心公式（看懂思路即可）

{d['formula']}

## 5. 实验结果

{d['experiment']}

## 6. 局限与争议

{d['limit']}

## 7. 历史影响

{d['influence']}

## 8. 一句话总结

> {d['summary']}
'''


def tpl_concepts(m, concepts):
    md = f'''---
outline: deep
---

# 第 3 页 · 核心概念

## 先用生活直觉理解

{m['analogy']}

**典型应用**：{m['scene']}

```mermaid
flowchart LR
  A["输入"] --> B["核心处理"] --> C["输出"]
```

## 概念逐个拆解

'''
    for i, (t, text, dia) in enumerate(concepts, 1):
        md += f"### 概念 {i}：{t}\n\n{text}\n\n"
        if dia:
            md += f"```mermaid\n{dia}\n```\n\n"
    md += f'''## 和其他算法的关系

| 关系 | 算法 | 说明 |
|------|------|------|
| 前置依赖 | {m['dep_pre']} | 通常先做这些再做本算法 |
| 同类对比 | {m['dep_peer']} | 解决同类问题，各有取舍 |
| 下游常用 | {m['dep_post']} | 本算法结果常交给它们处理 |

::: tip 记忆锚点
{m['anchor']}
:::
'''
    return md


def tpl_architecture(m, steps, complexity):
    md = f'''---
outline: deep
---

# 第 4 页 · 算法架构

## 完整流程图

```mermaid
flowchart TB
'''
    for i, (name, desc) in enumerate(steps, 1):
        nid = chr(ord('A') + i - 1)
        md += f'  {nid}["{i}. {name}<br/>{desc}"]\n'
        if i < len(steps):
            md += f"  {nid} --> {chr(ord('A') + i)}\n"
    md += "```\n\n## 每一步在做什么\n\n"
    for i, (name, desc) in enumerate(steps, 1):
        md += f"### 步骤 {i}：{name}\n\n{desc}\n\n"
    md += f'''## 在整体视觉管线中的位置

```mermaid
flowchart LR
  A["原始图像"] --> B["预处理"]
  B --> C["{m['name']}"]
  C --> D["后处理 / 下游任务"]
```

## 复杂度分析

{complexity}

## 参数总览（论文建议 vs OpenCV 默认 vs 实战推荐）

| 参数 | 含义 | 论文建议 | OpenCV 默认 | 实战推荐 |
|------|------|----------|-------------|----------|
'''
    for p in m["params_arch"]:
        md += f"| {p[0]} | {p[1]} | {p[2]} | {p[3]} | **{p[4]}** |\n"
    md += f'''
## 边界情况与失败模式

'''
    for t, txt in m["failmodes"]:
        md += f"- **{t}**：{txt}\n"
    return md


def tpl_source(m, opencv_code, numpy_code, notes):
    return f'''---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
{opencv_code}
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解算法原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
{numpy_code}
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
'''
    # 这个表格在调用处替换占位
    return None


def tpl_source_full(m, opencv_code, numpy_code, notes, param_rows):
    md = f'''---
outline: deep
---

# 第 5 页 · 源码实现

## 方式一：OpenCV 一行调用（工业首选）

```python
{opencv_code}
```

## 方式二：NumPy 手写最小实现（理解原理用）

::: warning 性能提醒
手写版仅用于**理解原理**，比 OpenCV 慢几十倍，生产环境请用方式一。
:::

```python
{numpy_code}
```

## 关键参数说明

| 参数 | 含义 | 建议值 |
|------|------|--------|
'''
    for p in param_rows:
        md += f"| {p[0]} | {p[1]} | **{p[2]}** |\n"
    md += f'''
::: tip 工程实现说明
{notes}
:::

## 生产环境建议

- 优先用 OpenCV 接口，它带 SIMD 与多线程优化，别自己造轮子
- 嵌入式平台可用 `cv2.setNumThreads(1)` 控制线程数，避免抢占
- 大图先降采样处理再上采样结果，速度提升常肉眼可见
- 关键参数做成配置项，不同场景（白天/夜晚、室内/室外）单独调
'''
    return md


def tpl_painpoints(m, pitfalls):
    md = f'''---
outline: deep
---

# 第 6 页 · 踩坑清单

## 新手最常掉的坑

'''
    for i, (t, problem, solve) in enumerate(pitfalls, 1):
        md += f'''### 坑 {i}：{t}

::: danger 现象
{problem}
:::

::: tip 解决
{solve}
:::

'''
    md += '''## 通用调试四步法

1. **可视化中间结果**——不要只盯最终输出，把每一步的中间图都存下来看
2. **先小图后大图**——拿 200×200 的简单图跑通，再上真实场景大图
3. **先默认值后调参**——有 baseline 再改，一次只改一个参数
4. **对齐参考实现**——用 OpenCV 官方 tutorial 的结果做基准，差异大就查原因

## 自查清单

- [ ] 数据类型对不对？（uint8 vs float32 差别巨大）
- [ ] 通道顺序对不对？（BGR vs RGB、灰度 vs 彩色）
- [ ] 图像是否归一化？（0–255 vs 0–1）
- [ ] 边界是否处理？（图像边缘的卷积/插值）
- [ ] 参数单位对不对？（像素 vs 比例、毫秒 vs 秒）
'''
    return md


def tpl_tricks(m, koujue, params, tips, perf):
    md = f'''---
outline: deep
---

# 第 7 页 · 调参口诀

## 一句话调参口诀

```
{koujue}
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|------|------|--------|----------|----------|
'''
    for p in params:
        md += f"| {p[0]} | {p[1]} | **{p[2]}** | {p[3]} | {p[4]} |\n"
    md += "\n## 实战技巧\n\n"
    for t, txt in tips:
        md += f"### {t}\n\n{txt}\n\n"
    md += '''## 性能参考

| 条件 | 耗时 | 说明 |
|------|------|------|
'''
    for p in perf:
        md += f"| {p[0]} | {p[1]} | {p[2]} |\n"
    md += f'''
## 选型建议

**适合用**：{m['scene']}

**不适合用**：{'、'.join(m['cons'][:3])}

::: tip 一句话
{m['tagline']}
:::
'''
    return md


def build(key, m, one_line, why, scene_story, pages_hint, paper_data,
          concepts, steps, complexity, opencv_code, numpy_code, notes, param_rows,
          pitfalls, koujue, params, tips, perf):
    d = ROOT / key
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.md").write_text(tpl_index(m, one_line, why, scene_story, pages_hint), encoding="utf-8")
    (d / "paper.md").write_text(tpl_paper(m, paper_data), encoding="utf-8")
    (d / "concepts.md").write_text(tpl_concepts(m, concepts), encoding="utf-8")
    (d / "architecture.md").write_text(tpl_architecture(m, steps, complexity), encoding="utf-8")
    (d / "source.md").write_text(tpl_source_full(m, opencv_code, numpy_code, notes, param_rows), encoding="utf-8")
    (d / "painpoints.md").write_text(tpl_painpoints(m, pitfalls), encoding="utf-8")
    (d / "tricks.md").write_text(tpl_tricks(m, koujue, params, tips, perf), encoding="utf-8")
    n = sum(len((d / f).read_text(encoding="utf-8").splitlines())
            for f in ["index.md", "paper.md", "concepts.md", "architecture.md", "source.md", "painpoints.md", "tricks.md"])
    print(f"[{key}] 7 files, {n} lines")
