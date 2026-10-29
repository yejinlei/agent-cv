// OpenCV.js 加载器（极简版）
//
// 设计原则：
//   - 只在用户明确点"▶ 启动"时才开始加载，不做任何自动预热
//   - 只用最朴素的 <script src=... async> 追加到 head，不设 crossOrigin、
//     不用 preload、不用 fetch、不用 XHR，与"直接在浏览器地址栏打开 opencv.js"
//     的行为完全一致——既然那个能秒开，就不要加花活。
//   - 监听 script.onload → 等 cv.onRuntimeInitialized → cv.Mat 就绪即 resolve
//   - 全局单例，多组件共享同一次加载结果
//
// 状态：idle → loading → ready / error

// @ts-ignore
const BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.BASE_URL) || '/'
const CV_URL = BASE.replace(/\/$/, '') + '/lib/opencv.js'

let cvPromise = null
let cvInstance = null
let scriptEl = null

function remove (el) {
  if (el && el.parentNode) el.parentNode.removeChild(el)
}

/* ----------------------------- 主加载入口 ----------------------------- */
export function loadOpenCV (opts = {}) {
  // 1. 已经就绪
  if (cvInstance && typeof cvInstance.Mat === 'function') {
    opts.onStage && opts.onStage('ready')
    return Promise.resolve(cvInstance)
  }
  // 2. 已经在加载中
  if (cvPromise && !opts.force) return cvPromise
  if (opts.force) resetCV()

  opts.onStage && opts.onStage('loading')

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
      if (typeof window !== 'undefined' && window.cv) {
        try { delete window.cv.onRuntimeInitialized } catch (_) { window.cv.onRuntimeInitialized = undefined }
      }
      cvPromise = null
      opts.onError && opts.onError(err)
      reject(err)
    }

    // 5 分钟超时
    timeoutId = setTimeout(() => {
      fail(new Error('OpenCV.js 加载超时。建议点下方"🔗 直链预热"在新标签页单独打开一次（看到代码就关），再回本页点重试。'))
    }, 5 * 60 * 1000)
    if (opts.signal) {
      if (opts.signal.aborted) { fail(new DOMException('aborted','AbortError')); return }
      opts.signal.addEventListener('abort', () => fail(new DOMException('aborted','AbortError')), { once: true })
    }

    // 预置 cv 对象，等 WASM 就绪后触发
    if (typeof window !== 'undefined' && (!window.cv || typeof window.cv !== 'object')) {
      window.cv = {}
    }
    window.cv.onRuntimeInitialized = function () {
      // 再等 cv.Mat 出来
      let tries = 0
      const tick = () => {
        if (settled) return
        if (window.cv && typeof window.cv.Mat === 'function') {
          opts.onStage && opts.onStage('ready')
          done(window.cv); return
        }
        if (++tries > 300) {
          fail(new Error('WebAssembly 初始化完成但 cv.Mat 未就绪，请刷新重试'))
          return
        }
        setTimeout(tick, 50)
      }
      tick()
    }

    // 关键：最朴素的 script 标签，不带任何跨域/非必要属性
    // 这和用户"单独打开 opencv.js 秒开"走的是同一条浏览器加载链路
    scriptEl = document.createElement('script')
    scriptEl.src = CV_URL
    scriptEl.async = true
    scriptEl.dataset.cvScript = '1'
    scriptEl.onload = () => {
      opts.onStage && opts.onStage('initializing')
      // onload 时 onRuntimeInitialized 可能已经触发过（如果 cv.Mat 已就绪）
      if (window.cv && typeof window.cv.Mat === 'function') {
        opts.onStage && opts.onStage('ready'); done(window.cv); return
      }
      // 否则等 onRuntimeInitialized 回调
    }
    scriptEl.onerror = () => {
      fail(new Error('OpenCV.js 脚本下载失败。建议点下方"🔗 直链预热"在新标签页单独打开一次，再回本页重试。'))
    }
    document.head.appendChild(scriptEl)
  }).catch(err => { cvPromise = null; throw err })

  return cvPromise
}

export function isCVReady () { return !!(cvInstance && typeof cvInstance.Mat === 'function') }
export function getCVIfReady () { return isCVReady() ? cvInstance : null }
export function getCVUrl () { return CV_URL }
export function openCVUrl () {
  if (typeof window !== 'undefined') window.open(CV_URL, '_blank', 'noopener')
}
export function resetCV () {
  cvPromise = null; cvInstance = null
  remove(scriptEl); scriptEl = null
  if (typeof window !== 'undefined' && window.cv) {
    try { delete window.cv.onRuntimeInitialized } catch (_) { window.cv.onRuntimeInitialized = undefined }
  }
}

// 提供一个空 stub，保留原调用点但不做任何事
export function warmupOpenCV () {}
