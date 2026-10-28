<template>
  <div class="vl-root">
    <!-- ============ 未启动：首屏不下载 OpenCV.js，点击才加载 ============ -->
    <div v-if="status === 'idle'" class="vl-center">
      <div class="vl-big-icon">🎬</div>
      <p class="vl-title">视频真机实验 — 点击启动</p>
      <p class="vl-note">
        这里跑的是<b>真实的视频流</b>：左边是原始视频，右边是算法<b>逐帧处理</b>的结果。<br />
        光流、背景减除、目标跟踪这类算法天生依赖"帧与帧之间"的变化，<b>单张静态图演示不出来</b>，所以必须上视频。<br />
        启动后需要下载一次 OpenCV.js（约 11 MB 源码，HTTP 自动 gzip 后约 3.5 MB），之后浏览器会缓存。<br />
        全部运算都在<b>你本地浏览器</b>里用 WebAssembly 完成，视频<b>不会上传到任何服务器</b>。
      </p>
      <button class="vl-btn vl-btn-primary" @click="start">▶ 启动视频实验（加载 OpenCV.js）</button>
    </div>

    <!-- ============ 加载中 ============ -->
    <div v-else-if="status === 'loading' || status === 'initializing'" class="vl-center">
      <div class="vl-spinner"></div>
      <p class="vl-title">{{ statusText }}</p>
      <div class="vl-progress"><div class="vl-progress-inner"></div></div>
      <p class="vl-note">首次约 5～30 秒（取决于到 GitHub Pages 的链路），之后浏览器缓存，再次打开秒开。</p>
    </div>

    <!-- ============ 失败 ============ -->
    <div v-else-if="status === 'error'" class="vl-center">
      <div class="vl-big-icon">⚠️</div>
      <p class="vl-title">OpenCV.js 加载失败</p>
      <p class="vl-note">{{ errorMsg }}</p>
      <button class="vl-btn" @click="retry">🔄 重新加载</button>
    </div>

    <!-- ============ 就绪 ============ -->
    <template v-else>
      <!-- 工具条 -->
      <div class="vl-toolbar">
        <div class="vl-tool">
          <label>算法</label>
          <select v-model="currentAlgo" @change="onAlgoChange">
            <option v-for="a in algos" :key="a.id" :value="a.id">{{ a.name }}</option>
          </select>
        </div>
        <div class="vl-tool">
          <label>视频源</label>
          <select v-model="currentVideo" @change="onVideoChange">
            <option v-for="v in videos" :key="v.file" :value="v.file">{{ v.name }}</option>
            <option v-if="uploadedName" :value="uploadedUrl">{{ uploadedName }}</option>
          </select>
        </div>
        <div class="vl-tool">
          <label class="vl-upload">📁 上传视频<input type="file" accept="video/*" @change="onUpload" /></label>
        </div>
        <div class="vl-tool vl-tool-btns">
          <button class="vl-btn vl-btn-sm" @click="togglePlay">{{ playing ? '⏸ 暂停' : '▶ 播放' }}</button>
          <button class="vl-btn vl-btn-sm" @click="restartFromHead">↺ 从头开始</button>
          <button class="vl-btn vl-btn-sm" @click="toggleProcess">{{ processing ? '⏹ 停止处理' : '⚡ 开始处理' }}</button>
        </div>
      </div>

      <!-- 双画面：原视频 | 处理结果 -->
      <div class="vl-stage">
        <div class="vl-pane">
          <div class="vl-pane-label">原始视频（输入）</div>
          <div class="vl-canvas-box">
            <video
              ref="videoEl"
              class="vl-video"
              :src="activeSrc"
              playsinline
              muted
              preload="auto"
              @loadedmetadata="onMeta"
              @ended="onEnded"
            ></video>
          </div>
        </div>
        <div class="vl-pane">
          <div class="vl-pane-label">
            算法输出（逐帧实时处理）
            <span class="vl-stat" v-if="procMs > 0">{{ procMs.toFixed(0) }} ms/帧 · {{ frameCount }} 帧</span>
          </div>
          <div class="vl-canvas-box">
            <canvas ref="outCanvas" class="vl-canvas"></canvas>
            <div v-if="!processing" class="vl-overlay-hint">已暂停处理（点上方"开始处理"继续）</div>
            <div v-if="frameError" class="vl-overlay-err">{{ frameError }}</div>
          </div>
        </div>
      </div>

      <!-- 参数滑块 -->
      <div class="vl-params">
        <div class="vl-param" v-for="p in activeParams" :key="p.key">
          <div class="vl-param-head">
            <span>{{ p.label }}</span>
            <b>{{ p.value }}</b>
          </div>
          <input type="range" :min="p.min" :max="p.max" :step="p.step" v-model.number="p.value" @input="onParamChange" />
        </div>
        <p class="vl-hint">{{ activeAlgo.resetNote }}</p>
      </div>

      <p class="vl-desc">{{ activeAlgo.desc }}</p>

      <!-- 代码面板 -->
      <div class="vl-code">
        <div class="vl-code-tabs">
          <button :class="{ on: codeTab === 'py' }" @click="codeTab = 'py'">Python</button>
          <button :class="{ on: codeTab === 'cpp' }" @click="codeTab = 'cpp'">C++</button>
          <button :class="{ on: codeTab === 'js' }" @click="codeTab = 'js'">JavaScript</button>
          <span class="vl-code-spacer"></span>
          <button class="vl-btn vl-btn-sm" @click="copyCode">📋 复制</button>
        </div>
        <pre class="vl-pre"><code>{{ codeText }}</code></pre>
        <p class="vl-code-tip">
          ⬆ 面板里的参数值会<b>跟着上面的滑块实时变</b>，改完直接抄进你自己的项目即可。
        </p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { loadOpenCV } from '../lib/opencv-loader.js'
