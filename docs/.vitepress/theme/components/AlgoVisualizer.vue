<template>
  <div v-if="isMounted" class="algo-vis">
      <div class="vis-card">
        <div class="vis-title">🧪 {{ titleMap[type] || type }}</div>
        <p class="vis-desc">{{ descMap[type] || '' }}</p>
        <canvas ref="canvasRef" :width="W" :height="H" class="algo-canvas"></canvas>
        <div class="ctrl-row">
          <template v-for="c in (ctrls[type] || [])" :key="c.k">
            <label>{{ c.label }} = <b>{{ typeof c.v.value === "number" ? (c.step < 1 ? c.v.value.toFixed(2) : c.v.value) : c.v.value }}</b></label>
            <input type="range" :min="c.min" :max="c.max" :step="c.step || 1" v-model.number="c.v.value" @input="schedule()"/>
          </template>
          <template v-for="b in (btns[type] || [])" :key="b.label">
            <button @click="b.k()">{{ b.label }}</button>
          </template>
        </div>
        <div class="explain" v-html="explainMap[type] || ''"></div>
      </div>
    </div>
</template>

<script setup>
import {ref, reactive, onMounted, onBeforeUnmount, nextTick} from 'vue'

const W = 640, H = 320
const props = defineProps({ type: { type: String, required: true } })
const canvasRef = ref(null)
const isMounted = ref(false)
let rafPending = false
let unmounted = false

function ctx() {
  const c = canvasRef.value
  return c ? c.getContext('2d') : null
}
function schedule() {
  if (rafPending || unmounted) return
  rafPending = true
  requestAnimationFrame(() => {
    rafPending = false
    if (unmounted) return
    const c = ctx()
    const fn = drawers[props.type]
    if (c && fn) {
      try { fn(c) } catch (e) {
        // 动画函数报错不要白屏，画一个错误提示
        c.clearRect(0,0,W,H); c.fillStyle='#fff'; c.fillRect(0,0,W,H)
        c.fillStyle='#c0392b'; c.font='14px sans-serif'
        c.fillText('动画渲染出错：' + (e && e.message ? e.message : e), 20, 40)
      }
    }
  })
}

onMounted(() => {
  isMounted.value = true
  // 多重保险：挂载后下一帧画一次，再 50ms/200ms 补画两次（应对水合时序）
  nextTick(()=>{ schedule(); setTimeout(schedule, 50); setTimeout(schedule, 200) })
  // 滑块/参数变化时自动重画：用一个全局 watcher 跟踪所有 ctrl
  const timer = setInterval(schedule, 200)
  onBeforeUnmount(() => { clearInterval(timer) })
})

