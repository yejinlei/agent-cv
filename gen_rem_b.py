#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补齐算法批次 B：vibe / mosse / flann / essential-matrix / triangulation / bundle-adjustment / haar-wavelet"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_rem_tpl import build


# ================================================================
# 1. ViBe 背景建模
# ================================================================
m = {
    "name": "ViBe 背景建模", "en": "Visual Background Extractor", "year": "2011",
    "author": "Olivier Barnich / Marc Van Droogenbroeck",
    "paperUrl": "https://ieeexplore.ieee.org/document/5674058",
    "chapter": "第11章 · 运动分析", "chapterLink": "/chapters/ch11-motion",
    "branch": "图像处理", "level": "中级",
    "tagline": "用第一帧就给每个像素塞满样本，再随机更新——极简却极快的背景减除",
    "analogy": "ViBe 像一个「随手抓阄」的门卫：开门第一秒，他就记住每个位置附近 20 个邻居的颜色当「正常档案」。之后有人颜色对不上就报警。档案更新也随性——每次随机换掉一条旧记录。就这么简单，却能实时处理几十路监控。",
    "scene": "嵌入式/低功耗监控、多路视频实时检测、无人机图传前端、FPGA/SoC 视觉",
    "pros": ["极快（比 MOG2 快数倍）、内存省", "用第一帧即可初始化", "无参数或参数极少", "天然支持多路高清视频"],
    "cons": ["有「鬼影」（初始背景含运动物体时残留）", "对缓慢运动物体可能吸收为背景", "OpenCV 无内置（需自己实现或用第三方）", "对突然光照变化不鲁棒"],
    "dep_pre": "灰度化、降采样", "dep_peer": "MOG2、KNN、帧差法",
    "dep_post": "形态学、连通域、目标跟踪",
    "anchor": "记住「ViBe = 邻域样本集 + 随机更新 + 无参数」，快是它的命根子。",
    "params_arch": [
        ("N", "样本集大小", "20", "20", "**20**"),
        ("R", "颜色距离半径", "20", "20", "20~30"),
        ("minMatch", "判定背景的最少匹配数", "2", "2", "2"),
        ("φ", "随机更新概率倒数", "16", "16", "16"),
    ],
    "failmodes": [
        ("鬼影问题", "第一帧里有运动物体时，该物体被当成背景，之后离开留下「鬼影」。"),
        ("缓慢移动被吸收", "移动很慢的物体颜色会被样本集逐渐接纳，成为「背景」。"),
        ("无 OpenCV 现成接口", "OpenCV 未内置 ViBe，需自实现或用 opencv-contrib/第三方库。"),
        ("光照突变误检", "全局亮度突变后需要若干帧重新适应。"),
    ],
}
build("vibe", m,
      "给每个像素维护一个邻域样本集，新像素落在其中足够多样本的半径内即判为背景，样本集按随机策略更新。",
      "监控系统动辄几十路高清视频，MOG2/KNN 算不过来。ViBe 用最朴素的数据结构和随机更新策略，把背景减除压到**每像素几条比较**的代价，成为嵌入式监控的宠儿。",
      "一个园区有 64 路摄像头，后端服务器只有一台。用 MOG2 每路 30ms，跑不过来。换 ViBe，每路 3ms，64 路实时满帧，CPU 还剩一半。",
      ["搞懂 ViBe 为什么「快」——数据结构极简 + 随机更新", "理解样本集、匹配半径、匹配数三个要素", "知道鬼影是怎么来的、怎么去", "抄一段可跑的 ViBe 实现", "避开缓慢运动吸收、光照突变等坑", "会和 MOG2/KNN 明确分工"],
      {
          "title": "ViBe: A Universal Background Subtraction Algorithm for Video Sequences",
          "venue": "IEEE Transactions on Image Processing, 2011",
          "oneline": "用邻域样本集与随机更新策略实现极简、极快的通用背景减除。",
          "problem": "GMM 类方法需要为每个像素估计高斯参数，计算与内存开销大，难以在嵌入式设备上跑多路高清视频；且参数需按场景调，不够「通用」。",
          "idea": "每个像素不存分布，只存一个 20 个历史颜色的样本集。新像素与样本集比较，若足够多（≥2）在半径内则判背景。样本集更新用随机替换，更新概率恒定——无需任何参数估计。第一帧就用邻域像素填充样本集。",
          "idea_flow": "flowchart LR\n  A[\"首帧邻域填样本\"] --> B[\"新像素比样本集\"]\n  B --> C{\">=2个在半径内?\"}\n  C -- 是 --> D[\"背景+随机更新\"]\n  C -- 否 --> E[\"前景\"]",
          "contrib": "- 提出用**邻域样本集**代替概率分布做背景建模\n- 提出**随机更新**策略，无需参数、天然自适应\n- 实现极低的计算与内存开销，适合嵌入式与多路视频\n- 在多个公开数据集上与 GMM 相当或更好，速度却快数倍",
          "formula": "若样本集 S(x) 与当前值 v(x) 距离小于 R 的样本数 ≥ minMatch，则 x 为背景；每次更新以概率 1/φ 随机替换 S(x) 中一个样本。",
          "experiment": "在 ChangeDetection.net 等基准上，ViBe 的 F1 与 GMM 相当，处理 1080p 视频耗时仅为 GMM 的 1/3~1/5。",
          "limit": "初始帧含运动物体时产生鬼影；缓慢移动物体会被吸收为背景；对光照突变不鲁棒；OpenCV 无内置实现。",
          "influence": "成为嵌入式背景减除的事实标准之一，衍生出 ViBe+、PBAS、SubSENSE 等改进；「样本集 + 随机更新」思想被广泛借鉴。",
          "summary": "没有公式、没有参数估计，只靠一袋样本和随机替换，就成了最快的背景减除之一。",
      },
      [
          ("样本集", "每个像素存 20 个历史颜色值（从首帧的邻域随机抽取）。判断新像素时，看它离样本集里多少个样本足够近。", "flowchart LR\n  A[\"像素x\"] --> B[\"样本集20个值\"] --> C[\"比距离\"]"),
          ("匹配半径与匹配数", "半径 R 内算「匹配」。至少 2 个样本匹配才算背景——很宽松，所以抗噪。", None),
          ("随机更新", "每帧以固定小概率替换一个样本，还有更小概率更新邻居的样本。无需参数，背景自动缓慢漂移。", None),
          ("时空一致性与鬼影", "因为更新邻居样本，前景扩散会形成鬼影；解决办法是对可疑前景延迟判定或二次确认。", "flowchart TB\n  A[\"初始含运动物体\"] --> B[\"被记成背景\"] --> C[\"物体离开留下鬼影\"]"),
      ],
      [("首帧初始化", "用第一帧每个像素的 3×3 邻域像素随机填满它的样本集。"),
       ("逐像素比对", "新帧像素与样本集比距离，统计落在半径 R 内的样本数。"),
       ("判定与随机更新", "匹配数够则判背景并以 1/φ 概率替换样本，少数情况还更新邻居样本。"),
       ("后处理", "形态学去噪 + 连通域分析，得到干净的前景掩码。")],
      "时间复杂度 O(W·H·N)，但常数极小（N=20 的整数比较）；空间复杂度 O(W·H·N)。相比 MOG2 常数小得多。",
      '''import numpy as np
import cv2


class ViBe:
    """极简 ViBe 背景建模实现。"""

    def __init__(self, height, width, n=20, r=20, min_match=2, phi=16):
        self.n, self.r, self.min_match, self.phi = n, r, min_match, phi
        self.samples = np.zeros((n, height, width), np.uint8)
        self.height, self.width = height, width

    def init(self, frame):
        pad = np.pad(frame, 1, mode="edge")
        for k in range(self.n):
            dy, dx = np.random.randint(0, 3, 2) - 1
            self.samples[k] = pad[1 + dy:1 + dy + self.height, 1 + dx:1 + dx + self.width]
        return np.zeros(frame.shape, np.uint8)

    def apply(self, frame):
        diff = np.abs(self.samples.astype(np.int16) - frame.astype(np.int16))
        match = (diff < self.r).sum(axis=0)
        fg = (match < self.min_match).astype(np.uint8) * 255

        # 随机更新
        bg = fg == 0
        upd = bg & (np.random.rand(self.height, self.width) < 1.0 / self.phi)
        idx = np.random.randint(0, self.n, size=(self.height, self.width))
        for k in range(self.n):
            self.samples[k][upd & (idx == k)] = frame[upd & (idx == k)]
        return fg


cap = cv2.VideoCapture("video.mp4")
ok, frame0 = cap.read()
gray0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
vibe = ViBe(*gray0.shape)
vibe.init(gray0)''',
      '''# 若不想自己实现，也可用 MOG2 近似「随机更新」的轻量效果
import cv2

mog2 = cv2.createBackgroundSubtractorMOG2(
    history=100,          # 短历史 = 更新更快，接近 ViBe 的轻量感
    varThreshold=24,
    detectShadows=False,
)
cap = cv2.VideoCapture("video.mp4")
while cap.isOpened():
    ok, frame = cap.read()
    if not ok:
        break
    fg = mog2.apply(frame)
    cv2.imshow("fg", fg)
    if cv2.waitKey(30) == 27:
        break
cap.release()''',
      "OpenCV 未内置 ViBe；可用不等长的短历史 MOG2 近似其轻量特性，或用 opencv-contrib/第三方实现。",
      [("N", "样本集大小", "20"), ("R", "颜色距离半径", "20"), ("minMatch", "判定背景的最少匹配数", "2"), ("phi", "随机更新概率倒数", "16")],
      [
          ("鬼影甩不掉", "初始背景里有车/人，离开后留下鬼影。", "对持续存在的前景做「二次判定」，或运行若干帧后再作为初始背景。"),
          ("缓慢运动被吸收", "走得很慢的人被样本集接纳为背景。", "减小 φ 加快更新会加剧此问题；应增大样本集或降低更新率。"),
          ("以为 OpenCV 有 ViBe", "cv2 里找不到 createBackgroundSubtractorViBe。", "自实现（如上）或用 MOG2 近似，别浪费时间搜索。"),
          ("光照突变误检", "开灯/关灯瞬间满屏前景。", "检测前景占比异常时重置样本集。"),
      ],
      "ViBe 快在极简；首帧别含运动物体，否则出鬼影。",
      [("N", "样本集大小", "20", "更稳但更慢", "更快但易误检"),
       ("R", "匹配半径", "20", "更宽容、漏检增", "更敏感、噪声增"),
       ("phi", "更新概率倒数", "16", "更新更慢、更稳", "更新更快、易吸收前景")],
      [("多路视频", "ViBe 是少数能在单 CPU 核上跑多路 1080p 的背景减除算法。"),
       ("和形态学搭配", "ViBe 输出噪点略多，务必接一步开运算 + 连通域过滤。"),
       ("和 KNN 分工", "追求稳定用 KNN，追求速度与低内存用 ViBe。")],
      [("640×480 灰度", "≈1.5 ms/帧", "极快，常数小"),
       ("1920×1080 灰度", "≈8 ms/帧", "单核可跑多路"),
       ("对比 MOG2 1080p", "≈30 ms/帧", "ViBe 快约 4 倍")],
      )


