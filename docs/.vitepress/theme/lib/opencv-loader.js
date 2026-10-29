// OpenCV.js 加载器：preload 下载 + script 执行，两阶段分离
//
// 关键设计：
//   1. 进入页面立即后台 <link rel=preload as=script> 静默下载，不阻塞渲染；
//      等用户真的点"▶ 启动"时，文件大概率已经在 HTTP 缓存里了，<script> 插入
//      就走 304/disk cache，秒就绪。
//   2. 真正要执行时再插 <script>，async=true 不阻塞 HTML 解析；
//      onload 之后等 onRuntimeInitialized（WASM 编译完成）再 resolve。
//   3. 不使用 setInterval 轮询 performance（会卡主线程、在某些浏览器上读不到进度）；
//      改为监听 link.onload/onerror + 兜底 XHR 下载进度（只在用户点了"启动"后才用）。
//   4. CV_URL 用 import.meta.env.BASE_URL 拼接，避免硬编码 /agent-cv/。
//
// 状态机：idle → preloading（后台预热）→ loading（script 执行中）→ ready → error
//
// 回调：
//   onStage(stage)           -> 阶段变化
//   onProgress({loaded,total,stage}) -> 进度（尽力而为）
//   onError(err)             -> 失败

// @ts-ignore - Vite 注入
const BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.BASE_URL) || '/'
const CV_URL = BASE.replace(/\/$/, '') + '/lib/opencv.js'

let cvPromise = null
let cvInstance = null
let scriptEl = null
let linkEl = null
let preloadStarted = false
let preloadDone = false
let preloadError = null
let warmStart = false  // 用户已点过启动 → 不再静默预热

function remove (el) {
  if (el && el.parentNode) el.parentNode.removeChild(el)
}

function attachLinkProgress (link, onProgress) {
  if (!onProgress) return
  // 读 performance Resource-Timing，最多 1 秒一次，不卡主线程
  let last = -1
  const tick = () => {
    try {
      const entries = performance.getEntriesByName(CV_URL)
      const e = entries && entries[entries.length - 1]
      if (e) {
        const loaded = e.transferSize || e.encodedBodySize || e.decodedBodySize || 0
        if (loaded > 0 && loaded !== last) {
          last = loaded
          // gzip 约 3.5MB，raw 约 11MB；若 loaded 超过 roughTotal 说明没开 gzip
          const roughTotal = 3.5 * 1024 * 1024
          onProgress({ loaded, total: Math.max(roughTotal, loaded), stage: 'downloading' })
        }
        // 已解码完成 → 下载完成
        if (e.decodedBodySize > 0 && e.responseStatus !== 0) {
          onProgress({ loaded: e.decodedBodySize, total: e.decodedBodySize, stage: 'downloaded' })
          return
        }
      }
    } catch (_) {}
    if (!preloadDone && !preloadError) {
      setTimeout(tick, 1000)
    }
  }
  setTimeout(tick, 500)
}

/* ----------------------------- 后台静默预热 ----------------------------- */
export function warmupOpenCV () {
  if (preloadStarted || cvInstance || cvPromise || warmStart) return
  // 已经有个 cv 对象说明可能被其他入口加载过了
  if (typeof window !== 'undefined' && window.cv && typeof window.cv.Mat === 'function') {
    cvInstance = window.cv; return
  }
  preloadStarted = true
  if (typeof document === 'undefined') return
  // 如果页面里已经有 cv script 在下载/执行了，跳过
  if (document.querySelector(`script[src="${CV_URL}"]`)) { preloadDone = true; return }

  linkEl = document.createElement('link')
  linkEl.rel = 'preload'
  linkEl.as = 'script'
  linkEl.href = CV_URL
  linkEl.crossOrigin = 'anonymous'
  linkEl.onload = () => { preloadDone = true; preloadError = null }
  linkEl.onerror = () => { preloadError = new Error('preload failed'); remove(linkEl); linkEl = null }
  document.head.appendChild(linkEl)
}

