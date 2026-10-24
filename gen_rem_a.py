#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补齐算法批次 A：gaussian-blur / median-filter / hough-circles / contour-fitting / freak / felzenszwalb-segmentation / knn-background"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_rem_tpl import build

BOOK = "章毓晋《计算机视觉教程》"


# ================================================================
# 1. 高斯滤波
# ================================================================
m = {
    "name": "高斯滤波", "en": "Gaussian Blur", "year": "1809",
    "author": "Carl Friedrich Gauss（高斯函数）/ 图像处理沿用",
    "paperUrl": "https://homepages.inf.ed.ac.uk/rbf/HIPR2/gsmooth.htm",
    "chapter": "第3章 · 图像预处理", "chapterLink": "/chapters/ch03-preprocessing",
    "branch": "图像处理", "level": "基础",
    "tagline": "给图像戴一副老花镜——最常用的平滑去噪瑞士军刀",
    "analogy": "想象你隔着一层磨砂玻璃看照片：近处的细纹看不清了，大轮廓还在。离你越近的像素权重越大，越远的权重越小，像一个钟形的钟罩把附近的颜色加权平均掉——这就是高斯模糊。",
    "scene": "拍照手抖模糊、人脸磨皮、Canny 去噪预处理、SIFT/SURF 尺度空间构建",
    "pros": ["数学优美、各向同性", "可分离卷积，速度 O(n) 而非 O(n²)", "各向同性，不会产生方向性条纹", "无数算法的前置步骤（Canny/SIFT）"],
    "cons": ["会把边缘一起糊掉，不能保边", "对椒盐噪声无效", "σ 太大丢失细节", "计算量随核半径增长"],
    "dep_pre": "灰度化、通道拆分", "dep_peer": "中值滤波、双边滤波",
    "dep_post": "Canny 边缘检测、SIFT 尺度空间、梯度计算",
    "anchor": "记住「σ 是管模糊半径、ksize 是管范围」——ksize 一般取 6σ 左右的奇数。",
    "params_arch": [
        ("ksize", "高斯核尺寸", "6σ+1（奇数）", "(5,5)", "(5,5) 或 (7,7)"),
        ("sigmaX", "X 方向标准差 σ", "由 ksize 反推", "0（自动推导）", "按场景 1.0~3.0"),
        ("sigmaY", "Y 方向标准差", "= sigmaX", "0（等于 sigmaX）", "0"),
        ("borderType", "边界处理", "—", "BORDER_DEFAULT（反射）", "BORDER_REPLICATE（消暗边）"),
    ],
    "failmodes": [
        ("边缘被糊掉", "σ 越大边缘越模糊，若目标是保边去噪，必须换成双边滤波。"),
        ("ksize 取偶数", "OpenCV 直接报错，核尺寸必须是正奇数。"),
        ("图像边界变暗", "默认反射边界的卷积会使边缘略变暗，可改用 BORDER_REPLICATE。"),
        ("σ=0 的误用", "sigmaX=0 时按 ksize 自动推导 σ，但二者不对应会让模糊程度失控。"),
    ],
}
build("gaussian-blur", m,
      "拿一个「钟形权重小窗」在图上滑动，每个像素被邻居按距离加权平均——越近权重越大。",
      "几乎每个视觉算法的第一步都是「去噪」。真实图像总有传感器噪声、压缩伪影，直接算梯度会把噪声当边缘。高斯滤波是**最通用、最可控**的平滑手段，也是 Canny、SIFT 等经典算法的固定前置。",
      "你在夜里用手机拍路牌，照片满是噪点。先做一个高斯模糊，噪点被抹平，路牌轮廓却还认得出来——这就是为什么相机 App 的「降噪」默认就是高斯。",
      ["搞懂高斯核长什么样、σ 和核大小什么关系", "理解「权重按距离衰减」的直觉，不再死记公式", "看懂可分离卷积为什么能让速度从 O(n²) 降到 O(n)", "抄一段可跑的 OpenCV + NumPy 代码", "避开偶数核、边界变暗等 4 个高频坑", "掌握 σ 与 ksize 的换算口诀"],
      {
          "title": "高斯函数与图像平滑（非单篇论文，源自高斯分布的图像应用）",
          "venue": "数学基础：C. F. Gauss (1809)；图像应用见 Haralick & Shapiro (1992)",
          "oneline": "用二维高斯分布作为卷积核，实现加权平均式的各向同性平滑。",
          "problem": "早期图像去噪多用简单均值滤波（盒子核），但均值核会把邻域一视同仁，导致图像出现方块状伪影，且不满足「距离越近权重越大」的直觉。",
          "idea": "把概率论里的高斯分布搬到图像上：离中心越近的像素权重越高，权重曲线是钟形。这样一次平滑既去了噪，又最大限度保留了整体结构。",
          "idea_flow": "flowchart LR\n  A[\"二维高斯分布\"] --> B[\"离散化成权重核\"]\n  B --> C[\"在图像上滑动加权平均\"]\n  C --> D[\"平滑结果\"]",
          "contrib": "- 提出用**可分离**方式实现二维高斯卷积：先横向一维卷积，再纵向一维卷积\n- 证明二维高斯核可分解为两个一维高斯核的乘积\n- 奠定了尺度空间理论（SIFT 的多尺度）的数学基础",
          "formula": "二维高斯核：G(x, y) = (1 / (2πσ²)) · exp(−(x² + y²) / (2σ²))。可分离性：G(x, y) = G(x) · G(y)，于是 O(W²) 的二维卷积变成两趟 O(W) 的一维卷积。",
          "experiment": "在含高斯噪声的测试图上，高斯滤波相比均值滤波显著减少了块状伪影；在 Canny 检测前置使用 σ=1.4 时，边缘定位误差最小。",
          "limit": "高斯滤波是**线性低通滤波**，不区分边缘与噪声——边缘同样被衰减。对脉冲（椒盐）噪声几乎无效。",
          "influence": "它是尺度空间、SIFT、SURF、Canny、图像金字塔、LoG/DoG 等几乎所有经典多尺度方法的基石；深度学习时代的卷积神经网络（CNN）本质上也是可学习的高斯核推广。",
          "summary": "一个 1809 年的概率公式，成了 200 年后图像处理里出现频率最高的一行代码。",
      },
      [
          ("权重从小到大的钟形核", "高斯核是一个「中间高、四周低」的小矩阵，中心权重最大，越往外越小。OpenCV 会自动把核归一化，保证总权重为 1，这样滤波后亮度不变。", "flowchart LR\n  A[\"距离中心近\"] --> B[\"权重大\"]\n  C[\"距离中心远\"] --> D[\"权重小\"]"),
          ("σ 决定模糊程度", "σ（标准差）越大，钟形越扁平，远处邻居也参与平均，图像越糊；σ 越小则越接近原图，去噪能力越弱。", None),
          ("可分离卷积", "二维高斯核可以拆成「横着一条 + 竖着一条」，先横向卷一遍再纵向卷一遍，结果和直接二维卷积一样，但速度快得多。", "flowchart LR\n  A[\"二维核 WxW\"] --> B[\"拆成一维横向\"] --> C[\"再一维纵向\"]"),
          ("尺度空间的意义", "不同 σ 的高斯模糊结果堆叠起来，构成「尺度金字塔」。SIFT 正是靠它来检测不同大小的特征点。", None),
      ],
      [("选定 σ", "根据噪声水平与要保留的细节尺度选定 σ，σ 越大能压掉越大的噪声，也糊掉越大的细节。"),
       ("由 σ 定核大小", "核半径约取 3σ，核尺寸 ksize ≈ 2·ceil(3σ)+1，必须是正奇数。"),
       ("横向一维卷积", "用一维高斯向量 [g(-r), …, g(0), …, g(r)] 在图像行方向滑动加权平均。"),
       ("纵向一维卷积", "同一一维向量在列方向再卷一遍，得到最终平滑图像。")],
      "时间复杂度：朴素二维卷积 O(W·H·k²)；可分离后 O(W·H·k)，k 为核边长。空间复杂度 O(W·H)。",
      '''import cv2
import numpy as np

img = cv2.imread("input.jpg")

# 最常用：ksize=(5,5)，sigmaX=0 让 OpenCV 自动推导
blur = cv2.GaussianBlur(img, (5, 5), 0)

# 想自己控制模糊程度：先定 sigma，再反推 ksize
sigma = 2.0
k = int(2 * round(3 * sigma) + 1)
blur2 = cv2.GaussianBlur(img, (k, k), sigma)

cv2.imwrite("blur.png", blur)''',
      '''import numpy as np
import cv2


def gaussian_kernel(size, sigma):
    """生成归一化的一维高斯核。"""
    ax = np.arange(-(size // 2), size // 2 + 1, dtype=np.float32)
    g = np.exp(-(ax ** 2) / (2 * sigma ** 2))
    return g / g.sum()


def my_gaussian_blur(img, ksize, sigma):
    """可分离高斯模糊：先横向再纵向。"""
    g = gaussian_kernel(ksize, sigma)
    out = img.astype(np.float32)
    # 横向
    tmp = np.apply_along_axis(lambda r: np.convolve(r, g, mode="same"), 1, out)
    # 纵向
    res = np.apply_along_axis(lambda c: np.convolve(c, g, mode="same"), 0, tmp)
    return np.clip(res, 0, 255).astype(np.uint8)


img = cv2.imread("input.jpg", cv2.IMREAD_GRAYSCALE)
out = my_gaussian_blur(img, 9, 2.0)
print(out.shape)''',
      "ksize 必须是正奇数；sigmaX=0 时 OpenCV 按 ksize 公式 sigma = 0.3·((ksize−1)·0.5 − 1) + 0.8 自动推导。",
      [("ksize", "高斯核尺寸（正奇数）", "(5,5)"), ("sigmaX", "X 方向标准差", "0（自动）"), ("sigmaY", "Y 方向标准差", "0（跟随 sigmaX）"), ("borderType", "边界填充方式", "BORDER_DEFAULT")],
      [
          ("核尺寸必须是奇数", "传 (4,4) 会直接抛异常，OpenCV 要求正奇数。", "养成习惯：ksize = 2·r + 1，r 是想要的核半径。"),
          ("sigmaX=0 不是不模糊", "很多人以为 sigmaX=0 表示不做模糊，其实它表示「自动推导 σ」，模糊照样发生。", "想真的不处理就别调用，或者用 sigmaX=0 但 ksize=(1,1)。"),
          ("把边缘一起糊掉了", "高斯是线性低通，边缘和噪声一起被压。", "需要保边就换 cv2.bilateralFilter；需要保边又更快可用 cv2.medianBlur。"),
          ("深色背景出现暗边", "默认反射边界会令图像四边略暗。", "改用 cv2.BORDER_REPLICATE 复制边界像素。"),
      ],
      "sigma 定模糊、ksize 定范围；ksize ≈ 6σ+1 取奇数；保边别用它。",
      [("ksize", "核大小", "(5,5)", "更糊、更慢", "更接近原图"),
       ("sigmaX", "模糊强度 σ", "1.0~2.0", "模糊强、细节丢", "去噪弱"),
       ("borderType", "边界模式", "REPLICATE", "—", "—")],
      [("和 Canny 搭配", "Canny 内置高斯平滑，别重复做；若要更强去噪，可先手动高斯 σ=1.0，再调低 Canny 的 apertureSize。"),
       ("和 SIFT 搭配", "SIFT 内部用 σ=1.6 的高斯建尺度空间，自己预处理时不要超过这个值，否则特征点漂移。"),
       ("估计 σ 的小技巧", "用拉普拉斯方差的噪点估计法，或直接对平坦区域算局部标准差。")],
      [("640×480 灰度，ksize=5", "≈0.6 ms", "OpenCV 可分离卷积，单核"),
       ("1920×1080 彩色，ksize=7", "≈4 ms", "三通道分别处理"),
       ("1920×1080 彩色，ksize=31", "≈35 ms", "大核明显变慢")],
      )


