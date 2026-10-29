<template>
  <div class="math-vis">
    <div class="tab-bar">
      <button v-for="t in tabs" :key="t.id" :class="['tab-btn', {active: current === t.id}]" @click="current = t.id">{{ t.name }}</button>
    </div>

    <div class="vis-area">
      <!-- 1. 像素与邻域 -->
      <div v-if="current === 'pixel'" class="sub-vis">
        <h3>🧩 像素是什么？图像就是数字矩阵</h3>
        <p class="desc">图像是由一个个小格子（像素）组成的，每个格子存一个0~255的数字，0=黑，255=白，中间是灰。</p>
        <canvas ref="pixelCanvas" width="500" height="450" @mousemove="pixelHover" @mouseleave="pixelLeave"></canvas>
        <div class="ctrl-row">
          <label>鼠标悬停像素：坐标 ({{ hoverX }}, {{ hoverY }})，灰度值 = <b>{{ hoverVal }}</b></label>
        </div>
      </div>

      <!-- 2. 邻域与距离 -->
      <div v-if="current === 'neighbor'" class="sub-vis">
        <h3>📍 4邻域、8邻域、欧氏距离</h3>
        <p class="desc">红色是中心像素，橙色是4邻域（上下左右，距离=1），黄色是8邻域（加对角，距离=√2）。</p>
        <canvas ref="neighborCanvas" width="500" height="400"></canvas>
        <div class="ctrl-row">
          <label>距离类型：</label>
          <select v-model="distType">
            <option value="4">4邻域（曼哈顿距离，走直角）</option>
            <option value="8">8邻域（切比雪夫距离，可以斜走）</option>
            <option value="e" selected>欧氏距离（直线距离）</option>
          </select>
        </div>
      </div>

      <!-- 3. 卷积 -->
      <div v-if="current === 'conv'" class="sub-vis">
        <h3>🔲 卷积：滑动的3×3小窗口，每个位置做加权求和</h3>
        <p class="desc">卷积核就是一个小数字矩阵，在原图上滑，每个位置把对应位置相乘再加起来，就得到新图像的一个像素。</p>
        <canvas ref="convCanvas" width="640" height="380"></canvas>
        <div class="ctrl-row">
          <label>卷积核：</label>
          <select v-model="kernelType">
            <option value="blur">均值模糊（全1/9）</option>
            <option value="gauss">高斯模糊（中间大周围小）</option>
            <option value="sharpen" selected>锐化（突出中间）</option>
            <option value="edge">边缘检测（周围-1中间8）</option>
            <option value="emboss">浮雕</option>
          </select>
          <label style="margin-left:20px">滑动位置 x:</label>
          <input type="range" min="0" max="4" v-model.number="convX" />
          <label>y:</label>
          <input type="range" min="0" max="4" v-model.number="convY" />
        </div>
        <p class="calc">当前输出像素 = 加权求和 = <b>{{ convResult.toFixed(1) }}</b>（归一化后）</p>
      </div>

      <!-- 4. 梯度 Sobel -->
      <div v-if="current === 'grad'" class="sub-vis">
        <h3>📈 梯度：像素值变化有多快？边缘就是梯度大的地方</h3>
        <p class="desc">Sobel算子用两个3×3核，分别算x方向（左右变化）和y方向（上下变化）的梯度，合起来就是边缘强度。</p>
        <canvas ref="gradCanvas" width="600" height="300"></canvas>
        <div class="ctrl-row">
          <label>边缘方向：</label>
          <select v-model="edgeDir">
            <option value="v" selected>垂直边缘（左右明暗跳变）</option>
            <option value="h">水平边缘（上下明暗跳变）</option>
            <option value="d">斜边缘</option>
          </select>
        </div>
        <p class="calc">Gx = 左右差值；Gy = 上下差值；边缘强度 = √(Gx² + Gy²) = <b>{{ gradMag.toFixed(1) }}</b></p>
      </div>

      <!-- 5. 阈值分割 -->
      <div v-if="current === 'thresh'" class="sub-vis">
        <h3>✂️ 阈值分割：一刀把图切成"前景"和"背景"</h3>
        <p class="desc">灰度值大于阈值设为白（前景），小于设为黑（背景）。拖动阈值滑块看效果。</p>
        <canvas ref="threshCanvas" width="600" height="300"></canvas>
        <div class="ctrl-row">
          <label>阈值 T = {{ threshT }}</label>
          <input type="range" min="0" max="255" v-model.number="threshT" />
        </div>
      </div>

      <!-- 6. 霍夫直线 -->
      <div v-if="current === 'hough'" class="sub-vis">
        <h3>📐 霍夫变换：每个点"投票"，得票最多的线就是真直线</h3>
        <p class="desc">直角坐标系里的一个点(x,y)，在极坐标(ρ,θ)空间里对应一条正弦曲线；很多条曲线交于一点，说明这些点都在同一条直线上。</p>
        <canvas ref="houghCanvas" width="640" height="300"></canvas>
        <div class="ctrl-row">
          <label>点的数量：{{ houghN }}</label>
          <input type="range" min="3" max="20" v-model.number="houghN" />
        </div>
        <p class="calc">每个点投一票，交点处峰值 = <b>{{ houghPeak }}</b> 票 → 这就是检测出的直线</p>
      </div>

      <!-- 7. Harris 角点 -->
      <div v-if="current === 'harris'" class="sub-vis">
        <h3>🔺 Harris角点：往任何方向小窗口一动，灰度都大变的点就是角点</h3>
        <p class="desc">平坦区：怎么动灰度都不变；边缘：沿边动不变、跨边动变；角点：往哪动都变 → 这就是我们要找的特征点。</p>
        <canvas ref="harrisCanvas" width="600" height="220"></canvas>
        <div class="ctrl-row">
          <label>窗口类型：</label>
          <select v-model="harrisType">
            <option value="flat">平坦区（无特征）</option>
            <option value="edge">边缘（单方向特征）</option>
            <option value="corner" selected>角点（两个方向都有特征）</option>
          </select>
        </div>
      </div>

      <!-- 8. 傅里叶频域 -->
      <div v-if="current === 'fourier'" class="sub-vis">
        <h3>🌊 傅里叶变换：任何图像都能拆成不同频率的正弦波叠加</h3>
        <p class="desc">低频=整体明暗/大色块（模糊的"底色"），高频=细节/边缘/噪声（尖锐的跳变）。拖动滑块看不同频率组合出的效果。</p>
        <canvas ref="fourierCanvas" width="640" height="300"></canvas>
        <div class="ctrl-row">
          <label>保留低频：保留前{{ freqCut }}个频率分量</label>
          <input type="range" min="1" max="20" v-model.number="freqCut" />
        </div>
        <p class="calc">频率数越多，图像越清晰；只留低频 → 模糊（高斯模糊就是低通滤波），去掉低频只剩高频 → 只剩边缘</p>
      </div>

      <!-- 9. RANSAC -->
      <div v-if="current === 'ransac'" class="sub-vis">
        <h3>🎯 RANSAC：随机抽两个点画直线，看有多少点"站在这条线附近"，最多的就是真相</h3>
        <p class="desc">外点（噪声/错点）会干扰最小二乘法；RANSAC每次随机挑两个点试，谁支持的内点最多谁赢，对噪声超鲁棒。</p>
        <canvas ref="ransacCanvas" width="600" height="300"></canvas>
        <div class="ctrl-row">
          <button @click="ransacStep">点我试一次随机抽样</button>
          <span style="margin-left:20px">已迭代 {{ ransacIter }} 次，最佳内点数 = <b>{{ ransacBest }}</b></span>
          <button @click="ransacReset" style="margin-left:20px">重置</button>
        </div>
      </div>

      <!-- 10. 光流 Lucas-Kanade -->
      <div v-if="current === 'lk'" class="sub-vis">
        <h3>🏃 光流：同一个像素在相邻两帧之间移动了多少？</h3>
        <p class="desc">亮度恒定假设：同一个点在两帧里灰度一样；小运动假设：移动距离很小；邻域一致假设：小窗口里所有点动得一样。解Ax=b就能得到移动向量。</p>
        <canvas ref="lkCanvas" width="600" height="250"></canvas>
        <div class="ctrl-row">
          <label>物体移动速度：{{ lkSpeed }}</label>
          <input type="range" min="1" max="10" v-model.number="lkSpeed" />
        </div>
      </div>

      <!-- 11. 形态学 -->
      <div v-if="current === 'morph'" class="sub-vis">
        <h3>🧹 形态学：用小"刷子"（结构元）对二值图做腐蚀/膨胀</h3>
        <p class="desc">腐蚀：结构元贴住的区域必须全白才保留（毛刺被吃掉）；膨胀：只要有一点白就扩张（小洞被填上）；开运算=先腐后膨（去毛刺），闭运算=先膨后腐（填小洞）。</p>
        <canvas ref="morphCanvas" width="640" height="240"></canvas>
        <div class="ctrl-row">
          <label>操作：</label>
          <select v-model="morphOp">
            <option value="erode">腐蚀</option>
            <option value="dilate" selected>膨胀</option>
            <option value="open">开运算（去毛刺）</option>
            <option value="close">闭运算（填小洞）</option>
          </select>
          <label style="margin-left:20px">结构元大小：{{ morphK }}×{{ morphK }}</label>
          <input type="range" min="1" max="7" v-model.number="morphK" />
        </div>
      </div>

      <!-- 12. 高斯分布 -->
      <div v-if="current === 'gauss'" class="sub-vis">
        <h3>🔔 高斯函数：中间高、两边慢慢降的"钟形曲线"（最常用的权重）</h3>
        <p class="desc">离中心越近权重越大，越远越小。高斯模糊用它做加权平均，比均值模糊更自然，因为"近的像素更像"。</p>
        <canvas ref="gaussCanvas" width="600" height="280"></canvas>
        <div class="ctrl-row">
          <label>σ（平缓程度，越大越模糊）= {{ gaussSigma.toFixed(1) }}</label>
          <input type="range" min="0.5" max="5" step="0.1" v-model.number="gaussSigma" />
        </div>
      </div>

      <!-- 13. 颜色空间 -->
      <div v-if="current === 'color'" class="sub-vis">
        <h3>🎨 RGB / HSV 颜色空间：换一种"描述颜色"的方式</h3>
        <p class="desc">RGB是红/绿/蓝三盏灯的亮度；HSV是色相（什么颜色）、饱和度（鲜艳不鲜艳）、明度（亮不亮）——做颜色分割HSV更方便，因为颜色只由H决定。</p>
        <canvas ref="colorCanvas" width="600" height="260"></canvas>
        <div class="ctrl-row">
          <label>色相 H = {{ colorH }}°</label>
          <input type="range" min="0" max="360" v-model.number="colorH" />
          <label style="margin-left:20px">饱和度 S = {{ colorS }}%</label>
          <input type="range" min="0" max="100" v-model.number="colorS" />
        </div>
      </div>

      <!-- 14. 直方图 -->
      <div v-if="current === 'hist'" class="sub-vis">
        <h3>📊 灰度直方图：统计每个灰度值在图里有多少像素</h3>
        <p class="desc">直方图均衡化就是"把挤在一起的直方图拉开"，让暗图亮起来、亮图暗下去，对比度自动增强。</p>
        <canvas ref="histCanvas" width="640" height="280"></canvas>
        <div class="ctrl-row">
          <label>图像类型：</label>
          <select v-model="histType">
            <option value="dark">偏暗图像（直方图靠左）</option>
            <option value="bright" selected>偏亮图像（直方图靠右）</option>
            <option value="lowc">低对比度（挤在中间）</option>
            <option value="highc">高对比度（均匀分布）</option>
          </select>
          <label style="margin-left:20px"><input type="checkbox" v-model="histEq" /> 应用直方图均衡化</label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps({
  // 嵌入算法页时，指定默认选中的原理标签（如 'grad'）
  initialTab: { type: String, default: '' },
  // 紧凑模式：算法页内嵌时用，收窄留白并加一行说明
  compact:    { type: Boolean, default: false },
})

