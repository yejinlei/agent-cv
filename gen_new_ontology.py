#!/usr/bin/env python3
"""为 bilateral / mog2 / kcf / lbp 四个新算法批量生成 ontology YAML。"""
import os, yaml

OUT_ALGO = "ontology/instances/algorithms"
OUT_PAPER = "ontology/instances/papers"
OUT_CONCEPT = "ontology/instances/concepts"

os.makedirs(OUT_ALGO, exist_ok=True)
os.makedirs(OUT_PAPER, exist_ok=True)
os.makedirs(OUT_CONCEPT, exist_ok=True)

# -------- 论文 ----------
PAPERS = {
    "paper-tomasi-1998-bilateral": {
        "id": "paper-tomasi-1998-bilateral",
        "type": "paper",
        "title": "Bilateral Filtering for Gray and Color Images",
        "authors": ["Carlo Tomasi", "Roberto Manduchi"],
        "year": 1998,
        "venue": "ICCV",
        "url": "https://people.csail.mit.edu/sparis/publi/2008/fnt/Paris_08_Bilateral_Filtering.pdf",
        "doi": "10.1109/ICCV.1998.710815",
        "contribution": "首次同时用空间邻近度和亮度相似度做非线性保边滤波",
        "keyInsight": "跨边缘的像素颜色差大，给它们权重为 0，就能保边",
        "novelty": "值域高斯 × 空间高斯的乘积核，非迭代保边滤波",
        "limitations": ["原始 O(r²) 复杂度", "彩色 BGR 空间有色偏", "大核慢"],
        "influencedBy": ["op-gaussian-blur"],
        "influenced": ["algo-guided-filter", "algo-domain-transform", "algo-nlm"],
        "docsPath": "/algorithms/bilateral/paper",
    },
    "paper-zivkovic-2004-mog2": {
        "id": "paper-zivkovic-2004-mog2",
        "type": "paper",
        "title": "Improved Adaptive Gaussian Mixture Model for Background Subtraction",
        "authors": ["Zoran Zivkovic"],
        "year": 2004,
        "venue": "ICPR",
        "url": "https://ieeexplore.ieee.org/document/1333992",
        "doi": "10.1109/ICPR.2004.1333992",
        "contribution": "每个像素的高斯分量个数 K 自适应选择，且集成阴影检测",
        "keyInsight": "背景不一定是单一颜色，像素颜色分布往往是多峰的",
        "novelty": "Dirichlet 先验 + 在线学习率估计 + 自动选 K",
        "limitations": ["不能处理相机运动", "突发光照变化误检", "静态新物体会被吸收为背景"],
        "influencedBy": ["paper-stauffer-1999-gmm"],
        "influenced": ["paper-barnich-2011-vibe"],
        "docsPath": "/algorithms/mog2/paper",
    },
    "paper-henriques-2015-kcf": {
        "id": "paper-henriques-2015-kcf",
        "type": "paper",
        "title": "High-Speed Tracking with Kernelized Correlation Filters",
        "authors": ["João F. Henriques", "Rui Caseiro", "Pedro Martins", "Jorge Batista"],
        "year": 2015,
        "venue": "IEEE TPAMI",
        "url": "https://arxiv.org/abs/1404.7584",
        "doi": "10.1109/TPAMI.2014.2345390",
        "contribution": "用循环矩阵+FFT 将相关滤波训练/检测速度推到数百 FPS，并引入核技巧与多通道 HOG",
        "keyInsight": "滑动窗口的所有候选都是模板的循环移位，在傅里叶域可一次全部算出",
        "novelty": "核相关滤波 KCF + HOG 多通道特征 + 闭环式训练检测更新",
        "limitations": ["不处理尺度变化", "遮挡后漂移", "无重检测"],
        "influencedBy": ["paper-bolme-2010-mosse", "concept-fourier-transform"],
        "influenced": ["algo-dsst", "algo-csrt", "algo-sort", "algo-deepsort"],
        "docsPath": "/algorithms/kcf/paper",
    },
    "paper-ojala-1996-lbp": {
        "id": "paper-ojala-1996-lbp",
        "type": "paper",
        "title": "A Comparative Study of Texture Measures with Classification Based on Featured Distributions",
        "authors": ["Timo Ojala", "Matti Pietikäinen", "David Harwood"],
        "year": 1996,
        "venue": "Pattern Recognition",
        "url": "https://ieeexplore.ieee.org/document/5763036",
        "doi": "10.1016/0031-3203(95)00067-4",
        "contribution": "提出 LBP 算子，仅用局部二值模式直方图做纹理分类，性能超越 Gabor、MRF 等主流方法",
        "keyInsight": "纹理本质是局部亮度对比的统计分布，与绝对亮度无关",
        "novelty": "局部二值模式 + 块直方图统计；2002 年扩展为多分辨率/旋转不变/Uniform LBP",
        "limitations": ["对噪声敏感", "大尺度纹理需多分辨率扩展", "方向敏感"],
        "influencedBy": [],
        "influenced": ["algo-lbp-face", "algo-mb-lbp"],
        "docsPath": "/algorithms/lbp/paper",
    },
}