onBeforeUnmount(() => {
  unmounted = true
  for (const k of Object.keys(_state)) {
    if (_state[k] && typeof _state[k] === 'object' && 'running' in _state[k]) {
      _state[k].running = false
    }
  }
})
const titleMap = {
  'sift': 'SIFT 尺度不变特征变换',
  'surf': 'SURF 加速稳健特征',
  'flann': 'FLANN 快速近似近邻匹配',
  'freak': 'FREAK 视网膜采样描述子',
  'grabcut': 'GrabCut 交互式图割抠图',
  'kcf': 'KCF 核相关滤波跟踪',
  'meanshift': 'MeanShift 均值漂移',
  'mog2': 'MOG2 混合高斯背景建模',
  'sgbm': 'SGBM 半全局立体匹配',
  'icp': 'ICP 迭代最近点配准',
  'triangulation': '三角化恢复深度',
  'bundle': '光束法平差 Bundle Adjustment',
  'dpm': 'DPM 可变形部件模型',
  'camshift': 'CamShift 自适应均值漂移',
  'mosse': 'MOSSE 最小输出平方和误差',
  'csrt': 'CSRT 通道空间可靠性跟踪',
  'vibe': 'ViBe 视觉背景提取器',
  'viola-jones': 'Viola-Jones 级联人脸检测',
  'brief': 'BRIEF 二进制描述子',
  'bovw': 'BoVW 视觉词袋模型',
  'region-growing': '区域生长分割',
  'zhang-calibration': '张氏相机标定法',
  'epipolar': '对极几何与极线约束',
}
const descMap = {
  'sift': '一步步看：高斯金字塔怎么建、DoG怎么找极值点，为什么SIFT尺度旋转都不变。',
  'surf': 'SURF用箱式滤波器近似SIFT的高斯核，积分图算Hessian为什么能快3倍。',
  'flann': 'FLANN为什么比暴力匹配快？KD树一层层把查询点导向最可能的叶子。',
  'freak': 'FREAK模仿人眼视网膜——中心密集、外围稀疏，又快又鲁棒。',
  'grabcut': 'GrabCut用GMM+图割把前景从背景中抠出来，点迭代看收敛。',
  'kcf': 'KCF怎么用循环移位+相关响应做到几百FPS？',
  'meanshift': 'MeanShift怎么一步步漂到密度中心？点单步观察漂移路径。',
  'mog2': '每个像素为什么要维护多个高斯？偏离2.5σ的像素判为前景。',
  'sgbm': 'SGBM怎么算出视差图恢复深度？红色近、蓝色远。',
  'icp': 'ICP怎么把错位点云对齐？蓝点云一步步对齐到红点云。',
  'triangulation': '双目怎么从两个像素坐标算3D深度？视差越大越近，Z=fB/d。',
  'bundle': 'BA微调相机位姿与3D点使重投影误差最小，SLAM后端核心。',
  'dpm': 'DPM=根滤波器+部件+变形代价，比HOG+SVM更鲁棒。',
  'camshift': '在MeanShift基础上自动调整窗口大小和旋转角度，跟踪大小变化的目标。',
  'mosse': '首个实时相关滤波跟踪器(>600FPS)，PSR判断跟踪质量。',
  'csrt': 'CSRT多通道加权+空间可靠性掩码，比KCF准但慢一些。',
  'vibe': '每个像素20个历史样本，接近≥2个判背景；极简、嵌入式友好。',
  'viola-jones': '级联是漏斗：前面快、后面准，大部分窗口第一层就被拒。',
  'brief': '随机点对比亮度拼二进制串，汉明距离一个XOR就出结果，飞快。',
  'bovw': '借鉴文本检索：SIFT→K-Means→视觉词→词频直方图→分类；深度学习之前的王者。',
  'region-growing': '从种子点扩散，灰度差小于阈值T就并入，简单直观但T难选。',
  'zhang-calibration': '打印棋盘格拍几张不同角度照片→求单应→分解内参→优化重投影误差。',
  'epipolar': '左图一个点在右图必落在极线上，搜索从全图缩到一条线——双目/SLAM核心。',
}
const explainMap = {
  'sift': '<ul>\n  <li><b>① 高斯金字塔</b>：对原图不断降采样，每层再与多个不同σ的高斯核卷积，得到同一层不同模糊度的图像。</li>\n  <li><b>② DoG差分</b>：相邻σ图像相减，得到差分-of-Gaussian，模拟Laplacian边缘响应。</li>\n  <li><b>③ 极值检测</b>：在3×3×3的DoG邻域里找极大/极小值，就是候选关键点。</li>\n  <li><b>为什么尺度不变</b>：不同尺度都找，远近都能匹配上。</li>\n</ul>',
  'surf': '<ul>\n  <li><b>箱式滤波</b>：用矩形块近似高斯二阶导，只需常数时间（积分图）。</li>\n  <li><b>Hessian行列式</b>：det(H) = Dxx·Dyy − (0.9·Dxy)²，找极值点。</li>\n  <li><b>比SIFT快3倍</b>：没有复杂σ迭代，所有尺寸的核都用同一套积分图。</li>\n</ul>',
  'flann': '<ul>\n  <li><b>KD树</b>：按特征维度交替切分空间，每维度选中位数作分裂面。</li>\n  <li><b>查询</b>：从根节点逐层比较，沿最近的方向下到叶子；回溯兄弟分支检查是否更近。</li>\n  <li><b>复杂度</b>：暴力匹配O(N)，FLANN约O(logN)，百万点也能秒查。</li>\n</ul>',
  'freak': '<ul>\n  <li><b>视网膜样排布</b>：围绕关键点，中心区域采样密、外围稀疏，共43个预定义点。</li>\n  <li><b>二进制串</b>：对1024对点比较强度，选择其中512对最相关的拼256位串。</li>\n  <li><b>方向估计</b>：用对称点对的梯度和确定主方向，实现旋转不变。</li>\n</ul>',
  'grabcut': '<ul>\n  <li><b>用户画框</b>：框外全是确定背景，框内未知。</li>\n  <li><b>GMM建模</b>：前景/背景各用5个高斯混合，估计每像素属于前景的概率。</li>\n  <li><b>图割最小割</b>：把像素连成图，s/t分别代表前景/背景，min-cut得到分割。</li>\n  <li><b>迭代</b>：用新分割更新GMM参数，再割，直到收敛。</li>\n</ul>',
  'kcf': '<ul>\n  <li><b>循环矩阵</b>：基样本循环移位构造大量负样本，不需显式生成。</li>\n  <li><b>核技巧</b>：把HOG/灰度映射到高维，线性分类器在核空间变非线性。</li>\n  <li><b>频域加速</b>：卷积定理把相关变成逐点乘，FFT O(nlogn)算完。</li>\n  <li><b>峰值即位置</b>：响应图最高的点就是新位置。</li>\n</ul>',
  'meanshift': '<ul>\n  <li><b>核密度估计</b>：以当前点为中心、带宽h为半径，加权统计邻居。</li>\n  <li><b>均值漂移向量</b>：从当前点指向邻居加权重心，就是漂移方向。</li>\n  <li><b>爬山</b>：反复算漂移向量并移动，直到收敛到局部密度极大点。</li>\n</ul>',
  'mog2': '<ul>\n  <li><b>多高斯</b>：每个像素维护3-5个高斯，能处理"树叶晃动/水波"等多峰背景。</li>\n  <li><b>匹配</b>：新像素值若落在某高斯2.5σ内，更新它；否则新建/替换最旧的。</li>\n  <li><b>前景判定</b>：匹配到"背景高斯"（权重高、方差小）为背景，否则为前景。</li>\n</ul>',
  'sgbm': '<ul>\n  <li><b>匹配代价</b>：BT代价/Census，比较左右图像素块相似度。</li>\n  <li><b>代价聚合</b>：沿8/16方向动态规划聚合代价，避免全局匹配的NP难。</li>\n  <li><b>WTA</b>：每像素选代价最小的视差。</li>\n  <li><b>视差→深度</b>：Z = f·B / d，d越大Z越小(越近)。</li>\n</ul>',
  'icp': '<ul>\n  <li><b>找最近点</b>：蓝点每个点找红云中最近的点配成点对。</li>\n  <li><b>SVD求刚体变换</b>：H = Σ (p−p̄)(q−q̄)ᵀ，UΣVᵀ=H，则R=VUᵀ。</li>\n  <li><b>应用变换</b>：更新蓝云位置。</li>\n  <li><b>迭代</b>：直到点对距离平方和收敛。</li>\n</ul>',
  'triangulation': '<ul>\n  <li><b>相似三角形</b>：两个光心OₗOᵣ与3D点P构成三角形，P投影到左右图像得到pₗ,pᵣ。</li>\n  <li><b>视差d=xₗ−xᵣ</b>：点越近，左右投影差越大；点越远d→0。</li>\n  <li><b>深度公式</b>：Z = f·B / d，B为基线(两光心距)，f为焦距。</li>\n</ul>',
  'bundle': '<ul>\n  <li><b>重投影误差</b>：3D点经当前相机投影回2D，与观测像素的距离平方和。</li>\n  <li><b>非线性最小二乘</b>：Levenberg-Marquardt迭代优化相机外参与3D点坐标。</li>\n  <li><b>稀疏性</b>：Hessian矩阵稀疏（每个点只被少数相机看见），Schur补快速求解。</li>\n</ul>',
  'dpm': '<ul>\n  <li><b>根滤波器</b>：粗尺度HOG模板抓整体轮廓。</li>\n  <li><b>部件滤波器</b>：细尺度抓头、肩、腿等细节。</li>\n  <li><b>变形代价</b>：部件偏离"理想位置"的距离乘以弹性系数。</li>\n  <li><b>得分=根分+Σ部件分−Σ变形代价</b>：部件能"动"，处理姿态变化。</li>\n</ul>',
  'camshift': '<ul>\n  <li><b>先跑MeanShift</b>：得到目标中心。</li>\n  <li><b>二阶矩</b>：计算窗口内像素分布的零阶/一阶/二阶矩，得到椭圆方向、轴长。</li>\n  <li><b>自适应</b>：下一帧窗口大小方向都更新。</li>\n  <li>OpenCV老版本的人脸跟踪就用这个（虽不如KCF快）。</li>\n</ul>',
  'mosse': '<ul>\n  <li><b>相关滤波</b>：训练一个滤波器h，使h★样本=期望响应(高斯峰)。</li>\n  <li><b>频域训练</b>：H = G·F* / (F·F*+ε)，只需要几帧初始化。</li>\n  <li><b>PSR指标</b>：(峰值−旁瓣均值)/旁瓣标准差；PSR>10稳定，<7丢失。</li>\n</ul>',
  'csrt': '<ul>\n  <li><b>多通道</b>：HOG+颜色名CN(11维)+灰度+HoN共40+通道。</li>\n  <li><b>空间可靠性</b>：从前景概率图生成掩码，只在目标区域训练。</li>\n  <li><b>通道可靠性</b>：根据各通道响应的PSR加权，自动忽略失效通道。</li>\n  <li>OpenCV里准确率最高的传统跟踪器，就是慢一点。</li>\n</ul>',
  'vibe': '<ul>\n  <li><b>样本集</b>：每像素维护20个历史亮度样本(非参数模型)。</li>\n  <li><b>分类</b>：新像素值与样本比距离，半径内≥2个匹配→背景。</li>\n  <li><b>随机更新</b>：1/φ概率替换自己样本、1/φ概率替换邻居样本，模型自然衰减。</li>\n  <li>无浮点、无高斯拟合，几十行C就能跑，嵌入式首选。</li>\n</ul>',
  'viola-jones': '<ul>\n  <li><b>Haar特征+积分图</b>：矩形差特征O(1)算。</li>\n  <li><b>AdaBoost</b>：从海量Haar特征里挑最有效几十个弱分类器。</li>\n  <li><b>级联结构</b>：10~20层，每层把99%非脸窗口踢掉；真脸全部通过。</li>\n  <li>2001年划时代工作，15fps在当年奔腾机上跑。</li>\n</ul>',
  'brief': '<ul>\n  <li><b>随机采样对</b>：围绕关键点在patch里取n对点(p,q)。</li>\n  <li><b>二进制</b>：I(p)&lt;I(q)→1，否则→0，拼成n位串。</li>\n  <li><b>汉明距离</b>：两个串XOR后POPCNT数1，CPU一条指令算完。</li>\n  <li>比SIFT浮点描述子快几十倍，但无旋转不变(ORB给它补了旋转)。</li>\n</ul>',
  'bovw': '<ul>\n  <li><b>提特征</b>：从所有训练图提SIFT。</li>\n  <li><b>K-Means聚类</b>：聚K个中心作为"视觉单词"，形成词典。</li>\n  <li><b>量化</b>：把每图的SIFT硬分配到最近单词，统计词频直方图。</li>\n  <li><b>分类</b>：用SVM/KNN对直方图分类。</li>\n  <li>深度学习CNN本质是"自动学词典+端到端分类"。</li>\n</ul>',
  'region-growing': '<ul>\n  <li><b>选种子</b>：用户点一个点/自动按均匀性选。</li>\n  <li><b>扩散规则</b>：检查4邻域像素；与已生长区域均值差&lt;T则加入队列。</li>\n  <li><b>停止</b>：队列为空。</li>\n  <li>优点：简单、连通性好；缺点：阈值T敏感、没全局优化。</li>\n</ul>',
  'zhang-calibration': '<ul>\n  <li><b>拍棋盘</b>：≥3张不同姿态(不能共面)。</li>\n  <li><b>单应H</b>：每幅图由棋盘角点世界坐标→像素坐标求H。</li>\n  <li><b>解内参</b>：利用H₁H₁·H₂=0约束列方程，SVD分解出K(fx,fy,cx,cy,s)。</li>\n  <li><b>Levenberg-Marquardt</b>：最小化重投影误差精调。</li>\n  <li>张正友1999年提出，现在OpenCV calibrateCamera用的就是它。</li>\n</ul>',
  'epipolar': "<ul>\n  <li><b>对极几何</b>：OₗpₗOᵣ三点共面(对极面)，交右像面于极线l'。</li>\n  <li><b>基本矩阵F</b>：满足 pᵣᵀFpₗ=0，8点法即可估计。</li>\n  <li><b>极线约束</b>：pₗ已知→l'=Fpₗ，pᵣ必在l'上，搜索从2D降到1D。</li>\n</ul>",
  'slic': "<ul>\n  <li><b>SLIC</b>（Simple Linear Iterative Clustering）：超像素算法。</li>\n  <li>在 Labxy 五维空间做 K-Means，搜索范围限制在 2S×2S 邻域。</li>\n  <li>边界附着性好、速度快（线性复杂度），是做语义分割/显著性检测的常用预处理。</li>\n</ul>",
  'pnp': "<ul>\n  <li><b>PnP</b>（Perspective-n-Point）：已知 3D 点及其 2D 投影，求相机位姿 (R,t)。</li>\n  <li>经典解法：P3P（需 3 对点+1 对验证）、EPnP（O(n)）、迭代法 DLS。</li>\n  <li>是 AR / 机器人 / 位姿估计的核心：图像→2D-3D 匹配→PnP→相机→叠加虚拟物体。</li>\n</ul>",
  'lkflow': "<ul>\n  <li><b>光流</b>：像素在连续帧间的运动向量 (u,v)。</li>\n  <li>两个假设：亮度恒定（同一点在前后帧灰度一样）、小运动。</li>\n  <li>LK 在 3×3/5×5 窗口内联立方程求 (u,v)；Horn-Schunck 加全局光滑约束得到稠密光流。</li>\n</ul>",
}
const ctrls = {
  'sift': [{k:'octave',label:'金字塔层数',min:1,max:4,v:3,step:1,t:'range'},{k:'sigma',label:'DoG尺度σ',min:0.5,max:3.0,v:1.6,step:0.1,t:'range'}],
  'surf': [{k:'size',label:'箱式核大小',min:9,max:31,v:15,step:2,t:'range'}],
  'flann': [{k:'qx',label:'查询点x',min:20,max:620,v:300,step:1,t:'range'},{k:'qy',label:'查询点y',min:20,max:280,v:150,step:1,t:'range'}],
  'freak': [{k:'n',label:'采样点数',min:8,max:43,v:25,step:1,t:'range'}],
  'grabcut': [],
  'kcf': [{k:'pos',label:'目标框位置',min:50,max:500,v:200,step:1,t:'range'}],
  'meanshift': [],
  'mog2': [{k:'alpha',label:'学习率α',min:0.001,max:0.1,v:0.01,step:0.001,t:'range'}],
  'sgbm': [{k:'maxd',label:'最大视差',min:0,max:80,v:30,step:1,t:'range'},{k:'bs',label:'块大小',min:3,max:21,v:9,step:2,t:'range'}],
  'icp': [],
  'triangulation': [{k:'d',label:'视差d(像素)',min:5,max:180,v:40,step:1,t:'range'},{k:'B',label:'基线B(mm)',min:30,max:200,v:120,step:5,t:'range'}],
  'bundle': [],
  'dpm': [{k:'dx',label:'部件偏移',min:-40,max:40,v:0,step:1,t:'range'}],
  'camshift': [],
  'mosse': [{k:'psr',label:'PSR峰值旁瓣比',min:3,max:30,v:18,step:1,t:'range'}],
  'csrt': [{k:'chw',label:'颜色通道权重',min:0,max:1,v:0.7,step:0.05,t:'range'}],
  'vibe': [],
  'viola-jones': [],
  'brief': [{k:'n',label:'点对数n',min:32,max:256,v:128,step:32,t:'range'}],
  'bovw': [],
  'region-growing': [{k:'T',label:'阈值T',min:5,max:60,v:20,step:1,t:'range'}],
  'zhang-calibration': [{k:'n',label:'姿态数',min:2,max:15,v:5,step:1,t:'range'}],
  'epipolar': [{k:'x',label:'左图像素x',min:50,max:280,v:150,step:1,t:'range'}],
  'slic': [{k:'k',label:'超像素密度',min:2,max:6,v:4,step:1,t:'range'}],
  'pnp': [{k:'ang',label:'物体旋转角',min:0,max:360,v:30,step:5,t:'range'}],
  'lkflow': [{k:'t',label:'位移幅度',min:0,max:100,v:50,step:5,t:'range'}],
}
Object.keys(ctrls).forEach(k=>ctrls[k].forEach(c=>{c.v=ref(c.v)}))
const btns = reactive({
  'sift': [],
  'surf': [],
  'flann': [{k:()=>btn_flannStep(),label:'单步下树 ▶'},{k:()=>btn_flannReset(),label:'重置'}],
  'freak': [],
  'grabcut': [{k:()=>btn_grabcutStep(),label:'迭代一次 ▶'}],
  'kcf': [{k:()=>btn_kcfRun(),label:'▶跑跟踪'}],
  'meanshift': [{k:()=>btn_msStep(),label:'单步漂移 ▶'},{k:()=>btn_msReset(),label:'重置起点'}],
  'mog2': [{k:()=>btn_mog2Tick(),label:'过一帧 ▶'}],
  'sgbm': [],
  'icp': [{k:()=>btn_icpStep(),label:'单步对齐 ▶'},{k:()=>btn_icpReset(),label:'重置错位'}],
  'triangulation': [],
  'bundle': [{k:()=>btn_baStep(),label:'单步优化 ▶'},{k:()=>btn_baReset(),label:'打乱相机'}],
  'dpm': [],
  'camshift': [{k:()=>btn_csStep(),label:'单步收敛 ▶'},{k:()=>btn_csReset(),label:'重置'}],
  'mosse': [],
  'csrt': [],
  'vibe': [{k:()=>btn_vibeTick(),label:'过一帧 ▶'}],
  'viola-jones': [{k:()=>btn_vjNext(),label:'下一层级联 ▶'},{k:()=>btn_vjReset(),label:'重置'}],
  'brief': [],
  'bovw': [{k:()=>btn_bovwStep(),label:'下一步 ▶'}],
  'region-growing': [{k:()=>btn_rgStep(),label:'生长一步 ▶'},{k:()=>btn_rgReset(),label:'重置种子'}],
  'zhang-calibration': [],
  'epipolar': [],
  'slic': [],
  'pnp': [],
  'lkflow': [],
})

