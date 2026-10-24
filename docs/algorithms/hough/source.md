# 源码走读 · 霍夫变换

> 从 OpenCV 一行调用 → 工业级车道线/圆检测 → Numpy 手写教学版 → OpenCV 源码隐藏细节。

## 一、OpenCV 最简调用（5 行）

### 1.1 直线检测（车道线）

```python
import cv2, numpy as np

img = cv2.imread("road.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(cv2.GaussianBlur(gray, (5,5), 1.0), 50, 150)
lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180,
                        threshold=80, minLineLength=100, maxLineGap=10)
if lines is not None:
    for l in lines:
        x1,y1,x2,y2 = l[0]
        cv2.line(img, (x1,y1), (x2,y2), (0,255,0), 2)
cv2.imwrite("result.jpg", img)
```

### 1.2 圆检测（瓶盖/瞳孔/硬币）

```python
img = cv2.imread("coins.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 5)                 # 中值模糊抗椒盐噪声
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,
                           dp=1.2, minDist=50,
                           param1=100, param2=40,
                           minRadius=20, maxRadius=80)
if circles is not None:
    circles = np.round(circles[0]).astype(int)
    for x,y,r in circles:
        cv2.circle(img, (x,y), r, (0,255,0), 2)
        cv2.circle(img, (x,y), 2, (0,0,255), 3)
cv2.imwrite("circles.jpg", img)
```

## 二、工业级案例

### 2.1 车道线检测（完整管线）

```python
import cv2, numpy as np

def detect_lane_lines(frame):
    H, W = frame.shape[:2]

    # 1. ROI：只保留下半部分（路面区域）
    mask = np.zeros((H, W), dtype=np.uint8)
    roi_pts = np.array([[
        (int(W*0.1), H), (int(W*0.45), int(H*0.6)),
        (int(W*0.55), int(H*0.6)), (int(W*0.9), H)
    ]], dtype=np.int32)
    cv2.fillPoly(mask, roi_pts, 255)

    # 2. 预处理
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)
    roi_edges = cv2.bitwise_and(edges, edges, mask=mask)

    # 3. HoughLinesP
    lines = cv2.HoughLinesP(roi_edges, rho=1, theta=np.pi/180,
                            threshold=50, minLineLength=50, maxLineGap=100)

    # 4. 过滤 + 按斜率分左右车道
    left, right = [], []
    if lines is not None:
        for l in lines:
            x1,y1,x2,y2 = l[0]
            if abs(x2-x1) < 1: continue          # 过滤垂直线
            slope = (y2-y1)/(x2-x1)
            if abs(slope) < 0.3: continue        # 过滤近水平线
            intercept = y1 - slope*x1
            if slope < 0 and x1 < W/2:
                left.append((slope, intercept))
            elif slope > 0 and x1 > W/2:
                right.append((slope, intercept))

    # 5. 平均拟合左右车道线
    def fit_line(pairs, y_lo, y_hi):
        if not pairs: return None
        s = np.mean([p[0] for p in pairs])
        b = np.mean([p[1] for p in pairs])
        x_lo = int((y_lo - b)/s); x_hi = int((y_hi - b)/s)
        return (x_lo, y_lo), (x_hi, y_hi)

    ll = fit_line(left, H, int(H*0.6))
    rl = fit_line(right, H, int(H*0.6))

    out = frame.copy()
    if ll: cv2.line(out, ll[0], ll[1], (0,0,255), 5)
    if rl: cv2.line(out, rl[0], rl[1], (0,0,255), 5)
    return out

cap = cv2.VideoCapture("highway.mp4")
while True:
    ret, f = cap.read()
    if not ret: break
    cv2.imshow("lane", detect_lane_lines(f))
    if cv2.waitKey(1) & 0xFF == 27: break
```

### 2.2 文档倾斜校正（利用最长直线角度）

```python
import cv2, numpy as np

def deskew_document(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=200,
                            minLineLength=200, maxLineGap=5)
    if lines is None:
        return img

    angles = []
    for l in lines:
        x1,y1,x2,y2 = l[0]
        angle = np.degrees(np.arctan2(y2-y1, x2-x1))
        # 只取接近水平/垂直的直线（文档主要方向）
        if -45 < angle < 45:
            angles.append(angle)
    if not angles:
        return img

    median_angle = np.median(angles)
    # 旋转
    H, W = img.shape[:2]
    M = cv2.getRotationMatrix2D((W/2, H/2), median_angle, 1.0)
    return cv2.warpAffine(img, M, (W, H),
                          flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)
```

### 2.3 瓶盖/圆零件检测与计数

