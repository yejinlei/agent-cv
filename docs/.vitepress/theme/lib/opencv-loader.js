// OpenCV.js 加载器（极简版 · 最稳）
//
// 之前踩过的坑（全都是"自作聪明"搞出来的）：
//   1. 自动 prefetch → credentials/crossorigin 不匹配，浏览器视为两次请求、白下
//   2. setInterval 200ms 轮询 → 11MB 下载期间占主线程，页面看起来白屏卡死
//   3. onRuntimeInitialized 单一钩子 → 缓存命中时 WASM 同步执行完再插脚本，回调不触发
//   4. 隐藏 iframe 预热 → 占同源 HTTP 连接、控制台弹 credentials 警告、部分浏览器下 iframe
//      的 onload 并不代表文件已进主页面缓存
//   5. fetch/ReadableStream 进度条 → 绕开 HTTP 缓存，每次都重下，反而更慢
//
// 结论：越花哨越容易出问题。最简单的最稳：
//   - 用户明确点击按钮之后，才插一个最朴素的 <script async src=opencv.js>
//   - 不做任何预加载、预热、prefetch、iframe、fetch
//   - script.onload 后每 100ms 看一眼 cv.Mat 是否可用，轮 300 次（30s）足够 WASM 编译完
//   - 脚本标签只插一次；重复点击复用结果；卸载/重试时清理干净
//   - 全程 try/catch，任何异常都只 fail 这个组件，绝不抛出中断 Vue 水合
//
// 状态机：idle → loading → initializing → ready / error

// @ts-ignore
const BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.BASE_URL) || '/'
const CV_URL = BASE.replace(/\/$/, '') + '/lib/opencv.js'

let cvPromise = null
let cvInstance = null
let scriptEl = null

function remove(el) {
  if (el && el.parentNode) {
    try { el.parentNode.removeChild(el) } catch (_) {}
  }
}

function cleanup() {
  remove(scriptEl); scriptEl = null
  if (typeof window !== 'undefined' && window.cv) {
    try { window.cv.onRuntimeInitialized = null } catch (_) {}
  }
}

/**
 * 加载 OpenCV.js
 * @param {Object} opts
 * @param {(stage:string)=>void} [opts.onStage] 阶段回调：loading | initializing | ready | error
 * @param {boolean} [opts.force] 强制重新加载（重试时用）
 */
export function loadOpenCV(opts = {}) {
  // 1. 已经就绪：直接返回
  if (cvInstance && typeof cvInstance.Mat === 'function') {
    try { opts.onStage && opts.onStage('ready') } catch (_) {}
    return Promise.resolve(cvInstance)
  }
  // 2. 已经在加载中：复用同一个 promise，不重复发请求
  if (cvPromise && !opts.force) return cvPromise
  if (opts.force) { cleanup(); cvPromise = null; cvInstance = null }

  // SSR 保护：服务端绝不可能执行到这里，但万一调用了直接拒掉
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return Promise.reject(new Error('OpenCV.js 只能在浏览器中加载'))
  }

  cvPromise = new Promise((resolve, reject) => {
    let settled = false
    let pollTimer = null
    let timeoutTimer = null

    const setStage = (s) => {
      try { opts.onStage && opts.onStage(s) } catch (_) {}
    }

    const done = (cv) => {
      if (settled) return
      settled = true
      if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
      if (timeoutTimer) { clearTimeout(timeoutTimer); timeoutTimer = null }
      cvInstance = cv
      resolve(cv)
    }

    const fail = (err) => {
      if (settled) return
      settled = true
      if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
      if (timeoutTimer) { clearTimeout(timeoutTimer); timeoutTimer = null }
      cleanup()
      cvPromise = null
      setStage('error')
      reject(err)
    }

    // ---- WASM 就绪检测 ----
    // 不依赖单一的 onRuntimeInitialized（缓存命中时它可能已经被触发过）：
    // script.onload 之后，每 100ms 看一眼 cv.Mat 是否可用，最多等 30 秒。
    const startPolling = () => {
      setStage('initializing')
      let tries = 0
      pollTimer = setInterval(() => {
        tries++
        try {
          if (window.cv && typeof window.cv.Mat === 'function') {
            setStage('ready'); done(window.cv); return
          }
        } catch (_) {}
        if (tries > 300) { // 30 秒还没好，判定失败
          fail(new Error('WebAssembly 编译超时（超过 30 秒）。建议刷新页面重试，或检查浏览器是否禁用了 WebAssembly。'))
        }
      }, 100)
    }

    // ---- 兜底超时：下载 + 编译总共 60 秒，再超就算失败 ----
    timeoutTimer = setTimeout(() => {
      fail(new Error('OpenCV.js 加载超时（超过 60 秒）。\n' +
        '可能原因：①到 GitHub Pages 链路较慢；②浏览器同时下载了太多资源。\n' +
        '建议：点「🔗 直链预热」在新标签页单独打开一次 opencv.js（看到代码即可关闭），回本页点「重新加载」——此时文件已在浏览器缓存，秒加载。'))
    }, 60000)

    // ---- 关键：预置 onRuntimeInitialized 钩子（必须在 appendChild 之前） ----
    // 首次加载（非缓存命中）时，WASM 编译完会调这个；我们同时也在轮询，双保险。
    if (!window.cv || typeof window.cv !== 'object') window.cv = {}
    window.cv.onRuntimeInitialized = function () {
      // 轮询会自己发现 Mat 可用，这里不直接 done，避免重复
    }

    // ---- 插入 <script> 元素 ----
    setStage('loading')
    scriptEl = document.createElement('script')
    scriptEl.src = CV_URL
    scriptEl.async = true
    scriptEl.dataset.cvScript = '1'
    // 不设 crossOrigin：和页面同源，无需 CORS
    // 不设 defer：async 足够，不阻塞 HTML 解析

    scriptEl.onload = () => {
      // script 下载+JS 解析完 → 开始等 WASM
      // 命中强缓存时 onload 瞬间触发，此时 WASM 可能已同步编译完
      try {
        if (window.cv && typeof window.cv.Mat === 'function') {
          setStage('ready'); done(window.cv); return
        }
      } catch (_) {}
      startPolling()
    }
    scriptEl.onerror = (e) => {
      fail(new Error('OpenCV.js 脚本下载失败。\n' +
        '请检查网络是否能访问 yejinlei.github.io；也可点「🔗 直链预热」在新标签页单独打开一次，再回本页重试。'))
    }

    try {
      document.head.appendChild(scriptEl)
    } catch (err) {
      fail(new Error('无法插入 script 标签：' + (err && err.message ? err.message : err)))
    }
  })

  // 返回的 promise 被外部 catch 后不要把 cvPromise 清掉（避免并发调用问题）；
  // 只有真正 fail 时才在 fail() 内部清 cvPromise
  return cvPromise.catch(err => { throw err })
}

export function isCVReady() {
  try { return !!(cvInstance && typeof cvInstance.Mat === 'function') } catch (_) { return false }
}
export function getCVIfReady() { return isCVReady() ? cvInstance : null }
export function getCVUrl() { return CV_URL }
export function openCVUrl() {
  if (typeof window !== 'undefined') window.open(CV_URL, '_blank', 'noopener')
}
export function resetCV() {
  cleanup()
  cvPromise = null
  cvInstance = null
}

// 兼容老代码的空实现（调用 warmupOpenCV 什么都不做，避免未定义报错）
export function warmupOpenCV() {}