# ================================================================
# 2. MOSSE 相关滤波跟踪
# ================================================================
m = {
    "name": "MOSSE 相关滤波跟踪", "en": "Minimum Output Sum of Squared Error Filter", "year": "2010",
    "author": "David S. Bolme / J. Ross Beveridge / Bruce A. Draper / Yui Man Lui",
    "paperUrl": "https://www.cs.colostate.edu/~draper/papers/bolme_cvpr10.pdf",
    "chapter": "第11章 · 运动分析", "chapterLink": "/chapters/ch11-motion",
    "branch": "目标检测", "level": "中级",
    "tagline": "用傅里叶变换把「找目标」变成「一次乘除」，600 FPS 的开山鼻祖",
    "analogy": "你在找一枚硬币，手里拿着一张「硬币模板」。MOSSE 说：别一格格挪着比，我把它变到频率世界，用一次乘除就知道哪里最像。于是每秒能扫 600 次。它是 KCF、CSRT 这一整族跟踪算法的祖师爷。",
    "scene": "高速单目标跟踪、无人机视觉跟随、体育转播自动追球、实时 AR 追踪",
    "pros": ["极快（600+ FPS）", "只需一个矩形框初始化", "对形变、光照有一定鲁棒性", "代码短、易实现"],
    "cons": ["不具备尺度自适应", "快速运动/遮挡易丢失", "精度不如 KCF/CSRT", "对旋转敏感"],
    "dep_pre": "灰度化 + 对数/归一化预处理（压光照）", "dep_peer": "KCF、CSRT、CamShift",
    "dep_post": "尺度估计模块、丢失重检测",
    "anchor": "记住「MOSSE = 相关滤波 + FFT 加速 + 最小输出误差」，速度最快、精度一般。",
    "params_arch": [
        ("lr", "学习率", "0.125", "0.125", "**0.02~0.2**"),
        ("sigma", "高斯响应 σ", "2.0", "2.0", "2.0"),
        ("psr_thresh", "峰值旁瓣比阈值", "—", "7.0", "7.0（判丢失）"),
        ("search_window", "搜索窗相对目标倍数", "1.5", "—", "1.5~2.0"),
    ],
    "failmodes": [
        ("目标出画/遮挡后不找回", "MOSSE 无重检测，一旦丢失就永久丢失。"),
        ("快速运动跟丢", "搜索窗太小，目标一下跳出窗口。"),
        ("尺度变化失败", "MOSSE 假设目标大小不变，变大变小就丢。"),
        ("初始化框不准", "初始框含大量背景，滤波器学到背景纹理。"),
    ],
}
build("mosse", m,
      "训练一个滤波器，使它与目标模板卷积后响应最大；再对这个响应图求峰值定位目标。",
      "跟踪是视频分析的基石。光流、CamShift 各有局限，2010 年 MOSSE 首次把**相关滤波 + 傅里叶加速**引入跟踪，一举把速度提到 600 FPS，开启了 KCF/CSRT 这条黄金谱系。",
      "无人机要自动跟拍一个人。机上 CPU 只有手机级别，深度学习跑不动。用 MOSSE，一个矩形框圈住人，之后每帧一次 FFT 乘除就锁住他，600 FPS 绰绰有余。",
      ["搞懂「相关滤波」为什么能定位目标", "理解 FFT 如何把卷积变成乘除", "知道 MOSSE 和 KCF 的传承关系", "抄一段可跑的 MOSSE 跟踪代码", "避开丢失不找回、尺度固定等坑", "会选 MOSSE / KCF / CSRT"],
      {
          "title": "Visual Object Tracking using Adaptive Correlation Filters",
          "venue": "CVPR 2010",
          "oneline": "用最小化输出平方误差训练相关滤波器，配合 FFT 实现超高速目标跟踪。",
          "problem": "2010 年前的主流跟踪器（如光流、粒子滤波、mean-shift）要么慢、要么对光照形变敏感，难以做到实时高帧率。",
          "idea": "把「定位目标」看成「找一个滤波器，使它对目标图像的响应最大」。训练时用目标区域的多个变形样本，令期望响应是以目标为中心的二维高斯。借助傅里叶变换，卷积变成逐点乘除，训练与推理都极快。",
          "idea_flow": "flowchart LR\n  A[\"目标区域样本\"] --> B[\"期望高斯响应\"]\n  B --> C[\"FFT域解最小二乘\"]\n  C --> D[\"滤波器H\"]\n  D --> E[\"新帧相关->峰值定位\"]",
          "contrib": "- 提出**最小输出平方误差**准则在线训练相关滤波器\n- 首次将**FFT 加速的相关滤波**用于跟踪，达 600+ FPS\n- 引入 PSR（峰值旁瓣比）判断跟踪是否丢失\n- 开创相关滤波跟踪这一谱系",
          "formula": "滤波器 H* = Σ G_i ⊙ F_i* / ( Σ F_i ⊙ F_i* + ε )，其中 F 为输入样本的 FFT、G 为期望响应的 FFT，⊙ 为逐元素乘。下帧响应 y = IFFT( H ⊙ F )。",
          "experiment": "在 OTB 等基准上，MOSSE 以远超同期的速度取得当时领先的精度，成为相关滤波跟踪的开山之作。",
          "limit": "无尺度自适应；无丢失恢复机制；搜索窗固定，快速运动易丢；对旋转敏感。",
          "influence": "直接催生 CSK、KCF、CN、SRDCF、CSRT 等整条相关滤波跟踪谱系，成为传统跟踪领域影响最深的一篇论文之一。",
          "summary": "把跟踪变成一次 FFT 乘除，从此实时跟踪有了「又快又稳」的可能。",
      },
      [
          ("相关运算与响应峰值", "把模板在图上滑动做相关，哪里响应最大，哪里就是目标。响应图是一张「相似度地形图」。", "flowchart LR\n  A[\"模板\"] --> B[\"与搜索区相关\"] --> C[\"响应图\"] --> D[\"峰值=目标位置\"]"),
          ("为什么用 FFT", "相关/卷积在空域是滑窗，在频域是逐点乘。「变换—相乘—反变换」比滑窗快几个数量级。", None),
          ("期望响应是高斯的", "训练时我们希望输出是一张中心为亮斑的高斯图——亮斑中心即目标。滤波器据此求解。", None),
          ("在线自适应与学习率", "每帧用新结果微调滤波器，学习率决定「更新多快」，太快会漂移、太慢跟不上变化。", None),
      ],
      [("初始化", "在第一帧框选目标，取目标区域及其变形样本，FFT 域解出初始滤波器。"),
       ("逐帧定位", "新帧在搜索窗内做 FFT 相关，响应图峰值位置即目标新位置。"),
       ("在线更新", "用当前帧结果按学习率更新滤波器分子分母，实现自适应。"),
       ("丢失检测", "用峰值旁瓣比 PSR 判断响应是否可信，低于阈值则判为丢失。")],
      "时间复杂度 O(W·H·log(WH))，主要来自两次 FFT；空间复杂度 O(W·H)。实际可跑数百 FPS。",
      '''import cv2

# OpenCV 提供 MOSSE（旧版 API：cv2.legacy）
tracker = cv2.legacy.TrackerMOSSE_create()
cap = cv2.VideoCapture("video.mp4")
ok, frame = cap.read()
bbox = cv2.selectROI("select", frame, False)   # 手动框选目标
tracker.init(frame, bbox)

while True:
    ok, frame = cap.read()
    if not ok:
        break
    ok, box = tracker.update(frame)
    if ok:
        x, y, w, h = [int(v) for v in box]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    else:
        cv2.putText(frame, "LOST", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("MOSSE", frame)
    if cv2.waitKey(1) == 27:
        break
cap.release()''',
      '''import numpy as np
import cv2

# 手写 MOSSE 核心：FFT 域训练 + 相关定位（高度简化）
H, W = 32, 32
sigma, lr, eps = 2.0, 0.125, 1e-5

# 期望响应：中心亮的高斯
ys, xs = np.mgrid[0:H, 0:W]
ys, xs = ys - H // 2, xs - W // 2
G = np.exp(-(xs ** 2 + ys ** 2) / (2 * sigma ** 2)).astype(np.float32)
Gf = np.fft.fft2(G)
Hf = np.zeros((H, W), np.complex64)
Gf_sum, Ff_sum = np.zeros((H, W), np.complex64), np.zeros((H, W), np.complex64)

# 用若干含小形变的样本训练（此处示意用同一块加噪）
patch = cv2.imread("target.png", 0).astype(np.float32) / 255.0
for _ in range(8):
    Ff = np.fft.fft2(patch + 0.01 * np.random.randn(H, W))
    Gf_sum += Gf * np.conj(Ff)
    Ff_sum += np.conj(Ff) * Ff
Hf = Gf_sum / (Ff_sum + eps)

# 推理：新帧相关并找峰值
frame_patch = patch + 0.02 * np.random.randn(H, W)
resp = np.real(np.fft.ifft2(Hf * np.fft.fft2(frame_patch)))
dy, dx = np.unravel_index(np.argmax(resp), resp.shape)
print("峰值偏移:", (dx - W // 2, dy - H // 2))''',
      "OpenCV 4.x 的 MOSSE 在 legacy 命名空间：cv2.legacy.TrackerMOSSE_create()；需安装 opencv-contrib-python。",
      [("learning_rate", "在线更新学习率", "0.125"), ("sigma", "期望高斯响应 σ", "2.0"), ("psr_threshold", "PSR 丢失阈值", "7.0"), ("search_window", "搜索窗倍数", "1.5")],
      [
          ("跟踪丢失不找回", "MOSSE 无重检测，目标一旦出窗就永久丢失。", "接一个 SIFT/模板匹配的全局重检测做找回。"),
          ("搜索窗太小", "目标快速运动一下跳出搜索窗。", "把搜索窗放到目标尺寸的 1.5~2 倍。"),
          ("学习率过高", "滤波器更新太激进，跟到背景上就漂移。", "学习率降到 0.02~0.05，或按响应质量自适应。"),
          ("用错 API 命名空间", "cv2.TrackerMOSSE_create 在 4.x 报错。", "改用 cv2.legacy.TrackerMOSSE_create()。"),
      ],
      "MOSSE 快但脆；窗要够大、学习率要小、丢了要重检。",
      [("learning_rate", "学习率", "0.125", "跟得紧但易漂", "更稳但慢适应"),
       ("sigma", "响应 σ", "2.0", "响应更集中", "响应更平坦"),
       ("psr_threshold", "丢失阈值", "7.0", "更易判丢失", "更宽容")],
      [("适合场景", "目标大小基本不变、光照平稳、追求高帧率的场合。"),
       ("不适合场景", "目标剧烈尺度变化、长时间遮挡、需要极高精度的场合——换 CSRT。"),
       ("选型梯度", "速度优先 MOSSE > KCF > CSRT；精度优先 CSRT > KCF > MOSSE。")],
      [("320×240 目标窗", "≈600 FPS", "论文报道，纯 CPU"),
       ("OpenCV TrackerMOSSE", "≈100 FPS", "含全流程开销"),
       ("对比 KCF", "≈60 FPS", "KCF 慢些但更稳")],
      )