const tabs = [
  {id:'pixel', name:'像素矩阵'},
  {id:'neighbor', name:'邻域与距离'},
  {id:'conv', name:'卷积'},
  {id:'grad', name:'梯度/边缘'},
  {id:'thresh', name:'阈值分割'},
  {id:'hough', name:'霍夫变换'},
  {id:'harris', name:'Harris角点'},
  {id:'fourier', name:'傅里叶频域'},
  {id:'ransac', name:'RANSAC'},
  {id:'lk', name:'Lucas-Kanade光流'},
  {id:'morph', name:'形态学运算'},
  {id:'gauss', name:'高斯分布'},
  {id:'color', name:'颜色空间'},
  {id:'hist', name:'直方图'},
]
const current = ref(tabs.some(t => t.id === props.initialTab) ? props.initialTab : 'pixel')

// ---- refs ----
const pixelCanvas = ref(null), neighborCanvas = ref(null), convCanvas = ref(null), gradCanvas = ref(null)
const threshCanvas = ref(null), houghCanvas = ref(null), harrisCanvas = ref(null), fourierCanvas = ref(null)
const ransacCanvas = ref(null), lkCanvas = ref(null), morphCanvas = ref(null), gaussCanvas = ref(null)
const colorCanvas = ref(null), histCanvas = ref(null)

// ---- state ----
const hoverX = ref(0), hoverY = ref(0), hoverVal = ref(128)
const distType = ref('e')
const kernelType = ref('sharpen'), convX = ref(2), convY = ref(2), convResult = ref(0)
const edgeDir = ref('v'), gradMag = ref(0)
const threshT = ref(128)
const houghN = ref(8), houghPeak = ref(0)
const harrisType = ref('corner')
const freqCut = ref(5)
const ransacIter = ref(0), ransacBest = ref(0), ransacPoints = ref([])
const lkSpeed = ref(5)
const morphOp = ref('dilate'), morphK = ref(3)
const gaussSigma = ref(1.5)
const colorH = ref(0), colorS = ref(100)
const histType = ref('bright'), histEq = ref(false)

