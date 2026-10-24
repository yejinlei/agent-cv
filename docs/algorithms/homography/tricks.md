# 单应矩阵 · 调参口诀

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

## 单应矩阵 调参口诀

```
平面或是纯旋转，单应矩阵才成立；
四个点对就能解，RANSAC 抗错配；
warpPerspective 拉正图，文档扫描全靠它；
DLT 求 H 用 SVD，记得归一化数值更稳；
点不共线分散排，一条直线求不出来；
IPM 逆透视车道鸟瞰，张正友标定每步都用它。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| ransacReprojThreshold | RANSAC 重投影阈值(px) | **5.0** | 严 | 宽松 |
| method | 求解方法 | **RANSAC** | — | — |

## 实战技巧

### 文档扫描自动检测四角

```python
# 找最大四边形做文档角点
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
canny = cv2.Canny(cv2.GaussianBlur(gray,(5,5),0), 30, 100)
cnt = max(cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0], key=cv2.contourArea)
eps = 0.02*cv2.arcLength(cnt, True)
approx = cv2.approxPolyDP(cnt, eps, True)
# approx 4个点即四角
```

### IPM 逆透视（车道鸟瞰）

预先标定好地面的 4 个点（路面上已知间距的梯形），求 H 映射到俯视矩形，即可做车道线检测。

### 全景拼接

相机绕光心旋转拍摄多张照片，相邻两张用 H 拼接即可（OpenCV Stitcher 自动处理）。

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| findHomography RANSAC (100点) | < 5 ms | CPU |
| warpPerspective | ~5 ms/MPix | CPU |

## 选型建议

**适用场景**：文档扫描/矫正、逆透视变换 IPM（车道鸟瞰）、AR 平面跟踪、全景拼接（纯旋转）、张正友标定、图像配准

**不适用场景**：仅平面/纯旋转成立、有深度差时错位、点共线退化

