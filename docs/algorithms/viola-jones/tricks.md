# Viola-Jones 调参技巧

## ① scaleFactor：金字塔密度

**默认 1.1**。控制图像金字塔每层缩放比。

| scaleFactor | 速度 | 召回率 | 适用 |
|---|---|---|---|
| 1.05 | 慢（层数多） | 最高 | 离线高精度 |
| **1.1** | **适中** | **高** | **通用默认** |
| 1.2 | 快 | 中 | 实时/视频 |
| 1.3~1.5 | 很快 | 低 | 粗筛/超大图 |

**心法**：1.1 是甜点。如果速度优先，升到 1.2；如果追求召回，降到 1.05。

## ② minNeighbors：聚类阈值

**默认 3**。一个候选区域至少要有多少个近邻检测框才保留。

| minNeighbors | 精度 | 召回 | 适用 |
|---|---|---|---|
| 0~1 | 极低（假脸多） | 最高 | 调试看原始候选点 |
| **3~4** | **中** | **高** | **通用默认** |
| 5~6 | 高 | 中 | 考勤、门禁（宁可漏不可误） |
| 8+ | 极高 | 低 | 假阳率要求极严的场合 |

**心法**：从默认 3 开始，如果假脸多就加到 5；如果漏脸多就降到 2。

## ③ minSize / maxSize：尺寸范围

**强烈建议设置 minSize**，能省大量时间并减少小噪声误检。

| 应用 | minSize | maxSize |
|---|---|---|
| 自拍近景（脸较大） | (80, 80) | (400, 400) |
| 监控/远景（脸较小） | (30, 30) | 不设 |
| 摄像头实时（建议） | (60, 60) | 不设 |
| 集体合照（小脸） | (20, 20) | (150, 150) |
| 证件照（脸占主要面积） | (100, 100) | 不设 |

**实用代码**：根据图像尺寸自动设 minSize
```python
h, w = gray.shape
min_dim = min(h, w)
min_face = (max(20, min_dim // 10), max(20, min_dim // 10))  # 至少 1/10 图幅
faces = face_cascade.detectMultiScale(
    gray, 1.1, 4, minSize=min_face
)
```

## ④ flags 参数（向后兼容）

OpenCV 4.x 基本不用 flags。老代码里常见：
- `cv2.CASCADE_SCALE_IMAGE`：按比例缩放（默认就是，正常不用设）
- `cv2.CASCADE_FIND_BIGGEST_OBJECT`：只返回最大的脸
- `cv2.CASCADE_DO_ROUGH_SEARCH`：粗略搜索，快但精度低

现代版本推荐用默认（=0）即可。

## ⑤ 模型选择：哪个 xml 更好用？

OpenCV 自带的几个正脸模型其实有区别：

| 模型 | 速度 | 精度 | 对非正脸容忍度 | 推荐 |
|---|---|---|---|---|
| `haarcascade_frontalface_default.xml` | 中 | 中 | 低 | 默认，通用 |
| `haarcascade_frontalface_alt.xml` | **快** | 较高 | 中 | **推荐**：速度精度平衡好 |
| `haarcascade_frontalface_alt2.xml` | 中 | **最高** | **较高** | 质量最好 |
| `haarcascade_frontalface_alt_tree.xml` | 慢 | 高 | 中 | 多阶段 tree 结构 |

**实战建议**：先用 `_alt2.xml`，如果速度不够换 `_alt.xml`。

```python
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'  # 推荐
)
```

## ⑥ 多模型组合（正脸+侧脸）

一个模型覆盖不了所有角度，最常见的组合：

```python
front = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
profile = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

def detect_all_faces(gray):
    faces = list(front.detectMultiScale(gray, 1.1, 4, minSize=(40,40)))
    # 侧脸图（考虑左右两种朝向，水平翻转再检一次）
    profiles = list(profile.detectMultiScale(gray, 1.1, 4, minSize=(40,40)))
    flipped = cv2.flip(gray, 1)
    profiles_flip = list(profile.detectMultiScale(flipped, 1.1, 4, minSize=(40,40)))
    h, w = gray.shape
    for (x,y,ww,hh) in profiles_flip:
        profiles.append((w - x - ww, y, ww, hh))  # 翻回来
    # 合并去重
    return non_max_suppression(faces + profiles, overlap_thresh=0.3)
```

## ⑦ 自己写简单 NMS 替代 groupRectangles

Viola-Jones 的 minNeighbors 聚类有时不如 IoU-based NMS 灵活。如果自己做：

