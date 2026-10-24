#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量创建新算法的本体 YAML 实例"""
import yaml
from pathlib import Path

ROOT = Path("/home/user/workspace/7648064683708846935/agent-cv/ontology/instances")

# === 新算法本体 ===
ALGOS_YAML = {
    "fast": {
        "id": "fast", "type": "Algorithm", "name": "FAST 角点检测",
        "enName": "Features from Accelerated Segment Test",
        "year": 2006, "branch": "feature-detection", "level": "mid",
        "docsPath": "/algorithms/fast/", "chapter": "ch-8-local-feature",
        "papers": [],
        "dependsOn": [],
        "evolvedFrom": "harris",
        "inheritedBy": "orb",
        "tags": ["corner", "real-time", "keypoint"],
        "concepts": ["concept-fast-detector", "concept-non-maximum-suppression"],
    },
    "brief": {
        "id": "brief", "type": "Algorithm", "name": "BRIEF 二进制描述子",
        "enName": "Binary Robust Independent Elementary Features",
        "year": 2010, "branch": "feature-detection", "level": "mid",
        "docsPath": "/algorithms/brief/", "chapter": "ch-8-local-feature",
        "papers": [],
        "dependsOn": ["fast"],
        "evolvedFrom": "sift",
        "inheritedBy": "orb",
        "tags": ["descriptor", "binary", "real-time"],
        "concepts": ["concept-binary-descriptor"],
    },
    "shi-tomasi": {
        "id": "shi-tomasi", "type": "Algorithm", "name": "Shi-Tomasi 角点",
        "enName": "Good Features to Track",
        "year": 1994, "branch": "feature-detection", "level": "mid",
        "docsPath": "/algorithms/shi-tomasi/", "chapter": "ch-8-local-feature",
        "papers": [],
        "dependsOn": [],
        "evolvedFrom": "harris",
        "inheritedBy": "fast",
        "tags": ["corner", "tracking", "gftt"],
        "concepts": [],
    },
    "mser": {
        "id": "mser", "type": "Algorithm", "name": "MSER 最大稳定极值区域",
        "enName": "Maximally Stable Extremal Regions",
        "year": 2002, "branch": "feature-detection", "level": "mid",
        "docsPath": "/algorithms/mser/", "chapter": "ch-8-local-feature",
        "papers": [],
        "dependsOn": [],
        "tags": ["region", "affine-invariant", "blob"],
        "concepts": [],
    },
    "watershed": {
        "id": "watershed", "type": "Algorithm", "name": "分水岭分割",
        "enName": "Watershed Transform",
        "year": 1991, "branch": "segmentation", "level": "mid",
        "docsPath": "/algorithms/watershed/", "chapter": "ch-10-image-segmentation",
        "papers": [],
        "dependsOn": ["morphology"],
        "tags": ["segmentation", "marker-controlled", "region"],
        "concepts": [],
    },
    "grabcut": {
        "id": "grabcut", "type": "Algorithm", "name": "GrabCut 抠图",
        "enName": "GrabCut Interactive Foreground Extraction",
        "year": 2004, "branch": "segmentation", "level": "mid",
        "docsPath": "/algorithms/grabcut/", "chapter": "ch-10-image-segmentation",
        "papers": [],
        "dependsOn": [],
        "tags": ["segmentation", "interactive", "matting", "graph-cut"],
        "concepts": [],
    },
    "kmeans": {
        "id": "kmeans", "type": "Algorithm", "name": "K-Means 颜色聚类",
        "enName": "K-Means Clustering",
        "year": 1967, "branch": "segmentation", "level": "basic",
        "docsPath": "/algorithms/kmeans/", "chapter": "ch-10-image-segmentation",
        "papers": [],
        "dependsOn": [],
        "inheritedBy": "bovw",
        "tags": ["clustering", "color-quantization", "segmentation"],
        "concepts": ["concept-kmeans"],
    },
    "meanshift": {
        "id": "meanshift", "type": "Algorithm", "name": "MeanShift 均值漂移",
        "enName": "Mean-Shift Mode Seeking",
        "year": 2002, "branch": "segmentation", "level": "mid",
        "docsPath": "/algorithms/meanshift/", "chapter": "ch-10-image-segmentation",
        "papers": [],
        "dependsOn": [],
        "inheritedBy": "camshift",
        "tags": ["clustering", "density", "segmentation"],
        "concepts": [],
    },
    "slic": {
        "id": "slic", "type": "Algorithm", "name": "SLIC 超像素",
        "enName": "Simple Linear Iterative Clustering",
        "year": 2010, "branch": "segmentation", "level": "mid",
        "docsPath": "/algorithms/slic/", "chapter": "ch-10-image-segmentation",
        "papers": [],
        "dependsOn": ["kmeans"],
        "tags": ["superpixel", "over-segmentation", "preprocessing"],
        "concepts": [],
    },
    "morphology": {
        "id": "morphology", "type": "Algorithm", "name": "形态学操作",
        "enName": "Mathematical Morphology",
        "year": 1964, "branch": "image-processing", "level": "basic",
        "docsPath": "/algorithms/morphology/", "chapter": "ch-4-image-enhancement",
        "papers": [],
        "dependsOn": [],
        "inheritedBy": "watershed",
        "tags": ["erosion", "dilation", "preprocessing", "binary"],
        "concepts": [],
    },
    "sgbm": {
        "id": "sgbm", "type": "Algorithm", "name": "SGM 半全局立体匹配",
        "enName": "Semi-Global Matching",
        "year": 2005, "branch": "geometry", "level": "advanced",
        "docsPath": "/algorithms/sgbm/", "chapter": "ch-14-3d-vision",
        "papers": [],
        "dependsOn": [],
        "tags": ["stereo", "disparity", "depth", "semi-global"],
        "concepts": [],
    },
    "pnpsolver": {
        "id": "pnpsolver", "type": "Algorithm", "name": "PnP 位姿估计",
        "enName": "Perspective-n-Point",
        "year": 2009, "branch": "geometry", "level": "advanced",
        "docsPath": "/algorithms/pnpsolver/", "chapter": "ch-14-3d-vision",
        "papers": [],
        "dependsOn": ["zhang-calibration"],
        "tags": ["pose-estimation", "AR", "pnp", "6DoF"],
        "concepts": ["reprojection-error", "lm-optimization", "radial-distortion"],
    },
    "icp": {
        "id": "icp", "type": "Algorithm", "name": "ICP 迭代最近点",
        "enName": "Iterative Closest Point",
        "year": 1992, "branch": "geometry", "level": "advanced",
        "docsPath": "/algorithms/icp/", "chapter": "ch-14-3d-vision",
        "papers": [],
        "dependsOn": [],
        "tags": ["point-cloud", "registration", "3D", "lidar"],
        "concepts": [],
    },
    "camshift": {
        "id": "camshift", "type": "Algorithm", "name": "CamShift 目标跟踪",
        "enName": "Continuously Adaptive Mean-Shift",
        "year": 1998, "branch": "detection", "level": "mid",
        "docsPath": "/algorithms/camshift/", "chapter": "ch-11-object-detection",
        "papers": [],
        "dependsOn": ["meanshift"],
        "tags": ["tracking", "color", "mean-shift"],
        "concepts": ["concept-histogram"],
    },
    "farneback": {
        "id": "farneback", "type": "Algorithm", "name": "Farnebäck 稠密光流",
        "enName": "Gunnar Farnebäck Dense Optical Flow",
        "year": 2003, "branch": "geometry", "level": "mid",
        "docsPath": "/algorithms/farneback/", "chapter": "ch-13-motion-analysis",
        "papers": [],
        "dependsOn": [],
        "evolvedFrom": "horn-schunck",
        "tags": ["optical-flow", "dense", "motion"],
        "concepts": ["concept-optical-flow", "concept-pyramidal-lk"],
    },
}

