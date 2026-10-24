# 源码走读：区域生长分割

## OpenCV 最简调用

```python
# OpenCV 没有直接的 SRG API，可用 floodFill 或 watershed 替代。
# 若要真正 SRG，建议用 skimage 或自己实现（见 naive code）。
import cv2, numpy as np
# 近似：用 floodFill（单一阈值，BFS 顺序）做单区域生长：
img = cv2.imread('scene.jpg')
mask = np.zeros((img.shape[0]+2, img.shape[1]+2), np.uint8)
seed_pt = (100, 100)
lo = (20, 20, 20); up = (20, 20, 20)
cv2.floodFill(img, mask, seed_pt, (0,255,0), lo, up,
              flags=cv2.FLOODFILL_FIXED_RANGE)

```

## 手写最小实现（理解原理）

```python
import numpy as np, cv2, heapq

def region_growing(img, seeds, conn=8):
    """
    img: 单通道灰度图 (H,W) float32
    seeds: [(x,y, region_id), ...]
    返回 labels 图
    """
    h, w = img.shape
    labels = -np.ones((h,w), dtype=np.int32)
    in_heap = np.zeros((h,w), dtype=bool)
    mean = {}; count = {}
    heap = []

    if conn == 8:
        dy = [-1,-1,-1,0,0,1,1,1]; dx = [-1,0,1,-1,1,-1,0,1]
    else:
        dy = [-1,1,0,0]; dx = [0,0,-1,1]

    for (sx, sy, rid) in seeds:
        labels[sy, sx] = rid
        mean[rid] = float(img[sy, sx])
        count[rid] = 1
        for j in range(len(dx)):
            ny, nx = sy+dy[j], sx+dx[j]
            if 0<=ny<h and 0<=nx<w and labels[ny,nx]==-1 and not in_heap[ny,nx]:
                d = abs(float(img[ny,nx]) - mean[rid])
                heapq.heappush(heap, (d, nx, ny, rid))
                in_heap[ny,nx] = True

    while heap:
        d, x, y, rid = heapq.heappop(heap)
        if labels[y,x] != -1: continue
        labels[y,x] = rid
        # 更新均值
        count[rid] += 1
        mean[rid] = (mean[rid]*(count[rid]-1) + float(img[y,x]))/count[rid]
        for j in range(len(dx)):
            ny, nx = y+dy[j], x+dx[j]
            if 0<=ny<h and 0<=nx<w and labels[ny,nx]==-1 and not in_heap[ny,nx]:
                nd = abs(float(img[ny,nx]) - mean[rid])
                heapq.heappush(heap, (nd, nx, ny, rid))
                in_heap[ny,nx] = True
    return labels

```

## OpenCV 源码核心片段解读

OpenCV 没有直接的 SRG 实现，但 ITK（医学影像库）里有非常成熟的 `itk::RegionGrowingImageFilter` 家族：
- `itk::ConnectedThresholdImageFilter`：固定阈值 flood fill
- `itk::ConfidenceConnectedImageFilter`：动态统计量（均值±σ·倍数）
- `itk::VectorConfidenceConnected`：彩色/多通道版本

另外 OpenCV 的 `cv::watershed` 和 `cv::floodFill` 可以覆盖 SRG 的大部分用例：
- 单区域固定阈值生长 → floodFill
- 多种子竞争扩张 → watershed（把种子当 marker）