function dot(ctx,x,y,r,color){ctx.fillStyle=color;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill()}
function line(ctx,x1,y1,x2,y2,color,w){ctx.strokeStyle=color;ctx.lineWidth=w||1;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke()}
function fillText(ctx,text,x,y,color,size){ctx.fillStyle=color||'#333';ctx.font=(size||13)+'px sans-serif';ctx.fillText(text,x,y)}
function clear(ctx,w,h){ctx.clearRect(0,0,w||640,h||320);ctx.fillStyle='#fff';ctx.fillRect(0,0,w||640,h||320)}
function p(id,k){ const c=ctrls[id]; if(!c) return null; const f=c.find(x=>x.k===k); return f?f.v.value:null }

// 23个算法的draw函数 + 按钮回调
// 每个draw函数在 drawers[id] 中注册；按钮回调以 btn_xxx 命名

const drawers = {};
let _state = reactive({});
function state(id,k,init){ if(!_state[id]) _state[id]={}; if(_state[id][k]===undefined) _state[id][k]=init; return _state[id][k] }

// =============== SIFT ===============
drawers.sift = function(ctx){
  clear(ctx);
  const oct = p('sift','octave')|0;
  const sig = p('sift','sigma');
  fillText(ctx,'SIFT：高斯金字塔 + DoG + 极值点',20,25,'#333',14);
  // 画 oct 个 octave
  const ox=30,oy=50,cw=80,ch=45,gap=10,ogap=20;
  let n=0;
  for(let o=0;o<oct;o++){
    const h = ch/Math.pow(1.6,o);
    const w = cw/Math.pow(1.6,o);
    const nScale = 5;
    for(let s=0;s<nScale;s++){
      const x = ox + n*(w+gap), y = oy + (ch-h)*0.6 + o*ogap*0;
      const blur = 0.3 + s*0.4;
      ctx.fillStyle = `rgba(68,119,221,${0.2+blur*0.12})`;
      ctx.fillRect(x,y,w,h);
      ctx.strokeStyle='#88aadd';ctx.strokeRect(x,y,w,h);
      ctx.fillStyle='#666';ctx.font='10px sans-serif';
      ctx.fillText(`σ=${(sig*Math.pow(2,s/3)).toFixed(2)}`,x,y-3);
      n++;
    }
    n++; // 组间间隔
  }
  // DoG层
  fillText(ctx,'→ DoG差分（相邻σ相减）：找3×3×3极值点',20,200);
  const dx=30,dy=220;
  for(let i=0;i<4;i++){
    const x=dx+i*100;
    ctx.fillStyle='#eee';ctx.fillRect(x,dy,80,40);
    for(let k=0;k<5;k++){
      const px=x+10+Math.random()*60, py=dy+10+Math.random()*20;
      dot(ctx,px,py,2+Math.random()*2,'#e55');
    }
    ctx.strokeStyle='#aaa';ctx.strokeRect(x,dy,80,40);
  }
  dot(ctx,190,240,4,'#ff0');
  fillText(ctx,'★ 在26邻域(3×3×3)找极大极小→关键点',30,285,'#c00',12);
}

// =============== SURF ===============
drawers.surf = function(ctx){
  clear(ctx);
  const sz = p('surf','size')|0;
  fillText(ctx,'SURF：用箱式核近似高斯二阶导，积分图O(1)计算',20,25,'#333',14);
  // 画三种箱式核：Dxx Dyy Dxy
  const drawBox=(x,y,w,h,c)=>{ctx.fillStyle=c;ctx.fillRect(x,y,w,h)};
  // Dxx（横向条）
  const cx=140,cy=150;
  drawBox(cx-sz/2,cy-sz/4,sz,sz/6,'#4477dd');
  drawBox(cx-sz/2,cy+sz/12,sz,sz/6,'#4477dd');
  ctx.fillStyle='#dd6644';ctx.fillRect(cx-sz/2,cy-sz/12,sz,sz/6);
  ctx.strokeStyle='#333';ctx.strokeRect(cx-sz/2,cy-sz/2,sz,sz);
  fillText(ctx,'Dxx≈∂²G/∂x²',cx-40,cy-sz/2-10);
  // Dyy
  const cx2=330;
  drawBox(cx2-sz/4,cy-sz/2,sz/6,sz,'#4477dd');
  drawBox(cx2+sz/12,cy-sz/2,sz/6,sz,'#4477dd');
  ctx.fillStyle='#dd6644';ctx.fillRect(cx2-sz/12,cy-sz/2,sz/6,sz);
  ctx.strokeStyle='#333';ctx.strokeRect(cx2-sz/2,cy-sz/2,sz,sz);
  fillText(ctx,'Dyy≈∂²G/∂y²',cx2-40,cy-sz/2-10);
  // Dxy
  const cx3=500;
  ctx.fillStyle='#4477dd';
  ctx.fillRect(cx3-sz/2,cy-sz/2,sz/4,sz/4);
  ctx.fillRect(cx3+sz/4,cy+sz/4,sz/4,sz/4);
  ctx.fillStyle='#dd6644';
  ctx.fillRect(cx3+sz/4,cy-sz/2,sz/4,sz/4);
  ctx.fillRect(cx3-sz/2,cy+sz/4,sz/4,sz/4);
  ctx.strokeStyle='#333';ctx.strokeRect(cx3-sz/2,cy-sz/2,sz,sz);
  fillText(ctx,'Dxy',cx3-15,cy-sz/2-10);
  fillText(ctx,'det(H)=Dxx·Dyy − (0.9·Dxy)² → 找极大值点',180,270,'#c00',13);
  fillText(ctx,'蓝=正权重  橙=负权重',180,295,'#666',12);
}

// =============== FLANN ===============
function _flannInit(){
  if(_state.flann && _state.flann.pts) return;
  const pts=[];
  for(let i=0;i<60;i++){ pts.push({x:40+Math.random()*560, y:40+Math.random()*240}) }
  // 简单KD树：按x中值切→子节点按y中值切→x...
  function build(points, depth){
    if(points.length===0) return null;
    if(points.length<=3){return {pts:points,depth}}
    const axis=depth%2;
    points.sort((a,b)=> axis===0?a.x-b.x:a.y-b.y);
    const mid=points.length>>1;
    return {
      split:axis, val:axis===0?points[mid].x:points[mid].y,
      left:build(points.slice(0,mid),depth+1),
      right:build(points.slice(mid+1),depth+1),
      pts:[points[mid]], depth
    };
  }
  const root=build(pts.slice(),0);
  _state.flann={pts,root,path:[],stepN:0};
}
function flann_query_path(tree,qx,qy,path){
  if(!tree) return;
  path.push(tree);
  if(tree.pts){return}
  const v = tree.split===0?qx:qy;
  if(v < tree.val) flann_query_path(tree.left,qx,qy,path);
  else flann_query_path(tree.right,qx,qy,path);
}
drawers.flann = function(ctx){
  _flannInit();
  clear(ctx);
  fillText(ctx,'FLANN KD树查询：黄点从根节点沿最近方向下到叶子',20,25,'#333',14);
  const qx=p('flann','qx'),qy=p('flann','qy');
  const st=_state.flann;
  // 画点
  st.pts.forEach(p=>dot(ctx,p.x,p.y,2,'#8ab'));
  // 画分割线（仅绘制当前走过路径涉及的节点及其祖先）
  function drawSplits(node,rect){
    if(!node||node.left===undefined) return;
    const visited = st.path.includes(node);
    ctx.strokeStyle=visited?'#e55':'rgba(180,200,220,0.5)';
    ctx.lineWidth=visited?2:1;
    if(node.split===0){
      ctx.beginPath();ctx.moveTo(node.val,rect.y1);ctx.lineTo(node.val,rect.y2);ctx.stroke();
      fillText(ctx,node.val.toFixed(0),node.val+2,rect.y1+12,visited?'#e55':'#aac',10);
    }else{
      ctx.beginPath();ctx.moveTo(rect.x1,node.val);ctx.lineTo(rect.x2,node.val);ctx.stroke();
      fillText(ctx,node.val.toFixed(0),rect.x1+2,node.val-2,visited?'#e55':'#aac',10);
    }
    const v = node.split===0?qx:qy;
    if(v<node.val){
      const nr=node.split===0?{x1:rect.x1,y1:rect.y1,x2:node.val,y2:rect.y2}:{x1:rect.x1,y1:rect.y1,x2:rect.x2,y2:node.val};
      drawSplits(node.left,nr);
    }else{
      const nr=node.split===0?{x1:node.val,y1:rect.y1,x2:rect.x2,y2:rect.y2}:{x1:rect.x1,y1:node.val,x2:rect.x2,y2:rect.y2};
      drawSplits(node.right,nr);
    }
  }
  drawSplits(st.root,{x1:20,y1:40,x2:620,y2:290});
  // 高亮点
  dot(ctx,qx,qy,6,'#ff0');
  ctx.strokeStyle='#ff0';ctx.lineWidth=2;ctx.beginPath();ctx.arc(qx,qy,10,0,Math.PI*2);ctx.stroke();
  // 走了多少步
  fillText(ctx,`已下探 ${st.stepN} 层，路径节点数 ${st.path.length}`,20,310);
}
function btn_flannStep(){
  _flannInit();
  const qx=p('flann','qx'),qy=p('flann','qy');
  _state.flann.stepN++;
  _state.flann.path=[];
  function collect(tree, depth){
    if(!tree) return null;
    if(depth>_state.flann.stepN){
      _state.flann.path.push(tree);
      return tree;
    }
    _state.flann.path.push(tree);
    if(tree.left===undefined) return tree;
    const v=tree.split===0?qx:qy;
    if(v<tree.val) return collect(tree.left,depth+1) || tree;
    else return collect(tree.right,depth+1) || tree;
  }
  collect(_state.flann.root,0);
  draw('flann');
}
function btn_flannReset(){_state.flann&&(_state.flann.stepN=0);_state.flann&&(_state.flann.path=[]);draw('flann')}