// ========== 1. 像素矩阵 ==========
function drawPixel() {
  const c = pixelCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  const size = 60, off = 50
  // 7x7 模拟灰度矩阵（中间有个亮块）
  const g = []
  for(let y=0;y<7;y++){
    const row=[]
    for(let x=0;x<7;x++){
      let v = 60 + Math.random()*30
      if(x>=2&&x<=4&&y>=2&&y<=4) v = 180 + Math.random()*40
      if(x===3&&y===3) v=255
      row.push(v|0)
    }
    g.push(row)
  }
  ctx.clearRect(0,0,c.width,c.height)
  for(let y=0;y<7;y++)for(let x=0;x<7;x++){
    const v = g[y][x]
    ctx.fillStyle = `rgb(${v},${v},${v})`
    ctx.fillRect(off+x*size, off+y*size, size-2, size-2)
    ctx.fillStyle = v>150?'#000':'#fff'
    ctx.font='14px monospace'
    ctx.textAlign='center'; ctx.textBaseline='middle'
    ctx.fillText(v, off+x*size+size/2, off+y*size+size/2)
  }
  ctx.fillStyle='#333';ctx.font='16px sans-serif'
  ctx.textAlign='left'
  ctx.fillText('← 每个格子就是一个像素，里面的数字是灰度值', off+7*size+20, off+size*3)
  ctx.fillText('0 = 纯黑，255 = 纯白', off+7*size+20, off+size*3+30)
  c._g = g
}
function pixelHover(e){
  const c = pixelCanvas.value
  const rect = c.getBoundingClientRect()
  const x = e.clientX - rect.left, y = e.clientY - rect.top
  const size=60, off=50
  const gx = ((x-off)/size)|0, gy=((y-off)/size)|0
  if(c._g && gx>=0&&gx<7&&gy>=0&&gy<7){
    hoverX.value=gx; hoverY.value=gy; hoverVal.value=c._g[gy][gx]
  }
}
function pixelLeave(){ hoverVal.value=128 }

// ========== 2. 邻域 ==========
function drawNeighbor(){
  const c = neighborCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  const size=50, off=100
  ctx.clearRect(0,0,c.width,c.height)
  const cx=3, cy=3
  for(let y=0;y<7;y++)for(let x=0;x<7;x++){
    let color='#f5f5f5'
    if(x===cx&&y===cy) color='#ff6b6b'
    else if(distType.value==='4' && Math.abs(x-cx)+Math.abs(y-cy)===1) color='#ffa94d'
    else if(distType.value==='8' && Math.max(Math.abs(x-cx),Math.abs(y-cy))===1) color='#ffd43b'
    else if(distType.value==='e'){
      const d = Math.hypot(x-cx,y-cy)
      if(d===1) color='#ffa94d'
      else if(d<=1.5) color='#ffd43b'
    }
    ctx.fillStyle = color
    ctx.fillRect(off+x*size, off+y*size, size-2, size-2)
    ctx.strokeStyle='#ccc';ctx.strokeRect(off+x*size, off+y*size, size-2, size-2)
  }
  // 标注
  ctx.fillStyle='#333';ctx.font='15px sans-serif';ctx.textAlign='left'
  const labels = [
    `红色：中心像素 (${cx},${cy})`,
    distType.value==='4'?'橙色：4邻域（上下左右，距离=1，共4个）':
    distType.value==='8'?'橙色+黄色：8邻域（加对角，共8个）':
    '橙色：距离=1；黄色：距离≈√2≈1.414',
    '欧氏距离 = √((x1-x2)²+(y1-y2)²)  就是普通直线距离',
  ]
  labels.forEach((t,i)=>ctx.fillText(t, off+8*size, off+i*30+30))
}

// ========== 3. 卷积 ==========
const kernels = {
  blur:   [[1,1,1],[1,1,1],[1,1,1]],
  gauss:  [[1,2,1],[2,4,2],[1,2,1]],
  sharpen:[[0,-1,0],[-1,5,-1],[0,-1,0]],
  edge:   [[-1,-1,-1],[-1,8,-1],[-1,-1,-1]],
  emboss: [[-2,-1,0],[-1,1,1],[0,1,2]],
}
function drawConv(){
  const c = convCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  // 7x7 原图
  const img = []
  for(let y=0;y<7;y++){
    const r=[]
    for(let x=0;x<7;x++){
      // 一个渐变+中间有一条边
      let v = 80 + x*25
      if(y>=3) v=180
      r.push(v|0)
    }
    img.push(r)
  }
  const ks=50, ox=30, oy=30
  // 画原图
  for(let y=0;y<7;y++)for(let x=0;x<7;x++){
    const v=img[y][x]
    ctx.fillStyle=`rgb(${v},${v},${v})`
    ctx.fillRect(ox+x*ks, oy+y*ks, ks-2, ks-2)
    ctx.fillStyle=v>150?'#000':'#fff'
    ctx.font='12px monospace';ctx.textAlign='center';ctx.textBaseline='middle'
    ctx.fillText(v, ox+x*ks+ks/2, oy+y*ks+ks/2)
  }
  // 高亮 3x3 窗口
  const kx=convX.value, ky=convY.value
  ctx.strokeStyle='#ff4757';ctx.lineWidth=3
  ctx.strokeRect(ox+kx*ks-1, oy+ky*ks-1, ks*3, ks*3)

  // 画卷积核
  const k = kernels[kernelType.value]
  const kox=ox+7*ks+50, koy=oy+ks
  ctx.fillStyle='#333';ctx.font='15px sans-serif';ctx.textAlign='center'
  ctx.fillText('卷积核', kox+ks*1.5, koy-20)
  for(let y=0;y<3;y++)for(let x=0;x<3;x++){
    ctx.fillStyle='#e3f2fd'
    ctx.fillRect(kox+x*ks, koy+y*ks, ks-2, ks-2)
    ctx.strokeStyle='#1976d2';ctx.strokeRect(kox+x*ks, koy+y*ks, ks-2, ks-2)
    ctx.fillStyle='#000';ctx.font='bold 14px monospace'
    ctx.fillText(k[y][x], kox+x*ks+ks/2, koy+y*ks+ks/2)
  }

  // 输出图 5x5
  const oox=kox+4*ks+50, ooy=oy+ks
  ctx.fillStyle='#333';ctx.font='15px sans-serif'
  ctx.fillText('输出图', oox+ks*2.5-ks, ooy-20)
  let sum=0, ksum=0
  for(let y=0;y<3;y++)for(let x=0;x<3;x++){
    sum += img[ky+y][kx+x]*k[y][x]
    ksum += k[y][x]
  }
  if(ksum===0) ksum=1
  let out = sum/ksum
  if(out<0) out=0; if(out>255) out=255
  convResult.value=out
  for(let y=0;y<5;y++)for(let x=0;x<5;x++){
    // 预先算所有输出
    let s=0
    for(let j=0;j<3;j++)for(let i=0;i<3;i++) s+=img[y+j][x+i]*k[j][i]
    let v=s/ksum; v=Math.max(0,Math.min(255,v))|0
    ctx.fillStyle=`rgb(${v},${v},${v})`
    ctx.fillRect(oox+x*ks, ooy+y*ks, ks-2, ks-2)
  }
  // 高亮当前位置
  ctx.strokeStyle='#ff4757';ctx.lineWidth=3
  ctx.strokeRect(oox+kx*ks-1, ooy+ky*ks-1, ks, ks)
  // 计算式
  ctx.fillStyle='#333';ctx.font='14px sans-serif';ctx.textAlign='left'
  let formula='当前窗口加权求和 = '
  const parts=[]
  for(let y=0;y<3;y++)for(let x=0;x<3;x++){
    parts.push(`${img[ky+y][kx+x]}×${k[y][x]}`)
  }
  ctx.fillText(formula, ox, oy+7*ks+30)
  ctx.font='12px monospace'
  for(let i=0;i<parts.length;i+=3) ctx.fillText(parts.slice(i,i+3).join(' + '), ox, oy+7*ks+55+(i/3)*20)
}

