// Mermaid 代码块 -> 客户端渲染容器
// 用法：```mermaid ... ```
let id = 0

export function mermaidMarkdownPlugin(md) {
  const defaultFence =
    md.renderer.rules.fence ||
    function (tokens, idx, options, env, self) {
      return self.renderToken(tokens, idx, options)
    }

  md.renderer.rules.fence = (tokens, idx, options, env, self) => {
    const token = tokens[idx]
    const info = token.info ? token.info.trim() : ''
    if (info === 'mermaid') {
      const code = token.content
      const graphId = `mermaid-graph-${id++}`
      const encoded = encodeURIComponent(code)
      return `<div class="mermaid-wrapper" data-mermaid="${encoded}" id="${graphId}"><pre class="mermaid">${md.utils.escapeHtml(
        code
      )}</pre></div>`
    }
    return defaultFence(tokens, idx, options, env, self)
  }
}

export default mermaidMarkdownPlugin