// =============== FREAK ===============
drawers.freak = function(ctx){
  clear(ctx);
  const n = p('freak','n')|0;
  fillText(ctx,`FREAK：视网膜式采样（${n}点，中心密外围疏）`,20,25,'#333',14);
  const cx=320,cy=160;
  // 同心圆
  for(let r=20;r<=110;r+=20){
    ctx.strokeStyle='rgba(68,119,221,0.3)';ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();
  }
  // 采样点：极坐标，r越小点越密
  let placed=0;
  for(let ring=0;ring<6 && placed<n;ring++){
    const r=20+ring*18;
    const count=Math.min(Math.ceil((ring+1)*4), n-placed);
    for(let i=0;i<count;i++){
      const a=(i/count)*Math.PI*2;
      dot(ctx,cx+r*Math.cos(a),cy+r*Math.sin(a),3-ring*0.3,'#e55');
      placed++;
    }
  }
  dot(ctx,cx,cy,3,'#44d');
  // 随机点对连线
  ctx.strokeStyle='rgba(229,85,85,0.3)';ctx.lineWidth=1;
  const allPts=[];
  placed=0;
  for(let ring=0;ring<6 && placed<n;ring++){
    const r=20+ring*18;
    const count=Math.min(Math.ceil((ring+1)*4), n-placed);
    for(let i=0;i<count;i++){
      const a=(i/count)*Math.PI*2;
      allPts.push({x:cx+r*Math.cos(a),y:cy+r*Math.sin(a)});
      placed++;
    }
  }
  for(let i=0;i<30;i++){
    const a=allPts[(Math.random()*allPts.length)|0],b=allPts[(Math.random()*allPts.length)|0];
    ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
  }
  fillText(ctx,'随机点对比较亮度→二进制串；外围感受野大、中心细',20,295,'#666',12);
}

// =============== GrabCut ===============
function _gcInit(){
  if(_state.gc && _state.gc.pix) return;
  const W=60,H=30,pix=[];
  for(let y=0;y<H;y++){
    const row=[];
    for(let x=0;x<W;x++){
      // 背景随机+前景一个圆
      const inFg=(x-42)*(x-42)/100+(y-15)*(y-15)/36 < 1;
      const v=inFg? 180+Math.random()*30: 80+Math.random()*40;
      row.push({v:v|0,fg:0});
    }
    pix.push(row);
  }
  _state.gc={pix,iters:0,W,H};
}
drawers.grabcut = function(ctx){
  _gcInit();
  clear(ctx);
  fillText(ctx,`GrabCut：GMM+图割  迭代第${_state.gc.iters}次`,20,25,'#333',14);
  const st=_state.gc, ps=8;
  // 框
  ctx.strokeStyle='#4477dd';ctx.lineWidth=2;ctx.strokeRect(28*ps+20,6*ps+45,28*ps,18*ps);
  fillText(ctx,'初始框（用户画的）',28*ps+20,6*ps+40,'#4477dd',11);
  for(let y=0;y<st.H;y++){
    for(let x=0;x<st.W;x++){
      const p=st.pix[y][x];
      ctx.fillStyle=p.fg===1?'#ffd080':'#6688aa';
      ctx.fillRect(20+x*ps,45+y*ps,ps-1,ps-1);
    }
  }
  fillText(ctx,'橙色=前景  蓝=背景  点"迭代一次"看GMM收敛',20,300,'#666',12);
}
function btn_grabcutStep(){
  _gcInit();
  _state.gc.iters++;
  // 简单模拟：按灰度阈值判断，每轮阈值更准
  const t=130+_state.gc.iters*5;
  for(const row of _state.gc.pix){
    for(const p of row){
      // 仅在框内判断
      p.fg = p.v>t ? 1:0;
    }
  }
  draw('grabcut');
}

// =============== KCF ===============
function _kcfInit(){
  if(!_state.kcf){
    const pts=[];
    for(let i=0;i<300;i++){
      pts.push({x:80+Math.random()*480,y:60+Math.random()*200});
    }
    _state.kcf={pts,running:false};
  }
}
drawers.kcf = function(ctx){
  _kcfInit();
  clear(ctx);
  fillText(ctx,'KCF相关滤波：响应图峰值=新位置（红尖峰跟踪绿点运动）',20,25,'#333',14);
  const pos=p('kcf','pos');
  // 场景
  ctx.fillStyle='#e8e8d8';ctx.fillRect(20,45,600,200);
  _state.kcf.pts.forEach((p,i)=>{dot(ctx,p.x,p.y,1,'#aaa')});
  // 目标
  dot(ctx,pos,140,8,'#4c4');
  // 响应图
  const rx=20,ry=250,rw=600,rh=50;
  ctx.fillStyle='#222';ctx.fillRect(rx,ry,rw,rh);
  for(let x=0;x<rw;x+=3){
    const dx=rx+x-pos;
    const d=Math.sqrt(dx*dx);
    const v=Math.exp(-d*d/600)*0.9+Math.random()*0.04;
    const g=Math.min(255,v*255|0);
    ctx.fillStyle=`rgb(${g},${(g*0.4)|0},0)`;
    ctx.fillRect(rx+x,ry,3,rh);
  }
  dot(ctx,pos,ry+rh/2,6,'#0f0');
  fillText(ctx,'响应峰',pos+10,ry+15,'#0f0',11);
}
function btn_kcfRun(){
  _kcfInit();
  let pos=p('kcf','pos');
  const step=()=>{
    pos+=8+Math.random()*4;
    if(pos>580)pos=60;
    _state.kcf.pos=pos;
    const c=ctrls['kcf'].find(x=>x.k==='pos');
    if(c) c.v.value=pos;
    draw('kcf');
    if(_state.kcf.running) requestAnimationFrame(step);
  };
  _state.kcf.running=!_state.kcf.running;
  if(_state.kcf.running) step();
}

// =============== MeanShift ===============
function _msInit(){
  if(_state.ms && _state.ms.pts) return;
  const pts=[];
  // 三个高斯簇
  for(let i=0;i<80;i++){pts.push({x:180+(Math.random()-0.5)*60,y:100+(Math.random()-0.5)*60})}
  for(let i=0;i<60;i++){pts.push({x:450+(Math.random()-0.5)*80,y:200+(Math.random()-0.5)*60})}
  for(let i=0;i<70;i++){pts.push({x:300+(Math.random()-0.5)*60,y:230+(Math.random()-0.5)*60})}
  _state.ms={pts,path:[{x:130,y:85}],h:60};
}
drawers.meanshift = function(ctx){
  _msInit();
  clear(ctx);
  fillText(ctx,'MeanShift：蓝点沿密度梯度爬升到红色中心',20,25,'#333',14);
  const st=_state.ms;
  st.pts.forEach(p=>dot(ctx,p.x,p.y,2,'#9bd'));
  // 带宽圈
  const cur=st.path[st.path.length-1];
  ctx.strokeStyle='rgba(229,85,85,0.4)';ctx.setLineDash([4,3]);
  ctx.beginPath();ctx.arc(cur.x,cur.y,st.h,0,Math.PI*2);ctx.stroke();
  ctx.setLineDash([]);
  // 路径
  ctx.strokeStyle='#e55';ctx.lineWidth=2;
  ctx.beginPath();ctx.moveTo(st.path[0].x,st.path[0].y);
  for(let i=1;i<st.path.length;i++) ctx.lineTo(st.path[i].x,st.path[i].y);
  ctx.stroke();
  dot(ctx,st.path[0].x,st.path[0].y,5,'#e8e800');
  dot(ctx,cur.x,cur.y,6,'#e55');
  fillText(ctx,'起点',st.path[0].x-10,st.path[0].y-10,'#aa0',11);
  fillText(ctx,'收敛中心',cur.x+8,cur.y-5,'#e55',11);
}
function btn_msStep(){
  _msInit();
  const st=_state.ms, cur=st.path[st.path.length-1];
  let sx=0,sy=0,n=0;
  st.pts.forEach(p=>{
    const dx=p.x-cur.x, dy=p.y-cur.y;
    if(dx*dx+dy*dy<st.h*st.h){sx+=p.x;sy+=p.y;n++}
  });
  if(n>0){
    st.path.push({x:sx/n,y:sy/n});
  }
  draw('meanshift');
}
function btn_msReset(){_state.ms&&(_state.ms.path=[{x:130,y:85}]);draw('meanshift')}

// =============== MOG2 ===============
function _mogInit(){
  if(_state.mog && _state.mog.gauss) return;
  const gauss=[{mean:120,var:60,w:0.7},{mean:200,var:40,w:0.2},{mean:60,var:30,w:0.1}];
  const hist=[];
  for(let i=0;i<100;i++) hist.push(120+(Math.random()-0.5)*40);
  _state.mog={gauss,hist,fg:[]};
}
drawers.mog2 = function(ctx){
  _mogInit();
  const alpha=p('mog2','alpha');
  clear(ctx);
  fillText(ctx,`MOG2：单像素维护3个高斯（树叶晃动多峰背景） α=${alpha.toFixed(3)}`,20,25,'#333',14);
  const st=_state.mog;
  // 画直方图
  const px=40,py=60,W=560,H=180;
  ctx.fillStyle='#f0f0e0';ctx.fillRect(px,py,W,H);
  ctx.strokeStyle='#aaa';ctx.strokeRect(px,py,W,H);
  // 高斯曲线
  const cs=['#4477dd','#dd7744','#44aa77'];
  st.gauss.forEach((g,i)=>{
    ctx.strokeStyle=cs[i];ctx.lineWidth=2;ctx.beginPath();
    for(let x=0;x<255;x++){
      const y = Math.exp(-(x-g.mean)*(x-g.mean)/(2*g.var))*g.w*H;
      if(x===0)ctx.moveTo(px+x*W/255,py+H-y);
      else ctx.lineTo(px+x*W/255,py+H-y);
    }
    ctx.stroke();
    fillText(ctx,`μ=${g.mean|0} σ=${Math.sqrt(g.var)|0} w=${g.w.toFixed(2)}`,px+10+i*180,py+H+18,cs[i],11);
  });
  // 最近100个值
  st.hist.forEach((v,i)=>{
    dot(ctx,px+v*W/255, py+H-10-i*0.5,1.5,'#888');
  });
  // 当前像素
  const last=st.hist[st.hist.length-1];
  dot(ctx,px+last*W/255, py+H-8,5,'#e55');
  const isFg = st.gauss.every(g=>Math.abs(last-g.mean)>2.5*Math.sqrt(g.var));
  fillText(ctx,isFg?'✗ 偏离所有高斯2.5σ→判为前景（运动目标）':'✓ 匹配背景高斯',20,300,isFg?'#c00':'#080',13);
}
function btn_mog2Tick(){
  _mogInit();
  const st=_state.mog;
  // 50%从背景高斯采，50%新前景值
  let val;
  if(Math.random()<0.75){
    const g=st.gauss[(Math.random()*3)|0];
    val=g.mean+(Math.random()-0.5)*Math.sqrt(g.var)*1.5;
  }else{
    val=20+(Math.random()*20)|0;
  }
  val=Math.max(0,Math.min(255,val|0));
  st.hist.push(val);
  if(st.hist.length>120)st.hist.shift();
  // 更新
  const alpha=p('mog2','alpha');
  st.gauss.forEach(g=>{
    if(Math.abs(val-g.mean)<2.5*Math.sqrt(g.var)){
      g.w=(1-alpha)*g.w+alpha;
      const rho=alpha/Math.exp(-((val-g.mean)**2)/(2*g.var));
      g.mean=(1-rho)*g.mean+rho*val;
      g.var=(1-rho)*g.var+rho*(val-g.mean)*(val-g.mean);
    }else{
      g.w=(1-alpha)*g.w;
    }
  });
  draw('mog2');
}