// ========== 4. 梯度 Sobel ==========
function drawGrad(){
  const c = gradCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const w=120,h=80, cell=20, ox=30, oy=30
  // 构建图像
  const g=[]
  for(let y=0;y<h;y++){
    const r=[]
    for(let x=0;x<w;x++){
      let v = 80
      if(edgeDir.value==='v' && x>=60) v=220
      if(edgeDir.value==='h' && y>=40) v=220
      if(edgeDir.value==='d' && x-y>=20) v=220
      r.push(v|0)
    }
    g.push(r)
  }
  // 画（缩放）
  const scale=2
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
    const v=g[y][x]
    ctx.fillStyle=`rgb(${v},${v},${v})`
    ctx.fillRect(ox+x*scale, oy+y*scale, scale, scale)
  }
  // 取中心 3x3 算 Sobel
  const cx=60,cy=40
  const sobelX=[[-1,0,1],[-2,0,2],[-1,0,1]]
  const sobelY=[[-1,-2,-1],[0,0,0],[1,2,1]]
  let Gx=0,Gy=0
  for(let j=-1;j<=1;j++)for(let i=-1;i<=1;i++){
    Gx += g[cy+j][cx+i]*sobelX[j+1][i+1]
    Gy += g[cy+j][cx+i]*sobelY[j+1][i+1]
  }
  gradMag.value = Math.hypot(Gx,Gy)
  ctx.strokeStyle='#ff4757';ctx.lineWidth=2
  ctx.strokeRect(ox+(cx-1)*scale, oy+(cy-1)*scale, 3*scale, 3*scale)
  // 数值区
  const tx=ox+w*scale+40, ty=oy
  ctx.fillStyle='#333';ctx.font='15px sans-serif';ctx.textAlign='left'
  ctx.fillText(`取边缘附近的 3×3 窗口：`, tx, ty+20)
  ctx.fillText(`Sobel X核（测水平边缘？不，测垂直边缘）：`, tx, ty+50)
  ctx.font='13px monospace'
  ;[[-1,0,1],[-2,0,2],[-1,0,1]].forEach((r,i)=>ctx.fillText(r.join('  '), tx+20, ty+75+i*20))
  ctx.fillStyle='#333';ctx.font='15px sans-serif'
  ctx.fillText(`Gx = ${Gx}（x方向梯度）`, tx, ty+150)
  ctx.fillText(`Gy = ${Gy}（y方向梯度）`, tx, ty+175)
  ctx.fillText(`边缘强度 = √(Gx²+Gy²) = ${gradMag.value.toFixed(1)}`, tx, ty+200)
  ctx.fillStyle='#d63031';ctx.font='bold 14px sans-serif'
  ctx.fillText(gradMag.value>100 ? '✔ 这里是边缘！' : '✘ 这里是平坦区', tx, ty+230)
}

// ========== 5. 阈值分割 ==========
function drawThresh(){
  const c = threshCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const w=200
  // 生成原图（双峰：前景+背景）
  const g=[]
  for(let y=0;y<w;y++){
    const r=[]
    for(let x=0;x<w;x++){
      let v = 60 + Math.random()*40
      if((x-100)**2+(y-100)**2 < 60*60) v = 180+Math.random()*40
      r.push(v|0)
    }
    g.push(r)
  }
  const scale=1.2, ox=30, oy=30
  // 原图
  for(let y=0;y<w;y++)for(let x=0;x<w;x++){
    const v=g[y][x]
    ctx.fillStyle=`rgb(${v},${v},${v})`
    ctx.fillRect(ox+x*scale, oy+y*scale, scale, scale)
  }
  ctx.fillStyle='#333';ctx.font='14px sans-serif';ctx.textAlign='center'
  ctx.fillText('原图（灰度）', ox+w*scale/2, oy+w*scale+20)
  // 阈值后
  const oox=ox+w*scale+60
  for(let y=0;y<w;y++)for(let x=0;x<w;x++){
    const v = g[y][x]>threshT.value?255:0
    ctx.fillStyle=`rgb(${v},${v},${v})`
    ctx.fillRect(oox+x*scale, oy+y*scale, scale, scale)
  }
  ctx.fillStyle='#333';ctx.fillText(`阈值 T=${threshT.value} 分割结果`, oox+w*scale/2, oy+w*scale+20)
  // 直方图
  const hist = new Array(256).fill(0)
  for(let y=0;y<w;y++)for(let x=0;x<w;x++) hist[g[y][x]]++
  const hx=oox, hy=oy+w*scale+40, hw=w*scale, hh=60
  ctx.strokeStyle='#ccc';ctx.strokeRect(hx,hy,hw,hh)
  const maxH=Math.max(...hist)
  ctx.fillStyle='#1976d2'
  for(let i=0;i<256;i++){
    ctx.fillRect(hx+i*hw/256, hy+hh-hist[i]/maxH*hh, hw/256+0.5, hist[i]/maxH*hh)
  }
  ctx.strokeStyle='#ff4757';ctx.lineWidth=2
  ctx.beginPath()
  ctx.moveTo(hx+threshT.value*hw/256, hy)
  ctx.lineTo(hx+threshT.value*hw/256, hy+hh)
  ctx.stroke()
}

