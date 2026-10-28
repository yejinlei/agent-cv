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
    // 1) 清理已存在的 prefetch 链接
    const removeExisting = () => {
      document.querySelectorAll('link[rel="prefetch"], link[rel="preload"][as="script"]').forEach((el) => {
        // 保留 opencv.js 自己的手动加载（它由 Playground 点击按钮后以普通 script 标签插入）
        const href = el.getAttribute('href') || ''
        if (href.includes('/lib/opencv.js')) return
        el.remove()
      })
    }
    removeExisting()

    // 2) 监听后续动态插入的 prefetch，立即移除
    const mo = new MutationObserver((muts) => {
      for (const m of muts) {
        m.addedNodes.forEach((n) => {
          if (n.nodeType === 1 && (n as HTMLElement).tagName === 'LINK') {
            const link = n as HTMLLinkElement
            const rel = (link.getAttribute('rel') || '').toLowerCase()
            const href = link.getAttribute('href') || ''
            if (rel === 'prefetch' && !href.includes('/lib/opencv.js')) {
              link.remove()
            }
          }
        })
      }
    })
    mo.observe(document.head, { childList: true, subtree: true })

    // 3) 把 VitePress 自己的 link 预取逻辑直接 stub 掉（1.6+ 的路由内部会用这个）
    setTimeout(() => {
      const vp = (window as any).__VITEPRESS__ ?? (window as any).__vitepress__
      if (vp && vp.router) {
        vp.router.preload = async () => {}
      }
    }, 0)
  } catch (e) {
    // 禁用预取失败不影响功能
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
