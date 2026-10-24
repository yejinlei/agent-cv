# SURF 实战踩坑

## 坑 1：专利！专利！专利！

### 症状
- OpenCV 3.x 之后 `cv2.SURF()` 直接找不到
- 需要安装 `opencv-contrib-python`
- 某些版本（OpenCV 4.x）连 contrib 都默认不编译 SURF，需要从源码编译打开 `OPENCV_ENABLE_NONFREE=ON`

### 根因
SURF 专利归 ETH Zurich 与 KU Leuven 所有，**在美国 2026 年前后陆续到期，但欧洲/中国保护期更长**。OpenCV 主分支为避免法律风险，把它放到 `xfeatures2d`（"非自由模块"）里。

### 避坑
```bash
# 尽量找带专利模块的版本（老版 Python 更容易装）
pip install opencv-contrib-python==3.4.2.17  # 经典兼容版
# 或者
pip install opencv-contrib-python  # 最新版部分版本仍包含
```

**工程选型建议**：
- 科研、个人项目、不打算闭源销售 → SURF 可以用
- 商业化产品、SDK、手机 App → **直接用 ORB / AKAZE / SIFT（SIFT 专利已过期）**

## 坑 2：`hessianThreshold` 设太小，关键点爆炸

### 症状
- `hessianThreshold=100` 时，一张图能出几万个点，匹配巨慢
- 内存暴涨（描述子 N×64 float）
- 错误匹配大量增加

### 根因
阈值越低，越弱的纹理也被当作关键点。**SURF 的阈值单位比 SIFT 大**，SIFT 用 0.04（contrastThreshold），SURF 默认 400，量级差 1 万倍。

### 避坑

| 场景 | 推荐阈值 |
|---|---|
| 纹理丰富、要密点 | 100 ~ 300 |
| 通用场景（默认） | **400 ~ 500** |
| 只想要最稳定点 | 800 ~ 1500 |
| 大尺寸图片（>2000px） | 600 ~ 1000 |

```python
# 先试默认 500，根据点数再调
surf = cv2.xfeatures2d.SURF_create(500)
kp, des = surf.detectAndCompute(img, None)
print(f"点个数: {len(kp)}")  # 一般控制在几百 ~ 几千
```

## 坑 3：U-SURF（upright）用错场景导致匹配失败

### 症状
- 设了 `upright=True` 想提速，结果旋转图像后匹配率断崖式下降
- 或者反过来：图像明明不旋转，却设了 `upright=False`，白白浪费时间

### 根因
`upright=True` 跳过方向分配步骤，描述子不做旋转对齐。图像旋转超过 10°~15° 时，描述子对不上。

### 避坑

| 场景 | upright |
|---|---|
| 手机竖屏拍照匹配、SLAM、全景拼接 | **False（默认）** |
| 扫描文档、票据识别（图像方向固定） | **True**（快 15%） |
| 工业检测（相机固定朝下） | **True** |

## 坑 4：灰度图才能用，忘了转灰度

### 症状
```
error: (-215:Assertion failed) !_src.empty() && (_src.depth() == CV_8U || _src.depth() == CV_32F) ...
```

### 根因
SURF 算法本体只接受**单通道**灰度图。直接传 3 通道 BGR，OpenCV 有些版本会报错，有些版本会默默取第一个通道但结果不对。

### 避坑
```python
img = cv2.imread('xxx.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 必须
kp, des = surf.detectAndCompute(gray, None)
```

## 坑 5：64 维 vs 128 维混用导致匹配崩溃

### 症状
```
OpenCV(4.5.5) error: (-5:Bad argument) ...
```
或者 `knnMatch` 直接崩溃。

### 根因
一张图用 `extended=False`（64 维），另一张图用 `extended=True`（128 维），描述子维度不一致，BFMatcher/FLANN 不答应。