import { VIDEO_ALGOS, VIDEO_ALGO_MAP, resetVideoState, fillCode } from '../lib/video-algos.js'

const props = defineProps({
  algo: { type: String, default: 'lkflow' },
})

/* ---------------- 静态清单 ---------------- */
const algos = VIDEO_ALGOS.map(a => ({ id: a.id, name: a.name }))

const videos = [
  { file: 'motion-demo.mp4', name: '样例 ① 静止街景 + 运动方块（跟踪 / 光流 / 背景减除）', algo: ['framediff', 'mog2', 'lkflow', 'meanshift', 'camshift'] },
  { file: 'pan-demo.mp4', name: '样例 ② 相机平移的街道（稠密光流）', algo: ['farneback'] },
]

/* ---------------- 响应式状态 ---------------- */
const status = ref('idle')
const statusText = ref('')
const errorMsg = ref('')
const currentAlgo = ref(VIDEO_ALGO_MAP[props.algo] ? props.algo : 'lkflow')
const currentVideo = ref('motion-demo.mp4')
const uploadedUrl = ref('')
const uploadedName = ref('')
const playing = ref(false)
const processing = ref(false)
const procMs = ref(0)
const frameCount = ref(0)
const frameError = ref('')
const codeTab = ref('py')

const videoEl = ref(null)
const outCanvas = ref(null)

const activeAlgo = computed(() => VIDEO_ALGO_MAP[currentAlgo.value])
const activeParams = ref(activeAlgo.value.params.map(p => ({ ...p })))
/* 参数用普通对象参与运算（滑块只改这里的值，模板读 activeParams） */
const paramValues = ref({})
function syncParamValues () { const o = {}; for (const p of activeParams.value) o[p.key] = p.value; paramValues.value = o }

const BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.BASE_URL) || '/'
const VIDEO_BASE = BASE + 'videos/'

const activeSrc = computed(() => {
  if (currentVideo.value === uploadedUrl.value && uploadedUrl.value) return uploadedUrl.value
  return VIDEO_BASE + currentVideo.value
})

const codeText = computed(() => {
  const tpl = activeAlgo.value.code[codeTab.value] || ''
  const body = fillCode(tpl, paramValues.value, {})
  const head = {
    py: '# 依赖：pip install opencv-python  (传统 CV，无需 GPU，树莓派/Jetson 都能跑)\n',
    cpp: '// 依赖：OpenCV 4.x  (apt install libopencv-dev)\n',
    js: '// 依赖：opencv.js（本站 docs/public/lib/opencv.js 单文件版）\n',
  }[codeTab.value]
  return head + '\n' + body
})

/* ---------------- 非响应式的重对象（cv.Mat 绝不能被 Vue 代理，否则 delete 会炸） ---------------- */
let cv = null
let state = {}
let prevMat = null
let rafId = null
let lastTs = 0
let srcCanvas = null
let srcCtx = null
let outCtx = null
let imgBuf = null
let W = 480, H = 360
let disposing = false

