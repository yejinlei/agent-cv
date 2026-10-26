# Viola-Jones 源码走读

## ① OpenCV 静态图片人脸检测（标准用法）

```python
import cv2

# 1) 加载预训练模型（OpenCV 内置）
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml'
)

# 2) 读图 + 预处理
img = cv2.imread('group.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.equalizeHist(gray)  # 必加！均衡化抗光照

# 3) 检测
faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,      # 金字塔缩放比
    minNeighbors=5,       # 聚类最小邻居数
    minSize=(30, 30),     # 最小人脸
    flags=cv2.CASCADE_SCALE_IMAGE
)
print(f"检测到 {len(faces)} 张人脸")

# 4) 画框 + 在脸内再检测眼睛
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    roi_gray = gray[y:y+h, x:x+w]
    roi_color = img[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=3)
    for (ex, ey, ew, eh) in eyes:
        cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)

cv2.imwrite('faces_detected.png', img)
```

## ② 摄像头实时人脸检测

```python
import cv2

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)
cap = cv2.VideoCapture(0)  # 0 = 默认摄像头

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.2, minNeighbors=4, minSize=(60, 60)
    )
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow('Face Detection (Press Q to quit)', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

::: tip 实时优化小技巧
- `scaleFactor=1.2`（比默认 1.1 快，精度略降）
- `minSize=(60,60)`（不检测小脸，省大量窗口）
- 分辨率降到 320×240 或 640×480
- 现在的笔记本通常能跑到 **30+ FPS**
:::

## ③ OpenCV 内置可用的 haarcascade 模型

| 模型文件 | 用途 |
|---|---|
| `haarcascade_frontalface_default.xml` | 通用正脸（最常用） |
| `haarcascade_frontalface_alt2.xml` | 正脸，对轻微侧脸更鲁棒 |
| `haarcascade_profileface.xml` | **侧脸**检测 |
| `haarcascade_eye.xml` | 眼睛 |
| `haarcascade_eye_tree_eyeglasses.xml` | 戴眼镜的眼睛 |
| `haarcascade_smile.xml` | 笑脸 |
| `haarcascade_upperbody.xml` | 上半身 |
| `haarcascade_fullbody.xml` | 全身 |
| `haarcascade_licence_plate_rus_16stages.xml` | 俄罗斯车牌 |

```python
import os
for f in os.listdir(cv2.data.haarcascades):
    if f.endswith('.xml'):
        print(f)
```

## ④ numpy 手写积分图

```python
import numpy as np

def integral_image(img: np.ndarray) -> np.ndarray:
    """计算积分图，返回 (H+1, W+1)，首行首列为 0"""
    H, W = img.shape
    ii = np.zeros((H+1, W+1), dtype=np.int64)
    for y in range(1, H+1):
        row_sum = 0
        for x in range(1, W+1):
            row_sum += int(img[y-1, x-1])
            ii[y, x] = ii[y-1, x] + row_sum
    return ii

def rect_sum(ii: np.ndarray, x: int, y: int, w: int, h: int) -> int:
    """用积分图算矩形 (x,y) 到 (x+w-1, y+h-1) 的和"""
    x1, y1 = x, y
    x2, y2 = x + w - 1, y + h - 1
    return int(ii[y2+1, x2+1] - ii[y1, x2+1] - ii[y2+1, x1] + ii[y1, x1])

# 验证
img = (np.random.rand(100, 100) * 255).astype(np.uint8)
ii = integral_image(img)
x, y, w, h = 10, 20, 15, 20
assert rect_sum(ii, x, y, w, h) == int(img[y:y+h, x:x+w].sum())
print("积分图验证通过 ✓")
```

## ⑤ numpy 手写单个 Haar 特征计算

以"两矩形横向边缘特征"为例：
- 左半黑、右半白
- 特征值 = 白区和 − 黑区和

```python
def haar_2_horizontal(ii, x, y, w, h):
    """两矩形横向特征：左右两半，值=右-左"""
    half_w = w // 2
    left  = rect_sum(ii, x,         y, half_w, h)
    right = rect_sum(ii, x+half_w,  y, half_w, h)
    return right - left

