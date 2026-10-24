#!/usr/bin/env python3
"""
agent-cv 本体校验器
=====================

用 JSON Schema 校验 ontology/instances 下的 YAML 实例。
写错字段（如把 year 写成字符串、branch 填了不存在的分支）会直接报错。

用法：
    python ontology/validate.py                      # 校验全部实例
    python ontology/validate.py <file.yaml>          # 校验单个文件

依赖：
    pip install pyyaml jsonschema
"""

import sys
import os
from pathlib import Path

try:
    import yaml
except ImportError:
    print("缺少依赖：请先执行 pip install pyyaml jsonschema")
    sys.exit(2)

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("缺少依赖：请先执行 pip install pyyaml jsonschema")
    sys.exit(2)


ROOT = Path(__file__).resolve().parent
SCHEMA_DIR = ROOT / "schema"
INSTANCE_DIR = ROOT / "instances"

# 实例 type -> schema 文件
TYPE_TO_SCHEMA = {
    "Algorithm": "algorithm.schema.yaml",
    "Operator": "operator.schema.yaml",
    "Paper": "paper.schema.yaml",
    "Application": "application.schema.yaml",
    "Library": "library.schema.yaml",
    "Trick": "trick.schema.yaml",
    "PainPoint": "painpoint.schema.yaml",
    "Concept": "concept.schema.yaml",
    "CaseStudy": "casestudy.schema.yaml",
    "Chapter": "chapter.schema.yaml",
}

# 六大数据支分支（与 docs/branches 对齐）
VALID_BRANCHES = {
    "branch-image-processing",
    "branch-feature-detection",
    "branch-feature-matching",
    "branch-segmentation",
    "branch-detection",
    "branch-geometry",
}


class Colors:
    OK = "\033[32m"
    ERR = "\033[31m"
    WARN = "\033[33m"
    DIM = "\033[2m"
    END = "\033[0m"


def load_schemas():
    """加载所有 schema"""
    schemas = {}
    for name in set(TYPE_TO_SCHEMA.values()):
        path = SCHEMA_DIR / name
        if not path.exists():
            print(f"{Colors.WARN}⚠  Schema 缺失: {name}{Colors.END}")
            continue
        with open(path, encoding="utf-8") as f:
            schemas[name] = yaml.safe_load(f)
    return schemas


def validate_file(path, schemas):
    """校验单个实例文件，返回 (成功?, 错误列表)"""
    errors = []

    with open(path, encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return False, [f"YAML 解析失败: {e}"]

    if not isinstance(data, dict):
        return False, ["文件内容不是 YAML 映射（object）"]

    # ① type 必须存在且已注册
    obj_type = data.get("type")
    if obj_type is None:
        return False, ["缺少必填字段 type"]
    if obj_type not in TYPE_TO_SCHEMA:
        return False, [f"未知的 type: {obj_type}（合法值: {sorted(TYPE_TO_SCHEMA)}）"]

    schema_name = TYPE_TO_SCHEMA[obj_type]
    schema = schemas.get(schema_name)
    if schema is None:
        return False, [f"找不到 schema: {schema_name}"]

    # ② JSON Schema 校验
    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in err.path) or "(根)"
        errors.append(f"[{loc}] {err.message}")

    # ③ 语义校验（Schema 表达不了的跨字段约束）
    if obj_type == "Algorithm":
        if data.get("branch") not in VALID_BRANCHES:
            errors.append(
                f"[branch] 不是合法分支: {data.get('branch')}；"
                f"合法值: {sorted(VALID_BRANCHES)}"
            )
        # 至少要有一篇论文
        if not data.get("papers"):
            errors.append("[papers] Algorithm 至少要关联一篇原始论文")

        # 自引用检查
        if data.get("id") in (data.get("dependsOn") or []):
            errors.append(f"[dependsOn] 不能依赖自己: {data.get('id')}")

        # 演化来源不能是自己
        if data.get("evolvedFrom") == data.get("id"):
            errors.append(f"[evolvedFrom] 不能演化自自己: {data.get('id')}")

    if obj_type == "Operator":
        if not data.get("opencvFunc") and not data.get("usedBy"):
            errors.append(
                "[opencvFunc/usedBy] 至少要给出 OpenCV 函数或被哪个算法使用"
            )

    if obj_type == "Paper":
        if not data.get("doi") and not data.get("url"):
            errors.append("[doi/url] 至少要给出 DOI 或可访问链接（不允许无法核验的引用）")

    if obj_type == "Trick":
        if not data.get("relatedAlgorithms"):
            errors.append("[relatedAlgorithms] 技巧必须挂到至少一个算法上")
        if data.get("id") in (data.get("relatedAlgorithms") or []):
            errors.append(f"[relatedAlgorithms] 不能引用自己: {data.get('id')}")

    if obj_type == "PainPoint":
        if not data.get("relatedAlgorithms"):
            errors.append("[relatedAlgorithms] 踩坑记录必须挂到至少一个算法上")

    if obj_type == "CaseStudy":
        if not data.get("relatedAlgorithms"):
            errors.append("[relatedAlgorithms] 案例必须关联至少一个算法")
        if len(data.get("pipeline") or []) < 2:
            errors.append("[pipeline] 案例流程至少要两步，否则不算可复现的案例")

    return (len(errors) == 0), errors