const FPS_TARGET = 12
const MAX_W = 480

/* ---------------- 启动 ---------------- */
async function start () {
  status.value = 'loading'
  statusText.value = '正在下载 OpenCV.js …'
  try {
    cv = await loadOpenCV({
      onStage: (s) => {
        if (s === 'loading') { status.value = 'loading'; statusText.value = '正在下载 OpenCV.js …' }
        else if (s === 'script-loaded') { status.value = 'initializing'; statusText.value = '正在编译 WebAssembly …' }
      },
      onProgress: () => {},
    })
    status.value = 'initializing'
    statusText.value = '正在准备视频与画布 …'
    await nextTick()
    setupCanvases()
    status.value = 'ready'
    syncParamValues()
    /* 自动挑一部匹配该算法的样例视频 */
    pickPreferVideo()
    await nextTick()
    attachVideo()
  } catch (e) {
    resetCVLocal()
    status.value = 'error'
    errorMsg.value = (e && e.message) || String(e)
  }
}

function retry () { status.value = 'idle'; errorMsg.value = ''; start() }

function resetCVLocal () {
  stopLoop()
  if (prevMat) { try { prevMat.delete() } catch (_) {} prevMat = null }
  resetVideoState(state)
  state = {}
  cv = null
}

function setupCanvases () {
  srcCanvas = document.createElement('canvas')
  srcCanvas.width = W; srcCanvas.height = H
  srcCtx = srcCanvas.getContext('2d', { willReadFrequently: true })
  imgBuf = new Uint8ClampedArray(W * H * 4)
  if (outCanvas.value) {
    outCanvas.value.width = W; outCanvas.value.height = H
    outCtx = outCanvas.value.getContext('2d')
  }
}

function pickPreferVideo () {
  const v = videos.find(x => x.algo && x.algo.includes(currentAlgo.value))
  if (v) currentVideo.value = v.file
  else if (!uploadedUrl.value) currentVideo.value = 'motion-demo.mp4'
}

/* ---------------- 视频 ---------------- */
function attachVideo () {
  const el = videoEl.value
  if (!el) return
  playing.value = false
  processing.value = false
  frameCount.value = 0
  procMs.value = 0
  frameError.value = ''
  doResetState()
}

function onMeta () {
  const el = videoEl.value
  if (!el || !el.videoWidth) return
  const scale = Math.min(1, MAX_W / el.videoWidth)
  W = Math.max(64, Math.round(el.videoWidth * scale))
  H = Math.max(48, Math.round(el.videoHeight * scale))
  setupCanvases()
  doResetState()
  clearCanvas()
}

function clearCanvas () {
  if (!outCtx) return
  outCtx.fillStyle = '#0b1020'
  outCtx.fillRect(0, 0, outCanvas.value.width, outCanvas.value.height)
  outCtx.fillStyle = 'rgba(255,255,255,.55)'
  outCtx.font = '14px system-ui, sans-serif'
  outCtx.fillText('点击「播放」开始逐帧处理', 14, H / 2)
}

function togglePlay () {
  const el = videoEl.value
  if (!el) return
  if (el.paused) {
    el.play().then(() => { playing.value = true; processing.value = true; startLoop() }).catch(() => {})
  } else {
    el.pause(); playing.value = false
  }
}

function restartFromHead () {
  const el = videoEl.value
  if (!el) return
  doResetState()
  clearCanvas()
  el.currentTime = 0
  el.play().then(() => { playing.value = true; processing.value = true; startLoop() }).catch(() => {})
}

function toggleProcess () { processing.value = !processing.value }

function onEnded () {
  playing.value = false
  processing.value = false
  stopLoop()
  const el = videoEl.value
  if (el) { doResetState(); el.currentTime = 0; el.play().then(() => { playing.value = true; processing.value = true; startLoop() }).catch(() => {}) }
}

function onVideoChange () {
  const el = videoEl.value
  if (!el) return
  el.pause()
  playing.value = false; processing.value = false
  stopLoop()
  doResetState()
  el.load()
  clearCanvas()
}

function onUpload (e) {
  const f = e.target.files && e.target.files[0]
  if (!f) return
  if (uploadedUrl.value) { try { URL.revokeObjectURL(uploadedUrl.value) } catch (_) {} }
  uploadedUrl.value = URL.createObjectURL(f)
  uploadedName.value = '我上传的：' + f.name
  currentVideo.value = uploadedUrl.value
  const el = videoEl.value
  if (el) { el.pause(); stopLoop(); doResetState(); el.load(); clearCanvas() }
}

