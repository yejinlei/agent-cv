# Lucas-Kanade 光流：调参技巧

把 LK 调到工业可用，核心是 5 个参数的 tradeoff + 几个工程补丁。

## 一、五个核心参数调参顺序

按"先保能跟、再保准确、最后提速度"的顺序调：

### Step 1：先选点（`goodFeaturesToTrack`）参数
| 参数 | 作用 | 起点 | 调法 |
|---|---|---|---|
| `maxCorners` | 每帧最多保留多少点 | 200 | 稳像 100~200，SLAM 500~1000，动作捕捉 200~500 |
| `qualityLevel` | 点质量阈值（相对最强点的比例） | 0.01 | 点不够 → 降到 0.005 甚至 0.001；点太杂 → 升到 0.03 |
| `minDistance` | 点之间最小像素间距 | 7~10 | 太密容易跟重复 → 加大；点分布不均 → 减小并配合 mask |
| `blockSize` | 算梯度的邻域大小 | 7 | 图像模糊/噪点多 → 加大到 11；高分辨率纹理清晰 → 3 |

::: tip 选点第一原则
**宁可少而精，不要多而杂**。100 个好角点比 1000 个边缘点/平坦点有用得多。qualityLevel 宁可高一点（0.03）再不够再降。
:::

### Step 2：再调 LK 本身
| 参数 | 作用 | 起点 | 调法 |
|---|---|---|---|
| `winSize` | 搜索窗口 | (15,15) | 运动大/纹理稀 → 21~31；精细跟踪/运动小 → 7~11。**总是奇数** |
| `maxLevel` | 金字塔层数 | 3 | VGA 视频 3 层；720p 4 层；1080p 5 层；快速运动加 1 层 |
| `criteria` | 每层迭代终止 | (EPS+COUNT, 10, 0.03) | 追求精度 count=30, epsilon=0.01；速度优先 count=5 |
| `minEigThreshold` | 最小特征值过滤 | 1e-4 | 图像噪点大 → 1e-3；纹理弱的图 → 1e-5（但容易出坏点）|

### Step 3：最后调后处理阈值
| 参数 | 作用 | 起点 |
|---|---|---|
| `err 阈值` | 前向误差上限 | 10~20（uint8）|
| `fb_err 阈值` | 反向检查距离上限 | 1~2 像素 |
| 补点阈值 | 好点低于多少补新点 | 初始 maxCorners 的 30~50% |

## 二、不同场景的"抄作业"参数表

### 场景 1：视频稳像（手机/无人机）

```python
feature_params = dict(maxCorners=200, qualityLevel=0.01, minDistance=10, blockSize=7)
lk_params = dict(winSize=(21, 21), maxLevel=3,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
FB_ERR_THRESHOLD = 1.5
MIN_GOOD_POINTS = 80
```
要点：点选均匀分布（minDistance=10），winSize 稍大抗抖，fb_err 严格。估计全局仿射时用 RANSAC 再过滤一次。

### 场景 2：SLAM/视觉里程计（低速，小位移）

```python
feature_params = dict(maxCorners=500, qualityLevel=0.01, minDistance=7, blockSize=7)
lk_params = dict(winSize=(15, 15), maxLevel=4,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01),
    minEigThreshold=1e-3)
FB_ERR_THRESHOLD = 1.0
```
要点：点要多（500+），均匀分布，minEigThreshold 稍高保质量，fb_err 极严格（<1 像素），跟踪丢的点不删除只标记（SLAM 要做地图点管理）。

### 场景 3：高速目标跟踪（比如无人机高速飞行、运动捕捉）

```python
feature_params = dict(maxCorners=300, qualityLevel=0.005, minDistance=5, blockSize=5)
lk_params = dict(winSize=(31, 31), maxLevel=5,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03))
FB_ERR_THRESHOLD = 2.0
```
要点：大窗口 + 多层金字塔处理大位移；qualityLevel 降低让点多；fb_err 适当放宽。**配合高速快门（1/500s 以上）**避免运动模糊是关键。

### 场景 4：嵌入式平台（Raspberry Pi / OpenMV）

```python
feature_params = dict(maxCorners=50, qualityLevel=0.03, minDistance=15, blockSize=5)
lk_params = dict(winSize=(11, 11), maxLevel=2,
    criteria=(cv2.TERM_CRITERIA_COUNT, 5, 0))  # 只做 5 次迭代
MIN_GOOD_POINTS = 20
```
要点：点少（50 个）、窗口小、金字塔浅、迭代少。牺牲精度换速度。OpenMV 上硬件 LK 只有 8 个点专用加速。

### 场景 5：动作捕捉（高精度，亚像素级）