### 避坑
```python
# 两张图必须用同一个 SURF 实例
surf = cv2.xfeatures2d.SURF_create(500, extended=False)
kp1, des1 = surf.detectAndCompute(gray1, None)  # 64 维
kp2, des2 = surf.detectAndCompute(gray2, None)  # 也是 64 维 ✓
```

## 坑 6：FLANN 参数没设对，匹配速度不如暴力匹配

### 症状
- 关键点少（<1000）时，用 FLANN 反而比 BFMatcher 慢
- 或者 matches 报错"query desc is empty"

### 根因
FLANN 是基于 KD-Tree 的近邻算法，**规模小的时候建树开销大于查询收益**。

### 避坑
```python
if len(kp1) < 1000 or len(kp2) < 1000:
    # 点少直接暴力
    bf = cv2.BFMatcher(cv2.NORM_L2)
    matches = bf.knnMatch(des1, des2, k=2)
else:
    # 点多用 FLANN
    FLANN_INDEX_KDTREE = 1
    flann = cv2.FlannBasedMatcher(
        dict(algorithm=FLANN_INDEX_KDTREE, trees=5),
        dict(checks=50)
    )
    matches = flann.knnMatch(des1, des2, k=2)
```

## 坑 7：大尺度场景下 octave 不够

### 症状
- 匹配大小悬殊的物体（比如一张 500px 的小图和一张 2000px 大图里的对应物体）匹配不上
- 大尺寸物体的关键点都丢了

### 根因
默认 `nOctaves=4` 只覆盖尺度 ~1.2 ~ 10。**如果物体尺度差超过 10 倍**，需要加 octave 数，或者先把图像**统一尺寸**。

### 避坑
```python
surf = cv2.xfeatures2d.SURF_create(
    hessianThreshold=400,
    nOctaves=5,       # 多一级，覆盖更大尺度
    nOctaveLayers=4
)
```

## 坑 8：mask 参数没用上导致关键点出现在不想要的地方

### 症状
- 图像边框、黑边、水印上出了一堆关键点干扰匹配
- 拼接时不想让天空、墙面这种低纹理区出点

### 根因
`detectAndCompute` 的第二个参数就是 mask，默认 None（全图算）。

### 避坑
```python
mask = np.ones(img.shape, dtype=np.uint8)
mask[:20, :] = 0    # 屏蔽顶部 20 像素
mask[-20:, :] = 0   # 屏蔽底部 20 像素
mask[:, :20] = 0    # 屏蔽左边
mask[:, -20:] = 0   # 屏蔽右边
kp, des = surf.detectAndCompute(img, mask)
```

## 坑 9：以为 SURF 是彩色的

### 症状
- 想对彩色图分别提 RGB 三通道特征
- 结果发现 SURF 不直接支持彩色

### 根因
SURF 设计时就是灰度算法。OpenCV 的 SURF 不支持彩色。

### 避坑
真要彩色特征，手动分通道提然后拼起来：
```python
b, g, r = cv2.split(img_color)
kp_b, des_b = surf.detectAndCompute(b, None)
kp_g, des_g = surf.detectAndCompute(g, None)
kp_r, des_r = surf.detectAndCompute(r, None)
# 把 kp 按通道加偏移、des 拼起来即可（但要自己管理）
```
一般没必要，灰度通常已经够用。

## 常见错误速查表

| 错误信息 | 原因 | 解法 |
|---|---|---|
| `module 'cv2' has no attribute 'xfeatures2d'` | 没装 contrib 或版本太新 | `pip install opencv-contrib-python==3.4.2.17` |
| `The function/feature is not implemented` | 编译时没开 NONFREE | 用老版本 contrib，或换 ORB/SIFT |
| `(-215) _src.type() == CV_8UC1` | 没转灰度 | `cv2.cvtColor(img, COLOR_BGR2GRAY)` |
| 描述子是 None | 阈值太高/图像全黑 | 调低 hessianThreshold、检查图像 |
| 匹配点全是错的 | 没做比值检验 | Lowe ratio test (0.75) |
| 内存暴涨 | 阈值太低点太多 | 把阈值调到 400+ |