# ================================================================
# 3. FLANN 快速最近邻
# ================================================================
m = {
    "name": "FLANN 快速最近邻搜索", "en": "Fast Library for Approximate Nearest Neighbors", "year": "2009",
    "author": "Marius Muja / David G. Lowe",
    "paperUrl": "https://ieeexplore.ieee.org/document/5159256",
    "chapter": "第13章 · 广义匹配", "chapterLink": "/chapters/ch13-matching",
    "branch": "特征匹配", "level": "中级",
    "tagline": "不追求百分百准确的最近邻，用「近似」换来几十倍的匹配提速",
    "analogy": "你在图书馆找一本最接近某主题的书。暴力法是走遍每一排书架；FLANN 是先用「分区索引」直接跳到可能的那几排，找到「差不多最好」的就走。偶尔不是最优，但快得多——匹配几千个特征点的时候，这点误差根本不重要。",
    "scene": "大规模特征匹配（SLAM、全景拼接、图像检索）、SIFT/SURF 描述子匹配、点云配准",
    "pros": ["比暴力匹配快几十倍", "支持 KD-Tree 与 LSH 多种索引", "自动选参（IndexParams）", "在特征点多时优势巨大"],
    "cons": ["近似结果，可能漏掉真正最近邻", "参数（trees/checks）需要调", "特征点少时反而不如暴力匹配", "高维数据下 KD-Tree 退化为线性"],
    "dep_pre": "特征检测 + 描述子（SIFT/SURF/ORB）", "dep_peer": "BFMatcher 暴力匹配",
    "dep_post": "比率测试、RANSAC 几何验证、单应估计",
    "anchor": "记住「浮点描述子用 KD-Tree（trees/checks），二进制描述子用 LSH」。",
    "params_arch": [
        ("algorithm", "索引算法", "KD-Tree", "FLANN_DIST_L2", "SIFT→KDTree；ORB→LSH"),
        ("trees", "KD-Tree 数量", "4", "4", "**4~8**"),
        ("checks", "搜索节点上限", "32", "32", "**50~100**"),
        ("table_number", "LSH 哈希表数", "—", "12", "12"),
    ],
    "failmodes": [
        ("用 FLANN 匹配 ORB 却没建 LSH", "对二进制描述子用 KD-Tree，结果一团糟。"),
        ("checks 太小", "近似太激进，匹配数骤减。"),
        ("特征点很少时用它", "几百个点以下，暴力匹配更快且更准。"),
        ("不做比率测试", "Lowe 比率测试缺失，误匹配大量涌入。"),
    ],
}
build("flann", m,
      "用 KD-Tree / LSH 等索引结构，在特征空间里快速找到「近似最近邻」，替掉逐点暴力比较。",
      "一张图有 5000 个 SIFT 特征点，两张图暴力匹配要算 2500 万次距离。FLANN 用**空间索引**把搜索范围缩小，几十毫秒搞定——这是 SLAM、全景拼接等大规模匹配的必修课。",
      "你在做一个全景拼接 App。两张 1200 万像素照片各有上万特征点，暴力匹配要好几秒。换成 FLANN，先建 KD-Tree 索引再搜，200 毫秒出结果，用户几乎无感。",
      ["搞懂「近似最近邻」为什么能快几十倍", "分清 KD-Tree 与 LSH 各适用什么描述子", "掌握 trees / checks 的调法", "抄一段 FLANN + 比率测试的完整匹配代码", "避开二进制描述子配 KD 树的坑", "会判断何时该退回暴力匹配"],
      {
          "title": "Fast Approximate Nearest Neighbors with Automatic Algorithm Configuration",
          "venue": "VISAPP 2009",
          "oneline": "提出可自动配置的近似最近邻库，用 KD-Tree/LSH 索引在大规模数据上实现数十倍加速。",
          "problem": "精确最近邻搜索在高维下极其昂贵（维度灾难），暴力比较在特征点上万时成为瓶颈，且不同数据类型需要不同索引结构，用户难以选型。",
          "idea": "放弃「精确」，接受「近似」：用 KD-Tree 或 LSH 索引只搜索最可能的分支，找到一个足够近的邻居即返回。并让库根据数据自动挑选合适的索引与参数，降低使用门槛。",
          "idea_flow": "flowchart LR\n  A[\"特征向量集\"] --> B[\"建索引 KD-Tree/LSH\"]\n  B --> C[\"查询近似最近邻\"]\n  C --> D[\"匹配结果\"]",
          "contrib": "- 提出**自动算法配置**：按数据规模与类型自动选索引\n- 集成 KD-Tree（浮点）与 LSH（二进制）两大索引\n- 在 OpenCV 中成为 SIFT/SURF 匹配的默认推荐匹配器\n- 大幅降低了大规模匹配的使用门槛",
          "formula": "KD-Tree 以方差最大维度切分空间递归建树；查询时按分支优先搜索，checks 限定最多检查节点数，在「搜索质量」与「速度」间权衡。",
          "experiment": "在百万级 SIFT 描述子上，FLANN 相比暴力匹配提速数十倍，召回率仍保持 90% 以上。",
          "limit": "结果是近似的，可能漏掉真最近邻；高维下 KD-Tree 效率退化；参数需针对数据调；小规模数据无优势。",
          "influence": "成为 OpenCV 中大规模特征匹配的标准工具，被 SLAM（ORB-SLAM 等）、图像检索、点云配准广泛采用；「近似换速度」的思路影响了后续所有向量检索库（如 Faiss、HNSW）。",
          "summary": "用一点精度，换来几十倍速度——这是大规模匹配能跑起来的关键。",
      },
      [
          ("什么是最近邻搜索", "给定一个查询特征，在库里找与它最相似的那个。匹配两张图就是让彼此的特征互为最近邻。", None),
          ("暴力匹配 vs 索引", "暴力匹配逐个算距离 O(N²)；索引法只查最可能的分支，把 N² 降到接近 N·log N。", "flowchart LR\n  A[\"BF: 逐点比\"] --> B[\"O(N^2)\"]\n  C[\"FLANN: 索引\"] --> D[\"≈O(N logN)\"]"),
          ("KD-Tree 与 LSH", "浮点描述子（SIFT/SURF）用 KD-Tree 按维度切分空间；二进制描述子（ORB/BRIEF）用 LSH 做哈希分桶。", None),
          ("近似换速度", "checks 参数控制搜索多少个节点。设小则快但漏，设大则准但慢——典型的时间换精度旋钮。", None),
      ],
      [("准备描述子", "先用 SIFT/SURF/ORB 提取两组特征点与描述子。"),
       ("配置索引参数", "浮点描述子配 KD-Tree（trees/checks），二进制描述子配 LSH。"),
       ("执行 knnMatch", "对每个查询点找 k=2 个最近邻，供比率测试使用。"),
       ("比率测试 + RANSAC", "用 Lowe 比率筛掉模糊匹配，再用 RANSAC 剔除几何不一致的外点。")],
      "时间复杂度约 O(N·log N)（建索引 + 查询），低于暴力匹配的 O(N²)；空间复杂度即索引大小 O(N)。",
      '''import cv2
import numpy as np

img1 = cv2.imread("a.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("b.jpg", cv2.IMREAD_GRAYSCALE)

sift = cv2.SIFT_create()
kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

# SIFT 是浮点描述子 -> KD-Tree 索引
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)         # 越大越准越慢

flann = cv2.FlannBasedMatcher(index_params, search_params)
knn = flann.knnMatch(des1, des2, k=2)

# Lowe 比率测试
good = []
for m, n in knn:
    if m.distance < 0.75 * n.distance:
        good.append(m)
print("原始匹配:", len(knn), "-> 优质匹配:", len(good))

# 用 RANSAC 进一步剔除几何外点
if len(good) >= 4:
    src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    print("内点数:", int(mask.sum()))''',
      '''import cv2
import numpy as np

# ORB 是二进制描述子 -> 必须用 LSH 索引
img1 = cv2.imread("a.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("b.jpg", cv2.IMREAD_GRAYSCALE)

orb = cv2.ORB_create(2000)
kp1, des1 = orb.detectAndCompute(img1, None)
kp2, des2 = orb.detectAndCompute(img2, None)

FLANN_INDEX_LSH = 6
index_params = dict(
    algorithm=FLANN_INDEX_LSH,
    table_number=12,
    key_size=20,
    multi_probe_level=2,
)
search_params = dict(checks=50)

flann = cv2.FlannBasedMatcher(index_params, search_params)
knn = flann.knnMatch(des1, des2, k=2)
good = [m for m, n in knn if m.distance < 0.8 * n.distance]
print("ORB + LSH 优质匹配:", len(good))''',
      "浮点描述子（SIFT/SURF）用 FLANN_INDEX_KDTREE；二进制描述子（ORB/BRIEF/BRISK）必须用 FLANN_INDEX_LSH，否则匹配质量极差。",
      [("trees", "KD-Tree 数量", "5"), ("checks", "搜索节点上限", "50"), ("table_number", "LSH 哈希表数", "12"), ("k", "knnMatch 的 k", "2（做比率测试）")],
      [
          ("ORB 用 KD-Tree", "二进制描述子用欧氏距离建 KD 树，语义完全不对，匹配稀烂。", "二进制描述子一律用 FLANN_INDEX_LSH + NORM_HAMMING。"),
          ("checks 设太小", "比如设成 2，近似过猛，好匹配也被漏掉。", "从 50 起步，按匹配数调整，通常 50~100。"),
          ("忘记比率测试", "没有 Lowe 比率，误匹配会淹没正确匹配。", "knnMatch(k=2) 后按 0.75~0.8 比率过滤。"),
          ("特征点很少也用 FLANN", "几百个点时索引开销大于收益。", "点数少时改回 BFMatcher，更准也够快。"),
      ],
      "浮点用 KD 树、二进制用 LSH；checks 从 50 起；最后必做比率测试。",
      [("trees", "KD-Tree 数量", "5", "更准但更慢", "更快但更漏"),
       ("checks", "搜索节点数", "50", "更准更慢", "更快更漏"),
       ("ratio", "比率阈值", "0.75", "更严、匹配更少更准", "更宽、匹配更多更糙")],
      [("和 RANSAC 必配", "FLANN 只负责「像」，几何一致性交给 findHomography + RANSAC。"),
       ("大规模检索", "特征库上万张图时，FLANN 建一次索引用多次，或换更快的 Faiss/HNSW。"),
       ("点云配准", "ICP 的对应点搜索也常用 KD-Tree 加速，原理与此相同。")],
      [("1000×1000 SIFT 匹配", "≈25 ms", "FLANN，checks=50"),
       ("暴力匹配同规模", "≈900 ms", "BFMatcher 对照"),
       ("5000×5000 匹配", "≈300 ms", "规模越大 FLANN 优势越明显")],
      )


