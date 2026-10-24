<script setup>
/**
 * Mermaid 客户端渲染器
 *
 * 设计要点（很重要，别改回去）：
 * 1. 「单飞」——同一时刻只允许一个渲染循环在跑，新来的触发只登记一个待办标记。
 *    原实现允许任意多个并发循环抢同一批图，是流程图画不出来/卡死的根因。
 * 2. 渲染期间临时断开 MutationObserver，避免「自己改 DOM → 触发自己 → 再渲染」的雪崩。
 * 3. 用路由变化驱动重渲染，而不是对整个 body 的任意 DOM 变动做无限次全量扫描。
 * 4. 渲染失败时给出可见的错误提示，而不是让读者对着一片空白发呆。
 */
import { onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vitepress'

let mermaidApi = null

async function ensureMermaid() {
  if (mermaidApi) return mermaidApi
  const mod = await import('mermaid')
  mermaidApi = mod.default
  mermaidApi.initialize({
    startOnLoad: false,
    theme: 'base',
    securityLevel: 'loose',
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
    themeVariables: {
      primaryColor: '#e8f0ff',
      primaryTextColor: '#1a2b50',
      primaryBorderColor: '#3b6fd4',
      lineColor: '#5b6b8c',
      secondaryColor: '#fff3e0',
      tertiaryColor: '#f3f6fb',
      fontSize: '14px'
    },
    flowchart: { curve: 'basis', htmlLabels: true, padding: 12, useMaxWidth: true },
    sequence: { useMaxWidth: true }
  })
  return mermaidApi
}

let rendering = false
let pending = false

async function flush() {
  if (typeof window === 'undefined') return
  if (rendering) {
    pending = true
    return
  }
  rendering = true
  if (mo) mo.disconnect()
  try {
    const all = document.querySelectorAll('.mermaid-wrapper')
    const todo = []
    for (const node of all) {
      if (node.dataset.rendered === '1') continue
      if (node.dataset.rendered === 'error') continue
      todo.push(node)
    }
    if (!todo.length) return
    const api = await ensureMermaid()
    let i = 0
    for (const node of todo) {
      try {
        const code = decodeURIComponent(node.dataset.mermaid || '')
        const graphId = `mmd-${i++}-${Math.random().toString(36).slice(2, 8)}`
        const { svg } = await api.render(graphId, code)
        node.innerHTML = svg
        node.dataset.rendered = '1'
      } catch (e) {
        node.dataset.rendered = 'error'
        const msg = String((e && e.message) || e)
        node.innerHTML =
          '<div class="mermaid-error">⚠ 该流程图渲染失败：' +
          msg.replace(/[<>&]/g, '') +
          '</div>'
        console.error('[mermaid] render failed:', e)
      }
    }
  } catch (e) {
    console.error('[mermaid] init failed:', e)
  } finally {
    rendering = false
    if (mo) mo.observe(document.body, { childList: true, subtree: true })
    if (pending) {
      pending = false
      nextTick(() => flush())
    }
  }
}

let mo = null
const route = useRoute()

onMounted(() => {
  flush()
  // 兜底：只监听「节点被增删」，且渲染期间自断，触发时也只是登记一个待办
  mo = new MutationObserver(() => flush())
  mo.observe(document.body, { childList: true, subtree: true })
})

onUnmounted(() => {
  if (mo) mo.disconnect()
})

watch(
  () => route.path,
  () => nextTick(() => flush())
)
</script>

<template>
  <span style="display: none" />
</template>