# ================================================================
# 2. 中值滤波
# ================================================================
m = {
    "name": "中值滤波", "en": "Median Filter", "year": "1978",
    "author": "John Tukey",
    "paperUrl": "https://ieeexplore.ieee.org/document/1163410",
    "chapter": "第3章 · 图像预处理", "chapterLink": "/chapters/ch03-preprocessing",
    "branch": "图像处理", "level": "基础",
    "tagline": "邻居投票取中位数——椒盐噪声的克星",
    "analogy": "你站在广场上听大家报价，大多数人都喊 50 块，有两个人恶作剧喊 0 和 1000。平均是 275，严重失真；但取中位数还是 50，完美干掉捣蛋鬼。中值滤波就是这么回事。",
    "scene": "椒盐噪声去除、扫描文档去噪、老照片修复、二值图去小白点",
    "pros": ["能彻底消灭椒盐噪声", "不引入新的灰度值（保真）", "对边缘的保护优于均值滤波", "实现简单、无需参数"],
    "cons": ["对高斯噪声效果一般", "核大了会抹掉细线条", "速度随核平方增长", "细节圆形化（小目标被削角）"],
    "dep_pre": "灰度化", "dep_peer": "高斯滤波、双边滤波",
    "dep_post": "二值化、连通域分析、边缘检测",
    "anchor": "记住「中值滤波专治黑白点，核取 3 就够狠，取 5 会伤细线」。",
    "params_arch": [
        ("ksize", "邻域窗口边长", "3", "5", "**3**（>5 慎用）"),
        ("边框", "窗口在边缘的处理", "—", "自动反射", "先 pad 再滤波"),
    ],
    "failmodes": [
        ("把细线一起删掉", "核大于细节宽度时，细笔画、细网格会被当成噪声抹掉。"),
        ("对高斯噪声无感", "中值对连续型噪声不擅长，这时该用高斯。"),
        ("大核变慢", "中值需要对窗口排序，ksize=9 时比 ksize=3 慢近一个数量级。"),
        ("彩色图误用", "直接对 BGR 三通道分别中值可能产生偏色，应确认通道处理方式。"),
    ],
}
build("median-filter", m,
      "在像素周围取一个小窗口，把这些像素的灰度值排序，取正中间的值替换中心像素。",
      "椒盐噪声（孤立的纯黑/纯白点）是均值与高斯滤波的噩梦——它们会被摊开成一片灰，去不干净。中值滤波用「投票取中间值」的方式，直接把离群点投出去，是**非线性去噪**的代表。",
      "你扫描一张老文件，纸面上散落着黑点和白点。高斯滤波做完还是一层脏兮兮的灰雾，中值滤波做完黑白点直接消失，字迹却依然锐利。",
      ["理解「排序取中位数」为什么能干掉椒盐点", "看懂中值滤波与均值滤波的本质区别（非线性 vs 线性）", "知道它的临界失败点：细线会被吃掉", "抄一段 OpenCV 与 NumPy 的对照实现", "避开大核、彩色偏色等坑", "会用「中值 + 形态学」组合清二值图"],
      {
          "title": "Nonlinear (nonsuperposable) methods for smoothing data",
          "venue": "Proc. Conf. Record, EASCON 1974（Tukey）；图像中值滤波 1978 年普及",
          "oneline": "提出用邻域中位数代替均值做平滑，可彻底抑制脉冲噪声。",
          "problem": "20 世纪 70 年代，信号与图像处理几乎被线性滤波垄断。但线性滤波对脉冲噪声（个别点被完全污染）无能为力：平均值会被离群点带偏。",
          "idea": "既然均值怕离群点，那就别用均值——用排序后的中位数。中位数只关心「排在中间的那个」，个别极端值再大也影响不了它。",
          "idea_flow": "flowchart LR\n  A[\"邻域像素\"] --> B[\"排序\"] --> C[\"取中位数\"] --> D[\"替换中心\"]",
          "contrib": "- 提出**非线性平滑**这一整类新方法\n- 证明中值滤波能完全消除宽度小于窗口半径的脉冲\n- 提出「根信号」概念，为中值滤波族（加权中值、方向中值）奠基",
          "formula": "out(x, y) = median{ I(x+i, y+j) | (i, j) ∈ W }，W 为 k×k 邻域窗口。",
          "experiment": "对叠加 10% 椒盐噪声的图像，3×3 中值滤波几乎完全恢复原图，而同等核的均值滤波仍留下大片灰斑。",
          "limit": "对高斯型噪声提升有限；核越大，边缘与细结构损失越明显；排序运算限制了实时性。",
          "influence": "成为图像去噪的标准工具，并催生了加权中值、中值金字塔、形态学滤波等一大批非线性方法；也是 JPEG 抗脉冲噪声、扫描仪固件的常驻算法。",
          "summary": "一个「取中位数」的朴素想法，成了所有椒盐去噪的默认答案。",
      },
      [
          ("为什么中位数不怕离群点", "均值会被极端值拉偏，中位数只看排序位置。1000 个 50 里混进一个 0 和一个 1000，排序后中间仍是 50。", None),
          ("非线性滤波", "中值滤波不满足「叠加原理」，输出不能写成输入像素的线性加权和，因此称为非线性滤波。", "flowchart LR\n  A[\"线性：输出=Σw·输入\"] --> B[\"中值：输出=中位数\"]"),
          ("椒盐噪声模型", "椒盐噪声即像素被随机替换成 0 或 255，像撒了黑胡椒与白盐，中值滤波专门针对它设计。", None),
          ("窗口形状", "除了方形窗口，还可用十字形、圆形窗口，能减少对斜线的破坏。", None),
      ],
      [("选窗口大小", "从 3×3 起步，椒盐比例高时用 5×5，但超过 5×5 会明显伤细节。"),
       ("边缘填充", "窗口越过图像边界时，常用复制或反射填充，避免边缘变暗。"),
       ("排序取中值", "对窗口内像素灰度排序，取第 (k²+1)/2 个值作为输出。"),
       ("滑窗输出", "窗口逐像素滑动，得到整幅滤波结果。")],
      "时间复杂度 O(W·H·k²·log k)（每窗口排序）；用直方图法可优化到近似 O(W·H·k)。空间复杂度 O(W·H)。",
      '''import cv2

img = cv2.imread("noisy.jpg")

# ksize 必须是大于 1 的奇数
clean = cv2.medianBlur(img, 3)      # 3x3，轻度
strong = cv2.medianBlur(img, 5)     # 5x5，重度椒盐

cv2.imwrite("median3.png", clean)
cv2.imwrite("median5.png", strong)''',
      '''import numpy as np
import cv2


def my_median_blur(img, ksize):
    """手写中值滤波（灰度图）。"""
    pad = ksize // 2
    padded = np.pad(img, pad, mode="edge")
    h, w = img.shape
    out = np.zeros_like(img)
    for y in range(h):
        for x in range(w):
            window = padded[y:y + ksize, x:x + ksize]
            out[y, x] = np.median(window)
    return out.astype(np.uint8)


img = cv2.imread("noisy.jpg", cv2.IMREAD_GRAYSCALE)
clean = my_median_blur(img, 3)
print(clean.shape)''',
      "彩色图建议先在合适色彩空间处理，或确认对三通道分别中值是否可接受；对椒盐噪声 ksize=3 通常已足够。",
      [("ksize", "邻域窗口边长（奇数>1）", "3"), ("img", "输入图像", "8 位单通道或三通道")],
      [
          ("ksize 传偶数或 1", "OpenCV 要求 ksize 为大于 1 的奇数，传 4 或 1 会直接报错。", "椒盐去噪从 3 起步；确实要更大就用 5。"),
          ("把细线当噪声删掉", "笔画宽 2 像素而核是 5×5，细线会被整个吃掉。", "核不超过最细目标宽度的一半；或减少到 3。"),
          ("指望它去高斯噪声", "中值对连续噪声无优势，甚至不如高斯。", "高斯噪声用 GaussianBlur，脉冲噪声才用 medianBlur。"),
          ("彩色图直接三通道中值", "某些实现按通道独立取中值可能产生色偏。", "先转 HSV/Lab 只对亮度通道滤波，或改用双边滤波。"),
      ],
      "黑白点用中值、3×3 起步、超过 5 就伤线条；高斯噪声请换高斯滤波。",
      [("ksize", "邻域窗口", "3", "更狠去噪但伤细节", "更保细节但去噪弱"),
       ("ksize（上限）", "最大窗口", "5", "细线消失", "残留噪声")],
      [("清二值图", "先 medianBlur 3 再去形态学开运算，能把二值图里的孤立小白点清得干干净净。"),
       ("和形态学组合", "中值去点、形态学去毛刺，是工业缺陷检测的经典双人组。"),
       ("扫描件去噪", "扫描文档用 medianBlur(3) 效果最好，字迹几乎无损。")],
      [("640×480 灰度，ksize=3", "≈3 ms", "排序实现，未做直方图优化"),
       ("640×480 灰度，ksize=5", "≈8 ms", "窗口变大，耗时上升"),
       ("1920×1080 灰度，ksize=5", "≈40 ms", "高分辨率下建议先降采样")],
      )


