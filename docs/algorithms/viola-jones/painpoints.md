# Viola-Jones 实战踩坑

## 坑 1：没做直方图均衡化导致检测率低

### 症状
- 同一张脸，在不同光照下（阳光下/室内/逆光）有时能检出有时不能
- 检测框断断续续，时有时无
- 侧脸/暗光几乎全漏

### 根因
Haar 特征值 = "白区和 − 黑区和"，**直接受整体亮度影响**。不均匀光照下，"眼睛比脸颊暗"这种相对关系可能被整体偏亮/偏暗淹没。

### 避坑
```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.equalizeHist(gray)  # ✅ 必加
faces = face_cascade.detectMultiScale(gray, ...)
```

进阶：**CLAHE**（限制对比度自适应直方图均衡）在局部光照不均时更好：
```python
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
gray = clahe.apply(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
```

## 坑 2：minNeighbors 设太小 → 假脸满天飞；设太大 → 漏检

### 症状
- `minNeighbors=0`：一张图出几百个框，墙、门、阴影都被当脸
- `minNeighbors=10`：很多真脸没了
- 默认 3 在某些场景下还是偏多

### 根因
同一个真实人脸会被多个窗口（相邻位置、相邻尺度）命中，`minNeighbors` 是"一个框周围至少有几个近邻才保留"——它本质是**精度 vs 召回的平衡**。

### 推荐值

| 场景 | minNeighbors |
|---|---|
| 希望召回高（宁可多误检） | **1~2** |
| **通用默认** | **3~5** |
| 希望精度高（门禁，宁可漏检） | 5~8 |
| 严谨场景（二次过滤前的粗筛） | 6~10 |

```python
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
```

## 坑 3：scaleFactor 太激进 → 漏检人脸

### 症状
- `scaleFactor=1.5` 时小的脸、中等大小的脸经常漏
- `scaleFactor=1.05` 时速度明显变慢

### 根因
scaleFactor 是金字塔每层图像缩小的倍数。**值越大，层间人脸尺寸跳变越大，某个尺寸的脸可能正好落在两层之间，错过检测**。

### 推荐值

| 场景 | scaleFactor |
|---|---|
| **速度优先（实时）** | **1.2~1.3** |
| 通用默认 | **1.1** |
| 高精度离线检测 | 1.05 |
| 超大图/多尺度 | 1.1 + 设 minSize/maxSize |

**经验**：1.1 是最常用的甜点值。

## 坑 4：没设 minSize，图像很大时速度极慢

### 症状
- 在 4K 图片上跑 detectMultiScale，几分钟都不返回
- CPU 爆满

### 根因
没设 minSize 时，OpenCV 从 24×24 开始检测，金字塔会一直缩到图像本身大小。在 4K 图（3840×2160）上，需要滑几十层，总窗口数可能上亿。

### 避坑
```python
# 按图像尺寸估计合理的最小人脸
h, w = gray.shape[:2]
min_face = int(max(w, h) * 0.05)  # 最小人脸约占图像短边的 5%
faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(min_face, min_face)  # ✅ 加这个
)
```

## 坑 5：侧脸、俯仰脸、遮挡脸检测失败

### 症状
- 侧脸几乎全漏
- 戴口罩、戴墨镜、低头看手机都漏
- 头歪超过 30° 也漏

### 根因
`haarcascade_frontalface_default.xml` 是用**正面、清晰、光照均匀、无遮挡**的人脸训练的。Haar 特征太浅，无法处理大形变和遮挡。

### 避坑
- **侧脸**：用 `haarcascade_profileface.xml`
- **戴眼镜的眼睛**：用 `haarcascade_eye_tree_eyeglasses.xml`
- **复杂场景/多角度**：放弃 Haar，上深度学习（MTCNN / RetinaFace / YuNet）

```python
profile_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_profileface.xml'
)
profiles = profile_cascade.detectMultiScale(gray, 1.1, 3)
# 正脸 + 侧脸结果合并
```

## 坑 6：眼睛检测在脸外乱检