// =============== SGBM ===============
drawers.sgbm = function(ctx){
  clear(ctx);
  const D=p('sgbm','maxd')|0, B=p('sgbm','bs')|0;
  fillText(ctx,`SGBM立体匹配：maxD=${D} block=${B} → 视差图 → 深度Z=fB/d`,20,25,'#333',14);
  // 左右图像简化：画一个近方块+远方块
  ctx.fillStyle='#88aadd';ctx.fillRect(30,60,270,180);ctx.strokeRect(30,60,270,180);
  ctx.fillStyle='#aaccaa';ctx.fillRect(330,60,270,180);ctx.strokeRect(330,60,270,180);
  fillText(ctx,'左图',150,52,'#333',12);fillText(ctx,'右图',455,52,'#333',12);
  // 前景方块（视差大）
  ctx.fillStyle='#dd6644';ctx.fillRect(120,130,70,70);
  ctx.fillStyle='#dd6644';ctx.fillRect(120+D*0.8,130,70,70);
  // 远景方块（视差小）
  ctx.fillStyle='#44aa77';ctx.fillRect(220,80,50,50);
  ctx.fillStyle='#44aa77';ctx.fillRect(220+D*0.2,80,50,50);
  // 视差图
  const dx=30,dy=250,dw=570,dh=35;
  for(let x=0;x<dw;x++){
    const d = x<dw*0.3?D*0.3 : (x<dw*0.55?D*0.9 : D*0.2);
    const hue = (1-d/D)*240; // 蓝(远)→红(近)
    ctx.fillStyle=`hsl(${hue|0},70%,55%)`;
    ctx.fillRect(dx+x,dy,1,dh);
  }
  fillText(ctx,'视差图：红=近（大视差） 蓝=远（小视差）',30,300,'#333',12);
}

// =============== ICP ===============
function _icpInit(reset){
  if(!reset && _state.icp && _state.icp.src) return;
  const tgt=[],src=[];
  for(let i=0;i<50;i++){
    const a=Math.random()*Math.PI*2;
    const r=60+Math.random()*30;
    tgt.push({x:320+Math.cos(a)*r, y:160+Math.sin(a)*r*0.7});
  }
  // 错位
  const dx0=80,dy0=-50,rot=0.5;
  tgt.forEach(p=>{
    src.push({
      x: p.x*Math.cos(rot)-p.y*Math.sin(rot)+dx0 + 200,
      y: p.x*Math.sin(rot)+p.y*Math.cos(rot)+dy0
    });
  });
  _state.icp={src,tgt,iters:0};
}
drawers.icp = function(ctx){
  _icpInit();
  clear(ctx);
  fillText(ctx,`ICP迭代对齐：第${_state.icp.iters}步（红点=目标，蓝点=源，最近点连线）`,20,25,'#333',14);
  const st=_state.icp;
  st.tgt.forEach(p=>dot(ctx,p.x,p.y,3,'#e55'));
  st.src.forEach(p=>dot(ctx,p.x,p.y,3,'#4477dd'));
  // 画前几个最近点连线
  for(let i=0;i<st.src.length;i+=5){
    const s=st.src[i];
    let best=null,bd=1e9;
    st.tgt.forEach(t=>{const d=(t.x-s.x)**2+(t.y-s.y)**2;if(d<bd){bd=d;best=t}});
    if(best){ctx.strokeStyle='rgba(100,100,100,0.2)';ctx.beginPath();ctx.moveTo(s.x,s.y);ctx.lineTo(best.x,best.y);ctx.stroke()}
  }
  fillText(ctx,'红点云=目标模型    蓝点云=新扫描    SVD求R,t变换蓝点',20,300,'#666',12);
}
function btn_icpStep(){
  _icpInit();
  const st=_state.icp;
  // 找最近点
  const pairs=st.src.map(s=>{
    let best=null,bd=1e9;
    st.tgt.forEach(t=>{const d=(t.x-s.x)**2+(t.y-s.y)**2;if(d<bd){bd=d;best=t}});
    return {s,t:best};
  });
  // 求质心
  let sc={x:0,y:0},tc={x:0,y:0};
  pairs.forEach(p=>{sc.x+=p.s.x;sc.y+=p.s.y;tc.x+=p.t.x;tc.y+=p.t.y});
  sc.x/=pairs.length;sc.y/=pairs.length;tc.x/=pairs.length;tc.y/=pairs.length;
  // H矩阵(简化成2D:求旋转角)
  let num=0,den=0;
  pairs.forEach(p=>{
    num+=(p.s.x-sc.x)*(p.t.y-tc.y)-(p.s.y-sc.y)*(p.t.x-tc.x);
    den+=(p.s.x-sc.x)*(p.t.x-tc.x)+(p.s.y-sc.y)*(p.t.y-tc.y);
  });
  const theta=Math.atan2(num,den);
  const tx=tc.x-(sc.x*Math.cos(theta)-sc.y*Math.sin(theta));
  const ty=tc.y-(sc.x*Math.sin(theta)+sc.y*Math.cos(theta));
  // 应用0.3步长
  const step=0.4;
  const a=theta*step;
  st.src.forEach(p=>{
    const nx=p.x*Math.cos(a)-p.y*Math.sin(a)+tx*step;
    const ny=p.x*Math.sin(a)+p.y*Math.cos(a)+ty*step;
    p.x=nx;p.y=ny;
  });
  st.iters++;
  draw('icp');
}
function btn_icpReset(){_icpInit(true);draw('icp')}

// =============== 三角化 ===============
drawers.triangulation = function(ctx){
  clear(ctx);
  const d=p('triangulation','d')|0, B=p('triangulation','B')|0;
  const f=120;
  const Z=f*B/d;
  fillText(ctx,`三角化：基线B=${B}mm, 焦距f=${f}px, 视差d=${d}px → 深度Z=fB/d=${Z|0}mm`,20,25,'#333',14);
  // 画两个相机+成像面+3D点
  const Ol={x:150,y:200},Or={x:150+B,y:200};
  // 成像面（在f前方——反向投影更直观）
  const imgY=280;
  ctx.fillStyle='#ddd';ctx.fillRect(60,imgY,B+180,40);ctx.strokeRect(60,imgY,B+180,40);
  fillText(ctx,'左成像面',80,imgY+25,'#333',11);
  fillText(ctx,'右成像面',B+130,imgY+25,'#333',11);
  dot(ctx,Ol.x,Ol.y,6,'#4477dd');dot(ctx,Or.x,Or.y,6,'#e55');
  fillText(ctx,'Oₗ',Ol.x-8,Ol.y-10,'#4477dd');
  fillText(ctx,'Oᵣ',Or.x+3,Or.y-10,'#e55');
  line(ctx,Ol.x,Ol.y,Or.x,Or.y,'#888',1);
  fillText(ctx,'基线B',(Ol.x+Or.x)/2-12,Ol.y-5,'#888',11);
  // 3D点
  const Px=(Ol.x+Or.x)/2, Py=Ol.y - Math.min(Z*0.4,140);
  dot(ctx,Px,Py,6,'#ff0');
  fillText(ctx,'P(3D)',Px+5,Py-5,'#c80');
  // 投影线
  line(ctx,Ol.x,Ol.y,Px,Py,'#4477dd',1);
  line(ctx,Or.x,Or.y,Px,Py,'#e55',1);
  // 投影到成像面的点
  const pl={x:Ol.x-f*(Px-Ol.x)/(Ol.y-Py), y:imgY+20};
  const pr={x:Or.x-f*(Px-Or.x)/(Or.y-Py), y:imgY+20};
  // 简化：把投影点直接按视差偏移画在成像面上
  const plx=120, prx=120+d*1.2;
  dot(ctx,plx,imgY+20,5,'#4477dd');dot(ctx,prx+80,imgY+20,5,'#e55');
  line(ctx,plx,imgY+20,prx+80,imgY+20,'#c00',2);
  fillText(ctx,`视差d=${d}`,(plx+prx+80)/2-20,imgY+15,'#c00',11);
  fillText(ctx,'视差越大→点越近；视差=0→无穷远',20,310,'#666',12);
}

// =============== Bundle Adjustment ===============
function _baInit(reset){
  if(!reset && _state.ba && _state.ba.cams) return;
  const pts=[];
  for(let i=0;i<30;i++){
    pts.push({x:320+(Math.random()-0.5)*300,y:120+(Math.random()-0.5)*80});
  }
  const cams=[{x:80,y:260,a:-0.4},{x:320,y:280,a:0},{x:560,y:260,a:0.4}];
  const obs=cams.map(c=>pts.map(p=>({u:(p.x-c.x)*Math.cos(c.a)+(p.y-c.y)*Math.sin(c.a),v:-(p.x-c.x)*Math.sin(c.a)+(p.y-c.y)*Math.cos(c.a)})));
  // 加噪
  const noisedCams=cams.map(c=>({x:c.x+(Math.random()-0.5)*40,y:c.y+(Math.random()-0.5)*20,a:c.a+(Math.random()-0.5)*0.3}));
  _state.ba={pts,cams,obs,noisedCams,iters:0};
}
drawers.bundle = function(ctx){
  _baInit();
  clear(ctx);
  fillText(ctx,`Bundle Adjustment（第${_state.ba.iters}步）：蓝=观测  灰=当前投影  红点=3D点`,20,25,'#333',14);
  const st=_state.ba;
  // 3D点
  st.pts.forEach(p=>dot(ctx,p.x,p.y,2,'#e55'));
  // 相机三角
  st.noisedCams.forEach((c,i)=>{
    const gt=st.cams[i];
    ctx.fillStyle='#4477dd';
    ctx.beginPath();ctx.moveTo(c.x,c.y);ctx.lineTo(c.x-18*Math.cos(c.a-Math.PI/6),c.y-18*Math.sin(c.a-Math.PI/6));ctx.lineTo(c.x-18*Math.cos(c.a+Math.PI/6),c.y-18*Math.sin(c.a+Math.PI/6));ctx.closePath();ctx.fill();
    // 投影线（灰）
    ctx.strokeStyle='rgba(100,100,100,0.2)';
    st.pts.forEach(p=>{ctx.beginPath();ctx.moveTo(c.x,c.y);ctx.lineTo(p.x,p.y);ctx.stroke()});
    // 观测（蓝）
    ctx.strokeStyle='rgba(68,119,221,0.5)';
    st.pts.forEach(p=>{
      const u=(p.x-gt.x)*Math.cos(gt.a)+(p.y-gt.y)*Math.sin(gt.a);
      const v=-(p.x-gt.x)*Math.sin(gt.a)+(p.y-gt.y)*Math.cos(gt.a);
      // 反投影回像面（简单近似）
    });
  });
  fillText(ctx,'最小化 Σ‖π(K,Tᵢ,Xⱼ)−xᵢⱼ‖² ：同时优化所有T和X',20,300,'#666',12);
}
function btn_baStep(){
  _baInit();
  const st=_state.ba;
  // 模拟一步LM：把相机向GT挪30%
  st.noisedCams.forEach((c,i)=>{
    const gt=st.cams[i];
    c.x+=(gt.x-c.x)*0.3;
    c.y+=(gt.y-c.y)*0.3;
    c.a+=(gt.a-c.a)*0.3;
  });
  st.iters++;
  draw('bundle');
}
function btn_baReset(){_baInit(true);draw('bundle')}

