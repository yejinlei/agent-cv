# 形态学操作 · 源码实现

<AlgorithmCard
  name="形态学操作"
  enName="Mathematical Morphology"
  chapter="ch-4-image-enhancement"
  branch="image-processing"
  year="1964"
  author="G. Matheron / J. Serra"
  paper="—"
  level="basic"
  tagline="膨胀、腐蚀、开、闭、顶帽黑帽——五把瑞士军刀帮你清理图像里的小毛刺和黑洞"
  analogy="形态学就像一套木匠的打磨工具：腐蚀像用砂纸把凸起毛刺磨掉，膨胀像给凹坑补腻子，开运算像「先磨毛刺再补漆」（去小白点），闭运算像「先补漆再磨平」（填小黑洞）"
  scene="二值图去噪、孔洞填充、边缘提取、骨架提取、字符识别预处理、OCR、工业缺陷检测"
  :pros='["速度极快", "效果直观可控", "组合能力强", "支持任意核形状", "CPU 实时"]'
  :cons='["核大小/形状需调", "大核慢", "过度腐蚀/膨胀丢信息", "对边界细节破坏"]'
/>

## OpenCV 调用方法

形态学操作在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

img = cv2.imread("text.jpg", 0)
_, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

# 结构元素
kernel_rect = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
kernel_cross = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

# 基础操作
eroded = cv2.erode(binary, kernel_rect, iterations=1)
dilated = cv2.dilate(binary, kernel_rect, iterations=1)
opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_ellipse)
closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_ellipse)
gradient = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel_rect)
tophat = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel_rect)
blackhat = cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel_rect)
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

def binary_erode(binary, k):
    """二值图腐蚀（简易版）"""
    h, w = binary.shape
    kh, kw = k.shape
    pad_y, pad_x = kh//2, kw//2
    padded = np.pad(binary, ((pad_y,pad_y),(pad_x,pad_x)), mode='constant')
    out = np.zeros_like(binary)
    for y in range(h):
        for x in range(w):
            patch = padded[y:y+kh, x:x+kw]
            # 腐蚀：kernel 覆盖的所有点都必须是 255
            if np.all(patch[k == 1] == 255):
                out[y, x] = 255
    return out

def binary_dilate(binary, k):
    h, w = binary.shape
    kh, kw = k.shape
    pad_y, pad_x = kh//2, kw//2
    padded = np.pad(binary, ((pad_y,pad_y),(pad_x,pad_x)), mode='constant')
    out = np.zeros_like(binary)
    for y in range(h):
        for x in range(w):
            patch = padded[y:y+kh, x:x+kw]
            # 膨胀：kernel 覆盖范围有任意一个 255 即可
            if np.any(patch[k == 1] == 255):
                out[y, x] = 255
    return out
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **morphology** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="morphology" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