### 症状
- 直接对整张图跑 `haarcascade_eye.xml`，会在背景、头发、衣领处检出一堆"眼睛"

### 根因
眼睛的 Haar 模型本身不够强，单独用误检多。**必须先检测人脸，再在人脸 ROI 内检测眼睛**。

### 避坑
```python
faces = face_cascade.detectMultiScale(gray, 1.1, 5)
for (x, y, w, h) in faces:
    roi = gray[y:y+h, x:x+w]
    # 只在脸的上半部分找眼睛（眼睛不会长在脸下半）
    eyes = eye_cascade.detectMultiScale(roi[:h//2, :], 1.1, 3)
```

## 坑 7：detectMultiScale 返回的坐标是原图坐标还是缩放后坐标

### 症状
- 自己缩放图像后，画框位置对不上

### 根因
`detectMultiScale` 返回的 (x, y, w, h) 是**传入图像坐标系**的坐标。如果传的是原图，就是原图坐标；如果传的是 resize 后的图，就是缩放后坐标——需要自己乘以缩放比。

### 避坑
```python
# 正确做法：在原图上直接检测
faces = face_cascade.detectMultiScale(gray, 1.1, 5)
# (x,y,w,h) 直接对应原图
for (x,y,w,h) in faces:
    cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

# 如果你先 resize 了
small = cv2.resize(gray, (0,0), fx=0.5, fy=0.5)
faces_small = face_cascade.detectMultiScale(small, 1.1, 5)
scale_back = 2.0
for (x,y,w,h) in faces_small:
    x, y, w, h = int(x*scale_back), int(y*scale_back), int(w*scale_back), int(h*scale_back)
    cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
```

## 坑 8：灰度图没做对，报错或结果奇怪

### 症状
```
error: (-215:Assertion failed) !empty() in function 'detectMultiScale'
```
或检测结果全空。

### 根因
- 忘记加载模型（路径错、CascadeClassifier 为空）
- 传了 3 通道彩色图（OpenCV 3.x 某些版本会报错，4.x 会自动转但效果不好）
- 图片读取失败（路径错，img 为 None）

### 避坑
```python
face_cascade = cv2.CascadeClassifier(xml_path)
if face_cascade.empty():
    raise IOError("无法加载模型，检查路径")
img = cv2.imread(img_path)
if img is None:
    raise IOError("无法读取图像")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
```

## 坑 9：多人脸互相重叠，NMS 后只剩一个

### 症状
- 两个人靠得近，结果合并成一个大框
- 合照里脸被吃

### 根因
`minNeighbors` 的聚类会把所有重叠度高的框合并。两个人脸靠得近可能被归为一组。

### 避坑
1. 降低 `minNeighbors`（比如从 5 降到 3）
2. 用输出 rejectLevels/levelWeights 的进阶 API 自己做 NMS
3. 或者换深度学习检测（MTCNN/RetinaFace 处理近脸效果更好）

## 坑 10：小孩脸、非亚裔脸效果差

### 症状
- 亚洲成人效果不错，但婴儿、深肤色人种漏检率高

### 根因
默认正脸模型的训练集主要是欧美成年人脸（2000 年代初的数据集偏差）。Haar 特征对五官比例、肤色差异敏感。

### 避坑
- 用更新的模型（`haarcascade_frontalface_alt2.xml` 泛化好一点）
- 或切到深度学习方法

## 常见错误速查表

| 错误 | 原因 | 解法 |
|---|---|---|
| `!empty()` 断言失败 | 模型路径错 | 用 `cv2.data.haarcascades + 'xxx.xml'` |
| 检测框全空 | 没转灰度/没均衡化 | cvtColor + equalizeHist |
| 假脸太多 | minNeighbors 太小/图太小 | 调到 5+，加 minSize |
| 漏检严重 | scaleFactor 太大/minSize 太大 | 1.1，minSize 别太大 |
| 侧脸全漏 | 用了 default 模型 | 换 profileface 模型 |
| 速度很慢 | 没设 minSize/图太大 | 缩小图，设 minSize |