// =============== DPM ===============
drawers.dpm = function(ctx){
  clear(ctx);
  const dx=p('dpm','dx')|0;
  fillText(ctx,`DPM：根滤波器(整体)+部件滤波器(头/腿)+变形代价(偏移dx=${dx})`,20,25,'#333',14);
  // 根滤波器(人整体)
  ctx.fillStyle='#4477dd';ctx.fillRect(250,80,60,140);ctx.strokeStyle='#225';ctx.strokeRect(250,80,60,140);
  fillText(ctx,'根HOG',255,75,'#4477dd',11);
  // 部件
  const parts=[{name:'头',x:255,y:90,w:50,h:40,c:'#dd7744',ox:0,oy:-50},{name:'左臂',x:220,y:100,w:30,h:50,c:'#44aa77',ox:-35,oy:-30},{name:'右臂',x:310,y:100,w:30,h:50,c:'#44aa77',ox:35,oy:-30},{name:'左腿',x:255,y:190,w:25,h:40,c:'#ddaa44',ox:-15,oy:60},{name:'右腿',x:280,y:190,w:25,h:40,c:'#ddaa44',ox:15,oy:60}];
  parts.forEach(p=>{
    ctx.fillStyle=p.c;
    ctx.fillRect(p.x+dx,p.y,p.w,p.h);
    ctx.strokeStyle='#333';ctx.strokeRect(p.x+dx,p.y,p.w,p.h);
    fillText(ctx,p.name,p.x+dx+4,p.y-3,'#333',10);
    // 变形连线
    ctx.strokeStyle='rgba(200,50,50,0.4)';ctx.setLineDash([3,3]);
    ctx.beginPath();ctx.moveTo(p.x+p.w/2+dx,p.y);ctx.lineTo(280,150);ctx.stroke();
    ctx.setLineDash([]);
  });
  // 变形代价
  const cost=Math.abs(dx)*0.5;
  fillText(ctx,`总得分 = 根响应 + Σ部件响应 − ${cost.toFixed(1)}(变形代价)`,180,270,'#c00',13);
  fillText(ctx,'部件偏离理想位置越远，惩罚越大 → 能处理姿态变化',180,295,'#666',12);
}

// =============== CamShift ===============
function _csInit(){
  if(_state.cs && _state.cs.pts) return;
  const pts=[];
  for(let i=0;i<150;i++){pts.push({x:250+(Math.random()-0.5)*200,y:150+(Math.random()-0.5)*120})}
  for(let i=0;i<80;i++){const a=Math.random()*Math.PI*2;pts.push({x:350+Math.cos(a)*40,y:170+Math.sin(a)*30*0.7})}
  _state.cs={pts,win:{x:130,y:90,w:70,h:70},step:0};
}
drawers.camshift = function(ctx){
  _csInit();
  clear(ctx);
  fillText(ctx,'CamShift：窗口漂移→并按二阶矩自适应大小/方向',20,25,'#333',14);
  const st=_state.cs;
  st.pts.forEach(p=>dot(ctx,p.x,p.y,2,'#8ab'));
  ctx.strokeStyle='#e55';ctx.lineWidth=2;ctx.strokeRect(st.win.x,st.win.y,st.win.w,st.win.h);
  fillText(ctx,`自适应窗口 ${st.win.w.toFixed(0)}×${st.win.h.toFixed(0)}`,st.win.x+3,st.win.y-5,'#e55',11);
}
function btn_csStep(){
  _csInit();
  const st=_state.cs;
  st.step++;if(st.step>20)return;
  let sx=0,sy=0,mxx=0,myy=0,mxy=0,n=0;
  st.pts.forEach(p=>{
    if(p.x>st.win.x&&p.x<st.win.x+st.win.w&&p.y>st.win.y&&p.y<st.win.y+st.win.h){
      sx+=p.x;sy+=p.y;n++;
      mxx+=p.x*p.x;myy+=p.y*p.y;mxy+=p.x*p.y;
    }
  });
  if(n>0){
    const cx=sx/n,cy=sy/n;
    const w=Math.min(150,st.win.w+3),h=Math.min(100,st.win.h+2);
    st.win={x:cx-w/2,y:cy-h/2,w,h};
  }
  draw('camshift');
}
function btn_csReset(){_csInit();_state.cs.win={x:130,y:90,w:70,h:70};_state.cs.step=0;draw('camshift')}

// =============== MOSSE ===============
drawers.mosse = function(ctx){
  clear(ctx);
  const psr=p('mosse','psr');
  fillText(ctx,`MOSSE响应图：PSR=${psr.toFixed(0)} — 越高跟踪越稳`,20,25,'#333',14);
  const W=580,H=200,px=30,py=60;
  ctx.fillStyle='#222';ctx.fillRect(px,py,W,H);
  const pkX=px+W/2+Math.sin(Date.now()/1000)*60,pkY=py+H/2;
  for(let x=0;x<W;x+=3){
    for(let y=0;y<H;y+=3){
      const dx=(px+x)-pkX,dy=(py+y)-pkY;
      const d=Math.sqrt(dx*dx+dy*dy);
      const v=Math.exp(-d*d/800)*(0.4+psr/35)+Math.random()*0.05;
      const g=Math.min(255,v*255|0);
      ctx.fillStyle=`rgb(${g},${(g*0.7)|0},${(g*0.3)|0})`;
      ctx.fillRect(px+x,py+y,3,3);
    }
  }
  dot(ctx,pkX,pkY,7,'#0f0');
  ctx.strokeStyle='#0f0';ctx.lineWidth=1;ctx.beginPath();ctx.arc(pkX,pkY,16,0,Math.PI*2);ctx.stroke();
  const st=psr>10?'✓ PSR>10 跟踪稳定':(psr>7?'⚠ PSR 7-10 置信度低':'✗ PSR<7 目标丢失');
  fillText(ctx,st,30,290,psr>10?'#080':psr>7?'#c80':'#c00',13);
}

// =============== CSRT ===============
drawers.csrt = function(ctx){
  clear(ctx);
  const chw=p('csrt','chw');
  fillText(ctx,'CSRT多通道可靠性：各通道根据区分度动态加权',20,25,'#333',14);
  const channels=[
    {name:'HOG梯度',w:1.0,x:40,c:'#4477dd'},
    {name:'颜色名CN',w:chw,x:190,c:'#dd7744'},
    {name:'灰度',w:0.6,x:340,c:'#888'},
    {name:'HoN',w:0.4,x:490,c:'#44aa77'},
  ];
  channels.forEach(ch=>{
    ctx.fillStyle='#f0f0e8';ctx.fillRect(ch.x,60,120,180);
    ctx.strokeStyle=ch.c;ctx.lineWidth=2;ctx.strokeRect(ch.x+10,240-ch.w*150,100,ch.w*150);
    ctx.fillStyle=ch.c+'44';ctx.fillRect(ch.x+10,240-ch.w*150,100,ch.w*150);
    fillText(ctx,ch.name,ch.x+10,55,'#333',12);
    ctx.fillStyle=ch.c;ctx.font='bold 13px sans-serif';ctx.textAlign='center';
    fillText(ctx,'权重 '+ch.w.toFixed(2),ch.x+60,258,ch.c,13);
    ctx.textAlign='left';ctx.font='13px sans-serif';
  });
  fillText(ctx,'空间掩码只让目标区域参与训练，通道失效时自动降权',20,290,'#666',12);
}

// =============== ViBe ===============
function _vibeInit(){
  if(_state.vibe && _state.vibe.samples) return;
  const samples=[];
  for(let i=0;i<20;i++) samples.push(100+Math.random()*30);
  const hist=[];
  _state.vibe={samples,hist};
}
drawers.vibe = function(ctx){
  _vibeInit();
  clear(ctx);
  fillText(ctx,'ViBe：单像素20个历史样本，接近≥2个判为背景',20,25,'#333',14);
  const st=_state.vibe;
  // 当前像素值流
  ctx.fillStyle='#f0f0e8';ctx.fillRect(30,50,300,200);
  ctx.strokeStyle='#999';ctx.beginPath();ctx.moveTo(30,240);ctx.lineTo(330,240);ctx.stroke();
  st.hist.forEach((p,i)=>{
    ctx.fillStyle=p.moving?'#e55':'#48b';
    ctx.fillRect(40+i*7,250-p.v*0.7,5,p.v*0.7);
  });
  // 样本集
  ctx.fillStyle='#fff';ctx.fillRect(350,50,260,200);
  fillText(ctx,'20个背景样本：',360,70);
  st.samples.forEach((v,i)=>{
    const x=360+(i%5)*50,y=90+Math.floor(i/5)*50;
    ctx.fillStyle=`rgb(${v|0},${v|0},${v|0})`;
    ctx.fillRect(x,y,40,40);
    ctx.strokeStyle='#666';ctx.strokeRect(x,y,40,40);
  });
  fillText(ctx,'红=前景（运动）  蓝=背景    随机更新让模型自然衰减',30,290,'#666',12);
}
function btn_vibeTick(){
  _vibeInit();
  const st=_state.vibe;
  const moving = Math.random()<0.2;
  const val = moving?200+Math.random()*30:100+Math.random()*30;
  // 匹配计数
  let cnt=0;
  st.samples.forEach(s=>{if(Math.abs(s-val)<20)cnt++});
  const isFg = cnt<2;
  st.hist.push({v:val,moving:isFg});
  if(st.hist.length>40)st.hist.shift();
  if(!isFg && Math.random()<0.1){
    const i=(Math.random()*20)|0;
    st.samples[i]=val;
  }
  draw('vibe');
}