def haar_3_vertical(ii, x, y, w, h):
    """三矩形纵向特征（鼻梁）：值=中-两侧平均"""
    third_w = w // 3
    left   = rect_sum(ii, x,           y, third_w, h)
    middle = rect_sum(ii, x+third_w,   y, third_w, h)
    right  = rect_sum(ii, x+2*third_w, y, third_w, h)
    return middle - (left + right) // 2

# 测试特征值
img = np.zeros((100, 100), dtype=np.uint8)
# 左边暗（黑），右边亮（白）
img[:, :50] = 50
img[:, 50:] = 200
ii = integral_image(img)
f_val = haar_2_horizontal(ii, 10, 10, 60, 40)
print(f"横向 Haar 特征值（右侧亮）: {f_val}")  # 应该是很大的正数
```

## ⑥ numpy 手写弱分类器 + 单 Stage 推理（原理版）

```python
class WeakClassifier:
    """单个 Haar 特征 + 阈值 + 极性 = 一个弱分类器"""
    def __init__(self, feature_fn, threshold, polarity, alpha):
        self.fn = feature_fn
        self.theta = threshold
        self.p = polarity
        self.alpha = alpha

    def predict(self, ii, x, y, w, h):
        f = self.fn(ii, x, y, w, h)
        return self.alpha if self.p * f < self.p * self.theta else 0

class Stage:
    """级联中的一级"""
    def __init__(self, weaks, threshold):
        self.weaks = weaks
        self.threshold = threshold

    def predict(self, ii, x, y, w, h):
        score = sum(wk.predict(ii, x, y, w, h) for wk in self.weaks)
        return score >= self.threshold

# 示例：构造一个极简两级级联（教学用，非真实模型）
stage1 = Stage([
    WeakClassifier(lambda ii,x,y,w,h: haar_2_horizontal(ii,x,y,w,h),
                   threshold=50000, polarity=1, alpha=1)
], threshold=0.5)
# ...
# if stage1.predict(ii, x, y, 24, 24): 才进 stage2
```

## ⑦ 自己训练一个 Haar 分类器（命令行工具）

```bash
# 1) 准备正样本描述文件 pos.txt，每行：filepath x y w h
# 2) 准备负样本描述文件 neg.txt，每行：filepath
# 3) 生成 pos.vec
opencv_createsamples -info pos.txt -num 2000 -w 24 -h 24 -vec pos.vec
# 4) 训练
mkdir classifier
opencv_traincascade \
  -data classifier \
  -vec pos.vec \
  -bg neg.txt \
  -numPos 1800 -numNeg 3000 \
  -numStages 20 \
  -featureType HAAR \
  -w 24 -h 24 \
  -minHitRate 0.999 \
  -maxFalseAlarmRate 0.5
# 产物：classifier/cascade.xml
```

::: warning 训练耗时
训练一个质量不错的分类器需要**几千正样本、上万负样本、几小时到几天**，而且参数调优麻烦。**实战中优先用 OpenCV 预训练模型**，除非你要检测特定物体（比如自定义 Logo）。
:::

## OpenCV 源码关键文件

- `modules/objdetect/src/cascadedetect.cpp`：Haar+LBP+Hog 级联统一实现
  - `CascadeClassifierImpl::runAt`：单窗口多 stage 推理
  - `CascadeClassifierImpl::detectMultiScaleNoGrouping`：金字塔+滑窗
  - `groupRectangles`：近邻聚类合并
- `modules/objdetect/src/haar.cpp`：Haar 特征计算（积分图加速版，SIMD 优化）
- `apps/traincascade/`：训练工具源码

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **viola jones** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="facedetect" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
