# PnP 位姿估计 · 踩坑清单

<AlgorithmCard
  name="PnP 位姿估计"
  enName="Perspective-n-Point"
  chapter="ch-14-3d-vision"
  branch="geometry"
  year="1841/2009(EPnP)"
  author="Grunert / Lepetit(EPnP)"
  paper="—"
  level="advanced"
  tagline="已知几个 3D 点和它们在图上的位置，反推出相机在哪里看——AR 和机器人抓取的基石"
  analogy="你站在房间里，认出了墙上的钟、桌上的杯子、书架上的花盆——这三个东西真实位置你知道，就能反推出自己站在房间的什么地方、朝什么方向看"
  scene="AR 标记跟踪、机械臂抓取、视觉伺服、无人机着陆、AR 虚拟物体叠加、SLAM 位姿求解"
  :pros='["最少 3 点可解(P3P)", "毫秒级", "RANSAC 鲁棒", "OpenCV 内置多种方法", "精度高"]'
  :cons='["需要已知内参", "3D 点精度要高", "点共面/共线退化", "对外点敏感", "单位易搞错"]'
/>

## PnP 位姿估计 的常见坑

::: danger 坑：点不够或共面/共线
**现象**：4 个点共线或共面时解不稳定，出现奇怪的位姿。

**解决**：至少 **6 个非共面 3D 点**，分布在 Z 方向上有层次；最少 4 点但要用 P3P。
:::

::: danger 坑：内参没标定或不准
**现象**：重投影误差 5+ 像素，位姿完全错。

**解决**：PnP 对 K 敏感，**必须先标定内参**（重投影误差 < 0.3 像素）。
:::

::: danger 坑：3D 点单位和 t 单位搞混
**现象**：算出来 t 数值是 0.05 以为 5cm 结果是 50cm，差 10 倍。

**解决**：**t 的单位 = 你 3D 点的单位**。常用 mm 全部 mm、m 全部 m。
:::

::: danger 坑：忘记 Rodrigues 把 rvec 转 R
**现象**：直接把 rvec 当旋转矩阵用，结果报错。

**解决**：PnP 返回的是**旋转向量**（axis-angle，3 个元素），不是矩阵。需要 `cv2.Rodrigues(rvec)` 转 3×3 矩阵。
:::

::: danger 坑：用 solvePnP 不用 RANSAC 版本
**现象**：2D 点有几个误匹配，结果直接偏 30°。

**解决**：实际场景**永远用 solvePnPRansac**；只有在仿真或点 100% 可靠时才用 solvePnP。
:::

::: danger 坑：2D 点 dtype 不对
**现象**：报 OpenCV(4.x) error or (-215) 错误。

**解决**：obj_pts 和 img_pts 必须是 `np.float32`（不能是 float64），形状是 (N,1,2) 或 (N,2)。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