```python
import cv2, numpy as np

def count_circles(img, minR=20, maxR=80):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # HoughCircles 对噪声敏感，先中值模糊
    gray = cv2.medianBlur(gray, 5)

    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,
                               dp=1.2, minDist=minR*2,   # 圆心最小距离 ≥ 直径
                               param1=80, param2=35,
                               minRadius=minR, maxRadius=maxR)
    out = img.copy()
    if circles is not None:
        circles = np.round(circles[0]).astype(int)
        for x,y,r in circles:
            cv2.circle(out, (x,y), r, (0,255,0), 2)
            cv2.putText(out, f"r={r}", (x-r, y-r-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        cv2.putText(out, f"count: {len(circles)}", (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 2)
    return out
```

### 2.4 PCB 直线检测（走线方向分析）

```python
def pcb_trace_angles(pcb_img):
    """统计 PCB 走线主要方向（0°/45°/90°/135°）"""
    gray = cv2.cvtColor(pcb_img, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    edges = cv2.Canny(bw, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50,
                            minLineLength=30, maxLineGap=3)
    angles = []
    if lines is not None:
        for l in lines:
            x1,y1,x2,y2 = l[0]
            ang = np.degrees(np.arctan2(y2-y1, x2-x1)) % 180
            if ang > 90: ang -= 180      # 归一化到 [-90, 90)
            angles.append(round(ang/45)*45)  # 量化到 45° 倍数
    from collections import Counter
    return Counter(angles)
```

## 三、Numpy 手写教学版（理解 PPHT 核心）

```python
import cv2, numpy as np, random

def ppht_manual(edges, rho_res=1, theta_res=np.pi/180,
                threshold=50, min_line_len=50, max_gap=10):
    """渐进概率霍夫线变换（极简教学版，速度不如 OpenCV）"""
    H, W = edges.shape
    rho_max = int(np.ceil(np.sqrt(H*H + W*W)))
    rhos = np.arange(-rho_max, rho_max+1, rho_res)
    thetas = np.arange(0, np.pi, theta_res)
    cos_t = np.cos(thetas); sin_t = np.sin(thetas)

    acc = np.zeros((len(rhos), len(thetas)), dtype=np.int32)

    # 边缘点池
    points = list(zip(*np.where(edges > 0)))  # [(y,x), ...]
    random.shuffle(points)
    point_set = set(points)

    lines_out = []

    while points:
        y, x = points.pop()
        point_set.discard((y,x))

        # 投票
        rho_vals = x*cos_t + y*sin_t
        votes = []
        for k, rv in enumerate(rho_vals):
            ri = int(round(rv + rho_max))
            if 0 <= ri < len(rhos):
                acc[ri, k] += 1
                votes.append((ri, k))

        # 找最高票 bin
        peak = max(votes, key=lambda p: acc[p])
        peak_v = acc[peak]
        if peak_v < threshold:
            continue

        rho_i, theta_i = peak
        rho_p, theta_p = rhos[rho_i], thetas[theta_i]

        # 沿直线方向行走（简化：用直线参数，向两侧搜点）
        dx = -np.sin(theta_p); dy = np.cos(theta_p)  # 直线方向
        # 搜索直线段端点（简化实现）
        pts_on_line = []
        for t in range(-W, W+1):
            px, py = int(round(x + t*dx)), int(round(y + t*dy))
            if (py, px) in point_set:
                pts_on_line.append((px, py))

        if len(pts_on_line) < 2:
            continue

        pts_on_line.sort(key=lambda p: p[0]*dx + p[1]*dy)
        x1,y1 = pts_on_line[0]; x2,y2 = pts_on_line[-1]
        length = np.hypot(x2-x1, y2-y1)
        if length < min_line_len:
            continue

        # 移除线段上的点
        for px,py in pts_on_line:
            if (py,px) in point_set:
                point_set.discard((py,px))
                if (py,px) in points:
                    points.remove((py,px))

        lines_out.append((x1,y1,x2,y2))

    return np.array(lines_out).reshape(-1,1,4)
```

## 四、OpenCV 源码隐藏细节

### 4.1 HoughLinesP 内部做了什么

OpenCV 的 `modules/imgproc/src/hough.cpp` 中 `HoughLinesProbabilistic` 大致流程：

1. **边缘点收集**：把所有非零点存到 `vector<Point2i> points`，并建一张 `mask[y][x]=1` 表记录点是否还在池里
2. **随机索引**：维护一个 shuffle 过的索引数组 `length→index`，用一个 `count` 指针循环取点
3. **累加器**：`vector<int> _accum(numrho*numangle, 0)`，一维数组
4. **投票**：取一个点，对所有 theta 累加，找 max 值
5. **线段生长（关键）**：
   - 用 `icvGetPointPositions` 沿直线方向前后行走，每走 `max_gap` 个像素就检查是否有边缘点，直到 gap 超 `maxLineGap` 或出图像边界
   - 端点由首尾两个边缘点决定
