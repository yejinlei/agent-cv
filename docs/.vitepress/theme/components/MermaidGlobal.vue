<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

let mermaidApi = null
const loaded = ref(false)

async function ensureMermaid() {
  if (mermaidApi) return mermaidApi
  const mod = await import('mermaid')
  mermaidApi = mod.default
  mermaidApi.initialize({
    startOnLoad: false,
    theme: 'base',
    securityLevel: 'loose',
    fontFamily: 'inherit',
    themeVariables: {
      primaryColor: '#e8f0ff',
      primaryTextColor: '#1a2b50',
      primaryBorderColor: '#3b6fd4',
      lineColor: '#5b6b8c',
      secondaryColor: '#fff3e0',
      tertiaryColor: '#f3f6fb',
      fontSize: '14px'
    },
    flowchart: { curve: 'basis', htmlLabels: true, padding: 12 },
    sequence: { useMaxWidth: true }
  })
  return mermaidApi
}

async function render() {
  if (typeof window === 'undefined') return
  const nodes = document.querySelectorAll('.mermaid-wrapper')
  if (!nodes.length) return
  const api = await ensureMermaid()
  let n = 0
  for (const node of nodes) {
    if (node.dataset.rendered === '1') continue
    const code = decodeURIComponent(node.dataset.mermaid || '')
    const graphId = `mmd-${Date.now()}-${n++}`
    try {
      const { svg } = await api.render(graphId, code)
      node.innerHTML = svg
      node.dataset.rendered = '1'
    } catch (e) {
      node.dataset.rendered = 'error'
      console.error('mermaid render failed', e)
    }
  }
  loaded.value = true
}

let mo = null
onMounted(() => {
  render()
  // 处理路由切换 / 异步内容
  mo = new MutationObserver(() => render())
  mo.observe(document.body, { childList: true, subtree: true })
})
onUnmounted(() => mo && mo.disconnect())
</script>

<template>
  <span style="display: none" />
</template>
