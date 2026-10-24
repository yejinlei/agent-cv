# 形态学操作 · 调参口诀

<AlgorithmCard
  name="形态学操作"
  enName="Mathematical Morphology"
  chapter="ch-4-image-enhancement"
  branch="image-processing"
  year="1964"
  author="G. Matheron / J. Serra"
  paper="—"
  level="basic"
  tagline="膨胀、腐蚀、开、闭、顶帽黑帽——五把瑞士军刀帮你清理图像里的小毛刺和黑洞"
  analogy="形态学就像一套木匠的打磨工具：腐蚀像用砂纸把凸起毛刺磨掉，膨胀像给凹坑补腻子，开运算像「先磨毛刺再补漆」（去小白点），闭运算像「先补漆再磨平」（填小黑洞）"
  scene="二值图去噪、孔洞填充、边缘提取、骨架提取、字符识别预处理、OCR、工业缺陷检测"
  :pros='["速度极快", "效果直观可控", "组合能力强", "支持任意核形状", "CPU 实时"]'
  :cons='["核大小/形状需调", "大核慢", "过度腐蚀/膨胀丢信息", "对边界细节破坏"]'
/>

## 形态学操作 调参口诀

```
腐蚀取最小、膨胀取最大，先腐后膨是开、先膨后腐是闭；
开去掉亮刺、闭填好黑洞，顶帽提亮、黑帽提暗；
核形状看目标：方块用矩形、圆用椭圆、十字对十字线；
核大小 3 起步，不够加 iterations 不要直接上大核；
灰度图也能做，最小最大当滤波；
OCR 之前闭一开，文字笔画变干净。
```

## 参数速查表

| 参数 | 含义 | 推荐值 | 调大效果 | 调小效果 |
|---|---|---|---|---|
| kernel shape | 核形状 | **RECT/ELLIPSE** | — | — |
| kernel size | 核大小（奇数） | **3** | 处理大块 | 保留细节 |
| iterations | 迭代次数 | **1** | 效果强 | 温和 |

## 实战技巧

### OCR 预处理经典流程

```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
# 去掉小噪声点 + 填充字符内部小洞
k = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, k)   # 去噪点
binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, k)  # 填洞
```

### 背景不均匀校正（顶帽）

```python
# 不均匀光照背景：用大核做闭运算得到背景
bg = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT,(31,31)))
corrected = cv2.subtract(gray, bg)   # 顶帽效果
```

### 提取水平/垂直线

用长条形核提取某个方向的线：
```python
# 水平线
h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30,1))
horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_kernel)
# 垂直线
v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,30))
vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, v_kernel)
```

## 性能参考

| 条件 | 耗时 | 说明 |
|---|---|---|
| 3×3 腐蚀/膨胀 | ~1 ms/MPix | CPU SIMD 优化 |
| 开/闭运算 | ~2 ms/MPix | 腐蚀+膨胀各一次 |
| 大核 (21×21) | ~10 ms/MPix | 可用多次 3×3 替代 |

## 选型建议

**适用场景**：二值图去噪、孔洞填充、边缘提取、骨架提取、字符识别预处理、OCR、工业缺陷检测

**不适用场景**：核大小/形状需调、大核慢、过度腐蚀/膨胀丢信息