```python
def iou(a, b):
    x1,y1,w1,h1 = a; x2,y2,w2,h2 = b
    xi1,yi1 = max(x1,x2), max(y1,y2)
    xi2,yi2 = min(x1+w1,x2+w2), min(y1+h1,y2+h2)
    inter = max(0,xi2-xi1) * max(0,yi2-yi1)
    union = w1*h1 + w2*h2 - inter
    return inter / union if union > 0 else 0

def non_max_suppression(boxes, overlap_thresh=0.3):
    if not boxes:
        return []
    boxes = sorted(boxes, key=lambda b: b[2]*b[3], reverse=True)  # 按面积排
    keep = []
    while boxes:
        current = boxes[0]
        keep.append(current)
        boxes = [b for b in boxes[1:] if iou(current, b) < overlap_thresh]
    return keep
```

## ⑧ 典型场景参数模板

### 模板 A：实时摄像头（30 FPS）
```python
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'  # 快
)
faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.3,          # 大步进，快
    minNeighbors=4,
    minSize=(80, 80),         # 不检小脸
    flags=cv2.CASCADE_SCALE_IMAGE
)
# 图像先缩到 640 宽再检测，能更流畅
```

### 模板 B：离线相册人脸标注（精度优先）
```python
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
)
all_faces = []
# 正脸
all_faces += list(face_cascade.detectMultiScale(
    gray, scaleFactor=1.05, minNeighbors=3, minSize=(20,20)
))
# + 侧脸模型 + 翻转
# ... 再做 NMS 合并
```

### 模板 C：门禁/考勤（少误检）
```python
faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=6,       # 高门槛
    minSize=(120, 120),   # 人站得近，脸大
    maxSize=(400, 400)
)
# 只保留最大的 1 张
if len(faces) > 1:
    faces = [max(faces, key=lambda r: r[2]*r[3])]
```

### 模板 D：笑脸快门（脸+眼+笑三级验证）
```python
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
)
smile_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_smile.xml'
)

faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60,60))
for (x,y,w,h) in faces:
    roi = gray[y+int(h*0.3):y+h, x:x+w]  # 只看脸下半
    smiles = smile_cascade.detectMultiScale(
        roi, scaleFactor=1.5, minNeighbors=15, minSize=(20,10)
    )
    if len(smiles) > 0:
        print("笑了！快门！")
```

## ⑨ 与其他检测算法选型对照

| 需求 | 选什么 |
|---|---|
| **嵌入式/无 GPU，只检测正脸** | ✅ Viola-Jones（Haar） |
| 行人检测 | HOG+SVM |
| 多视角物体（车/动物） | DPM（已过时）或深度学习 |
| 高准确率人脸 | MTCNN / YuNet / RetinaFace |
| 实时人脸 + 关键点 | YuNet（OpenCV 内置，2020 后） |
| 通用物体 | YOLO/SSD/Faster R-CNN |
| CPU 实时人脸 + 不折腾 | YuNet（OpenCV 4.5+ FaceDetectorYN） |

::: tip 新选择：OpenCV FaceDetectorYN
OpenCV 4.5+ 内置了 **YuNet** 人脸检测器（深度神经网络），单模型几百 KB，CPU 实时，**精度远好于 Haar**：
```python
detector = cv2.FaceDetectorYN.create(
    "face_detection_yunet_2022mar.onnx", "", (320, 320)
)
```
新项目优先考虑它；Haar 更适合教学、极低算力芯片、以及理解级联思想。
:::

## ⑩ 加速套路清单

1. **缩小图像**：检测前把图缩到 640 或 320 宽
2. **设 minSize**：不检小到看不见的脸
3. **调大 scaleFactor**：1.2~1.3 足够
4. **用 `_alt.xml`**：比 `default.xml` 快
5. **转灰度 + CLAHE**：预处理一次，检测更稳还可能减少多级推理
6. **跳帧检测**：视频里每 2~3 帧检一次，中间帧用跟踪（KCF/TLD）延续
7. **ROI 限定**：只在感兴趣区域（比如屏幕中央）检测

```python
# 组合拳：实时摄像头终极版
small = cv2.resize(gray, (320, int(320*h/w)))
faces_small = face_cascade.detectMultiScale(
    small, scaleFactor=1.2, minNeighbors=4, minSize=(40,40)
)
scale = w / 320
faces = [(int(x*scale), int(y*scale), int(ww*scale), int(hh*scale))
         for x,y,ww,hh in faces_small]
```

## 速查表

| 参数 | 默认 | 推荐范围 |
|---|---|---|
| scaleFactor | 1.1 | 1.05 ~ 1.3 |
| minNeighbors | 3 | 2 ~ 6 |
| minSize | (0,0) | 根据场景设（推荐 30~80） |
| maxSize | (0,0) | 可选 |
| 模型选择 | default.xml | **alt2.xml（质量最佳）/ alt.xml（最快）** |
