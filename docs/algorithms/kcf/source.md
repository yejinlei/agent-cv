# 💻 源码实现

## ① OpenCV 一行调用（最简单）

```python
import cv2

cap = cv2.VideoCapture(0)
ok, frame = cap.read()
bbox = cv2.selectROI("select", frame, False)  # 手动框选

tracker = cv2.TrackerKCF_create()
tracker.init(frame, bbox)

while True:
    ok, frame = cap.read()
    if not ok: break
    ok, bbox = tracker.update(frame)
    if ok:
        x, y, w, h = [int(v) for v in bbox]
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
    else:
        cv2.putText(frame, "LOST", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    cv2.imshow("KCF", frame)
    if cv2.waitKey(30) == 27: break
cap.release(); cv2.destroyAllWindows()
```

## ② 带 PSR 跟丢检测的工业版

```python
import cv2, numpy as np

class KCFTracker:
    def __init__(self):
        self.tracker = cv2.TrackerKCF_create()
        self.lost_frames = 0
        self.max_lost = 20  # 连丢 20 帧就放弃

    def init(self, frame, bbox):
        self.tracker.init(frame, bbox)
        self.bbox = bbox

    def update(self, frame):
        ok, bbox = self.tracker.update(frame)
        if ok:
            self.lost_frames = 0
            self.bbox = bbox
            return True, bbox
        else:
            self.lost_frames += 1
            if self.lost_frames > self.max_lost:
                return False, None  # 真丢了，建议重新检测
            return True, self.bbox  # 暂用旧位置
```

## ③ 多目标跟踪的朴素扩展

```python
trackers = []
# 每检测到一个新目标，就 new 一个 TrackerKCF 并 init
# 每帧 update 所有 tracker，超过 N 帧失败就销毁
# 每隔几秒重跑一次检测器把新目标加进来——这就是 SORT/DeepSORT 的雏形
```

## ④ KCF vs CSRT vs MOSSE 切换

```python
tracker_mosse = cv2.legacy.TrackerMOSSE_create()   # 700 FPS，最快但飘
tracker_kcf   = cv2.TrackerKCF_create()           # 150 FPS，性价比
tracker_csrt  = cv2.TrackerCSRT_create()          # 30 FPS，最稳
```