// ========== 6. 霍夫 ==========
function drawHough(){
  const c = houghCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  // 左边：原图点
  const W=280,H=280,ox=20,oy=10
  ctx.strokeStyle='#ccc';ctx.strokeRect(ox,oy,W,H)
  ctx.fillStyle='#333';ctx.font='14px sans-serif';ctx.textAlign='center'
  ctx.fillText('直角坐标系 (x,y)', ox+W/2, oy+H+20)
  // 生成一条直线上的点 + 一些噪点
  const pts=[]
  const lineA=0.5, lineB=80 // y=0.5x+80
  for(let i=0;i<houghN.value;i++){
    const x=30+Math.random()*220
    const y=lineA*x+lineB + (Math.random()-0.5)*20
    if(y>10&&y<270) pts.push({x,y})
  }
  // 加点噪声
  for(let i=0;i<3;i++){
    pts.push({x:Math.random()*W, y:Math.random()*H})
  }
  pts.forEach(p=>{
    ctx.fillStyle='#2196f3'
    ctx.beginPath();ctx.arc(ox+p.x,oy+p.y,4,0,Math.PI*2);ctx.fill()
  })
  // 画真值线
  ctx.strokeStyle='#ff9800';ctx.lineWidth=1;ctx.setLineDash([5,5])
  ctx.beginPath();ctx.moveTo(ox,oy+lineB);ctx.lineTo(ox+W,oy+lineA*W+lineB);ctx.stroke()
  ctx.setLineDash([])

  // 右边：霍夫空间
  const hox=ox+W+40, hoy=oy, hW=280, hH=280
  ctx.strokeStyle='#ccc';ctx.strokeRect(hox,hoy,hW,hH)
  ctx.fillStyle='#333';ctx.textAlign='center'
  ctx.fillText('霍夫空间 (ρ,θ) — 每个点对应一条正弦曲线', hox+hW/2, hoy+hH+20)
  // 累加器
  const acc = Array.from({length:180},()=>new Array(200).fill(0))
  const maxRho=Math.hypot(W,H)
  pts.forEach(p=>{
    ctx.strokeStyle='rgba(33,150,243,0.3)';ctx.lineWidth=1
    ctx.beginPath()
    for(let t=0;t<180;t+=3){
      const th=t*Math.PI/180
      const rho=p.x*Math.cos(th)+p.y*Math.sin(th)
      const rr = ((rho+maxRho)/(2*maxRho))*200|0
      acc[t][rr]++
      const px = hox+t/180*hW, py=hoy+hH-rr/200*hH
      if(t===0) ctx.moveTo(px,py); else ctx.lineTo(px,py)
    }
    ctx.stroke()
  })
  // 找峰值
  let peak=0,bestT=0,bestR=0
  for(let t=0;t<180;t++)for(let r=0;r<200;r++) if(acc[t][r]>peak){peak=acc[t][r];bestT=t;bestR=r}
  houghPeak.value=peak
  // 画峰值点
  ctx.fillStyle='#ff4757'
  ctx.beginPath();ctx.arc(hox+bestT/180*hW,hoy+hH-bestR/200*hH,8,0,Math.PI*2);ctx.fill()
  ctx.fillStyle='#d63031';ctx.font='bold 13px sans-serif';ctx.textAlign='left'
  ctx.fillText(`峰值 ${peak} 票 → 检测直线`, hox-10, hoy-5)
  // 把检出的直线画回左图
  const rho = (bestR/200)*2*maxRho - maxRho
  const th=bestT*Math.PI/180
  ctx.strokeStyle='#ff4757';ctx.lineWidth=2
  const x0=ox+rho*Math.cos(th), y0=oy+rho*Math.sin(th)
  const x1=x0+1000*(-Math.sin(th)), y1=y0+1000*Math.cos(th)
  const x2=x0-1000*(-Math.sin(th)), y2=y0-1000*Math.cos(th)
  ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke()
}

// ========== 7. Harris ==========
function drawHarris(){
  const c = harrisCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const cases = {
    flat: {title:'平坦区：窗口怎么动，灰度都不变 → E(u,v)≈0 任意方向', color:'#90caf9', arrow:'↔↕  灰度不变'},
    edge: {title:'边缘：沿边动不变，跨边动变 → 一个方向E大、一个方向E小', color:'#ffd54f', arrow:'→ 沿边不变  ↑ 跨边变'},
    corner:{title:'角点：往哪儿动灰度都变 → 两个方向E都大 ✔', color:'#ef5350', arrow:'↗↘↙↖ 往哪动都变'},
  }
  const cc = cases[harrisType.value]
  // 画图例
  ctx.fillStyle='#333';ctx.font='15px sans-serif';ctx.textAlign='left'
  ctx.fillText(cc.title, 30, 30)
  // 画大色块代表区域
  const size=180, ox=50, oy=60
  if(harrisType.value==='flat'){
    ctx.fillStyle='#e0e0e0';ctx.fillRect(ox,oy,size,size)
  } else if(harrisType.value==='edge'){
    ctx.fillStyle='#e0e0e0';ctx.fillRect(ox,oy,size/2,size)
    ctx.fillStyle='#616161';ctx.fillRect(ox+size/2,oy,size/2,size)
  } else {
    ctx.fillStyle='#e0e0e0';ctx.fillRect(ox,oy,size,size)
    ctx.fillStyle='#616161';ctx.fillRect(ox+size/2,oy,size/2,size)
    ctx.fillStyle=cc.color;ctx.fillRect(ox,oy+size/2,size,size/2)
  }
  // 小窗口
  const wx=ox+size/2-25, wy=oy+size/2-25
  ctx.strokeStyle=cc.color;ctx.lineWidth=4
  ctx.strokeRect(wx,wy,50,50)
  // 箭头示意
  ctx.fillStyle=cc.color;ctx.font='bold 24px sans-serif';ctx.textAlign='center'
  ctx.fillText(cc.arrow, ox+size/2, oy+size+40)

  // E(u,v) 响应曲面
  const gx=ox+size+80, gy=oy+30, gw=200, gh=180
  ctx.fillStyle='#333';ctx.font='14px sans-serif';ctx.textAlign='center'
  ctx.fillText('E(u,v) 响应曲面', gx+gw/2, gy-10)
  ctx.strokeStyle='#ccc';ctx.strokeRect(gx,gy,gw,gh)
  if(harrisType.value==='flat'){
    ctx.fillStyle='#90caf9';ctx.beginPath();ctx.ellipse(gx+gw/2,gy+gh/2,40,30,0,0,Math.PI*2);ctx.fill()
  } else if(harrisType.value==='edge'){
    ctx.fillStyle='#ffd54f';ctx.fillRect(gx+30,gy+20,gw-60,gh-40)
  } else {
    ctx.fillStyle='#ef5350';ctx.beginPath();ctx.arc(gx+gw/2,gy+gh/2,50,0,Math.PI*2);ctx.fill()
  }
  // 公式
  ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='left'
  ctx.fillText('Harris 响应 R = det(M) - k·tr(M)²', gx, gy+gh+25)
  ctx.fillText('平坦区 R≈0，边缘 R<0，角点 R>>0', gx, gy+gh+45)
}

// ========== 8. 傅里叶 ==========
function drawFourier(){
  const c = fourierCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  // 构造一维信号：方波
  const N=200, signal=[]
  for(let i=0;i<N;i++) signal.push(i<N/2?0:1)
  // 用前K个正弦重建
  const K=freqCut.value
  const recon = new Array(N).fill(0.5)
  // 方波傅里叶级数：f(x) = 0.5 + 2/π Σ sin((2k-1)ωx)/(2k-1)
  for(let k=1;k<=K;k++){
    const n=2*k-1
    for(let i=0;i<N;i++){
      recon[i] += 2/Math.PI * Math.sin(n*2*Math.PI*i/N)/n
    }
  }
  // 画原信号
  const ox=30, oy=50, w=280, h=180
  ctx.strokeStyle='#ccc';ctx.strokeRect(ox,oy,w,h)
  ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='center'
  ctx.fillText('原始信号（方波 = 跳变边缘）', ox+w/2, oy-15)
  ctx.strokeStyle='#1976d2';ctx.lineWidth=2;ctx.beginPath()
  signal.forEach((v,i)=>{
    const px=ox+i*w/N, py=oy+h-v*h*0.7-h*0.15
    if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py)
  });ctx.stroke()
  // 画重建
  const rx=ox+w+40
  ctx.strokeStyle='#ccc';ctx.strokeRect(rx,oy,w,h)
  ctx.fillStyle='#333';ctx.fillText(`前 ${K} 个频率重建 = 留前${K}大频率（低通）`, rx+w/2, oy-15)
  ctx.strokeStyle='#e91e63';ctx.lineWidth=2;ctx.beginPath()
  recon.forEach((v,i)=>{
    const px=rx+i*w/N, py=oy+h-v*h*0.7-h*0.15
    if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py)
  });ctx.stroke()
  // 频谱
  ctx.fillStyle='#333';ctx.textAlign='left';ctx.font='13px sans-serif'
  ctx.fillText('🟦 低频 = 整体亮度/大色块（图像"底色"）', ox, oy+h+30)
  ctx.fillText('🟥 高频 = 边缘/细节/噪声（尖锐跳变）', ox, oy+h+50)
  ctx.fillText('👉 高斯模糊 = 只留低频（去掉高频细节）', ox, oy+h+70)
  ctx.fillText('👉 边缘检测 = 只留高频（去掉低频底色）', ox, oy+h+90)
}