# -------- 新算法 ----------
ALGOS = {
    "algo-bilateral": {
        "id": "algo-bilateral",
        "type": "algorithm",
        "name": "双边滤波",
        "enName": "Bilateral Filter",
        "year": 1998,
        "authors": ["Tomasi", "Manduchi"],
        "branch": "branch-image-processing",
        "layer": "low",
        "status": "stable",
        "tags": ["保边滤波", "磨皮", "edge-preserving"],
        "plainTalk": "磨皮美颜的爷爷算法：离得近、颜色像的像素才被拉平，边缘自动保住",
        "docsPath": "/algorithms/bilateral/",
        "papers": ["paper-tomasi-1998-bilateral"],
        "concepts": ["concept-edge-aware", "concept-gaussian", "concept-denoising"],
        "dependsOn": ["op-gaussian-blur"],
        "evolvedFrom": "",
        "replacedBy": "algo-guided-filter",
        "appliedIn": ["beauty", "hdr-tonemapping", "cartoonization"],
        "inheritedBy": ["algo-guided-filter", "algo-domain-transform", "algo-bilateral-grid"],
        "inputs": ["彩色/灰度图 I", "d 核直径", "σs 空间高斯", "σr 值域高斯"],
        "outputs": ["保边去噪图 I'"],
        "limits": ["核越大越慢", "强椒盐噪声无效", "大 halo 风险"],
    },
    "algo-mog2": {
        "id": "algo-mog2",
        "type": "algorithm",
        "name": "MOG2 背景减除",
        "enName": "Adaptive Gaussian Mixture Background Subtraction",
        "year": 2004,
        "authors": ["Zivkovic"],
        "branch": "branch-geometry",
        "layer": "mid",
        "status": "stable",
        "tags": ["背景建模", "运动检测", "监控"],
        "plainTalk": "每个像素都记「平时是什么颜色」，来个不一样的就当闯入者",
        "docsPath": "/algorithms/mog2/",
        "papers": ["paper-zivkovic-2004-mog2"],
        "concepts": ["concept-background-model", "concept-gaussian-mixture", "concept-shadow-detection"],
        "dependsOn": ["op-morphology", "op-connected-components"],
        "evolvedFrom": "paper-stauffer-1999-gmm",
        "replacedBy": "",
        "appliedIn": ["surveillance", "motion-detection", "people-counting"],
        "inheritedBy": ["algo-vi-be", "algo-knn-bg"],
        "inputs": ["视频帧序列", "history 帧数", "varThreshold", "detectShadows"],
        "outputs": ["前景掩码 fgMask（0/127/255）"],
        "limits": ["相机动则失效", "光照突变误检", "静态物体被吸收"],
    },
    "algo-kcf": {
        "id": "algo-kcf",
        "type": "algorithm",
        "name": "KCF 核相关滤波跟踪",
        "enName": "Kernelized Correlation Filter",
        "year": 2015,
        "authors": ["Henriques", "Caseiro", "Martins", "Batista"],
        "branch": "branch-detection",
        "layer": "mid",
        "status": "stable",
        "tags": ["单目标跟踪", "相关滤波", "fast-tracking"],
        "plainTalk": "拿模板在频域里做「全场滑动匹配」，一个元素乘就出响应图，CPU 上跑 150 FPS",
        "docsPath": "/algorithms/kcf/",
        "papers": ["paper-henriques-2015-kcf"],
        "concepts": ["concept-correlation-filter", "concept-circulant-matrix", "concept-kernel-trick", "concept-fourier-transform", "concept-hog"],
        "dependsOn": ["op-hanming-window", "op-hog"],
        "evolvedFrom": "algo-mosse",
        "replacedBy": "algo-csrt",
        "appliedIn": ["visual-tracking", "uav-follow", "annotation"],
        "inheritedBy": ["algo-dsst", "algo-csrt"],
        "inputs": ["初始帧 ROI", "视频帧序列"],
        "outputs": ["逐帧 bbox", "PSR 置信度"],
        "limits": ["无尺度估计", "遮挡漂移", "无重检测"],
    },
    "algo-lbp": {
        "id": "algo-lbp",
        "type": "algorithm",
        "name": "LBP 局部二值模式",
        "enName": "Local Binary Pattern",
        "year": 1996,
        "authors": ["Ojala", "Pietikäinen", "Harwood"],
        "branch": "branch-image-processing",
        "layer": "mid",
        "status": "stable",
        "tags": ["纹理", "人脸识别", "局部特征"],
        "plainTalk": "每个像素和 8 个邻居比亮暗，拼出一个 8 位二进制「纹理指纹」",
        "docsPath": "/algorithms/lbp/",
        "papers": ["paper-ojala-1996-lbp"],
        "concepts": ["concept-texture", "concept-uniform-pattern", "concept-histogram"],
        "dependsOn": ["op-grayscale"],
        "evolvedFrom": "",
        "replacedBy": "",
        "appliedIn": ["face-recognition", "texture-classification", "defect-detection"],
        "inheritedBy": ["algo-lbp-face", "algo-mb-lbp", "algo-lbp-top"],
        "inputs": ["灰度图", "P 邻居点数", "R 半径"],
        "outputs": ["LBP 编码图 / 59 维块直方图向量"],
        "limits": ["对噪声敏感", "方向敏感", "需对齐"],
    },
}

