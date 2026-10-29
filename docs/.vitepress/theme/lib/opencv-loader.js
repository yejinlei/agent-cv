// OpenCV.js 加载器（缓存预热版）
//
// 核心问题：单独打开 https://yejinlei.github.io/agent-cv/lib/opencv.js 秒开，
// 但在站内用 <script> 加载时，因为 VitePress 会预取十几个章节的 JS chunk，
// 和 opencv.js 抢同一个域名的 HTTP/2 连接，在部分网络环境下会排队超时。
//
// 解法：启动时先用一个隐藏 <iframe src=opencv.js> 去"灌缓存"——iframe 加载
// 和页面其他资源完全独立、会走浏览器原生 HTTP 缓存；等 iframe onload 时，
// 文件已经 100% 在浏览器磁盘缓存里，再插入 <script> 就能从本地缓存同步读取，
// 绕过排队。整个过程用户无感，不需要手动开新标签。
//
// 状态：idle → prewarming → loading → initializing → ready / error

// @ts-ignore
const BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.BASE_URL) || '/'
const CV_URL = BASE.replace(/\/$/, '') + '/lib/opencv.js'

let cvPromise = null
let cvInstance = null
let scriptEl = null
let warmupIframe = null

function remove (el) {
  if (el && el.parentNode) el.parentNode.removeChild(el)
}
function cleanupIframe () {
  if (warmupIframe) {
    try { warmupIframe.src = 'about:blank' } catch (_) {}
    remove(warmupIframe)
    warmupIframe = null
  }
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

  cvPromise = new Promise((resolve, reject) => {
    let settled = false
    let stage = 'prewarming'
    const setStage = (s) => { stage = s; opts.onStage && opts.onStage(s) }

    const done = (cv) => {
      if (settled) return
      settled = true; cvInstance = cv
      cleanupIframe()
      resolve(cv)
    }
    const fail = (err) => {
      if (settled) return
      settled = true
      remove(scriptEl); scriptEl = null
      cleanupIframe()
      if (typeof window !== 'undefined' && window.cv) {
        try { delete window.cv.onRuntimeInitialized } catch (_) { window.cv.onRuntimeInitialized = undefined }
      }
      cvPromise = null
      opts.onError && opts.onError(err)
      reject(err)
    }

    // 兜底超时：10 分钟（iframe 预热+脚本执行足够宽裕；
    // 真要失败也不会是因为超时，而是 onerror）
    const timeoutId = setTimeout(() => {
      fail(new Error('OpenCV.js 加载超时。如果持续失败，请点下方「🔗 直链预热」在新标签页单独打开一次（看到代码就关），再回本页重试。'))
    }, 10 * 60 * 1000)

    // --- 阶段 2：等 iframe 把 opencv.js 灌进缓存后，插入 <script> 真正执行 ---
    const insertScript = () => {
      if (settled) return
      setStage('loading')

      // 预置 cv 对象，等 WASM 就绪回调
      if (typeof window !== 'undefined' && (!window.cv || typeof window.cv !== 'object')) {
        window.cv = {}
      }
      window.cv.onRuntimeInitialized = function () {
        let tries = 0
        const tick = () => {
          if (settled) return
          if (window.cv && typeof window.cv.Mat === 'function') {
            setStage('ready')
            done(window.cv); return
          }
          if (++tries > 300) {
            clearTimeout(timeoutId)
            fail(new Error('WebAssembly 初始化完成但 cv.Mat 未就绪，请刷新重试'))
            return
          }
          setTimeout(tick, 50)
        }
        tick()
      }

      scriptEl = document.createElement('script')
      scriptEl.src = CV_URL
      scriptEl.async = true
      scriptEl.dataset.cvScript = '1'
      scriptEl.onload = () => {
        setStage('initializing')
        // onload 时 onRuntimeInitialized 可能已经触发过（缓存命中时同步执行）
        if (window.cv && typeof window.cv.Mat === 'function') {
          clearTimeout(timeoutId)
          setStage('ready'); done(window.cv); return
        }
      }
      scriptEl.onerror = () => {
        clearTimeout(timeoutId)
        fail(new Error('OpenCV.js 脚本下载失败。建议点下方「🔗 直链预热」在新标签页单独打开一次，再回本页重试。'))
      }
      document.head.appendChild(scriptEl)
    }

    // --- 阶段 1：用隐藏 iframe 先把文件拉到浏览器缓存 ---
    //
    // 只有当缓存里明显没有这份文件时才预热；如果用户已经预热过
    // （或之前加载过一次），直接插 script 走缓存，省一次请求。
    // 我们没法 100% 检测缓存命中，所以用一个简单启发式：
    // 如果 cvInstance/cvPromise 存在说明已经加载过；
    // 如果 memory cache 命中，iframe onload 会立刻触发，不浪费时间。
    setStage('prewarming')

    // 如果 performance API 能看出来资源已经在缓存里，就跳过 iframe
    let alreadyCached = false
    try {
      const entries = performance.getEntriesByName(CV_URL)
      if (entries.length > 0) {
        const e = entries[entries.length - 1]
        // transferSize 为 0 且 decodedBodySize > 0 说明命中 HTTP 缓存
        if (e.transferSize === 0 && e.decodedBodySize > 0) alreadyCached = true
      }
    } catch (_) {}

    if (alreadyCached) {
      insertScript()
    } else {
      warmupIframe = document.createElement('iframe')
      warmupIframe.style.cssText = 'position:absolute;width:0;height:0;border:0;visibility:hidden;'
      warmupIframe.src = CV_URL
      warmupIframe.onload = () => {
        // iframe 加载完 = 文件已在浏览器缓存
        // 稍微再等 50ms 让浏览器把缓存落盘
        setTimeout(insertScript, 50)
      }
      warmupIframe.onerror = () => {
        // iframe 加载失败也继续尝试直接插 script，不阻断
        insertScript()
      }
      // iframe 兜底：15 秒还没 onload 也直接走 script 分支，不卡死
      setTimeout(() => { if (!settled && stage === 'prewarming') insertScript() }, 15000)
      document.body.appendChild(warmupIframe)
    }
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
  cleanupIframe()
  if (typeof window !== 'undefined' && window.cv) {
    try { delete window.cv.onRuntimeInitialized } catch (_) { window.cv.onRuntimeInitialized = undefined }
  }
}
export function warmupOpenCV () {}
