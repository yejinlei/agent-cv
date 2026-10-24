<script setup>
import { ref, onMounted, watch } from 'vue'

// 传统 CV 技术谱系数据（内置，可扩展为读取 YAML）
const data = {
  name: '传统计算机视觉',
  year: '1963–2012',
  children: [
    {
      name: '① 图像处理',
      color: '#3b6fd4',
      children: [
        { name: '线性滤波', year: '高斯/均值/中值', leaf: true },
        { name: 'Canny 边缘检测', year: '1986', leaf: true },
        { name: 'Sobel / Laplacian', year: '1968', leaf: true },
        { name: 'Otsu 阈值', year: '1979', leaf: true },
        { name: '形态学操作', year: '1980s', leaf: true }
      ]
    },
    {
      name: '② 特征检测',
      color: '#2fa36b',
      children: [
        { name: 'Harris 角点', year: '1988', leaf: true },
        { name: 'SIFT', year: '1999/2004', leaf: true },
        { name: 'SURF', year: '2006', leaf: true },
        { name: 'FAST', year: '2006', leaf: true },
        { name: 'ORB', year: '2011', leaf: true }
      ]
    },
    {
      name: '③ 特征匹配',
      color: '#d98324',
      children: [
        { name: 'Brute-Force / FLANN', year: '描述子匹配', leaf: true },
        { name: 'RANSAC', year: '1981', leaf: true },
        { name: 'Lucas-Kanade 光流', year: '1981', leaf: true },
        { name: '图像拼接', year: '全景', leaf: true }
      ]
    },
    {
      name: '④ 图像分割',
      color: '#9b59b6',
      children: [
        { name: '分水岭 Watershed', year: '1979', leaf: true },
        { name: 'MeanShift', year: '1995', leaf: true },
        { name: 'GrabCut', year: '2004', leaf: true },
        { name: 'GraphCut', year: '2001', leaf: true }
      ]
    },
    {
      name: '⑤ 目标检测',
      color: '#c0392b',
      children: [
        { name: 'Viola-Jones', year: '2001', leaf: true },
        { name: 'HOG+SVM', year: '2005', leaf: true },
        { name: 'DPM', year: '2008', leaf: true },
        { name: 'NMS 非极大值抑制', year: 'classic', leaf: true }
      ]
    },
    {
      name: '⑥ 几何视觉',
      color: '#16a2a2',
      children: [
        { name: '张正友标定法', year: '1999', leaf: true },
        { name: '对极几何 / 八点法', year: '1981', leaf: true },
        { name: '立体匹配 SGBM', year: 'classic', leaf: true },
        { name: 'SFM 结构光重建', year: '1992', leaf: true }
      ]
    }
  ]
}

const svgRef = ref(null)
const selected = ref('')
let d3mod = null

async function ensureD3() {
  if (d3mod) return d3mod
  d3mod = await import('d3')
  return d3mod
}

async function draw() {
  if (typeof window === 'undefined') return
  const d3 = await ensureD3()
  const el = svgRef.value
  if (!el) return
  el.innerHTML = ''

  const width = el.clientWidth || 960
  const height = 560
  const margin = { top: 24, right: 150, bottom: 24, left: 40 }

  const svg = d3
    .select(el)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height])
    .style('max-width', '100%')
    .style('height', 'auto')
    .style('font', '13px sans-serif')

  const root = d3.hierarchy(data)
  const dx = 40
  const dy = width / 5
  const tree = d3.tree().nodeSize([dx, dy])
  tree(root)

  let x0 = Infinity
  let x1 = -Infinity
  root.each((d) => {
    if (d.x > x1) x1 = d.x
    if (d.x < x0) x0 = d.x
  })

  const g = svg
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top - x0 + dx})`)

  const linkGen = d3
    .linkHorizontal()
    .x((d) => d.y)
    .y((d) => d.x)

  g.append('g')
    .attr('fill', 'none')
    .attr('stroke', '#c3ccdd')
    .attr('stroke-width', 1.5)
    .selectAll('path')
    .data(root.links())
    .join('path')
    .attr('d', linkGen)

  const node = g
    .append('g')
    .selectAll('g')
    .data(root.descendants())
    .join('g')
    .attr('transform', (d) => `translate(${d.y},${d.x})`)
    .style('cursor', (d) => (d.depth >= 1 ? 'pointer' : 'default'))

  node
    .append('circle')
    .attr('r', (d) => (d.depth === 0 ? 8 : d.depth === 1 ? 6 : 4))
    .attr('fill', (d) => (d.data.leaf ? '#fff' : d.data.color || '#3b6fd4'))
    .attr('stroke', (d) => d.data.color || '#3b6fd4')
    .attr('stroke-width', 2)

  node
    .append('text')
    .attr('dy', '0.32em')
    .attr('x', (d) => (d.children ? -10 : 10))
    .attr('text-anchor', (d) => (d.children ? 'end' : 'start'))
    .attr('font-weight', (d) => (d.depth <= 1 ? 700 : 400))
    .attr('fill', (d) => (d.depth <= 1 ? '#1a2b50' : '#4a5872'))
    .text((d) => d.data.name)

  node
    .append('text')
    .attr('dy', '1.5em')
    .attr('x', (d) => (d.children ? -10 : 10))
    .attr('text-anchor', (d) => (d.children ? 'end' : 'start'))
    .attr('font-size', '10px')
    .attr('fill', '#98a4b8')
    .text((d) => (d.data.leaf || d.depth === 1 ? d.data.year : ''))

  node.on('click', (evt, d) => {
    selected.value = `${d.data.name}  ${d.data.year || ''}`
  })
}

let ro = null
onMounted(async () => {
  await draw()
  ro = new ResizeObserver(() => draw())
  if (svgRef.value) ro.observe(svgRef.value)
})
watch(svgRef, () => draw())
</script>

<template>
  <div class="family-tree">
    <div ref="svgRef" class="family-tree__canvas" />
    <div class="family-tree__hint">
      点击任意节点查看名称 · 六条技术分支共 {{ 26 }} 个代表算法
      <span v-if="selected" class="family-tree__sel">已选：{{ selected }}</span>
    </div>
  </div>
</template>

<style scoped>
.family-tree {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  padding: 8px;
  margin: 16px 0;
}
.family-tree__canvas {
  width: 100%;
  overflow-x: auto;
}
.family-tree__hint {
  font-size: 12px;
  color: var(--vp-c-text-3);
  padding: 6px 10px;
}
.family-tree__sel {
  margin-left: 12px;
  color: #3b6fd4;
  font-weight: 600;
}
</style>