# 写入每个算法
for key, data in ALGOS_YAML.items():
    fpath = ROOT / "algorithms" / f"{key}.yaml"
    with open(fpath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"[+] algorithms/{key}.yaml")

# 更新 homography.yaml 和 horn-schunck.yaml 的 docsPath
for name in ["homography", "horn-schunck"]:
    fpath = ROOT / "algorithms" / f"{name}.yaml"
    with open(fpath, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    d["docsPath"] = f"/algorithms/{name}/"
    with open(fpath, "w", encoding="utf-8") as f:
        yaml.dump(d, f, allow_unicode=True, sort_keys=False)
    print(f"[~] algorithms/{name}.yaml docsPath updated")

# === 添加新 concepts ===
NEW_CONCEPTS = {
    "concept-morphology": {
        "id": "concept-morphology", "type": "Concept", "name": "形态学操作",
        "plainTalk": "用结构元素像印章一样扫过图像，通过局部最大/最小值实现腐蚀、膨胀等形状操作",
        "layer": "L1",
        "formalDefinition": "基于集合论和格论的图像处理框架，通过结构元素与图像的 min/max 卷积实现形状变换",
    },
    "concept-disparity": {
        "id": "concept-disparity", "type": "Concept", "name": "视差",
        "plainTalk": "同一个 3D 点在左右相机里的横坐标差，近大远小",
        "layer": "L2",
        "formalDefinition": "d = x_L - x_R，深度 Z = f·B/d，B 为基线，f 为焦距",
    },
    "concept-back-projection": {
        "id": "concept-back-projection", "type": "Concept", "name": "反向投影",
        "plainTalk": "把图像每个像素换成「它是目标颜色的概率」，亮的地方就像目标",
        "layer": "L2",
        "formalDefinition": "基于颜色直方图，对整张图逐像素查询其颜色在目标直方图中的概率值得到概率图",
    },
    "concept-dense-flow": {
        "id": "concept-dense-flow", "type": "Concept", "name": "稠密光流",
        "plainTalk": "不只在角点，给每个像素都算出一个运动箭头",
        "layer": "L2",
        "formalDefinition": "在能量最小化框架下，对全图每个像素估计位移向量 (u,v)，数据项+平滑正则项",
    },
    "concept-superpixel": {
        "id": "concept-superpixel", "type": "Concept", "name": "超像素",
        "plainTalk": "把百万像素切成几百个颜色一致、形状紧凑的小块",
        "layer": "L2",
        "formalDefinition": "在颜色-位置联合空间中聚类得到的感知一致小区域，用作后续处理单元",
    },
    "concept-gmm-segmentation": {
        "id": "concept-gmm-segmentation", "type": "Concept", "name": "GMM 颜色建模",
        "plainTalk": "前景背景各用几个高斯云朵描述颜色分布，判断像素属于哪一边",
        "layer": "L2",
        "formalDefinition": "用 K 个高斯分量的混合模型对 RGB 颜色分布建模，通过 EM 迭代估计参数",
    },
    "concept-graph-cut": {
        "id": "concept-graph-cut", "type": "Concept", "name": "图割最小割",
        "plainTalk": "把图像建模成带边权的图，一刀割断前景和背景的联系，割断的边总权重最小",
        "layer": "L3",
        "formalDefinition": "通过构造包含源点 S 和汇点 T 的图，用 max-flow/min-cut 算法求能量函数全局最优分割",
    },
    "concept-icp": {
        "id": "concept-icp", "type": "Concept", "name": "迭代最近点",
        "plainTalk": "两片点云互相找最近点配对，算刚体变换让它们对齐，反复迭代",
        "layer": "L3",
        "formalDefinition": "交替进行最近点对应和 SVD 刚体变换估计，直到两片点云收敛到对齐",
    },
}
for key, data in NEW_CONCEPTS.items():
    fpath = ROOT / "concepts" / f"{key}.yaml"
    with open(fpath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"[+] concepts/{key}.yaml")

print("\n=== 本体 YAML 更新完成 ===")
