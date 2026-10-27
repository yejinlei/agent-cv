/**
 * 最简、最可靠的 OpenCV.js 加载器
 *
 * 正确模型（针对 opencv.js 官方单文件构建）：
 * 1. 用普通 <script> 标签加载，script.onload 表示脚本已同步执行完毕，window.cv 对象已存在；
 * 2. 但 cv.Mat 等 API 要等 wasm 编译完成后才可用，就绪信号是 cv.onRuntimeInitialized 回调；
 * 3. 要处理"挂回调时 cv 已经就绪"的竞态：挂完回调后立即再检查一次 cv.Mat。
 *
 * 不使用 XHR/Blob/fetch/eval，不做轮询，不用 import()，不 await window.cv（cv 不是 Promise）。
 */

const CV_URL = '/agent-cv/lib/opencv.js'

let cvPromise = null
let cvState = 'idle' // 'idle' | 'loading' | 'ready' | 'error'
let cvError = null
const listeners = new Set()

function notify() {
  listeners.forEach((fn) => {
    try { fn(cvState, window.cv, cvError) } catch (_) {}
  })
}

function setCvState(next, err) {
  cvState = next
  if (err) cvError = err
  notify()
}

export function getCvState() {
  return { state: cvState, error: cvError }
}

export function subscribeCv(fn) {
  listeners.add(fn)
  fn(cvState, window.cv, cvError)
  return () => listeners.delete(fn)
}

export function loadOpenCV() {
  if (cvPromise) return cvPromise
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('not in browser'))
  }

  cvPromise = new Promise((resolve, reject) => {
    // 已经加载过
    if (window.cv && window.cv.Mat) {
      setCvState('ready')
      resolve(window.cv)
      return
    }

    setCvState('loading')

    let settled = false
    const timeoutMs = 180000 // 3 分钟（国内 GitHub Pages 慢网络保底）
    const timer = setTimeout(() => {
      if (settled) return
      settled = true
      const err = new Error('OpenCV.js 加载超时（3 分钟）。网络较慢时请耐心等待，或检查网络。')
      setCvState('error', err)
      reject(err)
    }, timeoutMs)

    const done = () => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      setCvState('ready')
      resolve(window.cv)
    }
    const fail = (e) => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      const err = new Error('OpenCV.js 脚本加载失败：' + (e && e.message ? e.message : String(e)))
      setCvState('error', err)
      reject(err)
    }

    // 已经有一个 <script> 被之前的页面注入但未就绪
    const existing = document.querySelector(`script[data-cv-loader="1"]`)
    if (existing) {
      // 复用现有 script，重新挂回调
      const hookCv = () => {
        if (!window.cv) { fail(new Error('cv 对象未出现')); return }
        if (window.cv.Mat) { done(); return }
        const prev = window.cv.onRuntimeInitialized
        window.cv.onRuntimeInitialized = () => {
          if (typeof prev === 'function') { try { prev() } catch (_) {} }
          done()
        }
      }
      if (existing.loaded) {
        hookCv()
      } else {
        existing.addEventListener('load', hookCv, { once: true })
        existing.addEventListener('error', fail, { once: true })
      }
      return
    }

    const script = document.createElement('script')
    script.src = CV_URL
    script.async = true
    script.dataset.cvLoader = '1'
    script.onload = () => {
      script.loaded = true
      try {
        if (!window.cv) { fail(new Error('脚本执行后 window.cv 未定义')); return }
        if (window.cv.Mat) { done(); return }
        // 挂 onRuntimeInitialized —— 这是官方就绪信号
        const prev = window.cv.onRuntimeInitialized
        window.cv.onRuntimeInitialized = () => {
          if (typeof prev === 'function') { try { prev() } catch (_) {} }
          done()
        }
        // 兜底：挂完回调后再检查一次，避免在 onload 和挂钩之间 wasm 已就绪导致错过回调
        if (window.cv.Mat) done()
      } catch (e) {
        fail(e)
      }
    }
    script.onerror = fail
    document.head.appendChild(script)
  })

  // 出错时允许重试（重置 promise）
  cvPromise.catch(() => {
    cvPromise = null
  })

  return cvPromise
}

export function resetOpenCVForRetry() {
  cvPromise = null
  cvState = 'idle'
  cvError = null
  const s = document.querySelector(`script[data-cv-loader="1"]`)
  if (s && s.parentNode) s.parentNode.removeChild(s)
  delete window.cv
  notify()
}
