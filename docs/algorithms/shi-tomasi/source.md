# Shi-Tomasi 角点 (GFTT) · 源码实现

<AlgorithmCard
  name="Shi-Tomasi 角点 (GFTT)"
  enName="Shi-Tomasi / Good Features to Track"
  chapter="ch-8-local-feature"
  branch="feature-detection"
  year="1994"
  author="Jianbo Shi / Carlo Tomasi"
  paper="—"
  level="mid"
  tagline="把 Harris 响应函数换成 min(λ1,λ2)，一个参数不用调，工程界角点首选"
  analogy="Harris 像个老中医用「阴阳失调公式」判断亚健康，还要调一个神秘的 k；Shi-Tomasi 直接看你「最差的那一科成绩」——只要最差那一科也及格，你就是好学生"
  scene="光流跟踪（goodFeaturesToTrack+calcOpticalFlowPyrLK 是标配）、相机标定棋盘角点、视频稳像"
  :pros='["无需调 k 参数", "响应值物理意义明确", "自带 minDistance 防扎堆", "能限制 top-N 数量"]'
  :cons='["不具尺度/旋转不变", "需要定 qualityLevel", "分布不均时扎堆", "不含描述子"]'
/>

## OpenCV 调用方法

Shi-Tomasi 角点 (GFTT)在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

img = cv2.imread("test.jpg", 0)
corners = cv2.goodFeaturesToTrack(
    img,
    maxCorners=200,        # 最多返回角点数
    qualityLevel=0.01,     # 质量等级（比例）
    minDistance=10,        # 最小间距（像素）
    blockSize=3,           # 邻域窗口大小
    useHarrisDetector=False,  # False=Shi-Tomasi；True=Harris
    k=0.04                 # Harris 时的 k，Shi-Tomasi 忽略
)
color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
for c in corners:
    x, y = c.ravel().astype(int)
    cv2.circle(color, (x, y), 3, (0,0,255), -1)
cv2.imwrite("shitomasi.jpg", color)
print(f"检测到 {len(corners)} 个角点")
```

### 关键参数说明

| 参数 | 含义 | 建议值 |
|---|---|---|
| （见各算法具体参数表） | — | — |

## NumPy 手写最小实现

下面写一个简化版的实现，帮助理解原理（性能远不如 OpenCV，仅用于教学）：

```python
import numpy as np
import cv2

def shi_tomasi(img, max_corners=200, quality=0.01, min_dist=10, block=3):
    """简化版 Shi-Tomasi 角点检测"""
    # ① Sobel 梯度
    Ix = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    Iy = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
    Ixx = cv2.GaussianBlur(Ix*Ix, (block, block), 0)
    Ixy = cv2.GaussianBlur(Ix*Iy, (block, block), 0)
    Iyy = cv2.GaussianBlur(Iy*Iy, (block, block), 0)
    # ② 算 min(λ1,λ2)（用简化公式避免求特征值）
    # λ = (trace - sqrt(trace^2 - 4*det)) / 2
    trace = Ixx + Iyy
    det = Ixx * Iyy - Ixy * Ixy
    discriminant = np.maximum(trace*trace - 4*det, 0)
    lam_min = (trace - np.sqrt(discriminant)) / 2
    # ③ 阈值化
    thresh = lam_min.max() * quality
    candidates = np.argwhere(lam_min > thresh)
    # ④ 按响应降序，做 minDistance 抑制
    vals = lam_min[candidates[:,0], candidates[:,1]]
    order = np.argsort(-vals)
    kept = []
    for idx in order:
        y, x = candidates[idx]
        ok = True
        for (ky, kx) in kept:
            if (y-ky)**2 + (x-kx)**2 < min_dist**2:
                ok = False; break
        if ok:
            kept.append((y, x))
            if len(kept) >= max_corners:
                break
    return np.array(kept).reshape(-1, 1, 2).astype(np.float32)
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