/* ---------------- 处理主循环 ---------------- */
function startLoop () {
  if (rafId) return
  lastTs = 0
  rafId = requestAnimationFrame(loop)
}

function stopLoop () {
  if (rafId) { cancelAnimationFrame(rafId); rafId = null }
}

function loop (ts) {
  rafId = requestAnimationFrame(loop)
  const el = videoEl.value
  if (!el || el.paused || el.ended || !processing.value || !cv) return
  const gap = 1000 / FPS_TARGET
  if (ts - lastTs < gap) return
  lastTs = ts
  processFrame()
}

function doResetState () {
  if (prevMat) { try { prevMat.delete() } catch (_) {} prevMat = null }
  resetVideoState(state)
  state = {}
  frameCount.value = 0
  frameError.value = ''
}

function processFrame () {
  const el = videoEl.value
  if (!el || !srcCtx || !outCtx || !cv) return
  if (!el.videoWidth) return
  let cur = null, out = null
  const t0 = performance.now()
  try {
    srcCtx.drawImage(el, 0, 0, W, H)
    const img = srcCtx.getImageData(0, 0, W, H)
    cur = cv.matFromImageData(img)
    out = activeAlgo.value.runVideo(cv, prevMat, cur, paramValues.value, state)
    const ow = out.cols, oh = out.rows
    if (outCanvas.value.width !== ow || outCanvas.value.height !== oh) {
      outCanvas.value.width = ow; outCanvas.value.height = oh
      imgBuf = new Uint8ClampedArray(ow * oh * 4)
      octxRebind()
    }
    const src = out.data
    if (src.length === imgBuf.length) imgBuf.set(src)
    else imgBuf.set(src.subarray(0, imgBuf.length))
    outCtx.putImageData(new ImageData(imgBuf, ow, oh), 0, 0)
    frameError.value = ''
  } catch (e) {
    frameError.value = '本帧处理出错：' + ((e && e.message) || e)
  } finally {
    if (out) { try { out.delete() } catch (_) {} }
    if (prevMat) { try { prevMat.delete() } catch (_) {} }
    prevMat = cur
    procMs.value = performance.now() - t0
    frameCount.value++
  }
}

function octxRebind () { if (outCanvas.value) outCtx = outCanvas.value.getContext('2d') }

function onAlgoChange () {
  doResetState()
  pickPreferVideo()
  const el = videoEl.value
  if (el && el.src !== activeSrc.value) { el.load() }
  activeParams.value = VIDEO_ALGO_MAP[currentAlgo.value].params.map(p => ({ ...p }))
  syncParamValues()
  clearCanvas()
}

function onParamChange () {
  syncParamValues()
  /* MOG2 的 history / varThreshold 改了需要重建背景模型 */
  const a = currentAlgo.value
  if (a === 'mog2') { if (state && 'mog' in state) { try { state.mog.delete() } catch (_) {} delete state.mog; delete state._hist } }
  if (a === 'meanshift' || a === 'camshift') { state._needHist = true }
}

async function copyCode () {
  try { await navigator.clipboard.writeText(codeText.value) } catch (_) {}
}

/* ---------------- 生命周期 ---------------- */
onMounted(() => { W = 480; H = 360 })
onBeforeUnmount(() => {
  disposing = true
  stopLoop()
  const el = videoEl.value
  if (el) { el.pause(); el.removeAttribute('src'); el.load() }
  if (prevMat) { try { prevMat.delete() } catch (_) {} prevMat = null }
  resetVideoState(state)
  if (uploadedUrl.value) { try { URL.revokeObjectURL(uploadedUrl.value) } catch (_) {} }
  cv = null
})
</script>

