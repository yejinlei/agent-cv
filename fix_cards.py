#!/usr/bin/env python3
"""修复 AlgorithmCard 两个问题：
1. 把 chapter=文字 改成带跳转链接的 chapterLink，并把 chapter 改成 slug 形式（ch03-ch15）
   同时修改 AlgorithmCard.vue 支持 chapterLink 字段
2. 修正 mog2 的 branch（应该是 图像处理 / 运动分析 而不是 几何视觉）
"""
import os, re, glob

ALGOS_DIR = "docs/algorithms"

# 章号 -> slug + 中文名 + 链接 映射
CHAPTER_MAP = {
    "第3章":  ("ch03-preprocessing", "第3章 · 图像预处理"),
    "第4章":  ("ch04-primitives",     "第4章 · 基元检测"),
    "第5章":  ("ch05-segmentation",   "第5章 · 目标分割"),
    "第6章":  ("ch06-representation", "第6章 · 目标表达与描述"),
    "第7章":  ("ch07-texture",        "第7章 · 纹理分析"),
    "第8章":  ("ch08-shape",          "第8章 · 形状分析"),
    "第9章":  ("ch09-stereo",         "第9章 · 立体视觉"),
    "第10章": ("ch10-3d-recovery",    "第10章 · 三维景物恢复"),
    "第11章": ("ch11-motion",         "第11章 · 运动分析"),
    "第12章": ("ch12-recognition",    "第12章 · 景物识别"),
    "第13章": ("ch13-matching",       "第13章 · 广义匹配"),
    "第14章": ("ch14-activity",       "第14章 · 时空行为理解"),
    "第15章": ("ch15-scene",          "第15章 · 场景解释"),
}

def first_chapter_slug(chapter_text: str):
    """从 chapter="第4章 · 基元检测 / 第6章 · ..." 取第一个章"""
    m = re.search(r"第(\d+)章", chapter_text)
    if not m:
        return None, None
    key = f"第{m.group(1)}章"
    return CHAPTER_MAP.get(key, (None, None))

fixed = 0
for mdfile in glob.glob(f"{ALGOS_DIR}/*/index.md"):
    with open(mdfile, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1) 找 chapter="..." 属性
    def replace_chapter(match):
        val = match.group(1)
        slug, label = first_chapter_slug(val)
        if not slug:
            return match.group(0)
        # 显示仍然用完整文字；增加 chapterLink
        link = f"/chapters/{slug}"
        return f'chapter="{val}"  chapterLink="{link}"'

    content = re.sub(r'chapter="([^"]+)"', replace_chapter, content)

    # 2) 修 mog2 的 branch
    if "mog2/index.md" in mdfile:
        content = content.replace('branch="几何视觉"', 'branch="图像处理"')

    if content != original:
        with open(mdfile, "w", encoding="utf-8") as f:
            f.write(content)
        fixed += 1
        print(f"✓ {mdfile}")

print(f"\n共修复 {fixed} 个文件")