// ========== 9. RANSAC ==========
function genRansacPoints(){
  const pts=[]
  // 30个内点
  for(let i=0;i<30;i++){
    const x=Math.random()*500+50
    const y=0.5*x+80+(Math.random()-0.5)*20
    pts.push({x,y,inlier:true})
  }
  // 20个外点
  for(let i=0;i<20;i++){
    pts.push({x:Math.random()*560+20, y:Math.random()*240+20, inlier:false})
  }
  return pts
}
function ransacStep(){
  const pts=ransacPoints.value
  // 随机挑2点
  let i1=0,i2=0
  while(i1===i2){i1=(Math.random()*pts.length)|0;i2=(Math.random()*pts.length)|0}
  const p1=pts[i1],p2=pts[i2]
  // 线 ax+by+c=0
  const a=p2.y-p1.y, b=p1.x-p2.x, c=p2.x*p1.y-p1.x*p2.y
  const n=Math.hypot(a,b)
  let inliers=0
  const thresh=8
  pts.forEach(p=>{
    const d=Math.abs(a*p.x+b*p.y+c)/n
    if(d<thresh) inliers++
  })
  if(inliers>ransacBest.value){
    ransacBest.value=inliers
    ransacCanvas.value._best={a,b,c,n}
  }
  ransacIter.value++
  drawRansac()
}
function ransacReset(){
  ransacPoints.value=genRansacPoints()
  ransacIter.value=0
  ransacBest.value=0
  ransacCanvas.value._best=null
  drawRansac()
}
function drawRansac(){
  const c = ransacCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const ox=20,oy=20,w=560,h=240
  ctx.strokeStyle='#ccc';ctx.strokeRect(ox,oy,w,h)
  ctx.fillStyle='#333';ctx.font='14px sans-serif';ctx.textAlign='left'
  ctx.fillText('🔵 内点（在真线上） + 🔴 外点（噪声/错配点）', ox+10, oy-5)
  ransacPoints.value.forEach(p=>{
    ctx.fillStyle=p.inlier?'#2196f3':'#ff5252'
    ctx.beginPath();ctx.arc(ox+p.x,oy+p.y,3,0,Math.PI*2);ctx.fill()
  })
  if(c._best){
    const {a,b,c}=c._best
    ctx.strokeStyle='#4caf50';ctx.lineWidth=3
    const y0=(-c-a*0)/b, y1=(-c-a*w)/b
    ctx.beginPath();ctx.moveTo(ox,oy+y0);ctx.lineTo(ox+w,oy+y1);ctx.stroke()
    ctx.fillStyle='#4caf50';ctx.font='bold 14px sans-serif'
    ctx.fillText(`最佳拟合线（${ransacBest.value}个点支持）`, ox+10, oy+h+20)
  }
  ctx.fillStyle='#666';ctx.font='13px sans-serif'
  ctx.fillText('每次"点我试一次"=随机抽2个点画一条线，数附近有多少点支持它，多轮后得票最高即真相。最小二乘会被红点带歪，RANSAC不会！', ox+10, oy+h+45)
}

// ========== 10. LK光流 ==========
let lkFrame=0
function drawLK(){
  const c = lkCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const w=250,h=200,oy=30
  // 帧1
  ctx.strokeStyle='#ccc';ctx.strokeRect(20,oy,w,h)
  ctx.fillStyle='#333';ctx.font='13px';ctx.textAlign='center'
  ctx.fillText('帧 t', 20+w/2, oy-10)
  ctx.fillStyle='#e0e0e0';ctx.fillRect(20,oy,w,h)
  const bx=80,by=80,bw=60,bh=60
  ctx.fillStyle='#2196f3';ctx.fillRect(20+bx,oy+by,bw,bh)
  ctx.strokeStyle='#ff4757';ctx.lineWidth=2;ctx.strokeRect(20+bx-5,oy+by-5,bw+10,bh+10)
  ctx.fillStyle='#ff4757';ctx.font='11px';ctx.fillText('跟踪窗口', 20+bx+bw/2, oy+by-10)
  // 帧2 移动
  const dx=lkSpeed.value, dy=0
  ctx.strokeStyle='#ccc';ctx.strokeRect(20+w+40,oy,w,h)
  ctx.fillText('帧 t+1', 20+w+40+w/2, oy-10)
  ctx.fillStyle='#e0e0e0';ctx.fillRect(20+w+40,oy,w,h)
  ctx.fillStyle='#2196f3';ctx.fillRect(20+w+40+bx+dx,oy+by+dy,bw,bh)
  // 原始窗口位置（虚）
  ctx.strokeStyle='#ff4757';ctx.setLineDash([4,4]);ctx.strokeRect(20+w+40+bx-5,oy+by-5,bw+10,bh+10)
  ctx.setLineDash([])
  // 位移箭头
  ctx.strokeStyle='#4caf50';ctx.lineWidth=3
  ctx.beginPath()
  ctx.moveTo(20+w+40+bx+bw/2, oy+by+bh/2)
  ctx.lineTo(20+w+40+bx+bw/2+dx, oy+by+bh/2+dy)
  ctx.stroke()
  ctx.fillStyle='#4caf50';ctx.font='bold 14px sans-serif';ctx.textAlign='left'
  ctx.fillText(`位移 = (${dx}, ${dy}) 像素`, 20+w*2+70, oy+40)
  ctx.fillStyle='#333';ctx.font='13px'
  ctx.fillText('三个假设：', 20+w*2+70, oy+70)
  ctx.fillText('① 亮度恒定（点的灰度不变）', 20+w*2+70, oy+90)
  ctx.fillText('② 运动小（相邻帧位移小）', 20+w*2+70, oy+110)
  ctx.fillText('③ 邻域一致（窗口内点动得一样）', 20+w*2+70, oy+130)
  ctx.fillText('解 Ix·u + Iy·v = -It 得(u,v)', 20+w*2+70, oy+150)
  ctx.fillStyle='#999';ctx.font='12px'
  ctx.fillText('Ix/Iy = x/y方向梯度  It = 时间差', 20+w*2+70, oy+170)
}

