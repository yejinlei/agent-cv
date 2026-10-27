#!/usr/bin/env python3
"""批量加厚薄弱算法档案，追加直觉讲解、SVG 对比、常见坑、口诀。
只在文件末尾追加"## 扩展"章节，不动已有内容、不动 frontmatter。
"""
import os, sys

BASE = 'docs/algorithms'

# ========== SVG 生成工具：纯 inline SVG，无外部依赖 ==========

def svg_compare_row(rows, width=720, cell_h=160, desc_color=True):
    """生成「原图 | 算法 A | 算法 B」三列对比图。
    rows: [(title_l, svg_l, title_m, svg_m, title_r, svg_r)]
    每列 svg 用一个示意。
    """
    cell_w = width // 3
    parts = [f'<div style="overflow-x:auto"><svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{cell_h*len(rows)+30}" style="background:#fafbfc;border-radius:12px;border:1px solid #eaecef">']
    # 列标题（写在第一行每个 cell 顶部）
    for i, r in enumerate(rows):
        y0 = i*cell_h + 5
        parts.append(f'<text x="{cell_w*0+cell_w//2}" y="{y0+18}" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">{r[0]}</text>')
        parts.append(f'<text x="{cell_w*1+cell_w//2}" y="{y0+18}" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">{r[2]}</text>')
        parts.append(f'<text x="{cell_w*2+cell_w//2}" y="{y0+18}" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">{r[4]}</text>')
        # 绘制三个示意图
        parts.append(f'<g transform="translate({cell_w*0+30},{y0+28})">{r[1]}</g>')
        parts.append(f'<g transform="translate({cell_w*1+30},{y0+28})">{r[3]}</g>')
        parts.append(f'<g transform="translate({cell_w*2+30},{y0+28})">{r[5]}</g>')
        # 竖分隔线
        if i==0:
            parts.append(f'<line x1="{cell_w}" y1="5" x2="{cell_w}" y2="{cell_h*len(rows)+5}" stroke="#e1e4e8" stroke-dasharray="4,3"/>')
            parts.append(f'<line x1="{cell_w*2}" y1="5" x2="{cell_w*2}" y2="{cell_h*len(rows)+5}" stroke="#e1e4e8" stroke-dasharray="4,3"/>')
    parts.append('</svg></div>')
    return ''.join(parts)


# --- 具体算法的 SVG 示意生成函数 ---

def svg_blur_gauss():
    # 高斯模糊 vs 均值模糊 vs 中值模糊
    orig = '<circle cx="90" cy="60" r="45" fill="#4a90e2"/><circle cx="90" cy="60" r="4" fill="white"/>'
    mean = '<circle cx="90" cy="60" r="45" fill="#4a90e2" opacity="0.5" stroke="#4a90e2" stroke-width="4"/><rect x="60" y="45" width="60" height="30" fill="white" opacity="0.4"/>'
    gauss = '<circle cx="90" cy="60" r="45" fill="#4a90e2" opacity="0.7"/><ellipse cx="90" cy="60" rx="55" ry="55" fill="none" stroke="#4a90e2" stroke-width="2" opacity="0.3"/>'
    median = '<circle cx="90" cy="60" r="45" fill="#4a90e2"/>'
    return orig, mean, gauss, median

def svg_noise_saltpepper():
    # 带椒盐噪声的图
    import random; random.seed(7)
    pts=''
    for _ in range(60):
        x=random.randint(0,180); y=random.randint(0,120)
        c='black' if random.random()<0.5 else 'white'
        pts+=f'<rect x="{x}" y="{y}" width="3" height="3" fill="{c}"/>'
    img = f'<rect x="0" y="0" width="180" height="120" fill="#c8b48a"/><circle cx="60" cy="60" r="30" fill="#3b5998"/><circle cx="130" cy="75" r="20" fill="#c0392b"/>{pts}'
    after_mean = f'<rect x="0" y="0" width="180" height="120" fill="#c8b48a"/><circle cx="60" cy="60" r="32" fill="#3b5998" opacity="0.7"/><circle cx="130" cy="75" r="22" fill="#c0392b" opacity="0.7"/>'
    after_median = f'<rect x="0" y="0" width="180" height="120" fill="#c8b48a"/><circle cx="60" cy="60" r="30" fill="#3b5998"/><circle cx="130" cy="75" r="20" fill="#c0392b"/>'
    return img, after_mean, after_median

def svg_edge_gradient():
    # 三种梯度算子对比
    orig = '<rect x="10" y="10" width="160" height="100" fill="#ddd"/><polygon points="30,30 100,25 120,70 50,90" fill="#555"/>'
    sob = '<rect x="10" y="10" width="160" height="100" fill="#000"/><polyline points="30,30 100,25 120,70 50,90 30,30" fill="none" stroke="#fff" stroke-width="3"/>'
    prw = '<rect x="10" y="10" width="160" height="100" fill="#000"/><polyline points="30,30 100,25 120,70 50,90 30,30" fill="none" stroke="#bbb" stroke-width="2"/><polyline points="40,40 95,35" fill="none" stroke="#ddd" stroke-width="1"/>'
    can = '<rect x="10" y="10" width="160" height="100" fill="#000"/><polyline points="30,30 100,25 120,70 50,90 30,30" fill="none" stroke="#fff" stroke-width="1.5"/>'
    return orig, sob, prw, can

def svg_corner():
    # 角点 vs 边 vs 平坦
    flat = '<rect x="0" y="0" width="180" height="120" fill="#d6d6d6"/><circle cx="90" cy="60" r="6" fill="#e74c3c"/><text x="90" y="100" text-anchor="middle" font-size="12" fill="#555">平坦</text>'
    edge = '<rect x="0" y="0" width="90" height="120" fill="#d6d6d6"/><rect x="90" y="0" width="90" height="120" fill="#888"/><circle cx="90" cy="60" r="6" fill="#e74c3c"/><text x="90" y="100" text-anchor="middle" font-size="12" fill="#555">边缘</text>'
    corner = '<rect x="0" y="0" width="90" height="60" fill="#d6d6d6"/><rect x="90" y="0" width="90" height="60" fill="#888"/><rect x="0" y="60" width="90" height="60" fill="#888"/><rect x="90" y="60" width="90" height="60" fill="#555"/><circle cx="90" cy="60" r="6" fill="#e74c3c"/><text x="90" y="100" text-anchor="middle" font-size="12" fill="#555">角点</text>'
    return flat, edge, corner

def svg_backsub():
    # 帧差 vs KNN vs MOG2
    bg = '<rect x="0" y="0" width="180" height="120" fill="#b4c7e7"/><rect x="0" y="80" width="180" height="40" fill="#7a8e5a"/><rect x="10" y="50" width="40" height="40" fill="#8b4513"/>'  # 背景
    fg_diff = '<rect x="0" y="0" width="180" height="120" fill="#000"/><path d="M95,30 L115,70 L75,70 Z" fill="#fff"/><rect x="70" y="70" width="50" height="20" fill="#fff"/>'  # 只有轮廓
    fg_knn = '<rect x="0" y="0" width="180" height="120" fill="#000"/><circle cx="100" cy="40" r="12" fill="#fff"/><rect x="85" y="50" width="30" height="50" fill="#fff"/>'
    fg_mog2 = '<rect x="0" y="0" width="180" height="120" fill="#000"/><circle cx="100" cy="40" r="12" fill="#fff"/><rect x="85" y="50" width="30" height="50" fill="#fff"/><ellipse cx="100" cy="115" rx="20" ry="6" fill="#888"/>'
    return bg, fg_diff, fg_knn, fg_mog2

