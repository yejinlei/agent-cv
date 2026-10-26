# 单应矩阵 · 源码实现

<AlgorithmCard
  name="单应矩阵"
  enName="Homography Matrix H"
  chapter="ch-14-3d-vision"
  branch="geometry"
  year="传统几何"
  author="射影几何经典"
  paper="—"
  level="mid"
  tagline="一个 3×3 矩阵搞定「一个平面」在两张图之间的映射，4 对点就能求，文档扫描和全景拼接的灵魂"
  analogy="你把手机对着一张纸拍斜了，单应矩阵就像一个拉正的魔法：告诉它纸的四个角应该在什么位置，它就能把整张纸拉正成矩形——就像你从正上方拍的一样"
  scene="文档扫描/矫正、逆透视变换 IPM（车道鸟瞰）、AR 平面跟踪、全景拼接（纯旋转）、张正友标定、图像配准"
  :pros='["数学简洁(8自由度)", "4对点可求", "OpenCV一行findHomography", "应用极广", "RANSAC鲁棒"]'
  :cons='["仅平面/纯旋转成立", "有深度差时错位", "点共线退化", "warpPerspective易出画布", "DLT需归一化"]'
/>

## OpenCV 调用方法

单应矩阵在 OpenCV 中直接可用，下面给一个可运行的完整例子：

```python
import cv2
import numpy as np

# 文档矫正：四个角点拉正为矩形
img = cv2.imread("doc.jpg")
h, w = 500, 400   # 目标矩形
pts_src = np.array([[120,30],[580,50],[560,470],[100,460]], dtype=np.float32)  # 文档四角
pts_dst = np.array([[0,0],[w,0],[w,h],[0,h]], dtype=np.float32)
H = cv2.getPerspectiveTransform(pts_src, pts_dst)
doc = cv2.warpPerspective(img, H, (w, h))
cv2.imwrite("doc_rectified.jpg", doc)

# 图像配准 + RANSAC
# 假设 kp1/kp2/des1/des2 是 ORB 检测结果
bf = cv2.BFMatcher(cv2.NORM_HAMMING)
matches = bf.knnMatch(des1, des2, k=2)
good = [m for m,n in matches if m.distance<0.75*n.distance]
pts1 = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
pts2 = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
H, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 5.0)
aligned = cv2.warpPerspective(img1, H, (img2.shape[1], img2.shape[0]))
```

### 关键参数说明

| 参数 | 含义 | 建议值 |
|---|---|---|
| （见各算法具体参数表） | — | — |

## NumPy 手写最小实现

下面写一个简化版的实现，帮助理解原理（性能远不如 OpenCV，仅用于教学）：

```python
import numpy as np
import cv2

def homography_dlt(pts1, pts2):
    """直接线性变换求单应矩阵（pts1, pts2: Nx2, N>=4）"""
    n = len(pts1)
    A = []
    for i in range(n):
        x, y = pts1[i]; xp, yp = pts2[i]
        A.append([-x,-y,-1,0,0,0, x*xp,y*xp,xp])
        A.append([0,0,0,-x,-y,-1, x*yp,y*yp,yp])
    A = np.array(A)
    _, _, Vt = np.linalg.svd(A)
    H = Vt[-1].reshape(3,3)
    return H / H[2,2]
```

## 生产环境建议

- 工程中**直接使用 OpenCV 接口**，不要自己手写（OpenCV 有 SIMD/多线程优化）
- 如果是嵌入式平台，可以考虑用 OpenCV 的 `cv2.setNumThreads(1)` 控制线程
- 对大图像先降分辨率处理，再上采样结果（精度损失可忽略时速度提升显著）

## 🎮 动手试一试

原理看完了，现在就在你浏览器里跑一遍 **homography** 吧——拖动滑块调参数，下面的 Python/C++/JS 代码会自动跟着变，复制即可用。

<ClientOnly>
  <OpencvPlayground initial-algo="homography" compact />
</ClientOnly>

👉 想要更丰富的示例图、上传自己的照片、切换其他算法？去 [🎮 真机实验室](/playgrounds/)。
