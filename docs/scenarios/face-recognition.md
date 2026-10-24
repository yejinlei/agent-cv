# 👤 人脸检测与识别

> **任务类型**：实时人脸定位（检测）+ 身份比对（识别）
> **典型要求**：检测 15–30 FPS（无 GPU）｜ 识别准确率 > 99%（1:1 场景）
> **涉及章**：第12章（景物识别）、第4章（特征）、第6章（描述子）、第13章（匹配）

---

## 先把两件事分清楚

| 任务 | 回答什么 | 传统方法 | 现代主流 |
|---|---|---|---|
| **人脸检测** | 图里有没有人脸、在哪 | **Viola-Jones 级联** / HOG+SVM | 轻量 CNN 检测器 |
| **人脸识别** | 这个人是谁 | **Eigenfaces / Fisherfaces / LBPH** | 深度特征 + 度量学习 |

**这一页两个都讲，因为工业上「边缘盒子 + 无 GPU + 实时」的场景，传统方法仍然有实战价值。**

---

## 第一部分：人脸检测（Viola-Jones 实战）

### 为什么它在嵌入式上仍主流

```
CPU 单核，VGA 分辨率：
  Viola-Jones  →  20–40 ms   ✅ 满足实时
  轻量 CNN     →  80–300 ms  ❌ 不满足，除非有 NPU
```

**代价**：只擅长正面、对光照敏感、遮挡时下降。**收益**：无需 GPU、模型几百 KB、启动快。

### 完整可运行代码

```python
import cv2

class FaceDetector:
    def __init__(self, min_neighbors=6, min_size=(40, 40)):
        # 多模型融合：正面 + 侧脸，覆盖更全
        self.front = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.profile = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_profileface.xml')
        self.min_neighbors = min_neighbors
        self.min_size = min_size

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 关键预处理：直方图均衡化能显著提升暗光检出率
        gray = cv2.equalizeHist(gray)

        common = dict(scaleFactor=1.1, minNeighbors=self.min_neighbors,
                      minSize=self.min_size, flags=cv2.CASCADE_SCALE_IMAGE)
        faces = list(self.front.detectMultiScale(gray, **common))

        # 侧脸：把图水平翻转再检测，覆盖左右两侧
        flipped = cv2.flip(gray, 1)
        w = gray.shape[1]
        for (x, y, fw, fh) in self.profile.detectMultiScale(flipped, **common):
            faces.append((w - x - fw, y, fw, fh))

        return merge_overlapping(faces, iou_thr=0.3)

def merge_overlapping(boxes, iou_thr=0.3):
    """合并重叠的检测框（级联检测常在一个脸上出多个框）"""
    boxes = sorted(boxes, key=lambda b: -b[2] * b[3])
    kept = []
    for b in boxes:
        if all(iou(b, k) < iou_thr for k in kept):
            kept.append(b)
    return kept

def iou(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x1, y1 = max(ax, bx), max(ay, by)
    x2, y2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0
```

### 参数调优表

| 参数 | 作用 | 推荐 |
|---|---|---|
| `scaleFactor` | 金字塔缩放比 | **1.1**（1.05 更全更慢，1.2 更快更漏） |
| `minNeighbors` | **最关键**：邻居数阈值 | **5–6**（3 误报多，8 漏检多） |
| `minSize` | 最小人脸尺寸 | 按实际场景设，**设了能大幅提速** |
| 输入分辨率 | 缩到多小 | **640×480 足够**；再大收益小而耗时翻倍 |
| 预处理 | 直方图均衡化 | **必加**，暗光场景检出率提升明显 |

---

## 第二部分：人脸识别（三种传统方法）

| 方法 | 原理 | 优点 | 缺点 |
|---|---|---|---|
| **Eigenfaces**（PCA） | 把人脸看成「特征脸的线性组合」 | 简单、快 | 对光照/表情极敏感 |
| **Fisherfaces**（LDA） | 找「类间差异大、类内差异小」的方向 | **比 Eigenfaces 稳** | 需要每类多张样本 |
| **LBPH** | 用 LBP 直方图统计局部纹理 | **抗光照变化最好** | 对姿态变化敏感 |

::: tip 传统人脸识别的定位
**在「固定机位 + 固定光照 + 人数少（几十人）」的场景，LBPH 至今可用**——门禁、考勤、工位状态检测都还在用。**一旦人数上百、光照多变、需要跨姿态，就必须上深度方案（ArcFace 等）。**
:::

### LBPH 完整实现