# ================================================================
# 4. 本质矩阵估计
# ================================================================
m = {
    "name": "本质矩阵估计", "en": "Essential Matrix Estimation", "year": "1981",
    "author": "H. Christopher Longuet-Higgins",
    "paperUrl": "https://www.sciencedirect.com/science/article/abs/pii/0025556481900255",
    "chapter": "第9章 · 立体视觉", "chapterLink": "/chapters/ch09-stereo",
    "branch": "几何视觉", "level": "高级",
    "tagline": "从两张照片的对应点，直接解出相机「转了多大、往哪挪了」",
    "analogy": "你和朋友站在两个位置各拍一张同一间屋子。相同家具在两图中的位置差，其实编码了你们俩「相距多远、朝向差多少」。本质矩阵就是破译这组位置差的密码本——解出它，就知道了相机之间的运动。",
    "scene": "SfM 运动恢复结构、视觉里程计、SLAM 初始化、相机外参标定",
    "pros": ["无需知道场景 3D 结构即可解相机运动", "只用 5 对以上点即可求解", "配合 RANSAC 极稳健", "是 SfM/VO 的基石"],
    "cons": ["需要内参已知（先用 K 归一化）", "纯旋转/平面场景退化", "解出的位姿有 4 种组合需筛选", "噪声与误匹配敏感"],
    "dep_pre": "特征匹配 + 内参矩阵 K", "dep_peer": "基础矩阵 F、单应矩阵 H",
    "dep_post": "三角化、PnP、光束法平差",
    "anchor": "记住「E = [t]×R，秩 2，两个相等奇异值」——它是归一化坐标下的对极约束。",
    "params_arch": [
        ("method", "求解方法", "8点法", "RANSAC", "**RANSAC（阈值 1.0）**"),
        ("threshold", "内点阈值（像素）", "—", "1.0", "0.5~2.0"),
        ("confidence", "置信度", "—", "0.99", "0.99"),
        ("K", "内参矩阵", "必须先标定", "—", "**务必准确**"),
    ],
    "failmodes": [
        ("未用内参归一化", "直接用像素坐标算，得到的是基础矩阵 F 而非本质矩阵 E。"),
        ("纯旋转导致退化", "相机只旋转不平移时 E 不可解，应改用单应矩阵。"),
        ("平面场景退化", "所有点在同一个平面上时，E 的求解不稳定。"),
        ("解出的位姿有 4 种", "E 分解出 4 组 (R,t)，必须用三角化选唯一正确的。"),
    ],
}
build("essential-matrix", m,
      "用两视图的匹配点对，解出满足对极约束 x₂ᵀ E x₁ = 0 的本质矩阵，再分解出相机相对旋转与平移方向。",
      "要从照片重建 3D，第一步永远是「相机在哪、朝哪」。本质矩阵把**两幅图的对应关系**直接翻译成**相机之间的运动**，是一切 SfM、视觉里程计、SLAM 的起点。",
      "你用手机绕着一栋建筑走一圈拍了几十张照片，想重建出 3D 模型。软件首先要估计每两张照片之间相机移动了多少——靠的就是本质矩阵，再一路串成整条轨迹。",
      ["搞懂对极约束 x₂ᵀEx₁=0 的几何含义", "分清本质矩阵 E 与基础矩阵 F 的区别", "理解 E=[t]×R 的分解与 4 选 1", "抄一段 RANSAC 求解 + 位姿恢复的代码", "避开纯旋转、平面场景等退化", "知道它在 SfM 流程中的位置"],
      {
          "title": "A Computer Algorithm for Reconstructing a Scene from Two Projections",
          "venue": "Nature, 1981",
          "oneline": "提出用 8 对以上对应点线性求解本质矩阵，从两视图恢复相机运动与场景结构。",
          "problem": "在此之前，从两张照片恢复 3D 需要已知相机位姿；如何只凭图像对应点直接解出相机运动，是计算机视觉尚未攻克的核心难题。",
          "idea": "两幅图的对应点受「对极约束」限制：存在一个 3×3 矩阵 E，使得 x₂ᵀ E x₁ = 0 对所有对应点成立。把 E 的 9 个元素当未知数，每对点给一个方程，8 对即可线性求解。矩阵 E 随后可分解为旋转与平移。",
          "idea_flow": "flowchart LR\n  A[\"匹配点对\"] --> B[\"对极约束方程\"]\n  B --> C[\"解出本质矩阵E\"]\n  C --> D[\"SVD分解\"]\n  D --> E[\"R与t(4选1)\"]",
          "contrib": "- 提出 8 点法线性求解本质矩阵\n- 揭示 E = [t]× R 的结构：秩 2、两个相等奇异值\n- 证明可从 E 直接分解出相机相对位姿\n- 奠定对极几何与两视图重建的理论基础",
          "formula": "对极约束：x₂ᵀ E x₁ = 0，其中 x 为归一化相机坐标。结构：E = [t]× R，[t]× 为 t 的反对称矩阵。SVD 分解 E = U diag(1,1,0) Vᵀ，则 R = U W Vᵀ 或 U Wᵀ Vᵀ，t = ±U 的第三列。",
          "experiment": "合成与实拍数据上，8 点法在无噪声下精确，含噪声时配合归一化（Hartley）与 RANSAC 方能稳健。",
          "limit": "纯旋转或平面场景退化；对噪声与误匹配敏感；需内参已知；分解出的 4 组位姿需额外筛选。",
          "influence": "成为 SfM、视觉里程计、SLAM 的基石；后续 Hartley 归一化 8 点法、Nistér 5 点法、RANSAC 求解框架都在此基础上发展。",
          "summary": "一个约束方程 x₂ᵀEx₁=0，把「看清相机怎么动」变成了可解的方程组。",
      },
      [
          ("对极几何", "空间一点 P 与两个相机光心，确定一个平面（对极平面）。P 在第二幅图的投影必然落在一条线上（极线），这条线由 E 决定。", "flowchart LR\n  A[\"空间点P\"] --> B[\"两光心\"] --> C[\"对极平面\"] --> D[\"极线约束\"]"),
          ("E 与 F 的区别", "E 作用于归一化相机坐标（内参已知），F 作用于像素坐标（内参未知）。F = K₂⁻ᵀ E K₁⁻¹。", None),
          ("E 的结构", "E = [t]× R，表明它同时编码了旋转 R 与平移方向 t；它秩为 2，两个非零奇异值相等——这是可分解的前提。", None),
          ("分解与 4 选 1", "SVD 分解得到 4 组 (R,t)，其中只有一组能让所有点在两个相机前方。用三角化验证深度为正即可筛选。", "flowchart TB\n  A[\"SVD分解E\"] --> B[\"4组(R,t)\"] --> C[\"三角化\"] --> D[\"深度>0 的唯一解\"]"),
      ],
      [("匹配与归一化", "先做特征匹配，再用内参矩阵 K 把像素坐标归一化到相机坐标。"),
       ("8 点法 + RANSAC", "用 RANSAC 反复采样 8 对点求 E，取内点最多的解。"),
       ("强制秩 2 约束", "对解出的 E 做 SVD，把奇异值强制为 (1,1,0)，恢复合法结构。"),
       ("分解位姿", "SVD 分解得到 4 组 (R,t)，三角化验证选唯一正确的一组。")],
      "时间复杂度 O(n) 用于构建方程 + O(RANSAC 迭代 × 8 点求解)；空间复杂度 O(n)。",
      '''import cv2
import numpy as np

img1 = cv2.imread("a.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("b.jpg", cv2.IMREAD_GRAYSCALE)
K = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], np.float32)

sift = cv2.SIFT_create()
kp1, d1 = sift.detectAndCompute(img1, None)
kp2, d2 = sift.detectAndCompute(img2, None)

flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
knn = flann.knnMatch(d1, d2, k=2)
good = [m for m, n in knn if m.distance < 0.75 * n.distance]

pts1 = np.float32([kp1[m.queryIdx].pt for m in good])
pts2 = np.float32([kp2[m.trainIdx].pt for m in good])

# 用 RANSAC 求本质矩阵
E, mask = cv2.findEssentialMat(pts1, pts2, K, method=cv2.RANSAC,
                               prob=0.999, threshold=1.0)
# 从 E 恢复旋转与平移（会内部筛选出唯一解）
_, R, t, mask_pose = cv2.recoverPose(E, pts1, pts2, K, mask=mask)
print("旋转 R:\\n", R)
print("平移方向 t:", t.ravel())''',
      '''import numpy as np

# 手写 8 点法（线性求解，未做 RANSAC / 归一化，仅示意）
def eight_point(pts1, pts2):
    """pts1, pts2: (N,2) 归一化相机坐标。返回 E。"""
    A = []
    for (x1, y1), (x2, y2) in zip(pts1, pts2):
        A.append([x2 * x1, x2 * y1, x2,
                  y2 * x1, y2 * y1, y2,
                  x1, y1, 1])
    A = np.array(A)
    _, _, Vt = np.linalg.svd(A)
    E = Vt[-1].reshape(3, 3)

    # 强制秩 2 约束：奇异值置为 (1,1,0)
    U, S, Vt2 = np.linalg.svd(E)
    S = np.array([1.0, 1.0, 0.0])
    return U @ np.diag(S) @ Vt2


pts1 = np.random.rand(20, 2)
pts2 = pts1 + 0.01 * np.random.randn(20, 2)
E = eight_point(pts1, pts2)
print("E 的奇异值:", np.linalg.svd(E)[1])   # 应为 (1,1,~0)''',
      "务必先用内参 K 归一化坐标，否则求出的实为基础矩阵 F；务必用 RANSAC 版本，纯 8 点法对误匹配极敏感。",
      [("threshold", "RANSAC 内点阈值", "1.0 像素"), ("prob", "置信度", "0.999"), ("K", "相机内参矩阵", "必须先标定"), ("method", "求解器", "cv2.RANSAC")],
      [
          ("不归一化坐标", "直接拿像素坐标求解，得到 F，误以为是 E，位姿全错。", "先用 K⁻¹ 把点转到归一化相机坐标，或直接调 findEssentialMat 传 K。"),
          ("纯旋转场景", "相机只转不平移，对极约束退化，E 不可解。", "检测到退化时改用单应矩阵 findHomography 估计旋转。"),
          ("平面场景", "所有对应点共面时求解不稳定。", "平面场景优先用单应矩阵；若必须用 E，需保证有离面点。"),
          ("忘记 4 选 1", "只分解不筛选，可能选到深度为负的错误位姿。", "务必用 recoverPose 或三角化验证，取深度全正的那组。"),
      ],
      "先归一化、再 RANSAC、最后 4 选 1；纯旋转就换单应。",
      [("threshold", "内点阈值", "1.0 px", "更宽容、内点多", "更严、内点少"),
       ("prob", "置信度", "0.999", "迭代更多更稳", "可能提前终止"),
       ("method", "求解方式", "RANSAC", "—", "—")],
      [("和单应矩阵分工", "场景以平面为主（墙面、棋盘）用单应；有丰富 3D 结构才用本质矩阵。"),
       ("作为 SfM 第一步", "E 分解得到初始两视图位姿，再用三角化建初始点云，然后光束法平差优化。"),
       ("配合内参标定", "K 的精度直接决定 E 的质量，务必先做好相机标定。")],
      [("500 对应点，RANSAC", "≈8 ms", "findEssentialMat"),
       ("5000 对应点", "≈60 ms", "点数增加线性"),
       ("手写 8 点法（无RANSAC）", "≈1 ms", "但无抗噪能力")],
      )


