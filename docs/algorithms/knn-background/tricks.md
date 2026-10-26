---
outline: deep
---

# 第 7 页 · 调参口诀

## 一句话调参口诀

```
KNN 比 MOG2 稳但更慢；history 管记忆长度、dist2Threshold 管宽容度。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|------|------|--------|----------|----------|
| history | 历史长度 | **500** | 记忆更长、更稳 | 更快适应但易误检 |
| dist2Threshold | 距离阈值 | **400** | 更宽容、漏检增 | 更敏感、噪声增 |
| detectShadows | 阴影检测 | **True** | 标出阴影 | 阴影当前景 |

## 实战技巧

### 和 MOG2 对比选型

要快用 MOG2，要稳（树叶/水面）用 KNN。

### 降采样提速

先缩到 640×360 做检测，再把掩码放大回原图，速度提升明显。

### 组合连通域

检测出的前景掩码直接送 connectedComponentsWithStats，即可数人数、算面积。

## 性能参考

| 条件 | 耗时 | 说明 |
|------|------|------|
| 640×480，nSamples=7 | ≈6 ms/帧 | KNN 检测 |
| 640×480，MOG2 对照 | ≈3 ms/帧 | MOG2 更快 |
| 1920×1080，nSamples=7 | ≈30 ms/帧 | 高分辨率建议降采样 |

## 选型建议

**适合用**：监控运动检测、人流量统计、车辆计数、周界入侵报警（比 MOG2 更抗噪）

**不适合用**：比 MOG2 慢、内存占用更高（每像素存 N 个样本）、参数（history/nSamples/dist2Threshold）需调

::: tip 一句话
记住每个像素最近的 N 个历史颜色，新颜色离它们太远就判为前景
:::

<!-- AUTO-EXTENSION-2 -->

## 🎯 参数建议

| 参数 | 起点 | 备注 |
| --- | --- | --- |
| history | 500 | 室外场景大一点（500~1000）|
| dist2Threshold | 400 | 值越大越宽容（树叶场景 600+）|
| detectShadows | true | 阴影标 127，后处理好过滤 |

### 三行上手

```python
bs = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400.0, detectShadows=True)
while True:
    fg = bs.apply(frame, learningRate=-1)  # -1 = 自动学习率
    # fg: 0=背景, 127=阴影, 255=前景
```
