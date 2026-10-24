<AlgorithmCard
  name="区域生长分割"
  enName="Region Growing"
  chapter="ch10"
  branch="segmentation"
  year="1994"
  author="Rolf Adams / Leanne Bischof (Seeded Region Growing)"
  paper="Adams & Bischof, TPAMI 1994"
  level="mid"
  tagline="几颗种子丢进图里，像水一样往四周漫，只灌和自己「颜色相近」的地方，最后把图切成几块"
  analogy="想象你在山顶泼几杯染料（不同颜色），染料顺着山坡往下流，只往颜色和自己差不多的地方跑（因为颜色差大代表「不是同一个物体」），最后不同色块自然分出了边界——这就是区域生长。"
  scene="医学影像分割（肿瘤/器官）、交互式抠图（用户点几下就能分出物体）、遥感影像地块分割、工业检测里颜色一致区域的提取。"
  :pros='["原理直观，容易解释给非技术同事", "交互式（种子由用户指定）", "能处理任意形状区域", "边界闭合", "对初始种子鲁棒性较好"]'
  :cons='["需要种子点（人工或自动）", "阈值/相似性准则选择敏感", "串行算法较慢（BFS 按像素优先级）", "对噪声敏感（需要预处理）", "容易漏过分水岭式的细长连接"]'
/>


## 一分钟速览

**区域生长分割**（Region Growing，1994，Rolf Adams / Leanne Bischof (Seeded Region Growing)）
从种子出发用优先级队列向外扩散，每次把最像当前区域的邻域像素吸进来，动态更新区域统计量，直到所有像素都被吸进某个区域——最直觉也最经典的区域分割算法。

<ChildPages />
