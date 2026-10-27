/**
 * 最可靠的 OpenCV.js 加载器（最终版）
 *
 * 关键时序理解（踩过多次坑后的结论）：
 *
 * opencv.js 是一个 UMD 包，顶层执行：
 *     root.cv = factory()
 * factory() 内部：
 *     1. 同步初始化一堆变量；
 *     2. 读 wasmBinaryFile（此构建中是 data:application/octet-stream;base64,... 内嵌）；
 *     3. 异步编译 WebAssembly；
 *     4. 编译完成后调用 Module['onRuntimeInitialized']()（如果存在）；
 *     5. 同步 return Module；
 *
 * 问题：如果我们在 <script> 的 onload 里才去设置 cv.onRuntimeInitialized = callback，
 * 因为 wasm 是内嵌 base64，极大概率在 onload 触发前就已经编译完并同步调过
 * onRuntimeInitialized() 了——此时我们挂的 callback 永远不会被触发，界面就会一直死转。
 *
 * 正确做法：在 appendChild(script) **之前**，就预先在 window 上放一个带
 * onRuntimeInitialized 钩子的占位 cv 对象。factory() 启动时 var Module =
 * typeof cv !== "undefined" ? cv : {} 会合并已有的 cv，wasm 就绪时就会调用我们的钩子。
 *
 * 同时仍然在 onload 里做一次 cv.Mat 兜底检查（处理 wasm 还没编译完、需要等回调的慢场景，
 * 或 script 来自 prefetch 已缓存的情况）。
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

  // 已经就绪
  if (window.cv && window.cv.Mat) {
    setCvState('ready')
    return Promise.resolve(window.cv)
  }

  cvPromise = new Promise((resolve, reject) => {
    setCvState('loading')

    let settled = false
    const timeoutMs = 180000 // 3 分钟
    const timer = setTimeout(() => {
      if (settled) return
      settled = true
      const err = new Error('OpenCV.js 加载超时（3 分钟）。GitHub Pages 在国内访问较慢，请检查网络后重试。')
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
      const msg = e && e.message ? e.message : String(e)
      const err = new Error('OpenCV.js 加载失败：' + msg)
      setCvState('error', err)
      reject(err)
    }

    // —— 关键修复：在注入 <script> 之前，预置占位 cv 对象并挂好 onRuntimeInitialized ——
    // 这样 factory() 内 var Module = typeof cv !== "undefined" ? cv : {} 会拿到我们的钩子，
    // wasm 编译完后会同步调用 Module['onRuntimeInitialized']()，
    // 不论这个调用在脚本 onload 之前还是之后，我们都能拿到信号。
    if (!window.cv) {
      window.cv = {}
    }
    // 如果上一次已经有 onRuntimeInitialized（不可能，但保稳健），保留链式调用
    const prevHook = window.cv.onRuntimeInitialized
    let hookFired = false
    window.cv.onRuntimeInitialized = () => {
      hookFired = true
      if (typeof prevHook === 'function') {
        try { prevHook() } catch (_) {}
      }
      done()
    }

    // 检查是不是已经有同 URL 的 script 在页面上（VitePress 预加载/其他组件先注入）
    const existing = document.querySelector(`script[data-cv-loader="1"][src="${CV_URL}"]`)
    if (existing) {
      if (existing.loaded || hookFired) {
        // 脚本已经执行过——如果钩子没触发、但 cv.Mat 已经存在，直接 done
        if (window.cv && window.cv.Mat) done()
        // 否则说明 wasm 还在编译，等我们已经挂好的 onRuntimeInitialized 触发即可
      } else {
        existing.addEventListener('load', () => {
          existing.loaded = true
          // onload 兜底：如果 wasm 在 onload 之后才好，我们的钩子会被调；
          // 如果钩子已经被调（hookFired=true），done() 里 settled 检查会直接 return。
          // 如果因为某种原因钩子没被挂/被覆盖，轮询几次兜底。
          if (hookFired) return
          if (window.cv && window.cv.Mat) { done(); return }
          // 极端情况：重新挂钩
          const prev2 = window.cv.onRuntimeInitialized
          window.cv.onRuntimeInitialized = () => {
            if (typeof prev2 === 'function') { try { prev2() } catch (_) {} }
            done()
          }
          // 再给一次即时检查
          if (window.cv && window.cv.Mat) done()
        }, { once: true })
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
        // 脚本执行完毕后 window.cv 已经是 factory 返回的 Module（我们预置的 onRuntimeInitialized 已合并进去）
        if (!window.cv) {
          fail(new Error('脚本执行后 window.cv 未定义'))
          return
        }
        // 路径 1：wasm 在 onload 前就已经好了 → 我们的 onRuntimeInitialized 钩子已经触发（hookFired=true）
        if (hookFired) return
        // 路径 2：cv.Mat 已经存在但钩子没触发（异常情况）→ 直接 done
        if (window.cv.Mat) { done(); return }
        // 路径 3：wasm 还没好，且钩子在脚本执行过程中被覆盖了 → 重新挂
        const prev2 = window.cv.onRuntimeInitialized
        // 如果 prev2 已经是我们的函数（window.cv 被保留），不用重复挂
        if (prev2 !== window.cv.onRuntimeInitialized_backup) {
          window.cv.onRuntimeInitialized = () => {
            if (typeof prev2 === 'function' && prev2 !== window.cv.onRuntimeInitialized) {
              try { prev2() } catch (_) {}
            }
            done()
          }
        }
        // 最后做一次即时检查（处理"检查完瞬间就绪"的竞态）
        if (window.cv.Mat) done()
      } catch (e) {
        fail(e)
      }
    }
    script.onerror = fail
    document.head.appendChild(script)
  })

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