def collect_instances():
    """收集所有实例文件"""
    files = []
    if not INSTANCE_DIR.exists():
        return files
    for sub in sorted(INSTANCE_DIR.iterdir()):
        if sub.is_dir():
            files.extend(sorted(sub.glob("*.yaml")))
    return files


def cross_check(files):
    """跨文件一致性检查：所有引用的 ID 必须存在"""
    ids = set()
    refs = []  # (来源文件, 字段, 被引用的 ID)

    for path in files:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            continue
        this_id = data.get("id")
        if this_id:
            ids.add(this_id)

    ref_fields = (
        "concepts", "dependsOn", "papers", "applications", "usedBy",
        "caseStudies", "painPoints", "tricks", "relatedAlgorithms",
        "implementsAlgorithms", "algorithmStack",
    )
    single_ref_fields = ("evolvedFrom",)

    for path in files:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            continue
        for fld in ref_fields:
            for ref in data.get(fld) or []:
                if isinstance(ref, str):
                    refs.append((path, fld, ref))
        for fld in single_ref_fields:
            ref = data.get(fld)
            if isinstance(ref, str):
                refs.append((path, fld, ref))

    dangling = [(p, f, r) for (p, f, r) in refs if r not in ids]
    return ids, refs, dangling


def main():
    schemas = load_schemas()

    # 单文件模式
    if len(sys.argv) > 1:
        targets = [Path(sys.argv[1])]
    else:
        targets = collect_instances()

    if not targets:
        print(f"{Colors.WARN}没有找到任何实例文件{Colors.END}")
        return 1

    print(f"{Colors.DIM}校验 {len(targets)} 个实例文件...{Colors.END}\n")

    ok_count = 0
    fail_count = 0
    all_errors = []

    for path in targets:
        try:
            rel = path.relative_to(ROOT.parent)
        except ValueError:
            rel = path
        success, errors = validate_file(path, schemas)

        if success:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            print(
                f"{Colors.OK}✅ {rel}{Colors.END}  "
                f"({data.get('type')}, id={data.get('id')})"
            )
            ok_count += 1
        else:
            print(f"{Colors.ERR}❌ {rel}{Colors.END}")
            for e in errors:
                print(f"     {Colors.ERR}·{Colors.END} {e}")
            fail_count += 1
            all_errors.append((path, errors))

    # 跨文件引用检查
    if len(targets) > 1:
        ids, refs, dangling = cross_check(targets)
        print()
        print(f"{Colors.DIM}跨文件引用检查：{len(ids)} 个实体，{len(refs)} 条引用{Colors.END}")
        if dangling:
            print(f"{Colors.WARN}⚠  {len(dangling)} 条「悬空引用」（被引用的 ID 尚无实例）{Colors.END}")
            shown = {}
            for _, _, r in dangling:
                shown[r] = shown.get(r, 0) + 1
            for r, c in sorted(shown.items()):
                print(f"     {Colors.WARN}·{Colors.END} {r}  (被引用 {c} 次)")
            print(f"{Colors.DIM}  提示：渐进式覆盖——先建实例再补文档，悬空引用不算校验失败。{Colors.END}")
        else:
            print(f"{Colors.OK}✅ 所有引用都有对应实例{Colors.END}")

    print()
    print("─" * 52)
    if fail_count == 0:
        print(f"{Colors.OK}全部通过：{ok_count} 个实例校验成功{Colors.END}")
        return 0
    print(
        f"{Colors.ERR}校验失败：{ok_count} 通过 / {fail_count} 失败{Colors.END}"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
