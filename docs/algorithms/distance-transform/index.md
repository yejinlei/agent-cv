<AlgorithmCard
  name="距离变换"
  enName="Distance Transform"
  chapter="ch03"
  branch="image-processing"
  year="1966"
  author="Azriel Rosenfeld / John Pfaltz / Gunilla Borgefors"
  paper="Rosenfeld & Pfaltz 1966 / Borgefors 1986"
  level="low"
  tagline="给二值图每个像素发一张「到最近墙有多远」的地图，中心最远、边缘最近；分水岭、骨架、点匹配都要靠它"
  analogy="想象在一个漆黑的迷宫里（白色=能走，黑色=墙），给每个位置标出「离最近一堵墙有几步」：墙根是 0，走廊中间是大数字，大厅正中央是最大的数。画成热力图，最亮的地方就是「整个区域的脊梁」——这就是距离变换。"
  scene="分水岭分割的种子生成、目标骨架提取、二值图匹配（chamfer matching）、形态学细化、医学影像中心线提取、文字识别的字宽估计。"
  :pros='["O(N) 复杂度（两次扫描）", "结果稳定、可解释", "是分水岭、骨架、匹配等算法的基础", "OpenCV 一行调用"]'
  :cons='["输入必须是干净的二值图（0/1 或 0/255）", "不同距离类型精度不同（L1/L2/C）", "边界条件要注意", "距离类型选错会导致结果偏差"]'
/>


## 一分钟速览

**距离变换**（Distance Transform，1966，Azriel Rosenfeld / John Pfaltz / Gunilla Borgefors）
对二值图做两次反向扫描，用 3×3 邻域最小距离递推，得到每个前景点到最近背景的距离图——形态学、分割、匹配的底层积木。

<ChildPages />
