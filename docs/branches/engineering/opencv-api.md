# 库与 API 速查

> **一句话**：同一个操作，OpenCV / scikit-image / PIL / NumPy 分别怎么写——**以及该选哪个**。

---

## 该选哪个库

| 库 | 语言 | 定位 | 什么时候用 |
|---|---|---|---|
| **OpenCV** | Py / C++ | 工业级，算法最全、最快 | **默认首选**，尤其是 C++ 部署 |
| **scikit-image** | Python | 教学/科研友好，API 优雅 | 快速验证算法、科研原型 |
| **Pillow (PIL)** | Python | 图像 I/O 与基础处理 | 只做读图/存图/裁剪/格式转换 |
| **NumPy** | Python | 数值计算底座 | 自己写算子、做自定义后处理 |
| **HALCON / VisionPro** | 商业 | 工业视觉全家桶 | 拿到预算的商业产线 |

::: tip 一条实践经验
**读图用 PIL、算法用 OpenCV、实验用 skimage、部署用 OpenCV C++**。别在一个项目里混用三套颜色通道约定——这是最常见的低级 bug 来源。
:::

---

## ⚠️ 先记住这张「颜色通道」对照表

**这是跨库使用最容易出错的地方：**

| 库 | 默认通道顺序 | 读进来的变量长什么样 |
|---|---|---|
| **OpenCV (`cv2.imread`)** | **BGR** | `(H, W, 3)` |
| **PIL (`Image.open`)** | **RGB** | PIL Image 对象 |
| **scikit-image (`io.imread`)** | **RGB** | `(H, W, 3)` |
| **Matplotlib (`plt.imread`)** | **RGB**（浮点 0–1） | `(H, W, 3)` |

```python
import cv2
from PIL import Image

# OpenCV 读进来是 BGR
img_bgr = cv2.imread('a.jpg')

# 转成 PIL 必须在读入后立刻 BGR→RGB
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
pil_img = Image.fromarray(img_rgb)

# 反过来：PIL → OpenCV
img_bgr2 = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
```

**症状**：图看着「红蓝颠倒」——人脸发蓝、天空发橙。**根因 99% 是通道顺序搞错了。**

---

## 常用操作对照

### ① 读取 / 保存

| 操作 | OpenCV | scikit-image | PIL |
|---|---|---|---|
| 彩色读图 | `cv2.imread(p)` | `io.imread(p)` | `Image.open(p)` |
| 灰度读图 | `cv2.imread(p, 0)` | `io.imread(p, as_gray=True)` | `Image.open(p).convert('L')` |
| 保存 | `cv2.imwrite(p, img)` | `io.imsave(p, img)` | `img.save(p)` |

### ② 缩放 / 旋转

| 操作 | OpenCV | scikit-image | PIL |
|---|---|---|---|
| 缩放 | `cv2.resize(img, (w, h))` | `transform.resize(img, (h, w))` | `img.resize((w, h))` |
| 旋转 | `cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)` | `transform.rotate(img, 90)` | `img.rotate(90)` |
| 仿射 | `cv2.warpAffine(img, M, (w, h))` | `transform.warp(img, tform)` | `img.transform(...)` |

::: warning 缩放参数顺序不一致
**OpenCV 是 `(宽, 高)`，skimage 是 `(高, 宽)`** —— 这是跨库移植时最高频的 bug。写错的结果是图被拉变形。
:::

### ③ 滤波

| 操作 | OpenCV | scikit-image |
|---|---|---|
| 高斯 | `cv2.GaussianBlur(img, (5,5), 1.0)` | `filters.gaussian(img, sigma=1.0)` |
| 中值 | `cv2.medianBlur(img, 5)` | `filters.median(img, disk(2))` |
| 双边 | `cv2.bilateralFilter(img, 9, 75, 75)` | `restoration.denoise_bilateral(img)` |
| 自定义卷积 | `cv2.filter2D(img, -1, kernel)` | `ndi.convolve(img, kernel)` |

### ④ 边缘与特征

| 操作 | OpenCV | scikit-image |
|---|---|---|
| Canny | `cv2.Canny(img, 50, 150)` | `feature.canny(img, sigma=1.0)` |
| Sobel | `cv2.Sobel(img, cv2.CV_64F, 1, 0)` | `filters.sobel(img)` |
| 霍夫直线 | `cv2.HoughLinesP(edges, ...)` | `transform.probabilistic_hough_line` |
| Harris 角点 | `cv2.cornerHarris(gray, 2, 3, 0.04)` | `feature.corner_harris(img)` |
| LBP | ❌ 无内置（自己写或 skimage） | `feature.local_binary_pattern` |

### ⑤ 分割与形态学

| 操作 | OpenCV | scikit-image |
|---|---|---|
| Otsu | `cv2.threshold(g, 0, 255, cv2.THRESH_OTSU)` | `filters.threshold_otsu(img)` |
| 分水岭 | `cv2.watershed(img, markers)` | `segmentation.watershed(img, markers)` |
| 腐蚀/膨胀 | `cv2.erode` / `cv2.dilate` | `morphology.binary_erosion` |
| 连通域 | `cv2.connectedComponentsWithStats` | `measure.label` |
| 区域属性 | `cv2.contourArea` / `minAreaRect` | `measure.regionprops` |

---

## 一个「同一个任务三种写法」的完整例子

**任务**：灰度化 → 去噪 → Otsu 二值化 → 形态学去毛刺

```python
# ---------- 写法 A：OpenCV（推荐，最快，部署友好） ----------
import cv2
img = cv2.imread('part.jpg', 0)
blur = cv2.GaussianBlur(img, (5, 5), 1.2)
_, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, k)

# ---------- 写法 B：scikit-image（API 优雅，适合实验） ----------
import numpy as np
from skimage import io, filters, morphology
img = io.imread('part.jpg', as_gray=True)          # 自动 float 0-1
blur = filters.gaussian(img, sigma=1.2)
th = filters.threshold_otsu(blur)
bw = blur > th                                     # 得到 bool 数组
bw = morphology.binary_opening(bw, morphology.disk(2))

# ---------- 写法 C：PIL + NumPy（轻量，只做 I/O 时用） ----------
from PIL import Image, ImageFilter
import numpy as np
img = Image.open('part.jpg').convert('L')
blur = img.filter(ImageFilter.GaussianBlur(1.2))
arr = np.array(blur)
th = arr.mean()                                    # PIL 没有 Otsu，得自己算
bw = (arr > th).astype(np.uint8) * 255
```

---

## 部署时的三条硬建议

- **① 部署一定用 OpenCV，且优先 C++**。Python 版在嵌入式上启动慢、内存占用大；C++ 版可静态链接，体积小、启动快。
- **② 不要在部署脚本里依赖 PIL**（除非只做读图）。PIL 处理大图时内存占用明显高于 OpenCV。
- **③ 固定版本号**。`cv2.Canny` 在不同大版本间的默认行为有过变化，产线必须锁定 OpenCV 版本并写进文档。

---

## 相关页面

- 🛠 [性能与算力优化](/branches/engineering/performance)
- 🏭 [产线工程化](/branches/engineering/pipeline)
- 🚀 [嵌入式边缘部署案例](/cases/edge-deployment)