// =============== Viola-Jones ===============
function _vjInit(){
  const boxes=[];
  for(let i=0;i<100;i++){
    boxes.push({x:Math.random()*540+30,y:Math.random()*180+40,s:20+Math.random()*60,isFace:Math.random()<0.06,rejected:0});
  }
  _state.vj={boxes,layer:0};
}
drawers.viola_jones = drawers['viola-jones'] = function(ctx){
  if(!_state.vj) _vjInit();
  clear(ctx);
  fillText(ctx,`Viola-Jones级联漏斗：第${_state.vj.layer}/5层  过滤非脸窗口`,20,25,'#333',14);
  const st=_state.vj;
  ctx.fillStyle='#f8f8f0';ctx.fillRect(30,40,580,200);
  let nKeep=0,nFace=0;
  st.boxes.forEach(b=>{
    if(b.rejected>0 && b.rejected<=st.layer){
      ctx.strokeStyle='rgba(200,80,80,0.2)';ctx.lineWidth=1;ctx.strokeRect(b.x,b.y,b.s,b.s*1.2);
    }else if(b.rejected===0){
      nKeep++;
      ctx.strokeStyle=b.isFace?'rgba(50,180,50,0.9)':'rgba(80,120,200,0.5)';ctx.lineWidth=1.5;
      ctx.strokeRect(b.x,b.y,b.s,b.s*1.2);
      if(b.isFace)nFace++;
    }
  });
  fillText(ctx,`剩余窗口: ${nKeep}（真脸${nFace}张）`,30,265);
  const widths=[580,400,260,150,80,45];
  for(let i=1;i<=st.layer;i++){
    ctx.fillStyle=`rgba(91,127,209,${0.2+i*0.1})`;
    ctx.fillRect(30+(580-widths[i-1])/2,277+i*3,widths[i-1],10);
  }
}
function btn_vjNext(){
  if(!_state.vj)_vjInit();
  const st=_state.vj;
  if(st.layer>=5)return;
  st.layer++;
  st.boxes.forEach(b=>{
    if(!b.isFace&&b.rejected===0&&Math.random()<0.3+st.layer*0.1)b.rejected=st.layer;
  });
  draw('viola-jones');
}
function btn_vjReset(){_vjInit();draw('viola-jones')}

// =============== BRIEF ===============
drawers.brief = function(ctx){
  clear(ctx);
  const n=p('brief','n')|0;
  fillText(ctx,`BRIEF：${n}对点亮度比较→${n}位二进制串→汉明距离XOR一秒算完`,20,25,'#333',14);
  const cx=180,cy=160,R=95;
  ctx.fillStyle='#eee';ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle='#5b7fd1';ctx.stroke();
  ctx.strokeStyle='#e55';ctx.lineWidth=1;
  const pairs=[];
  for(let i=0;i<n;i++){
    const a1=Math.random()*Math.PI*2,r1=Math.random()*R;
    const a2=Math.random()*Math.PI*2,r2=Math.random()*R;
    const p1={x:cx+r1*Math.cos(a1),y:cy+r1*Math.sin(a1)};
    const p2={x:cx+r2*Math.cos(a2),y:cy+r2*Math.sin(a2)};
    ctx.beginPath();ctx.moveTo(p1.x,p1.y);ctx.lineTo(p2.x,p2.y);ctx.stroke();
    dot(ctx,p1.x,p1.y,1.5,'#e55');dot(ctx,p2.x,p2.y,1.5,'#44d');
    pairs.push(Math.random()<0.5?'0':'1');
  }
  ctx.fillStyle='#f8f8f0';ctx.fillRect(330,60,270,200);
  fillText(ctx,'二进制描述子（部分）：',340,80);
  ctx.fillStyle='#222';ctx.font='10px monospace';
  let s='';
  pairs.forEach((b,i)=>{
    s+=b;
    if((i+1)%32===0){ctx.fillText(s,340,100+(i/32)*16);s=''}
  });
  if(s)ctx.fillText(s,340,100+Math.floor(pairs.length/32)*16);
  ctx.font='12px sans-serif';
  fillText(ctx,'汉明距离 = POPCNT(a XOR b)',340,210,'#666',12);
  fillText(ctx,'CPU一条指令算完 → 超快匹配',340,230,'#666',12);
}

// =============== BoVW ===============
drawers.bovw = function(ctx){
  clear(ctx);
  const step = _state.bovw?_state.bovw.step:0;
  const titles=['①从图像中提取SIFT特征点','②K-Means聚类成视觉单词','③构建视觉词典(K个聚类中心)','④统计每图词频直方图','⑤SVM/KNN对直方图分类/检索'];
  fillText(ctx,titles[step],20,25,'#333',14);
  if(step===0){
    for(let i=0;i<3;i++){
      const x=50+i*200;
      ctx.fillStyle='#cde';ctx.fillRect(x,60,160,120);ctx.strokeStyle='#5b7fd1';ctx.strokeRect(x,60,160,120);
      for(let j=0;j<25;j++)dot(ctx,x+20+Math.random()*120,80+Math.random()*80,2,'#e55');
      fillText(ctx,'图'+(i+1),x+10,55);
    }
  }else if(step===1){
    const centers=[{x:220,y:160,c:'#e55'},{x:340,y:200,c:'#48d'},{x:400,y:140,c:'#ed4'},{x:280,y:230,c:'#4a8'}];
    centers.forEach(ce=>{for(let i=0;i<30;i++)dot(ctx,ce.x+(Math.random()-0.5)*60,ce.y+(Math.random()-0.5)*40,2,ce.c+'aa');dot(ctx,ce.x,ce.y,7,ce.c)});
  }else if(step===2){
    const words=['蓝天','白云','绿','红','车轮','窗户','树','人脸'],colors=['#48d','#ddd','#4a4','#d44','#333','#88c','#484','#fdb'];
    words.forEach((w,i)=>{const x=50+(i%4)*140,y=90+Math.floor(i/4)*75;ctx.fillStyle=colors[i];ctx.fillRect(x,y,110,55);ctx.fillStyle='#000';ctx.font='bold 14px sans-serif';ctx.textAlign='center';ctx.fillText(w,x+55,y+33);ctx.textAlign='left'});
  }else if(step===3){
    const hists=[[8,6,2,1,0,1,3,0],[1,2,8,6,3,2,0,1],[0,1,1,2,7,6,1,3]],cs=['#48d','#d44','#4a4'];
    hists.forEach((h,hi)=>{fillText(ctx,'图'+(hi+1)+' 词频',50+hi*200,75);h.forEach((v,i)=>{ctx.fillStyle=cs[hi];ctx.fillRect(60+hi*200+i*22,220-v*14,18,v*14)})});
  }else{
    ctx.fillStyle='#f0f0e8';ctx.fillRect(40,80,560,150);
    ctx.fillStyle='#333';ctx.font='16px sans-serif';ctx.textAlign='center';
    ctx.fillText('SVM/KNN对直方图分类',320,130);ctx.fillText('→ 这是"猫/车/人/..."',320,170);
    ctx.font='13px sans-serif';ctx.fillText('深度学习CNN = "自动学词典+端到端分类"',320,210);ctx.textAlign='left';
  }
}
function btn_bovwStep(){
  if(!_state.bovw)_state.bovw={step:0};
  _state.bovw.step=(_state.bovw.step+1)%5;
  draw('bovw');
}

// =============== Region Growing ===============
function _rgInit(){
  const grid=[],visited=[];
  for(let y=0;y<20;y++){const g=[],v=[];for(let x=0;x<40;x++){let val=80+Math.random()*20;if(x>15)val=180+Math.random()*20;if((x-25)*(x-25)+(y-10)*(y-10)<20)val=130+Math.random()*20;g.push(val|0);v.push(0)}grid.push(g);visited.push(v)}
  const q=[{x:30,y:10}];visited[10][30]=2;
  _state.rg={grid,visited,q:q,cnt:0};
}
drawers['region-growing']=drawers.region_growing=function(ctx){
  if(!_state.rg)_rgInit();
  clear(ctx);
  const T=p('region-growing','T')|0;
  fillText(ctx,`区域生长 T=${T}：从种子扩散，灰度差<T就并入`,20,25,'#333',14);
  const st=_state.rg, sz=13;
  for(let y=0;y<20;y++)for(let x=0;x<40;x++){
    let col;
    if(st.visited[y][x]===1)col='#44dd66';
    else if(st.visited[y][x]===2)col='#aaffaa';
    else col=`rgb(${st.grid[y][x]},${st.grid[y][x]},${st.grid[y][x]})`;
    ctx.fillStyle=col;ctx.fillRect(30+x*sz,40+y*sz,sz-1,sz-1);
  }
  dot(ctx,30+30*sz+sz/2-3,40+10*sz+sz/2-3,5,'#e55');
  let cnt=0;st.visited.forEach(r=>r.forEach(v=>{if(v===1)cnt++}));
  fillText(ctx,`已生长 ${cnt} 像素，队列剩余 ${st.q.length}`,30,310);
};
function btn_rgStep(){
  if(!_state.rg)_rgInit();
  const st=_state.rg,T=p('region-growing','T')|0;
  for(let k=0;k<20&&st.q.length>0;k++){
    const {x,y}=st.q.shift();
    st.visited[y][x]=1;
    let sum=0,n=0;
    for(let yy=0;yy<20;yy++)for(let xx=0;xx<40;xx++)if(st.visited[yy][xx]===1){sum+=st.grid[yy][xx];n++}
    const mean=n?sum/n:st.grid[y][x];
    [[1,0],[-1,0],[0,1],[0,-1]].forEach(([dx,dy])=>{
      const nx=x+dx,ny=y+dy;
      if(nx>=0&&nx<40&&ny>=0&&ny<20&&st.visited[ny][nx]===0){
        if(Math.abs(st.grid[ny][nx]-mean)<T){st.visited[ny][nx]=2;st.q.push({x:nx,y:ny})}
      }
    });
  }
  draw('region-growing');
}
function btn_rgReset(){_rgInit();draw('region-growing')}

// =============== 张氏标定 ===============
drawers['zhang-calibration']=drawers.zhang_calibration=function(ctx){
  clear(ctx);
  const n=p('zhang-calibration','n')|0;
  fillText(ctx,`张氏标定：${n}张不同姿态棋盘→单应→内参→重投影优化`,20,25,'#333',14);
  // 相机
  ctx.fillStyle='#4488dd';ctx.fillRect(60,220,20,20);fillText(ctx,'C',65,234,'#fff',11);
  // 光线锥
  ctx.strokeStyle='#4488dd';ctx.lineWidth=1;ctx.setLineDash([2,2]);
  ctx.beginPath();ctx.moveTo(80,230);ctx.lineTo(200,40);ctx.lineTo(600,40);ctx.lineTo(560,200);ctx.closePath();ctx.stroke();
  ctx.setLineDash([]);
  // n张棋盘
  for(let i=0;i<n;i++){
    const t=i/(Math.max(n-1,1));
    const cx=250+t*280,cy=180-t*100,rot=t*0.5-t*t*0.4;
    ctx.save();ctx.translate(cx,cy);ctx.rotate(rot);
    for(let yy=0;yy<4;yy++)for(let xx=0;xx<6;xx++){ctx.fillStyle=(xx+yy)%2?'#222':'#fff';ctx.fillRect(xx*12-36,yy*12-24,12,12)}
    ctx.strokeStyle='#333';ctx.strokeRect(-36,-24,72,48);ctx.restore();
  }
};