// ========== 11. 形态学 ==========
function drawMorph(){
  const c = morphCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const w=180,oy=30, scale=15
  // 原图：方块+毛刺+小洞
  const g=[]
  const N=12
  for(let y=0;y<N;y++){const r=[];for(let x=0;x<N;x++) r.push(0);g.push(r)}
  for(let y=3;y<9;y++)for(let x=2;x<10;x++) g[y][x]=1
  // 毛刺
  g[2][5]=1; g[9][6]=1; g[5][1]=1
  // 小洞
  g[5][5]=0; g[6][7]=0
  function drawGrid(g0,ox,title){
    ctx.strokeStyle='#ccc';ctx.strokeRect(ox-2,oy-2,N*scale+4,N*scale+4)
    for(let y=0;y<N;y++)for(let x=0;x<N;x++){
      ctx.fillStyle=g0[y][x]?'#212121':'#fff'
      ctx.fillRect(ox+x*scale,oy+y*scale,scale-1,scale-1)
    }
    ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='center'
    ctx.fillText(title, ox+N*scale/2, oy+N*scale+20)
  }
  drawGrid(g, 20, '原图（带毛刺+小洞）')
  // 处理
  const k=morphK.value
  function morph(g0, op){
    const out=g0.map(r=>r.slice())
    const r=(k-1)/2|0
    for(let y=0;y<N;y++)for(let x=0;x<N;x++){
      let found0=false, found1=false
      for(let j=-r;j<=r;j++)for(let i=-r;i<=r;i++){
        const ny=y+j,nx=x+i
        if(ny<0||ny>=N||nx<0||nx>=N) continue
        if(g0[ny][nx]===1) found1=true
        if(g0[ny][nx]===0) found0=true
      }
      if(op==='erode') out[y][x] = found0?0:1
      if(op==='dilate') out[y][x] = found1?1:0
    }
    return out
  }
  let out
  if(morphOp.value==='erode') out=morph(g,'erode')
  else if(morphOp.value==='dilate') out=morph(g,'dilate')
  else if(morphOp.value==='open') out=morph(morph(g,'erode'),'dilate')
  else out=morph(morph(g,'dilate'),'erode')
  drawGrid(out, 20+N*scale+60, {erode:'腐蚀后（毛刺被吃掉，图变小）',dilate:'膨胀后（小洞被填上，图变大）',open:'开运算=先腐后膨（去毛刺）',close:'闭运算=先膨后腐（填小洞）'}[morphOp.value])
  // 结构元
  const kox=20+N*scale*2+120
  ctx.fillStyle='#333';ctx.font='13px';ctx.textAlign='center'
  ctx.fillText(`结构元 ${k}×${k}`, kox+k*scale/2, oy-10)
  for(let y=0;y<k;y++)for(let x=0;x<k;x++){
    ctx.fillStyle='#1976d2'
    ctx.fillRect(kox+x*scale, oy+y*scale+20, scale-1, scale-1)
  }
}

// ========== 12. 高斯 ==========
function drawGauss(){
  const c = gaussCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const ox=60,oy=30,w=500,h=220
  ctx.strokeStyle='#ccc';ctx.strokeRect(ox,oy,w,h)
  // 画坐标轴
  ctx.strokeStyle='#999';ctx.beginPath()
  ctx.moveTo(ox,oy+h);ctx.lineTo(ox+w,oy+h)
  ctx.moveTo(ox,oy);ctx.lineTo(ox,oy+h);ctx.stroke()
  ctx.fillStyle='#666';ctx.font='12px';ctx.textAlign='center'
  ctx.fillText('-3σ', ox+w*0.1, oy+h+15)
  ctx.fillText('0', ox+w/2, oy+h+15)
  ctx.fillText('+3σ', ox+w*0.9, oy+h+15)
  // 画高斯曲线
  const σ=gaussSigma.value
  ctx.strokeStyle='#e91e63';ctx.lineWidth=3;ctx.beginPath()
  for(let i=0;i<=w;i++){
    const x = (i/w-0.5)*6*σ
    const y = Math.exp(-x*x/(2*σ*σ))
    const px=ox+i, py=oy+h-y*h*0.9
    if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py)
  }
  ctx.stroke()
  // 填充
  ctx.fillStyle='rgba(233,30,99,0.2)'
  ctx.lineTo(ox+w,oy+h);ctx.lineTo(ox,oy+h);ctx.fill()
  // 3x3 核
  const kox=ox+w+40,koy=oy,ks=40
  ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='center'
  ctx.fillText(`对应 3×3 高斯核（σ=${σ.toFixed(1)}）`, kox+ks*1.5, koy-10)
  const kern=[];let ksum=0
  for(let j=-1;j<=1;j++){const r=[];for(let i=-1;i<=1;i++){
    const v=Math.exp(-(i*i+j*j)/(2*σ*σ));r.push(v);ksum+=v
  };kern.push(r)}
  for(let y=0;y<3;y++)for(let x=0;x<3;x++){
    const v=kern[y][x]/ksum
    const g=255-(v*255*8|0)
    ctx.fillStyle=`rgb(${g},${100+v*155|0},255)`
    ctx.fillRect(kox+x*ks,koy+y*ks+20,ks-2,ks-2)
    ctx.fillStyle='#000';ctx.font='12px monospace';ctx.textAlign='center';ctx.textBaseline='middle'
    ctx.fillText(v.toFixed(2),kox+x*ks+ks/2,koy+y*ks+ks/2+20)
  }
  ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='left';ctx.textBaseline='alphabetic'
  ctx.fillText(`G(x,y) = (1/2πσ²) · e^(-(x²+y²)/2σ²)`, ox, oy+h+40)
  ctx.fillText(`σ越大 → 曲线越"矮胖" → 模糊越厉害`, ox, oy+h+60)
}

// ========== 13. 颜色空间 ==========
function hsv2rgb(h,s,v){
  s/=100;v/=100
  const c=v*s, x=c*(1-Math.abs(((h/60)%2)-1)), m=v-c
  let r,g,b
  if(h<60)[r,g,b]=[c,x,0];else if(h<120)[r,g,b]=[x,c,0];else if(h<180)[r,g,b]=[0,c,x]
  else if(h<240)[r,g,b]=[0,x,c];else if(h<300)[r,g,b]=[x,0,c];else[r,g,b]=[c,0,x]
  return [(r+m)*255|0,(g+m)*255|0,(b+m)*255|0]
}
function drawColor(){
  const c = colorCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  // RGB 三灯
  const ox=40,oy=40,sz=80
  const [r,g,b]=hsv2rgb(colorH.value,colorS.value,100)
  ctx.fillStyle=`rgb(${r},0,0)`;ctx.fillRect(ox,oy,sz,sz)
  ctx.fillStyle=`rgb(0,${g},0)`;ctx.fillRect(ox+sz+10,oy,sz,sz)
  ctx.fillStyle=`rgb(0,0,${b})`;ctx.fillRect(ox+2*sz+20,oy,sz,sz)
  ctx.fillStyle='#333';ctx.font='13px';ctx.textAlign='center'
  ctx.fillText(`R=${r}`, ox+sz/2, oy+sz+20)
  ctx.fillText(`G=${g}`, ox+sz+10+sz/2, oy+sz+20)
  ctx.fillText(`B=${b}`, ox+2*sz+20+sz/2, oy+sz+20)
  ctx.fillText('+', ox+sz+5, oy+sz/2);ctx.fillText('+', ox+2*sz+15, oy+sz/2)
  // 混合结果
  ctx.fillStyle=`rgb(${r},${g},${b})`
  ctx.fillRect(ox+3*sz+50,oy,sz,sz)
  ctx.strokeStyle='#333';ctx.strokeRect(ox+3*sz+50,oy,sz,sz)
  ctx.fillText('混合色', ox+3*sz+50+sz/2, oy+sz+20)
  // HSV 色相环
  const cx=480,cy=150,rad=60
  for(let a=0;a<360;a++){
    const [rr,gg,bb]=hsv2rgb(a,colorS.value,100)
    ctx.strokeStyle=`rgb(${rr},${gg},${bb})`;ctx.lineWidth=8
    ctx.beginPath()
    ctx.arc(cx,cy,rad,a*Math.PI/180,(a+1)*Math.PI/180);ctx.stroke()
  }
  // 选中标
  const th=colorH.value*Math.PI/180
  ctx.fillStyle='#fff';ctx.beginPath()
  ctx.arc(cx+Math.cos(th)*rad, cy+Math.sin(th)*rad, 6,0,Math.PI*2);ctx.fill()
  ctx.strokeStyle='#000';ctx.stroke()
  ctx.fillStyle='#333';ctx.textAlign='center';ctx.font='13px'
  ctx.fillText(`H=${colorH.value}°（色相=是什么颜色）`, cx, cy+rad+30)
  ctx.fillText(`S=${colorS.value}%（饱和度=鲜艳程度）`, cx, cy+rad+50)
  ctx.fillText('V=100%（明度=亮暗）', cx, cy+rad+70)
}

