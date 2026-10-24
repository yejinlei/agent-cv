# 💻 源码实现

## ① 最小可运行版（10 行就动起来）

```python
import cv2

cap = cv2.VideoCapture(0)  # 或视频文件路径
bg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=32, detectShadows=True)

while True:
    ok, frame = cap.read()
    if not ok: break
    mask = bg.apply(frame)            # 0=背景 127=阴影 255=前景
    cv2.imshow("mask", mask)
    if cv2.waitKey(30) == 27: break
cap.release(); cv2.destroyAllWindows()
```

## ② 工业版：后处理 + 画框

```python
import cv2, numpy as np

bg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=36, detectShadows=True)
cap = cv2.VideoCapture("surveillance.mp4")

while True:
    ok, frame = cap.read()
    if not ok: break

    mask = bg.apply(frame)
    # 1. 把阴影（127）先折成 0，我们只关心真正的前景
    mask[mask == 127] = 0
    # 2. 开运算去噪
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3)))
    # 3. 闭运算填洞
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7)))
    # 4. 连通域过滤小噪声
    num, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    out = frame.copy()
    for i in range(1, num):
        x, y, w, h, area = stats[i]
        if area < 200: continue
        cv2.rectangle(out, (x,y), (x+w,y+h), (0,255,0), 2)

    cv2.imshow("motion", out)
    if cv2.waitKey(30) == 27: break
cap.release(); cv2.destroyAllWindows()
```

## ③ MOG2 vs KNN 对比

```python
bg_mog2 = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=36)
bg_knn  = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400)
```
- **室内固定场景**：MOG2 更稳，误检少；
- **动态背景（树叶、喷泉、水波）**：KNN 更鲁棒，因为非参数；
- **嵌入式/低算力**：MOG2 略快。
