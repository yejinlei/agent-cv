# MeanShift 均值漂移 · 调参口诀

<AlgorithmCard
  name="MeanShift 均值漂移"
  enName="Mean-Shift Mode Seeking"
  chapter="ch-10-image-segmentation"
  branch="segmentation"
  year="1975/2002"
  author="K. Fukunaga / D. Comaniciu / P. Meer"
  paper="—"
  level="mid"
  tagline="每个点朝邻居最密的方向挪一步，最后聚成几坨——不用提前说有几坨"
  analogy="广场上站了一群人，每个人都往「周围人最密集的方向」走一步。走几步后大家会聚成几个紧密的小圈子，每个圈子就是一类"
  scene="图像平滑分割（pyrMeanShiftFiltering）、目标跟踪（CamShift）、聚类、运动目标分割"
  :pros='["无需指定聚类数", "同时考虑颜色+空间", "任意形状聚类", "对光照鲁棒"]'
  :cons='["速度很慢", "带宽 sp/sr 参数难调", "窗口大小固定", "高维不行"]'
/>

## MeanShift 均值漂移 调参口诀

```
空间半径 sp 十到二十，太大糊一片太小碎；
颜色半径 sr 二到四十，越大平滑越狠；
金字塔一层是默认，加层提速但精度降；
滤波后还得连通域，不然只有颜色齐；
大图像记得先缩小，不然几秒跑不完；
想自动找类数用它，已知类数直接 K-Means。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| sp | 空间窗口半径 | **15** | 区域连贯但慢 | 细节多可能过分割 |
| sr | 颜色窗口半径 | **30** | 颜色平滑强 | 保留颜色变化 |
| maxLevel | 金字塔层数 | **1** | 快但粗糙 | 慢但精 |

## 实战技巧

### MeanShift 后接 Canny 做闭合边缘

```python
shifted = cv2.pyrMeanShiftFiltering(img, 15, 30)
edges = cv2.Canny(shifted, 50, 150)
# edges 会很干净，因为 MeanShift 已经把同区域颜色平滑
```

### 用 MeanShift 做视频背景消除

MeanShift 能把运动前景变成颜色一致的块，后续帧差+连通域即可检运动。

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| pyrMeanShiftFiltering (320×240) | ~100 ms | CPU |
| pyrMeanShiftFiltering (640×480) | ~400 ms | CPU |
| pyrMeanShiftFiltering (1920×1080) | ~3 s | CPU，需降分辨率 |

## 选型建议

**适用场景**：图像平滑分割（pyrMeanShiftFiltering）、目标跟踪（CamShift）、聚类、运动目标分割

**不适用场景**：速度很慢、带宽 sp/sr 参数难调、窗口大小固定