def svg_featmatch():
    # SIFT 128维 vs ORB 256bit vs BRISK 512bit
    sift_desc = '<text x="10" y="20" font-size="11" fill="#555">128 维浮点</text>' + ''.join([f'<rect x="{10+(i%16)*10}" y="{30+(i//16)*8}" width="8" height="6" fill="#4a90e2" opacity="{0.3+0.7*(i%5)/4}"/>' for i in range(128)])
    orb_desc = '<text x="10" y="20" font-size="11" fill="#555">256 bit 二值</text>' + ''.join([f'<rect x="{10+(i%16)*10}" y="{30+(i//16)*8}" width="8" height="6" fill="{("#000","#fff")[(i*7)%2]}"/>' for i in range(128)])
    brisk_desc = '<text x="10" y="20" font-size="11" fill="#555">512 bit 二值</text>' + ''.join([f'<rect x="{10+(i%16)*10}" y="{30+(i//16)*8}" width="8" height="6" fill="{("#000","#fff")[(i*13)%2]}"/>' for i in range(128)])
    return sift_desc, orb_desc, brisk_desc

def svg_tracker():
    # KCF vs CSRT vs MOSSE 跟踪框稳定性对比（抖动 vs 准度 vs 速度）
    init = '<rect x="0" y="0" width="180" height="120" fill="#f5f5dc"/><rect x="60" y="40" width="40" height="40" fill="none" stroke="red" stroke-width="2"/><text x="80" y="35" text-anchor="middle" font-size="11" fill="red">初始框</text>'
    kcf = '<rect x="0" y="0" width="180" height="120" fill="#f5f5dc"/><rect x="75" y="48" width="36" height="36" fill="none" stroke="#e67e22" stroke-width="2" stroke-dasharray="3,2"/><text x="93" y="43" text-anchor="middle" font-size="11" fill="#e67e22">KCF 快</text>'
    csrt = '<rect x="0" y="0" width="180" height="120" fill="#f5f5dc"/><rect x="60" y="40" width="40" height="40" fill="none" stroke="#27ae60" stroke-width="2"/><text x="80" y="35" text-anchor="middle" font-size="11" fill="#27ae60">CSRT 准</text>'
    mosse = '<rect x="0" y="0" width="180" height="120" fill="#f5f5dc"/><rect x="50" y="30" width="50" height="50" fill="none" stroke="#9b59b6" stroke-width="2" stroke-dasharray="2,2"/><text x="75" y="25" text-anchor="middle" font-size="11" fill="#9b59b6">MOSSE 极快</text>'
    return init, kcf, csrt, mosse

def svg_stereo():
    # 双目视差示意
    left = '<rect x="0" y="0" width="180" height="120" fill="#445"/><circle cx="50" cy="60" r="25" fill="#e74c3c"/><circle cx="120" cy="60" r="15" fill="#3498db"/><text x="90" y="110" text-anchor="middle" font-size="11" fill="#ccc">左相机</text>'
    right = '<rect x="0" y="0" width="180" height="120" fill="#445"/><circle cx="70" cy="60" r="25" fill="#e74c3c"/><circle cx="128" cy="60" r="15" fill="#3498db"/><text x="90" y="110" text-anchor="middle" font-size="11" fill="#ccc">右相机</text>'
    disp = '<rect x="0" y="0" width="180" height="120" fill="#000"/><circle cx="50" cy="60" r="25" fill="#fff"/><circle cx="120" cy="60" r="15" fill="#888"/><text x="90" y="110" text-anchor="middle" font-size="11" fill="#ccc">视差图（近处更亮）</text>'
    return left, right, disp

def svg_segment():
    # 原图 vs Watershed vs GrabCut vs 区域生长
    orig = '<rect x="0" y="0" width="180" height="120" fill="#b4c7e7"/><circle cx="90" cy="60" r="35" fill="#e74c3c"/>'
    ws = '<rect x="0" y="0" width="180" height="120" fill="#fff"/><circle cx="90" cy="60" r="35" fill="#e74c3c" stroke="#000" stroke-width="1"/><text x="90" y="110" text-anchor="middle" font-size="10" fill="#333">Watershed 过分割风险</text>'
    gc = '<rect x="0" y="0" width="180" height="120" fill="#888"/><circle cx="90" cy="60" r="35" fill="#e74c3c"/><text x="90" y="110" text-anchor="middle" font-size="10" fill="#fff">GrabCut（要框）</text>'
    rg = '<rect x="0" y="0" width="180" height="120" fill="#fff"/><circle cx="90" cy="60" r="25" fill="#e74c3c"/><circle cx="90" cy="60" r="35" fill="none" stroke="#aaa" stroke-dasharray="3,3"/><text x="90" y="110" text-anchor="middle" font-size="10" fill="#333">区域生长（要点种子）</text>'
    return orig, ws, gc, rg

# ========== 每个算法的加厚内容 ==========
# key = 算法目录名，value = dict(page -> 要追加的 markdown 片段)

EXT = {}

