# SGM 半全局立体匹配 · 踩坑清单

<AlgorithmCard
  name="SGM 半全局立体匹配"
  enName="Semi-Global Matching"
  chapter="ch-14-3d-vision"
  branch="geometry"
  year="2005"
  author="Heiko Hirschmüller"
  paper="—"
  level="advanced"
  tagline="双目测距的工业标准，8 个方向做平滑约束，又快又稳出稠密视差图"
  analogy="BM 块匹配像个没耐心的小孩，只看自己周围一小圈就乱猜；SGM 像个老练的侦探，从上下左右斜 8 个方向打听消息，让相邻像素的深度差不多，拼出连贯的深度图"
  scene="双目深度相机（RealSense、自动驾驶双目）、无人机避障、机器人导航、三维重建、工业检测"
  :pros='["稠密视差图", "速度可接受(CPU实时)", "精度经典最高", "OpenCV内置StereoSGBM", "参数可解释"]'
  :cons='["参数多", "无纹理区域失败", "重复纹理误匹配", "需要精确标定", "远处深度误差大"]'
/>

## SGM 半全局立体匹配 的常见坑

::: danger 坑：numDisparities 不是 16 的倍数
**现象**：报错或结果奇怪。

**解决**：**numDisparities 必须是 16 的整数倍**（16/32/48/…/256）。
:::

::: danger 坑：P1/P2 乱填
**现象**：视差图要么全是阶梯状（平滑过强），要么全是噪声（平滑不足）。

**解决**：**P1=8·3·block²，P2=32·3·block²** 是官方推荐；P2 一般是 P1 的 4 倍。
:::

::: danger 坑：忘记除以 16.0
**现象**：视差值都是 16 的倍数（看起来有 16 层阶梯）。

**解决**：SGBM 输出是**定点 16 位小数**（4 位小数），必须 `.astype(np.float32)/16.0`。
:::

::: danger 坑：minDisparity 设错
**现象**：目标很近但 minDisparity 太大，导致前景一片黑。

**解决**：minDisparity 默认 0；如果相机有会聚角导致无穷远视差不为 0，需要调整。
:::

::: danger 坑：没做双目标定/校正直接喂图
**现象**：视差图满屏噪声。

**解决**：SGBM **必须**基于校正后的图（极线水平）。先 `stereoCalibrate + stereoRectify + initUndistortRectifyMap + remap`。
:::

::: danger 坑：没有 WLS 后处理，视差图全是孔洞
**现象**：直接用 SGBM 输出，很多无效区域（值=min_disp-1）。

**解决**：**强烈建议用 DisparityWLSFilter**，同时配 disp12MaxDiff、speckle 过滤。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

