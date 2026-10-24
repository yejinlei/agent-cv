import DefaultTheme from 'vitepress/theme-without-fonts'
import { h } from 'vue'
import type { Theme } from 'vitepress'

import './custom.css'
import FamilyTree from './components/FamilyTree.vue'
import MermaidGlobal from './components/MermaidGlobal.vue'
import AlgorithmCard from './components/AlgorithmCard.vue'
import OpencvPlayground from './components/OpencvPlayground.vue'

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
  }
} satisfies Theme
