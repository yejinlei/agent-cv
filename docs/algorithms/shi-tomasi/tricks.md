# Shi-Tomasi 角点 (GFTT) · 调参口诀

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

## Shi-Tomasi 角点 (GFTT) 调参口诀

```
最小特征值当判据，k 参数不再要；
quality 是比例不是值，百分之一是起点；
minDistance 十像素，跟踪标定都够用；
block 大小 3 默认，纹理弱时加大到 5；
为光流量身定做，好特征就叫 goodFeaturesToTrack；
点集要定期重检测，长时跟踪记得加 FB 校验。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| maxCorners | 最多返回角点数 | **200** | 覆盖全图但计算量大 | 速度快但可能漏 |
| qualityLevel | 质量比例阈值 | **0.01** | 点少质量高 | 点多噪声多 |
| minDistance | 最小间距（像素） | **10** | 分布均匀 | 可能扎堆 |
| blockSize | 梯度窗口大小 | **3** | 抗噪性好 | 定位更准 |

## 实战技巧

### 亚像素精化（标定必备）

`goodFeaturesToTrack` 的精度是整像素，标定板需要亚像素精度：
```python
criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 40, 0.001)
corners_sub = cv2.cornerSubPix(gray, corners, (5,5), (-1,-1), criteria)
```
精度能到 0.1 像素。

### 配合 LK 光流的标准流程

```python
p0 = cv2.goodFeaturesToTrack(prev, 200, 0.01, 10)
p1, st, err = cv2.calcOpticalFlowPyrLK(prev, curr, p0, None, winSize=(21,21), maxLevel=3)
good = p1[st==1]
# 每 30 帧重检测一次
```

### 网格均匀化

如果全图角点分布不均，把图分 4×4 网格，每格独立 `goodFeaturesToTrack` 取 25 个点，共 400 点全图均匀分布。

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| Shi-Tomasi 检测 (640×480) | ~10 ms | 200 个角点 |
| Harris | ~20 ms | 同规模 |
| FAST | ~3 ms | 数千角点，不含 NMS 排序 |

## 选型建议

**适用场景**：光流跟踪（goodFeaturesToTrack+calcOpticalFlowPyrLK 是标配）、相机标定棋盘角点、视频稳像

**不适用场景**：不具尺度/旋转不变、需要定 qualityLevel、分布不均时扎堆

