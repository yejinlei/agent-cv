# ⚙ 调参口诀

## 口诀

> **KCF 快 CSRT 稳，MOSSE 跑上无人机；PSR 小于六别更新，学习率小不漂移。**

## 选型开关

| 场景 | 推荐跟踪器 |
| --- | --- |
| 嵌入式/无人机/极高速 | MOSSE |
| CPU 实时单目标平衡 | **KCF** |
| 尺度变化/旋转/最稳精度 | CSRT |
| 有 GPU / 多人脸/长时 | MedianFlow + YOLO 重检测 |
| 多目标且要 ID 保持 | DeepSORT（KCF/卡尔曼+ReID）|

## KCF 的关键参数（OpenCV）

| 参数 | 默认 | 建议 | 说明 |
| --- | --- | --- | --- |
| `sigma` | 0.2 | 0.2~0.5 | 高斯核带宽，越大容忍形变越多 |
| `lambda` | 0.0001 | 1e-4 | 正则项，越大越保守 |
| `interp_factor` | 0.02 | 0.005~0.02 | 学习率，越大跟得快但易飘 |
| `resize` | True | True | 是否缩小到固定大小加速 |
| `detect_threshold` | 0.5 | 0.4~0.6 | 响应峰值阈值 |

## 5 条黄金法则

1. **永远做 PSR 跟丢判断**，不要盲目 update。
2. **第一帧框要严**——宁可框紧一点，不要带太多背景。
3. **学习率不要大于 0.02**，否则漂移是早晚的事。
4. **遮挡期停止更新**，比加复杂特征管用。
5. **KCF 是短时跟踪器**，长时间跑必须配检测器。

<!-- AUTO-EXTENSION -->

## 🎯 调参与替换指南

### 如果发现 KCF 不好用，按顺序检查

1. **框是不是太大**？框里一半是背景 → 重新初始化，给紧一点；
2. **目标是不是尺度在变**？换 **DSST/CSRT**（它们内置尺度估计）；
3. **是不是经常被挡**？换 **CSRT**（它有遮挡检测+重检测）；
4. **是不是要极高帧率 >200fps**？换 **MOSSE**（牺牲精度换速度）；
5. **是不是旋转剧烈**？KCF 对平面外旋转很差，用 **CSRT** 或基于深度学习的跟踪器。

### KCF vs CSRT vs MOSSE 一张图说清

<div style="text-align:center">
<svg xmlns="http://www.w3.org/2000/svg" width="720" height="170" style="background:#fafbfc;border-radius:12px;border:1px solid #eaecef">
  <g transform="translate(20,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#e67e22">KCF</text>
    <text x="100" y="35" text-anchor="middle" font-size="11" fill="#555">核相关滤波 · 通用</text>
    <rect x="0" y="45" width="200" height="25" fill="#eee"/>
    <rect x="0" y="45" width="140" height="25" fill="#e67e22"/>
    <text x="100" y="62" text-anchor="middle" font-size="10" fill="#fff">速度 70%</text>
    <rect x="0" y="75" width="200" height="25" fill="#eee"/>
    <rect x="0" y="75" width="130" height="25" fill="#e67e22"/>
    <text x="100" y="92" text-anchor="middle" font-size="10" fill="#fff">精度 65%</text>
    <rect x="0" y="105" width="200" height="25" fill="#eee"/>
    <rect x="0" y="105" width="60" height="25" fill="#e67e22"/>
    <text x="100" y="122" text-anchor="middle" font-size="10" fill="#333">抗遮挡 30%</text>
  </g>
  <g transform="translate(260,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#27ae60">CSRT</text>
    <text x="100" y="35" text-anchor="middle" font-size="11" fill="#555">信道与空间可靠性 · 准</text>
    <rect x="0" y="45" width="200" height="25" fill="#eee"/>
    <rect x="0" y="45" width="80" height="25" fill="#27ae60"/>
    <text x="100" y="62" text-anchor="middle" font-size="10" fill="#333">速度 40%</text>
    <rect x="0" y="75" width="200" height="25" fill="#eee"/>
    <rect x="0" y="75" width="180" height="25" fill="#27ae60"/>
    <text x="100" y="92" text-anchor="middle" font-size="10" fill="#fff">精度 90%</text>
    <rect x="0" y="105" width="200" height="25" fill="#eee"/>
    <rect x="0" y="105" width="160" height="25" fill="#27ae60"/>
    <text x="100" y="122" text-anchor="middle" font-size="10" fill="#fff">抗遮挡 80%</text>
  </g>
  <g transform="translate(500,10)">
    <text x="100" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="#9b59b6">MOSSE</text>
    <text x="100" y="35" text-anchor="middle" font-size="11" fill="#555">最小输出平方误差 · 极快</text>
    <rect x="0" y="45" width="200" height="25" fill="#eee"/>
    <rect x="0" y="45" width="195" height="25" fill="#9b59b6"/>
    <text x="100" y="62" text-anchor="middle" font-size="10" fill="#fff">速度 98%</text>
    <rect x="0" y="75" width="200" height="25" fill="#eee"/>
    <rect x="0" y="75" width="90" height="25" fill="#9b59b6"/>
    <text x="100" y="92" text-anchor="middle" font-size="10" fill="#333">精度 45%</text>
    <rect x="0" y="105" width="200" height="25" fill="#eee"/>
    <rect x="0" y="105" width="30" height="25" fill="#9b59b6"/>
    <text x="100" y="122" text-anchor="middle" font-size="10" fill="#333">抗遮挡 15%</text>
  </g>
</svg>
</div>

**口诀**：
> **要稳要准用 CSRT，要快要通用 KCF，几百帧跑嵌入式用 MOSSE。**
