# FAST 角点检测

<AlgorithmCard
  name="FAST 角点检测"
  enName="Features from Accelerated Segment Test"
  chapter="ch-8-local-feature"
  branch="feature-detection"
  year="2006"
  author="Edward Rosten / Tom Drummond"
  paper="—"
  level="mid"
  tagline="用一个圆圈 16 个邻居，一眼认出角点，速度比 Harris 快 10 倍"
  analogy="FAST 像一个哨兵：不进屋检查，只趴在窗户上数——窗外 16 个邻居里如果连续 12 个都比屋里亮或都比屋里暗，那这间房肯定是个「犄角旮旯」"
  scene="SLAM、AR、实时物体识别里做特征点检测，毫秒级返回几千个点，CPU 上就能跑 60fps"
  :pros='["速度极快（比 Harris 快 10 倍以上）", "实现简单", "角点重复率高", "OpenCV 高度优化"]'
  :cons='["不具备尺度不变性", "不具备旋转不变性", "阈值敏感", "需要 NMS", "不含描述子"]'
/>
## OpenCV 调用

### 基本调用

```python
import cv2

img = cv2.imread("test.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 创建 FAST 检测器
fast = cv2.FastFeatureDetector_create(
    threshold=20,                  # 亮度差阈值（越大点越少、越严格）
    nonmaxSuppression=True,        # 开 NMS（强烈建议 True）
    type=cv2.FAST_FEATURE_DETECTOR_TYPE_9_16  # FAST-9-16（默认）
)

# 检测
kp = fast.detect(gray, None)
print(f"检测到 {len(kp)} 个角点")

# 可视化
out = cv2.drawKeypoints(img, kp, None, color=(0, 0, 255))
cv2.imshow("FAST", out)
cv2.waitKey(0)
```

### 参数表

| 参数 | 含义 | 建议值 |
|---|---|---|
| `threshold` | 中心与邻居的亮度差阈值 | **10–30**；↓点多（有噪声），↑点少（漏检） |
| `nonmaxSuppression` | 非极大值抑制 | **True**（False 会出一堆扎堆点） |
| `type` | FAST 变种 | `TYPE_9_16`（推荐）、`TYPE_7_12`、`TYPE_5_8` |

### 常用变种枚举

```python
cv2.FAST_FEATURE_DETECTOR_TYPE_5_8     # FAST-5-8（最快）
cv2.FAST_FEATURE_DETECTOR_TYPE_7_12    # FAST-7-12
cv2.FAST_FEATURE_DETECTOR_TYPE_9_16    # FAST-9-16（默认推荐）
```

## NumPy 手写最小实现（FAST-12）

下面写一个简化但可运行的 FAST-12，帮你吃透算法：

```python
import numpy as np
import cv2

def is_fast_corner(img, y, x, threshold=20, N=12):
    """
    判断 (x,y) 是否是 FAST 角点。
    使用固定的 16 个邻居位置（半径 3）。
    """
    p = int(img[y, x])
    t = threshold
    bright = 0
    dark = 0
    # 圆周 16 点坐标（顺时针，从右开始）
    circle = [
        (0, 3), (1, 3), (2, 2), (3, 1), (3, 0), (3, -1), (2, -2), (1, -3),
        (0, -3), (-1, -3), (-2, -2), (-3, -1), (-3, 0), (-3, 1), (-2, 2), (-1, 3)
    ]
    # 初筛：先查 1,5,9,13（索引 0,4,8,12）
    pre = [0, 4, 8, 12]
    bright_pre = 0
    dark_pre = 0
    for i in pre:
        dy, dx = circle[i]
        v = int(img[y + dy, x + dx])
        if v > p + t:
            bright_pre += 1
        elif v < p - t:
            dark_pre += 1
    if bright_pre < 3 and dark_pre < 3:
        return False, 0
    # 完整扫描 16 点，找最长连续亮/暗
    max_consec = 0
    cur_b = 0
    cur_d = 0
    # 为处理环形连续，把 16 点复制一份接在后面
    vals = []
    for dy, dx in circle:
        v = int(img[y + dy, x + dx])
        if v > p + t:
            vals.append(1)   # 亮
        elif v < p - t:
            vals.append(-1)  # 暗
        else:
            vals.append(0)   # 相似
    vals += vals  # 复制一次
    for v in vals:
        if v == 1:
            cur_b += 1
            cur_d = 0
        elif v == -1:
            cur_d += 1
            cur_b = 0
        else:
            cur_b = cur_d = 0
        max_consec = max(max_consec, cur_b, cur_d)
    if max_consec >= N:
        # 响应分数（简易）
        V = 0
        for i, (dy, dx) in enumerate(circle):
            V += abs(int(img[y + dy, x + dx]) - p) - t
        return True, V
    return False, 0


def fast_detect(img, threshold=20, N=12, nms=True):
    h, w = img.shape
    corners = []
    for y in range(3, h - 3):
        for x in range(3, w - 3):
            ok, V = is_fast_corner(img, y, x, threshold, N)
            if ok:
                corners.append((y, x, V))
    if not nms:
        return [(y, x) for y, x, _ in corners]
    # 3×3 NMS：对同一块只留 V 最大
    keep = {}
    for y, x, V in corners:
        key = (y // 3, x // 3)
        if key not in keep or V > keep[key][2]:
            keep[key] = (y, x, V)
    return [(y, x) for y, x, _ in keep.values()]


# 使用
img = cv2.imread("test.jpg", 0)
pts = fast_detect(img, threshold=20, N=9)
color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
for y, x in pts:
    cv2.circle(color, (x, y), 3, (0, 0, 255), -1)
cv2.imshow("my FAST", color)
cv2.waitKey(0)
```

::: tip 注意
- 手写版是教学用，速度很慢（双重 for 循环），生产请用 OpenCV
- OpenCV 的 FAST 是用 C + SIMD 优化过的，比纯 Python 快几百倍
- 实际工程直接 `cv2.FastFeatureDetector_create()` 即可
:::

## FAST + 光流的标准组合

FAST 最常见的搭档是 LK 光流（稀疏光流跟踪）：

```python
# 初始化：第一帧提 FAST 角点
fast = cv2.FastFeatureDetector_create(threshold=20)
p0 = np.array([k.pt for k in fast.detect(prev_gray)], dtype=np.float32).reshape(-1, 1, 2)

# 逐帧 LK 跟踪
for frame in video:
    p1, st, err = cv2.calcOpticalFlowPyrLK(prev_gray, frame_gray, p0, None,
                                            winSize=(21, 21), maxLevel=3)
    good = p1[st == 1]
    # ... 使用 good 做 VO/SLAM
```

**这是 VINS-Mono、ORB-SLAM 前端的基本流程**。

## 相关链接

- [FAST 算法流程](/algorithms/fast/architecture)
- [FAST 调参口诀](/algorithms/fast/tricks)
- [Shi-Tomasi 角点（gFTT）](/algorithms/shi-tomasi/)
- [Lucas-Kanade 光流](/algorithms/lucas-kanade/)