```python
# 选点时亚像素精化
p0 = cv2.goodFeaturesToTrack(gray, 500, 0.01, 10)
cv2.cornerSubPix(gray, p0, (5,5), (-1,-1),
    (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_COUNT, 50, 0.001))

lk_params = dict(winSize=(21, 21), maxLevel=4,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 0.001))
FB_ERR_THRESHOLD = 0.5
```
要点：cornerSubPix 精化 + 严格收敛 + 大窗口 + fb_err < 0.5 像素。配合红外高对比度标记点。

### 场景 6：人脸/物体特征点跟踪（局部）

```python
# 只在 ROI 内检测点，不整图
roi_mask = np.zeros(gray.shape, np.uint8)
roi_mask[y:y+h, x:x+w] = 255
p0 = cv2.goodFeaturesToTrack(gray, 100, 0.01, 5, mask=roi_mask)
lk_params = dict(winSize=(11, 11), maxLevel=2,
    criteria=(cv2.TERM_CRITERIA_COUNT, 20, 0.01))
```
要点：用 mask 把选点区域限制在 ROI，避免背景点干扰；窗口小因为面部表情是形变，大窗口会平均掉。

## 三、速度优化清单

| 优化 | 效果 | 代价 |
|---|---|---|
| 降分辨率（先 cv2.pyrDown 再 LK） | 速度 ×4 | 精度下降 |
| 减少 maxCorners（200→50） | 速度 ×4 | 鲁棒性降 |
| 减小 winSize（21→11） | 速度 ×2~3 | 大位移易失败 |
| 减小 maxLevel（4→2） | 速度 ×1.5 | 大位移能力降 |
| 减少迭代次数（30→10） | 速度 ×2 | 精度略降 |
| 隔帧跟踪（不是每帧而是隔 N 帧）| 速度 ×N | 位移大时跟不住 |
| 用灰度 uint8 而不是 float32 | 速度 ×1.2 | - |
| ROI 限定（只在感兴趣区域检测/跟踪）| 速度视 ROI 大小 | 应用受限 |

## 四、精度优化清单

- **cornerSubPix 亚像素精化**：初始点精度从 1 像素提到 0.01 像素
- **前向-反向双向检查**：剔除欺骗性匹配，精度提升 30%+
- **后接 RANSAC 几何验证**：用全局运动模型（单应/仿射）过滤离群点
- **迭代 LK（criteria 调严）**：count=50, epsilon=0.001
- **用 float32 输入**：避免 uint8 截断误差
- **CLAHE 预处理**：解决光照不均，对室内/室外切换场景明显有效

## 五、LK 什么时候该换算法？

| 信号 | 换什么 |
|---|---|
| 物体发生旋转/缩放，纯平移 LK 漂 | 换**仿射 LK**（`calcOpticalFlowFarneback` 稠密，或自己实现 affine LK）|
| 物体/相机高速运动，金字塔也顶不住 | 降分辨率 + 升 maxLevel；或换**事件相机**；或换深度学习光流 RAFT |
| 要求稠密光流（每像素都要运动）| 换 **Farneback**（CPU）或 **RAFT**（GPU）|
| 大形变/非刚体（人脸表情、液体）| LK 根本不适用，换 **光流+分割** 或 DL 方法 |
| 长时间跟踪目标（分钟以上）| 纯 LK 必丢，换 **TLD / MedianFlow / KCF / SiamRPN**|
| 弱纹理/平坦表面（墙面、天空）| 不用 LK，换**直接法**（DSO/LSD-SLAM）或加 IMU |

## 六、调参日记示范（实战记录）

第一次接到无人机稳像任务时的真实调参记录：

> **Day 1**：默认参数 winSize=15, maxLevel=3，点 200 个。慢速飞行 OK，快速转头时点几乎全丢。
>
> **Day 2**：把 maxLevel 加到 5，winSize=31，慢速和快速都能跟，但大转角时候点会"粘"在背景上（因为窗口跨前景背景）。
>
> **Day 3**：加 fb_err<2 检查，"粘"的点被剔除了，但点损耗太快，10 秒后只剩 20 个。
>
> **Day 4**：加自动补点（低于 80 就补）+ mask 屏蔽旧点周围，点数稳定在 120~200。
>
> **Day 5**：发现自动曝光导致云台"抖"。锁曝光后问题消失。
>
> **Day 6**：估计仿射变换时加 RANSAC（`cv2.estimateAffinePartial2D` 自带 RANSAC），抖动再降一个量级。
>
> **上线参数**：winSize=21, maxLevel=4, maxCorners=200, qualityLevel=0.01, fb_err<1.5, RANSAC inlier threshold=3.0。

**经验教训**：LK 本身只占 30% 的工作量，剩下 70% 是光照处理、点管理、后处理——这和所有传统 CV 算法一样。