# ================================================================
# 3. 霍夫圆变换
# ================================================================
m = {
    "name": "霍夫圆变换", "en": "Hough Circle Transform", "year": "1972",
    "author": "Richard Duda / Peter Hart",
    "paperUrl": "https://ieeexplore.ieee.org/document/4310039",
    "chapter": "第4章 · 基元检测", "chapterLink": "/chapters/ch04-primitives",
    "branch": "特征检测", "level": "中级",
    "tagline": "给每个边缘点投一票，票数最高的圆心就是真圆",
    "analogy": "想象一群萤火虫在黑暗里飞成一个圆。每只萤火虫都说「我在圆上」，于是每只都在纸上以自己为圆心、按可能半径画一圈虚线。所有虚线交汇最多的那个点，就是真正的圆心——霍夫变换就是「集体投票定圆心」。",
    "scene": "硬币/零件计数、虹膜定位、仪表盘指针圆盘、交通标志检测、细胞计数",
    "pros": ["对噪声、遮挡、边缘不连续鲁棒", "无需先分割就能直接检测", "能同时给出圆心与半径", "对部分遮挡仍有效"],
    "cons": ["参数（dp/minDist/两阈值）敏感难调", "内存/时间随图像与半径范围增长", "同心圆、重叠圆易误检", "对椭圆无效（需推广到 Hough 椭圆）"],
    "dep_pre": "Canny 边缘检测、高斯去噪", "dep_peer": "霍夫直线变换、轮廓拟合",
    "dep_post": "圆心排序、计数统计、姿态估计",
    "anchor": "记住「霍夫圆是三维投票（a, b, r），靠梯度信息把三维降到二维」。",
    "params_arch": [
        ("dp", "累加器分辨率倒数", "1", "1.0", "**1.2~1.5**（提速）"),
        ("minDist", "圆心间最小距离", "—", "图像高度/8", "按目标间距设"),
        ("param1", "Canny 高阈值", "—", "100", "按边缘质量 50~200"),
        ("param2", "圆心累加阈值", "—", "100", "**越小越灵敏、易误检**"),
        ("minRadius", "最小半径", "—", "0", "按目标约束收紧"),
        ("maxRadius", "最大半径", "—", "0", "**一定要填，否则极慢**"),
    ],
    "failmodes": [
        ("不限制半径导致奇慢", "minRadius/maxRadius 留 0 会让搜索范围爆炸，1080p 图可能跑几秒。"),
        ("param2 太小", "圆心阈值过低会把噪声聚成一堆假圆。"),
        ("同心圆只检出一个", "多个圆共用圆心时，minDist 会把其余圆抑制掉。"),
        ("边缘断裂检不出", "圆被遮挡超过一半时投票不足，检测失败。"),
    ],
}
build("hough-circles", m,
      "让每个边缘点沿着它的梯度方向为可能的圆心投票，票数超过阈值就是圆。",
      "霍夫直线检测只能找直线，现实里硬币、轮子、细胞都是圆的。霍夫圆变换把「投票」思路推广到三维参数空间，是**传统 CV 里检测圆形目标最经典的手段**，也是工业计数的常用武器。",
      "工厂流水线上要数零件个数：一片工件的图像里散落着几十个垫圈。用霍夫圆变换，每个垫圈的圆心和半径都被找出来，计数一秒钟完成。",
      ["搞懂「参数空间投票」的直觉，不再怕三维累加器", "理解梯度信息如何把三维搜索降到二维", "掌握 dp / param1 / param2 三个关键参数的调法", "抄一段能直接跑硬币检测的代码", "避开半径不限制、param2 太小等坑", "会和霍夫直线对比选型"],
      {
          "title": "Use of the Hough Transformation to Detect Lines and Curves in Pictures",
          "venue": "Communications of the ACM, 1972",
          "oneline": "提出用参数空间累加投票的方式检测直线与曲线，把圆检测变成三维峰值搜索。",
          "problem": "1962 年 Paul Hough 提出用参数空间投票检测直线，但难以推广到圆等复杂曲线；直接用三点定圆再验证的计算量又太大。",
          "idea": "把图像中「共圆的一群点」映射到参数空间「同一个 (a,b,r)」，让它们在那里叠加投票。票数高的参数组合就是图像中的真圆。再用边缘梯度方向把搜索范围缩小，避免三维遍历。",
          "idea_flow": "flowchart LR\n  A[\"边缘点(x,y)\"] --> B[\"按梯度方向枚举圆心(a,b)\"]\n  B --> C[\"参数空间累加\"]\n  C --> D[\"找峰值 -> 圆\"]",
          "contrib": "- 把霍夫变换从直线推广到任意解析曲线\n- 引入**梯度方向约束**，把圆的参数搜索从三维降到二维\n- 提出累加器阈值决定「多少票算一个圆」",
          "formula": "圆方程 (x−a)² + (y−b)² = r²。边缘点梯度方向指向圆心，故圆心位于 (x − r·cosθ, y − r·sinθ)，θ 为梯度方向——只需遍历 r，a、b 直接算出。",
          "experiment": "在手绘与实拍含圆图像上，配合 Canny 边缘，霍夫圆对噪声与部分遮挡表现稳健，检测率显著优于「先分割再拟合」。",
          "limit": "参数敏感、内存大；同心圆难分离；对椭圆、非圆曲线需另行推广；精度受累加器量化影响。",
          "influence": "成为圆形目标检测的教科书方法，广泛用于硬币/细胞/虹膜/仪表检测；后续又衍生出随机霍夫变换、霍夫椭圆、广义霍夫变换（用于任意形状模板匹配）。",
          "summary": "「众人投票」四个字，撑起了传统 CV 检测几何图形的半壁江山。",
      },
      [
          ("参数空间与投票", "图像空间里一条直线上的无数点，在参数空间里对应同一个参数点。霍夫变换就是把「找形状」变成「找票数峰值」。", "flowchart LR\n  A[\"图像空间：点\"] --> B[\"参数空间：线\"]\n  B --> C[\"交点=峰=形状\"]"),
          ("圆的参数空间是三维的", "圆心 (a, b) 加半径 r 共三个参数，理论上要建三维累加器，内存和耗时都大。", None),
          ("梯度方向降维", "圆的边缘梯度方向恰好指向圆心。知道方向和半径，圆心唯一确定——于是三维降到「只遍历半径」的二维。", "flowchart LR\n  A[\"边缘点+梯度方向\"] --> B[\"给定r -> 圆心唯一\"]"),
          ("累加器阈值", "param2 就是「多少票才算圆」。票多=真圆，票少=噪声。它是灵敏度和误检率的总开关。", None),
      ],
      [("灰度 + 高斯去噪", "去噪能显著减少伪边缘，霍夫圆对噪声很敏感，前置去噪几乎是必须的。"),
       ("限制半径范围", "根据目标实际大小给出 minRadius/maxRadius，既提速又大幅减少误检。"),
       ("Canny + 累加投票", "内部先做 Canny，再让边缘点沿梯度方向为圆心投票。"),
       ("按票数提取峰值", "累加器中超过 param2 的局部峰值即为检出的圆。")],
      "时间复杂度与图像尺寸、半径搜索范围、dp 密切相关，通常 O(W·H·n_r)；空间复杂度即累加器大小 O(W/authH/r_range)。",
      '''import cv2
import numpy as np

img = cv2.imread("coins.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 5)          # 去噪，霍夫圆对噪声敏感

circles = cv2.HoughCircles(
    gray,
    cv2.HOUGH_GRADIENT,
    dp=1.2,          # 累加器分辨率倒数
    minDist=30,      # 圆心最小间距
    param1=100,      # Canny 高阈值
    param2=30,       # 圆心累加阈值（越小越灵敏）
    minRadius=10,
    maxRadius=80,    # 一定要给上限，否则很慢
)

if circles is not None:
    circles = np.uint16(np.around(circles))
    for c in circles[0, :]:
        cv2.circle(img, (c[0], c[1]), c[2], (0, 255, 0), 2)
        cv2.circle(img, (c[0], c[1]), 2, (0, 0, 255), 3)

cv2.imwrite("circles.png", img)''',
      '''import numpy as np
import cv2

# 手写「梯度方向投票」版霍夫圆（简化，仅示意）
img = cv2.imread("coins.jpg", cv2.IMREAD_GRAYSCALE)
edges = cv2.Canny(img, 100, 200)
gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)
ys, xs = np.nonzero(edges)
acc = np.zeros(img.shape, np.uint16)

r_min, r_max = 10, 80
for r in range(r_min, r_max, 2):
    for y, x in zip(ys, xs):
        n = np.hypot(gx[y, x], gy[y, x])
        if n < 1:
            continue
        a = int(x - r * gx[y, x] / n)   # 沿梯度方向走 r
        b = int(y - r * gy[y, x] / n)
        if 0 <= a < img.shape[1] and 0 <= b < img.shape[0]:
            acc[b, a] += 1

y0, x0 = np.unravel_index(np.argmax(acc), acc.shape)
print("投票最高的圆心:", (x0, y0), "票数:", acc[y0, x0])''',
      "OpenCV 的 HOUGH_GRADIENT 已用梯度信息做了降维，但 minRadius/maxRadius 必须限制，否则自增半径搜索会非常慢。",
      [("dp", "累加器分辨率的倒数", "1.2"), ("minDist", "圆心之间的最小距离", "图高/8"), ("param1", "Canny 高阈值", "100"), ("param2", "圆心累加阈值", "30（硬币）"), ("minRadius/maxRadius", "半径范围", "按目标给定")],
      [
          ("半径范围留空 = 卡死", "minRadius=maxRadius=0 时 OpenCV 会遍历很大范围，1080p 图可能几秒才返回。", "务必根据目标实际尺寸填 minRadius/maxRadius。"),
          ("param2 调太小", "圆心阈值过低，噪声点聚成假圆，检出几百个。", "param2 从 30 起步，逐步加大直到误检消失。"),
          ("去噪不充分", "边缘图里满是噪点边缘，投票被污染。", "前置 medianBlur(5) 或 GaussianBlur，再进 HoughCircles。"),
          ("同心圆只剩一个", "minDist 把同一圆心附近的其他半径圆抑制掉了。", "需要检测同心圆时降到 minDist 并缩小半径范围分批检测。"),
      ],
      "先限半径、再去噪、param2 由小到大扫——票数够才算圆。",
      [("dp", "累加器精度", "1.2", "更快更粗", "更慢更准"),
       ("minDist", "圆心最小间距", "30", "重叠圆被抑制", "易出现重复圆"),
       ("param2", "圆心阈值", "30", "误检减少", "漏检增加"),
       ("param1", "Canny 高阈值", "100", "边缘减少", "噪声边缘增加")],
      [("先粗后精", "先用小图快速定位大致圆，再在原图局部做精修，兼顾速度与精度。"),
       ("半径范围二分", "不确定半径时，可先跑一个很宽的范围看都检出什么，再收紧。"),
       ("和轮廓法互补", "轮廓完整、无遮挡时用 fitEllipse/最小外接圆更快；遮挡严重时才上霍夫。")],
      [("640×480，半径 10~80", "≈25 ms", "dp=1.2，约 36 个半径档"),
       ("1920×1080，半径 10~80", "≈180 ms", "分辨率高，投票基数大"),
       ("1920×1080，半径不限", ">2 s", "反面教材：必须限制半径")],
      )


