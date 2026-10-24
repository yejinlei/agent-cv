# Lucas-Kanade 光流：实战与踩坑

LK 看起来好调，但工业界踩过的坑能绕地球半圈。这一章全是血泪经验。

## 10 个最常见的坑

### 坑 1：忘记转灰度图
**现象**：传入 3 通道 BGR → OpenCV 不会报错（某些版本默默当灰度处理），结果全是 NaN/inf 或全部 status=0。

**解法**：
```python
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # 必须先转！
```

### 坑 2：没锁曝光/AWB，点在同一个地方凭空"跳"
**现象**：相机自动曝光调整时，整帧亮度漂移，LK 以为点动了，实际没动——全局出现"鬼影运动"。

**解法**：
- 工业相机：锁曝光、锁增益、锁白平衡（手动模式）
- 普通 USB 摄像头：用 `v4l2-ctl` 或相机厂商 API 关闭自动曝光
- 实在锁不了：先做 CLAHE 直方图均衡，再 LK
```python
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
gray_eq = clahe.apply(gray)
```

### 坑 3：不做反向检查（Forward-Backward），点被"骗"了
**现象**：一个点被遮挡后重新出现在新位置，或进入了重复纹理（墙砖、格子），LK 前向跟踪以为跟对了，实际上跟错了对象。

**解法**：**双向跟踪**，前向+反向光流，回不到原点就丢：
```python
p1, st1, _ = cv2.calcOpticalFlowPyrLK(prev, curr, p0, None, **lk_params)
p0r, st2, _ = cv2.calcOpticalFlowPyrLK(curr, prev, p1, None, **lk_params)
fb = np.linalg.norm(p0 - p0r, axis=2).reshape(-1)
good = (st1.ravel() == 1) & (st2.ravel() == 1) & (fb < 2)  # 2 像素阈值
```
::: warning 所有严肃的跟踪系统（TLD、KLT、MedianFlow）都有这步，OpenCV 官方示例没有，但你一定要加。
:::

### 坑 4：winSize 太大跨边界
**现象**：窗口跨在物体边缘（一半车一半背景），两边运动方向相反，最小二乘"平均"出一个错误结果，点在边界上"颤抖"。

**解法**：
- winSize 不要盲目开大，15×15 起步，最多 31×31
- 在边界附近/深度不连续区域降低点密度（检测时用 mask 把边缘屏蔽掉）
- 或者用**仿射/平移一致性**做后验：单个点位移和周围点差异太大就丢

### 坑 5：maxLevel 不够，大位移跟不住
**现象**：快速运动物体、相机快速移动，点第一帧就丢。

**解法**：
- 视频分辨率 640×480，`maxLevel=3` 可处理 ~30 像素位移
- 1080p 视频或快速运动，`maxLevel=4~5`
- 同时适当加大 `winSize` 到 21~31

### 坑 6：maxLevel 太大，高层漂移
**现象**：最高层分辨率太低（比如 1/16 后只有 40×30），纹理细节丢失，LK 在高层估错方向，然后错误被逐层放大。

**解法**：
- `maxLevel` 不超过 `log2(min(W,H)/10)`（最小边至少剩 10 像素）
- 经验值：VGA (640×480) 用 3 层，720p 用 4 层，1080p 用 5 层，不要更多

### 坑 7：长时间不补点，点越跟越少
**现象**：前 10 秒 200 个点，1 分钟后只剩 10 个，稳像/姿态估计崩。

**解法**：
- 每帧都检查好点数，低于阈值（初始数量的 50% 或固定阈值 50）就补
- 补点时**用 mask 屏蔽已有好点周围 minDistance 范围**，避免重复
```python
if good_new.shape[0] < 50:
    mask = np.ones_like(gray) * 255
    for pt in good_new:
        cv2.circle(mask, tuple(pt.astype(int)), 7, 0, -1)
    new_pts = cv2.goodFeaturesToTrack(gray, mask=mask, **feature_params)
    if new_pts is not None:
        good_new = np.vstack([good_new.reshape(-1,1,2), new_pts])[:200]
```

### 坑 8：点 ID 没管理，补点后混淆
**现象**：补点后，原来的点和新点混在一起，下游（比如计算轨迹、做 SLAM）无法分辨"哪个点是哪个"。

**解法**：维护一个**全局 ID 数组**，每个点一个 ID，丢点不回收 ID，新点分配新 ID：
```python
next_id = 0
point_ids = []  # 与 p0 等长，每个点的 ID

# 补点时
for _ in range(len(new_pts)):
    point_ids.append(next_id); next_id += 1
# 丢点时同步删 point_ids 对应位置
```

### 坑 9：忘记 `prevPts` 必须是 float32
**现象**：传入 int 点（来自 `goodFeaturesToTrack` 默认是 float32，但如果你做了别的处理转成 int），OpenCV 某些版本报错或默默不工作。

**解法**：
```python
p0 = p0.astype(np.float32)
```

### 坑 10：在彩色图上跑 + err 阈值不调
**现象**：err 返回的是 uint8 差的平均，范围 0~255。很多人固定用 err<10，结果一半点被误杀，或者一半坏点被保留。

**解法**：
- **看 err 分布**：第一帧调试时 `plt.hist(err)`，看正常跟踪和失败点的分界
- 经验值：uint8 灰度图，err < 10~20 是正常，>30 基本失败
- **一定要结合 fb_err**：只看 err 不够，fb_err < 2 像素是硬指标

## 踩坑速查表

| 症状 | 可能原因 | 对应坑 # |
|---|---|---|
| 点从第一帧就全部 status=0 | 没转灰度 / minEigThreshold 太紧 / winSize 太小 | 1, 4 |
| 前几帧还行，之后点越来越少 | 没补点 / fb_err 没做 / 光照变化 | 3, 7, 2 |
| 点在物体边缘"抖" | winSize 跨边界 / 没有双向检查 | 4, 3 |
| 快速运动点直接丢 | maxLevel 不够 / winSize 太小 | 5 |
| 慢速稳，快速漂 | maxLevel 太大或 winSize 太大 | 6, 4 |
| 点整体在一个方向飘 | 曝光/AWB 飘移 / CLAHE 没做 | 2 |
| err 很小但点明显跟错 | 重复纹理/遮挡，必须看 fb_err | 3 |
| 下游轨迹错乱 | 没管理点 ID | 8 |

## 快速诊断 checklist

每次调 LK 都按这个过一遍：

- [ ] 输入是单通道灰度，float32/uint8？
- [ ] 相机曝光/增益/WB 锁定了？
- [ ] `goodFeaturesToTrack` 的 qualityLevel/minDistance/maxCorners 适合场景？
- [ ] `winSize` 和 `maxLevel` 与视频分辨率/运动速度匹配？
- [ ] 做了 Forward-Backward 反向检查？
- [ ] err 阈值根据实际数据分布调过？
- [ ] 有补点机制？好点低于阈值自动重检测？
- [ ] 点 ID 稳定管理？
- [ ] 掩码防止新点加在已有点附近？

这 9 项全过，LK 基本就稳了。
