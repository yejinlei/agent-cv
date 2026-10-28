import DefaultTheme from 'vitepress/theme-without-fonts'
import { h } from 'vue'
import type { Theme } from 'vitepress'

import './custom.css'
import FamilyTree from './components/FamilyTree.vue'
import MermaidGlobal from './components/MermaidGlobal.vue'
import AlgorithmCard from './components/AlgorithmCard.vue'
import OpencvPlayground from './components/OpencvPlayground.vue'
import MathVisualizer from './components/MathVisualizer.vue'
import ConvDemo from './components/ConvDemo.vue'
import AlgoVisualizer from './components/AlgoVisualizer.vue'

// 🔒 在客户端启动时就把 VitePress 的视口预取关掉，并主动清理 DOM 里所有 <link rel="prefetch">。
// 原因：VitePress 默认对出现在视口里的所有链接发 prefetch，国内访问 GitHub Pages 的链路下，
// 这会把浏览器到 github.io 的 6 个并发连接全占满（十几个章节分块同时下载），导致真正需要的
// 10MB OpenCV.js 在队列里排队 3 分钟超时。我们用 MutationObserver 从根上阻止：
//  1) 监听 document.head，任何新增的 rel=prefetch 立即移除；
//  2) 把 VitePress 内部的 `__vitepress__`/router.preload 置空；
//  3) 拦截所有对 <link rel=prefetch> 的创建。
// 注意：不能在 config.mts 顶层写 prefetch:false——该字段在部分 VitePress 版本下会导致客户端
// 启动白屏/水合错误，因此用这种运行时方式禁用更稳。
if (typeof window !== 'undefined') {
  try {
    // 1) 清理已存在的 prefetch / preload（所有——我们完全接管 OpenCV.js 的加载时机，不允许任何自动预取）
    const removeExisting = () => {
      document.querySelectorAll('link[rel="prefetch"], link[rel="preload"], link[rel="modulepreload"]').forEach((el) => {
        const href = el.getAttribute('href') || ''
        // 只移除会导致后台下载 opencv.js 的 prefetch/preload；
        // Playground 里自己创建的 Blob script 不带 rel，不受影响。
        if (href.includes('opencv.js')) {
          el.remove()
        }
      })
      // 同时清理任何已被自动注入的 opencv.js <script> 标签：
      //   - 只有 data-cv-blob="1" 是我们自己注入的（Blob URL 形式），其余一律删除
      document.querySelectorAll('script[src*="opencv.js"]').forEach((s) => {
        if (s.dataset && s.dataset.cvBlob === '1') return
        // 如果 cv 还没好（即不是用户主动点击启动的），删掉这个自动注入的 script
        if (!(window.cv && (window.cv).Mat)) {
          s.remove()
        }
      })
    }
    removeExisting()

    // 2) 监听后续动态插入的 link/script，立即移除任何想自动加载 opencv.js 的企图
    const mo = new MutationObserver((muts) => {
      for (const m of muts) {
        m.addedNodes.forEach((n) => {
          if (n.nodeType !== 1) return
          const el = n as HTMLElement
          if (el.tagName === 'LINK') {
            const link = el as HTMLLinkElement
            const rel = (link.getAttribute('rel') || '').toLowerCase()
            const href = link.getAttribute('href') || ''
            // 拦截任何想 prefetch/preload opencv.js 的链接
            if ((rel === 'prefetch' || rel === 'preload' || rel === 'modulepreload') && href.includes('opencv.js')) {
              link.remove()
            }
            // 同时拦截 VitePress 对其他页面的 prefetch（解决首屏并发堵塞）
            if (rel === 'prefetch' && !href.includes('opencv.js')) {
              link.remove()
            }
          } else if (el.tagName === 'SCRIPT') {
            const src = (el as HTMLScriptElement).getAttribute('src') || ''
            if (src.includes('opencv.js') && !(el as HTMLElement).dataset?.cvBlob) {
              // 非我们注入的 opencv.js script——可能是某处默认自动注入的，移除
              el.remove()
            }
          }
        })
      }
    })
    mo.observe(document.head, { childList: true, subtree: true })
    mo.observe(document.body, { childList: true, subtree: true })

    // 3) 把 VitePress 自己的 link 预取逻辑 stub 掉
    setTimeout(() => {
      const vp = (window as any).__VITEPRESS__ ?? (window as any).__vitepress__
      if (vp && vp.router) {
        vp.router.preload = async () => {}
        if (vp.router.go) { /* 不动导航 */ }
      }
    }, 0)
  } catch (e) {
    console.warn('[prefetch-block] disable failed:', e)
  }
}

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'layout-bottom': () => h(MermaidGlobal)
    })
  },
  enhanceApp({ app }) {
    app.component('FamilyTree', FamilyTree)
    app.component('AlgorithmCard', AlgorithmCard)
    app.component('OpencvPlayground', OpencvPlayground)
    app.component('MathVisualizer', MathVisualizer)
    app.component('ConvDemo', ConvDemo)
    app.component('AlgoVisualizer', AlgoVisualizer)
  }
} satisfies Theme