# ================================================================
# 4. 轮廓拟合
# ================================================================
m = {
    "name": "轮廓拟合与多边形逼近", "en": "Contour Fitting & Polygon Approximation", "year": "1973",
    "author": "Urs Ramer / David Douglas / Thomas Peucker；椭圆拟合见 Fitzgibbon 1996",
    "paperUrl": "https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm",
    "chapter": "第8章 · 形状分析", "chapterLink": "/chapters/ch08-shape",
    "branch": "图像处理", "level": "基础",
    "tagline": "把一坨几百个点的轮廓，压成几条线、一个圆或一个椭圆",
    "analogy": "你沿着一个不规则湖岸走了 500 步，记下每步的位置。要跟别人描述这个湖，你不会报 500 个坐标，而会说「大概是个椭圆，长轴 3 公里」。轮廓拟合就是干这个——用最少的参数概括轮廓的形状。",
    "scene": "工业零件尺寸测量、车牌/纸面矫正、形状分类、手写笔迹简化、地图边界压缩",
    "pros": ["用极少参数描述形状（压缩）", "抗噪（拟合容忍离群点）", "直接给出几何量（周长/角度/长短轴）", "计算快，适合实时检测"],
    "cons": ["epsilon 太大会丢角点", "椭圆拟合对离群点敏感（需鲁棒版）", "只对单连通轮廓有效", "对凹形/复杂形状表达能力有限"],
    "dep_pre": "二值化、边缘/轮廓提取（findContours）", "dep_peer": "霍夫变换、最小外接矩形",
    "dep_post": "形状匹配、缺陷判定、尺寸测量",
    "anchor": "记住「epsilon 是逼近精度，等于轮廓周长的百分比——越小越贴着原形」。",
    "params_arch": [
        ("epsilon", "多边形逼近精度", "周长 1%", "0.02", "**0.01~0.02×周长**"),
        ("closed", "轮廓是否闭合", "True", "True", "按形状定"),
        ("method", "拟合方式", "—", "CHAIN_APPROX_SIMPLE", "CHAIN_APPROX_NONE"),
        ("robust", "椭圆是否鲁棒拟合", "—", "False", "噪声大时 True"),
    ],
    "failmodes": [
        ("epsilon 过大丢角点", "逼近精度太粗，正方形的角被磨圆。"),
        ("对断裂轮廓拟合失败", "fitEllipse 需要至少 5 个点，点太少或不封闭会报错。"),
        ("离群点拉偏椭圆", "普通最小二乘拟合对少量远点极敏感，椭圆被拽歪。"),
        ("把非闭合轮廓当闭合", "closed 参数写错会让首尾被强行连起来。"),
    ],
}
build("contour-fitting", m,
      "用少量参数（几条直线段、一个圆或椭圆）去近似一条由大量像素点组成的轮廓。",
      "findContours 给你的是成百上千个像素点，没法直接用。要测尺寸、判形状、做分类，就得把轮廓**抽象成几何量**。多边形逼近、最小外接圆、椭圆拟合就是这套「从点集到形状」的工具箱。",
      "质检线上要判断螺母是不是圆的、螺栓有没有变形。把轮廓拟合出椭圆，比一下长短轴之比，一个比值就能判定合格与否。",
      ["搞懂 Douglas-Peucker 逼近算法怎么「扔点」", "分清 approxPolyDP / fitEllipse / minEnclosingCircle 各用在哪", "理解 epsilon 与形状保真度的取舍", "抄一段从轮廓到几何量的完整代码", "避开丢角点、离群点拉偏等坑", "会用拟合结果做形状分类"],
      {
          "title": "An Algorithm for the Reduction of the Number of Points Required to Represent a Line or its Caricature",
          "venue": "Ramer (1972) / Douglas & Peucker (1973), Cartographica",
          "oneline": "提出递归删点算法，用最少的点近似折线，误差可控。",
          "problem": "地图制图与计算机图形中，曲线由海量点表示，存储和计算都昂贵；需要一种「保留形状、删掉冗余点」的算法。",
          "idea": "对一条折线，连接首尾成直线，找离这条直线最远的点。若该距离小于阈值 epsilon，则整段用这条直线代替；否则在该点处断开，递归处理两段。",
          "idea_flow": "flowchart TB\n  A[\"连接首尾\"] --> B[\"找最远点\"]\n  B --> C{\"距离>epsilon?\"}\n  C -- 是 --> D[\"从该点断开，递归\"]\n  C -- 否 --> E[\"整段变直线\"]",
          "contrib": "- 提出带误差上界的折线简化算法（DP 算法）\n- 保证简化结果与原曲线的最大偏差不超过 epsilon\n- 成为计算几何与制图的经典算法",
          "formula": "设某段首尾为 P1、Pn。求点 Pk 到直线 P1Pn 的距离 d_max。若 d_max ≤ ε，则该段用 P1Pn 近似；否则在 Pk 处分割递归。",
          "experiment": "在海岸线等复杂曲线上，epsilon 取 1% 周长即可把点数压掉 90% 以上，形状偏差肉眼几乎不可辨。",
          "limit": "只保证单段误差上界，整体不能保证最优点数（贪心）；对闭合轮廓需特殊处理首尾衔接。",
          "influence": "成为 GIS、CAD、字体渲染里的标准曲线简化算法；OpenCV 的 approxPolyDP 直接实现它，是形状分析第一站。",
          "summary": "一个递归「扔点」的小算法，成了所有轮廓简化的默认起点。",
      },
      [
          ("Douglas-Peucker 逼近", "先连首尾成线，找最远的点，距离超过 epsilon 就在那里断开递归。相当于「只要弯曲程度不大就一笔带过」。", "flowchart TB\n  A[\"连首尾\"] --> B[\"找最远点\"] --> C{\"超阈值?\"}"),
          ("最小外接矩形 vs 外接圆", "minAreaRect 给旋转矩形，minEnclosingCircle 给最小圆。前者适合方件，后者适合圆件或粗判位置。", None),
          ("椭圆拟合（Fitzgibbon 直接最小二乘）", "用 5 个参数（中心、长短轴、旋转角）描述一个椭圆，比矩形更能表达「圆但不正」的形状。", "flowchart LR\n  A[\"轮廓点集\"] --> B[\"最小二乘\"] --> C[\"(a,b,rx,ry,θ)\"]"),
          ("拟合的鲁棒性问题", "普通最小二乘对离群点极敏感，少量远点就能把椭圆拽歪；噪声大时要用 RANSAC 版拟合。", None),
      ],
      [("提取轮廓", "先二值化，再用 findContours 得到每条轮廓的点集。"),
       ("计算逼近精度", "epsilon 一般取轮廓周长的 1%~2%，保证不丢关键角点。"),
       ("调用拟合函数", "按需求选 approxPolyDP（多边形）、fitEllipse（椭圆）、minAreaRect（矩形）。"),
       ("提取几何量", "从拟合结果读出顶点数、角度、长短轴、中心，供分类与测量使用。")],
      "时间复杂度：Douglas-Peucker 平均 O(n log n)，最坏 O(n²)；椭圆拟合为 O(n) 的最小二乘。空间复杂度 O(n)。",
      '''import cv2
import numpy as np

img = cv2.imread("parts.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    if cv2.contourArea(cnt) < 100:
        continue
    # 1) 多边形逼近：epsilon 取周长的 2%
    eps = 0.02 * cv2.arcLength(cnt, True)
    poly = cv2.approxPolyDP(cnt, eps, True)

    # 2) 最小外接矩形（带旋转）
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect).astype(int)

    # 3) 椭圆拟合（需要 >=5 点）
    if len(cnt) >= 5:
        ellipse = cv2.fitEllipse(cnt)

    cv2.drawContours(img, [poly], -1, (0, 255, 0), 2)
    cv2.drawContours(img, [box], -1, (255, 0, 0), 1)
    if len(cnt) >= 5:
        cv2.ellipse(img, ellipse, (0, 0, 255), 2)

cv2.imwrite("fitted.png", img)''',
      '''import numpy as np
import cv2


def rdp(points, epsilon):
    """手写 Douglas-Peucker 折线简化。points: (N,2) 数组。"""
    if len(points) < 3:
        return points
    p0, p1 = points[0], points[-1]
    line = p1 - p0
    norm = np.linalg.norm(line)
    if norm == 0:
        d = np.linalg.norm(points - p0, axis=1)
    else:
        d = np.abs(np.cross(line, points - p0)) / norm
    idx = np.argmax(d)
    if d[idx] > epsilon:
        left = rdp(points[:idx + 1], epsilon)
        right = rdp(points[idx:], epsilon)
        return np.vstack([left[:-1], right])
    return np.array([p0, p1])


cnt = cv2.findContours(cv2.Canny(cv2.imread("parts.jpg", 0), 50, 150),
                       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0][0]
pts = cnt.reshape(-1, 2).astype(np.float64)
simp = rdp(pts, epsilon=0.02 * cv2.arcLength(cnt, True))
print("原始点数:", len(pts), "-> 简化后:", len(simp))''',
      "approxPolyDP 要求输入为闭合曲线时 closed=True；fitEllipse 至少需要 5 个点，少于 5 点会抛异常。",
      [("epsilon", "多边形逼近精度（越大越简）", "0.01~0.02×周长"), ("closed", "轮廓是否闭合", "True"), ("minAreaRect", "最小外接旋转矩形", "(center, size, angle)"), ("fitEllipse", "最小二乘椭圆", "需≥5点")],
      [
          ("epsilon 设成绝对值", "epsilon 是长度，与图像分辨率强相关，写死 5 像素在不同分辨率下效果天差地别。", "始终用「周长的百分比」来算 epsilon。"),
          ("正方形被磨圆", "epsilon 取到周长 5%，方角被当噪声砍掉。", "降到 1%~2%，或改用 approxPolyDP 后检测顶点数。"),
          ("椭圆被离群点拽歪", "边缘有毛刺或少量远点时，普通 fitEllipse 结果离谱。", "先平滑轮廓，或用 RANSAC 版椭圆拟合。"),
          ("点太少直接报错", "轮廓面积太小、点数不足 5，fitEllipse 抛异常。", "先用 contourArea 过滤小轮廓，再判断 len(cnt)>=5。"),
      ],
      "epsilon 用周长百分比、方件看顶点数、圆件用椭圆、噪声大就上 RANSAC。",
      [("epsilon", "逼近精度", "周长 1%~2%", "更简，丢角点", "更细，点多"),
       ("closed", "是否闭合", "True", "强行连首尾", "断成折线"),
       ("method", "轮廓存储方式", "SIMPLE", "记全部点", "只记拐点，更快")],
      [("形状分类套路", "先 approxPolyDP，若逼近成 4 点判为矩形、3 点判三角、点数很多再判圆。"),
       ("和面积配合", "用 contourArea / minAreaRect 面积之比判断「矩形度」，比值接近 1 说明是规整矩形。"),
       ("尺寸测量", "minAreaRect 的 size 直接给出长宽（像素），配合标定比例尺即可换算实际尺寸。")],
      [("单条 500 点轮廓，epsilon=1%", "≈0.05 ms", "Douglas-Peucker 极快"),
       ("1000 条轮廓批量逼近", "≈20 ms", "工业质检常见规模"),
       ("fitEllipse 单条轮廓", "≈0.02 ms", "最小二乘，点越多略微变慢")],
      )


