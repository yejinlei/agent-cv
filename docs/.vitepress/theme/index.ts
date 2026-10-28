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

// 🔒 在客户端启动时关掉 VitePress 的视口预取（prefetch）。
// VitePress 默认对出现在视口里的所有链接发 prefetch，会把浏览器到 github.io 的
// 6 个并发连接全占满，导致真正需要的 OpenCV.js 脚本在队列里排队超时。
// 策略：
//   1) 移除现存的所有 link[rel=prefetch]；
//   2) 用 MutationObserver 持续拦截后续新增的 prefetch link；
//   3) stub 掉 VitePress router.preload；
//   4) **绝对不碰 <script> 标签**——我们自己加载 opencv.js 用的是普通
//      <script src="/agent-cv/lib/opencv.js"> 注入，标记 data-cv-script，
//      如果在 MutationObserver 里误删它，就会出现"下载完成后永远卡在初始化"。
if (typeof window !== 'undefined') {
  try {
    const removeExistingPrefetch = () => {
      document.querySelectorAll('link[rel="prefetch"]').forEach((el) => {
        el.remove()
      })
    }
    removeExistingPrefetch()

    const mo = new MutationObserver((muts) => {
      for (const m of muts) {
        m.addedNodes.forEach((n) => {
          if (n.nodeType !== 1) return
          const el = n as HTMLElement
          // 只处理 link 节点，绝不动 script
          if (el.tagName === 'LINK') {
            const link = el as HTMLLinkElement
            const rel = (link.getAttribute('rel') || '').toLowerCase()
            if (rel === 'prefetch') {
              link.remove()
            }
          }
        })
      }
    })
    mo.observe(document.head, { childList: true, subtree: true })
    if (document.body) {
      mo.observe(document.body, { childList: true, subtree: true })
    } else {
      document.addEventListener('DOMContentLoaded', () => {
        mo.observe(document.body, { childList: true, subtree: true })
      }, { once: true })
    }

    // Stub VitePress router.preload
    setTimeout(() => {
      const vp = (window as any).__VITEPRESS__ ?? (window as any).__vitepress__
      if (vp && vp.router && typeof vp.router.preload === 'function') {
        vp.router.preload = async () => {}
      }
    }, 0)
  } catch (e) {
    // 静默失败，不影响站点
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