# ================================================================
# 5. 三角化
# ================================================================
m = {
    "name": "三角测量（三角化）", "en": "Triangulation", "year": "1987",
    "author": "Richard Hartley / Peter Sturm（多视图三角化）",
    "paperUrl": "https://users.cecs.anu.edu.au/~hartley/Papers/triangulation/triangulation.pdf",
    "chapter": "第10章 · 三维景物恢复", "chapterLink": "/chapters/ch10-3d-recovery",
    "branch": "几何视觉", "level": "高级",
    "tagline": "两条「视线」在空间里交于一点——那个交点就是场景点的 3D 位置",
    "analogy": "你和朋友站在两个位置，各自用手指指向同一只鸟。两条视线在空间里理论上交于鸟的位置。三角测量就是：已知你们俩的位置和各自的指向，算出鸟到底在哪。",
    "scene": "SfM 建点云、双目立体恢复深度、SLAM 地图点生成、AR 锚点定位",
    "pros": ["几何直观、数学简单", "从 2D 对应直接得 3D 坐标", "是 SfM/立体视觉的核心步骤", "可与 RANSAC/重投影误差配合"],
    "cons": ["对噪声与基线长度敏感", "小基线（近纯旋转）时深度极不稳", "需准确的相机位姿", "近简并配置下误差爆炸"],
    "dep_pre": "相机位姿（R,t）+ 内参 K + 匹配点", "dep_peer": "PnP、本质矩阵估计",
    "dep_post": "光束法平差、深度图融合、点云滤波",
    "anchor": "记住「基线越长、深度越准；基线≈0 时三角化彻底失效」。",
    "params_arch": [
        ("method", "三角化方法", "DLT", "—", "**DLT 或 midpoint**"),
        ("normalize", "是否坐标归一化", "是", "—", "是（提升数值稳定）"),
        ("reproj_thresh", "重投影误差阈值", "—", "—", "1~3 像素"),
        ("min_depth", "最小深度过滤", "—", "—", "剔除近简并的远点"),
    ],
    "failmodes": [
        ("小基线导致深度发散", "两相机几乎重合时，微小像素误差被放大成巨大深度误差。"),
        ("误匹配产生离群点", "错误对应点三角化出飞到很远处的坏点。"),
        ("未做坐标归一化", "DTL 解法数值不稳定，结果抖动。"),
        ("忽略重投影误差", "不剔除误差大的点，点云里全是飞点。"),
    ],
}
build("triangulation", m,
      "给定两个相机的投影矩阵和一对匹配像素点，求一个 3D 点，使它在两图中的投影最接近给定像素。",
      "从 2D 图像恢复 3D 结构，最终必须落到「这个像素对应空间哪个点」。三角化就是这个临门一脚——SfM 的点云、双目深度、SLAM 的地图点，全部由它生成。",
      "你戴 VR 头显，设备要实时算出你眼前那杯咖啡在空间中的位置，才能把虚拟贴纸贴上去。头显里两个摄像头各看到咖啡上的一个特征点，三角化立刻给出它的 3D 坐标。",
      ["搞懂「两条视线求交点」为什么等价于解方程", "理解基线长度对深度精度的影响", "知道 DLT 与中点法两种解法的区别", "抄一段 DLT 三角化的可跑代码", "避开小基线、误匹配等致命坑", "明白它在 SfM 流程中的位置"],
      {
          "title": "Triangulation",
          "venue": "Computer Vision and Image Understanding, 1997（Hartley & Sturm）；相关思想早至 1980s",
          "oneline": "系统比较多种三角化方法，指出带归一化的 DLT 与最优法在精度与稳定性上各自的取舍。",
          "problem": "两条视线因噪声一般不会精确相交，简单求交点没有唯一解；不同三角化方法在误差分布与数值稳定性上差异巨大，实践中难以选择。",
          "idea": "把三角化写成「寻找 3D 点 X，使其在两幅图中的投影与观测点的偏差最小」。可用线性 DLT 快速求解，也可用迭代的最优法最小化重投影误差。研究表明：先做坐标归一化能显著提升稳定性。",
          "idea_flow": "flowchart LR\n  A[\"两相机投影矩阵\"] --> B[\"构造线性方程组\"]\n  B --> C[\"SVD解出3D点\"]\n  C --> D[\"重投影校验\"]",
          "contrib": "- 系统比较 DLT、中点法、最优法等三角化方法\n- 指出**坐标归一化**对数值稳定性的决定性作用\n- 给出重投影误差作为三角化质量的度量\n- 成为多视图几何的标准参考",
          "formula": "对每个视图 i：x_i × (P_i X) = 0，为 X 的两个线性方程。两视图共 4 个方程（3 独立）解 3 个未知数，用 SVD 求最小二乘解。",
          "experiment": "在含噪声合成数据上，归一化 DLT 与最优法精度接近，而最优法迭代开销更大；未归一化的 DLT 在退化配置下明显不稳。",
          "limit": "深度误差与基线长度成反比，小基线时极不稳定；对误匹配无免疫力；需要准确位姿。",
          "influence": "成为 SfM、SLAM、双目立体、多视图重建的核心步骤；OpenCV 的 triangulatePoints、COLMAP 等均基于此。",
          "summary": "两步求解、一步归一化，把「两条视线求交点」做成了稳定可靠的 3D 定位。",
      },
      [
          ("两条视线的交点", "每个相机对空间点有一条视线。理论上两线相交于该点，但噪声让它们错开，于是求「最接近两线」的点。", "flowchart LR\n  A[\"相机1视线\"] --> C[\"交点=3D点\"]\n  B[\"相机2视线\"] --> C"),
          ("DLT 线性解法", "用投影矩阵构造齐次线性方程组，其最小二乘解（SVD 最后一列）即 3D 点坐标，快速且无需迭代。", None),
          ("基线决定深度精度", "两台相机相距越远（基线越长），深度估计越准。基线接近 0（纯旋转）时，深度几乎不可解。", None),
          ("重投影误差做质检", "把三角化出的 3D 点重新投回两幅图，与原始像素比偏差。误差大的点判为坏点剔除。", None),
      ],
      [("准备输入", "两视图的投影矩阵 P₁、P₂（由内参 K 与位姿 R,t 组成），以及一对匹配像素点。"),
       ("构造方程组", "对每个视图写 x × (PX) = 0，得到关于 X 的线性方程，两视图共 4 行。"),
       ("SVD 求解", "对系数矩阵做 SVD，最小奇异值对应的右奇异向量即 3D 点（齐次坐标）。"),
       ("重投影校验与齐次化", "把点齐次化到欧氏坐标，计算重投影误差，剔除误差过大或深度异常的坏点。")],
      "时间复杂度 O(1) 每对点（4×4 SVD）；批量 N 对点 O(N)。空间复杂度 O(N)。",
      '''import cv2
import numpy as np

# 假设已有两视图投影矩阵 P1, P2 与匹配点 pts1, pts2
K = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], np.float32)
R = np.eye(3, dtype=np.float32)
t = np.array([[1.0], [0.0], [0.0]], np.float32)   # 基线 1 个单位
P1 = K @ np.hstack([np.eye(3), np.zeros((3, 1))])
P2 = K @ np.hstack([R, t])

pts1 = np.array([[320.0, 240.0], [400.0, 300.0]], np.float32)   # (N,2)
pts2 = np.array([[300.0, 240.0], [380.0, 300.0]], np.float32)

points4d = cv2.triangulatePoints(P1, P2, pts1.T, pts2.T)
points3d = (points4d[:3] / points4d[3]).T          # 齐次化 -> (N,3)
print("重建的 3D 点:\\n", points3d)''',
      '''import numpy as np


def triangulate_dlt(P1, P2, x1, x2):
    """手写 DLT 三角化。x1,x2 为齐次像素坐标 (3,)。"""
    A = np.vstack([
        x1[0] * P1[2] - x1[2] * P1[0],
        x1[1] * P1[2] - x1[2] * P1[1],
        x2[0] * P2[2] - x2[2] * P2[0],
        x2[1] * P2[2] - x2[2] * P2[1],
    ])
    _, _, Vt = np.linalg.svd(A)
    X = Vt[-1]
    return X[:3] / X[3]


K = np.array([[800., 0, 320], [0, 800., 240], [0, 0, 1]])
P1 = K @ np.hstack([np.eye(3), np.zeros((3, 1))])
P2 = K @ np.hstack([np.eye(3), np.array([[1.], [0], [0]])])

x1 = np.array([320., 240., 1.])
x2 = np.array([300., 240., 1.])
X = triangulate_dlt(P1, P2, x1, x2)
print("3D 点:", X)''',
      "基线越长深度越稳；务必做重投影误差过滤，剔除误差大或深度不合理的点，否则点云里全是飞点。",
      [("P1/P2", "两视图投影矩阵", "K[R|t]"), ("min_depth", "最小深度过滤", ">0"), ("reproj_thresh", "重投影误差阈值", "1~3 像素"), ("normalize", "坐标归一化", "推荐开启")],
      [
          ("基线太小", "两个相机几乎重合，深度误差爆炸，点云糊成一团。", "保证足够基线；纯旋转场景放弃三角化。"),
          ("误匹配生成飞点", "错误对应点三角化到很远的地方。", "先用 RANSAC 清匹配，三角化后再按重投影误差过滤。"),
          ("不归一化直接 DLT", "数值不稳定，结果抖动。", "先对像素坐标做归一化（Hartley 归一化）再求解。"),
          ("忽略深度符号", "三角化点跑到了相机背后。", "检查深度为正，负深度说明位姿有误。"),
      ],
      "基线要够、匹配要清、误差要滤；小基线就别指望深度准。",
      [("reproj_thresh", "重投影误差阈值", "1~3 px", "保留更多点但含坏点", "点更少但更干净"),
       ("min_depth", "最小深度", ">0", "剔远点", "保留远点"),
       ("方法", "DLT / 中点法", "DLT", "—", "—")],
      [("和本质矩阵串联", "E 分解得到位姿 → 三角化建初始点云 → 光束法平差联合优化。"),
       ("双目立体", "立体匹配得到视差后，三角化把视差换算成深度，即深度图。"),
       ("质检习惯", "三角化后一定打印重投影误差分布，误差中位数 >2 像素说明前端匹配有问题。")],
      [("100 对点 DLT", "≈0.5 ms", "cv2.triangulatePoints"),
       ("10000 对点", "≈50 ms", "批量线性"),
       ("含重投影过滤", "≈1.3×", "额外校验开销小")],
      )