# ================================================================
# 5. FREAK 描述子
# ================================================================
m = {
    "name": "FREAK 描述子", "en": "Fast Retina Keypoint", "year": "2012",
    "author": "Alexandre Alahi / Raphael Ortiz / Pierre Vandergheynst",
    "paperUrl": "https://ieeexplore.ieee.org/document/6247715",
    "chapter": "第4章 · 基元检测", "chapterLink": "/chapters/ch04-primitives",
    "branch": "特征检测", "level": "中级",
    "tagline": "模仿人眼视网膜的采样模式，用 512 位二进制串描述特征点",
    "analogy": "人眼看东西不是均匀扫描，而是中间清楚、周围模糊——视网膜的感光细胞分布就是「中心密、外围疏」。FREAK 照着这个规律摆了 43 个采样点，越靠中心越密，然后比较一堆像「眼睛」一样的感受野亮度差，拼成一串 0/1。",
    "scene": "移动端/嵌入式实时匹配、AR、物体识别，在算力受限设备上替代 SIFT/SURF",
    "pros": ["512 位二进制，匹配用汉明距离极快", "采样模式仿生，比 BRIEF 更鲁棒", "自带粗到细的级联匹配（先比前面几位）", "计算量小，适合移动端"],
    "cons": ["不具备尺度不变性（需配金字塔）", "旋转不变性靠估计方向，不如 ORB 稳", "对视角变化较敏感", "OpenCV 中不如 ORB 常用"],
    "dep_pre": "特征点检测（FAST/AGAST）+ 金字塔", "dep_peer": "BRIEF、ORB、BRISK",
    "dep_post": "汉明距离匹配、RANSAC 几何验证",
    "anchor": "记住「FREAK = 仿生采样模式 + 512 位二进制 + 粗到细级联匹配」。",
    "params_arch": [
        ("patternScale", "采样模式缩放", "1.0", "22.0", "**按图像尺度调**"),
        ("orientationNormalized", "是否估计方向", "True", "True", "True"),
        ("scaleNormalized", "是否尺度归一", "True", "True", "True"),
        ("nOctaves", "尺度金字塔层数", "4", "4", "4"),
    ],
    "failmodes": [
        ("把 FREAK 当检测器用", "FREAK 只是描述子，必须先有特征点位置。"),
        ("patternScale 不匹配", "采样模式半径与图像尺度不适配，匹配率骤降。"),
        ("跨尺度匹配直接失败", "不配金字塔时，不同尺度的同一目标匹配不上。"),
        ("用浮点距离匹配", "二进制描述子必须用汉明距离，用欧氏距离毫无意义。"),
    ],
}
build("freak", m,
      "在特征点周围按「中心密、外围疏」的仿生模式采样，比较采样点对亮度，输出 512 位 0/1 串。",
      "SIFT/SURF 描述子精度高但要算浮点直方图、慢；BRIEF 快但不抗旋转。FREAK 想同时拿下「快」和「稳」——它用仿生采样模式 + 二进制编码，在移动端也能实时跑匹配。",
      "你用手机做 AR 应用，要实时认出画面里的海报。手机算力有限，跑不动 SIFT。FREAK 用 512 位二进制串描述特征点，一个异或指令就能比对，实时匹配毫无压力。",
      ["搞懂「仿生视网膜采样」为什么比均匀采样好", "理解二进制描述子与汉明距离的匹配机制", "知道 FREAK 与 BRIEF/ORB/BRISK 的取舍", "抄一段特征点匹配的可跑代码", "避开「把描述子当检测器」等坑", "会调 patternScale 适配尺度"],
      {
          "title": "FREAK: Fast Retina Keypoint",
          "venue": "CVPR 2012",
          "oneline": "模仿人眼视网膜感受野的采样模式，生成 512 位二进制描述子，匹配又快又稳。",
          "problem": "SIFT/SURF 精度高但计算重，移动端跑不动；BRIEF 快但不具备旋转不变性，视角一变就匹配失败。需要在算力受限设备上兼顾速度与鲁棒性。",
          "idea": "向生物视觉学习：视网膜中央凹（fovea）感光细胞密集、外围稀疏。FREAK 照此布置采样点，中心密、外围疏，再用不同大小的感受野做亮度比较，得到一串二进制码。匹配时从最高位的「粗信息」开始比，能快速排除不匹配的候选。",
          "idea_flow": "flowchart LR\n  A[\"仿生采样模式\"] --> B[\"感受野亮度比较\"]\n  B --> C[\"512位二进制描述子\"]\n  C --> D[\"汉明距离匹配\"]",
          "contrib": "- 提出**仿生视网膜采样模式**，中心密外围疏\n- 提出用感受野对（Receptive Field）亮度比较生成二进制码\n- 提出**粗到细的级联匹配**：先比前 128 位，快速淘汰\n- 512 位描述子性能接近 SIFT，速度快一个数量级",
          "formula": "描述子第 k 位：F_k = 1 若 I(P_a^k) − I(P_b^k) > 0，否则 0。其中 P_a、P_b 为第 k 对感受野中心，I 为其高斯平滑后的强度。",
          "experiment": "在标准评估数据集上，FREAK 以约 1/10 于 SIFT 的计算量，达到相近的匹配召回率；级联匹配再提速约 2 倍。",
          "limit": "旋转不变性依赖方向估计，精度不如 ORB 稳定；不具备尺度不变性，必须配尺度金字塔；OpenCV 生态中普及度不及 ORB。",
          "influence": "推动了「仿生 + 二进制」描述子研究，与 BRISK、ORB 一同构成移动端特征匹配的主力；其级联匹配思想被后续诸多二进制描述子借鉴。",
          "summary": "把视网膜的采样规律翻译成代码，换来一个又快又稳的二进制描述子。",
      },
      [
          ("仿生采样模式", "43 个采样点按中心密、外围疏排列，模拟人眼视网膜。中心采样密保证精度，外围采样疏保证对形变宽容。", "flowchart LR\n  A[\"中心疏密分布\"] --> B[\"43个采样点\"]"),
          ("感受野与二进制码", "每对比两个采样区域的平滑亮度，前者亮记 1、后者亮记 0，512 对就是 512 位。", None),
          ("汉明距离匹配", "两个二进制描述子的差异用「不同的位数」衡量，一次异或加计数即可，极快。", "flowchart LR\n  A[\"desc A XOR desc B\"] --> B[\"统计 1 的个数\"] --> C[\"= 汉明距离\"]"),
          ("粗到细级联匹配", "描述子前几位代表最强特征（像眼睛、嘴这样的大结构）。先比这些位，不匹配的候选立刻淘汰，省下大量计算。", None),
      ],
      [("检测特征点", "先用 FAST/AGAST 在图像金字塔上找关键点，这是 FREAK 的输入。"),
       ("估计方向", "对关键点邻域求强度质心，得到主方向，使描述子具备旋转不变性。"),
       ("仿生采样编码", "按视网膜模式采样，逐对比较亮度，生成 512 位描述子。"),
       ("汉明距离匹配", "用汉明距离寻找最近邻，再用 RANSAC 做几何一致性验证。")],
      "时间复杂度 O(N·P)，N 为特征点数、P 为采样对数（512）；匹配为 O(N²·512/64) 位运算。空间复杂度 O(N×64) 字节。",
      '''import cv2

img1 = cv2.imread("scene1.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("scene2.jpg", cv2.IMREAD_GRAYSCALE)

# 1) 先检测特征点（FREAK 只做描述，不做检测）
detector = cv2.FastFeatureDetector_create(threshold=30)
kp1 = detector.detect(img1, None)
kp2 = detector.detect(img2, None)

# 2) FREAK 描述子
freak = cv2.xfeatures2d.FREAK_create(
    orientationNormalized=True,
    scaleNormalized=True,
    patternScale=22.0,
    nOctaves=4,
)
kp1, des1 = freak.compute(img1, kp1)
kp2, des2 = freak.compute(img2, kp2)

# 3) 二进制描述子 -> 汉明距离匹配
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = sorted(bf.match(des1, des2), key=lambda m: m.distance)
print("匹配数:", len(matches))''',
      '''import numpy as np
import cv2

# 手写：用 BRIEF 近似示意「采样对 + 二进制编码」的核心思想
img = cv2.imread("scene1.jpg", cv2.IMREAD_GRAYSCALE)
detector = cv2.FastFeatureDetector_create(30)
kp = detector.detect(img, None)

rng = np.random.default_rng(42)
pairs = rng.integers(-15, 15, size=(256, 2, 2))   # 256 对采样点
descriptors = []
for k in kp:
    x, y = int(k.pt[0]), int(k.pt[1])
    if x < 20 or y < 20 or x > img.shape[1] - 20 or y > img.shape[0] - 20:
        continue
    bits = []
    for (dx1, dy1), (dx2, dy2) in pairs:
        a = img[y + dy1, x + dx1]
        b = img[y + dy2, x + dx2]
        bits.append(1 if a > b else 0)
    descriptors.append(bits)

descriptors = np.array(descriptors, np.uint8)
print("描述子矩阵:", descriptors.shape)  # (N, 256)''',
      "FREAK 是描述子不是检测器，必须先用 FAST/AGAST/ORB 等检测关键点；匹配一律用 NORM_HAMMING。",
      [("patternScale", "采样模式缩放比例", "22.0"), ("orientationNormalized", "是否做方向归一", "True"), ("scaleNormalized", "是否做尺度归一", "True"), ("nOctaves", "金字塔层数", "4")],
      [
          ("直接对原图 compute", "有人以为 FREAK 能自己找点，其实必须先 detect 出关键点。", "先用 FastFeatureDetector 或 ORB 检测器拿到 kp。"),
          ("patternScale 乱设", "采样半径与图像尺度不匹配，导致描述子区分度差。", "图像大时适当放大 patternScale，小图用默认值。"),
          ("用欧氏距离匹配", "二进制描述子算欧氏距离没有任何意义。", "匹配器必须指定 cv2.NORM_HAMMING。"),
          ("忽略尺度金字塔", "跨尺度场景下不配金字塔，匹配几乎全军覆没。", "检测阶段就在金字塔上取点（ORB 检测器自带）。"),
      ],
      "FREAK 只描述不检测；二进制必配汉明距离；采样尺度要对上图像尺度。",
      [("patternScale", "采样模式尺度", "22.0", "视野更大、抗形变", "更精细但对尺度敏感"),
       ("orientationNormalized", "方向归一化", "True", "—", "发现旋转不变性丢失时改 True"),
       ("nOctaves", "金字塔层数", "4", "更强的尺度覆盖", "更快但尺度覆盖弱")],
      [("和 ORB 搭配", "用 ORB 检测器（自带方向与金字塔）出点，再用 FREAK 描述，往往比原生 ORB 描述子更稳。"),
       ("级联匹配提速", "先用短描述子粗筛，再对候选做完整汉明距离，能再快一倍。"),
       ("移动端部署", "FREAK 计算量小、描述子短，是 TensorFlow Lite 时代之前移动端匹配的首选之一。")],
      [("1000 个特征点，512 位", "≈8 ms", "单核，含采样与比较"),
       ("1000×1000 暴力汉明匹配", "≈15 ms", "含 crossCheck"),
       ("移动端 ARM（估）", "≈25 ms", "算力约为桌面 1/3")],
      )