6. **撤销投票**：线段上的点从累加器"减票"（每个被移除的点对所有 theta 的 bin 减 1）

### 4.2 HoughCircles 内置做了什么

`cv::HoughCircles(HOUGH_GRADIENT)` 实现：

1. **内部自动做 Canny**：用 `param1` 作为高阈值，高阈值/2 作为低阈值；**所以你不用先自己调 Canny**
2. **Sobel 算梯度**：`Sobel(..., dx=1, dy=0, ksize=3)` 得到 dx，同理 dy
3. **圆心投票（2D）**：对每个边缘点沿梯度方向 ±maxRadius 范围内投票
4. **NMS**：`minDist` 内只保留票数最高的圆心
5. **半径投票（1D）**：对每个候选圆心，统计所有边缘点到它的距离直方图，找峰值作为半径
6. **输出是浮点**：累加器用 `float`，圆心/半径都是浮点数；圆心会用重心法做亚像素精化

### 4.3 HoughLinesP 不会告诉你的几件事

- **`threshold` 是"触发线段搜索"的票数**，不是"最终检测到这条线所需的最少点数"——线段上的点可能远多于 threshold
- **`maxLineGap` 是行走时允许的连续空隙长度**，不是两个点之间的最大距离
- **相同参数多次运行结果可能略有不同**：因为随机抽样顺序不同；要稳定结果请设 `cv2.setRNGSeed(42)`
- **如果 `minLineLength` 设得太小，会输出一堆短噪声线段**；设得太大则长直线被截断
- **HoughCircles 不接受彩色图**，传 BGR 会报错或结果乱——必须先 `cvtColor(..., GRAY)`

## 五、直线参数可视化辅助（把 ρ,θ 画出来）

```python
def draw_line_from_rho_theta(img, rho, theta, color=(0,255,0)):
    """把 HoughLines 返回的 (ρ,θ) 画在图上"""
    a, b = np.cos(theta), np.sin(theta)
    x0, y0 = a*rho, b*rho
    # 沿直线方向延长到图像边界
    L = max(img.shape)
    x1, y1 = int(x0 + L*(-b)), int(y0 + L*a)
    x2, y2 = int(x0 - L*(-b)), int(y0 - L*a)
    cv2.line(img, (x1,y1), (x2,y2), color, 2)
```

## 六、HoughLinesP 参数表（速查）

| 参数 | 含义 | 典型值 | 调大时 | 调小时 |
|---|---|---|---|---|
| `rho` | ρ 分辨率（像素）| 1 | 更粗、更快、漏检 | 更精细、更慢 |
| `theta` | θ 分辨率（弧度）| π/180 (1°) | 角度粗、合并近线 | 角度细、峰值被稀释 |
| `threshold` | 触发线段搜索的最小票数 | 50–200 | 只保留强线、漏短弱线 | 误检增多 |
| `minLineLength` | 线段最小长度 | 30–150 | 过滤短线段 | 保留短段，噪声多 |
| `maxLineGap` | 线段上允许的最大间隙 | 5–20 | 能连接断裂线段 | 断裂处断开 |

## 七、HoughCircles 参数表

| 参数 | 含义 | 典型值 | 调大 | 调小 |
|---|---|---|---|---|
| `dp` | 累加器分辨率反比 | 1–2 | 累加器小、快、粗 | 累加器大、慢、精 |
| `minDist` | 两圆心最小距离 | 直径大小 | 合并近邻圆（漏检）| 同圆多次检出 |
| `param1` | Canny 高阈值 | 50–150 | 边缘少、漏检 | 边缘多、误检 |
| `param2` | 圆心累加器阈值 | 20–50 | 只保留强圆 | 假圆增多 |
| `minRadius/maxRadius` | 半径范围 | 按场景 | 缩小范围提速 | - |

## 八、其他语言等价 API

| 语言/库 | 函数 |
|---|---|
| C++ OpenCV | `cv::HoughLines`, `cv::HoughLinesP`, `cv::HoughCircles` |
| Python OpenCV | `cv2.HoughLines`, `cv2.HoughLinesP`, `cv2.HoughCircles` |
| Matlab | `hough`, `houghpeaks`, `houghlines`, `imfindcircles` |
| scikit-image | `skimage.transform.hough_line`, `hough_line_peaks`, `hough_circle` |
| Halcon | `hough_lines`, `hough_circles`, `hough_circle_trans` |
| OpenMV | `img.find_lines()`（内置 LSD，比 Hough 更适合 MCU）|

下一章：[⚠️ 踩坑指南](/algorithms/hough/painpoints)