```python
import cv2
import numpy as np

class LBPHRecognizer:
    """基于局部二值模式直方图的人脸识别（抗光照）"""
    def __init__(self, radius=1, neighbors=8, grid_x=8, grid_y=8):
        self.model = cv2.face.LBPHFaceRecognizer_create(
            radius=radius, neighbors=neighbors,
            grid_x=grid_x, grid_y=grid_y)
        self.labels = {}
        self.threshold = 70          # 距离阈值，超过则判为「未知」

    def _preprocess(self, face):
        """统一尺寸 + 光照归一化（这一步对准确率影响极大）"""
        face = cv2.resize(face, (100, 100))
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        # CLAHE 比全局均衡更好：分块处理，不会把局部噪点放大到全图
        return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(face)

    def train(self, faces, labels):
        """faces: 人脸图片列表；labels: 对应的人 ID 列表"""
        processed = [self._preprocess(f) for f in faces]
        self.model.train(processed, np.array(labels, np.int32))
        self.labels = {i: str(l) for i, l in enumerate(labels)}

    def predict(self, face):
        processed = self._preprocess(face)
        label, confidence = self.model.predict(processed)
        # 注意：LBPH 的 confidence 是「距离」，越小越好
        if confidence > self.threshold:
            return {'name': 'unknown', 'confidence': float(confidence)}
        return {'name': self.labels.get(label, str(label)),
                'confidence': float(confidence)}
```

::: warning LBPH 的 confidence 是「越小越好」
**这是最容易搞反的地方。** LBPH 返回的 `confidence` 是**距离**（0 表示完全匹配），**不是概率**。阈值判断要写成 `if conf > threshold: unknown`。
:::

### 三步对齐：识别率的关键

**很多人识别率上不去，不是模型不好，是没做人脸对齐。**

```python
def align_face(img, face_box, eye_cascade=None):
    """
    把两只眼睛摆到固定位置 —— 这一步能把 LBPH 准确率提升 10%+
    """
    x, y, w, h = face_box
    roi = img[y:y+h, x:x+w]

    if eye_cascade is None:
        eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml')

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    eyes = eye_cascade.detectMultiScale(gray, 1.1, 5,
                                        minSize=(int(w*0.15), int(h*0.15)))
    if len(eyes) < 2:
        return roi                      # 找不到眼睛就返回原图

    # 取两只眼睛的中心
    pts = sorted([(ex + ew//2, ey + eh//2) for ex, ey, ew, eh in eyes[:2]],
                 key=lambda p: p[0])
    (lx, ly), (rx, ry) = pts[0], pts[1]

    # 计算倾斜角并旋转，让双眼水平
    angle = np.degrees(np.arctan2(ry - ly, rx - lx))
    M = cv2.getRotationMatrix2D(((lx + rx)//2, (ly + ry)//2), angle, 1.0)
    aligned = cv2.warpAffine(roi, M, (roi.shape[1], roi.shape[0]))
    return aligned
```

---

## 完整流水线

```python
import cv2

detector = FaceDetector(min_neighbors=6, min_size=(40, 40))
recognizer = LBPHRecognizer()
recognizer.train(train_faces, train_labels)

cap = cv2.VideoCapture(0)
while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame = cv2.resize(frame, (640, 480))          # 限制分辨率提速
    faces = detector.detect(frame)

    for (x, y, w, h) in faces:
        aligned = align_face(frame, (x, y, w, h))
        result = recognizer.predict(aligned)

        color = (0, 255, 0) if result['name'] != 'unknown' else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, f"{result['name']} {result['confidence']:.0f}",
                    (x, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow('face', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
```

---

## 五个必踩的坑

::: warning 坑 1：不做人脸对齐直接识别
**这是准确率上不去的头号原因。** 同一个人歪头 15%，LBPH 算出的距离可能比另一个人还大。
**解法**：用双眼定位做旋转对齐（见上面 `align_face`）。
:::

::: warning 坑 2：训练样本光照单一
只用「办公室白光」下拍的照片训练，现场换成「门口逆光」直接失败。
**解法**：每个 ID 采集 **多光照、多表情、多角度**（至少 10 张），并用 CLAHE 做光照归一化。
:::

::: warning 坑 3：LBPH 阈值设错方向
把 `confidence` 当概率，写成 `if conf < threshold: unknown`——逻辑反了。
**解法**：记住 **LBPH 的 confidence 是距离，越小越像**，判未知用 `conf > threshold`。
:::

::: warning 坑 4：一帧只检测一次就下结论
单帧检测有波动，可能出现「这一帧认成 A、下一帧认成 B」。
**解法**：**时序投票**——连续 5 帧里 3 帧以上一致才确认身份。
:::

::: warning 坑 5：忘了做「活体检测」
拿一张照片就能骗过 LBPH。
**解法**：传统方法可用「眨眼检测（眼睛区域方差变化）」「微小头部动作」「多光谱/红外」等做简单活体；要求高的场景必须加专用活体模块。
:::

---

## 相关页面

- 🎯 [场景反查入口](/scenarios/)
- 📘 [第12章 景物识别](/chapters/ch12-recognition)
- 📌 [Viola-Jones 检测器详解](/branches/detection/viola-jones)
- 📄 [HOG+SVM 完整档案](/algorithms/hog-svm/)（另一种经典检测器）
- 🛠 [性能与算力优化](/branches/engineering/performance)