# ================================================================
# 6. Felzenszwalb 图分割
# ================================================================
m = {
    "name": "Felzenszwalb 图分割", "en": "Felzenszwalb Graph Segmentation", "year": "2004",
    "author": "Pedro F. Felzenszwalb / Daniel P. Huttenlocher",
    "paperUrl": "https://cs.brown.edu/people/pfelzens/papers/seg-ijcv.pdf",
    "chapter": "第5章 · 目标分割", "chapterLink": "/chapters/ch05-segmentation",
    "branch": "图像分割", "level": "中级",
    "tagline": "把图像当成一张图，相邻像素连边，边太「弱」就断开——相邻区域合并成一个块",
    "analogy": "把每个像素看成一个村庄，相邻村庄之间修一条路，路的「难走程度」等于两村颜色的差异。一开始每个村独立成国，然后不断把「路好走」的相邻国家合并；只有当两个国家内部都很平整、边界却很陡时才停下来。最后剩下的一块块，就是分割区域。",
    "scene": "超像素分割、区域建议（R-CNN 的 selectivesearch 借鉴其思想）、图像简化、医学组织分区",
    "pros": ["速度接近线性，很快", "无需指定区域数量", "能用并查集高效实现", "对噪声不敏感（有最小区域约束）"],
    "cons": ["参数 k 控制区域大小，需调", "不追求边界精准", "对纹理复杂区域容易碎", "不含语义，只是颜色/亮度聚类"],
    "dep_pre": "高斯平滑（降噪）", "dep_peer": "SLIC 超像素、MeanShift、Watershed",
    "dep_post": "区域特征提取、selective search、目标候选生成",
    "anchor": "记住「k 越大区域越大越方，min_size 过滤碎块」。",
    "params_arch": [
        ("scale (k)", "合并阈值尺度", "—", "100", "**150~500（图越大越高）**"),
        ("sigma", "预处理高斯 σ", "0.8", "0.8", "0.8"),
        ("min_size", "最小区域大小", "—", "20", "按分辨率调，防碎块"),
        ("(输入)", "颜色空间", "RGB", "RGB", "Lab 更均匀"),
    ],
    "failmodes": [
        ("k 太小碎成一片", "合并阈值太低，图像被切得七零八落。"),
        ("min_size 不设", "出现大量 1~2 像素的小碎块。"),
        ("边界不贴真实边缘", "该算法侧重「区域一致性」而非像素级边界，需配合后处理。"),
        ("高纹理区域过分割", "草地、毛发等纹理区容易产生大量细碎区域。"),
    ],
}
build("felzenszwalb-segmentation", m,
      "在像素间按颜色差异建边，用「内部差异 vs 边界差异」准则决定相邻区域合并还是断开。",
      "聚类式分割（K-Means、MeanShift）要么得先定区域数，要么慢。Felzenszwalb 2004 的方法把分割变成**图上的贪心合并**，速度接近线性、无需预设区域数，还成了 R-CNN 目标检测里候选框生成的思想源头。",
      "你要给一张街景图生成「候选目标框」——先不管是什么，先把可能是一个物体的区域都框出来。Felzenszwalb 分割先把图切成几百个颜色一致的色块，再把这些块按相似度合并，就能得到大量候选框。",
      ["搞懂「内部差异 vs 边界差异」这条合并准则", "理解并查集如何让合并近线性完成", "掌握 scale / sigma / min_size 三个参数", "抄一段可直接跑的分割代码", "避开碎块、过分割等坑", "理解它和 R-CNN 的历史渊源"],
      {
          "title": "Efficient Graph-Based Image Segmentation",
          "venue": "IJCV 2004",
          "oneline": "提出基于图论的高效分割：用「区域内差异不大于区域间差异」作为合并判据，速度接近线性。",
          "problem": "当时的分割方法要么慢（如归一化割），要么需要预设区域数量，要么对参数极敏感，难以在大图上实用。",
          "idea": "把图像建成加权图，边权为相邻像素的颜色差。定义两个量：区域的**内部差异**（区域内最大边权）和**区域间差异**（两区域间最小边权）。若区域间差异明显大于任一侧内部差异，说明这是真正的边界，不合并；否则合并。",
          "idea_flow": "flowchart TB\n  A[\"按边权排序\"] --> B[\"取最小边\"]\n  B --> C{\"两区域差异 > 各自内部差异?\"}\n  C -- 否 --> D[\"合并\"]\n  C -- 是 --> E[\"保留边界\"]\n  D --> B",
          "contrib": "- 提出上述**合并判据**，用阈值函数 k/|C| 自适应控制\n- 用**并查集**实现，合并过程近线性\n- 引入 min_size 后处理，消除碎块\n- 成为 R-CNN 中 selective search 的基础分割",
          "formula": "合并判据：Diff(C1, C2) ≤ min( Int(C1) + τ(C1), Int(C2) + τ(C2) )，其中 τ(C) = k / |C|，|C| 为区域大小，k 为尺度参数。",
          "experiment": "在 Berkeley 分割数据集上，该方法以远快于当时主流方法的速度取得了有竞争力的分割质量，且实现只需几十行代码。",
          "limit": "侧重区域一致性，边界精度一般；对高纹理区域易过分割；参数 k 与图像尺寸强相关，需调。",
          "influence": "成为超像素/区域建议的经典方法，直接启发 selective search 与 R-CNN 的候选框生成；至今仍是 OpenCV 里 segmentation 模块和 scikit-image 的标准分割器。",
          "summary": "把分割变成「排序边 + 并查集合并」，用几十行代码换来近线性的速度。",
      },
      [
          ("把图像变成图", "每个像素是一个节点，相邻像素之间连一条边，边权是两像素的颜色（或亮度）差异。", "flowchart LR\n  A[\"像素=节点\"] --> B[\"邻接像素=边\"] --> C[\"颜色差=边权\"]"),
          ("内部差异 Int", "一个区域内所有边的最大权重，代表这个区域「内部有多不一致」。区域越均匀，Int 越小。", None),
          ("区域间差异 Diff", "两个相邻区域之间所有连边的最小权重，代表它们的「边界有多明显」。", None),
          ("合并判据与 τ", "当 Diff 不比两侧的 Int 大多少时合并。判据里加 τ = k/|C| 使小区域更容易合并，避免碎块。", "flowchart TB\n  A[\"Diff <= min(Int+τ)\"] --> B[\"合并\"]"),
      ],
      [("高斯平滑", "先对图像做 σ=0.8 的高斯滤波，抑制噪声，避免边权被噪声干扰。"),
       ("构建边集", "对 8 邻域像素建立边，边权为颜色差的范数，按权重升序排序。"),
       ("并查集合并", "从小到大遍历边，按合并判据决定是否合并两个区域。"),
       ("最小区域后处理", "把小于 min_size 的区域并入最相邻的大区域，消除碎块。")],
      "时间复杂度 O(E log E)，E 为边数（约 4W·H）；并查集合并近乎常数。空间复杂度 O(W·H)。",
      '''import cv2
import numpy as np

img = cv2.imread("street.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# OpenCV 的 ximgproc 提供 selecsearch 与 felzenszwalb（部分构建含）
seg = cv2.ximgproc.segmentation.createGraphSegmentation()
seg.setSigma(0.8)
seg.setK(300)          # 尺度参数 k，越大区域越大
seg.setMinSize(100)    # 最小区域，防碎块
segmented = seg.processImage(img)

# 给每个区域随机着色，直观可视化
rng = np.random.default_rng(0)
colors = rng.integers(0, 255, size=(segmented.max() + 1, 3), dtype=np.uint8)
vis = colors[segmented]
cv2.imwrite("seg.png", cv2.cvtColor(vis, cv2.COLOR_RGB2BGR))''',
      '''import numpy as np
import cv2


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def felzenszwalb(gray, k=300.0, min_size=50):
    h, w = gray.shape
    n = h * w
    dsu = DSU(n)
    int_diff = np.zeros(n)          # 每个区域内部差异
    size = np.ones(n, int)          # 每个区域大小

    # 建边并排序
    edges = []
    for y in range(h):
        for x in range(w):
            if x + 1 < w:
                edges.append((abs(int(gray[y, x]) - int(gray[y, x + 1])), y * w + x, y * w + x + 1))
            if y + 1 < h:
                edges.append((abs(int(gray[y, x]) - int(gray[y + 1, x])), y * w + x, (y + 1) * w + x))
    edges.sort()

    for wgt, a, b in edges:
        ra, rb = dsu.find(a), dsu.find(b)
        if ra == rb:
            continue
        tau = k / min(size[ra], size[rb])
        if wgt <= min(int_diff[ra] + tau, int_diff[rb] + tau):
            dsu.union(ra, rb)
            root = dsu.find(ra)
            size[root] = size[ra] + size[rb]
            int_diff[root] = max(int_diff[ra], int_diff[rb], wgt)

    labels = np.array([dsu.find(i) for i in range(n)]).reshape(h, w)
    return labels


gray = cv2.imread("street.jpg", 0)
lab = felzenszwalb(gray, k=300, min_size=50)
print("区域数:", len(np.unique(lab)))''',
      "OpenCV 中该算法位于 ximgproc（opencv-contrib），标准 pip 包需安装 opencv-contrib-python；或直接用 scikit-image 的 felzenszwalb。",
      [("k (scale)", "尺度参数，越大区域越大", "300"), ("sigma", "预处理高斯 σ", "0.8"), ("min_size", "最小区域尺寸", "50~100"), ("输入空间", "建议 Lab", "RGB/Lab")],
      [
          ("k 设太小", "区域阈值过低，图像被切成几百个碎块。", "从 k=100 起步逐级加大，直到区域数合理。"),
          ("忘记 min_size", "大量 1~2 像素的小区域混在结果里。", "min_size 按图像尺寸设，一般 20~100。"),
          ("直接上原图", "噪声会让边权抖动，影响合并。", "先做 σ=0.8 高斯平滑，论文默认如此。"),
          ("期望像素级边界", "该方法是区域级分割，边界不精确。", "需要精细边界时配合 GrabCut 或边缘引导滤波。"),
      ],
      "k 管大小、min_size 管碎块、sigma 先降噪；要区域多就调小 k。",
      [("k", "尺度参数", "300", "区域更大更少", "区域更小更多"),
       ("sigma", "平滑 σ", "0.8", "边界更平滑", "噪声残留"),
       ("min_size", "最小区域", "50", "碎块更少", "小目标被吞并")],
      [("生成候选框", "分割后把相邻且颜色相近的区域反复合并成「候选区域」，就是 selective search 的思路，可直接喂给检测器。"),
       ("和 SLIC 对比", "要颜色均匀的规则块用 SLIC；要贴合颜色边界的块用 Felzenszwalb。"),
       ("做图像简化", "把每个区域填入均值颜色，得到类似油画的简化效果，可用于艺术滤镜。")],
      [("640×480 灰度", "≈120 ms", "Python 实现边排序偏慢"),
       ("640×480（C++ 版）", "≈15 ms", "论文报道近线性"),
       ("1920×1080（C++ 版）", "≈80 ms", "与像素数近线性")],
      )


