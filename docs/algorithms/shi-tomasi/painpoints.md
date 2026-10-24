# Shi-Tomasi 角点 (GFTT) · 踩坑清单

<AlgorithmCard
  name="Shi-Tomasi 角点 (GFTT)"
  enName="Shi-Tomasi / Good Features to Track"
  chapter="ch-8-local-feature"
  branch="feature-detection"
  year="1994"
  author="Jianbo Shi / Carlo Tomasi"
  paper="—"
  level="mid"
  tagline="把 Harris 响应函数换成 min(λ1,λ2)，一个参数不用调，工程界角点首选"
  analogy="Harris 像个老中医用「阴阳失调公式」判断亚健康，还要调一个神秘的 k；Shi-Tomasi 直接看你「最差的那一科成绩」——只要最差那一科也及格，你就是好学生"
  scene="光流跟踪（goodFeaturesToTrack+calcOpticalFlowPyrLK 是标配）、相机标定棋盘角点、视频稳像"
  :pros='["无需调 k 参数", "响应值物理意义明确", "自带 minDistance 防扎堆", "能限制 top-N 数量"]'
  :cons='["不具尺度/旋转不变", "需要定 qualityLevel", "分布不均时扎堆", "不含描述子"]'
/>

## Shi-Tomasi 角点 (GFTT) 的常见坑

::: danger 坑：qualityLevel 太高导致点太少
**现象**：qualityLevel=0.1 或更大时，弱纹理区域一个点都检测不到。

**解决**：默认从 **0.01** 起步；弱纹理/模糊图降到 0.005。
:::

::: danger 坑：minDistance 太小导致角点扎堆
**现象**：minDistance=3 时，一个角点周围能出 5、6 个点。

**解决**：光流跟踪建议 **10**；标定建议 20–30；想多点设为 5。
:::

::: danger 坑：直接拿 Shi-Tomasi 点做长时跟踪
**现象**：光流有累计漂移，跟踪 100 帧后点会跑到同一处。

**解决**：必须做 **前向后向一致性检验**，并每 20–30 帧重检测一次点。
:::

::: danger 坑：以为 Shi-Tomasi 有尺度不变
**现象**：图放大后点完全对不上。

**解决**：Shi-Tomasi 固定窗口，**没有尺度不变性**。多尺度场景用 SIFT/ORB。
:::

::: danger 坑：在强噪声图上直接检测
**现象**：噪声会被 Sobel 放大，出现大量假角点。

**解决**：检测前先高斯模糊（sigma=1）：`gray = cv2.GaussianBlur(gray, (3,3), 1.0)`。
:::

::: danger 坑：useHarrisDetector 参数理解错
**现象**：以为 True 时 Harris 更好；实际上光流场景 Shi-Tomasi 更合适。

**解决**：光流/跟踪永远用 `useHarrisDetector=False`（默认）。
:::

## 调试建议

1. **先可视化中间结果**——不要看最终输出，要一步步看每个中间步骤对不对
2. **先用小图、简单图测试**——确认 pipeline 跑通再上真实场景
3. **参数先从默认值开始**——不要一上来就乱调，有 baseline 再改
4. **对比参考实现**——拿 OpenCV tutorial 或官方 sample 对比自己的结果