# -------- 新概念 ----------
CONCEPTS = {
    "concept-edge-aware": {
        "id": "concept-edge-aware",
        "type": "concept",
        "name": "保边滤波 Edge-Aware Filtering",
        "plainTalk": "平滑图像但不糊边缘的一类滤波器",
        "explain": "传统滤波只按空间距离加权会把边缘糊掉；保边滤波额外考虑亮度/颜色差异，跨边缘像素权重被压低。",
        "members": ["algo-bilateral", "algo-guided-filter", "algo-domain-transform", "algo-bilateral-grid", "algo-nlm"],
        "docsPath": "/algorithms/bilateral/concepts",
    },
    "concept-background-model": {
        "id": "concept-background-model",
        "type": "concept",
        "name": "背景建模 Background Modeling",
        "plainTalk": "对「没有目标时画面长什么样」建立数学描述",
        "explain": "视频里把每一帧和背景模型对比，差异大的像素就是运动前景。关键是模型要能缓慢适应光照变化、树叶晃动等动态背景。",
        "members": ["algo-mog2", "algo-knn-bg", "algo-vi-be"],
        "docsPath": "/algorithms/mog2/concepts",
    },
    "concept-shadow-detection": {
        "id": "concept-shadow-detection",
        "type": "concept",
        "name": "阴影检测 Shadow Detection",
        "plainTalk": "把「物体投下的黑影」和「物体本身」区分开",
        "explain": "阴影只改变亮度不改变色调。HSV 空间里，如果新像素比背景暗 0.3~0.8 倍但色相/饱和度近似，就是阴影。",
        "members": ["algo-mog2"],
        "docsPath": "/algorithms/mog2/concepts",
    },
    "concept-correlation-filter": {
        "id": "concept-correlation-filter",
        "type": "concept",
        "name": "相关滤波 Correlation Filter",
        "plainTalk": "训练一个滤波器让目标位置出现峰值响应",
        "explain": "跟踪问题转化为岭回归：学一个滤波器 w，目标处响应=1、背景=0；检测时做卷积/相关，峰值就是目标位置。MOSSE/KCF/CSRT/DSST 都是这一家族。",
        "members": ["algo-mosse", "algo-kcf", "algo-dsst", "algo-csrt"],
        "docsPath": "/algorithms/kcf/concepts",
    },
    "concept-circulant-matrix": {
        "id": "concept-circulant-matrix",
        "type": "concept",
        "name": "循环矩阵 Circulant Matrix",
        "plainTalk": "所有行都是第一行的循环移位",
        "explain": "循环矩阵能被傅里叶矩阵对角化：C(x) = Fᴴ diag(Fx) F。这把岭回归的训练/检测复杂度从 O(n³) 降到 O(n log n)，是 KCF 速度的数学根基。",
        "members": ["algo-kcf", "algo-mosse"],
        "docsPath": "/algorithms/kcf/concepts",
    },
    "concept-uniform-pattern": {
        "id": "concept-uniform-pattern",
        "type": "concept",
        "name": "Uniform 模式",
        "plainTalk": "LBP 8 位编码里 0→1 跳变次数不超过 2 的模式",
        "explain": "自然图像 90% 以上的 LBP 编码都只有 ≤2 次跳变（共 58 种），把剩下 198 种归成一类，直方图从 256 维降到 59 维，更稳更小。",
        "members": ["algo-lbp"],
        "docsPath": "/algorithms/lbp/concepts",
    },
}


def dump_yaml(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


if __name__ == "__main__":
    os.chdir("/home/user/workspace/7648064683708846935/agent-cv")
    n = 0
    for pid, p in PAPERS.items():
        dump_yaml(f"{OUT_PAPER}/{pid}.yaml", p); n += 1
    for aid, a in ALGOS.items():
        dump_yaml(f"{OUT_ALGO}/{aid}.yaml", a); n += 1
    for cid, c in CONCEPTS.items():
        dump_yaml(f"{OUT_CONCEPT}/{cid}.yaml", c); n += 1
    print(f"Wrote {n} YAML files.")
