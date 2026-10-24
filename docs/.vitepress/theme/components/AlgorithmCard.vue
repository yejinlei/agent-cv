<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  enName: { type: String, default: '' },
  chapter: { type: String, default: '' },      // 所属章（学习路径纵轴，显示用）
  chapterLink: { type: String, default: '' },  // 章节跳转链接
  branch: { type: String, default: '' },        // 所属分支（技术族横轴）
  branchLink: { type: String, default: '' },    // 分支跳转链接
  year: { type: [String, Number], default: '' },
  author: { type: String, default: '' },
  paper: { type: String, default: '' },
  level: { type: String, default: '低层' },     // 低层/中层/高层
  tagline: { type: String, default: '' },       // 一句话白话
  analogy: { type: String, default: '' },       // 生活化比方
  scene: { type: String, default: '' },         // 生活/工业场景
  pros: { type: Array, default: () => [] },
  cons: { type: Array, default: () => [] }
})

const levelColor = computed(() => {
  switch (props.level) {
    case '低层': return { bg: '#e7f1ff', fg: '#0a3b6b', dot: '#4a90e2' }
    case '中层': return { bg: '#e8f8ec', fg: '#0b4d24', dot: '#52c77a' }
    case '高层': return { bg: '#ffece8', fg: '#6b1a08', dot: '#ef6b4a' }
    default:     return { bg: '#f0f0f5', fg: '#333',   dot: '#888' }
  }
})
</script>

<template>
  <div class="algo-card">
    <div class="algo-card__header">
      <div class="algo-card__title">
        <h3>{{ name }}<span v-if="enName" class="algo-card__en"> · {{ enName }}</span></h3>
        <p v-if="tagline" class="algo-card__tagline">{{ tagline }}</p>
      </div>
      <span class="algo-card__level" :style="{ background: levelColor.bg, color: levelColor.fg }">
        <span class="dot" :style="{ background: levelColor.dot }"></span>{{ level }}
      </span>
    </div>

    <div class="algo-card__axes">
      <a v-if="chapter" :href="chapterLink || '#'" class="axis-chip axis-chip--chapter" :class="{ 'axis-chip--link': chapterLink }">
        📘 {{ chapter }}
      </a>
      <a v-if="branch" :href="branchLink || '#'" class="axis-chip axis-chip--branch" :class="{ 'axis-chip--link': branchLink }">
        🌿 {{ branch }}
      </a>
      <span v-if="year" class="axis-chip axis-chip--meta">📅 {{ year }}</span>
      <span v-if="author" class="axis-chip axis-chip--meta">👤 {{ author }}</span>
    </div>

    <div v-if="analogy" class="algo-card__block">
      <div class="algo-card__label">💡 生活化比方</div>
      <p>{{ analogy }}</p>
    </div>

    <div v-if="scene" class="algo-card__block">
      <div class="algo-card__label">🎯 典型场景</div>
      <p>{{ scene }}</p>
    </div>

    <div class="algo-card__grid">
      <div v-if="pros.length" class="algo-card__pros">
        <div class="algo-card__label">✅ 强项</div>
        <ul><li v-for="p in pros">{{ p }}</li></ul>
      </div>
      <div v-if="cons.length" class="algo-card__cons">
        <div class="algo-card__label">⚠️ 短板</div>
        <ul><li v-for="c in cons">{{ c }}</li></ul>
      </div>
    </div>

    <a v-if="paper" :href="paper" target="_blank" class="algo-card__paper">📄 原论文链接</a>
  </div>
</template>

<style scoped>
.algo-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px 22px;
  background: #fff;
  margin: 16px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: box-shadow .2s, transform .2s;
}
.algo-card:hover {
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.algo-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}
.algo-card__title h3 { margin: 0; font-size: 20px; color: #111; }
.algo-card__en { color: #888; font-weight: normal; font-size: 14px; }
.algo-card__tagline { margin: 6px 0 0; color: #555; font-size: 14px; }
.algo-card__level {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;
  white-space: nowrap;
}
.algo-card__level .dot { width: 8px; height: 8px; border-radius: 50%; }

.algo-card__axes {
  display: flex; flex-wrap: wrap; gap: 6px;
  margin: 14px 0 10px;
}
.axis-chip {
  display: inline-block; padding: 3px 10px;
  font-size: 12px; border-radius: 4px;
}
.axis-chip--chapter { background: #fff3e0; color: #e65100; border-left: 3px solid #ff9800; }
.axis-chip--branch  { background: #e8eaf6; color: #283593; border-left: 3px solid #5c6bc0; }
.axis-chip--meta    { background: #f5f5f5; color: #555; }
.axis-chip--link {
  text-decoration: none; cursor: pointer; transition: filter .15s, transform .15s;
}
.axis-chip--link:hover { filter: brightness(.95); transform: translateY(-1px); }

.algo-card__block { margin: 12px 0; }
.algo-card__label { font-size: 12px; font-weight: 600; color: #888; margin-bottom: 4px; letter-spacing: .5px; }
.algo-card__block p { margin: 0; line-height: 1.7; color: #333; font-size: 14px; }

.algo-card__grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 12px 0;
}
.algo-card__grid ul { margin: 4px 0 0; padding-left: 20px; font-size: 13px; line-height: 1.7; color: #444; }
.algo-card__pros { background: #f3faf4; border-radius: 8px; padding: 10px 12px; }
.algo-card__cons { background: #fdf4f3; border-radius: 8px; padding: 10px 12px; }

.algo-card__paper {
  display: inline-block; margin-top: 8px;
  font-size: 13px; color: #4a90e2; text-decoration: none;
}
.algo-card__paper:hover { text-decoration: underline; }

@media (max-width: 600px) {
  .algo-card__grid { grid-template-columns: 1fr; }
  .algo-card__header { flex-direction: column; }
}
</style>