# -------- MOG2 背景建模 --------
EXT['mog2'] = {
'concepts': '''
## 🔍 直观对比：三种背景减法谁最强？

**帧差法**只看"相邻两帧差"，物体一旦停住就消失；**KNN** 用 K 个最近邻建模，对动态树叶更宽容但慢半拍；**MOG2** 用自适应 K 个高斯，每像素高斯数量自动增减，是速度和鲁棒的最优平衡。

<div style="text-align:center">
<svg xmlns="http://www.w3.org/2000/svg" width="720" height="160" style="background:#fafbfc;border-radius:12px;border:1px solid #eaecef">
  <g transform="translate(10,5)">
    <text x="110" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">原图（走路的人+树叶抖动）</text>
    <rect x="0" y="28" width="220" height="120" fill="#b4c7e7"/>
    <rect x="0" y="108" width="220" height="40" fill="#7a8e5a"/>
    <circle cx="60" cy="60" r="6" fill="#2ecc71" opacity="0.7"/>
    <circle cx="90" cy="60" r="6" fill="#2ecc71" opacity="0.7"/>
    <circle cx="120" cy="60" r="6" fill="#2ecc71" opacity="0.7"/>
    <rect x="150" y="60" width="25" height="50" fill="#2c3e50"/>
    <circle cx="162" cy="50" r="10" fill="#f4c28b"/>
  </g>
  <g transform="translate(250,5)">
    <text x="110" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">帧差法（只看见边缘）</text>
    <rect x="0" y="28" width="220" height="120" fill="#000"/>
    <rect x="145" y="55" width="6" height="55" fill="#fff"/>
    <rect x="174" y="55" width="6" height="55" fill="#fff"/>
    <text x="110" y="135" text-anchor="middle" font-size="10" fill="#888">人停了就消失</text>
  </g>
  <g transform="translate(490,5)">
    <text x="110" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">MOG2（整个人+阴影灰）</text>
    <rect x="0" y="28" width="220" height="120" fill="#000"/>
    <ellipse cx="162" cy="120" rx="25" ry="6" fill="#888"/>
    <rect x="150" y="60" width="25" height="50" fill="#fff"/>
    <circle cx="162" cy="50" r="10" fill="#fff"/>
    <text x="110" y="135" text-anchor="middle" font-size="10" fill="#888">阴影标灰，可分离</text>
  </g>
</svg>
</div>

## 🧓 老奶奶能听懂的版本

想象你坐在窗前看小区。**帧差法**像个每隔 1 秒看一眼、只记"谁动了"的老花眼——那人站着打电话，它就以为人没了。**MOG2** 像你自己：你知道那棵树一直在晃（"绿/蓝/灰"三种状态都是"正常"），同时你也能一下子认出"那个穿黑衣的人是新来的"，还能看出来他脚下的黑影不是他本人。

## 🧩 为什么 "K" 个高斯而不是 1 个？

- **1 个高斯**假设像素"一直在某个平均值附近轻微抖动"——树叶、波浪、喷泉这种多状态像素直接崩；
- **固定 K（比如 5）个高斯**浪费算力，纯色墙面用 1 个就够；
- **MOG2 自动选 K**：哪个像素分布简单就少用几个，复杂就多加，省下的算力给更需要的地方。
''',
'painpoints': '''
## 🚨 实战最常踩的 5 个坑（续）

### 6. 鬼影（Ghost）——它怎么还在那里？

**现象**：人走了之后，原地还留着一个半透明人影，过几秒才消失。
**根因**：学习率 α 太小，旧背景"忘不掉"；或者那个人一开始就被模型当成了背景（第一帧刚好有他）。
**解法**：
- 启动时**前 30~50 帧里不要有人**，让模型先"认识空场景"；
- 前 50 帧把 `learningRate` 临时设成 `1.0`（强制每帧 100% 更新），之后再降回 `-1`（自动）。

### 7. 水面/喷泉/雨永远是前景

水面反光是像素值**持续多峰跳变**，没有稳定背景。**唯一靠谱办法**：把感兴趣区域（ROI）扣掉水面对应的 mask，不指望 MOG2 解决。

### 8. 阴影参数 shadowValue 默认 127 就够

别改成 255，会和前景混在一起；别改成 0，会和背景混在一起。**127 是专门为 "中间灰" 留的标记值**，后处理按 `mask == 127` 单独过滤阴影。

### 9. detectShadows 关 vs 开

- **开**：多花 15~20% 算力，多一个灰色通道，但后处理方便；
- **关**：速度快，阴影会被涂成白块当成前景。**嵌入式端算力紧就关**，其他时候默认开。

### 10. 室内日光灯下 100Hz 闪烁

荧光灯实际是以 100Hz 频率闪烁的（50Hz 交流电 ×2 峰值），MOG2 会把墙壁当"运动物体"。
**解法**：快门设成 1/100 的整数倍；或者把 `varThreshold` 提到 24~32 容忍这种周期性小幅跳变。
''',
'tricks': '''
## 🎯 参数速查卡（续）

### 场景到参数的映射表

| 场景 | history | varThreshold | detectShadows | 必加后处理 |
| --- | --- | --- | --- | --- |
| 室外停车场慢车 | 500 | 24 | 开 | 开 3×3 + 闭 7×7 + 面积过滤 |
| 室内走廊快速通过 | 100 | 16 | 关（无日光阴影）| 开 3×3 |
| 树叶/水面前景 | 200 | 36~64 | 开 | 开 5×5 + 更大闭核 |
| 红外夜视 | 30 | 36 | 关 | 中值滤波 3×3 先去噪 |
| 低空无人机 | 200 | 16 | 开 | 光流补偿后再 MOG2 |

### 性能调优口诀

> **背景在前三十帧，学率拉高忘旧人；<br/>阈值看噪不要硬，先开后闭再滤洞；<br/>阴影灰值一二七，后处理时单独剔。**

### OpenCV.js 替代方案

本项目真机实验室里由于 OpenCV.js 构建不包含 `createBackgroundSubtractorMOG2`（是编译开关问题，不是算法问题），可用 **KNN 背景建模** 近似达到相似效果，真机实验室里已提供 KNN 实现供你调参。
'''
}

