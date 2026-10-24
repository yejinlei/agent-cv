# DPM 源码走读

## ① OpenCV DPMDetector 调用（最简单）

OpenCV 3.x 在 `contrib` 里提供了 `cv2.dpm.DPMDetector`，OpenCV 4.x 起已从主分支移除。

```python
import cv2
import numpy as np

# ⚠️ 需要 opencv-contrib-python 且版本 3.x
# OpenCV 4.x 已移除 DPMDetector，需要用 3.x 或者自己编译 voc-release5

# 1) 加载模型
# OpenCV 自带少量预训练模型（如 INRIA Person），或者自己训练
detector = cv2.dpm.DPMDetector_create(
    ["inriaperson.xml"],  # 模型文件列表，可以多个 component
    ["person"]            # 对应类别名
)

# 2) 读图像
img = cv2.imread("pedestrians.jpg")

# 3) 检测
rects, scores, class_ids = detector.detect(img)
print(f"检测到 {len(rects)} 个目标")

# 4) 画框
for (x, y, w, h), s, cid in zip(rects, scores, class_ids):
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(img, f"{s:.2f}", (x, y-5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

cv2.imwrite("dpm_result.png", img)
```

::: warning OpenCV 版本提示
- OpenCV 3.x + `opencv-contrib-python`：`cv2.dpm.DPMDetector_create` 可用
- OpenCV 4.x：该模块被移除
- 想要在新版 OpenCV 用 DPM，推荐直接编译 [voc-release5](https://github.com/rbgirshick/voc-dpm)（原作者 C++/Matlab 版本）或用 [dpm-python](https://github.com/mitmul/dpm) 等第三方实现
:::

## ② 官方 voc-release5 检测命令（Matlab）

Felzenszwalb 官方实现是 Matlab + C/C++ MEX：

```matlab
% 加载预训练模型（voc-release5 自带）
load('VOC2007/inriaperson_final.mat');

% 读图像
im = imread('test.jpg');

% 检测
[ds, bs] = imgdetect(im, model, model.thresh);
% ds: N×5 (x1,y1,x2,y2,score)
% bs: 每个检测框对应的部件位置

% NMS
top = nms(ds, 0.3);
ds = ds(top, :);
bs = bs(top, :);

% 显示
showboxes(im, bs);
```

## ③ Python 端到端理解版：HOG + 滑动窗 + 简单"根+部件"（教学原理）

真实 DPM 代码量大（voc-release5 约 5000+ 行 C/Matlab），下面用极简代码演示核心打分思想（不含距离变换和 Latent SVM 训练，只做"根+2 部件"的直接打分）：

```python
import cv2
import numpy as np

def compute_hog(img):
    """计算 HOG 特征，返回 (H, W, 31) 的 cell 特征向量"""
    hog = cv2.HOGDescriptor((64,128), (16,16), (8,8), (8,8), 9)
    # 真实 DPM 用更细的 32 维带符号/无符号混合 HOG，这里简化
    h = hog.compute(img, winStride=(8,8), padding=(0,0))
    return h

def simple_dpm_detect(img, root_w, part_ws, part_anchors):
    """
    极简 DPM 检测（原理版）：
    root_w:  根模板 (RH, RW, D)
    part_ws: 部件模板列表 [(PH, PW, D)]
    part_anchors: 每个部件的理想锚点 (ay, ax) 相对根左上角的 cell 位置
    """
    # 1. 计算全图 HOG
    # 真实 DPM 会自己算金字塔和多层 HOG，这里简化成单层
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 为了原理演示，我们用固定步长滑窗
    h, w = gray.shape
    win_h, win_w = root_w.shape[0]*8+16, root_w.shape[1]*8+16  # cell=8px
    detections = []
    stride = 8  # 1 cell 步长
    for y in range(0, h - win_h, stride):
        for x in range(0, w - win_w, stride):
            patch = gray[y:y+win_h, x:x+win_w]
            feat = cv2.HOGDescriptor((win_w,win_h),(16,16),(8,8),(8,8),9).compute(patch).flatten()
            # 将 feat reshape 到 cell 网格
            # 这里为了简洁，用简化打分：只看根模板点积
            root_feat = feat[:root_w.size].reshape(root_w.shape)
            root_score = float((root_feat * root_w).sum())
            total = root_score
            # 部件打分（省略距离变换，直接在锚点处点积）
            for pw, (ay, ax) in zip(part_ws, part_anchors):
                # 锚点附近搜索 ±2 cell
                best = -1e9
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        py, px = ay+dy, ax+dx
                        # 形变代价：弹簧惩罚
                        cost = 0.1 * (dx*dx + dy*dy)
                        # 取部件区域特征
                        # （省略：实际是从整体 hog 中切片）
                        part_score = 0 - cost  # 简化
                        if part_score > best:
                            best = part_score
                total += best
            if total > 0.5:
                detections.append((x, y, win_w, win_h, total))
    return detections
```

> 真实 DPM 最关键的"距离变换 O(HW) 求最优部件位置"单独实现起来约 20~30 行一维 DP，有兴趣可以看 Felzenszwalb 2004 论文 *Distance Transforms of Sampled Functions*。

## ④ 距离变换 1 维实现（核心加速）

```python
import numpy as np

def dt_1d(f, a, b):
    """
    一维广义距离变换：
      g[x] = max_z [f[z] - a*(x-z)^2 - b*(x-z)]
    a > 0, 二次项系数
    抛物线包络算法，O(n)
    """
    n = len(f)
    d = np.zeros(n)         # 输出
    v = np.zeros(n, int)    # 每个抛物线段对应的 z
    z = np.zeros(n+1)       # 段间交点位置
    k = 0
    v[0] = 0
    z[0] = -np.inf
    z[1] = np.inf

    for q in range(1, n):
        # 抛物线 q 与 v[k] 的交点
        s = ((f[q] - a*q*q - b*q) - (f[v[k]] - a*v[k]*v[k] - b*v[k])) / (2*a*(v[k]-q))
        while k >= 0 and s <= z[k]:
            k -= 1
            s = ((f[q] - a*q*q - b*q) - (f[v[k]] - a*v[k]*v[k] - b*v[k])) / (2*a*(v[k]-q))
        k += 1
        v[k] = q
        z[k] = s
        z[k+1] = np.inf

    k = 0
    for q in range(n):
        while z[k+1] < q:
            k += 1
        d[q] = -a*(q - v[k])**2 - b*(q - v[k]) + f[v[k]]
    return d

def dt_2d(f, ax, bx, ay, by):
    """二维可分距离变换（x 和 y 独立二次项）"""
    H, W = f.shape
    g = np.zeros_like(f)
    # 先对每行做 1D
    for y in range(H):
        g[y, :] = dt_1d(f[y, :], ax, bx)
    # 再对每列做 1D
    for x in range(W):
        g[:, x] = dt_1d(g[:, x], ay, by)
    return g

# 测试
f = np.random.rand(20, 20)
g = dt_2d(f, 0.1, 0.0, 0.1, 0.0)
print("距离变换输出形状:", g.shape)
```

**时间复杂度**：20×20 的图只用 O(20+20) = 40 次运算（每行一次 O(n)，每列一次 O(n)），而不是暴力法的 O(20²·k²)。

## ⑤ 自己训练 DPM 模型（voc-release5 流程）

官方 Matlab 工具链：

```matlab
% 1) 准备数据
%    正样本: VOC2007/Annotations/*.xml + JPEGImages/*.jpg
%    负样本: VOC2007/JPEGImages 中不含该类别的图片

% 2) 配置模型
globals;
cls = 'person';
note = 'first run';

% 3) 训练
model = pascal_train(cls, note);
% 会自动跑：
%   - 初始化根（warp 正样本平均 HOG）
%   - 初始部件放置
%   - 多轮 latent SVM + 难负样本挖掘
%   - 混合模型聚类
%   - bounding box regression

% 4) 测试
boxes = imgdetect(im, model, -0.5);
```

**训练耗时**：一个类别（如 person）在 2010 年的服务器上需要 **1~2 天**，其中 90% 时间在难负样本挖掘（滑动窗口扫描所有负图）。

## ⑥ OpenCV 4.x 替代方案

由于 OpenCV 4.x 移除了 DPMDetector，新项目如果只想"试一下 DPM 的效果"，推荐两个选项：

**选项 A：用旧版 opencv-contrib**
```bash
pip install opencv-contrib-python==3.4.2.17
```

**选项 B：直接用深度学习检测**
```python
# OpenCV 4.5+ 内置 DNN 模块可以跑 YOLO/SSD，效果远超 DPM
net = cv2.dnn.readNetFromDarknet("yolov3.cfg", "yolov3.weights")
```

## OpenCV/官方源码核心文件

- **voc-release5**（Felzenszwalb 官方）：
  - `features/`：HOG+金字塔计算
  - `dt.cc`：距离变换实现（C 代码）
  - `model/`：模型结构（root + parts + deformation）
  - `train.m`、`learn.cc`：Latent SVM 训练
  - `detect.m`、`ffld/`：检测
- **OpenCV**（3.x contrib）：
  - `modules/dpm/src/dpm_cascade.cpp`：级联加速版 DPM（比原始 voc-release 快）
  - `modules/dpm/src/dpm_model.cpp`：模型加载
  - `modules/dpm/src/dpm_nms.cpp`：NMS
