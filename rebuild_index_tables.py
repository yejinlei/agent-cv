#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建 algorithms/index.md 的全算法索引表 与 versions/index.md 的分支版本表 + 对比大表补充行。"""
import io, os, re, yaml

BASE = os.path.dirname(os.path.abspath(__file__))
ALGO_DIR = os.path.join(BASE, "docs", "algorithms")
INST = os.path.join(BASE, "ontology", "instances", "algorithms")

BRANCH_CN = {
    "branch-image-processing": "① 图像处理（基础积木）",
    "branch-feature-detection": "② 特征检测（找关键点）",
    "branch-feature-matching": "③ 特征匹配（建立对应）",
    "branch-segmentation": "④ 图像分割",
    "branch-detection": "⑤ 目标检测（传统派）",
    "branch-geometry": "⑥ 几何视觉",
}
ORDER = ["branch-image-processing", "branch-feature-detection", "branch-feature-matching",
         "branch-segmentation", "branch-detection", "branch-geometry"]
SHORT = {"branch-image-processing": "图像处理", "branch-feature-detection": "特征检测",
         "branch-feature-matching": "特征匹配", "branch-segmentation": "图像分割",
         "branch-detection": "目标检测", "branch-geometry": "几何视觉"}

# slug -> (一句话, 对比表补充: 任务|特征类型|复杂度|尺度|旋转|光照|场景)
INFO = {
    "sobel": ("3×3 卷积算梯度，边缘鼻祖", ("边缘", "梯度", "O(N)", "❌", "❌", "❌", "边缘粗提取")),
    "gaussian-blur": ("可分离高斯核线性平滑，去噪基石", ("平滑", "线性卷积", "O(N·k) 可分离", "❌", "❌", "✅", "预处理、尺度空间")),
    "median-filter": ("排序取中值，去椒盐不糊边", ("去噪", "秩排序非线性", "O(N·k²)", "❌", "❌", "✅", "脉冲/椒盐噪声")),
    "otsu": ("类间方差最大自动阈值", ("二值化", "直方图", "O(N)", "❌", "❌", "⚠️", "文档/缺陷分割")),
    "canny": ("三阶段管线，单像素细边", ("边缘", "梯度+NMS", "O(N)", "❌", "❌", "⚠️", "高质量边缘")),
    "hough": ("参数空间投票找直线/圆", ("形状检测", "投票", "O(N·θ)", "❌", "❌", "⚠️", "直线检测")),
    "morphology": ("膨胀/腐蚀/开闭，形状滤波基础", ("形状滤波", "结构元素", "O(N)", "❌", "❌", "✅", "去噪、连通、缺陷检测")),
    "bilateral": ("空间×值域高斯，保边去噪", ("保边滤波", "空间×值域高斯", "O(r²·N)", "❌", "❌", "✅", "美颜、HDR、卡通化")),
    "clahe": ("分块直方图均衡 + 对比度裁剪", ("增强", "局部直方图", "O(N)", "❌", "❌", "✅", "医学影像、低对比增强")),
    "distance-transform": ("到最近背景的欧氏距离场", ("距离场", "两遍扫描", "O(N)", "❌", "❌", "✅", "骨架、粘连分离")),
    "connected-components": ("两遍扫描标记连通块", ("连通分析", "并查集/等价表", "O(N)", "❌", "❌", "✅", "目标计数、区域标记")),
    "gabor": ("方向/频率选择性纹理滤波", ("纹理", "Gabor 核", "O(N·k)", "❌", "⚠️方向组", "✅", "纹理分类、指静脉")),
    "lbp": ("局部二值模式纹理描述", ("纹理描述", "局部二值模式直方图", "O(N)", "❌", "❌", "✅(单调不变)", "人脸、纹理、缺陷")),
    "haar-wavelet": ("多分辨率分解，压缩与特征", ("变换", "低通/高通滤波组", "O(N)", "❌", "❌", "✅", "压缩、Haar 特征")),
    "mog2": ("自适应高斯混合背景模型", ("运动前景", "自适应高斯混合", "O(N·K)", "—", "—", "⚠️", "监控、人流统计")),
    "knn-background": ("非参数最近样本背景估计", ("运动前景", "KNN 密度估计", "O(N·K)", "—", "—", "⚠️", "多模态背景监控")),
    "vibe": ("样本一致性随机传播背景建模", ("运动前景", "样本一致性", "O(N·K)", "—", "—", "⚠️", "嵌入式运动检测")),
    "harris": ("自相关矩阵角点", ("角点", "自相关矩阵", "O(N)", "❌", "✅", "⚠️", "追踪、拼接")),
    "sift": ("DoG 尺度+128 维描述子", ("特征点", "DoG+128维", "O(N·M)", "✅", "✅", "✅", "图像拼接、识别")),
    "surf": ("Hessian 近似+积分图加速", ("特征点", "Hessian+64维", "O(N)", "✅", "✅", "✅", "实时匹配")),
    "orb": ("oFAST+rBRIEF 免费实时", ("特征点", "oFAST+rBRIEF", "O(N)", "⚠️多尺度", "✅", "✅", "SLAM、AR")),
    "fast": ("决策树判定，比 Harris 快 10 倍", ("角点", "圆周 16 像素决策树", "O(N)", "❌", "❌", "⚠️", "实时关键点、SLAM 前端")),
    "shi-tomasi": ("min(λ1,λ2)，光流友好角点", ("角点", "min(λ1,λ2)", "O(N)", "❌", "✅", "⚠️", "KLT 光流跟踪")),
    "mser": ("阈值稳定极值区域", ("区域/斑点", "阈值稳定极值区域", "O(N log N)", "✅", "✅", "⚠️", "宽基线匹配、文本检测")),
    "brisk": ("AGAST+同心采样，二进制快特征", ("特征点", "AGAST+同心采样", "O(N)", "✅", "✅", "⚠️", "移动端 SLAM")),
    "akaze": ("非线性扩散尺度空间 + M-LDB", ("特征点", "非线性扩散+M-LDB", "O(N)", "✅", "✅", "✅", "手机端匹配")),
    "hough-circles": ("圆心投票检测圆", ("圆检测", "参数投票", "O(N³)", "❌", "❌", "⚠️", "硬币/虹膜/工件圆心")),
    "contour-fitting": ("道格拉斯-普克折线简化", ("轮廓", "递归分治", "O(N log N)", "❌", "❌", "✅", "形状分析、多边形拟合")),
    "freak": ("仿视网膜级联二进制描述子", ("描述子", "同心采样级联比较", "O(N·D)", "❌", "⚠️", "⚠️", "嵌入式端到端匹配")),
    "ransac": ("随机采样一致剔除外点", ("几何拟合", "—", "随机采样", "—", "—", "—", "剔除外点")),
    "lucas-kanade": ("稀疏光流跟踪", ("光流", "灰度守恒", "O(N·iter)", "❌", "❌", "❌", "KLT 追踪")),
    "brief": ("256 bit 二进制描述子", ("描述子", "256 bit 点对比较", "O(N·D)", "❌", "❌", "⚠️", "快速匹配")),
    "homography": ("4 点 RANSAC 估算平面变换", ("几何变换", "DLT/RANSAC", "O(N)", "—", "—", "—", "图像拼接、AR 平面")),
    "flann": ("自动配置的近似最近邻搜索", ("匹配加速", "kd-tree / 层次聚类树", "O(N log N)", "—", "—", "—", "大规模特征匹配")),
    "watershed": ("梯度地形浸没分割", ("分割", "梯度地形浸没", "O(N log N)", "❌", "❌", "❌", "细胞/颗粒分割")),
    "kmeans": ("颜色空间聚类", ("聚类分割", "颜色空间 Lloyd", "O(N·K·iter)", "❌", "❌", "❌", "颜色量化、超像素基础")),
    "meanshift": ("密度峰值非参数聚类", ("聚类/跟踪", "核密度梯度上升", "O(N²)", "❌", "❌", "❌", "视频跟踪、分割")),
    "slic": ("LabXY 5 维局部 K-Means", ("超像素", "LabXY 局部 K-Means", "O(N)", "❌", "❌", "⚠️", "超像素前处理")),
    "grabcut": ("GMM+GraphCut 迭代抠图", ("抠图", "GMM+GraphCut", "O(N³) 最坏", "❌", "❌", "⚠️", "人像抠图")),
    "region-growing": ("种子点相似性扩张分割", ("分割", "区域增长", "O(N)", "❌", "❌", "⚠️", "医学/缺陷区域提取")),
    "felzenszwalb-segmentation": ("最小生成树贪心超像素", ("超像素", "MST 贪心合并", "O(N log N)", "❌", "❌", "⚠️", "候选区域生成")),
    "viola-jones": ("Haar+AdaBoost 级联人脸", ("人脸检测", "Haar+积分图", "级联加速", "❌", "正面", "❌", "人脸、正脸")),
    "hog-svm": ("行人检测标配", ("行人检测", "梯度直方图", "O(N·window)", "❌", "⚠️", "⚠️", "行人、刚性物体")),
    "dpm": ("可变形部件传统检测巅峰", ("通用检测", "HOG+部件", "O(N·window·part)", "⚠️金字塔", "⚠️", "⚠️", "PASCAL 时代巅峰")),
    "bovw": ("视觉词袋+SVM 检索", ("分类/检索", "视觉词袋直方图", "O(N·K)", "⚠️SPM", "❌", "⚠️TF-IDF", "图像检索、分类")),
    "camshift": ("自适应 MeanShift 跟踪", ("跟踪", "肤色反投影+MeanShift", "O(N·iter)", "❌", "⚠️", "❌", "人脸/目标跟踪")),
    "kcf": ("循环矩阵核相关滤波跟踪", ("单目标跟踪", "核相关滤波+HOG", "O(N log N)", "❌(需DSST)", "⚠️", "⚠️", "短时跟踪、UAV")),
    "csrt": ("通道+空间可靠性跟踪", ("单目标跟踪", "多通道相关滤波", "O(N log N)", "❌", "⚠️", "⚠️", "高精度短时跟踪")),
    "mosse": ("频域相关滤波，600+ FPS", ("单目标跟踪", "相关滤波频域解", "O(N log N)", "❌", "⚠️", "❌", "高速实时跟踪")),
    "zhang-calibration": ("棋盘格标定相机", ("相机标定", "棋盘角点", "O(N·img)", "—", "—", "—", "所有三维视觉前置")),
    "epipolar-geometry": ("基础矩阵+三角化", ("双视图几何", "—", "O(N)", "—", "—", "—", "三维重建、SLAM")),
    "essential-matrix": ("两视图相对位姿求解", ("两视图几何", "八点法+分解", "O(N)", "—", "—", "—", "SfM 初始化")),
    "triangulation": ("两视线求交还原三维点", ("三维重建", "DLT/最优三角化", "O(N)", "—", "—", "—", "SfM、双目 3D")),
    "bundle-adjustment": ("全局重投影误差最小化", ("优化", "稀疏 LM", "O(n³) 稀疏", "—", "—", "—", "SfM/SLAM 后端")),
    "sgbm": ("半全局立体匹配", ("立体深度", "半全局多方向 DP", "O(N·D)", "❌", "❌", "⚠️", "双目深度")),
    "horn-schunck": ("全局平滑稠密光流", ("稠密光流", "全局变分", "O(N·iter)", "❌", "❌", "❌", "平滑稠密运动场")),
    "farneback": ("多项式稠密光流", ("稠密光流", "二次多项式展开", "O(N)", "❌", "❌", "⚠️", "视频稳像、动作识别")),
    "pnpsolver": ("O(n) 位姿求解", ("位姿估计", "虚拟控制点", "O(n)", "—", "—", "—", "AR、无人机位姿")),
    "icp": ("迭代最近点点云配准", ("点云配准", "最近点+SVD", "O(N log N)", "—", "—", "—", "三维重建、激光定位")),
}