# -------- KCF 跟踪 --------
EXT['kcf'] = {
'architecture': '''
## 🏗 算法流程（续）：循环移位的魔法

KCF 最天才的地方是：**不需要真的采成千上万个负样本**——它利用"循环移位"性质，一张图平移 1 格、2 格……N 格，就自动生成 N×N 个"虚拟样本"，而这些样本在傅里叶域里**正好可以用对角矩阵表示**，训练瞬间变成元素级乘法，速度暴增几千倍。

```mermaid
flowchart LR
  A[初始框 x] --> B[提取 HOG 特征]
  B --> C[循环移位 → 成千虚拟样本]
  C --> D[在傅里叶域岭回归<br/>元素级运算 O(n²)→O(n)]
  D --> E[得到相关滤波模板 w]
  E --> F[下一帧在搜索区做响应图<br/>argmax 即新位置]
  F --> G[更新模板 w ← (1-η)w + ηw_new]
  G --> F
```

## 📐 三种核函数对比

| 核 | 速度 | 精度 | 推荐场景 |
| --- | --- | --- | --- |
| **线性核** | ⚡ 最快 | 一般 | 高帧率 >100fps 场景 |
| **高斯核（默认）** | 中等 | 最好 | 通用场景 |
| **多项式核** | 慢 | 与高斯接近 | 不推荐 |

这就是为什么 OpenCV 默认用高斯核——综合性价比最高。

## 🔁 为什么会"漂移"？

每帧都在更新模板，只要有几帧跟偏了（遮挡、光照突变、形变），**错误就会慢慢累积进模板**，框越来越偏，最后彻底飞掉。这个问题叫**模型漂移（model drift）**，是所有在线更新跟踪器的通病。
''',
'painpoints': '''
## 🚨 KCF 的 5 大致命弱点

1. **不抗尺度变化**：原版 KCF 框大小固定，人走远了框还那么大，背景被框进来 → 模板污染；
2. **不抗出视野**：目标完全被挡 1 帧以上，直接跟飞，再也救不回来；
3. **不能从失败中恢复**：跟丢了不会报"我丢了"，而是继续自信地把随便什么东西当目标；
4. **HOG 特征对形变敏感**：人转身、弯腰时 HOG 完全变了，响应峰值骤降；
5. **灰度/HOG 对颜色完全无感**：穿红衣的人和穿蓝衣的人长得很像时容易认错。

**实战判定跟丢的黄金指标**：响应图最大值 PSR（Peak-to-Sidelobe Ratio）< 6 时认为已跟丢，触发重检测。
''',
'tricks': '''
## 🎯 调参与替换指南

### 如果发现 KCF 不好用，按顺序检查

1. **框是不是太大**？框里一半是背景 → 重新初始化，给紧一点；
2. **目标是不是尺度在变**？换 **DSST/CSRT**（它们内置尺度估计）；
3. **是不是经常被挡**？换 **CSRT**（它有遮挡检测+重检测）；
4. **是不是要极高帧率 >200fps**？换 **MOSSE**（牺牲精度换速度）；
5. **是不是旋转剧烈**？KCF 对平面外旋转很差，用 **CSRT** 或基于深度学习的跟踪器。

### KCF vs CSRT vs MOSSE 一张图说清

<div style="text-align:center">
<svg xmlns="http://www.w3.org/2000/svg" width="720" height="170" style="background:#fafbfc;border-radius:12px;border:1px solid #eaecef">
  <g transform="translate(20,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#e67e22">KCF</text>
    <text x="100" y="35" text-anchor="middle" font-size="11" fill="#555">核相关滤波 · 通用</text>
    <rect x="0" y="45" width="200" height="25" fill="#eee"/>
    <rect x="0" y="45" width="140" height="25" fill="#e67e22"/>
    <text x="100" y="62" text-anchor="middle" font-size="10" fill="#fff">速度 70%</text>
    <rect x="0" y="75" width="200" height="25" fill="#eee"/>
    <rect x="0" y="75" width="130" height="25" fill="#e67e22"/>
    <text x="100" y="92" text-anchor="middle" font-size="10" fill="#fff">精度 65%</text>
    <rect x="0" y="105" width="200" height="25" fill="#eee"/>
    <rect x="0" y="105" width="60" height="25" fill="#e67e22"/>
    <text x="100" y="122" text-anchor="middle" font-size="10" fill="#333">抗遮挡 30%</text>
  </g>
  <g transform="translate(260,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#27ae60">CSRT</text>
    <text x="100" y="35" text-anchor="middle" font-size="11" fill="#555">信道与空间可靠性 · 准</text>
    <rect x="0" y="45" width="200" height="25" fill="#eee"/>
    <rect x="0" y="45" width="80" height="25" fill="#27ae60"/>
    <text x="100" y="62" text-anchor="middle" font-size="10" fill="#333">速度 40%</text>
    <rect x="0" y="75" width="200" height="25" fill="#eee"/>
    <rect x="0" y="75" width="180" height="25" fill="#27ae60"/>
    <text x="100" y="92" text-anchor="middle" font-size="10" fill="#fff">精度 90%</text>
    <rect x="0" y="105" width="200" height="25" fill="#eee"/>
    <rect x="0" y="105" width="160" height="25" fill="#27ae60"/>
    <text x="100" y="122" text-anchor="middle" font-size="10" fill="#fff">抗遮挡 80%</text>
  </g>
  <g transform="translate(500,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#9b59b6">MOSSE</text>
    <text x="100" y="35" text-anchor="middle" font-size="11" fill="#555">最小输出平方误差 · 极快</text>
    <rect x="0" y="45" width="200" height="25" fill="#eee"/>
    <rect x="0" y="45" width="195" height="25" fill="#9b59b6"/>
    <text x="100" y="62" text-anchor="middle" font-size="10" fill="#fff">速度 98%</text>
    <rect x="0" y="75" width="200" height="25" fill="#eee"/>
    <rect x="0" y="75" width="90" height="25" fill="#9b59b6"/>
    <text x="100" y="92" text-anchor="middle" font-size="10" fill="#333">精度 45%</text>
    <rect x="0" y="105" width="200" height="25" fill="#eee"/>
    <rect x="0" y="105" width="30" height="25" fill="#9b59b6"/>
    <text x="100" y="122" text-anchor="middle" font-size="10" fill="#333">抗遮挡 15%</text>
  </g>
</svg>
</div>

**口诀**：
> **要稳要准用 CSRT，要快要通用 KCF，几百帧跑嵌入式用 MOSSE。**
'''
}

