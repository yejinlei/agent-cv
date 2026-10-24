# BRIEF 二进制描述子 · 源码实现

<AlgorithmCard
  name="BRIEF 二进制描述子"
  enName="Binary Robust Independent Elementary Features"
  chapter="ch-8-local-feature"
  branch="feature-detection"
  year="2010"
  author="Michael Calonder et al."
  paper="—"
  level="mid"
  tagline="不再算浮点数直方图，只比 256 对像素大小，一个整数就能描述一个角点"
  analogy="SIFT/SURF 像做了一份 128 项血常规，BRIEF 只问 256 个「你比你旁边那个大吗」的是非题，用答案拼出一个 256 位的指纹"
  scene="资源受限的嵌入式设备、移动端、实时 SLAM 前端，毫秒级匹配几千个点"
  :pros='["描述子 256 位（32 字节）", "汉明距离匹配极快", "对光照模糊鲁棒", "构造简单"]'
  :cons='["不抗旋转", "不抗尺度", "对噪声敏感", "随机点对选择影响性能"]'
/>

## OpenCV 调用方法

BRIEF 二进制描述子在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

img = cv2.imread("test.jpg", 0)
# ① 先用 FAST/STAR 等检测关键点
star = cv2.xfeatures2d.StarDetector_create()      # 或 FastFeatureDetector_create
brief = cv2.xfeatures2d.BriefDescriptorExtractor_create(bytes=32, use_orientation=False)
kp = star.detect(img, None)
kp, des = brief.compute(img, kp)
print(f"描述子形状: {des.shape}, dtype: {des.dtype}")   # (N, 32) uint8

# ② 匹配两张图
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
matches = bf.knnMatch(des1, des2, k=2)
good = [m for m, n in matches if m.distance < 0.75 * n.distance]
out = cv2.drawMatches(img1, kp1, img2, kp2, good, None, flags=2)
cv2.imwrite("brief_match.jpg", out)
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

def brief_descriptor(img, kp, patch_size=31, n_pairs=256, seed=42):
    """简易 BRIEF 描述子：在每个关键点周围取 patch，随机选 n_pairs 对点比较。"""
    rng = np.random.RandomState(seed)
    half = patch_size // 2
    # 生成随机点对（在 [-half+1, half-1] 范围内高斯采样后截断）
    pts = rng.normal(0, half / 5, size=(n_pairs, 4))
    pts = np.clip(pts, -half + 1, half - 1).astype(int)
    h, w = img.shape
    des = np.zeros((len(kp), n_pairs // 8), dtype=np.uint8)
    for i, k in enumerate(kp):
        x, y = int(k.pt[0]), int(k.pt[1])
        if x - half < 0 or x + half >= w or y - half < 0 or y + half >= h:
            continue
        patch = img[y - half:y + half + 1, x - half:x + half + 1].astype(np.int32)
        bits = []
        for (dy1, dx1, dy2, dx2) in pts:
            v1 = patch[half + dy1, half + dx1]
            v2 = patch[half + dy2, half + dx2]
            bits.append(1 if v1 < v2 else 0)
        # 打包成字节
        for j in range(n_pairs // 8):
            byte = 0
            for b in range(8):
                byte |= (bits[j * 8 + b] << b)
            des[i, j] = byte
    return des
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

