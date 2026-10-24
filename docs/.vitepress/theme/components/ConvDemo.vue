<template>
  <div class="cv-demo">
    <div class="demo-header">
      <h3>🎛️ 卷积是什么？拖一拖就懂</h3>
      <p class="demo-desc">卷积 = 拿一个小窗户（卷积核）在图像上滑，每个位置做"加权平均"。试试选不同核，感受效果！</p>
    </div>
    <div class="demo-body">
      <div class="demo-controls">
        <div class="control-group">
          <label>选择卷积核：</label>
          <div class="btn-group">
            <button :class="{active: kernel==='blur'}" @click="setKernel('blur')">均值模糊</button>
            <button :class="{active: kernel==='gauss'}" @click="setKernel('gauss')">高斯模糊</button>
            <button :class="{active: kernel==='sharpen'}" @click="setKernel('sharpen')">锐化</button>
            <button :class="{active: kernel==='edge'}" @click="setKernel('edge')">边缘检测</button>
            <button :class="{active: kernel==='emboss'}" @click="setKernel('emboss')">浮雕效果</button>
          </div>
        </div>
        <div class="control-group">
          <label>核大小: {{kernelSize}}×{{kernelSize}}</label>
          <input v-model.number="kernelSize" type="range" min="3" max="15" step="2" @input="applyConvolution" />
        </div>
        <div class="control-group">
          <label>自己写3×3核（填数字，点应用）：</label>
          <div class="kernel-editor">
            <div v-for="i in 3" :key="i" class="kernel-row">
              <input v-for="j in 3" :key="j" v-model.number="customKernel[(i-1)*3 + (j-1)]" type="number" step="0.1" />
            </div>
          </div>
          <button @click="applyCustom" class="btn-primary">应用自定义核</button>
        </div>
      </div>
      <div class="kernel-visual">
        <p class="kernel-title">当前卷积核（权重越红越大，越蓝越小）：</p>
        <div class="kernel-grid">
          <div v-for="(w, i) in currentKernel.flat()" :key="i" class="kernel-cell" :style="getKernelColor(w)">
            {{ w.toFixed(1) }}
          </div>
        </div>
      </div>
      <div class="demo-canvases">
        <div class="canvas-col">
          <p>原图（鼠标拖动红框看卷积过程）</p>
          <canvas ref="srcCanvas" width="300" height="300" @mousemove="onMouseMove"></canvas>
        </div>
        <div class="canvas-col">
          <p>卷积后结果</p>
          <canvas ref="dstCanvas" width="300" height="300"></canvas>
        </div>
      </div>
      <div class="demo-explain" v-html="explanation"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const srcCanvas = ref(null)
const dstCanvas = ref(null)
const kernel = ref('blur')
const kernelSize = ref(3)
const customKernel = ref([0,-1,0,-1,5,-1,0,-1,0])
const currentKernel = ref([])
const mousePos = ref({x:150,y:150})
const srcImg = ref(null)

const kernels = {
  blur: (size) => Array(size*size).fill(1/(size*size)),
  gauss: (size) => {
    const s = size, sigma = s/3
    let k = []
    let sum = 0
    const half = Math.floor(s/2)
    for (let y=-half; y<=half; y++) {
      for (let x=-half; x<=half; x++) {
        const v = Math.exp(-(x*x+y*y)/(2*sigma*sigma))
        k.push(v); sum += v
      }
    }
    return k.map(v => v/sum)
  },
  sharpen: (size) => {
    const k = Array(size*size).fill(-1)
    k[Math.floor(size*size/2)] = size*size
    return k
  },
  edge: () => [-1,-1,-1,-1,8,-1,-1,-1,-1],
  emboss: () => [-2,-1,0,-1,1,1,0,1,2]
}

const explanation = computed(() => {
  const desc = {
    blur: '<b>均值模糊</b>：每个像素等于周围所有像素的平均值，相当于"把周围揉在一起"，噪点没了、细节也糊了。就像近视眼不戴眼镜看东西。',
    gauss: '<b>高斯模糊</b>：离中心越近权重越大，越远权重越小（钟形曲线）。比均值模糊更自然，是最常用的模糊，美图秀秀磨皮就是它。',
    sharpen: '<b>锐化</b>：中心权重很大，周围是负的——相当于"我减去周围的平均"，把边缘和细节放大，照片变清晰就是这招。',
    edge: '<b>边缘检测</b>：周围权重负，中心正大。平滑区域加起来是0（黑），只有亮度突变的边缘才会亮起来——这就是"找边"的本质！',
    emboss: '<b>浮雕效果</b>：对角线上一正一负，模拟光线从左上角打过来的凹凸感，像刻在石头上。'
  }
  return desc[kernel.value]
})

function setKernel(name) {
  kernel.value = name
  applyConvolution()
}

function getKernelColor(w) {
  const max = Math.max(...currentKernel.value.flat().map(Math.abs))
  if (w > 0) {
    const r = Math.floor(200 + w/max*55)
    const g = Math.floor(100 + (1-w/max)*155)
    const b = Math.floor(100 + (1-w/max)*155)
    return { background: `rgb(${r},${g},${b})` }
  } else {
    const b = Math.floor(200 + (-w)/max*55)
    const r = Math.floor(100 + (1-(-w)/max)*155)
    const g = Math.floor(100 + (1-(-w)/max)*155)
    return { background: `rgb(${r},${g},${b})` }
  }
}

function applyConvolution() {
  const s = kernel.value === 'edge' || kernel.value === 'emboss' ? 3 : kernelSize.value
  if (kernel.value === 'custom') {
    currentKernel.value = [customKernel.value.slice(0,3), customKernel.value.slice(3,6), customKernel.value.slice(6,9)]
  } else {
    const k = kernels[kernel.value](s)
    const mat = []
    for (let i=0; i<s; i++) mat.push(k.slice(i*s, (i+1)*s))
    currentKernel.value = mat
  }
  convolve()
}