# -------- LBP 纹理 --------
EXT['lbp'] = {
'architecture': '''
## 🏗 算法全流程（从图到判别）

```mermaid
flowchart LR
  A[原图转灰度] --> B[CLAHE 光照均衡]
  B --> C[划分 cell 8×8 或 16×16]
  C --> D["每个像素算 LBP(P=8,R=1)"]
  D --> E[每个 cell 统计 59 维 uniform 直方图]
  E --> F[所有 cell 直方图拼接 → 一个大向量]
  F --> G[L2-Hys 归一化（先 L2、裁剪到 0.2、再 L2）]
  G --> H{用什么任务?}
  H --人脸--> I[和模板做卡方距离比较]
  H --纹理分类--> J[送 SVM 分类]
  H --缺陷检测--> K[找非均匀模式异常聚集的 cell]
```

## 🔑 为什么 "划分 cell" 这么重要？

直接对整张图做 LBP 直方图只有 59 维——它只告诉你"图里有哪些模式"，但**位置信息全丢了**（一张眼睛图和一张嘴图可能有相同直方图）。分成 cell 之后：
- 每个 cell 自己的直方图描述**局部纹理**；
- 拼接顺序保留**空间位置**（眼睛在上面 cell、嘴巴在下面 cell）；
- 这就像把脸拆成"左眉、右眉、左眼、右眼、鼻梁、左嘴角、右嘴角、下巴"，一块一块对比。
''',
'concepts': '''
## 🔍 三种 LBP 变体一张图看懂

<div style="text-align:center">
<svg xmlns="http://www.w3.org/2000/svg" width="720" height="170" style="background:#fafbfc;border-radius:12px;border:1px solid #eaecef">
  <g transform="translate(20,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">原始 LBP (3×3)</text>
    <rect x="20" y="30" width="160" height="120" fill="#fff" stroke="#ccc"/>
    <!-- 3x3 grid -->
    <g font-size="10" text-anchor="middle">
      <rect x="40" y="50" width="30" height="30" fill="#eee"/><text x="55" y="69" fill="#333">6</text>
      <rect x="70" y="50" width="30" height="30" fill="#ddd"/><text x="85" y="69" fill="#333">9</text>
      <rect x="100" y="50" width="30" height="30" fill="#eee"/><text x="115" y="69" fill="#333">5</text>
      <rect x="40" y="80" width="30" height="30" fill="#bbb"/><text x="55" y="99" fill="#fff">3</text>
      <rect x="70" y="80" width="30" height="30" fill="#ddd"/><text x="85" y="99" fill="#c00" font-weight="bold">7</text>
      <rect x="100" y="80" width="30" height="30" fill="#eee"/><text x="115" y="99" fill="#333">8</text>
      <rect x="40" y="110" width="30" height="30" fill="#eee"/><text x="55" y="129" fill="#333">4</text>
      <rect x="70" y="110" width="30" height="30" fill="#ddd"/><text x="85" y="129" fill="#333">7</text>
      <rect x="100" y="110" width="30" height="30" fill="#eee"/><text x="115" y="129" fill="#333">6</text>
    </g>
    <text x="100" y="162" text-anchor="middle" font-size="10" fill="#888">256 种模式，半径固定</text>
  </g>
  <g transform="translate(260,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">圆形 LBP (P=8,R=2)</text>
    <rect x="20" y="30" width="160" height="120" fill="#fff" stroke="#ccc"/>
    <circle cx="100" cy="90" r="50" fill="none" stroke="#ddd" stroke-dasharray="3,2"/>
    <circle cx="100" cy="90" r="4" fill="#c00"/>
    <circle cx="150" cy="90" r="3" fill="#444"/><circle cx="135" cy="55" r="3" fill="#444"/>
    <circle cx="100" cy="40" r="3" fill="#444"/><circle cx="65" cy="55" r="3" fill="#444"/>
    <circle cx="50" cy="90" r="3" fill="#444"/><circle cx="65" cy="125" r="3" fill="#444"/>
    <circle cx="100" cy="140" r="3" fill="#444"/><circle cx="135" cy="125" r="3" fill="#444"/>
    <text x="100" y="162" text-anchor="middle" font-size="10" fill="#888">半径可调，双线性插值</text>
  </g>
  <g transform="translate(500,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">Uniform LBP</text>
    <rect x="20" y="30" width="160" height="120" fill="#fff" stroke="#ccc"/>
    <rect x="35" y="45" width="60" height="25" fill="#e8f4e8" stroke="#5cb85c"/><text x="65" y="62" text-anchor="middle" font-size="10">58 种 uniform</text>
    <rect x="105" y="45" width="60" height="25" fill="#f8e8e8" stroke="#d9534f"/><text x="135" y="62" text-anchor="middle" font-size="10">198 种混为 1</text>
    <text x="100" y="100" text-anchor="middle" font-size="11" fill="#333">共 59 维，抗噪 ↑4×</text>
    <text x="100" y="120" text-anchor="middle" font-size="10" fill="#888">覆盖自然图像 90%+ 模式</text>
    <text x="100" y="162" text-anchor="middle" font-size="10" fill="#888">人脸识别标准配置</text>
  </g>
</svg>
</div>

## 🧓 用大白话解释 LBP

LBP 就像每个像素都在做"我邻居谁比我亮"的小投票。把周围 8 个邻居挨个比一遍，比我亮记 1、比我暗记 0，拼起来是个 8 位二进制数——**这个数就是这个像素的"纹理密码"**。

神奇的是，**不管你整张图怎么调亮、调暗、乘个系数**，邻居之间的大小关系几乎不变，所以密码也不变——这就是 LBP "不怕光照变化"的根本原因。

## ⚠️ 什么时候不能用 LBP？

- **低分辨率 < 32×32 的脸**：cell 太少，拼接后的直方图没信息量；
- **大范围视角变化**：侧脸和正脸纹理分布完全不同；
- **严重模糊的图像**：邻居之间大小关系被抹平，密码失去意义；
- **要求语义级别识别**（"这是猫还是狗"）：LBP 只描述纹理，不懂形状语义，必须搭配 HOG 或深度学习。
''',
'painpoints': '''
## 🚨 实战坑点补充

### 1. 不做 CLAHE 直接上 LBP = 送人头

如果图像一边亮一边暗（窗户逆光、闪光灯），同一张脸上"亮的那半"邻居都比中心亮、"暗的那半"邻居都比中心暗，LBP 密码直接错乱。**CLAHE 必须放在最前面**，参数 `clipLimit=2.0, tileGridSize=(8,8)` 是标准。

### 2. cell 大小不是越大越好

- **cell 太小（4×4）**：直方图稀疏（每个 cell 只有 16 个像素），统计不稳，识别率差；
- **cell 太大（32×32）**：空间位置精度丢失，变成"整坨平均"；
- **16×16 是 100×100 人脸的甜点**，对齐好的脸几乎都是这个值。

### 3. 归一化别用 L1，一定 L2-Hys

L1 归一化对大值（偶尔出现的强边缘）太敏感；L2-Hys 是 HOG 论文里提出的两步归一化（先 L2、裁剪到 0.2、再 L2），**对局部光照突变最鲁棒**。OpenCV 里用 `NORM_L2` 再手动 clip 也行。

### 4. 直方图距离用错 = 识别率掉 20%

直方图不是欧氏空间里的向量，而是**概率单纯形上的点**。距离度量必须用：
- **卡方距离**（χ²）：直方图匹配的金标准；
- **Hellinger 距离**（Bhattacharyya）：对小 bin 差异更敏感；
- **直方图相交**：快，但对非均匀光照鲁棒性差。
**绝对不要直接用欧氏距离**。

### 5. 对齐！对齐！对齐！

LBP 是拼 cell 的直方图，**人脸左右眼差 5 个像素，一个 cell 的内容就全换了**。必须先用人脸关键点对齐到两眼水平+固定尺寸（典型 100×100 两眼间距 40 像素），否则再好的特征也白搭。
'''
}