def load_algos():
    out = {}
    for fn in os.listdir(INST):
        if not fn.endswith(".yaml"):
            continue
        d = yaml.safe_load(io.open(os.path.join(INST, fn), encoding="utf-8"))
        dp = d.get("docsPath") or ""
        m = re.match(r"^/algorithms/([a-z0-9-]+)/?$", dp)
        if not m:
            continue
        out[m.group(1)] = d
    return out


def main():
    algos = load_algos()
    dirs = sorted([x for x in os.listdir(ALGO_DIR) if os.path.isdir(os.path.join(ALGO_DIR, x))])
    missing = [d for d in dirs if d not in INFO]
    if missing:
        print("!! 缺少一句话数据:", missing)
    rows = {}
    for d in dirs:
        info = INFO.get(d)
        if info is None:
            continue
        a = algos.get(d, {})
        name = a.get("name", d)
        year = a.get("year", "-")
        branch = a.get("branch", "branch-image-processing")
        rows[d] = dict(name=name, year=year, branch=branch, one=info[0], cmp=info[1])

    # ---- 1. algorithms/index.md 全算法索引表 ----
    new_table = ["## 全算法索引（{} 个档案，持续更新）\n".format(len(rows)), "",
                 "| 分支 | 算法 | 年份 | 一句话 | 入口 |", "|---|---|---|---|---|"]
    for b in ORDER:
        for d in dirs:
            r = rows.get(d)
            if r and r["branch"] == b:
                new_table.append(f"| {SHORT[b]} | {r['name']} | {r['year']} | {r['one']} | [→](/algorithms/{d}/) |")
    new_table.append("")
    idx = io.open(os.path.join(BASE, "docs", "algorithms", "index.md"), encoding="utf-8").read()
    start = idx.index("## 全算法索引")
    end = idx.index("**收录原则**")
    idx = idx[:start] + "\n".join(new_table) + "\n" + idx[end:]
    io.open(os.path.join(BASE, "docs", "algorithms", "index.md"), "w", encoding="utf-8").write(idx)
    print("updated docs/algorithms/index.md", len(rows), "algos")

    # ---- 2. versions/index.md 分支版本表 ----
    vpath = os.path.join(BASE, "docs", "versions", "index.md")
    v = io.open(vpath, encoding="utf-8").read()
    sec_start = v.index("## 六大分支的版本索引")
    sec_end = v.index("---\n\n## 全算法对比大表")
    blocks = ["## 六大分支的版本索引\n"]
    for b in ORDER:
        blocks.append(f"### {BRANCH_CN[b]}\n")
        blocks.append("| 版本 | 年代 | 一句话 | 档案 |")
        blocks.append("|---|---|---|---|")
        for d in dirs:
            r = rows.get(d)
            if r and r["branch"] == b:
                blocks.append(f"| {r['name']} | {r['year']} | {r['one']} | [→ {d}（完整档案）](/algorithms/{d}/) |")
        blocks.append("")
    v = v[:sec_start] + "\n".join(blocks) + v[sec_end:]

    # ---- 3. versions/index.md 对比大表（整体重建，避免与简称行重复）----
    tstart = v.index("## 全算法对比大表")
    tend = v.index("[系列家族]")
    cmp_lines = ["## 全算法对比大表", "",
                 "| 算法 | 年代 | 任务 | 特征类型 | 计算复杂度 | 尺度不变 | 旋转不变 | 抗光照 | 开源免费 | 典型场景 |",
                 "|---|---|---|---|---|---|---|---|---|---|"]
    for b in ORDER:
        for d in dirs:
            r = rows.get(d)
            if r and r["branch"] == b:
                c = r["cmp"]
                cmp_lines.append(
                    f"| {r['name']} | {r['year']} | {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} | {c[5]} | ✅ | {c[6]} |")
    cmp_lines.append("")
    v = v[:tstart] + "\n".join(cmp_lines) + "\n\n" + v[tend:]
    io.open(vpath, "w", encoding="utf-8").write(v)
    print("rebuilt 对比大表:", len(rows), "行")


if __name__ == "__main__":
    main()
