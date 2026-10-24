# Otsu 实战与踩坑

> Otsu 的坑几乎全在「**它的假设不成立时，它依然会给你一个阈值**」——不报错，但结果是错的。

## 坑 1：直方图单峰却硬用 Otsu ⭐⭐⭐⭐⭐

```python
# ❌ 单峰图（如整片均匀金属表面）Otsu 会硬切一刀，切出噪声斑块
th, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

**症状**：二值图里出现大量随机斑块，看不出任何目标结构。

**原因**：Otsu 假设「有两类」，单峰图里根本没有真正的两类可分，它会挑一个让「方差看起来最大」的位置硬切。

**修法**：先看直方图；若单峰，改用固定阈值、三角法或换算法。

```python
import numpy as np
if gray.std() < 8:            # 对比度太低，别信 Otsu
    print('警告：直方图可能单峰，Otsu 不可靠')
```

**本体实体**：`pain-otsu-unimodal`

## 坑 2：光照不均还全图 Otsu ⭐⭐⭐⭐⭐

```python
# ❌ 文档左亮右暗：亮区清、暗区全黑
th, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

**症状**：一边前景丢失、一边背景变黑。

**修法（推荐顺序）**：

```python
# ① 背景归一化（最推荐，保留全局 Otsu）
bg = cv2.morphologyEx(gray, cv2.MORPH_CLOSE,
                      cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
norm = cv2.divide(gray, bg, scale=255)
th, bw = cv2.threshold(norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# ② 或改用自适应阈值
bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                           cv2.THRESH_BINARY, 31, 10)
```

**本体实体**：`pain-otsu-illumination`

## 坑 3：前景/背景面积悬殊 ⭐⭐⭐⭐

```python
# ❌ 小缺陷占全图 0.5%，Otsu 会偏向背景，缺陷被划进背景
```

**症状**：阈值偏高（或偏低），小目标整体被吞掉。

**原因**：$\omega_0\omega_1$ 这一项在两组面积悬殊时很小，Otsu 会为了「均衡」把阈值往小目标一侧拉偏。

**修法**：

- 用**局部 Otsu**（分块）
- 用**加权 Otsu**（给小类更高权重）
- 或直接改用固定阈值（若缺陷灰度已知）

**本体实体**：`pain-otsu-imbalance`

## 坑 4：噪声直接污染直方图 ⭐⭐⭐⭐

```python
# ❌ 椒盐噪声让直方图长出假的边峰，Otsu 被带偏
```

**修法**：

```python
# 用中值滤波去椒盐（比高斯更适合）
denoised = cv2.medianBlur(gray, 3)
th, bw = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

::: warning 顺序很重要
**先去噪，再 Otsu**。反过来（先二值化再去噪）会把噪点固化成黑块白块，形态学也救不回来。
:::

## 坑 5：16 位/12 位图直接喂 Otsu ⭐⭐⭐

```python
# ❌ 16 位工业生产图（0-65535）直接 Otsu —— OpenCV 按 8 位处理会出错
# ✅ 先归一化到 0-255
gray8 = cv2.normalize(gray16, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
th, bw = cv2.threshold(gray8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

**为什么**：Otsu 依赖 256 格直方图；16 位图的有效灰度全挤在低区，直方图形状完全失真。

## 坑 6：以为 th 是「最后要用的灰度值」 ⭐⭐

```python
th, bw = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# th 是「自动选出的阈值」，不是二值图的最大值
# 想调阈值先说清楚：df 的第二个参数必须传 0 才让 OTSU 生效
```

**细节**：调用时第二个参数（`thresh`）**必须传 0**（或任意值），因为它会被 `THRESH_OTSU` 标志覆盖。传别的数会让人误以为生效了。

## 坑 7：忘了形态学后处理 ⭐⭐⭐⭐

```python
# ❌ Otsu 出来的掩膜常带毛刺、孔洞、小噪点，直接交下游
# ✅ 开运算去小点 + 闭运算填洞
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
clean = cv2.morphologyEx(bw, cv2.MORPH_OPEN, k)
clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE, k)
```

**为什么**：Otsu 只保证「阈值最优」，不保证「区域整洁」。几乎任何工业管线在 Otsu 后都会接形态学。

**本体实体**：`pain-otsu-morphology`

## 坑 8：彩色图分通道各做 Otsu ⭐⭐⭐

```python
# ❌ B/G/R 各做一次 Otsu → 三张不同的二值图，无法合并
# ✅ 转灰度后做一次；或转 HSV 对 V（亮度）通道做
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
v = hsv[:, :, 2]
th, bw = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

## 坑 9：全黑/全白图导致除零或异常 ⭐⭐

```python
# 全同灰度图：ω1 = 0，公式里出现除零
# ✅ 加保护
if gray.max() == gray.min():
    bw = np.zeros_like(gray)
else:
    th, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

## 坑 10：把 Otsu 当成分割的终点 ⭐⭐⭐⭐

```python
# ❌ 以为 Otsu 一跑，分割就完事
# ✅ Otsu 只是「阈值分割」这一步；后面还要连通域、面积过滤、轮廓提取
```

**正确链条**：

```
去噪 → 背景归一化 → Otsu 二值化 → 形态学清理 → 连通域/轮廓 → 面积/形状筛选 → 结果
```

## 踩坑速查表

| # | 症状 | 原因 | 修法 |
|---|---|---|---|
| 1 | 随机斑块，无结构 | 单峰图硬用 Otsu | 换固定/三角法 |
| 2 | 明暗区表现分裂 | 光照不均 | 背景归一化 / 分块 / 自适应 |
| 3 | 小目标被吞 | 面积悬殊 | 局部 Otsu / 加权 / 固定阈值 |
| 4 | 阈值被带偏 | 噪声污染直方图 | 先去噪（中值） |
| 5 | 结果荒谬 | 16 位图未归一化 | 先归一化到 0-255 |
| 6 | 以为传了阈值 | 第二个参数非 0 | 传 0，靠标志生效 |
| 7 | 掩膜毛糙 | 缺形态学后处理 | 开+闭运算 |
| 8 | 三张二值图打架 | 分通道各做 Otsu | 转灰度/HSV 的 V |
| 9 | 报错/除零 | 全黑全白图 | 加保护 |
| 10 | 以为分割完成 | 概念误解 | 后续还要连通域+筛选 |

## 诊断 Checklist

- [ ] 画过直方图了吗？**是双峰吗**？
- [ ] 光照均匀吗？不均就**先归一化或分块**？
- [ ] 前景占比多少？**悬殊就别用全局 Otsu**？
- [ ] 去过噪吗（尤其椒盐）？
- [ ] 输入是 **8 位**吗？
- [ ] 后面接了**形态学**吗？
- [ ] 这是**二值化**还是**分割的终点**？

[← 上一篇：源码走读](./source) · [下一篇：调参技巧 →](./tricks)
