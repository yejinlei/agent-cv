# 调参技巧：连通域分析（Two-Pass）

## 五字口诀

****二值净、两趟扫、从 1 数、按面筛****

## 调参顺序（按这个顺序调，少走弯路）

1. 二值化必须干净（先开运算）
2. connectivity 选对（字符 4、一般 8）
3. `connectedComponentsWithStats` 一次性拿所有信息
4. **按面积过滤** stats[i, CC_STAT_AREA]，保留目标大小范围
5. 需要形状再对每个 mask 用 findContours

## 与其他算法的搭配组合

- **MOG2 → 连通域 → 按面积筛**：视频监控里数前景目标
- **阈值化 → 连通域 → OCR**：字符分割先把每个字切出来
- **阈值化 → 连通域 → 按圆度筛**：检测圆形/球形缺陷
- **连通域筛选 → GrabCut 初始化**：用连通域 bbox 作为 GrabCut 输入

## 调优 Checklist

- [ ] 图像已做必要的预处理（二值化 + 开运算去噪）
- [ ] 核心参数已按场景粗调到合理区间
- [ ] 输出结果做了必要的后处理（按面积/宽高比过滤）
- [ ] 速度/精度做了 benchmark

<!-- AUTO-EXTENSION -->

## 🎯 典型 5 行用法

```python
n, labels, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)
for i in range(1, n):  # 0 是背景
    x, y, w, h, area = stats[i]
    if area < 100 or area > 10000:
        continue  # 过滤太小太大
    cx, cy = centroids[i]
    cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
```

### 实战 5 条

1. **二值化要先做干净**：连通域对"粘连"非常敏感——两个米粒有一个像素桥连在一起就会被标成一个；必要时先做开运算；
2. **lType 用 CV_32S 而不是 CV_16U**：后者最大只能标 65535 个连通域，大图容易溢出；
3. **面积过滤是必做的后处理**：二值化后总有噪声小点点；
4. **重心比外接矩形中心更准**：外接矩形中心在矩形几何中点，重心（centroids）才是物体真实中心；
5. **圆形度 = 4π·area / perimeter²**：完美圆 = 1，越扁越小，用于区分"圆形缺陷"和"长条形划痕"。