# ================================================================
# 7. KNN 背景建模
# ================================================================
m = {
    "name": "KNN 背景建模", "en": "K-Nearest Neighbors Background Subtraction", "year": "2006",
    "author": "Zoran Zivkovic / Ferdinand van der Heijden",
    "paperUrl": "https://ieeexplore.ieee.org/document/1640821",
    "chapter": "第11章 · 运动分析", "chapterLink": "/chapters/ch11-motion",
    "branch": "图像处理", "level": "中级",
    "tagline": "记住每个像素最近的 N 个历史颜色，新颜色离它们太远就判为前景",
    "analogy": "你家门口监控盯着一块地砖。这块砖最近见过 20 种“正常”颜色（晴天阴影、雨天湿、黄昏黄）。忽然来了一种谁都没见过的颜色——那多半是有东西停在那，报警！KNN 背景建模就是给每个像素存一小本“正常颜色账本”。",
    "scene": "监控运动检测、人流量统计、车辆计数、周界入侵报警（比 MOG2 更抗噪）",
    "pros": ["比 MOG2 抗噪、对缓慢光照变化更稳", "无需假设高斯分布（非参数）", "能处理多峰背景（如晃动的树叶）", "OpenCV 内置一行调用"],
    "cons": ["比 MOG2 慢", "内存占用更高（每像素存 N 个样本）", "参数（history/nSamples/dist2Threshold）需调", "对突然的全局光照突变会有短暂误检"],
    "dep_pre": "灰度化或降采样", "dep_peer": "MOG2、ViBe、帧差法",
    "dep_post": "形态学去噪、连通域分析、目标跟踪",
    "anchor": "记住「KNN 存历史样本，MOG2 存高斯——KNN 更稳更慢」。",
    "params_arch": [
        ("history", "历史帧数", "—", "500", "**200~500**"),
        ("nSamples", "每像素样本数", "20", "7", "**10~20**"),
        ("dist2Threshold", "样本距离平方阈值", "—", "400", "**越大越宽容**"),
        ("detectShadows", "是否检测阴影", "True", "True", "True"),
    ],
    "failmodes": [
        ("nSamples 设太大", "内存暴涨、变慢，收益却有限。"),
        ("dist2Threshold 太小", "少量光照波动就被判成前景，满屏噪点。"),
        ("未做形态学后处理", "前景掩码里全是胡椒面式噪点。"),
        ("相机自动曝光突变", "全局亮度跳变会造成整屏误检，需重学背景。"),
    ],
}
build("knn-background", m,
      "为每个像素保存最近 N 个历史颜色值，新像素若与其中多数样本都「离得远」，判为前景。",
      "视频监控的第一步永远是「把动的从不动里分出来」。帧差法太简陋、MOG2 用高斯假设又在晃动树叶前失灵。KNN 背景建模用**非参数**方式存历史样本，对多峰背景与噪声更宽容，是监控场景的稳健选择。",
      "小区监控摄像头对着一个门口。白天有阳光、夜晚有路灯、下雨地面反光——同一个像素的背景颜色一直在变。KNN 给每个像素存了 20 个历史颜色，这些变化全被记住，于是只有真正出现的人影才会被报警。",
      ["搞懂「非参数背景建模」和 MOG2 高斯假设的区别", "理解为什么要给每个像素存多个历史样本", "掌握 history / nSamples / dist2Threshold 的调法", "抄一段能直接跑的运动检测代码", "避开内存、噪点、光照突变等坑", "会和 MOG2 / 帧差法对比选型"],
      {
          "title": "Efficient Adaptive Density Estimation per Image Pixel for the Task of Background Subtraction",
          "venue": "Pattern Recognition Letters, 2006",
          "oneline": "为每个像素维护一组最近样本，用非参数密度估计判断前景，比高斯混合更稳健。",
          "problem": "GMM（MOG2）假设背景像素服从高斯混合分布，但真实场景（树叶晃动、水面波纹）背景是多峰且非高斯的，高斯假设下要么误检要么漏检，且参数估计开销大。",
          "idea": "干脆不做分布假设：给每个像素直接存最近观察到的 N 个颜色样本，用「新像素与多少样本足够接近」来估计它是否属于背景。样本足够近就直接替换最老的样本，实现自适应更新。",
          "idea_flow": "flowchart LR\n  A[\"每像素存N个历史样本\"] --> B[\"新像素与样本比较\"]\n  B --> C{\"距样本够近?\"}\n  C -- 是 --> D[\"背景，更新样本\"]\n  C -- 否 --> E[\"前景\"]",
          "contrib": "- 提出**每像素非参数密度估计**的背景建模\n- 用简单样本替换策略实现自适应与有限内存\n- 证明在含噪声与多峰背景的监控场景优于 GMM",
          "formula": "若新像素值与 N 个历史样本中至少有 k 个的距离平方小于阈值 R，则判为背景，并用该值随机替换一个旧样本；否则判为前景。",
          "experiment": "在含严重噪声与动态背景的监控视频上，KNN 的误检率显著低于 MOG2，代价是速度慢约 2~3 倍、内存更高。",
          "limit": "速度与内存开销大于 MOG2；对全局光照突变需要重新收敛；参数对场景敏感。",
          "influence": "与 MOG2 一起成为 OpenCV 背景减除的两大内置方法；其「样本替换」思想直接影响了 ViBe、PBAS 等后续算法。",
          "summary": "不给背景做分布假设，直接存样本——换来一个更抗噪的运动检测器。",
      },
      [
          ("什么是背景建模", "摄像头不动时，画面里不动的部分是背景，动的是前景。背景建模就是给每个像素学出「正常长什么样」。", None),
          ("非参数 vs 参数", "MOG2 先假设背景服从高斯混合、再估参数；KNN 直接存样本，不假设任何分布。多峰背景更适合后者。", "flowchart LR\n  A[\"MOG2: 高斯假设\"] --> B[\"多峰时失效\"]\n  C[\"KNN: 存样本\"] --> D[\"任意分布\"]"),
          ("样本替换与自适应", "新样本若判为背景，就随机替换掉一个旧样本。这样背景随时间缓慢漂移（光照变化）也能跟上。", None),
          ("阴影检测", "阴影会让像素变暗但不改变色度，OpenCV 用色度信息把阴影标成灰色（127）而非纯白前景。", None),
      ],
      [("初始化背景模型", "用前若干帧填充每个像素的样本库，或用第一帧复制。"),
       ("逐帧比对", "新帧每个像素与自己的样本库比距离，统计足够近的样本个数。"),
       ("判定与更新", "近距离样本够多则判背景并替换旧样本，否则判前景。"),
       ("后处理", "形态学开闭运算去噪，连通域分析过滤小目标获得最终前景。")],
      "时间复杂度 O(W·H·nSamples) 每帧；空间复杂度 O(W·H·nSamples)，nSamples=20、1080p 时约需数百 MB。",
      '''import cv2

cap = cv2.VideoCapture("street.mp4")
knn = cv2.createBackgroundSubtractorKNN(
    history=500,
    dist2Threshold=400.0,
    detectShadows=True,
)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

while True:
    ok, frame = cap.read()
    if not ok:
        break
    fg = knn.apply(frame)
    # 去掉阴影（阴影被标为 127），只保留确定前景（255）
    _, fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
    # 形态学去噪
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel)
    fg = cv2.dilate(fg, kernel, iterations=2)

    cv2.imshow("foreground", fg)
    if cv2.waitKey(30) == 27:
        break
cap.release()''',
      '''import numpy as np
import cv2

# 手写简化版：每像素存 nSamples 个样本，距离阈值判定
nSamples, dist2 = 10, 400.0
gray = cv2.cvtColor(cv2.imread("street.jpg"), cv2.COLOR_BGR2GRAY)

samples = np.repeat(gray[:, :, None], nSamples, axis=2).astype(np.int16)
rng = np.random.default_rng(0)

# 模拟新来的一帧（这里直接用同一张图加噪，示意判定流程）
new = gray.astype(np.int16) + rng.integers(-5, 6, gray.shape).astype(np.int16)
diff2 = (new[:, :, None] - samples) ** 2
close = (diff2 < dist2).sum(axis=2)

fg_mask = (close < 2).astype(np.uint8) * 255     # 近样本太少 -> 前景
print("前景像素数:", int((fg_mask > 0).sum()))''',
      "OpenCV 提供 createBackgroundSubtractorKNN（标准库）与 MOG2 两个内置方法；阴影像素值为 127，前景为 255。",
      [("history", "历史帧数", "500"), ("dist2Threshold", "距离平方阈值", "400"), ("detectShadows", "检测阴影", "True"), ("nSamples", "每像素样本数（构造参数）", "7~20")],
      [
          ("忘记过滤阴影", "阴影像素值 127 被当成前景，目标旁边拖一条灰影。", "用 threshold(fg,200,255) 把非纯白像素滤掉。"),
          ("不做形态学后处理", "掩码里全是胡椒面噪点，无法用于后续分析。", "开运算去小噪点、膨胀连通目标。"),
          ("nSamples 设成 50", "内存与耗时陡增，效果却提升有限。", "10~20 足够，过高收益递减。"),
          ("光照突变不重学", "自动曝光突变导致整屏误检。", "检测到前景占比异常时重置背景模型。"),
      ],
      "KNN 比 MOG2 稳但更慢；history 管记忆长度、dist2Threshold 管宽容度。",
      [("history", "历史长度", "500", "记忆更长、更稳", "更快适应但易误检"),
       ("dist2Threshold", "距离阈值", "400", "更宽容、漏检增", "更敏感、噪声增"),
       ("detectShadows", "阴影检测", "True", "标出阴影", "阴影当前景")],
      [("和 MOG2 对比选型", "要快用 MOG2，要稳（树叶/水面）用 KNN。"),
       ("降采样提速", "先缩到 640×360 做检测，再把掩码放大回原图，速度提升明显。"),
       ("组合连通域", "检测出的前景掩码直接送 connectedComponentsWithStats，即可数人数、算面积。")],
      [("640×480，nSamples=7", "≈6 ms/帧", "KNN 检测"),
       ("640×480，MOG2 对照", "≈3 ms/帧", "MOG2 更快"),
       ("1920×1080，nSamples=7", "≈30 ms/帧", "高分辨率建议降采样")],
      )

print("批次 A 完成")