# -------- 双边滤波 --------
EXT['bilateral'] = {
'concepts': '''
## 🧓 大白话解释：双边滤波 = "看颜色交朋友"

普通高斯模糊是"离得近的像素一起平均"——边缘被糊掉。双边滤波多了一个条件："不仅要离得近，**颜色还要接近**才一起平均"。

打比方：你在派对上找人平均意见——
- **高斯模糊**：只找身边 5 米内的所有人，不管他们是不是一伙的；
- **双边滤波**：只找身边 5 米内**且和你穿同色衣服**的人。

结果就是：**衣服内部大家一起平均（磨皮），衣服和衣服之间的边缘（颜色突变处）没人跨过去，边缘依然锐利**。

## 🔍 效果对比图

<div style="text-align:center">
<svg xmlns="http://www.w3.org/2000/svg" width="720" height="170" style="background:#fafbfc;border-radius:12px;border:1px solid #eaecef">
  <g transform="translate(20,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">原图（带噪点）</text>
    <rect x="20" y="30" width="160" height="120" fill="#fff"/>
    <rect x="20" y="30" width="80" height="120" fill="#d4a373"/>
    <rect x="100" y="30" width="80" height="120" fill="#3a5a40"/>
    <g>
      <circle cx="50" cy="60" r="1.5" fill="#000"/><circle cx="70" cy="80" r="1.5" fill="#fff"/>
      <circle cx="120" cy="50" r="1.5" fill="#000"/><circle cx="150" cy="100" r="1.5" fill="#fff"/>
      <circle cx="60" cy="120" r="1.5" fill="#000"/><circle cx="140" cy="70" r="1.5" fill="#fff"/>
    </g>
    <line x1="100" y1="30" x2="100" y2="150" stroke="#000" stroke-width="2"/>
  </g>
  <g transform="translate(260,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">高斯模糊（边缘糊了）</text>
    <rect x="20" y="30" width="160" height="120" fill="#fff"/>
    <defs><linearGradient id="grad1" x1="0" x2="1"><stop offset="0" stop-color="#d4a373"/><stop offset="0.5" stop-color="#a07b5a"/><stop offset="1" stop-color="#3a5a40"/></linearGradient></defs>
    <rect x="20" y="30" width="160" height="120" fill="url(#grad1)"/>
    <text x="100" y="160" text-anchor="middle" font-size="10" fill="#888">边缘被跨过去平均了</text>
  </g>
  <g transform="translate(500,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">双边滤波（边缘保住了）</text>
    <rect x="20" y="30" width="160" height="120" fill="#fff"/>
    <rect x="20" y="30" width="80" height="120" fill="#d4a373"/>
    <rect x="100" y="30" width="80" height="120" fill="#3a5a40"/>
    <line x1="100" y1="30" x2="100" y2="150" stroke="#000" stroke-width="2"/>
    <text x="100" y="160" text-anchor="middle" font-size="10" fill="#888">噪点没了，边还在</text>
  </g>
</svg>
</div>
''',
'architecture': '''
## 🏗 数学公式直观化

双边滤波的权重 = **空间高斯 × 颜色高斯**：

$$
w(i,j,k,l) = \exp\left(-\frac{(i-k)^2 + (j-l)^2}{2\sigma_s^2}\right) \cdot \exp\left(-\frac{\|I(i,j)-I(k,l)\|^2}{2\sigma_r^2}\right)
$$

- 第一个高斯（σ_s）：**离得多近**——决定"磨皮力度"（半径）；
- 第二个高斯（σ_r）：**颜色多像**——决定"保边阈值"。

两个数乘起来，离得远权重小，颜色差得多权重也小；**只有又近又像**的像素才真的参与平均。

## 📊 σ_s 和 σ_r 的直觉

| 参数 | 太小 | 正好 | 太大 |
| --- | --- | --- | --- |
| **σ_s（空间）** | 没效果 | d=2σ_s 即可 | 太慢，但不会更糊 |
| **σ_r（颜色）** | 什么都不平滑（只平均同色） | 30~60（磨皮） | 退化成普通高斯（什么都平均）|

**经验公式**：`d = -1`（自动）、`sigmaColor = sigmaSpace = 50~100` 是通用美颜起点。

## 🧩 为什么双边滤波慢？怎么加速？

高斯模糊可以用"分离卷积"先横再竖，复杂度 O(N)；双边滤波**因为乘了颜色高斯，无法分离**，必须 O(N r²) 复杂度。
加速方法：
- **OpenCV 里自动用 O(1) 近似实现**（论文作者 Paris & Durand 提出），对 σ 大的情况提速 10 倍以上；
- 实在太慢可以用**引导滤波（Guided Filter）**或**Domain Transform**，效果类似、速度快一个量级。
''',
'painpoints': '''
## 🚨 常见坑点

1. **美颜场景 σColor 别开太大**：>80 会把五官当"平坦区域"糊掉，变成塑料脸；
2. **σSpace 不要小于 σColor**：会出现"颜色权重为主、空间权重几乎不管"的奇怪效果；
3. **迭代两次 σ=30 比一次 σ=60 更自然**：单次强滤波容易出现"梯度反转"伪影（边缘旁出现白边）；
4. **对彩色图要在 Lab 空间处理**：直接在 RGB 空间做，色差不是欧氏距离，保边不准；
5. **实时视频 >1080p 时别用双边**：引导滤波（`cv2.ximgproc.guidedFilter`）速度快 5~10 倍。
''',
'tricks': '''
## 🎯 参数速查卡

| 场景 | d | σColor | σSpace | 备注 |
| --- | --- | --- | --- | --- |
| 人脸磨皮（轻） | -1 | 30 | 30 | 几乎看不出来 |
| 人脸磨皮（中） | -1 | 50 | 50 | 美颜 App 典型值 |
| 人脸磨皮（强） | -1 | 75 | 75 | 卡通化效果 |
| 去 JPEG 块效应 | -1 | 20 | 20 | 弱保边平滑 |
| HDR 色调映射 | -1 | 20 | 100 | 大半径小色差 |
| 卡通化（Cartoon） | -1 | 100 | 100 | 迭代 3~5 次后再 edge |

### 美颜典型管线（3 行代码效果拉满）

```python
# 1. 磨皮（双边）
smooth = cv2.bilateralFilter(img, -1, 50, 50)
# 2. 细节增强（原图 - 磨皮 = 细节，加回去）
detail = cv2.addWeighted(img, 1.5, smooth, -0.5, 0)
# 3. 美白（简单 gamma）
result = np.clip(np.power(detail/255., 0.85)*255, 0, 255).astype('uint8')
```
'''
}

# -------- CLAHE --------
EXT['clahe'] = {
'concepts': '''
## 🧓 大白话解释 CLAHE：局部聪明的对比度增强

普通直方图均衡（HE）是"整张图一把抓"——有一个地方太亮或太暗，整张图都被它带歪。自适应直方图均衡（AHE）把图切成小块，每块自己均衡，但**小块里出现一个特别亮的噪声点，这一块就被放大得特别夸张**（噪声爆炸）。

**CLAHE** = AHE + **对比度裁剪（Contrast Limited）**：
- 每个小块里，超过阈值的像素"溢出量"**重新均匀分给所有 bin**，不让某几个 bin 独占对比度；
- 最后双线性插值拼接块与块，消除块边界。

打比方：HE 像把全国贫富差距一次性拉平（结果一线城市房价暴涨）；AHE 像每个城市自己调（结果某村出了个亿万富翁把全村人均拉高）；**CLAHE 像每个城市都设个"首富上限"，多出来的钱平分给全村**。

## 🔍 效果对比

<div style="text-align:center">
<svg xmlns="http://www.w3.org/2000/svg" width="720" height="160" style="background:#fafbfc;border-radius:12px;border:1px solid #eaecef">
  <g transform="translate(20,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">原图（逆光）</text>
    <rect x="20" y="30" width="160" height="120"/>
    <defs><linearGradient id="dark" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset="0.6" stop-color="#333"/><stop offset="1" stop-color="#fff"/></linearGradient></defs>
    <rect x="20" y="30" width="160" height="120" fill="url(#dark)"/>
    <text x="100" y="100" text-anchor="middle" font-size="11" fill="#fff">脸全黑，背景过曝</text>
  </g>
  <g transform="translate(260,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">普通 HE</text>
    <rect x="20" y="30" width="160" height="120"/>
    <rect x="20" y="30" width="160" height="120" fill="#888"/>
    <text x="100" y="100" text-anchor="middle" font-size="11" fill="#fff">噪声放大，背景发灰</text>
  </g>
  <g transform="translate(500,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#27ae60">CLAHE</text>
    <rect x="20" y="30" width="160" height="120"/>
    <rect x="20" y="30" width="160" height="120" fill="#b4a090"/>
    <circle cx="70" cy="80" r="15" fill="#d4a373"/>
    <text x="100" y="140" text-anchor="middle" font-size="11" fill="#333">脸清晰了，背景自然</text>
  </g>
</svg>
</div>
''',
'tricks': '''
## 🎯 参数速查卡

| 场景 | clipLimit | tileGridSize | 备注 |
| --- | --- | --- | --- |
| 通用 | 2.0 | (8,8) | 论文默认值 |
| 人脸（自然） | 2.0 | (8,8) | 先做再上 LBP/HOG |
| 医学 X 光 | 3.0 | (8,8) | 肺纹理要明显 |
| 红外热成像 | 4.0 | (16,16) | 信噪比低，大 tile |
| 文档扫描 | 1.5 | (8,8) | 文字要黑，纸要白 |
| 弱光夜景增强 | 3.0~4.0 | (8,8) | 先去噪再 CLAHE |

### 必知 5 条

1. **必须在 Lab 空间的 L 通道做**：`cv2.cvtColor(img, COLOR_BGR2LAB)`，拆分 L/a/b，只对 L 做 CLAHE，再合回去；直接对 RGB 做颜色会飘；
2. **clipLimit 不是越大越好**：>4.0 基本等于没裁剪，噪声暴增；
3. **tileGridSize 8×8 是甜点**：4×4 过度增强，16×16 退化成全局 HE；
4. **CLAHE 永远放在去噪之后、特征提取之前**；
5. **做匹配任务时**（光流、特征匹配、立体匹配），CLAHE 是提升低光匹配率性价比最高的一步。

### 三行黄金代码

```python
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
l,a,b = cv2.split(lab)
l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(l)
result = cv2.cvtColor(cv2.merge([l,a,b]), cv2.COLOR_LAB2BGR)
```
'''
}

