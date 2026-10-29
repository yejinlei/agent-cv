import { defineConfig } from 'vitepress'
import { mermaidMarkdownPlugin } from './mermaid-plugin.mts'

export default defineConfig({
  lang: 'zh-CN',
  title: 'agent-cv',
  description: '传统计算机视觉本体论研究站 — 论文 → 理论 → 实现 → 实战',

  base: '/agent-cv/',
  ignoreDeadLinks: true,

  // VitePress 默认会对出现在视口里的所有链接做 <link rel="prefetch"> 预取，
  // 国内访问 GitHub Pages 链路下，这会让几十个章节分块同时下载，占满 6 个浏览器并发连接，
  // 把真正需要的 opencv.js 堵在队列里几分钟超时。
  // 这里不直接用 VitePress 的 prefetch: false（某些版本会引发 hydration/启动白屏问题），
  // 而是在 enhanceApp 里注入一个 MutationObserver，从 DOM 里主动移除任何预取 link，
  // 并把 window.checkViewport 空函数，从根上切断自动预取。

  markdown: {
    lineNumbers: true,
    math: true,
    config: (md) => {
      md.use(mermaidMarkdownPlugin)
    }
  },

  // 不再主动给 opencv.js 加 prefetch 链接——让 Playground 组件在用户点击「启动真机实验」按钮时才加载，
  // 保证所有页面首屏不会后台下载 3.5MB(gzip) 的 OpenCV，彻底告别并发堵塞。
  transformPageData() {
    return
  },

  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'agent-cv',

    nav: [
      { text: '🌱 小白入门', link: '/for-beginners' },
      {
        text: '🧭 学习路径',
        items: [
          { text: '学习路径地图（双轴）', link: '/learning-path' },
          { text: '🧪 原理实验室（看不懂公式点这）', link: '/math-lab/' },
          { text: '—— 章节体系 · 纵轴视角 ——', link: '/chapters/' },
          { text: '总览：章体系地图（预备篇 + 13 章）', link: '/chapters/' },
          { text: '第 1–2 章 · 视觉与图像基础', link: '/chapters/ch01-foundation' },
          { text: '第 3 章 · 图像预处理', link: '/chapters/ch03-preprocessing' },
          { text: '第 4 章 · 基元检测', link: '/chapters/ch04-primitives' },
          { text: '第 5 章 · 目标分割', link: '/chapters/ch05-segmentation' },
          { text: '第 6 章 · 目标表达和描述', link: '/chapters/ch06-representation' },
          { text: '第 7 章 · 纹理分析', link: '/chapters/ch07-texture' },
          { text: '第 8 章 · 形状分析', link: '/chapters/ch08-shape' },
          { text: '第 9 章 · 立体视觉', link: '/chapters/ch09-stereo' },
          { text: '第 10 章 · 三维景物恢复', link: '/chapters/ch10-3d-recovery' },
          { text: '第 11 章 · 运动分析', link: '/chapters/ch11-motion' },
          { text: '第 12 章 · 景物识别', link: '/chapters/ch12-recognition' },
          { text: '第 13 章 · 广义匹配', link: '/chapters/ch13-matching' },
          { text: '第 14 章 · 时空行为理解', link: '/chapters/ch14-activity' },
          { text: '第 15 章 · 场景解释', link: '/chapters/ch15-scene' }
        ]
      },
      { text: '🎮 真机实验室', link: '/playgrounds/' },
      {
        text: '🗺️ 知识图谱',
        items: [
          { text: '—— 技术分支 · 横轴视角 ——', link: '/branches/' },
          { text: '技术分支总览', link: '/branches/' },
          { text: '图像处理', link: '/branches/image-processing/' },
          { text: '特征检测', link: '/branches/feature-detection/' },
          { text: '特征匹配', link: '/branches/feature-matching/' },
          { text: '图像分割', link: '/branches/segmentation/' },
          { text: '目标检测', link: '/branches/detection/' },
          { text: '几何视觉', link: '/branches/geometry/' },
          { text: '🔧 工程实现层', link: '/branches/engineering/' },
          { text: '—— 全局视图 ——', link: '/global/family' },
          { text: '家族树', link: '/global/family' },
          { text: '系列演化', link: '/global/evolutions' },
          { text: '演进故事', link: '/global/evolution-story' },
          { text: '时间线', link: '/global/timeline' },
          { text: '外部技术影响', link: '/global/external-techniques' },
          { text: '—— 脉络与本体 ——', link: '/legacy/' },
          { text: '传承脉络', link: '/legacy/' },
          { text: '本体 Schema', link: '/ontology/schema' }
        ]
      },
      {
        text: '🧰 词典与工具',
        items: [
          { text: '🧱 算子词典', link: '/operators/' },
          { text: '场景反查', link: '/scenarios/' },
          { text: '术语表', link: '/glossary' },
          { text: '—— 横向工具页 ——', link: '/global/choose-algorithm' },
          { text: '算法选型决策树', link: '/global/choose-algorithm' },
          { text: '对比矩阵', link: '/global/compare-matrix' },
          { text: '基准数据', link: '/global/benchmarks' },
          { text: '数据流全景', link: '/global/data-flow' },
          { text: '故障排查手册', link: '/global/troubleshooting' },
          { text: '概念反向索引', link: '/global/concepts' },
          { text: '—— 案例与实现 ——', link: '/cases/' },
          { text: '实战案例', link: '/cases/' },
          { text: '衍生实现（OpenCV / HALCON / 嵌入式 / 现代继承）', link: '/derivatives/' },
          { text: '🚧 路线预告', link: '/derivatives/roadmap' }
        ]
      },
      {
        text: '📚 经典算法速查',
        items: [
          { text: '📋 版本总览 / 对比大表（59 个算法全在这）', link: '/versions/' },
          { text: '—— 按分支直达 ——', link: '/branches/' },
          { text: '① 图像处理', link: '/branches/image-processing/' },
          { text: '② 特征检测', link: '/branches/feature-detection/' },
          { text: '③ 特征匹配', link: '/branches/feature-matching/' },
          { text: '④ 图像分割', link: '/branches/segmentation/' },
          { text: '⑤ 目标检测与跟踪', link: '/branches/detection/' },
          { text: '⑥ 几何视觉', link: '/branches/geometry/' },
          { text: '—— 高频率算法直达 ——', link: '/algorithms/canny/' },
          { text: 'Canny 边缘检测', link: '/algorithms/canny/' },
          { text: '霍夫直线/圆检测', link: '/algorithms/hough/' },
          { text: 'Harris 角点', link: '/algorithms/harris/' },
          { text: 'SIFT 特征', link: '/algorithms/sift/' },
          { text: 'SURF / ORB / AKAZE / BRISK', link: '/algorithms/orb/' },
          { text: 'RANSAC 外点剔除', link: '/algorithms/ransac/' },
          { text: 'Lucas-Kanade 光流', link: '/algorithms/lucas-kanade/' },
          { text: 'GrabCut 交互式抠图', link: '/algorithms/grabcut/' },
          { text: 'Viola-Jones 人脸检测', link: '/algorithms/viola-jones/' },
          { text: '张氏相机标定', link: '/algorithms/zhang-calibration/' }
        ]
      }
    ],

    sidebar: {
      '/for-beginners': [
        {
          text: '🐣 小白入门 5 页',
          items: [
            { text: '首页：5 页地图', link: '/for-beginners/' },
            { text: '第 1 页 · 计算机视觉在做什么', link: '/for-beginners/p1-what-is-cv' },
            { text: '第 2 页 · 六个关键转折', link: '/for-beginners/p2-six-milestones' },
            { text: '第 3 页 · Canny 拆解（样板）', link: '/for-beginners/p3-canny-deep-dive' },
            { text: '第 4 页 · SIFT/V-J/HOG 各记一句', link: '/for-beginners/p4-other-classics' },
            { text: '第 5 页 · 什么时候用传统 CV', link: '/for-beginners/p5-when-to-use' }
          ]
        }
      ],
      '/learning-path': [
        {
          text: '🧭 学习路径（纵轴）',
          items: [
            { text: '总览：从像素到场景', link: '/learning-path' }
          ]
        }
      ],
      '/global/': [
        {
          text: '全局谱系',
          items: [
            { text: '传统 CV 家族树', link: '/global/family' },
            { text: '技术演化事件', link: '/global/evolutions' },
            { text: '演进故事 · 一条线看传统 CV', link: '/global/evolution-story' },
            { text: '发展时间线', link: '/global/timeline' },
            { text: '外部技术影响', link: '/global/external-techniques' }
          ]
        },
        {
          text: '横向使用页',
          items: [
            { text: '算法选型决策树', link: '/global/choose-algorithm' },
            { text: '算法对比矩阵', link: '/global/compare-matrix' },
            { text: '基准数据对照', link: '/global/benchmarks' },
            { text: '数据流全景图', link: '/global/data-flow' },
            { text: '故障排查手册', link: '/global/troubleshooting' },
            { text: '概念反向索引', link: '/global/concepts' }
          ]
        }
      ],
      '/ontology/': [
        {
          text: '知识本体',
          items: [
            { text: '本体总览', link: '/ontology/schema' },
            { text: '实体类型详解', link: '/ontology/entity-types' },
            { text: '关系定义', link: '/ontology/relations' },
            { text: '实例索引（175 条）', link: '/ontology/instances' }
          ]
        }
      ],
      '/branches/': [
        {
          text: '技术分支总览',
          items: [{ text: '六大分支', link: '/branches/' }]
        },
        {
          text: '① 图像处理',
          items: [
            { text: '分支导览', link: '/branches/image-processing/' },
            { text: '滤波与卷积', link: '/branches/image-processing/filtering' },
            { text: '阈值分割', link: '/branches/image-processing/thresholding' },
            { text: '形态学操作', link: '/branches/image-processing/morphology' }
          ]
        },
        {
          text: '② 特征检测',
          items: [
            { text: '分支导览', link: '/branches/feature-detection/' },
            { text: '边缘检测', link: '/branches/feature-detection/edges' },
            { text: '角点检测', link: '/branches/feature-detection/corners' },
            { text: '斑点与特征点', link: '/branches/feature-detection/blobs' }
          ]
        },
        {
          text: '③ 特征匹配',
          items: [
            { text: '分支导览', link: '/branches/feature-matching/' },
            { text: '描述子匹配', link: '/branches/feature-matching/descriptors' },
            { text: '鲁棒估计', link: '/branches/feature-matching/robust-estimation' }
          ]
        },
        {
          text: '④ 图像分割',
          items: [
            { text: '分支导览', link: '/branches/segmentation/' },
            { text: '区域与聚类分割', link: '/branches/segmentation/region-clustering' },
            { text: '交互式分割', link: '/branches/segmentation/interactive' }
          ]
        },
        {
          text: '⑤ 目标检测',
          items: [
            { text: '分支导览', link: '/branches/detection/' },
            { text: '滑动窗口与积分图', link: '/branches/detection/sliding-window' },
            { text: '经典检测器总览', link: '/branches/detection/classic-detectors' },
            { text: 'Viola-Jones 人脸检测', link: '/branches/detection/viola-jones' },
            { text: 'DPM 可变形部件模型', link: '/branches/detection/dpm' },
            { text: '词袋模型 BoVW', link: '/branches/detection/bovw' }
          ]
        },
        {
          text: '⑥ 几何视觉',
          items: [
            { text: '分支导览', link: '/branches/geometry/' },
            { text: '相机标定与对极几何', link: '/branches/geometry/camera-geometry' },
            { text: '立体匹配与 SFM', link: '/branches/geometry/stereo-sfm' }
          ]
        },
        {
          text: '🔧 工程实现层',
          items: [
            { text: '分支导览', link: '/branches/engineering/' },
            { text: 'OpenCV 库与 API 速查', link: '/branches/engineering/opencv-api' },
            { text: '性能与算力账本', link: '/branches/engineering/performance' },
            { text: '产线工程化管线', link: '/branches/engineering/pipeline' }
          ]
        }
      ],
      '/chapters/': [
        {
          text: '📚 章节体系（纵轴学习路径）',
          items: [{ text: '章体系地图总览', link: '/chapters/' }]
        },
        {
          text: '预备知识（打地基）',
          items: [{ text: '第 1–2 章 · 视觉与图像基础', link: '/chapters/ch01-foundation' }]
        },
        {
          text: '低层视觉（像素 → 特征）',
          items: [
            { text: '第 3 章 · 图像预处理', link: '/chapters/ch03-preprocessing' },
            { text: '第 4 章 · 基元检测', link: '/chapters/ch04-primitives' }
          ]
        },
        {
          text: '中层视觉（目标 → 描述）',
          items: [
            { text: '第 5 章 · 目标分割', link: '/chapters/ch05-segmentation' },
            { text: '第 6 章 · 目标表达和描述', link: '/chapters/ch06-representation' },
            { text: '第 7 章 · 纹理分析', link: '/chapters/ch07-texture' },
            { text: '第 8 章 · 形状分析', link: '/chapters/ch08-shape' }
          ]
        },
        {
          text: '高层视觉（几何 → 语义）',
          items: [
            { text: '第 9 章 · 立体视觉', link: '/chapters/ch09-stereo' },
            { text: '第 10 章 · 三维景物恢复', link: '/chapters/ch10-3d-recovery' },
            { text: '第 11 章 · 运动分析', link: '/chapters/ch11-motion' },
            { text: '第 12 章 · 景物识别', link: '/chapters/ch12-recognition' },
            { text: '第 13 章 · 广义匹配', link: '/chapters/ch13-matching' },
            { text: '第 14 章 · 时空行为理解', link: '/chapters/ch14-activity' },
            { text: '第 15 章 · 场景解释', link: '/chapters/ch15-scene' }
          ]
        }
      ],
      '/scenarios/': [
        {
          text: '🎯 按场景找算法',
          items: [{ text: '场景反查入口', link: '/scenarios/' }]
        },
        {
          text: '工业与测量',
          items: [
            { text: '零件缺陷检测', link: '/scenarios/defect-inspection' },
            { text: '尺寸测量与定位', link: '/scenarios/measurement' }
          ]
        },
        {
          text: '文档与人脸',
          items: [
            { text: '文档扫描与 OCR', link: '/scenarios/ocr-document' },
            { text: '车牌识别', link: '/scenarios/license-plate' },
            { text: '人脸识别', link: '/scenarios/face-recognition' }
          ]
        },
        {
          text: '拼接与重建',
          items: [{ text: '全景拼接', link: '/scenarios/panorama' }]
        }
      ],
      '/operators/': [
        {
          text: '🧱 算子词典',
          items: [
            { text: '算子总览', link: '/operators/' },
            { text: '高斯模糊', link: '/operators/gaussian-blur' },
            { text: '高斯差分 DoG', link: '/operators/dog' },
            { text: 'Sobel 算子', link: '/operators/sobel' },
            { text: '非极大值抑制 NMS', link: '/operators/non-max-suppression' },
            { text: '滞后连接', link: '/operators/hysteresis-tracking' },
            { text: '双阈值判定', link: '/operators/double-threshold' },
            { text: 'L2 归一化', link: '/operators/l2-normalization' },
            { text: '自适应阈值', link: '/operators/adaptive-threshold' },
            { text: '直方图统计', link: '/operators/histogram' },
            { text: 'Hessian 矩阵', link: '/operators/hessian' },
            { text: '泰勒展开（亚像素）', link: '/operators/taylor-expansion' },
            { text: 'AdaBoost 集成学习', link: '/operators/adaboost' },
            { text: 'SVM 训练', link: '/operators/svm-training' }
          ]
        }
      ],
      '/algorithms/': [
        { text: '算法档案（完整版）', items: [{ text: '版本总览 / 对比大表', link: '/versions/' }] },
        {
          text: 'Canny 边缘检测（样板）',
          items: [
            { text: '总览', link: '/algorithms/canny/' },
            { text: '论文精读', link: '/algorithms/canny/paper' },
            { text: '核心概念', link: '/algorithms/canny/concepts' },
            { text: '算法流程', link: '/algorithms/canny/architecture' },
            { text: '源码走读', link: '/algorithms/canny/source' },
            { text: '实战与踩坑', link: '/algorithms/canny/painpoints' },
            { text: '调参技巧', link: '/algorithms/canny/tricks' }
          ]
        },
        {
          text: 'SIFT 特征匹配（样板）',
          items: [
            { text: '总览', link: '/algorithms/sift/' },
            { text: '论文精读', link: '/algorithms/sift/paper' },
            { text: '核心概念', link: '/algorithms/sift/concepts' },
            { text: '算法流程', link: '/algorithms/sift/architecture' },
            { text: '源码走读', link: '/algorithms/sift/source' },
            { text: '实战与踩坑', link: '/algorithms/sift/painpoints' },
            { text: '调参技巧', link: '/algorithms/sift/tricks' }
          ]
        },
        {
          text: 'HOG+SVM 行人检测（样板）',
          items: [
            { text: '总览', link: '/algorithms/hog-svm/' },
            { text: '论文精读', link: '/algorithms/hog-svm/paper' },
            { text: '核心概念', link: '/algorithms/hog-svm/concepts' },
            { text: '算法流程', link: '/algorithms/hog-svm/architecture' },
            { text: '源码走读', link: '/algorithms/hog-svm/source' },
            { text: '实战与踩坑', link: '/algorithms/hog-svm/painpoints' },
            { text: '调参技巧', link: '/algorithms/hog-svm/tricks' }
          ]
        },
        {
          text: 'Harris 角点检测',
          items: [
            { text: '总览', link: '/algorithms/harris/' },
            { text: '论文精读', link: '/algorithms/harris/paper' },
            { text: '核心概念', link: '/algorithms/harris/concepts' },
            { text: '算法流程', link: '/algorithms/harris/architecture' },
            { text: '源码走读', link: '/algorithms/harris/source' },
            { text: '实战与踩坑', link: '/algorithms/harris/painpoints' },
            { text: '调参技巧', link: '/algorithms/harris/tricks' }
          ]
        },
        {
          text: 'RANSAC 外点剔除',
          items: [
            { text: '总览', link: '/algorithms/ransac/' },
            { text: '论文精读', link: '/algorithms/ransac/paper' },
            { text: '核心概念', link: '/algorithms/ransac/concepts' },
            { text: '算法流程', link: '/algorithms/ransac/architecture' },
            { text: '源码走读', link: '/algorithms/ransac/source' },
            { text: '实战与踩坑', link: '/algorithms/ransac/painpoints' },
            { text: '调参技巧', link: '/algorithms/ransac/tricks' }
          ]
        },
        {
          text: 'Lucas-Kanade 光流',
          items: [
            { text: '总览', link: '/algorithms/lucas-kanade/' },
            { text: '论文精读', link: '/algorithms/lucas-kanade/paper' },
            { text: '核心概念', link: '/algorithms/lucas-kanade/concepts' },
            { text: '算法流程', link: '/algorithms/lucas-kanade/architecture' },
            { text: '源码走读', link: '/algorithms/lucas-kanade/source' },
            { text: '实战与踩坑', link: '/algorithms/lucas-kanade/painpoints' },
            { text: '调参技巧', link: '/algorithms/lucas-kanade/tricks' }
          ]
        },
        {
          text: '张氏相机标定',
          items: [
            { text: '总览', link: '/algorithms/zhang-calibration/' },
            { text: '论文精读', link: '/algorithms/zhang-calibration/paper' },
            { text: '核心概念', link: '/algorithms/zhang-calibration/concepts' },
            { text: '算法流程', link: '/algorithms/zhang-calibration/architecture' },
            { text: '源码走读', link: '/algorithms/zhang-calibration/source' },
            { text: '实战与踩坑', link: '/algorithms/zhang-calibration/painpoints' },
            { text: '调参技巧', link: '/algorithms/zhang-calibration/tricks' }
          ]
        },
        {
          text: '霍夫变换·直线/圆检测',
          items: [
            { text: '总览', link: '/algorithms/hough/' },
            { text: '论文精读', link: '/algorithms/hough/paper' },
            { text: '核心概念', link: '/algorithms/hough/concepts' },
            { text: '算法流程', link: '/algorithms/hough/architecture' },
            { text: '源码走读', link: '/algorithms/hough/source' },
            { text: '实战与踩坑', link: '/algorithms/hough/painpoints' },
            { text: '调参技巧', link: '/algorithms/hough/tricks' }
          ]
        },
        {
          text: 'Sobel 边缘算子（基础原子算子）',
          items: [
            { text: '总览', link: '/algorithms/sobel/' },
            { text: '论文精读', link: '/algorithms/sobel/paper' },
            { text: '核心概念', link: '/algorithms/sobel/concepts' },
            { text: '算法流程', link: '/algorithms/sobel/architecture' },
            { text: '源码走读', link: '/algorithms/sobel/source' },
            { text: '实战与踩坑', link: '/algorithms/sobel/painpoints' },
            { text: '调参技巧', link: '/algorithms/sobel/tricks' }
          ]
        },
        {
          text: 'Otsu 大津阈值（基础原子算子）',
          items: [
            { text: '总览', link: '/algorithms/otsu/' },
            { text: '论文精读', link: '/algorithms/otsu/paper' },
            { text: '核心概念', link: '/algorithms/otsu/concepts' },
            { text: '算法流程', link: '/algorithms/otsu/architecture' },
            { text: '源码走读', link: '/algorithms/otsu/source' },
            { text: '实战与踩坑', link: '/algorithms/otsu/painpoints' },
            { text: '调参技巧', link: '/algorithms/otsu/tricks' }
          ]
        },
        {
          text: '对极几何与三角化（进阶应用）',
          items: [
            { text: '总览', link: '/algorithms/epipolar-geometry/' },
            { text: '论文精读', link: '/algorithms/epipolar-geometry/paper' },
            { text: '核心概念', link: '/algorithms/epipolar-geometry/concepts' },
            { text: '算法流程', link: '/algorithms/epipolar-geometry/architecture' },
            { text: '源码走读', link: '/algorithms/epipolar-geometry/source' },
            { text: '实战与踩坑', link: '/algorithms/epipolar-geometry/painpoints' },
            { text: '调参技巧', link: '/algorithms/epipolar-geometry/tricks' }
          ]
        },
        {
          text: 'Viola-Jones 人脸检测',
          items: [
            { text: '总览', link: '/algorithms/viola-jones/' },
            { text: '论文精读', link: '/algorithms/viola-jones/paper' },
            { text: '核心概念', link: '/algorithms/viola-jones/concepts' },
            { text: '算法流程', link: '/algorithms/viola-jones/architecture' },
            { text: '源码走读', link: '/algorithms/viola-jones/source' },
            { text: '实战与踩坑', link: '/algorithms/viola-jones/painpoints' },
            { text: '调参技巧', link: '/algorithms/viola-jones/tricks' }
          ]
        },
        {
          text: 'BoVW 词袋模型',
          items: [
            { text: '总览', link: '/algorithms/bovw/' },
            { text: '论文精读', link: '/algorithms/bovw/paper' },
            { text: '核心概念', link: '/algorithms/bovw/concepts' },
            { text: '算法流程', link: '/algorithms/bovw/architecture' },
            { text: '源码走读', link: '/algorithms/bovw/source' },
            { text: '实战与踩坑', link: '/algorithms/bovw/painpoints' },
            { text: '调参技巧', link: '/algorithms/bovw/tricks' }
          ]
        },
        {
          text: 'SURF 加速稳健特征',
          items: [
            { text: '总览', link: '/algorithms/surf/' },
            { text: '论文精读', link: '/algorithms/surf/paper' },
            { text: '核心概念', link: '/algorithms/surf/concepts' },
            { text: '算法流程', link: '/algorithms/surf/architecture' },
            { text: '源码走读', link: '/algorithms/surf/source' },
            { text: '实战与踩坑', link: '/algorithms/surf/painpoints' },
            { text: '调参技巧', link: '/algorithms/surf/tricks' }
          ]
        },
        {
          text: 'DPM 可变形部件模型',
          items: [
            { text: '总览', link: '/algorithms/dpm/' },
            { text: '论文精读', link: '/algorithms/dpm/paper' },
            { text: '核心概念', link: '/algorithms/dpm/concepts' },
            { text: '算法流程', link: '/algorithms/dpm/architecture' },
            { text: '源码走读', link: '/algorithms/dpm/source' },
            { text: '实战与踩坑', link: '/algorithms/dpm/painpoints' },
            { text: '调参技巧', link: '/algorithms/dpm/tricks' }
          ]
        },
        {
          text: 'ORB 实时特征点',
          items: [
            { text: '总览', link: '/algorithms/orb/' },
            { text: '论文精读', link: '/algorithms/orb/paper' },
            { text: '核心概念', link: '/algorithms/orb/concepts' },
            { text: '算法流程', link: '/algorithms/orb/architecture' },
            { text: '源码走读', link: '/algorithms/orb/source' },
            { text: '实战与踩坑', link: '/algorithms/orb/painpoints' },
            { text: '调参技巧', link: '/algorithms/orb/tricks' }
          ]
        },
        {
          text: 'FAST 高速角点 (2006)',
          items: [
            { text: '总览', link: '/algorithms/fast/' },
            { text: '论文精读', link: '/algorithms/fast/paper' },
            { text: '核心概念', link: '/algorithms/fast/concepts' },
            { text: '算法流程', link: '/algorithms/fast/architecture' },
            { text: '源码走读', link: '/algorithms/fast/source' },
            { text: '实战与踩坑', link: '/algorithms/fast/painpoints' },
            { text: '调参技巧', link: '/algorithms/fast/tricks' }
          ]
        },
        {
          text: 'Shi-Tomasi 好跟踪角点 (1994)',
          items: [
            { text: '总览', link: '/algorithms/shi-tomasi/' },
            { text: '论文精读', link: '/algorithms/shi-tomasi/paper' },
            { text: '核心概念', link: '/algorithms/shi-tomasi/concepts' },
            { text: '算法流程', link: '/algorithms/shi-tomasi/architecture' },
            { text: '源码走读', link: '/algorithms/shi-tomasi/source' },
            { text: '实战与踩坑', link: '/algorithms/shi-tomasi/painpoints' },
            { text: '调参技巧', link: '/algorithms/shi-tomasi/tricks' }
          ]
        },
        {
          text: 'MSER 最大稳定极值区域 (2002)',
          items: [
            { text: '总览', link: '/algorithms/mser/' },
            { text: '论文精读', link: '/algorithms/mser/paper' },
            { text: '核心概念', link: '/algorithms/mser/concepts' },
            { text: '算法流程', link: '/algorithms/mser/architecture' },
            { text: '源码走读', link: '/algorithms/mser/source' },
            { text: '实战与踩坑', link: '/algorithms/mser/painpoints' },
            { text: '调参技巧', link: '/algorithms/mser/tricks' }
          ]
        },
        {
          text: 'BRIEF 二进制描述子 (2010)',
          items: [
            { text: '总览', link: '/algorithms/brief/' },
            { text: '论文精读', link: '/algorithms/brief/paper' },
            { text: '核心概念', link: '/algorithms/brief/concepts' },
            { text: '算法流程', link: '/algorithms/brief/architecture' },
            { text: '源码走读', link: '/algorithms/brief/source' },
            { text: '实战与踩坑', link: '/algorithms/brief/painpoints' },
            { text: '调参技巧', link: '/algorithms/brief/tricks' }
          ]
        },
        {
          text: 'K-Means 颜色聚类',
          items: [
            { text: '总览', link: '/algorithms/kmeans/' },
            { text: '论文精读', link: '/algorithms/kmeans/paper' },
            { text: '核心概念', link: '/algorithms/kmeans/concepts' },
            { text: '算法流程', link: '/algorithms/kmeans/architecture' },
            { text: '源码走读', link: '/algorithms/kmeans/source' },
            { text: '实战与踩坑', link: '/algorithms/kmeans/painpoints' },
            { text: '调参技巧', link: '/algorithms/kmeans/tricks' }
          ]
        },
        {
          text: 'Mean Shift 均值漂移 (2002)',
          items: [
            { text: '总览', link: '/algorithms/meanshift/' },
            { text: '论文精读', link: '/algorithms/meanshift/paper' },
            { text: '核心概念', link: '/algorithms/meanshift/concepts' },
            { text: '算法流程', link: '/algorithms/meanshift/architecture' },
            { text: '源码走读', link: '/algorithms/meanshift/source' },
            { text: '实战与踩坑', link: '/algorithms/meanshift/painpoints' },
            { text: '调参技巧', link: '/algorithms/meanshift/tricks' }
          ]
        },
        {
          text: 'SLIC 超像素 (2012)',
          items: [
            { text: '总览', link: '/algorithms/slic/' },
            { text: '论文精读', link: '/algorithms/slic/paper' },
            { text: '核心概念', link: '/algorithms/slic/concepts' },
            { text: '算法流程', link: '/algorithms/slic/architecture' },
            { text: '源码走读', link: '/algorithms/slic/source' },
            { text: '实战与踩坑', link: '/algorithms/slic/painpoints' },
            { text: '调参技巧', link: '/algorithms/slic/tricks' }
          ]
        },
        {
          text: '分水岭分割 (1991)',
          items: [
            { text: '总览', link: '/algorithms/watershed/' },
            { text: '论文精读', link: '/algorithms/watershed/paper' },
            { text: '核心概念', link: '/algorithms/watershed/concepts' },
            { text: '算法流程', link: '/algorithms/watershed/architecture' },
            { text: '源码走读', link: '/algorithms/watershed/source' },
            { text: '实战与踩坑', link: '/algorithms/watershed/painpoints' },
            { text: '调参技巧', link: '/algorithms/watershed/tricks' }
          ]
        },
        {
          text: '数学形态学基础 (1982)',
          items: [
            { text: '总览', link: '/algorithms/morphology/' },
            { text: '论文精读', link: '/algorithms/morphology/paper' },
            { text: '核心概念', link: '/algorithms/morphology/concepts' },
            { text: '算法流程', link: '/algorithms/morphology/architecture' },
            { text: '源码走读', link: '/algorithms/morphology/source' },
            { text: '实战与踩坑', link: '/algorithms/morphology/painpoints' },
            { text: '调参技巧', link: '/algorithms/morphology/tricks' }
          ]
        },
        {
          text: 'GrabCut 交互式抠图 (2004)',
          items: [
            { text: '总览', link: '/algorithms/grabcut/' },
            { text: '论文精读', link: '/algorithms/grabcut/paper' },
            { text: '核心概念', link: '/algorithms/grabcut/concepts' },
            { text: '算法流程', link: '/algorithms/grabcut/architecture' },
            { text: '源码走读', link: '/algorithms/grabcut/source' },
            { text: '实战与踩坑', link: '/algorithms/grabcut/painpoints' },
            { text: '调参技巧', link: '/algorithms/grabcut/tricks' }
          ]
        },
        {
          text: 'SGBM 半全局立体匹配 (2005)',
          items: [
            { text: '总览', link: '/algorithms/sgbm/' },
            { text: '论文精读', link: '/algorithms/sgbm/paper' },
            { text: '核心概念', link: '/algorithms/sgbm/concepts' },
            { text: '算法流程', link: '/algorithms/sgbm/architecture' },
            { text: '源码走读', link: '/algorithms/sgbm/source' },
            { text: '实战与踩坑', link: '/algorithms/sgbm/painpoints' },
            { text: '调参技巧', link: '/algorithms/sgbm/tricks' }
          ]
        },
        {
          text: 'Farnebäck 稠密光流 (2003)',
          items: [
            { text: '总览', link: '/algorithms/farneback/' },
            { text: '论文精读', link: '/algorithms/farneback/paper' },
            { text: '核心概念', link: '/algorithms/farneback/concepts' },
            { text: '算法流程', link: '/algorithms/farneback/architecture' },
            { text: '源码走读', link: '/algorithms/farneback/source' },
            { text: '实战与踩坑', link: '/algorithms/farneback/painpoints' },
            { text: '调参技巧', link: '/algorithms/farneback/tricks' }
          ]
        },
        {
          text: 'Horn-Schunck 稠密光流 (1981)',
          items: [
            { text: '总览', link: '/algorithms/horn-schunck/' },
            { text: '论文精读', link: '/algorithms/horn-schunck/paper' },
            { text: '核心概念', link: '/algorithms/horn-schunck/concepts' },
            { text: '算法流程', link: '/algorithms/horn-schunck/architecture' },
            { text: '源码走读', link: '/algorithms/horn-schunck/source' },
            { text: '实战与踩坑', link: '/algorithms/horn-schunck/painpoints' },
            { text: '调参技巧', link: '/algorithms/horn-schunck/tricks' }
          ]
        },
        {
          text: 'EPnP 位姿估计 (2009)',
          items: [
            { text: '总览', link: '/algorithms/pnpsolver/' },
            { text: '论文精读', link: '/algorithms/pnpsolver/paper' },
            { text: '核心概念', link: '/algorithms/pnpsolver/concepts' },
            { text: '算法流程', link: '/algorithms/pnpsolver/architecture' },
            { text: '源码走读', link: '/algorithms/pnpsolver/source' },
            { text: '实战与踩坑', link: '/algorithms/pnpsolver/painpoints' },
            { text: '调参技巧', link: '/algorithms/pnpsolver/tricks' }
          ]
        },
        {
          text: 'ICP 点云配准 (1992)',
          items: [
            { text: '总览', link: '/algorithms/icp/' },
            { text: '论文精读', link: '/algorithms/icp/paper' },
            { text: '核心概念', link: '/algorithms/icp/concepts' },
            { text: '算法流程', link: '/algorithms/icp/architecture' },
            { text: '源码走读', link: '/algorithms/icp/source' },
            { text: '实战与踩坑', link: '/algorithms/icp/painpoints' },
            { text: '调参技巧', link: '/algorithms/icp/tricks' }
          ]
        },
        {
          text: '单应矩阵估计',
          items: [
            { text: '总览', link: '/algorithms/homography/' },
            { text: '论文精读', link: '/algorithms/homography/paper' },
            { text: '核心概念', link: '/algorithms/homography/concepts' },
            { text: '算法流程', link: '/algorithms/homography/architecture' },
            { text: '源码走读', link: '/algorithms/homography/source' },
            { text: '实战与踩坑', link: '/algorithms/homography/painpoints' },
            { text: '调参技巧', link: '/algorithms/homography/tricks' }
          ]
        },
        {
          text: 'CamShift 连续自适应跟踪 (1998)',
          items: [
            { text: '总览', link: '/algorithms/camshift/' },
            { text: '论文精读', link: '/algorithms/camshift/paper' },
            { text: '核心概念', link: '/algorithms/camshift/concepts' },
            { text: '算法流程', link: '/algorithms/camshift/architecture' },
            { text: '源码走读', link: '/algorithms/camshift/source' },
            { text: '实战与踩坑', link: '/algorithms/camshift/painpoints' },
            { text: '调参技巧', link: '/algorithms/camshift/tricks' }
          ]
        },
        {
          text: 'BRISK 二进制尺度旋转不变特征 (2011)',
          items: [
            { text: '总览', link: '/algorithms/brisk/' },
            { text: '论文精读', link: '/algorithms/brisk/paper' },
            { text: '核心概念', link: '/algorithms/brisk/concepts' },
            { text: '算法流程', link: '/algorithms/brisk/architecture' },
            { text: '源码走读', link: '/algorithms/brisk/source' },
            { text: '实战与踩坑', link: '/algorithms/brisk/painpoints' },
            { text: '调参技巧', link: '/algorithms/brisk/tricks' }
          ]
        },
        {
          text: 'AKAZE 加速 KAZE 非线性特征 (2013)',
          items: [
            { text: '总览', link: '/algorithms/akaze/' },
            { text: '论文精读', link: '/algorithms/akaze/paper' },
            { text: '核心概念', link: '/algorithms/akaze/concepts' },
            { text: '算法流程', link: '/algorithms/akaze/architecture' },
            { text: '源码走读', link: '/algorithms/akaze/source' },
            { text: '实战与踩坑', link: '/algorithms/akaze/painpoints' },
            { text: '调参技巧', link: '/algorithms/akaze/tricks' }
          ]
        },
        {
          text: 'CLAHE 限制对比度自适应直方图均衡 (1994)',
          items: [
            { text: '总览', link: '/algorithms/clahe/' },
            { text: '论文精读', link: '/algorithms/clahe/paper' },
            { text: '核心概念', link: '/algorithms/clahe/concepts' },
            { text: '算法流程', link: '/algorithms/clahe/architecture' },
            { text: '源码走读', link: '/algorithms/clahe/source' },
            { text: '实战与踩坑', link: '/algorithms/clahe/painpoints' },
            { text: '调参技巧', link: '/algorithms/clahe/tricks' }
          ]
        },
        {
          text: '距离变换 (1966)',
          items: [
            { text: '总览', link: '/algorithms/distance-transform/' },
            { text: '论文精读', link: '/algorithms/distance-transform/paper' },
            { text: '核心概念', link: '/algorithms/distance-transform/concepts' },
            { text: '算法流程', link: '/algorithms/distance-transform/architecture' },
            { text: '源码走读', link: '/algorithms/distance-transform/source' },
            { text: '实战与踩坑', link: '/algorithms/distance-transform/painpoints' },
            { text: '调参技巧', link: '/algorithms/distance-transform/tricks' }
          ]
        },
        {
          text: '连通域分析 Two-Pass (1966)',
          items: [
            { text: '总览', link: '/algorithms/connected-components/' },
            { text: '论文精读', link: '/algorithms/connected-components/paper' },
            { text: '核心概念', link: '/algorithms/connected-components/concepts' },
            { text: '算法流程', link: '/algorithms/connected-components/architecture' },
            { text: '源码走读', link: '/algorithms/connected-components/source' },
            { text: '实战与踩坑', link: '/algorithms/connected-components/painpoints' },
            { text: '调参技巧', link: '/algorithms/connected-components/tricks' }
          ]
        },
        {
          text: '区域生长分割 (1994)',
          items: [
            { text: '总览', link: '/algorithms/region-growing/' },
            { text: '论文精读', link: '/algorithms/region-growing/paper' },
            { text: '核心概念', link: '/algorithms/region-growing/concepts' },
            { text: '算法流程', link: '/algorithms/region-growing/architecture' },
            { text: '源码走读', link: '/algorithms/region-growing/source' },
            { text: '实战与踩坑', link: '/algorithms/region-growing/painpoints' },
            { text: '调参技巧', link: '/algorithms/region-growing/tricks' }
          ]
        },
        {
          text: 'Gabor 纹理滤波 (1985)',
          items: [
            { text: '总览', link: '/algorithms/gabor/' },
            { text: '论文精读', link: '/algorithms/gabor/paper' },
            { text: '核心概念', link: '/algorithms/gabor/concepts' },
            { text: '算法流程', link: '/algorithms/gabor/architecture' },
            { text: '源码走读', link: '/algorithms/gabor/source' },
            { text: '实战与踩坑', link: '/algorithms/gabor/painpoints' },
            { text: '调参技巧', link: '/algorithms/gabor/tricks' }
          ]
        },
        {
          text: 'CSRT 通道空间可靠性跟踪 (2017)',
          items: [
            { text: '总览', link: '/algorithms/csrt/' },
            { text: '论文精读', link: '/algorithms/csrt/paper' },
            { text: '核心概念', link: '/algorithms/csrt/concepts' },
            { text: '算法流程', link: '/algorithms/csrt/architecture' },
            { text: '源码走读', link: '/algorithms/csrt/source' },
            { text: '实战与踩坑', link: '/algorithms/csrt/painpoints' },
            { text: '调参技巧', link: '/algorithms/csrt/tricks' }
          ]
        },
        {
          text: '双边滤波保边去噪 (1998)',
          items: [
            { text: '总览', link: '/algorithms/bilateral/' },
            { text: '论文精读', link: '/algorithms/bilateral/paper' },
            { text: '核心概念', link: '/algorithms/bilateral/concepts' },
            { text: '算法流程', link: '/algorithms/bilateral/architecture' },
            { text: '源码走读', link: '/algorithms/bilateral/source' },
            { text: '实战与踩坑', link: '/algorithms/bilateral/painpoints' },
            { text: '调参技巧', link: '/algorithms/bilateral/tricks' }
          ]
        },
        {
          text: 'MOG2 背景减除 (2004)',
          items: [
            { text: '总览', link: '/algorithms/mog2/' },
            { text: '论文精读', link: '/algorithms/mog2/paper' },
            { text: '核心概念', link: '/algorithms/mog2/concepts' },
            { text: '算法流程', link: '/algorithms/mog2/architecture' },
            { text: '源码走读', link: '/algorithms/mog2/source' },
            { text: '实战与踩坑', link: '/algorithms/mog2/painpoints' },
            { text: '调参技巧', link: '/algorithms/mog2/tricks' }
          ]
        },
        {
          text: 'KCF 核相关滤波跟踪 (2015)',
          items: [
            { text: '总览', link: '/algorithms/kcf/' },
            { text: '论文精读', link: '/algorithms/kcf/paper' },
            { text: '核心概念', link: '/algorithms/kcf/concepts' },
            { text: '算法流程', link: '/algorithms/kcf/architecture' },
            { text: '源码走读', link: '/algorithms/kcf/source' },
            { text: '实战与踩坑', link: '/algorithms/kcf/painpoints' },
            { text: '调参技巧', link: '/algorithms/kcf/tricks' }
          ]
        },
        {
          text: 'LBP 局部二值模式 (1996)',
          items: [
            { text: '总览', link: '/algorithms/lbp/' },
            { text: '论文精读', link: '/algorithms/lbp/paper' },
            { text: '核心概念', link: '/algorithms/lbp/concepts' },
            { text: '算法流程', link: '/algorithms/lbp/architecture' },
            { text: '源码走读', link: '/algorithms/lbp/source' },
            { text: '实战与踩坑', link: '/algorithms/lbp/painpoints' },
            { text: '调参技巧', link: '/algorithms/lbp/tricks' }
          ]
        },
        {
          text: '高斯滤波 (1990)',
          items: [
            { text: '总览', link: '/algorithms/gaussian-blur/' },
            { text: '论文精读', link: '/algorithms/gaussian-blur/paper' },
            { text: '核心概念', link: '/algorithms/gaussian-blur/concepts' },
            { text: '算法流程', link: '/algorithms/gaussian-blur/architecture' },
            { text: '源码走读', link: '/algorithms/gaussian-blur/source' },
            { text: '实战与踩坑', link: '/algorithms/gaussian-blur/painpoints' },
            { text: '调参技巧', link: '/algorithms/gaussian-blur/tricks' }
          ]
        },
        {
          text: '中值滤波 (1979)',
          items: [
            { text: '总览', link: '/algorithms/median-filter/' },
            { text: '论文精读', link: '/algorithms/median-filter/paper' },
            { text: '核心概念', link: '/algorithms/median-filter/concepts' },
            { text: '算法流程', link: '/algorithms/median-filter/architecture' },
            { text: '源码走读', link: '/algorithms/median-filter/source' },
            { text: '实战与踩坑', link: '/algorithms/median-filter/painpoints' },
            { text: '调参技巧', link: '/algorithms/median-filter/tricks' }
          ]
        },
        {
          text: '霍夫圆变换 (1972)',
          items: [
            { text: '总览', link: '/algorithms/hough-circles/' },
            { text: '论文精读', link: '/algorithms/hough-circles/paper' },
            { text: '核心概念', link: '/algorithms/hough-circles/concepts' },
            { text: '算法流程', link: '/algorithms/hough-circles/architecture' },
            { text: '源码走读', link: '/algorithms/hough-circles/source' },
            { text: '实战与踩坑', link: '/algorithms/hough-circles/painpoints' },
            { text: '调参技巧', link: '/algorithms/hough-circles/tricks' }
          ]
        },
        {
          text: '轮廓拟合与多边形逼近 (1992)',
          items: [
            { text: '总览', link: '/algorithms/contour-fitting/' },
            { text: '论文精读', link: '/algorithms/contour-fitting/paper' },
            { text: '核心概念', link: '/algorithms/contour-fitting/concepts' },
            { text: '算法流程', link: '/algorithms/contour-fitting/architecture' },
            { text: '源码走读', link: '/algorithms/contour-fitting/source' },
            { text: '实战与踩坑', link: '/algorithms/contour-fitting/painpoints' },
            { text: '调参技巧', link: '/algorithms/contour-fitting/tricks' }
          ]
        },
        {
          text: 'FREAK 仿生二进制描述子 (2012)',
          items: [
            { text: '总览', link: '/algorithms/freak/' },
            { text: '论文精读', link: '/algorithms/freak/paper' },
            { text: '核心概念', link: '/algorithms/freak/concepts' },
            { text: '算法流程', link: '/algorithms/freak/architecture' },
            { text: '源码走读', link: '/algorithms/freak/source' },
            { text: '实战与踩坑', link: '/algorithms/freak/painpoints' },
            { text: '调参技巧', link: '/algorithms/freak/tricks' }
          ]
        },
        {
          text: '高效图分割 Felzenszwalb (2004)',
          items: [
            { text: '总览', link: '/algorithms/felzenszwalb-segmentation/' },
            { text: '论文精读', link: '/algorithms/felzenszwalb-segmentation/paper' },
            { text: '核心概念', link: '/algorithms/felzenszwalb-segmentation/concepts' },
            { text: '算法流程', link: '/algorithms/felzenszwalb-segmentation/architecture' },
            { text: '源码走读', link: '/algorithms/felzenszwalb-segmentation/source' },
            { text: '实战与踩坑', link: '/algorithms/felzenszwalb-segmentation/painpoints' },
            { text: '调参技巧', link: '/algorithms/felzenszwalb-segmentation/tricks' }
          ]
        },
        {
          text: 'KNN 背景建模 (2006)',
          items: [
            { text: '总览', link: '/algorithms/knn-background/' },
            { text: '论文精读', link: '/algorithms/knn-background/paper' },
            { text: '核心概念', link: '/algorithms/knn-background/concepts' },
            { text: '算法流程', link: '/algorithms/knn-background/architecture' },
            { text: '源码走读', link: '/algorithms/knn-background/source' },
            { text: '实战与踩坑', link: '/algorithms/knn-background/painpoints' },
            { text: '调参技巧', link: '/algorithms/knn-background/tricks' }
          ]
        },
        {
          text: 'ViBe 背景建模 (2011)',
          items: [
            { text: '总览', link: '/algorithms/vibe/' },
            { text: '论文精读', link: '/algorithms/vibe/paper' },
            { text: '核心概念', link: '/algorithms/vibe/concepts' },
            { text: '算法流程', link: '/algorithms/vibe/architecture' },
            { text: '源码走读', link: '/algorithms/vibe/source' },
            { text: '实战与踩坑', link: '/algorithms/vibe/painpoints' },
            { text: '调参技巧', link: '/algorithms/vibe/tricks' }
          ]
        },
        {
          text: 'MOSSE 相关滤波跟踪 (2010)',
          items: [
            { text: '总览', link: '/algorithms/mosse/' },
            { text: '论文精读', link: '/algorithms/mosse/paper' },
            { text: '核心概念', link: '/algorithms/mosse/concepts' },
            { text: '算法流程', link: '/algorithms/mosse/architecture' },
            { text: '源码走读', link: '/algorithms/mosse/source' },
            { text: '实战与踩坑', link: '/algorithms/mosse/painpoints' },
            { text: '调参技巧', link: '/algorithms/mosse/tricks' }
          ]
        },
        {
          text: 'FLANN 快速最近邻 (2009)',
          items: [
            { text: '总览', link: '/algorithms/flann/' },
            { text: '论文精读', link: '/algorithms/flann/paper' },
            { text: '核心概念', link: '/algorithms/flann/concepts' },
            { text: '算法流程', link: '/algorithms/flann/architecture' },
            { text: '源码走读', link: '/algorithms/flann/source' },
            { text: '实战与踩坑', link: '/algorithms/flann/painpoints' },
            { text: '调参技巧', link: '/algorithms/flann/tricks' }
          ]
        },
        {
          text: '本质矩阵与八点法 (1981)',
          items: [
            { text: '总览', link: '/algorithms/essential-matrix/' },
            { text: '论文精读', link: '/algorithms/essential-matrix/paper' },
            { text: '核心概念', link: '/algorithms/essential-matrix/concepts' },
            { text: '算法流程', link: '/algorithms/essential-matrix/architecture' },
            { text: '源码走读', link: '/algorithms/essential-matrix/source' },
            { text: '实战与踩坑', link: '/algorithms/essential-matrix/painpoints' },
            { text: '调参技巧', link: '/algorithms/essential-matrix/tricks' }
          ]
        },
        {
          text: '三角化重建 (1997)',
          items: [
            { text: '总览', link: '/algorithms/triangulation/' },
            { text: '论文精读', link: '/algorithms/triangulation/paper' },
            { text: '核心概念', link: '/algorithms/triangulation/concepts' },
            { text: '算法流程', link: '/algorithms/triangulation/architecture' },
            { text: '源码走读', link: '/algorithms/triangulation/source' },
            { text: '实战与踩坑', link: '/algorithms/triangulation/painpoints' },
            { text: '调参技巧', link: '/algorithms/triangulation/tricks' }
          ]
        },
        {
          text: '光束法平差 BA (1958)',
          items: [
            { text: '总览', link: '/algorithms/bundle-adjustment/' },
            { text: '论文精读', link: '/algorithms/bundle-adjustment/paper' },
            { text: '核心概念', link: '/algorithms/bundle-adjustment/concepts' },
            { text: '算法流程', link: '/algorithms/bundle-adjustment/architecture' },
            { text: '源码走读', link: '/algorithms/bundle-adjustment/source' },
            { text: '实战与踩坑', link: '/algorithms/bundle-adjustment/painpoints' },
            { text: '调参技巧', link: '/algorithms/bundle-adjustment/tricks' }
          ]
        },
        {
          text: 'Haar 小波变换 (1989)',
          items: [
            { text: '总览', link: '/algorithms/haar-wavelet/' },
            { text: '论文精读', link: '/algorithms/haar-wavelet/paper' },
            { text: '核心概念', link: '/algorithms/haar-wavelet/concepts' },
            { text: '算法流程', link: '/algorithms/haar-wavelet/architecture' },
            { text: '源码走读', link: '/algorithms/haar-wavelet/source' },
            { text: '实战与踩坑', link: '/algorithms/haar-wavelet/painpoints' },
            { text: '调参技巧', link: '/algorithms/haar-wavelet/tricks' }
          ]
        },
      ],
      '/versions/': [
        {
          text: '📦 经典算法版本',
          items: [{ text: '版本总览 / 对比大表', link: '/versions/' }]
        },
        {
          text: '图像处理',
          items: [
            { text: 'Sobel 边缘算子（已升级为完整档案）', link: '/algorithms/sobel/' },
            { text: 'Otsu 大津阈值（已升级为完整档案）', link: '/algorithms/otsu/' },
            { text: '霍夫变换·直线/圆检测（已升级为完整档案）', link: '/algorithms/hough/' },
            { text: '数学形态学（已升级为完整档案）', link: '/algorithms/morphology/' },
            { text: '双边滤波保边去噪（已升级为完整档案）', link: '/algorithms/bilateral/' },
            { text: 'CLAHE 自适应直方图均衡（已升级为完整档案）', link: '/algorithms/clahe/' },
            { text: '距离变换（已升级为完整档案）', link: '/algorithms/distance-transform/' },
            { text: '连通域分析 Two-Pass（已升级为完整档案）', link: '/algorithms/connected-components/' },
            { text: 'Gabor 纹理滤波（已升级为完整档案）', link: '/algorithms/gabor/' },
            { text: 'LBP 局部二值模式（已升级为完整档案）', link: '/algorithms/lbp/' },
            { text: '高斯滤波（已升级为完整档案）', link: '/algorithms/gaussian-blur/' },
            { text: '中值滤波（已升级为完整档案）', link: '/algorithms/median-filter/' },
            { text: 'Haar 小波变换（已升级为完整档案）', link: '/algorithms/haar-wavelet/' },
            { text: 'ViBe 背景建模（已升级为完整档案）', link: '/algorithms/vibe/' },
            { text: 'KNN 背景建模（已升级为完整档案）', link: '/algorithms/knn-background/' }
          ]
        },
        {
          text: '特征检测',
          items: [
            { text: 'SURF 加速特征（已升级为完整档案）', link: '/algorithms/surf/' },
            { text: 'ORB 实时特征（已升级为完整档案）', link: '/algorithms/orb/' },
            { text: 'FAST 高速角点（已升级为完整档案）', link: '/algorithms/fast/' },
            { text: 'Shi-Tomasi 好跟踪角点（已升级为完整档案）', link: '/algorithms/shi-tomasi/' },
            { text: 'MSER 极值区域（已升级为完整档案）', link: '/algorithms/mser/' },
            { text: 'BRISK 二进制尺度旋转不变特征（已升级为完整档案）', link: '/algorithms/brisk/' },
            { text: 'AKAZE 加速 KAZE 非线性特征（已升级为完整档案）', link: '/algorithms/akaze/' },
            { text: '霍夫圆变换（已升级为完整档案）', link: '/algorithms/hough-circles/' },
            { text: '轮廓拟合与多边形逼近（已升级为完整档案）', link: '/algorithms/contour-fitting/' },
            { text: 'FREAK 仿生二进制描述子（已升级为完整档案）', link: '/algorithms/freak/' }
          ]
        },
        {
          text: '特征匹配',
          items: [
            { text: '（已升级为完整档案，见上方「核心算法」）', link: '/algorithms/ransac/' },
            { text: 'BRIEF 二进制描述子（已升级为完整档案）', link: '/algorithms/brief/' },
            { text: '单应矩阵估计（已升级为完整档案）', link: '/algorithms/homography/' },
            { text: 'FLANN 快速最近邻搜索（已升级为完整档案）', link: '/algorithms/flann/' }
          ]
        },
        {
          text: '图像分割',
          items: [
            { text: '分水岭分割（已升级为完整档案）', link: '/algorithms/watershed/' },
            { text: 'K-Means 颜色聚类（已升级为完整档案）', link: '/algorithms/kmeans/' },
            { text: 'Mean Shift 均值漂移（已升级为完整档案）', link: '/algorithms/meanshift/' },
            { text: 'SLIC 超像素（已升级为完整档案）', link: '/algorithms/slic/' },
            { text: 'GrabCut 交互式抠图（已升级为完整档案）', link: '/algorithms/grabcut/' },
            { text: '区域生长分割（已升级为完整档案）', link: '/algorithms/region-growing/' },
            { text: 'Felzenszwalb 图分割（已升级为完整档案）', link: '/algorithms/felzenszwalb-segmentation/' }
          ]
        },
        {
          text: '目标检测',
          items: [
            { text: 'Viola-Jones 人脸检测（已升级为完整档案）', link: '/algorithms/viola-jones/' },
            { text: 'DPM 可变形部件（已升级为完整档案）', link: '/algorithms/dpm/' },
            { text: 'BoVW 词袋模型（已升级为完整档案）', link: '/algorithms/bovw/' },
            { text: 'CamShift 自适应跟踪（已升级为完整档案）', link: '/algorithms/camshift/' },
            { text: 'KCF 核相关滤波跟踪（已升级为完整档案）', link: '/algorithms/kcf/' },
            { text: 'CSRT 通道空间可靠性跟踪（已升级为完整档案）', link: '/algorithms/csrt/' },
            { text: 'MOSSE 相关滤波跟踪（已升级为完整档案）', link: '/algorithms/mosse/' }
          ]
        },
        {
          text: '几何视觉',
          items: [
            { text: '张氏相机标定（已升级为完整档案）', link: '/algorithms/zhang-calibration/' },
            { text: '对极几何与三角化（已升级为完整档案）', link: '/algorithms/epipolar-geometry/' },
            { text: 'SGBM 半全局立体匹配（已升级为完整档案）', link: '/algorithms/sgbm/' },
            { text: 'Horn-Schunck 稠密光流（已升级为完整档案）', link: '/algorithms/horn-schunck/' },
            { text: 'Farnebäck 稠密光流（已升级为完整档案）', link: '/algorithms/farneback/' },
            { text: 'EPnP 位姿估计（已升级为完整档案）', link: '/algorithms/pnpsolver/' },
            { text: 'ICP 点云配准（已升级为完整档案）', link: '/algorithms/icp/' },
            { text: 'MOG2 背景减除（已升级为完整档案）', link: '/algorithms/mog2/' },
            { text: '本质矩阵与八点法（已升级为完整档案）', link: '/algorithms/essential-matrix/' },
            { text: '三角化重建（已升级为完整档案）', link: '/algorithms/triangulation/' },
            { text: '光束法平差 BA（已升级为完整档案）', link: '/algorithms/bundle-adjustment/' },
            { text: 'Lucas-Kanade 稀疏光流（已升级为完整档案）', link: '/algorithms/lucas-kanade/' }
          ]
        }
      ],
      '/cases/': [
        {
          text: '实战案例',
          items: [
            { text: '案例总览', link: '/cases/' },
            { text: '工业零件缺陷检测', link: '/cases/industrial-defect' },
            { text: '嵌入式边缘部署', link: '/cases/edge-deployment' }
          ]
        }
      ],
      '/legacy/': [
        {
          text: '传承脉络',
          items: [
            { text: '传统 CV → 深度学习', link: '/legacy/' },
            { text: 'NMS 到 YOLO', link: '/legacy/nms-to-yolo' },
            { text: '图像金字塔到 FPN', link: '/legacy/pyramid-to-fpn' }
          ]
        }
      ],
      '/derivatives/': [
        {
          text: '🔀 衍生实现',
          items: [
            { text: '衍生总览（OpenCV/HALCON/嵌入式/现代继承）', link: '/derivatives/' },
            { text: '🚧 路线预告', link: '/derivatives/roadmap' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/' }
    ],

    search: {
      provider: 'local'
    },

    footer: {
      message: '传统计算机视觉本体论研究 · 论文 → 理论 → 实现 → 实战',
      copyright: '© 2026 agent-cv'
    },

    outline: {
      level: [2, 3],
      label: '本页目录'
    },

    docFooter: {
      prev: '上一篇',
      next: '下一篇'
    }
  }
})