/* ----------------------------- 主加载入口 ----------------------------- */
export function loadOpenCV (opts = {}) {
  if (cvInstance && typeof cvInstance.Mat === 'function') {
    opts.onStage && opts.onStage('ready')
    return Promise.resolve(cvInstance)
  }
  if (cvPromise && !opts.force) return cvPromise
  if (opts.force) resetCV()

  warmStart = true
  cvPromise = new Promise((resolve, reject) => {
    let settled = false
    let pollId = null
    let timeoutId = null

    const cleanup = () => {
      if (timeoutId) { clearTimeout(timeoutId); timeoutId = null }
      if (pollId) { clearInterval(pollId); pollId = null }
    }
    const done = (cv) => {
      if (settled) return
      settled = true; cleanup(); cvInstance = cv
      resolve(cv)
    }
    const fail = (err) => {
      if (settled) return
      settled = true; cleanup()
      remove(scriptEl); scriptEl = null
      remove(linkEl); linkEl = null
      if (window.cv) { try { delete window.cv.onRuntimeInitialized } catch (_) { window.cv.onRuntimeInitialized = undefined } }
      cvPromise = null
      opts.onError && opts.onError(err)
      reject(err)
    }

    timeoutId = setTimeout(() => {
      fail(new Error('OpenCV.js 加载超时（5 分钟）。GitHub Pages 在国内访问偶有波动，可：① 点下面"直链预热"打开新标签页单独加载一次；② 切换网络；③ 过几分钟再试。'))
    }, 5 * 60 * 1000)
    if (opts.signal) {
      if (opts.signal.aborted) { fail(new DOMException('aborted','AbortError')); return }
      opts.signal.addEventListener('abort', () => fail(new DOMException('aborted','AbortError')), { once: true })
    }

    opts.onStage && opts.onStage('loading')

    // 预置 cv 对象（必须在 append script 之前，避免 WASM 极快就绪时错过回调）
    if (!window.cv || typeof window.cv !== 'object') window.cv = {}
    window.cv.onRuntimeInitialized = function () { waitMatReady() }

    const waitMatReady = () => {
      const check = (tries) => {
        if (settled) return
        if (window.cv && typeof window.cv.Mat === 'function') {
          opts.onStage && opts.onStage('ready')
          done(window.cv); return
        }
        if (tries > 300) { fail(new Error('WebAssembly 初始化完成但 cv.Mat 未就绪，请刷新重试')); return }
        setTimeout(() => check(tries + 1), 50)
      }
      check(0)
    }

    // 开始读下载进度（1 秒一次）
    attachLinkProgress(null, opts.onProgress)

    // 如果预热完成，script 会走缓存 → 下载阶段几乎瞬间跳过
    // 如果预热还没开始 / 失败，这里 insert script 会同时触发下载+解析
    scriptEl = document.createElement('script')
    scriptEl.src = CV_URL
    scriptEl.async = true
    scriptEl.dataset.cvScript = '1'
    scriptEl.onload = () => {
      opts.onStage && opts.onStage('initializing')
      opts.onProgress && opts.onProgress({ stage: 'initializing' })
      if (window.cv && typeof window.cv.Mat === 'function') {
        opts.onStage && opts.onStage('ready'); done(window.cv); return
      }
      // 兜底：每 100ms 检查 cv.Mat
      let tries = 0
      pollId = setInterval(() => {
        tries++
        if (settled) { clearInterval(pollId); return }
        if (window.cv && typeof window.cv.Mat === 'function') {
          clearInterval(pollId); opts.onStage && opts.onStage('ready'); done(window.cv)
        } else if (tries > 600) {
          clearInterval(pollId); fail(new Error('OpenCV.js 脚本已加载，但 WebAssembly 初始化超时。请点"直链预热"单独打开一次再重试。'))
        }
      }, 100)
    }
    scriptEl.onerror = () => {
      fail(new Error('OpenCV.js 脚本下载失败（可能是网络或缓存损坏）。建议点下方"🔗 直链预热"在新标签页单独打开一次，再回本页重试。'))
    }
    document.head.appendChild(scriptEl)
  }).catch(err => { cvPromise = null; throw err })

  return cvPromise
}

export function isCVReady () { return !!(cvInstance && typeof cvInstance.Mat === 'function') }
export function getCVIfReady () { return isCVReady() ? cvInstance : null }
export function getCVUrl () { return CV_URL }
export function isPreloaded () { return preloadDone }
export function openCVUrl () {
  if (typeof window !== 'undefined') window.open(CV_URL, '_blank', 'noopener')
}

export function resetCV () {
  cvPromise = null; cvInstance = null
  remove(scriptEl); scriptEl = null
  remove(linkEl); linkEl = null
  if (typeof window !== 'undefined' && window.cv) {
    try { delete window.cv.onRuntimeInitialized } catch (_) { window.cv.onRuntimeInitialized = undefined }
  }
}