// =============== 对极几何 ===============
drawers.epipolar = function(ctx){
  clear(ctx);
  const px=40+p('epipolar','x')|0,py=150;
  fillText(ctx,'对极几何：左图选点p → 右图匹配点必在绿极线l′上',20,25,'#333',14);
  ctx.fillStyle='#222';ctx.fillRect(40,50,250,180);ctx.strokeStyle='#fff';ctx.strokeRect(40,50,250,180);
  fillText(ctx,'左图',150,45,'#fff',12);
  ctx.fillStyle='#222';ctx.fillRect(350,50,250,180);ctx.strokeStyle='#fff';ctx.strokeRect(350,50,250,180);
  fillText(ctx,'右图',465,45,'#fff',12);
  dot(ctx,165,255,6,'#48d');dot(ctx,475,255,6,'#e55');
  fillText(ctx,'Oₗ 左光心',140,280,'#48d',11);fillText(ctx,'Oᵣ 右光心',445,280,'#e55',11);
  line(ctx,165,255,475,255,'#888',1);
  dot(ctx,px,py,6,'#ff0');
  line(ctx,165,255,px,py,'#ff0',1.5);
  const ry=py+40;
  line(ctx,350,ry-40,600,ry+40,'#0f0',2);
  line(ctx,475,255,520,ry,'#ff0',1);
  ctx.fillStyle='rgba(255,255,0,0.06)';ctx.beginPath();ctx.moveTo(165,255);ctx.lineTo(px,py);ctx.lineTo(520,ry);ctx.lineTo(475,255);ctx.closePath();ctx.fill();
  ctx.strokeStyle='#0f0';ctx.setLineDash([3,3]);
  ctx.setLineDash([]);
  fillText(ctx,'绿线=极线(匹配点必在此线)',360,255,'#0f0',12);
}

// =============== SLIC 超像素 / Felzenszwalb 分割示意 ===============
drawers.slic = function(ctx){
  clear(ctx);
  const grid=p('slic','k')|0 || 4;  // 每边超像素数（2~6 → 4~36 个超像素）
  const K=grid*grid;
  fillText(ctx,'SLIC 超像素：在 Lab 颜色+xy 空间做 K-Means 聚类，边界贴附物体轮廓',20,25,'#333',14);
  // 背景：一个"图像"——渐变色块 + 模拟前景目标
  const imgX=50,imgY=50,imgW=540,imgH=230;
  // 先画背景"像素纹理"
  const cells=36;
  for(let i=0;i<cells;i++)for(let j=0;j<Math.floor(cells*imgH/imgW);j++){
    const cx=imgX+i*imgW/cells, cy=imgY+j*imgH/(Math.floor(cells*imgH/imgW));
    const dx=(i-12),dy=(j-6);
    let r=100+dx*5, g=120+Math.sin(i*0.3)*30, b=150+dy*6;
    // 中央一个"圆"目标
    if((dx-6)*(dx-6)+(dy-3)*(dy-3)<10){r=220;g=180;b=80;}
    // 右下角矩形
    if(i>24 && j>9){r=70;g=140;b=200;}
    ctx.fillStyle=`rgb(${r|0},${g|0},${b|0})`;
    ctx.fillRect(cx,cy,imgW/cells+1,imgH/(Math.floor(cells*imgH/imgW))+1);
  }
  // 画超像素中心
  const cols=grid, rows=Math.ceil(K/cols);
  const stepX=imgW/cols, stepY=imgH/rows;
  ctx.strokeStyle='rgba(255,255,255,0.85)';ctx.lineWidth=1.5;
  for(let i=0;i<cols;i++)for(let j=0;j<rows;j++){
    const cx=imgX+stepX*(i+0.5), cy=imgY+stepY*(j+0.5);
    // 超像素：围绕中心画一个近似多边形（正方形加一点扰动）
    ctx.beginPath();
    const S=Math.min(stepX,stepY)*0.48;
    const pts=[[-S,-S],[S,-S],[S,S],[-S,S]];
    pts.forEach(([dx,dy],k)=>{
      const nx=cx+dx+(Math.sin(i*1.7+j*2.3)*S*0.15);
      const ny=cy+dy+(Math.cos(i*0.9+j*1.1)*S*0.15);
      if(k===0)ctx.moveTo(nx,ny);else ctx.lineTo(nx,ny);
    });
    ctx.closePath();ctx.stroke();
    dot(ctx,cx,cy,2,'#ff3');
  }
  fillText(ctx,`K ≈ ${cols*rows} 个超像素（每边 ${cols} 个）；同超像素内颜色一致，边界自动贴合图像边缘`,20,305,'#666',12);
}

// =============== PnP 位姿求解 ===============
drawers.pnp = function(ctx){
  clear(ctx);
  const ang=p('pnp','ang')|0;  // 旋转角
  fillText(ctx,'PnP（Perspective-n-Point）：通过 2D-3D 对应点反推相机位姿 R,t',20,25,'#333',14);
  // 左：3D 世界物体（立方体）
  fillText(ctx,'3D 世界坐标系',60,55,'#666',11);
  ctx.strokeStyle='#999';ctx.strokeRect(50,60,230,170);
  // 画立方体（等轴测）
  const cx=165,cy=150;
  const a=ang*Math.PI/180;
  const proj=(x,y,z)=>{
    const rx=x*Math.cos(a)-z*Math.sin(a);
    const rz=x*Math.sin(a)+z*Math.cos(a);
    const persp=200/(200+rz+50);
    return [cx+rx*persp*40, cy+y*persp*40-30];
  };
  const pts3d=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]];
  const p2d=pts3d.map(p=>proj(p[0],p[1],p[2]));
  const edges=[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
  ctx.strokeStyle='#48d';ctx.lineWidth=1.5;
  edges.forEach(([a,b])=>line(ctx,p2d[a][0],p2d[a][1],p2d[b][0],p2d[b][1],'#48d',1.5));
  p2d.forEach(p=>dot(ctx,p[0],p[1],3,'#48d'));

  // 右：2D 图像平面
  fillText(ctx,'2D 图像平面（投影点）',390,55,'#666',11);
  ctx.strokeStyle='#999';ctx.strokeRect(350,60,280,210);
  // 相机
  fillText(ctx,'相机',470,290,'#e55',12);dot(ctx,490,275,5,'#e55');
  // 投影：把 3D 点用透视投影到 2D（用一个固定内参）
  const fx=400, cx2=490, cy2=165;
  const proj2=(x,y,z)=>{
    const rx=x*Math.cos(a)-z*Math.sin(a);
    const rz=x*Math.sin(a)+z*Math.cos(a)+4; // 相机前方
    return [cx2+fx*rx/rz, cy2+fx*y/rz];
  };
  const p2d2=pts3d.map(p=>proj2(p[0],p[1],p[2]));
  edges.forEach(([a,b])=>line(ctx,p2d2[a][0],p2d2[a][1],p2d2[b][0],p2d2[b][1],'#fa0',1.5));
  p2d2.forEach(p=>dot(ctx,p[0],p[1],3,'#fa0'));
  // 相机到点的射线（虚线）
  ctx.setLineDash([2,3]);
  p2d2.forEach(p=>line(ctx,490,275,p[0],p[1],'#e555',0.8));
  ctx.setLineDash([]);

  fillText(ctx,'输入：已知 3D 点（蓝）+ 对应 2D 点（橙）；输出：相机旋转 R 和平移 t',20,305,'#666',12);
}

// =============== Lucas-Kanade 光流（给 Horn-Schunck 复用） ===============
drawers.lkflow = drawers['lucas-kanade'] = function(ctx){
  clear(ctx);
  const t=p('lkflow','t')|0;
  fillText(ctx,'光流：同一像素在前后两帧的运动向量（箭头方向=运动方向）',20,25,'#333',14);
  // 两帧并排
  ctx.strokeStyle='#999';
  ctx.strokeRect(40,50,260,210);ctx.strokeRect(340,50,260,210);
  fillText(ctx,'第 t 帧',150,45,'#666',11);fillText(ctx,'第 t+1 帧',450,45,'#666',11);
  // 生成网格点
  const pts=[];
  for(let y=80;y<250;y+=30)for(let x=60;x<280;x+=30){
    pts.push([x,y]);
  }
  // 画第 t 帧的特征点
  pts.forEach(([x,y])=>dot(ctx,x,y,2,'#48d'));
  // 第 t+1 帧：做整体"向右下漂移"模拟运动 + 少量噪点
  const dx=20*(t/100), dy=8*(t/100);
  pts.forEach(([x,y])=>{
    const nx=x+dx+300, ny=y+dy;
    dot(ctx,nx,ny,2,'#fa0');
  });
  // 在第 t 帧画箭头
  ctx.strokeStyle='#0f0';ctx.lineWidth=1.5;
  pts.forEach(([x,y])=>{
    const ex=x+dx, ey=y+dy;
    line(ctx,x,y,ex,ey,'#0f0',1.2);
    // 箭头
    ctx.beginPath();
    ctx.moveTo(ex,ey);
    ctx.lineTo(ex-4,ey-2);
    ctx.lineTo(ex-4,ey+2);
    ctx.closePath();ctx.fillStyle='#0f0';ctx.fill();
  });
  fillText(ctx,'绿箭头=光流向量，LK 假设"小运动 + 邻域亮度一致"，求解每个点的 (u,v)',20,285,'#666',12);
}



// 导出 —— 注册到全局
if (typeof window !== 'undefined') { window.__avis_drawers__ = drawers; }


function draw(t){
  const c = ctx(); if(!c) return
  const fn = drawers[t]; if(fn) fn(c)
}

</script>

<style scoped>
.algo-vis{margin:20px 0}
.vis-card{background:linear-gradient(135deg,#f0f7ff 0%,#fff8f0 100%);border:1px solid #d8e3f0;border-radius:12px;padding:20px}
.vis-title{font-size:18px;font-weight:700;color:#1a3a5c;margin-bottom:6px}
.vis-desc{color:#556;margin-bottom:12px;font-size:14px}
.ctrl-row{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:12px;font-size:13px;color:#444}
.ctrl-row label{display:flex;align-items:center;gap:4px}
.ctrl-row input[type=range]{width:110px}
.ctrl-row button{padding:5px 14px;background:#4477dd;color:#fff;border:none;border-radius:5px;cursor:pointer;font-size:12px;transition:background .2s}
.ctrl-row button:hover{background:#2e5fc4}
.explain{margin-top:14px;padding:12px 16px;background:#fff;border-left:3px solid #4477dd;border-radius:4px;font-size:13px;line-height:1.8;color:#333}
.explain :deep(ul){margin:0;padding-left:20px}
.explain :deep(li){margin:4px 0}
.explain :deep(b){color:#4477dd}
canvas{display:block;margin:8px auto;background:#fff;border:1px solid #e0e0e0;border-radius:6px;max-width:100%}
.viz-placeholder{display:flex;align-items:center;justify-content:center;height:320px;background:#f5f8fd;border:1px dashed #c0d0e8;border-radius:6px;color:#6a80a0;font-size:14px;margin:8px auto}
</style>
