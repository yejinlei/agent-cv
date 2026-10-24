# FAST 角点检测

<AlgorithmCard
  name="FAST 角点检测"
  enName="Features from Accelerated Segment Test"
  chapter="ch-8-local-feature"
  branch="feature-detection"
  year="2006"
  author="Edward Rosten / Tom Drummond"
  paper="—"
  level="mid"
  tagline="用一个圆圈 16 个邻居，一眼认出角点，速度比 Harris 快 10 倍"
  analogy="FAST 像一个哨兵：不进屋检查，只趴在窗户上数——窗外 16 个邻居里如果连续 12 个都比屋里亮或都比屋里暗，那这间房肯定是个「犄角旮旯」"
  scene="SLAM、AR、实时物体识别里做特征点检测，毫秒级返回几千个点，CPU 上就能跑 60fps"
  :pros='["速度极快（比 Harris 快 10 倍以上）", "实现简单", "角点重复率高", "OpenCV 高度优化"]'
  :cons='["不具备尺度不变性", "不具备旋转不变性", "阈值敏感", "需要 NMS", "不含描述子"]'
/>
## FAST 调参口诀

```
threshold 二十是起步，模糊图降十、清晰图三十补；
NMS 永远开 True，关闭就成马蜂窝；
FAST-9-16 是默认，想要更快 5-8、更准 12-16 换；
只检测不提描述，匹配还得 BRIEF/ORB 组合组；
点太密用网格配额，每格上限二十五；
想跨尺度加金字塔，想抗旋转用 ORB 一键补。
```

## 参数选择指南

| 场景 | threshold | N | NMS | 推荐搭配 |
|---|---|---|---|---|
| 实时 SLAM/VO（30fps） | **20** | 9 | ✅ | ORB 描述子 |
| 高速目标检测（60fps） | 30 | 12 | ✅ | AGAST + BRIEF |
| 图像配准（精度优先） | 10–15 | 9 | ✅ | SIFT 描述子 |
| 嵌入式/MCU | 20 | 9 | ✅ | BRIEF（32 字节） |
| 图像分割/角点可视化 | 20–30 | 9 | ✅ | — |

## 实战技巧

### ① 前置高斯模糊稳定检测

```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (3, 3), 1.0)   # 轻微去噪
kp = fast.detect(gray, None)
```

**好处**：抑制高频噪声，FAST 点更稳定。**sigma 不能太大**（>1.5 会把角点糊掉）。

### ② 限制总点数 + 选响应最强的

```python
kp = fast.detect(gray, None)
kp = sorted(kp, key=lambda k: k.response, reverse=True)[:500]   # 取前 500
```

### ③ 做 LK 光流时如何选点

```python
# 不要直接用 FAST 点做 LK，用 goodFeaturesToTrack 更稳
# 但如果要速度，FAST + LK 可以这样配：
p0 = cv2.goodFeaturesToTrack(gray, maxCorners=200, qualityLevel=0.01, minDistance=10)
# 这就是 Shi-Tomasi（见 /algorithms/shi-tomasi/）
```

### ④ 检测后需要均匀分布的话用 cv2.KeyPoint 转换

```python
def nms_kp(kp, dist_thresh=10):
    """对 KeyPoint 列表按响应排序，做距离 NMS"""
    kp_sorted = sorted(kp, key=lambda k: k.response, reverse=True)
    keep = []
    for k in kp_sorted:
        x1, y1 = k.pt
        ok = True
        for kk in keep:
            x2, y2 = kk.pt
            if (x1-x2)**2 + (y1-y2)**2 < dist_thresh**2:
                ok = False
                break
        if ok:
            keep.append(k)
    return keep
```

### ⑤ FAST 不适合的场景

| 场景 | 原因 | 替代 |
|---|---|---|
| 鱼眼/广角畸变严重 | 圆周 3 像素畸变后形状变了 | 先去畸变再检测 |
| 大幅缩放匹配 | 无尺度不变 | ORB/SIFT |
| 大幅旋转匹配 | 无方向 | ORB/SIFT |
| 低光照/强噪声 | 阈值难选 | FAST+高斯模糊 或 SIFT |

## 性能参考（1920×1080 灰度，CPU）

| 方法 | 耗时 | 点数 |
|---|---|---|
| Harris | ~50 ms | 数千 |
| Shi-Tomasi | ~30 ms | ~200（受 maxCorners 限制） |
| **FAST-9-16** | **~4–6 ms** | 数千 |
| AGAST | ~3–5 ms | 数千 |
| ORB（检测+描述） | ~15 ms | 500 |
| SIFT | ~200 ms | 数千 |

**FAST 是 CPU 实时场景唯一选择**。

## 相关链接

- [FAST 源码实现](/algorithms/fast/source)
- [FAST 踩坑清单](/algorithms/fast/painpoints)
- [ORB 完整档案（FAST+方向+描述+尺度）](/algorithms/orb/)
