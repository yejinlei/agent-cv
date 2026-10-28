// OpenCV.js 加载器：最朴素的 script 标签方案
// 为什么改回 script 标签？
//   1. 直接利用浏览器原生的 gzip / HTTP 缓存 / 304 协商，下载字节最少（3.5MB gzip vs 11MB raw）
//   2. 避免 fetch+Blob 绕开缓存、XHR 不透明响应、流式读取进度抖动等一系列复杂问题
//   3. 通过 performance.getEntriesByName 拿到真实字节进度；
//      没拿到就显示 "已开始下载…"，不伪造进度数字。
//   4. 在 script 插入 document.head **之前**就预置 window.cv.onRuntimeInitialized，
//      避免 WASM base64 dataURI 极快就绪时回调被错过。
//
// 回调状态：
//   onStage('loading')  -> 开始插入 script，准备下载
//   onStage('script-loaded') -> script onload 触发（脚本同步部分执行完，cv 对象已创建，WASM 可能还在编译）
//   onStage('ready')    -> WASM 初始化完成，cv.Mat 等 API 可用
//   onProgress({loaded, total})  -> 下载字节（尽力而为，取不到 total 时 total=0）
//   onError(err)        -> 失败

const CV_URL = '/agent-cv/lib/opencv.js'

let cvPromise = null
let cvInstance = null
let scriptEl = null
let progressTimer = null

function attachProgressProbe (onProgress) {
  let lastLoaded = -1
  const tick = () => {
    try {
      const entries = performance.getEntriesByName(CV_URL)
      if (entries && entries.length) {
        const e = entries[entries.length - 1]
        if (e.transferSize > 0 || e.decodedBodySize > 0 || e.encodedBodySize > 0) {
          const loaded = e.transferSize || e.encodedBodySize || e.decodedBodySize
          // 粗略估算：实际大小 10.5MB（磁盘），gzip 后 ~3.5MB
          // 拿不到服务器 Content-Length 时给用户一个合理的进度感知
          const roughTotal = 3.5 * 1024 * 1024
          if (loaded !== lastLoaded) {
            lastLoaded = loaded
            onProgress && onProgress({
              loaded,
              // 如果资源传输大小已经超过粗略值（意味着走的是未压缩 / 缓存命中），
              // 就以 loaded 为 total，避免进度条跑到顶不动
              total: Math.max(roughTotal, loaded),
            })
          }
        }
      }
    } catch (_) {}
  }
  progressTimer = setInterval(tick, 200)
  tick()
}

function stopProgressProbe () {
  if (progressTimer) { clearInterval(progressTimer); progressTimer = null }
}

function createLoadPromise ({ onProgress, onStage, onError, signal } = {}) {
  return new Promise((resolve, reject) => {
    if (cvInstance && typeof cvInstance.Mat === 'function') {
      onStage && onStage('ready')
      resolve(cvInstance)
      return
    }
    if (cvPromise) {
      cvPromise.then(resolve, reject)
      return
    }

    let settled = false
    let pollId = null
    let timeoutId = null

    const cleanup = () => {
      stopProgressProbe()
      if (timeoutId) { clearTimeout(timeoutId); timeoutId = null }
      if (pollId) { clearInterval(pollId); pollId = null }
    }

    const done = (cv) => {
      if (settled) return
      settled = true
      cleanup()
      cvInstance = cv
      resolve(cv)
    }

    const fail = (err) => {
      if (settled) return
      settled = true
      cleanup()
      // 失败时清理：移除 script、重置状态，下次重试可以重新开始
      if (scriptEl && scriptEl.parentNode) scriptEl.parentNode.removeChild(scriptEl)
      scriptEl = null
      cvPromise = null
      if (window.cv) {
        try { delete window.cv.onRuntimeInitialized } catch (_) { window.cv.onRuntimeInitialized = undefined }
      }
      onError && onError(err)
      reject(err)
    }

    // 超时 5 分钟
    timeoutId = setTimeout(() => {
      fail(new Error('OpenCV.js 加载超时（5 分钟）。GitHub Pages 为海外服务器，国内访问可能较慢，可刷新重试或切换网络。'))
    }, 5 * 60 * 1000)

    if (signal) {
      if (signal.aborted) { fail(new DOMException('aborted','AbortError')); return }
      signal.addEventListener('abort', () => fail(new DOMException('aborted','AbortError')), { once: true })
    }

    // 准备：先把 onRuntimeInitialized 挂到 window.cv 上
    onStage && onStage('loading')
    if (!window.cv || typeof window.cv !== 'object') {
      window.cv = {}
    }

    const waitMatReady = () => {
      // onRuntimeInitialized 回调到了，但再等几帧让所有类挂到 cv 上
      const check = (tries) => {
        if (settled) return
        if (window.cv && typeof window.cv.Mat === 'function') {
          onStage && onStage('ready')
          done(window.cv)
          return
        }
        if (tries > 200) { // 20 秒兜底
          fail(new Error('WebAssembly 初始化完成但 cv.Mat 缺失，请刷新重试。'))
          return
        }
        setTimeout(() => check(tries + 1), 50)
      }
      check(0)
    }

    window.cv.onRuntimeInitialized = function () { waitMatReady() }

    // 探测进度
    attachProgressProbe(onProgress)

    // 创建 script
    scriptEl = document.createElement('script')
    scriptEl.src = CV_URL
    scriptEl.async = true
    scriptEl.dataset.cvScript = '1'

    scriptEl.onload = () => {
      onStage && onStage('script-loaded')
      // onload 时脚本同步部分已执行完；如果 WASM 已经就绪（缓存命中/极快），cv.Mat 已经存在
      if (window.cv && typeof window.cv.Mat === 'function') {
        onStage && onStage('ready')
        done(window.cv)
        return
      }
      // 否则等 onRuntimeInitialized；但为防万一，启动兜底轮询
      let tries = 0
      pollId = setInterval(() => {
        tries++
        if (settled) { clearInterval(pollId); return }
        if (window.cv && typeof window.cv.Mat === 'function') {
          clearInterval(pollId)
          onStage && onStage('ready')
          done(window.cv)
        } else if (tries > 600) { // 60 秒兜底（WASM 初始化一般 3-10 秒）
          clearInterval(pollId)
          fail(new Error('OpenCV.js 脚本已加载，但 WebAssembly 初始化超时，请刷新重试。'))
        }
      }, 100)
    }

    scriptEl.onerror = (e) => {
      fail(new Error('OpenCV.js 脚本下载/执行失败（网络错误）。请检查网络或稍后重试。'))
    }

    document.head.appendChild(scriptEl)
  })
}

export function loadOpenCV (opts = {}) {
  if (!cvPromise || (opts.force === true)) {
    if (opts.force === true) {
      cvPromise = null
      cvInstance = null
      if (scriptEl && scriptEl.parentNode) scriptEl.parentNode.removeChild(scriptEl)
      scriptEl = null
    }
    cvPromise = createLoadPromise(opts).catch(err => {
      cvPromise = null
      throw err
    })
  }
  return cvPromise
}

export function isCVReady () {
  return !!(cvInstance && typeof cvInstance.Mat === 'function')
}

export function getCVIfReady () {
  return isCVReady() ? cvInstance : null
}

export function resetCV () {
  stopProgressProbe()
  cvPromise = null
  cvInstance = null
  if (scriptEl && scriptEl.parentNode) scriptEl.parentNode.removeChild(scriptEl)
  scriptEl = null
  if (window.cv) {
    try { delete window.cv.onRuntimeInitialized } catch (_) { window.cv.onRuntimeInitialized = undefined }
  }
}
