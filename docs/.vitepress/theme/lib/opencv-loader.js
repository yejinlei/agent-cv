/**
 * OpenCV.js 加载器 —— 最终可靠版
 *
 * 方案：fetch + 进度事件 + Blob URL + 全局单例
 *
 * 为什么不再用 <script src=...>：
 *   - script async 标签在浏览器里的请求优先级/调度受同页其他 defer 脚本影响，
 *     GitHub Pages 海外链路下容易在队列里 pending 很久。
 *   - fetch 可以直接拿到 progress 事件，显示真实下载进度；同时命中 HTTP 缓存
 *     时会直接 resolve（几毫秒），不会阻塞别的资源。
 *
 * onRuntimeInitialized 时序：
 *   - 拿到代码后通过 Blob URL 执行，在 appendChild(script) 之前就把 window.cv = {}
 *     和 onRuntimeInitialized 钩子挂好，factory() 里 var Module = ... 合并到钩子，
 *     不管 wasm 在 onload 之前还是之后就绪都不会丢信号。
 */

const CV_URL = '/agent-cv/lib/opencv.js'

let cvPromise = null
let cvState = 'idle' // 'idle' | 'downloading' | 'initializing' | 'ready' | 'error'
let cvError = null
let cvModule = null
const listeners = new Set()

function notify(progress) {
  listeners.forEach((fn) => {
    try { fn(cvState, cvModule, cvError, progress) } catch (_) {}
  })
}

function setCvState(next, err, progress) {
  cvState = next
  if (err) cvError = err
  notify(progress)
}

export function getCvState() {
  return { state: cvState, error: cvError, module: cvModule }
}

export function subscribeCv(fn) {
  listeners.add(fn)
  // 立即推一次当前状态
  fn(cvState, cvModule, cvError, null)
  return () => listeners.delete(fn)
}

export function resetOpenCVForRetry() {
  cvPromise = null
  cvState = 'idle'
  cvError = null
  cvModule = null
  // 清理可能注入的 blob script
  document.querySelectorAll('script[data-cv-blob]').forEach((s) => {
    if (s.src && s.src.startsWith('blob:')) URL.revokeObjectURL(s.src)
    s.remove()
  })
  try { delete window.cv } catch (_) { window.cv = undefined }
  notify(null)
}

export function loadOpenCV() {
  if (cvPromise) return cvPromise
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('not in browser'))
  }
  // 已经就绪
  if (cvModule && cvModule.Mat) {
    setCvState('ready')
    return Promise.resolve(cvModule)
  }
  if (window.cv && window.cv.Mat && !cvModule) {
    cvModule = window.cv
    setCvState('ready')
    return Promise.resolve(cvModule)
  }

  cvPromise = (async () => {
    setCvState('downloading')

    // —— 1. fetch 下载（带真实进度）——
    let resp
    try {
      resp = await fetch(CV_URL, { cache: 'force-cache' })
    } catch (e) {
      // 网络错误（DNS/断网/CORS）
      throw new Error('网络请求失败：' + (e.message || String(e)))
    }
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}：下载 OpenCV.js 失败，请检查网络或稍后重试`)
    }

    const totalLen = Number(resp.headers.get('content-length')) || 11534336 // 兜底 11MB
    const reader = resp.body && resp.body.getReader ? resp.body.getReader() : null
    let received = 0
    let chunks = []

    if (reader) {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        chunks.push(value)
        received += value.length
        setCvState('downloading', null, {
          loaded: received,
          total: totalLen,
          percent: totalLen > 0 ? Math.min(99, Math.round((received / totalLen) * 100)) : -1,
          stage: 'downloading',
        })
      }
    } else {
      // 浏览器不支持 stream（极少数情况），直接 arrayBuffer
      const buf = await resp.arrayBuffer()
      chunks = [new Uint8Array(buf)]
      received = buf.byteLength
    }

    // —— 2. 拼源码 → Blob URL ——
    const allBytes = new Uint8Array(received)
    let off = 0
    for (const c of chunks) { allBytes.set(c, off); off += c.length }
    const blob = new Blob([allBytes], { type: 'application/javascript' })
    const blobUrl = URL.createObjectURL(blob)

    setCvState('initializing')
    setCvState('initializing', null, { loaded: received, total: received, percent: 100, stage: 'initializing' })

    // —— 3. 挂好钩子再注入 script ——
    // 预置占位 cv，保证 factory() 里 var Module = typeof cv !== 'undefined' ? cv : {} 拿到我们的钩子
    if (!window.cv || window.cv.Mat === undefined) {
      window.cv = window.cv || {}
    }
    let settled = false
    let hookFired = false
    const prevHook = window.cv.onRuntimeInitialized
    const ready = new Promise((resolve, reject) => {
      window.cv.onRuntimeInitialized = () => {
        hookFired = true
        if (typeof prevHook === 'function') {
          try { prevHook() } catch (_) {}
        }
        if (settled) return
        settled = true
        resolve(window.cv)
      }
      // 60 秒初始化超时（WASM 编译一般 <10s）
      setTimeout(() => {
        if (!settled) {
          settled = true
          reject(new Error('WASM 初始化超时（60 秒），可能是浏览器不支持 WebAssembly 或资源不足'))
        }
      }, 60000)
    })

    await new Promise((resolve, reject) => {
      const s = document.createElement('script')
      s.src = blobUrl
      s.dataset.cvBlob = '1'
      s.async = true
      s.onload = () => {
        // onload 触发时脚本同步执行完，但 wasm 可能还在异步编译
        // 路径 1：钩子已经在 onload 前触发（data: wasm 内嵌，极快编译）
        if (hookFired) { resolve(); return }
        // 路径 2：cv.Mat 已经存在但钩子没触发（异常）
        if (window.cv && window.cv.Mat) {
          if (!settled) { settled = true; resolve(window.cv) }
          resolve(); return
        }
        // 路径 3：钩子被覆盖了，重新挂
        const prev2 = window.cv.onRuntimeInitialized
        window.cv.onRuntimeInitialized = () => {
          if (typeof prev2 === 'function' && prev2 !== window.cv.onRuntimeInitialized) {
            try { prev2() } catch (_) {}
          }
          if (!settled) { settled = true; resolve(window.cv) }
        }
        resolve()
      }
      s.onerror = (e) => {
        reject(new Error('脚本执行失败：' + (e.message || e.error || String(e))))
      }
      document.head.appendChild(s)
    })

    const cv = await ready
    cvModule = cv
    setCvState('ready')
    return cv
  })().catch((e) => {
    cvPromise = null // 允许重试
    setCvState('error', e)
    throw e
  })

  return cvPromise
}