function applyCustom() {
  kernel.value = 'custom'
  applyConvolution()
}

function generateSample() {
  const cvs = srcCanvas.value, ctx = cvs.getContext('2d')
  // 画一个便于看卷积效果的样例图：黑白格子+斜线+圆
  ctx.fillStyle = '#fff'; ctx.fillRect(0,0,300,300)
  ctx.fillStyle = '#000'
  for (let i=0; i<3; i++) for (let j=0; j<3; j++) {
    if ((i+j)%2===0) ctx.fillRect(i*100, j*100, 100, 100)
  }
  ctx.fillStyle = '#888'; ctx.beginPath(); ctx.arc(150,150,60,0,Math.PI*2); ctx.fill()
  ctx.strokeStyle = '#444'; ctx.lineWidth = 3
  ctx.beginPath(); ctx.moveTo(0,300); ctx.lineTo(300,0); ctx.stroke()
  ctx.strokeStyle = '#f0f'; ctx.lineWidth = 5
  ctx.strokeRect(40,40,70,70)
}

function convolve() {
  const src = srcCanvas.value, dst = dstCanvas.value
  const sctx = src.getContext('2d'), dctx = dst.getContext('2d')
  const sdata = sctx.getImageData(0,0,300,300)
  const ddata = dctx.createImageData(300,300)
  const k = currentKernel.value, ks = k.length, half = Math.floor(ks/2)
  
  for (let y=0; y<300; y++) {
    for (let x=0; x<300; x++) {
      let r=0,g=0,b=0
      for (let ky=0; ky<ks; ky++) {
        for (let kx=0; kx<ks; kx++) {
          const px = Math.min(299, Math.max(0, x+kx-half))
          const py = Math.min(299, Math.max(0, y+ky-half))
          const idx = (py*300+px)*4
          r += sdata.data[idx]*k[ky][kx]
          g += sdata.data[idx+1]*k[ky][kx]
          b += sdata.data[idx+2]*k[ky][kx]
        }
      }
      const i = (y*300+x)*4
      ddata.data[i] = Math.max(0,Math.min(255,r))
      ddata.data[i+1] = Math.max(0,Math.min(255,g))
      ddata.data[i+2] = Math.max(0,Math.min(255,b))
      ddata.data[i+3] = 255
    }
  }
  dctx.putImageData(ddata,0,0)
  // 画当前卷积位置的红框
  sctx.strokeStyle = 'red'; sctx.lineWidth = 2
  const h = half; const cx = mousePos.value.x, cy = mousePos.value.y
  sctx.strokeRect(cx-h, cy-h, ks, ks)
}

function onMouseMove(e) {
  const rect = srcCanvas.value.getBoundingClientRect()
  mousePos.value.x = Math.floor((e.clientX-rect.left)/rect.width*300)
  mousePos.value.y = Math.floor((e.clientY-rect.top)/rect.height*300)
  // 重绘原图+红框
  generateSample()
  const ctx = srcCanvas.value.getContext('2d')
  const ks = currentKernel.value.length, half = Math.floor(ks/2)
  ctx.strokeStyle = 'red'; ctx.lineWidth = 2
  ctx.strokeRect(mousePos.value.x-half, mousePos.value.y-half, ks, ks)
}

onMounted(() => {
  generateSample()
  setKernel('blur')
})
</script>

<style scoped>
.cv-demo { border:1px solid #d0d7de; border-radius:8px; padding:20px; margin:20px 0; background:#f6f8fa; }
.demo-header h3 { margin:0 0 8px; }
.demo-desc { color:#57606a; margin:0 0 16px; font-size:14px; }
.demo-body { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
.demo-controls { grid-column:1/-1; display:flex; flex-wrap:wrap; gap:20px; }
.control-group { flex:1; min-width:200px; }
.control-group label { display:block; font-weight:600; margin-bottom:6px; font-size:14px; }
.btn-group { display:flex; flex-wrap:wrap; gap:6px; }
.btn-group button { padding:6px 12px; border:1px solid #d0d7de; background:#fff; border-radius:4px; cursor:pointer; font-size:13px; }
.btn-group button.active { background:#0969da; color:#fff; border-color:#0969da; }
.btn-primary { padding:6px 14px; background:#2da44e; color:#fff; border:none; border-radius:4px; cursor:pointer; margin-top:8px; }
.kernel-editor { display:inline-grid; grid-template-columns:repeat(3,50px); gap:4px; margin-bottom:8px; }
.kernel-editor input { width:50px; text-align:center; padding:4px; border:1px solid #d0d7de; border-radius:4px; }
.kernel-visual { grid-column:1/-1; }
.kernel-title { margin:0 0 8px; font-size:14px; }
.kernel-grid { display:inline-grid; grid-template-columns:repeat(auto-fill, 50px); gap:4px; }
.kernel-cell { width:50px; height:50px; display:flex; align-items:center; justify-content:center; border:1px solid #d0d7de; border-radius:4px; font-family:monospace; font-size:12px; color:#000; }
.demo-canvases { display:flex; gap:20px; grid-column:1/-1; justify-content:center; flex-wrap:wrap; }
.canvas-col { text-align:center; }
.canvas-col p { margin:0 0 6px; font-size:14px; font-weight:600; }
.canvas-col canvas { border:1px solid #d0d7de; background:#fff; cursor:crosshair; }
.demo-explain { grid-column:1/-1; padding:12px; background:#fff8c5; border-left:4px solid #d4a72c; border-radius:4px; font-size:14px; line-height:1.6; }
</style>