# 批量给其他薄算法追加简短扩展（避免脚本过长，这里对剩余算法用通用薄扩展）
# 下面每个通用扩展聚焦于"易混点+参数口诀+何时用"

GENERIC = {
'akaze': {
'concepts': '''
## 🧓 大白话：AKAZE = "加速版的 KAZE"，SIFT 的免费替代品

KAZE 用非线性扩散滤波（加性算子分裂 AOS）构造尺度空间，**保留边缘**的同时做多尺度，比 SIFT 的高斯尺度空间（糊边）更精确，但 AOS 求解慢。AKAZE 用 **Fast Explicit Diffusion（FED）** 替代 AOS，速度快 3~5 倍。

关键点：
- **二进制描述子 M-LDB**：旋转+尺度+光照不变，**和 SIFT 一样稳健但比 SIFT 快两个数量级**；
- **专利免费**：SIFT/SURF 曾受专利保护，AKAZE 完全免费可商用；
- **OpenCV 官方推荐的"通用特征点"首选之一**（和 ORB 并列）。

## ORB vs AKAZE vs BRISK 怎么选？

| 维度 | ORB | AKAZE | BRISK |
| --- | --- | --- | --- |
| 速度 | ⚡⚡⚡ | ⚡⚡ | ⚡⚡ |
| 尺度/旋转不变 | 有 | 有 | 有 |
| 描述子 | 256 bit | 486 bit（可配） | 512 bit |
| 鲁棒性 | 一般 | **最好** | 较好 |
| 专利 | 免费 | 免费 | 免费 |
| 推荐 | 实时 SLAM | 通用匹配/拼接 | 嵌入式 |
''',
'tricks': '''
## 🎯 调参口诀

> **descriptor_type 用 M-LDB（默认），threshold 调 0.001 灵敏 / 0.01 稀疏；octaves 4~8 足够，NOCTAVES 和 SIFT 对齐。**

### OpenCV.js 真机可用！

本项目真机实验室的 AKAZE 真机页面直接调 OpenCV.js 即可：`new cv.AKAZE()`，配合 BFMatcher with HAMMING 距离就能跑。**这是开源无专利、真机可调的最稳特征点算法**。
'''
},
'csrt': {
'concepts': '''
## 🧓 大白话：CSRT = "跟踪器里的准神"

CSRT 的全称是 **Channel and Spatial Reliability Tracking**（信道与空间可靠性跟踪）。它和 KCF 的核心差异是：

1. **信道可靠性（Channel Reliability）**：HOG 有 31 个通道、颜色有多个通道——CSRT 会自动学习"当前帧哪些通道靠谱"，不靠谱的通道降权（比如目标被遮挡时 HOG 乱了，就少信 HOG、多信颜色）。
2. **空间可靠性（Spatial Reliability）**：KCF 把框内所有像素都当训练样本，但框经常会框进背景——CSRT 学习一个"空间权重图"，告诉滤波器"框里哪些像素真的是目标、哪些是背景"，**从根上减轻背景污染**。

代价：速度比 KCF 慢约 1.5~2 倍（CPU 上 ~50fps vs ~100fps），但精度显著更高，尤其抗尺度变化和遮挡。

## 选型口诀

> **KCF 80 分快，CSRT 90 分稳，MOSSE 60 分极速。**
> **算力允许时默认用 CSRT**，这是 OpenCV 官方在 2018 年后推荐的默认跟踪器。
''',
'painpoints': '''
## 🚨 CSRT 也有坑

1. **初始框要紧**：和 KCF 一样，别给"差不多就行"的框，越紧越准；
2. **极小目标（<15×15）效果差**：HOG cell 是 8×8，目标太小根本没法提特征；
3. **低帧率视频（<10fps）反而容易跟飞**：帧间位移太大，相关滤波响应图出现多峰；
4. **OpenCV.js 构建不含 CSRT 跟踪器**：真机实验室用不了，但可以在本页原理互动里体会算法思想。
'''
},
'region-growing': {
'concepts': '''
## 🧓 大白话：区域生长 = "往水里滴墨，让它自然晕开"

用户给一个（或几个）"种子点"，算法从种子开始往外扩散：**邻居像素和当前区域平均颜色差不超过阈值，就吸收进来**。一直扩散到所有相似像素都被吸收，剩下的就是边界。

这是**最符合人类直觉**的分割方法——你指哪里，它就给你分出那一片。

## 适用场景

- **医学图像分割**：医生在 CT 上点一下肿瘤，自动生长出整个肿瘤轮廓；
- **交互抠图**：用户点一下前景+点一下背景，类似魔棒工具；
- **遥感图像**：点一片森林/农田，自动统计面积。

## 优缺点

| 优点 | 缺点 |
| --- | --- |
| 思想简单、符合直觉 | **要人工给种子**，全自动难 |
| 能分出不规则形状 | 对噪声敏感，易漏油 |
| 边界准确（在颜色跳变处自然停下） | 阈值是全局的，复杂图像不好调 |
| 不需要训练数据 | 慢（大图像要遍历很多像素） |
''',
'tricks': '''
## 🎯 使用口诀

> **种子选中间，阈值先小后加；先平滑再生长，不然噪点满图爬。**

1. **先高斯/双边平滑**：噪点会让种子生长出很多毛刺小洞；
2. **8 邻域比 4 邻域生长更自然**：4 邻域只能上下左右，边界呈锯齿；
3. **阈值从低往高调**：调小了长不满，调大了漏出去；
4. **加"同质性准则"**：不仅和区域均值比，还要和区域标准差比，防止在渐变图上一路长出去；
5. **多颗种子并行**：复杂前景点 3~5 颗种子，比一颗种子从头长靠谱得多。
'''
},
'distance-transform': {
'concepts': '''
## 🧓 大白话：距离变换 = "每个位置离最近的边界有多远"

对一张二值图（前景白、背景黑），距离变换给**每个白像素**计算"离最近黑像素的距离"，结果是一张灰度图：越亮代表离边界越远（越靠内部），越暗代表越靠近边界。

这是一个**基础工具**，本身不是完整算法，但在很多高级方法里是关键一步：
- **细化/骨架提取**：取距离变换的局部最大值，就是骨架；
- **匹配（Chamfer Matching）**：模板边缘和图像边缘距离越小越匹配；
- **分割后处理**：距离变换峰值 = 各连通块中心（比连通域中心稳）；
- **文字识别**：先距离变换再做归一化，对齐字符笔画粗细。

## 三种距离

| 距离类型 | 精度 | 速度 | 应用 |
| --- | --- | --- | --- |
| **DIST_L1**（曼哈顿）| 低 | ⚡最快 | 粗略骨架 |
| **DIST_L2**（欧氏）| 高 | 较快 | 通用首选 |
| **DIST_C**（棋盘）| 低 | 快 | 形态学预处理 |
''',
'tricks': '''
## 🎯 典型三步用法

```python
# 1. 二值化（前景是 255）
_, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
# 2. 距离变换，归一化到 0~1
dist = cv2.distanceTransform(bw, cv2.DIST_L2, 5)
cv2.normalize(dist, dist, 0, 1.0, cv2.NORM_MINMAX)
# 3. 再阈值化——得到确定前景（峰值区域）
_, sure_fg = cv2.threshold(dist, 0.5*dist.max(), 255, 0)
```

这正是 Watershed 分割里"找确定前景"的标准套路——距离变换在 Watershed 里几乎是必用前处理。
'''
},
'gabor': {
'concepts': '''
## 🧓 大白话：Gabor 滤波器 = "图像处理的单细胞视力"

人的视觉皮层里有一种"简单细胞"，对**特定方向、特定频率的条纹**特别敏感——比如看竖条纹时某些细胞疯狂放电、看横条纹时另一些细胞放电。Gabor 滤波器就是这种细胞的数学模型：一个高斯包络下的正弦波。

$$
g(x,y) = \exp\left(-\frac{x'^2+\gamma^2 y'^2}{2\sigma^2}\right) \cdot \cos\left(\frac{2\pi}{\lambda}x' + \psi\right)
$$

- λ（波长）决定条纹粗细（频率）；
- θ（角度）决定方向敏感；
- σ（高斯宽度）决定感受野大小。

**用一组不同方向（0°/45°/90°/135°）、不同频率的 Gabor 核卷积一张图，得到的多通道响应就是"纹理特征"**——这是 Palmprint、指纹识别、纹理分类、织物缺陷检测的经典特征。

## 和其他纹理特征对比

| 特征 | 物理含义 | 适合任务 |
| --- | --- | --- |
| **LBP** | 局部差异统计 | 人脸识别、粗纹理分类 |
| **HOG** | 边缘方向分布 | 行人检测、形状识别 |
| **Gabor** | 多方向多频率响应 | 指纹/掌纹、细纹理、医学 |
''',
'tricks': '''
## 🎯 实战要点

1. **典型配置**：5 个尺度（λ: 3,4,6,8,12）× 8 个方向（0°~180° 每 22.5°）= 40 个核，能覆盖绝大多数纹理；
2. **必须做归一化**：不同核的响应幅值差异大，直接拼起来大响应会压住小响应；
3. **降采样加速**：Gabor 响应是过完备的，可以下采样到 1/4 再拼，速度快 16 倍；
4. **PCA 降维**：40 通道拼起来向量太长，用 PCA 压到 50~100 维再送 SVM；
5. **Gabor 卷积可通过 FFT 加速**（频域乘），大核时比空间卷积快。

### 遗憾

OpenCV.js 构建**不包含** `getGaborKernel` 函数（真机实验室跑不了），但 Python/C++ 版本都有，可以在源码页对照三语种代码。
'''
},
'brisk': {
'concepts': '''
## 🧓 大白话补充：BRISK = "带尺度的二值描述子，比 ORB 更准一点"

ORB 用 FAST 角点+旋转 BRIEF，但它的尺度金字塔比较粗（默认 8 层），且短点对是随机选的。BRISK 做了三件事改进：

1. **AGAST 角点**（FAST 的通用化版本，比 FAST 快约 10%）；
2. **双类型点对**：长点对用于估计主方向，短点对（512 对）用于生成描述子，比 ORB 的随机点对分布更均匀；
3. **亚尺度精定位**：在尺度轴做二次拟合，关键点定位精度比 ORB 高。

速度上比 ORB 慢约 20%，但**匹配精度高约 5~10%**，尤其是在大尺度变化场景。

## 选型口诀

> **嵌入式/超低功耗用 ORB，需要比 ORB 稍稳一点用 BRISK，要稳健不要急就 AKAZE。**
''',
'tricks': '''
## 🎯 参数建议

- `thresh`（AGAST 阈值）：默认 30；低一点关键点多（适合匹配稀疏场景），高一点关键点少但质量高；
- `octaves`：默认 4；大尺度变化（无人机拍摄）设 6~8；
- `patternScale`：默认 1.0；图像分辨率高（>1080p）可设到 1.2~1.5 让采样更大范围。

**BRISK 描述子 512 bit**，匹配必须用 **HAMMING 距离**，BFMatcher 或 FlannBasedMatcher(LSH) 都可以。
'''
},
'connected-components': {
'concepts': '''
## 🧓 大白话：连通域分析 = "把黑白色块一个个标出来"

二值化之后图上有很多白色"块"，连通域分析就是给**每个互相连接的白色块一个编号**，顺便统计它的面积、外接矩形、重心、圆形度等属性。这是**所有机器视觉项目必用的基础工具**——数米粒、数硬币、OCR 字符切分、缺陷检测、细胞计数，第一个想到的都是它。

**"连通"的定义**：
- **4-连通**：只认上下左右相邻；
- **8-连通**：对角也算相连。**默认用 8-连通**，更符合直觉。

## 为什么不用 findContours？

| 方法 | 输出 | 适用 |
| --- | --- | --- |
| `findContours` | 轮廓点集 | 要形状、周长、精确边界时 |
| **`connectedComponentsWithStats`** | 标签图+面积+外接矩形+重心 | **要统计数量、筛选大小、画色块** |

两个方法常常配合：先用连通域做大小过滤（去掉太小/太大的噪声块），再对保留的块做 `findContours` 算形状。
''',
'tricks': '''
## 🎯 典型 5 行用法

```python
n, labels, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)
for i in range(1, n):  # 0 是背景
    x, y, w, h, area = stats[i]
    if area < 100 or area > 10000:
        continue  # 过滤太小太大
    cx, cy = centroids[i]
    cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
```

### 实战 5 条

1. **二值化要先做干净**：连通域对"粘连"非常敏感——两个米粒有一个像素桥连在一起就会被标成一个；必要时先做开运算；
2. **lType 用 CV_32S 而不是 CV_16U**：后者最大只能标 65535 个连通域，大图容易溢出；
3. **面积过滤是必做的后处理**：二值化后总有噪声小点点；
4. **重心比外接矩形中心更准**：外接矩形中心在矩形几何中点，重心（centroids）才是物体真实中心；
5. **圆形度 = 4π·area / perimeter²**：完美圆 = 1，越扁越小，用于区分"圆形缺陷"和"长条形划痕"。
'''
}
}

EXT.update(GENERIC)


def append_extension(algo, content_map):
    """对每个 algo 的每个 page，如文件里还没有 '## 🔍 扩展补充' 标记，则在末尾追加内容。"""
    marker = '<!-- AUTO-EXTENSION -->'
    for page, addition in content_map.items():
        path = os.path.join(BASE, algo, page + '.md')
        if not os.path.exists(path):
            print(f'  [skip] {algo}/{page} not found'); continue
        with open(path, 'r', encoding='utf-8') as f:
            original = f.read()
        if marker in original:
            print(f'  [skip] {algo}/{page} already extended'); continue
        # 在末尾追加（避免破坏 frontmatter，frontmatter 一定在文件最开头 --- 之间）
        new_content = original.rstrip() + '\n\n' + marker + '\n\n' + addition.strip() + '\n'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'  [ok]   {algo}/{page} appended')


if __name__ == '__main__':
    target = sys.argv[1:] if len(sys.argv)>1 else list(EXT.keys())
    for algo in target:
        if algo in EXT:
            print(f'== thickening {algo} ==')
            append_extension(algo, EXT[algo])
        else:
            print(f'== [skip] {algo} (no extension defined) ==')
    print('\nDone.')