// ========== 14. 直方图 ==========
function drawHist(){
  const c = histCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const W=200
  // 生成图像
  const g=[]
  for(let y=0;y<W;y++){const r=[];for(let x=0;x<W;x++){
    let v
    if(histType.value==='dark') v = 30+Math.random()*60
    else if(histType.value==='bright') v = 160+Math.random()*60
    else if(histType.value==='lowc') v = 100+Math.random()*60
    else v = Math.random()*255
    r.push(v|0)
  };g.push(r)}
  function drawImg(g0,ox,oy,title){
    const scale=1
    for(let y=0;y<W;y++)for(let x=0;x<W;x++){
      const v=g0[y][x]
      ctx.fillStyle=`rgb(${v},${v},${v})`
      ctx.fillRect(ox+x*scale,oy+y*scale,scale,scale)
    }
    ctx.fillStyle='#333';ctx.font='13px';ctx.textAlign='center'
    ctx.fillText(title, ox+W/2, oy+W+20)
  }
  function drawHist0(g0,ox,oy,title){
    const h=new Array(256).fill(0)
    for(let y=0;y<W;y++)for(let x=0;x<W;x++) h[g0[y][x]]++
    const maxH=Math.max(...h)
    ctx.strokeStyle='#ccc';ctx.strokeRect(ox,oy,W,100)
    ctx.fillStyle='#1976d2'
    for(let i=0;i<256;i++){
      ctx.fillRect(ox+i*W/256, oy+100-h[i]/maxH*95, W/256+0.5, h[i]/maxH*95)
    }
    ctx.fillStyle='#333';ctx.font='13px';ctx.textAlign='center'
    ctx.fillText(title, ox+W/2, oy+120)
  }
  function equalize(g0){
    const h=new Array(256).fill(0)
    for(let y=0;y<W;y++)for(let x=0;x<W;x++) h[g0[y][x]]++
    const N=W*W, cdf=new Array(256).fill(0)
    cdf[0]=h[0];for(let i=1;i<256;i++)cdf[i]=cdf[i-1]+h[i]
    const map=[]
    const min=cdf.find(v=>v>0)
    for(let i=0;i<256;i++) map[i]=Math.round((cdf[i]-min)/(N-min)*255)
    const out=[]
    for(let y=0;y<W;y++){const r=[];for(let x=0;x<W;x++)r.push(map[g0[y][x]]);out.push(r)}
    return out
  }
  // 原图 + 直方图
  drawImg(g,30,30,'原图')
  drawHist0(g,30,30+W+40,'原图直方图')
  if(histEq.value){
    const eq=equalize(g)
    drawImg(eq,30+W+60,30,'均衡化后')
    drawHist0(eq,30+W+60,30+W+40,'均衡化后直方图（拉开了）')
  }
}

// ========== 统一绘制调度 ==========
// 每个 drawXXX 内部都会自行判空（const c = xxxCanvas.value; if(!c) return），
// 所以这里绝不能用某个具体 canvas（如 pixelCanvas）是否存在当"总开关"：
// 当页面初始 tab 不是 pixel（例如算法页用 initial-tab="lk" 嵌入）时，
// pixelCanvas 因 v-if 根本没挂载，总守卫会让整个渲染直接退出，表现为"原理图一片空白"。
function render(){
  drawPixel(); drawNeighbor(); drawConv(); drawGrad()
  drawThresh(); drawHough(); drawHarris(); drawFourier()
  drawRansac(); drawLK(); drawMorph(); drawGauss()
  drawColor(); drawHist()
}

// tab 切换会先卸载旧 canvas、再挂载新 canvas，必须等 DOM 更新完再画：
// nextTick 保证 v-if 已完成切换，rAF 再补一次以确保拿到稳定布局尺寸。
function renderStable(){
  nextTick(()=>{
    render()
    requestAnimationFrame(()=>render())
  })
}

onMounted(()=>{
  ransacPoints.value = genRansacPoints()
  renderStable()
  // tab 切换后重绘
  watch(current, ()=>renderStable())
  // state 变化重绘
  ;[distType,kernelType,convX,convY,edgeDir,threshT,houghN,harrisType,freqCut,
    lkSpeed,morphOp,morphK,gaussSigma,colorH,colorS,histType,histEq
  ].forEach(s=>watch(s, render))
})
</script>

<style scoped>
.math-vis{border:1px solid #e0e0e0;border-radius:10px;background:#fafafa;padding:15px;margin:20px 0}
.math-vis-compact{padding:10px 12px;margin:14px 0}
.math-vis-compact .tab-bar{margin-bottom:10px}
.embed-hint{font-size:13px;line-height:1.6;color:#4a5568;background:#eef6ff;border-left:3px solid #4a90d9;padding:8px 12px;border-radius:4px;margin:0 0 10px}
.tab-bar{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:15px}
.tab-btn{padding:8px 14px;border:1px solid #ddd;border-radius:20px;background:#fff;cursor:pointer;font-size:13px;transition:.2s}
.tab-btn:hover{background:#f0f7ff}
.tab-btn.active{background:#1976d2;color:#fff;border-color:#1976d2}
.vis-area{background:#fff;border-radius:8px;padding:20px;min-height:400px;overflow-x:auto}
.sub-vis h3{margin:0 0 8px;font-size:17px;color:#222}
.sub-vis .desc{color:#666;font-size:13px;margin:0 0 12px;line-height:1.6}
.sub-vis canvas{border:1px solid #eee;border-radius:6px;display:block;margin:10px 0;background:#fff}
.ctrl-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:10px 0;font-size:13px;color:#333}
.ctrl-row input[type=range]{width:140px}
.ctrl-row select{padding:4px 8px;border:1px solid #ccc;border-radius:4px}
.calc{background:#fff3e0;padding:8px 12px;border-left:3px solid #ff9800;font-size:13px;color:#333;border-radius:4px;margin:10px 0}
</style>