<style scoped>
.vl-root {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  padding: 14px;
  margin: 18px 0;
}
.vl-center { text-align: center; padding: 18px 10px; }
.vl-big-icon { font-size: 38px; line-height: 1; margin-bottom: 8px; }
.vl-title { font-weight: 700; margin: 6px 0 10px; }
.vl-note { font-size: 13px; line-height: 1.85; color: var(--vp-c-text-2); margin: 10px auto; max-width: 720px; }
.vl-btn {
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: all .15s;
}
.vl-btn:hover { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }
.vl-btn-primary {
  background: var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-1);
  color: #fff;
  font-weight: 600;
  padding: 10px 20px;
  font-size: 14px;
}
.vl-btn-primary:hover { opacity: .9; color: #fff; }
.vl-btn-sm { padding: 5px 10px; font-size: 12px; }
.vl-spinner {
  width: 34px; height: 34px; margin: 0 auto 10px;
  border: 3px solid var(--vp-c-divider);
  border-top-color: var(--vp-c-brand-1);
  border-radius: 50%;
  animation: vlspin 1s linear infinite;
}
@keyframes vlspin { to { transform: rotate(360deg); } }
.vl-progress { height: 6px; width: min(420px, 90%); margin: 12px auto 0; background: var(--vp-c-divider); border-radius: 4px; overflow: hidden; }
.vl-progress-inner { height: 100%; width: 40%; background: var(--vp-c-brand-1); border-radius: 4px; animation: vlindet 1.4s ease-in-out infinite; }
@keyframes vlindet { 0% { margin-left: -40%; } 100% { margin-left: 100%; } }

.vl-toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 12px; }
.vl-tool { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.vl-tool label { color: var(--vp-c-text-2); white-space: nowrap; }
.vl-tool select {
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  border-radius: 6px;
  padding: 4px 6px;
  font-size: 12px;
  max-width: 260px;
}
.vl-tool-btns { gap: 6px; margin-left: auto; }
.vl-upload {
  border: 1px dashed var(--vp-c-divider);
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
  color: var(--vp-c-brand-1) !important;
}
.vl-upload input { display: none; }

.vl-stage { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 720px) { .vl-stage { grid-template-columns: 1fr; } }
.vl-pane { min-width: 0; }
.vl-pane-label {
  font-size: 12px; color: var(--vp-c-text-2); margin-bottom: 6px;
  display: flex; justify-content: space-between; align-items: baseline; gap: 6px;
}
.vl-stat { font-size: 11px; color: var(--vp-c-brand-1); white-space: nowrap; }
.vl-canvas-box {
  position: relative;
  background: #0b1020;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 4 / 3;
  display: flex; align-items: center; justify-content: center;
}
.vl-video, .vl-canvas { width: 100%; height: 100%; object-fit: contain; display: block; }
.vl-overlay-hint, .vl-overlay-err {
  position: absolute; left: 8px; bottom: 8px;
  font-size: 11px; padding: 3px 8px; border-radius: 5px;
  background: rgba(0,0,0,.62); color: #ffd873;
}
.vl-overlay-err { top: 8px; bottom: auto; color: #ff9b9b; max-width: 92%; }

.vl-params { margin-top: 12px; display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px 16px; }
.vl-param { min-width: 0; }
.vl-param-head { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 3px; }
.vl-param-head b { color: var(--vp-c-brand-1); font-variant-numeric: tabular-nums; }
.vl-param input[type=range] { width: 100%; accent-color: var(--vp-c-brand-1); }
.vl-hint { grid-column: 1 / -1; font-size: 12px; line-height: 1.7; color: var(--vp-c-text-2); margin: 4px 0 0; }
.vl-desc { font-size: 13px; line-height: 1.8; color: var(--vp-c-text-2); margin: 10px 0 0; }

.vl-code { margin-top: 14px; border: 1px solid var(--vp-c-divider); border-radius: 10px; overflow: hidden; background: var(--vp-c-bg); }
.vl-code-tabs { display: flex; align-items: center; gap: 4px; padding: 6px 8px; border-bottom: 1px solid var(--vp-c-divider); background: var(--vp-c-bg-soft); }
.vl-code-tabs button {
  border: 1px solid transparent; background: transparent; color: var(--vp-c-text-2);
  font-size: 12px; padding: 4px 10px; border-radius: 6px; cursor: pointer;
}
.vl-code-tabs button.on { background: var(--vp-c-bg); border-color: var(--vp-c-divider); color: var(--vp-c-brand-1); font-weight: 600; }
.vl-code-spacer { flex: 1; }
.vl-pre { margin: 0; padding: 12px 14px; overflow-x: auto; font-size: 12px; line-height: 1.7; background: transparent; }
.vl-pre code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; white-space: pre; }
.vl-code-tip { font-size: 12px; color: var(--vp-c-text-2); margin: 0; padding: 8px 14px 10px; border-top: 1px dashed var(--vp-c-divider); }
</style>
