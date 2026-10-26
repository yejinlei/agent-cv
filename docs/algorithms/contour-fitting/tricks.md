---
outline: deep
---

# 第 7 页 · 调参口诀

## 一句话调参口诀

```
epsilon 用周长百分比、方件看顶点数、圆件用椭圆、噪声大就上 RANSAC。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|------|------|--------|----------|----------|
| epsilon | 逼近精度 | **周长 1%~2%** | 更简，丢角点 | 更细，点多 |
| closed | 是否闭合 | **True** | 强行连首尾 | 断成折线 |
| method | 轮廓存储方式 | **SIMPLE** | 记全部点 | 只记拐点，更快 |

## 实战技巧

### 形状分类套路

先 approxPolyDP，若逼近成 4 点判为矩形、3 点判三角、点数很多再判圆。

### 和面积配合

用 contourArea / minAreaRect 面积之比判断「矩形度」，比值接近 1 说明是规整矩形。

### 尺寸测量

minAreaRect 的 size 直接给出长宽（像素），配合标定比例尺即可换算实际尺寸。

## 性能参考

| 条件 | 耗时 | 说明 |
|------|------|------|
| 单条 500 点轮廓，epsilon=1% | ≈0.05 ms | Douglas-Peucker 极快 |
| 1000 条轮廓批量逼近 | ≈20 ms | 工业质检常见规模 |
| fitEllipse 单条轮廓 | ≈0.02 ms | 最小二乘，点越多略微变慢 |

## 选型建议

**适合用**：工业零件尺寸测量、车牌/纸面矫正、形状分类、手写笔迹简化、地图边界压缩

**不适合用**：epsilon 太大会丢角点、椭圆拟合对离群点敏感（需鲁棒版）、只对单连通轮廓有效

::: tip 一句话
把一坨几百个点的轮廓，压成几条线、一个圆或一个椭圆
:::

<!-- AUTO-EXTENSION-2 -->

## 🎯 实战四件套（检测形状）

```python
for cnt in contours:
    approx = cv2.approxPolyDP(cnt, 0.04*cv2.arcLength(cnt, True), True)
    if len(approx) == 3: shape = "三角形"
    elif len(approx) == 4:
        x,y,w,h = cv2.boundingRect(approx)
        ar = w/float(h)
        shape = "正方形" if 0.95<ar<1.05 else "矩形"
    elif len(approx) == 5: shape = "五边形"
    elif len(approx) > 8: shape = "圆形"
```