# ================================================================
# 6. 光束法平差
# ================================================================
m = {
    "name": "光束法平差", "en": "Bundle Adjustment", "year": "1958",
    "author": "Photogrammetry 领域起源 / Triggs et al. 2000 总结",
    "paperUrl": "https://www.cs.cornell.edu/courses/cs4670/2015fa/lectures/lec25_ba.pdf",
    "chapter": "第10章 · 三维景物恢复", "chapterLink": "/chapters/ch10-3d-recovery",
    "branch": "几何视觉", "level": "高级",
    "tagline": "同时微调所有相机位姿和所有 3D 点，让「重投影误差」全局最小",
    "analogy": "你拍了 100 张照片重建一座雕像，结果发现模型有点歪。光束法平差像一位总导演：它同时指挥 100 台相机的站位和几万个 3D 点，让每个点投回每张照片时都尽可能落在原像素上——全局调到最齐。",
    "scene": "SfM/摄影测量最终优化、SLAM 后端全局一致、AR 大场景锚定、三维重建精修",
    "pros": ["全局最优，精度提升显著", "可同时优化相机、点、内参", "是现代 SfM/SLAM 的标配后端", "可利用稀疏结构高效求解"],
    "cons": ["计算量大（可达上亿参数）", "需要好的初值否则不收敛", "实现复杂（稀疏雅可比、LM 迭代）", "对误匹配敏感"],
    "dep_pre": "初始位姿 + 初始点云 + 匹配", "dep_peer": "PnP、三角化",
    "dep_post": "稠密重建、网格化、纹理映射",
    "anchor": "记住「BA = 最小化重投影误差，用 LM 迭代 + 稀疏矩阵加速」。",
    "params_arch": [
        ("optimizer", "优化器", "LM", "LM", "**Levenberg-Marquardt**"),
        ("max_iter", "最大迭代次数", "—", "—", "50~200"),
        ("loss", "损失函数", "Huber", "—", "**Huber（抗外点）**"),
        ("fix_intrinsics", "是否固定内参", "—", "—", "数据少时固定"),
    ],
    "failmodes": [
        ("初值太差不收敛", "位姿错得离谱时 BA 发散或陷局部最优。"),
        ("误匹配污染", "错误对应点把优化带偏，需鲁棒损失或预剔除。"),
        ("参数量爆炸导致卡死", "上万相机 + 百万点，不利用稀疏结构内存爆掉。"),
        ("全优化（含内参）不稳", "数据不足时让内参参与优化会过拟合。"),
    ],
}
build("bundle-adjustment", m,
      "把相机位姿、3D 点坐标（有时还有内参）放在一起，最小化所有观测点的重投影误差之和。",
      "前面每一步（匹配、E 分解、三角化）都带误差，累积起来就是「缝合怪」。光束法平差是这个流程的**总收口**——全局联合优化，把精度从「能看」提升到「能用」。它是所有 SfM/SLAM 系统的精度命门。",
      "你用一个 App 拍了一间房做 3D 户型重建。没有 BA 时，起点和终点会「接不上」，墙线歪斜；加上 BA 全局优化后，整个房间严丝合缝。",
      ["搞懂 BA 的目标函数就是「重投影误差平方和」", "理解为什么它能全局提升精度", "知道 LM 迭代与稀疏结构为何关键", "抄一段真实可用的 BA 代码（scipy/ceres/g2o）", "避开初值差、误匹配等坑", "明白它在 SfM/SLAM 中的收口地位"],
      {
          "title": "Bundle Adjustment — A Modern Synthesis",
          "venue": "Vision Algorithms: Theory and Practice, 2000（Triggs 等综述）",
          "oneline": "系统总结光束法平差的现代实现，阐明其目标函数、稀疏结构与 LM 优化框架。",
          "problem": "SfM 由多步估计串成，每步误差累积导致最终模型不一致（漂移、错位）。如何联合优化全部参数使整体最优，且计算上可行，是长期难题。",
          "idea": "把所有待估参数（相机位姿、3D 点、内参）凑成一个巨大的最小二乘问题，目标是让每个 3D 点投回每张照片的位置尽量贴近观测像素。用 Levenberg-Marquardt 迭代求解，并利用「点与相机之间稀疏相连」的结构（Schur 补）大幅降维。",
          "idea_flow": "flowchart LR\n  A[\"初始位姿+点云\"] --> B[\"计算重投影误差\"]\n  B --> C[\"LM迭代更新\"]\n  C --> D{\"收敛?\"}\n  D -- 否 --> B\n  D -- 是 --> E[\"优化后模型\"]",
          "contrib": "- 给出 BA 的**统一数学表述**与 LM 求解框架\n- 阐明**稀疏雅可比与 Schur 补**带来的计算可行性\n- 引入鲁棒损失函数处理外点\n- 成为 SfM/摄影测量现代实现的参考规范",
          "formula": "min Σ_i Σ_j ρ( ‖ x_ij − π(K_i, R_i, t_i, X_j) ‖² )，其中 x_ij 为观测像素、π 为投影函数、X_j 为 3D 点、ρ 为鲁棒损失（如 Huber）。",
          "experiment": "在标准 SfM 数据集上，BA 可把重投影误差从数像素降到亚像素级，显著提升重建精度与全局一致性。",
          "limit": "计算量与内存开销大；依赖良好初值；对误匹配敏感；需专门优化库与稀疏结构利用。",
          "influence": "成为所有 SfM（COLMAP/Bundler）与 SLAM（ORB-SLAM/g2o/Ceres）系统的标配后端，是「传统三维重建精度天花板」的技术根基。",
          "summary": "把「所有相机 + 所有点」一起最小二乘，用稀疏结构撑起计算可行性——这是三维重建精度的护城河。",
      },
      [
          ("重投影误差", "把 3D 点投回图像得到的像素位置，与真实观测像素的差，就是误差。BA 要让所有误差的平方和最小。", "flowchart LR\n  A[\"3D点\"] --> B[\"投影到图\"] --> C[\"与观测比\"] --> D[\"误差\"]"),
          ("联合优化", "不是单独调相机或单独调点，而是全部参数一起调——因为相机一动，所有点的误差都变，必须联立。", None),
          ("为什么用 LM", "LM 在高斯牛顿与梯度下降之间自适应切换，兼顾收敛速度与稳定性，是 BA 的标准优化器。", None),
          ("稀疏结构与 Schur 补", "每个 3D 点只被少数相机看到，雅可比矩阵高度稀疏。利用它消元后，求解规模大幅下降，百万点级 BA 才跑得动。", None),
      ],
      [("构建初始估计", "用 E 分解 / PnP / 三角化得到初始相机位姿与点云，作为优化的起点。"),
       ("定义目标函数", "写出所有观测的重投影误差平方和，叠加鲁棒损失函数以抗外点。"),
       ("LM 迭代求解", "计算雅可比与海森矩阵，用 Schur 补降维，迭代更新参数直至收敛。"),
       ("输出与验收", "得到优化后位姿与点云；检查重投影误差分布是否降到亚像素级。")],
      "时间复杂度取决于参数规模与迭代次数，借助稀疏结构后近似 O(迭代 × (相机数 + 点数))；空间复杂度与观测数成正比。",
      '''import numpy as np
from scipy.optimize import least_squares

# 极简 BA：优化一个 3D 点与一个相机的外参（示意）
X0 = np.array([0.0, 0.0, 5.0])          # 初始 3D 点
K = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], np.float32)
observed = np.array([318.0, 242.0])     # 观测到的像素


def project(params):
    tx, ty, tz, Xx, Xy, Xz = params
    Xc = np.array([Xx + tx, Xy + ty, Xz + tz])   # 平移到相机坐标
    proj = K @ Xc
    return proj[:2] / proj[2]


def residual(params):
    return project(params) - observed


x_init = np.array([0.0, 0.0, 0.0, *X0])
res = least_squares(residual, x_init, method="lm")
print("优化后参数:", res.x)
print("最终重投影误差:", np.linalg.norm(res.fun))''',
      '''# 生产环境请用专门的 BA 库，别手写
# 方案1：Ceres Solver（C++，最主流）
#   - 定义 ResidualBlock 描述重投影误差
#   - 交给 ceres::Solve 自动求导与 LM 优化
# 方案2：g2o（C++，SLAM 常用）
#   - 顶点=相机位姿/3D点，边=观测约束
#   - 调用 optimizer.optimize(iterations)
# 方案3：scipy.optimize.least_squares（Python 小规模）
#   - 直接传残差函数，适合几千参数以内

# 下面用 g2o 风格的伪代码示意流程：
PLAN = """
1. 建图：为每个相机位姿、每个 3D 点添加顶点
2. 加边：每个观测 x_ij 添加一条「投影误差」边
3. 设初值：用 PnP/三角化结果填充顶点
4. 选优化器：Levenberg-Marquardt
5. 迭代优化：optimizer.optimize(50)
6. 输出：优化后的位姿与点云
"""
print(PLAN)''',
      "生产环境不要手写 BA，直接用 Ceres / g2o / GTSAM；手写仅用于理解目标函数。务必加 Huber 鲁棒损失抵抗误匹配。",
      [("loss", "鲁棒损失函数", "Huber"), ("max_iter", "最大迭代次数", "50~200"), ("fix_intrinsics", "是否固定内参", "数据少时固定"), ("optimizer", "优化器", "LM")],
      [
          ("初值太差直接发散", "位姿初值错得离谱时，LM 也拉不回来。", "先用 PnP / 三角化拿到不错的初值，再上 BA。"),
          ("不用鲁棒损失", "少量误匹配就能把全局优化带偏。", "用 Huber / Cauchy 损失，或先做 RANSAC 清匹配。"),
          ("全参数一起优化内参", "数据不足时内参过拟合，结果发散。", "数据量小时固定内参，只优化位姿与点。"),
          ("自己手写大规模 BA", "内存爆炸、速度感人。", "用 Ceres/g2o，它们内置稀疏结构与高效求解。"),
      ],
      "初值要准、损失要鲁棒、内参数据不足就固定；大规模一律用现成库。",
      [("loss", "鲁棒损失", "Huber", "更抗外点", "更接近最小二乘"),
       ("max_iter", "迭代次数", "50~200", "更充分但更慢", "可能未收敛"),
       ("fix_intrinsics", "固定内参", "视数据量", "—", "—")],
      [("SfM 中的位置", "匹配 → E → 三角化 → **BA** → 稠密重建，BA 是精度收口。"),
       ("SLAM 后端", "ORB-SLAM 的局部+全局 BA 是它能在走廊场景不漂移的关键。"),
       ("实用建议", "先用小规模子集跑 BA 验证正确性，再扩到全量；否则调试困难。")],
      [("100 相机 / 1 万点", "≈2 s", "Ceres，稀疏求解"),
       ("1000 相机 / 100 万点", "≈数分钟", "COLMAP 全局 BA"),
       ("scipy 手写（几千参数）", "≈0.5 s", "仅适合小规模学习")],
      )


