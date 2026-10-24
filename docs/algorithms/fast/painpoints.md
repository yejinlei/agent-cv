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
## FAST 的常见坑

::: danger 坑 1：threshold 太低，检测出海量噪声点
**现象**：`threshold=5` 或 `10` 时，一张图检测出几万个点，其中大部分是噪声。

**原因**：FAST 判据只看圆周 16 点，低阈值时任何微小纹理都能通过。

**解决**：
- 日常场景 `threshold=20` 起步
- 高对比纹理图 `threshold=30–40`
- 模糊图 `threshold=10–15`
- 配合 NMS（`nonmaxSuppression=True`）
:::

::: danger 坑 2：忘了开 NMS，角点扎堆
**现象**：同一个真实角点周围检测出 7、8 个紧挨的点。

**解决**：**`nonmaxSuppression=True`**（默认就是 True，别手动关）。
:::

::: danger 坑 3：以为 FAST 有尺度不变性
**现象**：图像放大 2 倍后，FAST 角点完全对不上。

**真相**：FAST 的半径固定是 3 像素，**没有尺度不变性**。

**解决**：
- 需要尺度不变性时，用 **ORB**（FAST + 图像金字塔）或 SIFT/SURF
- 或自己构建金字塔，在每层分别检测
:::

::: danger 坑 4：以为 FAST 有旋转不变性
**现象**：图像旋转后，同一点检测不出来，或者描述子匹配失败。

**真相**：纯 FAST **没有方向**，不抗旋转。

**解决**：
- 需要旋转不变性时，用 **ORB**（它给 FAST 加了灰度质心法的方向）
- 或者自己加方向分配（见 ORB 的 oFAST）
:::

::: danger 坑 5：直接用 FAST 做匹配失败
**现象**：两张图提了 FAST 点，却没法匹配。

**根因**：**FAST 只给"点"，不给"描述子"**——你不知道两个点"长得像不像"。

**解决**：必须搭配描述子：

| 组合 | 特点 |
|---|---|
| FAST + BRIEF | 快，但无旋转不变 |
| **FAST + rBRIEF = ORB** | **工业首选**，有旋转+尺度 |
| FAST + SIFT 描述子 | 精度高，慢 |

```python
# 推荐直接用 ORB
orb = cv2.ORB_create()
kp, des = orb.detectAndCompute(gray, None)
```
:::

::: danger 坑 6：FAST 点分布不均
**现象**：所有角点集中在墙角、纹理区域，墙面、天空一个点没有。

**解决（网格配额法）**：

```python
def grid_fast(img, grid=(4, 4), per_cell=25, threshold=20):
    h, w = img.shape
    fast = cv2.FastFeatureDetector_create(threshold=threshold)
    all_kp = []
    gh, gw = h // grid[0], w // grid[1]
    for i in range(grid[0]):
        for j in range(grid[1]):
            roi = img[i*gh:(i+1)*gh, j*gw:(j+1)*gw]
            kp = fast.detect(roi, None)
            kp = sorted(kp, key=lambda k: k.response, reverse=True)[:per_cell]
            for k in kp:
                k.pt = (k.pt[0] + j*gw, k.pt[1] + i*gh)
            all_kp.extend(kp)
    return all_kp
```
:::

::: danger 坑 7：FAST 在边界、模糊图上乱点
**现象**：图像边缘 3 像素内、失焦模糊区域会出一堆无意义点。

**解决**：
- 遍历时跳过图像边框（手写实现）
- OpenCV 版本自动处理边框
- 检测前先做轻微高斯模糊（`sigma=1`）去除噪声
:::

## 相关链接

- [FAST 源码实现](/algorithms/fast/source)
- [FAST 调参口诀](/algorithms/fast/tricks)
