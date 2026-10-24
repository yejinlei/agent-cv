# MSER 最大稳定极值区域 · 调参口诀

<AlgorithmCard
  name="MSER 最大稳定极值区域"
  enName="Maximally Stable Extremal Regions"
  chapter="ch-8-local-feature"
  branch="feature-detection"
  year="2002"
  author="Jiri Matas et al."
  paper="—"
  level="mid"
  tagline="像往黑白照片上浇水，颜色深浅慢慢渗开，那些形状最稳定的水坑就是好区域"
  analogy="把灰度图想象成一块地形，从黑到白慢慢淹水：一开始只有最深的坑有水，水涨后水面扩大。那些「水位变一点、水面大小几乎不变」的湖泊，就是最稳定的区域——MSER"
  scene="宽基线立体匹配、文本检测（自然场景文字）、目标识别、对仿射变换要求高的场景"
  :pros='["仿射不变性", "多尺度区域检测", "无需预设阈值", "对光照鲁棒", "形状任意"]'
  :cons='["对模糊敏感", "速度较慢", "参数 delta/minArea/maxArea 要调", "不适合低对比度"]'
/>

## MSER 最大稳定极值区域 调参口诀

```
delta 设 5 是默认，步长太大稳定点难寻；
min_area 六十、max 万一四，看图像尺寸来调整；
max_variation 零点二五，太大出一堆小区域；
文字检测天然擅长，自然场景文字它称王；
仿射不变是绝活，宽基线匹配都选它；
输出是区域不是点，记得拟合椭圆再提描述。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| _delta | 阈值步长 | **5** | 稳定但数量少 | 数量多但噪声大 |
| _min_area | 最小区域面积 | **60** | 去噪 | 检小目标 |
| _max_area | 最大区域比例 | **5% 图像** | 去大区域（天空） | 允许大目标 |
| _max_variation | 最大 q 值 | **0.25** | 只保留稳定的 | 容忍不稳定 |

## 实战技巧

### 文本检测经典组合

MSER + 几何过滤（宽高比、面积、占空比）+ 纹理过滤（笔画宽度）是 OpenCV3 text 模块和传统场景文本检测的经典组合：
```python
# OpenCV 文本检测 API（需 opencv-contrib）
swt = cv2.text.createStrokeWidthTransform()
erd = cv2.text.createERFilterNM1()```

### 颜色 MSER

对彩色图，在 RGB 三通道分别跑 MSER 然后合并，能检测更多彩色区域。

### 转换为仿射协变区域

```python
for region in regions:
    (x,y),(w,h),angle = cv2.fitEllipse(region)
    # 然后用这个椭圆做仿射归一化到圆形 patch
```

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| MSER detectRegions (640×480) | ~50–100 ms | CPU 单线程 |
| vs SIFT (同样图) | ~200 ms | SIFT 检测+描述 |

## 选型建议

**适用场景**：宽基线立体匹配、文本检测（自然场景文字）、目标识别、对仿射变换要求高的场景

**不适用场景**：对模糊敏感、速度较慢、参数 delta/minArea/maxArea 要调