# ================================================================
# 7. Haar 小波变换
# ================================================================
m = {
    "name": "Haar 小波变换", "en": "Haar Wavelet Transform", "year": "1909",
    "author": "Alfréd Haar",
    "paperUrl": "https://en.wikipedia.org/wiki/Haar_wavelet",
    "chapter": "第3章 · 图像预处理", "chapterLink": "/chapters/ch03-preprocessing",
    "branch": "图像处理", "level": "中级",
    "tagline": "用小方波的「平均值与差值」反复分解图像，一眼看出哪里平、哪里有突变",
    "analogy": "Haar 小波像把照片反复「对折比较」：先左右相邻两两求和（看到整体趋势）与求差（看到这里有没有突变），再对求和的低分辨率图重复一次。最后你会得到一堆「差值图」——它们精准标出了边缘在哪里。",
    "scene": "图像压缩（JPEG2000 概念前身）、多分辨率分析、快速 Haar 特征（Viola-Jones 人脸的基石）、边缘/纹理分析",
    "pros": ["计算极简（只有加减法）", "多分辨率分析，天然金字塔", "正交、可逆、无冗余", "是 Viola-Jones 积分图 Haar 特征的理论近亲"],
    "cons": ["小波基粗糙，方向分辨力弱", "不如 Daubechies 等平滑小波精细", "对噪声敏感（差分量会放大噪声）", "单一尺度信息量大，需配合阈值"],
    "dep_pre": "灰度化", "dep_peer": "Gabor 滤波、傅里叶变换、DoG",
    "dep_post": "系数阈值去噪、特征提取、边缘检测",
    "anchor": "记住「Haar 只有平均与差——低通看趋势，高通看边缘」。",
    "params_arch": [
        ("level", "分解层数", "—", "—", "**2~5 层**"),
        ("mode", "边界延拓方式", "—", "symmetric", "symmetric / periodization"),
        ("threshold", "去噪阈值", "—", "—", "软阈值 3σ"),
        ("wavelet", "小波基", "haar", "haar", "haar（或 db2 更平滑）"),
    ],
    "failmodes": [
        ("层数过多丢信息", "分解太深，最粗尺度只剩几个像素，失去意义。"),
        ("未做边界延拓", "卷积在边界处出错，产生边缘伪影。"),
        ("直接对彩色三通道分解", "应在 YCbCr 的亮度通道或 Lab 分解更合理。"),
        ("把细节系数当噪声一刀切", "阈值过大把所有边缘也删了。"),
    ],
}
build("haar-wavelet", m,
      "用一对「平均滤波器」和「差分滤波器」对图像做多级分解，得到低频趋势与各尺度的高频细节。",
      "傅里叶告诉你「图像里有哪些频率」，但丢掉了「频率出现在哪里」。Haar 小波同时给出**频率与位置**——而且只用加减法。它是多分辨率分析的最简形态，也是 Viola-Jones 人脸检测特征的思想源头。",
      "实时人脸检测要在几毫秒内判断「眼睛区域比脸颊暗」这种局部明暗模式。Haar 特征用小矩形区域的灰度差来表示这种模式，配合积分图 O(1) 算出——这正是 Haar 小波「均值与差值」思想在检测里的化身。",
      ["搞懂「平均 + 差分」为什么能同时抓趋势和边缘", "理解多分辨率分解与图像金字塔的关系", "掌握分解层数、阈值去噪的用法", "抄一段可跑的小波分解与重构代码", "避开层数过多、边界伪影等坑", "明白它与 Viola-Jones 的历史联系"],
      {
          "title": "Zur Theorie der orthogonalen Funktionensysteme",
          "venue": "Mathematische Annalen, 1910（Haar 原始工作）",
          "oneline": "提出历史上第一个正交小波基——最简单的小方波，开创多分辨率分析的先河。",
          "problem": "20 世纪初，如何用更局部化的基函数表示信号（相比傅里叶的全局正弦波）是待解问题；傅里叶基在时/空域没有位置信息。",
          "idea": "用最简单的小方波作为基：在一半区间取 +1、另一半取 −1，配合尺度伸缩与位置平移，张成一组正交基。任何信号都能用这些「小方波」的加权和表示，且每个小方波有明确的位置。",
          "idea_flow": "flowchart LR\n  A[\"信号\"] --> B[\"与各尺度小方波内积\"]\n  B --> C[\"小波系数\"]\n  C --> D[\"系数大处=突变/边缘\"]",
          "contrib": "- 提出第一个**正交小波基**，开创小波分析\n- 揭示「尺度 + 位置」双重局部的表示思想\n- 为多分辨率分析、Mallat 快速算法奠基\n- 成为离散小波变换最简单的实例",
          "formula": "Haar 尺度函数 φ 与 Haar 小波 ψ：\nφ(x) = 1 (0≤x<1)，否则 0\nψ(x) = 1 (0≤x<0.5)，−1 (0.5≤x<1)，否则 0\n分解即信号与 φ、ψ 的伸缩平移做内积。",
          "experiment": "在图像上，一层 Haar 分解把图分成左上低频（趋势）+ 三个方向高频（水平/垂直/对角边缘）；多级分解形成小波金字塔，广泛用于压缩与去噪。",
          "limit": "小波基不连续，方向选择性弱；图像平滑区域的表现不如 Daubechies/双正交小波；差分量对噪声敏感。",
          "influence": "奠定小波多分辨率分析理论（Mallat 1989 给出快速算法）；直接启发 Viola-Jones 用「矩形区域灰度差」构建 Haar 特征实现实时人脸检测；JPEG2000 采用的小波（CDF 9/7）亦属此家族。",
          "summary": "最朴素的小方波，却开创了「既看频率又看位置」的多分辨率分析。",
      },
      [
          ("尺度与小波函数", "尺度函数做「平均」抓趋势，小波函数做「差」抓突变。两者配合，既保留整体又定位细节。", "flowchart LR\n  A[\"尺度函数: 平均\"] --> B[\"低频趋势\"]\n  C[\"小波函数: 差值\"] --> D[\"高频细节\"]"),
          ("一层分解的四宫格", "对图像行、列各做一次低通/高通，得到 LL（低频）、LH、HL、HH（三个方向的细节）。", "flowchart TB\n  I[\"图像\"] --> LL[\"LL 低频\"]\n  I --> LH[\"LH 竖边缘\"]\n  I --> HL[\"HL 横边缘\"]\n  I --> HH[\"HH 对角\"]"),
          ("多分辨率金字塔", "对 LL 再分解一层，层层递进，得到不同尺度的表示——和图像金字塔异曲同工。", None),
          ("与 Haar 特征的联系", "Viola-Jones 的 Haar 特征就是「白矩形区灰度均值 − 黑矩形区灰度均值」，正是 Haar 小波「平均值与差值」思想在检测任务中的应用。", None),
      ],
      [("灰度化", "把图像转灰度（或只处理亮度通道），小波分解通常在单通道上做。"),
       ("多层分解", "用平均/差分滤波器对行与列交替滤波，逐层得到 LL/LH/HL/HH 四个子带。"),
       ("系数处理", "按需对高频系数做阈值（去噪）或直接保留（特征/压缩）。"),
       ("重构或提取特征", "逆变换重构图像，或直接用系数作为特征送入下游任务。")],
      "时间复杂度 O(W·H) 每层（只有加减）；多层 O(W·H·(1+1/4+…))≈O(W·H)。空间复杂度 O(W·H)。",
      '''import numpy as np
import cv2

img = cv2.imread("lena.jpg", cv2.IMREAD_GRAYSCALE).astype(np.float32)


def haar_2d(img):
    """一层二维 Haar 分解，返回 LL, LH, HL, HH。"""
    h, w = img.shape
    # 行方向：低通(平均) 与 高通(差分)
    row = img.reshape(h, w // 2, 2)
    low = (row[:, :, 0] + row[:, :, 1]) / np.sqrt(2)
    high = (row[:, :, 0] - row[:, :, 1]) / np.sqrt(2)
    L = np.hstack([low, high])
    # 列方向同理
    Lr = L.reshape(h // 2, 2, w)
    LL = (Lr[:, 0, :] + Lr[:, 1, :]) / np.sqrt(2)
    LH = (Lr[:, 0, :] - Lr[:, 1, :]) / np.sqrt(2)
    col = np.vstack([LL, LH])
    return col[:h // 2, :], col[h // 2:, :]


LL, detail_rows = haar_2d(img)
print("一层分解 LL 形状:", LL.shape)
cv2.imwrite("haar_ll.png", np.clip(LL, 0, 255).astype(np.uint8))''',
      '''import numpy as np
import pywt   # pip install PyWavelets

img = np.array([[10, 12, 20, 22],
                [11, 13, 21, 23],
                [30, 32, 40, 42],
                [31, 33, 41, 43]], dtype=np.float32)

# 一层 haar 分解，得到 4 个子带
coeffs = pywt.dwt2(img, "haar")
LL, (LH, HL, HH) = coeffs
print("LL (低频):\\n", LL)
print("LH (竖边缘):\\n", LH)
print("HL (横边缘):\\n", HL)
print("HH (对角):\\n", HH)

# 逆变换重构
recon = pywt.idwt2((LL, (LH, HL, HH)), "haar")
print("重构是否还原:", np.allclose(recon, img))''',
      "直接用小波做特征时，差分子带对噪声敏感，建议先轻微高斯平滑；做去噪时用软阈值而非硬阈值以减少振铃。",
      [("level", "分解层数", "2~5"), ("wavelet", "小波基", "haar"), ("mode", "边界延拓", "symmetric"), ("threshold", "去噪阈值", "3σ（软阈值）")],
      [
          ("层数分解过多", " decomposed 到只剩几像素，最粗尺度没有意义。", "层数控制在 2~5，保证最粗图仍有足够分辨率。"),
          ("边界出现伪影", "滤波在图像边界处理不当产生条纹。", "指定 mode='symmetric' 或 'periodization'。"),
          ("彩色图三通道直接分解", "色度通道分解意义小且易偏色。", "转 YCbCr 只分解 Y，或转 Lab 只分解 L。"),
          ("阈值一刀切", "把细节系数全清零，边缘一起没了。", "用软阈值 + 分尺度自适应阈值（Donoho 方法）。"),
      ],
      "Haar 只有加减、用它做多分辨率；层数别贪多、边界要延拓。",
      [("level", "分解层数", "3", "尺度更粗", "尺度更细"),
       ("threshold", "去噪阈值", "3σ", "去噪更狠但伤细节", "去噪弱"),
       ("wavelet", "小波基", "haar", "db2 更平滑", "haar 最省算")],
      [("去噪套路", "分解 → 对细节系数软阈值 → 重构，是经典的小波去噪三步曲。"),
       ("和 Viola-Jones 的关系", "用积分图快速算矩形灰度差 = Haar 特征的 O(1) 实现，做人脸检测的实时化关键。"),
       ("压缩应用", "保留少量大系数、丢弃小系数即可压缩，是 JPEG2000 的核心机制之一。")],
      [("512×512 灰度，3 层", "≈1 ms", "仅有加减运算"),
       ("pywt 一层分解", "≈0.5 ms", "PyWavelets 实现"),
       ("对比 FFT 同尺寸", "≈3 ms", "小波明显更快")],
      )

print("批次 B 完成")
