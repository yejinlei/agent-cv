// OpenCV.js 加载器：fetch + Blob URL 方案
// - 能拿到真实下载进度（字节数）；
// - 在注入 Blob script 之前就在 window.cv 上预置 onRuntimeInitialized 钩子，
//   避免 data-URI WASM 编译极快导致回调被错过；
// - 全局单例，多实例共享下载；
// - 失败会清理资源，支持重试。

const CV_URL = '/agent-cv/lib/opencv.js'

// 全局单例状态
let cvPromise = null
let cvInstance = null

function createLoadPromise ({ onProgress, onStage, onError, signal } = {}) {
  return new Promise((resolve, reject) => {
    // 情况 1：已经加载成功过
    if (cvInstance && typeof cvInstance.Mat === 'function') {
      onStage && onStage('ready')
      resolve(cvInstance)
      return
    }

    // 情况 2：正在加载中（另一个实例发起的），复用它的 Promise
    if (cvPromise) {
      cvPromise.then(resolve, reject)
      return
    }

    // 清理之前可能存在的脚本标签
    document.querySelectorAll('script[data-cv-script]').forEach(s => s.remove())

    let settled = false
    let blobUrl = null
    let timeoutId = null
    let pollId = null

    function done (cv) {
      if (settled) return
      settled = true
      clearTimeout(timeoutId)
      if (pollId) clearInterval(pollId)
      cvInstance = cv
      resolve(cv)
      // 释放 Blob URL 占的内存（cv 已执行完，可以 revoke）
      if (blobUrl) {
        // 延迟 revoke，避免脚本还在异步初始化时被回收
        setTimeout(() => {
          try { URL.revokeObjectURL(blobUrl) } catch (_) {}
          blobUrl = null
        }, 5000)
      }
    }

    function fail (err) {
      if (settled) return
      settled = true
      clearTimeout(timeoutId)
      if (pollId) clearInterval(pollId)
      if (blobUrl) {
        try { URL.revokeObjectURL(blobUrl) } catch (_) {}
        blobUrl = null
      }
      cvPromise = null
      document.querySelectorAll('script[data-cv-script]').forEach(s => s.remove())
      // 保留 window.cv 对象但重置 Promise
      onError && onError(err)
      reject(err)
    }

    // 超时：5 分钟（GitHub Pages 海外下载慢）
    timeoutId = setTimeout(() => {
      fail(new Error('OpenCV.js 加载超时（5 分钟）。请检查网络或切换网络后重试。'))
    }, 5 * 60 * 1000)

    // AbortSignal 支持（组件卸载时可中断）
    if (signal) {
      if (signal.aborted) {
        fail(new DOMException('aborted', 'AbortError'))
        return
      }
      signal.addEventListener('abort', () => {
        fail(new DOMException('aborted', 'AbortError'))
      }, { once: true })
    }

    // 阶段 1：下载
    onStage && onStage('downloading')

    // 先在 window.cv 上预置钩子，等下 Blob script 执行时 factory 会合并它
    // （这一步必须在 createObjectURL+appendChild 之前做）
    if (!window.cv || typeof window.cv !== 'object') {
      window.cv = {}
    }
    let runtimeCb = null
    window.cv.onRuntimeInitialized = function () {
      runtimeCb && runtimeCb()
    }

    fetch(CV_URL, {
      cache: 'force-cache', // 优先用 HTTP 缓存
      credentials: 'same-origin',
    }).then(res => {
      if (!res.ok) {
        throw new Error(`下载 OpenCV.js 失败：HTTP ${res.status}`)
      }
      if (!res.body) {
        throw new Error('浏览器不支持流式读取（ReadableStream）')
      }

      // 真实总字节数（Content-Length）；如果服务器未返回，给 null 让 UI 显示不确定进度
      const totalBytes = res.headers.get('content-length')
        ? parseInt(res.headers.get('content-length'), 10)
        : null
      let loadedBytes = 0

      const reader = res.body.getReader()
      const chunks = []

      function pump () {
        if (settled) return
        return reader.read().then(({ done, value }) => {
          if (settled) return
          if (done) {
            // 下载完成
            const blob = new Blob(chunks, { type: 'application/javascript' })
            blobUrl = URL.createObjectURL(blob)
            onProgress && onProgress({ loaded: loadedBytes, total: totalBytes, done: true })
            onStage && onStage('initializing')
            injectScript(blobUrl)
            return
          }
          chunks.push(value)
          loadedBytes += value.length
          onProgress && onProgress({ loaded: loadedBytes, total: totalBytes, done: false })
          return pump()
        }).catch(err => {
          fail(new Error(`下载中断：${err.message || err}`))
        })
      }
      return pump()
    }).catch(err => {
      if (settled) return
      fail(err)
    })

    // 阶段 2：注入 Blob script，等待 WASM 就绪
    function injectScript (url) {
      // window.cv 上已经预置了 onRuntimeInitialized，Blob 脚本执行时 factory 会用它
      const prevCb = window.cv.onRuntimeInitialized
      window.cv.onRuntimeInitialized = function () {
        // 再等几帧让所有类（Mat, MatVector, Size, Rect 等）都挂到 cv 上
        setTimeout(() => {
          if (settled) return
          if (window.cv && typeof window.cv.Mat === 'function') {
            onStage && onStage('ready')
            done(window.cv)
          } else {
            // 兜底轮询
            let tries = 0
            pollId = setInterval(() => {
              tries++
              if (settled) { clearInterval(pollId); return }
              if (window.cv && typeof window.cv.Mat === 'function') {
                clearInterval(pollId)
                onStage && onStage('ready')
                done(window.cv)
              } else if (tries > 200) { // 20 秒轮询上限
                clearInterval(pollId)
                fail(new Error('WebAssembly 初始化完成但 Mat 未定义，请刷新重试'))
              }
            }, 100)
          }
        }, 100)
        prevCb && prevCb.call(this)
      }

      const script = document.createElement('script')
      script.src = url
      script.async = true
      script.dataset.cvScript = '1'

      script.onload = function () {
        // onload 只表示脚本同步执行完，不代表 WASM 已初始化
        // （WASM 是异步的，初始化完成会走 onRuntimeInitialized）
        // 如果 onload 时 Mat 已经就绪（极小文件/缓存命中场景），直接 done
        if (window.cv && typeof window.cv.Mat === 'function' && !settled) {
          onStage && onStage('ready')
          done(window.cv)
        }
      }

      script.onerror = function () {
        fail(new Error('OpenCV.js 脚本执行失败，请刷新重试'))
      }

      document.head.appendChild(script)
    }
  })
}

export function loadOpenCV (opts = {}) {
  if (!cvPromise || (opts.force === true)) {
    if (opts.force === true) {
      cvPromise = null
      cvInstance = null
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

// 手动重置（调试/切换页面用）
export function resetCV () {
  cvPromise = null
  cvInstance = null
  document.querySelectorAll('script[data-cv-script]').forEach(s => s.remove())
}
