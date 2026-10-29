<template>
  <div class="ocv-root" :class="{ 'ocv-compact': compact }">
    <!-- 未启动：首屏点击按钮才开始加载，避免自动下载 3.5MB 的 opencv.js 拖慢首屏 / 堵并发队列 -->
    <div v-if="status === 'idle'" class="ocv-loading">
      <div style="font-size:40px;margin-bottom:8px;">🎮</div>
      <p class="ocv-status-text" style="font-weight:600;">真机实验 — 点击下方按钮启动</p>
      <p class="ocv-tip" style="margin:12px 0 20px;line-height:1.7;">
        OpenCV.js 源码约 11 MB（HTTP 传输自动 gzip 后约 3.5 MB），点击按钮后开始下载，在你本地浏览器用 WebAssembly 运行。<br/>
        首次启动需要几秒到几十秒（取决于到 GitHub Pages 的链路），之后浏览器会缓存，再次打开秒开。<br/>
        所有运算完全在你本地完成，<b>图片不会上传到任何服务器</b>。
      </p>
      <button class="ocv-retry-btn ocv-start-btn" @click="start">▶ 启动真机实验（加载 OpenCV.js）</button>
    </div>

    <!-- 加载中：简单 spinner + 阶段文字，不做任何进度条，交给浏览器自身加载 -->
    <div v-else-if="status === 'loading' || status === 'initializing'" class="ocv-loading">
      <div class="ocv-spinner"></div>
      <p class="ocv-status-text">{{ statusText }}</p>
      <p v-if="!compact" class="ocv-tip">
        OpenCV.js 约 3.5 MB（gzip 后），浏览器会直接走 HTTP 缓存。<br/>
        所有运算完全在你本地浏览器里完成（WebAssembly），图片/视频不会上传到任何服务器。<br/>
        如果持续转圈超过 30 秒，点下方「🔗 直链预热」单独打开一次再重试——你亲测那种方式秒开。
      </p>
      <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap;justify-content:center;">
        <button class="ocv-retry-btn" @click="cancelAndRetry" style="background:var(--vp-c-bg-soft);color:var(--vp-c-text-2);border:1px solid var(--vp-c-divider);">🔄 重试</button>
        <button class="ocv-retry-btn" @click="prewarm" style="background:var(--vp-c-bg-soft);color:var(--vp-c-text-2);border:1px solid var(--vp-c-divider);">🔗 直链预热（单独打开一次）</button>
      </div>
    </div>

    <!-- 加载失败 -->
    <div v-else-if="status === 'error'" class="ocv-loading">
      <div class="ocv-err-icon">⚠️</div>
      <p class="ocv-status-text">OpenCV.js 加载失败</p>
      <p class="ocv-hint">{{ errorMsg }}</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center;">
        <button class="ocv-retry-btn" @click="retry">🔄 重新加载</button>
        <button class="ocv-retry-btn" @click="prewarm" style="background:var(--vp-c-bg-soft);color:var(--vp-c-text-2);border:1px solid var(--vp-c-divider);">🔗 先直链预热</button>
      </div>
    </div>

    <template v-else>
      <!-- 顶部工具条 -->
      <div class="ocv-toolbar">
        <div class="ocv-tool-group">
          <label>示例图</label>
          <select v-model="currentSample" @change="loadSample">
            <option v-for="s in samples" :key="s.file" :value="s.file">{{ s.name }}</option>
          </select>
        </div>
        <div class="ocv-tool-group">
          <label class="ocv-upload">
            📂 上传图片
            <input type="file" accept="image/*" @change="onUpload" />
          </label>
        </div>
        <div class="ocv-tool-group" v-if="!embedAlgo">
          <label>算法</label>
          <select v-model="currentFilter" @change="onAlgoChange">
            <optgroup v-for="g in groups" :key="g" :label="g">
              <option v-for="f in filtersByGroup(g)" :key="f.id" :value="f.id">{{ f.name }}</option>
            </optgroup>
          </select>
        </div>
        <div class="ocv-tool-group">
          <button class="ocv-btn" @click="run">▶ 运行</button>
        </div>
        <div class="ocv-tool-group ocv-lang-group" v-if="!compact">
          <label>代码</label>
          <div class="ocv-lang-switch">
            <button v-for="l in languages" :key="l" :class="['ocv-lang-btn', { active: lang === l }]" @click="lang = l">{{ l }}</button>
          </div>
        </div>
      </div>

      <!-- 主体 -->
      <div class="ocv-main">
        <div class="ocv-panel">
          <div class="ocv-panel-title">原图</div>
          <canvas ref="srcCanvas" class="ocv-canvas"></canvas>
        </div>

        <div class="ocv-controls">
          <div class="ocv-panel-title">{{ activeFilter.name }}</div>
          <p class="ocv-desc">{{ activeFilter.desc }}</p>
          <div v-for="p in activeFilter.params" :key="p.key" class="ocv-param">
            <div class="ocv-param-head">
              <span>{{ p.label }}</span>
              <code>{{ paramValues[p.key] }}</code>
            </div>
            <input
              type="range"
              :min="p.min" :max="p.max" :step="p.step"
              v-model.number="paramValues[p.key]"
              @input="scheduleRun"
            />
          </div>
          <p v-if="!activeFilter.params.length" class="ocv-desc">该算法无可调参数</p>
          <div class="ocv-time" v-if="lastMs >= 0">⏱ 处理耗时：<b>{{ lastMs.toFixed(1) }} ms</b></div>
          <p v-if="runError" class="ocv-error">{{ runError }}</p>
          <div class="ocv-links" v-if="activeFilter.algoLink && !compact">
            <a :href="activeFilter.algoLink">📖 查看本算法完整原理档案 →</a>
          </div>
        </div>

        <div class="ocv-panel">
          <div class="ocv-panel-title">结果</div>
          <canvas ref="dstCanvas" class="ocv-canvas"></canvas>
        </div>
      </div>

      <!-- 代码面板 -->
      <div class="ocv-code-panel" v-if="!compact">
        <div class="ocv-code-head">
          <span>{{ lang }} 代码 — 与上方参数联动</span>
          <button class="ocv-copy-btn" @click="copyCode">📋 复制</button>
        </div>
        <pre class="ocv-code"><code>{{ currentCode }}</code></pre>
      </div>

      <p class="ocv-foot">
        全部运算在你的浏览器里用 <b>OpenCV.js（WebAssembly）</b> 实时完成，不上传任何图片到服务器——所以本站可以纯静态部署在 GitHub Pages 上。
        <span v-if="activeFilter.algoLink">｜ 📖 <a :href="activeFilter.algoLink">查看本算法原理档案</a></span>
      </p>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'

const props = defineProps({
  initialAlgo: { type: String, default: '' },  // 嵌入到算法页时，指定默认算法
  compact:     { type: Boolean, default: false }, // 紧凑嵌入模式（隐藏代码面板）
})

const BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.BASE_URL) || '/'
const OCV_URL = BASE + 'lib/opencv.js'
const HAAR_XML_URL = BASE + 'lib/haarcascade_frontalface_default.xml'
const SAMPLE_BASE = BASE + 'samples/'

const samples = [
  { file: 'scene.png',      name: '彩色色块（分割 / 聚类）' },
  { file: 'fruits.png',     name: '彩色水果（K-Means / GrabCut）' },
  { file: 'street.png',     name: '街景建筑（特征匹配 / 单应校正）' },
  { file: 'face.png',       name: '合成人脸（人脸检测）' },
  { file: 'pedestrian.png', name: '行人剪影（HOG/行人检测）' },
  { file: 'chessboard.png', name: '棋盘格（角点 / 相机标定）' },
  { file: 'coins.png',      name: '硬币圆点（霍夫圆 / 连通域）' },
  { file: 'shapes.png',     name: '黑白形状（轮廓 / 拟合）' },
  { file: 'edges.png',      name: '几何线条（边缘 / 霍夫直线）' },
  { file: 'noisy.png',      name: '椒盐噪声（滤波去噪）' },
  { file: 'doc.png',        name: '文档条码（阈值 / 形态学）' },
  { file: 'tex.png',        name: '纹理砖块（纹理 / LBP / Gabor）' },
  { file: 'frame1.png',     name: '连续帧·第1帧（光流）' },
]

// 算法 id → 算法档案页路径（用于「去原理页」跳转锚定）
const ALGO_LINK = {
  grayscale: '/chapters/ch03-preprocessing',
  gaussian: '/algorithms/gaussian-blur/',
  median: '/algorithms/median-filter/',
  bilateral: '/algorithms/bilateral/',
  equalize: '/chapters/ch03-preprocessing',
  clahe: '/algorithms/clahe/',
  filter2d: '/algorithms/sobel/',
  sobel: '/algorithms/sobel/',
  laplacian: '/algorithms/sobel/',
  canny: '/algorithms/canny/',
  threshold: '/algorithms/otsu/',
  adaptivethresh: '/algorithms/otsu/',
  morphology: '/algorithms/morphology/',
  houghlines: '/algorithms/hough/',
  houghcircles: '/algorithms/hough-circles/',
  harris: '/algorithms/harris/',
  gftt: '/algorithms/shi-tomasi/',
  fast: '/algorithms/fast/',
  orb: '/algorithms/orb/',
  brisk: '/algorithms/brisk/',
  akaze: '/algorithms/akaze/',
  mser: '/algorithms/mser/',
  blob: '/algorithms/mser/',
  contours: '/algorithms/contour-fitting/',
  kmeans: '/algorithms/kmeans/',
  inrange: '/algorithms/kmeans/',
  distance: '/algorithms/distance-transform/',
  connected: '/algorithms/connected-components/',
  watershed: '/algorithms/watershed/',
  template: '/chapters/ch13-matching',
  bfmatch: '/algorithms/orb/',
  homography: '/algorithms/homography/',
  lkflow: '/algorithms/lucas-kanade/',
  'gradient-flow': '/algorithms/farneback/',
  'sobel-hog': '/algorithms/hog-svm/',
  gabor: '/algorithms/gabor/',
  lbp: '/algorithms/lbp/',
  haarwavelet: '/algorithms/haar-wavelet/',
  facedetect: '/algorithms/viola-jones/',
}

/* ---------------- 算法注册表 ---------------- */
/* 每个算法：id/name/group/desc/params/run(srcRGBA,p)->Mat(RGBA) ；code: 以 {param} 形式嵌入当前参数 */
function gray2rgba(g) { const d = new cv.Mat(); cv.cvtColor(g, d, cv.COLOR_GRAY2RGBA); g.delete(); return d }
// 创建指定类型的空 Mat（避免 new cv.Mat() 默认 8UC1 被要求 CV_32F 的算法写入越界）
function mat32f(rows, cols) {
  if (rows && cols) return new cv.Mat(rows, cols, cv.CV_32FC1)
  return new cv.Mat()  // 让 opencv 自己分配尺寸（典型：distanceTransform / cornerHarris 会 resize 到输入尺寸）
}

const filters = [
  // —— 图像预处理 ——
  {
    id: 'grayscale', name: '灰度化', group: '图像预处理',
    desc: '把彩色图转成灰度图，是绝大多数算法第一步。',
    params: [],
    run: (s) => { const d = new cv.Mat(); cv.cvtColor(s, d, cv.COLOR_RGBA2GRAY); return gray2rgba(d) },
    codePy: 'img = cv.imread("image.jpg")\ngray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)',
    codeCpp: 'Mat img = imread("image.jpg");\nMat gray;\ncvtColor(img, gray, COLOR_BGR2GRAY);',
    codeJs:  'let src = cv.imread("canvas");\nlet gray = new cv.Mat();\ncv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);',
  },
  {
    id: 'gaussian', name: '高斯滤波', group: '图像预处理',
    desc: '按钟形权重加权平均去噪，可分离卷积提速。',
    params: [
      { key: 'ksize', label: '核大小 ksize', min: 1, max: 21, step: 2, value: 5 },
      { key: 'sigma', label: 'σ 标准差', min: 0, max: 6, step: 0.5, value: 0 },
    ],
    run: (s, p) => { const d = new cv.Mat(); cv.GaussianBlur(s, d, new cv.Size(p.ksize, p.ksize), p.sigma, p.sigma); return d },
    codePy: (p) => `blur = cv.GaussianBlur(img, ksize=(${p.ksize},${p.ksize}), sigmaX=${p.sigma})`,
    codeCpp: (p) => `GaussianBlur(img, dst, Size(${p.ksize},${p.ksize}), ${p.sigma}, ${p.sigma});`,
    codeJs:  (p) => `cv.GaussianBlur(src, dst, new cv.Size(${p.ksize},${p.ksize}), ${p.sigma}, ${p.sigma});`,
  },
  {
    id: 'median', name: '中值滤波', group: '图像预处理',
    desc: '邻域取中位数，椒盐噪声的克星。',
    params: [{ key: 'ksize', label: '核大小 ksize', min: 3, max: 15, step: 2, value: 3 }],
    run: (s, p) => { const d = new cv.Mat(); cv.medianBlur(s, d, p.ksize); return d },
    codePy: (p) => `dst = cv.medianBlur(img, ksize=${p.ksize})`,
    codeCpp: (p) => `medianBlur(img, dst, ${p.ksize});`,
    codeJs:  (p) => `cv.medianBlur(src, dst, ${p.ksize});`,
  },
  {
    id: 'bilateral', name: '双边滤波', group: '图像预处理',
    desc: '保边去噪：颜色近且位置近才参与平均。',
    params: [
      { key: 'd', label: '邻域直径 d', min: 3, max: 15, step: 2, value: 9 },
      { key: 'sigmaColor', label: '颜色 σ', min: 10, max: 200, step: 10, value: 75 },
      { key: 'sigmaSpace', label: '空间 σ', min: 10, max: 200, step: 10, value: 75 },
    ],
    run: (s, p) => { const d = new cv.Mat(); cv.bilateralFilter(s, d, p.d, p.sigmaColor, p.sigmaSpace, cv.BORDER_DEFAULT); return d },
    codePy: (p) => `dst = cv.bilateralFilter(img, d=${p.d}, sigmaColor=${p.sigmaColor}, sigmaSpace=${p.sigmaSpace})`,
    codeCpp: (p) => `bilateralFilter(img, dst, ${p.d}, ${p.sigmaColor}, ${p.sigmaSpace});`,
    codeJs:  (p) => `cv.bilateralFilter(src, dst, ${p.d}, ${p.sigmaColor}, ${p.sigmaSpace});`,
  },
  {
    id: 'equalize', name: '直方图均衡化', group: '图像预处理',
    desc: '拉伸灰度分布，提升整体对比度。',
    params: [],
    run: (s) => { const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const e = new cv.Mat(); cv.equalizeHist(g, e); g.delete(); return gray2rgba(e) },
    codePy: 'gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)\neq = cv.equalizeHist(gray)',
    codeCpp: 'cvtColor(img, gray, COLOR_BGR2GRAY);\nequalizeHist(gray, dst);',
    codeJs:  'cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);\ncv.equalizeHist(gray, dst);',
  },
  {
    id: 'clahe', name: 'CLAHE 限制对比度自适应均衡', group: '图像预处理',
    desc: '分块均衡并裁剪过强对比度，适合医学图像/逆光。',
    params: [
      { key: 'clipLimit', label: '裁剪上限', min: 1, max: 20, step: 1, value: 2 },
      { key: 'tileGrid', label: '网格边长', min: 2, max: 16, step: 2, value: 8 },
    ],
    run: (s, p) => { const g=new cv.Mat(); cv.cvtColor(s,g,cv.COLOR_RGBA2GRAY); const c=new cv.CLAHE(p.clipLimit,new cv.Size(p.tileGrid,p.tileGrid)); const d=new cv.Mat(); c.apply(g,d); c.delete(); g.delete(); return gray2rgba(d) },
    codePy: (p) => `clahe = cv.createCLAHE(clipLimit=${p.clipLimit}, tileGridSize=(${p.tileGrid},${p.tileGrid}))\ndst = clahe.apply(gray)`,
    codeCpp: (p) => `Ptr<CLAHE> c = createCLAHE(${p.clipLimit}, Size(${p.tileGrid},${p.tileGrid}));\nc->apply(gray, dst);`,
    codeJs:  (p) => `let c = new cv.CLAHE(${p.clipLimit}, new cv.Size(${p.tileGrid},${p.tileGrid}));\nc.apply(gray, dst); c.delete();`,
  },
  {
    id: 'filter2d', name: '锐化滤波 (filter2D)', group: '图像预处理',
    desc: '自定义卷积核做锐化，突出细节。',
    params: [{ key: 'alpha', label: '锐化强度', min: 0, max: 5, step: 1, value: 1 }],
    run: (s, p) => {
      const d = new cv.Mat()
      const a = p.alpha
      const kernel = cv.matFromArray(3, 3, cv.CV_32F, [0, -a, 0, -a, 1 + 4 * a, -a, 0, -a, 0])
      cv.filter2D(s, d, cv.CV_8U, kernel); kernel.delete(); return d
    },
    codePy: (p) => `kernel = np.array([[0,-${p.alpha},0],[-${p.alpha},${1+4*p.alpha},-${p.alpha}],[0,-${p.alpha},0]], np.float32)\ndst = cv.filter2D(img, -1, kernel)`,
    codeCpp: (p) => `Mat k = (Mat_<float>(3,3)<<0,-${p.alpha},0,-${p.alpha},${1+4*p.alpha},-${p.alpha},0,-${p.alpha},0);\nfilter2D(img, dst, -1, k);`,
    codeJs:  (p) => `let k = cv.matFromArray(3,3, cv.CV_32F, [0,-${p.alpha},0,-${p.alpha},${1+4*p.alpha},-${p.alpha},0,-${p.alpha},0]);\ncv.filter2D(src, dst, cv.CV_8U, k); k.delete();`,
  },
  {
    id: 'gabor', name: 'Gabor 纹理滤波', group: '图像预处理',
    desc: '方向/频率敏感的卷积核，常用于纹理与指纹增强。',
    params: [
      { key: 'ksize', label: '核大小', min: 5, max: 31, step: 2, value: 15 },
      { key: 'theta', label: '方向 θ (度)', min: 0, max: 180, step: 15, value: 0 },
      { key: 'sigma', label: 'σ', min: 1, max: 10, step: 1, value: 4 },
      { key: 'lambd', label: '波长 λ', min: 4, max: 20, step: 1, value: 10 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      // cv.getGaborKernel 在当前 opencv.js 构建中不可用，用 JS 手写
      const k = p.ksize, sig = p.sigma, th = p.theta * Math.PI/180, lm = p.lambd, gm = 0.5, ps = 0
      const half = Math.floor(k/2)
      const data = new Float32Array(k*k)
      for (let y=-half, yi=0; yi<k; y++, yi++)
        for (let x=-half, xi=0; xi<k; x++, xi++) {
          const x_ = x*Math.cos(th)+y*Math.sin(th), y_=-x*Math.sin(th)+y*Math.cos(th)
          const env = Math.exp(-(x_*x_+gm*gm*y_*y_)/(2*sig*sig))
          data[yi*k+xi] = env*Math.cos(2*Math.PI*x_/lm+ps)
        }
      const kernel = cv.matFromArray(k, k, cv.CV_32F, data)
      const d = new cv.Mat(); cv.filter2D(g, d, cv.CV_32F, kernel); const a = new cv.Mat(); cv.convertScaleAbs(d, a)
      kernel.delete(); g.delete(); d.delete(); return gray2rgba(a)
    },
    codePy: (p) => `kernel = cv.getGaborKernel((${p.ksize},${p.ksize}), sigma=${p.sigma}, theta=np.radians(${p.theta}), lambd=${p.lambd}, gamma=0.5)\ndst = cv.filter2D(img, cv.CV_8UC3, kernel)`,
    codeCpp: (p) => `Mat k = getGaborKernel(Size(${p.ksize},${p.ksize}), ${p.sigma}, ${(p.theta*Math.PI/180).toFixed(2)}, ${p.lambd}, 0.5);\nfilter2D(img, dst, CV_8UC3, k);`,
    codeJs:  (p) => `// 注：当前 opencv.js 未暴露 getGaborKernel，建议使用 filter2D + 手写核\nlet k = cv.matFromArray(${p.ksize},${p.ksize}, cv.CV_32F, /*...*/);\ncv.filter2D(src, dst, cv.CV_8U, k);`,
  },
  {
    id: 'lbp', name: 'LBP 局部二值模式', group: '图像预处理',
    desc: '每个像素与 8 邻域比较得 8 位二值码，纹理的基础描述子。',
    params: [],
    run: (s) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const out = new cv.Mat.zeros(g.rows, g.cols, cv.CV_8UC1)
      const d1 = g.data, d2 = out.data
      const w = g.cols, h = g.rows
      for (let y=1; y<h-1; y++) for (let x=1; x<w-1; x++) {
        const c = d1[y*w+x], code =
          ((d1[(y-1)*w+x-1]>c)<<7)|((d1[(y-1)*w+x]>c)<<6)|((d1[(y-1)*w+x+1]>c)<<5)|
          ((d1[y*w+x+1]>c)<<4)|((d1[(y+1)*w+x+1]>c)<<3)|((d1[(y+1)*w+x]>c)<<2)|
          ((d1[(y+1)*w+x-1]>c)<<1)|(d1[y*w+x-1]>c?1:0)
        d2[y*w+x] = code
      }
      g.delete(); return gray2rgba(out)
    },
    codePy: `def lbp(img):
    h, w = img.shape
    out = np.zeros((h,w), np.uint8)
    for y in range(1,h-1):
        for x in range(1,w-1):
            c = img[y,x]
            bits = [img[y-1,x-1]>c,img[y-1,x]>c,img[y-1,x+1]>c,
                    img[y,x+1]>c,img[y+1,x+1]>c,img[y+1,x]>c,
                    img[y+1,x-1]>c,img[y,x-1]>c]
            out[y,x] = sum(b<<(7-i) for i,b in enumerate(bits))
    return out`,
    codeCpp: `// 三层嵌套循环，对每个像素比对 8 邻域得到 8-bit 码。\nfor (int y=1; y<g.rows-1; y++)\n  for (int x=1; x<g.cols-1; x++) { /* bit comparisons */ }`,
    codeJs:  `// 同上：三层循环 + 8 邻域比较，得到 0~255 的 LBP 码`,
  },
  {
    id: 'haarwavelet', name: 'Haar 小波一级分解', group: '图像预处理',
    desc: '按 2×2 块拆分出 LL/LH/HL/HH 四个子带，频域入门。',
    params: [],
    run: (s) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const f = new cv.Mat(); g.convertTo(f, cv.CV_32F)
      const w=f.cols, h=f.rows, hh=h>>1, ww=w>>1
      const ll=new cv.Mat(),lh=new cv.Mat(),hl=new cv.Mat(),hh2=new cv.Mat()
      cv.resize(f, f, new cv.Size(ww*2, hh*2))
      // 用 2x2 box 粗近似 + 差分；为了可视化拼 2x2
      const out = new cv.Mat.zeros(h, w, cv.CV_8U)
      const sd=f.data32F, od=out.data
      for (let y=0;y<hh;y++) for (let x=0;x<ww;x++){
        const a=sd[(2*y)*w+2*x], b=sd[(2*y)*w+2*x+1], c=sd[(2*y+1)*w+2*x], d=sd[(2*y+1)*w+2*x+1]
        const A=(a+b+c+d)*0.25, H=(a-b+c-d)*0.25+128, V=(a+b-c-d)*0.25+128, D=(a-b-c+d)*0.25+128
        od[y*w+x] = Math.max(0,Math.min(255,A))
        od[y*w+x+ww] = Math.max(0,Math.min(255,H))
        od[(y+hh)*w+x] = Math.max(0,Math.min(255,V))
        od[(y+hh)*w+x+ww] = Math.max(0,Math.min(255,D))
      }
      f.delete(); ll.delete(); lh.delete(); hl.delete(); hh2.delete(); return gray2rgba(out)
    },
    codePy: `# Haar 一级分解：将图像 2x2 分块
LL = (img[0::2,0::2]+img[0::2,1::2]+img[1::2,0::2]+img[1::2,1::2])/4
LH = (img[0::2,0::2]-img[0::2,1::2]+img[1::2,0::2]-img[1::2,1::2])/4 + 128
HL = (img[0::2,0::2]+img[0::2,1::2]-img[1::2,0::2]-img[1::2,1::2])/4 + 128
HH = (img[0::2,0::2]-img[0::2,1::2]-img[1::2,0::2]+img[1::2,1::2])/4 + 128`,
    codeCpp: '// 2x2 像素块求均值和差，得到 LL/LH/HL/HH 四子带',
    codeJs:  '// 与 Python 版等价：逐 2x2 块做均值/差分',
  },
  // —— 边缘与基元 ——
  {
    id: 'sobel', name: 'Sobel 梯度', group: '边缘与基元',
    desc: '一阶差分算水平/垂直梯度，边缘定位的基础。',
    params: [{ key: 'ksize', label: '核大小', min: 1, max: 7, step: 2, value: 3 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const gx = new cv.Mat(), gy = new cv.Mat(), abs = new cv.Mat()
      cv.Sobel(g, gx, cv.CV_16S, 1, 0, p.ksize); cv.Sobel(g, gy, cv.CV_16S, 0, 1, p.ksize)
      cv.convertScaleAbs(gx, gx); cv.convertScaleAbs(gy, gy)
      cv.addWeighted(gx, 0.5, gy, 0.5, 0, abs)
      g.delete(); gx.delete(); gy.delete(); return gray2rgba(abs)
    },
    codePy: (p) => `gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)\ngx = cv.Sobel(gray, cv.CV_16S, 1, 0, ksize=${p.ksize})\ngy = cv.Sobel(gray, cv.CV_16S, 0, 1, ksize=${p.ksize})\nabs_gx = cv.convertScaleAbs(gx)\nabs_gy = cv.convertScaleAbs(gy)\ndst = cv.addWeighted(abs_gx, 0.5, abs_gy, 0.5, 0)`,
    codeCpp: (p) => `Sobel(gray, gx, CV_16S, 1, 0, ${p.ksize});\nSobel(gray, gy, CV_16S, 0, 1, ${p.ksize});\nconvertScaleAbs(gx, ax); convertScaleAbs(gy, ay);\naddWeighted(ax, 0.5, ay, 0.5, 0, dst);`,
    codeJs:  (p) => `cv.Sobel(gray, gx, cv.CV_16S, 1, 0, ${p.ksize});\ncv.Sobel(gray, gy, cv.CV_16S, 0, 1, ${p.ksize});\ncv.convertScaleAbs(gx, gx); cv.convertScaleAbs(gy, gy);\ncv.addWeighted(gx, 0.5, gy, 0.5, 0, dst);`,
  },
  {
    id: 'laplacian', name: 'Laplacian 拉普拉斯', group: '边缘与基元',
    desc: '二阶导数，对细节和噪声都敏感。',
    params: [{ key: 'ksize', label: '核大小', min: 1, max: 7, step: 2, value: 3 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const d = new cv.Mat(); cv.Laplacian(g, d, cv.CV_16S, p.ksize, 1, 0, cv.BORDER_DEFAULT)
      const a = new cv.Mat(); cv.convertScaleAbs(d, a); g.delete(); d.delete(); return gray2rgba(a)
    },
    codePy: (p) => `gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)\ndst = cv.Laplacian(gray, cv.CV_16S, ksize=${p.ksize})\ndst = cv.convertScaleAbs(dst)`,
    codeCpp: (p) => `Laplacian(gray, dst, CV_16S, ${p.ksize});\nconvertScaleAbs(dst, dst);`,
    codeJs:  (p) => `cv.Laplacian(gray, dst, cv.CV_16S, ${p.ksize});\ncv.convertScaleAbs(dst, dst);`,
  },
  {
    id: 'canny', name: 'Canny 边缘检测', group: '边缘与基元',
    desc: '经典多阶段边缘检测：去噪→梯度→非极大抑制→双阈值+连接。',
    params: [
      { key: 't1', label: '低阈值', min: 0, max: 300, step: 5, value: 50 },
      { key: 't2', label: '高阈值', min: 0, max: 500, step: 5, value: 150 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const d = new cv.Mat(); cv.Canny(g, d, p.t1, p.t2); g.delete(); return gray2rgba(d)
    },
    codePy: (p) => `gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)\nblur = cv.GaussianBlur(gray, (5,5), 0)\nedges = cv.Canny(blur, ${p.t1}, ${p.t2})`,
    codeCpp: (p) => `Canny(blur, edges, ${p.t1}, ${p.t2});`,
    codeJs:  (p) => `cv.Canny(gray, edges, ${p.t1}, ${p.t2});`,
  },
  {
    id: 'threshold', name: '阈值二值化 / Otsu', group: '边缘与基元',
    desc: '阈值一刀切；Otsu 自动找阈值（双峰直方图最准）。',
    params: [
      { key: 'thresh', label: '阈值 T（Otsu=0）', min: 0, max: 255, step: 1, value: 0 },
      { key: 'useOtsu', label: '使用 Otsu 自动阈值', min: 0, max: 1, step: 1, value: 1 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const d = new cv.Mat()
      const type = p.useOtsu ? cv.THRESH_BINARY | cv.THRESH_OTSU : cv.THRESH_BINARY
      cv.threshold(g, d, p.thresh, 255, type); g.delete(); return gray2rgba(d)
    },
    codePy: (p) => `gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)\n${p.useOtsu ? 'T, dst = cv.threshold(gray, 0, 255, cv.THRESH_BINARY|cv.THRESH_OTSU)  # 自动阈值' : `_, dst = cv.threshold(gray, ${p.thresh}, 255, cv.THRESH_BINARY)`}`,
    codeCpp: (p) => p.useOtsu ? 'threshold(gray, dst, 0, 255, THRESH_BINARY | THRESH_OTSU);' : `threshold(gray, dst, ${p.thresh}, 255, THRESH_BINARY);`,
    codeJs:  (p) => p.useOtsu ? 'cv.threshold(gray, dst, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU);' : `cv.threshold(gray, dst, ${p.thresh}, 255, cv.THRESH_BINARY);`,
  },
  {
    id: 'adaptivethresh', name: '自适应阈值', group: '边缘与基元',
    desc: '每个像素邻域内单独找阈值，应对光照不均。',
    params: [{ key: 'block', label: '邻域边长', min: 3, max: 31, step: 2, value: 11 }, { key: 'C', label: '常数 C', min: -20, max: 20, step: 1, value: 2 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const d = new cv.Mat()
      cv.adaptiveThreshold(g, d, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, p.block, p.C)
      g.delete(); return gray2rgba(d)
    },
    codePy: (p) => `dst = cv.adaptiveThreshold(gray, 255,\n    cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,\n    blockSize=${p.block}, C=${p.C})`,
    codeCpp: (p) => `adaptiveThreshold(gray, dst, 255, ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY, ${p.block}, ${p.C});`,
    codeJs:  (p) => `cv.adaptiveThreshold(gray, dst, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, ${p.block}, ${p.C});`,
  },
  {
    id: 'morphology', name: '形态学（腐蚀/膨胀/开/闭）', group: '边缘与基元',
    desc: '用结构元"啃掉毛刺/填平小洞"，是阈值后清洁必备。',
    params: [
      { key: 'op', label: '操作：0=腐蚀 1=膨胀 2=开 3=闭', min: 0, max: 3, step: 1, value: 2 },
      { key: 'k', label: '结构元大小', min: 1, max: 15, step: 2, value: 5 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const bi = new cv.Mat()
      cv.threshold(g, bi, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
      const k = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(p.k, p.k))
      const d = new cv.Mat()
      const opMap = [cv.MORPH_ERODE, cv.MORPH_DILATE, cv.MORPH_OPEN, cv.MORPH_CLOSE]
      cv.morphologyEx(bi, d, opMap[p.op], k); k.delete(); g.delete(); bi.delete(); return gray2rgba(d)
    },
    codePy: (p) => { const n=['cv.MORPH_ERODE','cv.MORPH_DILATE','cv.MORPH_OPEN','cv.MORPH_CLOSE'][p.op]; return `kernel = cv.getStructuringElement(cv.MORPH_RECT, (${p.k},${p.k}))\ndst = cv.morphologyEx(binary, ${n}, kernel)` },
    codeCpp: (p) => { const n=['MORPH_ERODE','MORPH_DILATE','MORPH_OPEN','MORPH_CLOSE'][p.op]; return `Mat k = getStructuringElement(MORPH_RECT, Size(${p.k},${p.k}));\nmorphologyEx(bin, dst, ${n}, k);` },
    codeJs:  (p) => { const n=['cv.MORPH_ERODE','cv.MORPH_DILATE','cv.MORPH_OPEN','cv.MORPH_CLOSE'][p.op]; return `let k = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(${p.k},${p.k}));\ncv.morphologyEx(bin, dst, ${n}, k); k.delete();` },
  },
  {
    id: 'houghlines', name: '霍夫直线检测', group: '边缘与基元',
    desc: '参数空间投票找直线，ρ-θ 累积器峰值即直线。',
    params: [
      { key: 'threshold', label: '投票阈值', min: 20, max: 300, step: 10, value: 100 },
      { key: 'minLineLength', label: '最短线段长', min: 10, max: 200, step: 5, value: 50 },
      { key: 'maxLineGap', label: '最大允许缝隙', min: 1, max: 30, step: 1, value: 10 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const d = s.clone(); const edges = new cv.Mat()
      cv.Canny(g, edges, 50, 150, 3)
      const lines = new cv.Mat()
      cv.HoughLinesP(edges, lines, 1, Math.PI/180, p.threshold, p.minLineLength, p.maxLineGap)
      // HoughLinesP 返回 (N,1) CV_32SC4：每行一条线、4 个 int32（x1,y1,x2,y2）
      const n = lines.rows
      const ldata = lines.data32S
      for (let i=0; i<n; i++) {
        const x1=ldata[i*4], y1=ldata[i*4+1], x2=ldata[i*4+2], y2=ldata[i*4+3]
        cv.line(d, new cv.Point(x1,y1), new cv.Point(x2,y2), [255,0,0,255], 2)
      }
      g.delete(); edges.delete(); lines.delete(); return d
    },
    codePy: (p) => `edges = cv.Canny(gray, 50, 150)\nlines = cv.HoughLinesP(edges, 1, np.pi/180,\n    threshold=${p.threshold}, minLineLength=${p.minLineLength}, maxLineGap=${p.maxLineGap})\nfor x1,y1,x2,y2 in lines:\n    cv.line(img, (x1,y1), (x2,y2), (0,0,255), 2)`,
    codeCpp: (p) => `vector<Vec4i> lines;\nHoughLinesP(edges, lines, 1, CV_PI/180, ${p.threshold}, ${p.minLineLength}, ${p.maxLineGap});\nfor (auto& l: lines) line(img, Point(l[0],l[1]), Point(l[2],l[3]), Scalar(0,0,255),2);`,
    codeJs:  (p) => `let lines = new cv.Mat();\ncv.HoughLinesP(edges, lines, 1, Math.PI/180, ${p.threshold}, ${p.minLineLength}, ${p.maxLineGap});\n// 遍历 lines.data32S 画线段`,
  },
  {
    id: 'houghcircles', name: '霍夫圆检测', group: '边缘与基元',
    desc: '三维参数空间(x,y,r)投票找圆。',
    params: [
      { key: 'dp', label: '累加器分辨率比 dp*10', min: 10, max: 30, step: 2, value: 12 },
      { key: 'minDist', label: '最小圆心距', min: 10, max: 200, step: 5, value: 40 },
      { key: 'param2', label: '投票阈值', min: 10, max: 150, step: 5, value: 50 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const d = s.clone()
      // 霍夫圆要求输入 8UC1，先 blur 一下减少误检
      const gblur = new cv.Mat(); cv.GaussianBlur(g, gblur, new cv.Size(9,9), 2, 2)
      const circles = new cv.Mat()
      cv.HoughCircles(gblur, circles, cv.HOUGH_GRADIENT, p.dp/10, p.minDist, 100, p.param2, 0, 0)
      // HoughCircles 返回 shape=(1, N, 3) 即 1 行 N 列、每列 3 通道 float32，用 data32F 扁平化
      // 注意：circles 在 opencv.js 里 col 数就是圆的数量，每个圆 3 个 float
      const nCircles = circles.cols || 0
      const cdata = circles.data32F
      for (let i=0; i<nCircles; i++){
        const x = cdata[i*3], y = cdata[i*3+1], r = cdata[i*3+2]
        if (r>0 && r < Math.max(d.cols,d.rows)) {
          cv.circle(d, new cv.Point(x,y), r|0, [0,255,0,255], 2)
          cv.circle(d, new cv.Point(x,y), 2, [0,0,255,255], 3)
        }
      }
      g.delete(); gblur.delete(); circles.delete(); return d
    },
    codePy: (p) => `circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, dp=${(p.dp/10).toFixed(1)}, minDist=${p.minDist},\n    param1=100, param2=${p.param2})\nfor x,y,r in circles[0]:\n    cv.circle(img, (x,y), int(r), (0,255,0), 2)`,
    codeCpp: (p) => `vector<Vec3f> circles;\nHoughCircles(gray, circles, HOUGH_GRADIENT, ${(p.dp/10).toFixed(1)}, ${p.minDist}, 100, ${p.param2});`,
    codeJs:  (p) => `let circles = new cv.Mat();\ncv.HoughCircles(gray, circles, cv.HOUGH_GRADIENT, ${(p.dp/10).toFixed(1)}, ${p.minDist}, 100, ${p.param2}, 0, 0);`,
  },
  {
    id: 'harris', name: 'Harris 角点', group: '边缘与基元',
    desc: '看窗口沿任意方向移动是否都变化剧烈——是，就是角点。',
    params: [{ key: 'blockSize', label: '邻域大小(必须奇数)', min: 3, max: 11, step: 2, value: 3 }, { key: 'k', label: 'Harris k (x100)', min: 2, max: 10, step: 1, value: 4 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const d = s.clone()
      // cornerHarris 要求 dst 必须是 CV_32FC1；blockSize 必须是奇数；ksize(Sobel) 必须是奇数
      const bs = (p.blockSize % 2 === 0) ? p.blockSize+1 : p.blockSize
      const dst = mat32f(g.rows, g.cols)
      cv.cornerHarris(g, dst, bs, 3, p.k/100, cv.BORDER_DEFAULT)
      const dstN = new cv.Mat(); cv.normalize(dst, dstN, 0, 255, cv.NORM_MINMAX); cv.convertScaleAbs(dstN, dstN)
      // 用 data 数组访问（ucharAt 在某些 opencv.js 版本不稳定）
      const data = dstN.data
      const w = d.cols
      for (let i=0; i<data.length; i++) {
        if (data[i] > 130) {
          const y = (i / w) | 0, x = i % w
          cv.circle(d, new cv.Point(x,y), 2, [255,0,0,255], -1)
        }
      }
      g.delete(); dst.delete(); dstN.delete(); return d
    },
    codePy: (p) => `dst = cv.cornerHarris(gray, blockSize=${p.blockSize}, ksize=3, k=${p.k/100})\ndst = cv.dilate(dst, None)\nimg[dst > 0.01*dst.max()] = [0,0,255]`,
    codeCpp: (p) => `cornerHarris(gray, dst, ${p.blockSize}, 3, ${p.k/100});`,
    codeJs:  (p) => `cv.cornerHarris(gray, dst, ${p.blockSize}, 3, ${p.k/100});`,
  },
  {
    id: 'gftt', name: 'Shi-Tomasi 角点 (GFTT)', group: '边缘与基元',
    desc: 'Harris 的改进：用 λ₁,λ₂ 中较小者判角点，跟踪效果更稳。',
    params: [{ key: 'maxCorners', label: '最多点数', min: 10, max: 500, step: 10, value: 100 }, { key: 'quality', label: '质量水平(x100)', min: 1, max: 20, step: 1, value: 1 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const d = s.clone(); const corners = new cv.Mat()
      cv.goodFeaturesToTrack(g, corners, p.maxCorners, p.quality/100, 10)
      // goodFeaturesToTrack 返回 (N,1) CV_32FC2 —— 共 N 个点，每点 x,y 两个 float32
      const nPts = corners.rows
      const cdata = corners.data32F
      for (let i=0; i<nPts; i++){
        const x = cdata[i*2], y = cdata[i*2+1]
        cv.circle(d, new cv.Point(x,y), 3, [0,255,0,255], -1)
      }
      g.delete(); corners.delete(); return d
    },
    codePy: (p) => `corners = cv.goodFeaturesToTrack(gray,\n    maxCorners=${p.maxCorners}, qualityLevel=${p.quality/100}, minDistance=10)\nfor pt in corners:\n    x,y = pt.ravel()\n    cv.circle(img, (int(x),int(y)), 3, (0,255,0), -1)`,
    codeCpp: (p) => `vector<Point2f> corners;\ngoodFeaturesToTrack(gray, corners, ${p.maxCorners}, ${p.quality/100}, 10);`,
    codeJs:  (p) => `let corners = new cv.Mat();\ncv.goodFeaturesToTrack(gray, corners, ${p.maxCorners}, ${p.quality/100}, 10);`,
  },
  {
    id: 'fast', name: 'FAST 角点', group: '边缘与基元',
    desc: 'Bresenham 圆周上连续 N 个点都明显更亮/更暗 → 角点，极快。',
    params: [{ key: 'thresh', label: '亮度差阈值', min: 5, max: 80, step: 5, value: 30 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const d = s.clone()
      const fd = new cv.FastFeatureDetector(p.thresh, true)
      const kp = new cv.KeyPointVector()
      fd.detect(g, kp)
      for (let i=0; i<kp.size(); i++) {
        const k = kp.get(i); cv.circle(d, new cv.Point(k.pt.x,k.pt.y), 3, [255,255,0,255], -1)
      }
      fd.delete(); kp.delete(); g.delete(); return d
    },
    codePy: (p) => `fast = cv.FastFeatureDetector_create(threshold=${p.thresh})\nkp = fast.detect(gray, None)\nimg2 = cv.drawKeypoints(img, kp, None, color=(255,255,0))`,
    codeCpp: (p) => `Ptr<FastFeatureDetector> fd = FastFeatureDetector::create(${p.thresh});\nvector<KeyPoint> kp; fd->detect(gray, kp);`,
    codeJs:  (p) => `let fd = new cv.FastFeatureDetector(${p.thresh});\nlet kp = new cv.KeyPointVector();\nfd.detect(gray, kp);`,
  },
  {
    id: 'orb', name: 'ORB 特征点', group: '边缘与基元',
    desc: 'FAST 角点 + 旋转 BRIEF 二进制描述子，免费快速，是 SIFT/SURF 的平替。',
    params: [{ key: 'nfeatures', label: '特征点数', min: 50, max: 2000, step: 50, value: 500 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const d = s.clone()
      const det = new cv.ORB(p.nfeatures); const kp = new cv.KeyPointVector(); const des = new cv.Mat()
      det.detect(g, kp); det.compute(g, kp, des)
      for (let i=0; i<kp.size(); i++){
        const k = kp.get(i); cv.circle(d, new cv.Point(k.pt.x,k.pt.y), 3, [0,255,255,255], -1)
      }
      det.delete(); kp.delete(); des.delete(); g.delete(); return d
    },
    codePy: (p) => `orb = cv.ORB_create(nfeatures=${p.nfeatures})\nkp, des = orb.detectAndCompute(gray, None)\nimg2 = cv.drawKeypoints(img, kp, None, color=(0,255,255))`,
    codeCpp: (p) => `Ptr<ORB> orb = ORB::create(${p.nfeatures});\norb->detectAndCompute(gray, noArray(), kp, des);`,
    codeJs:  (p) => `let orb = new cv.ORB(${p.nfeatures});\norb.detect(gray, kp); orb.compute(gray, kp, des);`,
  },
  {
    id: 'brisk', name: 'BRISK 特征点', group: '边缘与基元',
    desc: '二进制描述子 + 尺度空间，比 ORB 尺度鲁棒。',
    params: [{ key: 'thresh', label: 'FAST 阈值', min: 10, max: 80, step: 5, value: 30 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const d = s.clone()
      const det = new cv.BRISK(p.thresh, 3); const kp = new cv.KeyPointVector(); const des = new cv.Mat()
      det.detect(g, kp); det.compute(g, kp, des)
      for (let i=0; i<kp.size(); i++){ const k=kp.get(i); cv.circle(d, new cv.Point(k.pt.x,k.pt.y), 3, [255,0,255,255], -1) }
      det.delete(); kp.delete(); des.delete(); g.delete(); return d
    },
    codePy: (p) => `brisk = cv.BRISK_create(thresh=${p.thresh})\nkp, des = brisk.detectAndCompute(gray, None)`,
    codeCpp: (p) => `Ptr<BRISK> b = BRISK::create(${p.thresh});`,
    codeJs:  (p) => `let b = new cv.BRISK(${p.thresh});`,
  },
  {
    id: 'akaze', name: 'AKAZE 特征点', group: '边缘与基元',
    desc: '非线性尺度空间，二进制描述子 M-LDB，开源免费。',
    params: [],
    run: (s) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const d = s.clone()
      const det = new cv.AKAZE(); const kp = new cv.KeyPointVector(); const des = new cv.Mat()
      det.detect(g, kp); det.compute(g, kp, des)
      for (let i=0; i<kp.size(); i++){ const k=kp.get(i); cv.circle(d, new cv.Point(k.pt.x,k.pt.y), 3, [0,128,255,255], -1) }
      det.delete(); kp.delete(); des.delete(); g.delete(); return d
    },
    codePy: 'akaze = cv.AKAZE_create()\nkp, des = akaze.detectAndCompute(gray, None)',
    codeCpp: 'Ptr<AKAZE> a = AKAZE::create();',
    codeJs:  'let a = new cv.AKAZE();',
  },
  {
    id: 'mser', name: 'MSER 稳定极值区域', group: '边缘与基元',
    desc: '在阈值变化中始终稳定的连通区域 = 好的文字/区域特征。',
    params: [],
    run: (s) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const d = s.clone()
      const det = new cv.MSER(); const regs = new cv.PointVectorVector();
      det.detectRegions(g, regs, new cv.Mat())
      for (let i=0; i<regs.size(); i++){
        const r = regs.get(i)
        for (let j=0; j<r.size(); j++){ const pt=r.get(j); cv.circle(d, new cv.Point(pt.x,pt.y), 1, [255,0,128,255], -1) }
        r.delete()
      }
      det.delete(); regs.delete(); g.delete(); return d
    },
    codePy: 'mser = cv.MSER_create()\nregions, _ = mser.detectRegions(gray)',
    codeCpp: 'Ptr<MSER> m = MSER::create();\nvector<vector<Point>> regions; m->detectRegions(gray, regions, noArray());',
    codeJs:  'let m = new cv.MSER();\nm.detectRegions(gray, regions, new cv.Mat());',
  },
  {
    id: 'blob', name: 'SimpleBlob 斑点检测', group: '边缘与基元',
    desc: '按面积/圆度/颜色一致性聚类找斑点（亮/暗圆块）。',
    params: [{ key: 'minArea', label: '最小面积', min: 10, max: 5000, step: 50, value: 100 }],
    run: (s, p) => {
      const params = new cv.SimpleBlobDetector_Params()
      params.filterByArea = true; params.minArea = p.minArea
      const det = new cv.SimpleBlobDetector(params); const kp = new cv.KeyPointVector()
      det.detect(s, kp); const d = s.clone()
      for (let i=0; i<kp.size(); i++){ const k=kp.get(i); cv.circle(d, new cv.Point(k.pt.x,k.pt.y), k.size/2, [0,0,255,255], 2) }
      det.delete(); kp.delete(); params.delete(); return d
    },
    codePy: (p) => `params = cv.SimpleBlobDetector_Params()\nparams.filterByArea = True\nparams.minArea = ${p.minArea}\ndet = cv.SimpleBlobDetector_create(params)\nkp = det.detect(gray)`,
    codeCpp: (p) => `SimpleBlobDetector::Params p;\np.filterByArea = true; p.minArea = ${p.minArea};\nPtr<SimpleBlobDetector> d = SimpleBlobDetector::create(p);`,
    codeJs:  (p) => `let p = new cv.SimpleBlobDetector_Params();\np.filterByArea = true; p.minArea = ${p.minArea};\nlet det = new cv.SimpleBlobDetector(p);`,
  },
  {
    id: 'contours', name: '轮廓提取 + 多边形逼近', group: '边缘与基元',
    desc: '二值图中找连通区域外轮廓，再用 Douglas-Peucker 逼近成多边形。',
    params: [{ key: 'epsilon', label: '逼近精度 ε', min: 1, max: 50, step: 1, value: 10 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const bi=new cv.Mat()
      cv.Canny(g, bi, 50, 150); const contours=new cv.MatVector(); const hier=new cv.Mat()
      cv.findContours(bi, contours, hier, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
      const d = s.clone()
      for (let i=0; i<contours.size(); i++){
        const c = contours.get(i); const apx = new cv.Mat()
        cv.approxPolyDP(c, apx, p.epsilon, true)
        cv.drawContours(d, contours, i, [0,255,0,255], 2)
        c.delete(); apx.delete()
      }
      contours.delete(); hier.delete(); g.delete(); bi.delete(); return d
    },
    codePy: (p) => `cnts, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)\nfor c in cnts:\n    approx = cv.approxPolyDP(c, epsilon=${p.epsilon}, closed=True)\n    cv.drawContours(img, [approx], 0, (0,255,0), 2)`,
    codeCpp: (p) => `findContours(bin, cnts, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);\nfor(auto &c : cnts) {\n  vector<Point> a; approxPolyDP(c, a, ${p.epsilon}, true);\n  drawContours(img, vector<vector<Point>>{a}, 0, Scalar(0,255,0),2);\n}`,
    codeJs:  (p) => `cv.findContours(bi, contours, hier, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);\nfor(let i=0;i<contours.size();i++){\n  let apx = new cv.Mat();\n  cv.approxPolyDP(contours.get(i), apx, ${p.epsilon}, true);\n  cv.drawContours(dst, contours, i, [0,255,0,255], 2);\n}`,
  },
  // —— 图像分割 ——
  {
    id: 'kmeans', name: 'K-Means 颜色聚类', group: '图像分割',
    desc: '把所有像素按 RGB 空间距离聚成 K 类，最简单的彩色分割。',
    params: [{ key: 'K', label: '簇数 K', min: 2, max: 12, step: 1, value: 4 }],
    run: (s, p) => {
      const samples_ = s.reshape(3, s.rows*s.cols); const f32 = new cv.Mat()
      samples_.convertTo(f32, cv.CV_32F)
      const labels = new cv.Mat(), centers = new cv.Mat()
      cv.kmeans(f32, p.K, labels, new cv.TermCriteria(cv.TERM_CRITERIA_EPS+cv.TERM_CRITERIA_MAX_ITER, 10, 1.0), 3, cv.KMEANS_PP_CENTERS, centers)
      const out = new cv.Mat(s.rows, s.cols, s.type())
      for (let i=0; i<s.rows*s.cols; i++){
        const c = labels.data32S[i]
        out.data[i*4]   = centers.data32F[c*3+0]
        out.data[i*4+1] = centers.data32F[c*3+1]
        out.data[i*4+2] = centers.data32F[c*3+2]
        out.data[i*4+3] = 255
      }
      samples_.delete(); f32.delete(); labels.delete(); centers.delete(); return out
    },
    codePy: (p) => `Z = img.reshape((-1,3)).astype(np.float32)\ncriteria = (cv.TERM_CRITERIA_EPS+cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)\n_,label,C = cv.kmeans(Z, ${p.K}, None, criteria, 3, cv.KMEANS_PP_CENTERS)\nC = np.uint8(C)\ndst = C[label.flatten()].reshape(img.shape)`,
    codeCpp: (p) => `kmeans(samples, ${p.K}, labels, TermCriteria(/*...*/), 3, KMEANS_PP_CENTERS, centers);`,
    codeJs:  (p) => `cv.kmeans(data, ${p.K}, labels,\n  new cv.TermCriteria(cv.TERM_CRITERIA_EPS+cv.TERM_CRITERIA_MAX_ITER, 10, 1.0),\n  3, cv.KMEANS_PP_CENTERS, centers);`,
  },
  {
    id: 'inrange', name: '颜色阈值分割 (inRange)', group: '图像分割',
    desc: '按 HSV 颜色立方体范围抠出目标色（常用在"挑出红苹果"这类场景）。',
    params: [
      { key: 'hueL', label: '色相下限', min: 0, max: 179, step: 1, value: 35 },
      { key: 'hueH', label: '色相上限', min: 0, max: 179, step: 1, value: 85 },
      { key: 'sat', label: '饱和度下限', min: 0, max: 255, step: 5, value: 40 },
    ],
    run: (s, p) => {
      const hsv = new cv.Mat(); cv.cvtColor(s, hsv, cv.COLOR_RGB2HSV)
      const mask = new cv.Mat(); const lo = new cv.Mat(hsv.rows, hsv.cols, hsv.type(), [p.hueL,p.sat,40,255]); const hi = new cv.Mat(hsv.rows,hsv.cols,hsv.type(),[p.hueH,255,255,255])
      cv.inRange(hsv, lo, hi, mask); const d=new cv.Mat(); s.copyTo(d, mask)
      hsv.delete(); lo.delete(); hi.delete(); mask.delete(); return d
    },
    codePy: (p) => `hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)\nlower = np.array([${p.hueL},${p.sat},40])\nupper = np.array([${p.hueH},255,255])\nmask = cv.inRange(hsv, lower, upper)\ndst = cv.bitwise_and(img, img, mask=mask)`,
    codeCpp: (p) => `inRange(hsv, Scalar(${p.hueL},${p.sat},40), Scalar(${p.hueH},255,255), mask);\nbitwise_and(img, img, dst, mask);`,
    codeJs:  (p) => `cv.cvtColor(src, hsv, cv.COLOR_RGB2HSV);\nlet lo = new cv.Mat(hsv.rows, hsv.cols, hsv.type(), [${p.hueL},${p.sat},40,0]);\nlet hi = new cv.Mat(hsv.rows, hsv.cols, hsv.type(), [${p.hueH},255,255,255]);\ncv.inRange(hsv, lo, hi, mask);`,
  },
  {
    id: 'distance', name: '距离变换', group: '图像分割',
    desc: '每个像素到最近背景像素的距离——分水岭分割的"种子"。',
    params: [],
    run: (s) => {
      const g=new cv.Mat(); cv.cvtColor(s,g,cv.COLOR_RGBA2GRAY); const bi=new cv.Mat()
      cv.threshold(g, bi, 0, 255, cv.THRESH_BINARY|cv.THRESH_OTSU)
      const dist = new cv.Mat(); cv.distanceTransform(bi, dist, cv.DIST_L2, 3)
      const d = new cv.Mat(); cv.normalize(dist, d, 0, 255, cv.NORM_MINMAX); cv.convertScaleAbs(d, d)
      g.delete(); bi.delete(); dist.delete(); return gray2rgba(d)
    },
    codePy: `dist = cv.distanceTransform(binary, cv.DIST_L2, 3)\ncv.normalize(dist, dist, 0, 1.0, cv.NORM_MINMAX)`,
    codeCpp: 'distanceTransform(bin, dist, DIST_L2, 3);\nnormalize(dist, dist, 0, 1, NORM_MINMAX);',
    codeJs:  'cv.distanceTransform(bi, dist, cv.DIST_L2, 3);\ncv.normalize(dist, d, 0, 255, cv.NORM_MINMAX);',
  },
  {
    id: 'connected', name: '连通域分析', group: '图像分割',
    desc: '同一连通区域同一编号，常用于数硬币、数米粒。',
    params: [],
    run: (s) => {
      const g=new cv.Mat(); cv.cvtColor(s,g,cv.COLOR_RGBA2GRAY); const bi=new cv.Mat()
      cv.threshold(g, bi, 0, 255, cv.THRESH_BINARY|cv.THRESH_OTSU)
      const labels = new cv.Mat(), stats = new cv.Mat(), centroids = new cv.Mat()
      const n = cv.connectedComponentsWithStats(bi, labels, stats, centroids)
      const d = s.clone()
      for (let i=1; i<n; i++){
        const x = stats.data32S[i*5], y=stats.data32S[i*5+1], w=stats.data32S[i*5+2], h=stats.data32S[i*5+3]
        cv.rectangle(d, new cv.Point(x,y), new cv.Point(x+w,y+h), [255,0,0,255], 2)
      }
      g.delete(); bi.delete(); labels.delete(); stats.delete(); centroids.delete(); return d
    },
    codePy: `n, labels, stats, centroids = cv.connectedComponentsWithStats(binary)\nfor i in range(1, n):\n    x,y,w,h,area = stats[i]\n    cv.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)`,
    codeCpp: 'connectedComponentsWithStats(bin, labels, stats, centroids);\nfor (int i=1;i<n;i++) { int x=stats.at<int>(i,CC_STAT_LEFT); /*...*/ }',
    codeJs:  'cv.connectedComponentsWithStats(bi, labels, stats, centroids);',
  },
  {
    id: 'watershed', name: '分水岭分割', group: '图像分割',
    desc: '把图像当"地形"，从已知种子向四周注水，会撞的地方就是边界。',
    params: [],
    run: (s) => {
      // 简化版：Otsu 二值→距离变换→取前 30% 作种子→watershed
      const g=new cv.Mat(); cv.cvtColor(s,g,cv.COLOR_RGBA2GRAY); const bi=new cv.Mat()
      cv.threshold(g, bi, 0, 255, cv.THRESH_BINARY_INV|cv.THRESH_OTSU)
      // distanceTransform 输出 CV_32FC1
      const dist = mat32f(); cv.distanceTransform(bi, dist, cv.DIST_L2, 3)
      const dnorm = new cv.Mat(); cv.normalize(dist, dnorm, 0, 1, cv.NORM_MINMAX, cv.CV_32F)
      const sureFg = new cv.Mat(); cv.threshold(dnorm, sureFg, 0.3, 255, cv.THRESH_BINARY)  // dnorm 已归一化到 [0,1]
      const fgU8 = new cv.Mat(); sureFg.convertTo(fgU8, cv.CV_8U)
      const markers = new cv.Mat(); cv.connectedComponents(fgU8, markers)
      const markersI32 = new cv.Mat(); markers.convertTo(markersI32, cv.CV_32S)
      cv.watershed(s, markersI32)
      const d = s.clone()
      // watershed 边界标记为 -1，直接读 data32S 避免 intAt 越界
      const w = d.cols, mdata = markersI32.data32S, ddata = d.data
      for (let y=0; y<d.rows; y++) {
        for (let x=0; x<d.cols; x++) {
          if (mdata[y*w+x] === -1) {
            const idx = (y*w+x)*4
            ddata[idx]=255; ddata[idx+1]=0; ddata[idx+2]=255; ddata[idx+3]=255
          }
        }
      }
      g.delete(); bi.delete(); dist.delete(); dnorm.delete(); sureFg.delete(); fgU8.delete(); markers.delete(); markersI32.delete(); return d
    },
    codePy: `# 1) Otsu 二值化
_, bin = cv.threshold(gray,0,255,cv.THRESH_BINARY_INV|cv.THRESH_OTSU)
# 2) 距离变换取确定前景
dist = cv.distanceTransform(bin,cv.DIST_L2,3)
_, sure_fg = cv.threshold(dist,0.3*dist.max(),255,cv.THRESH_BINARY)
# 3) 连通域做种子
n, markers = cv.connectedComponents(sure_fg.astype(np.uint8))
markers = markers.astype(np.int32)
# 4) 分水岭
cv.watershed(img, markers)
img[markers==-1] = [0,0,255]  # 边界染红`,
    codeCpp: 'watershed(img, markers);\n// markers == -1 的像素即边界',
    codeJs:  'cv.watershed(src, markers);',
  },
  // —— 匹配与几何 ——
  {
    id: 'template', name: '模板匹配 (matchTemplate)', group: '匹配与几何',
    desc: '滑动窗口算相似度（如 NCC），最直观的"找小图在大图中的位置"。',
    params: [{ key: 'threshold', label: '匹配阈值(x100)', min: 30, max: 99, step: 1, value: 70 }],
    run: (s, p) => {
      // 直接取中央 60x60 做模板
      const tw=Math.min(60, s.cols-2), th=Math.min(60, s.rows-2)
      const tplRoi = new cv.Rect(Math.max(0,(s.cols-tw)/2|0), Math.max(0,(s.rows-th)/2|0), tw, th)
      const tpl = s.roi(tplRoi); const res = new cv.Mat()
      cv.matchTemplate(s, tpl, res, cv.TM_CCOEFF_NORMED)
      const d = s.clone()
      cv.rectangle(d, new cv.Point(tplRoi.x,tplRoi.y), new cv.Point(tplRoi.x+tw,tplRoi.y+th), [0,255,255,255], 2)
      // matchTemplate 输出 CV_32FC1，大小 (H-th+1, W-tw+1)，用 data32F 访问避免 floatAt 越界
      let M = -Infinity, mx=0, my=0
      const rdata = res.data32F
      const rw = res.cols
      for (let i=0; i<rdata.length; i++) {
        if (rdata[i] > M) { M = rdata[i]; mx = i % rw; my = (i / rw) | 0 }
      }
      if (M >= p.threshold/100) cv.rectangle(d, new cv.Point(mx,my), new cv.Point(mx+tw,my+th), [0,0,255,255], 2)
      tpl.delete(); res.delete(); return d
    },
    codePy: (p) => `res = cv.matchTemplate(img, tpl, cv.TM_CCOEFF_NORMED)\ny, x = np.unravel_index(np.argmax(res), res.shape)\nif res[y,x] > ${(p.threshold/100).toFixed(2)}:\n    cv.rectangle(img, (x,y), (x+w,y+h), (0,0,255), 2)`,
    codeCpp: (p) => `matchTemplate(img, tpl, res, TM_CCOEFF_NORMED);`,
    codeJs:  (p) => `cv.matchTemplate(src, tpl, res, cv.TM_CCOEFF_NORMED);`,
  },
  {
    id: 'bfmatch', name: 'ORB + BFMatcher 特征匹配', group: '匹配与几何',
    desc: '在两张图上分别提取 ORB 描述子，用汉明距离暴力匹配。',
    params: [],
    run: (s) => {
      // 简单做：拿原图 vs 旋转变换后的图，画匹配线
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const g2 = new cv.Mat(); const M = cv.getRotationMatrix2D(new cv.Point(g.cols/2, g.rows/2), 15, 1.0)
      cv.warpAffine(g, g2, M, new cv.Size(g.cols, g.rows))
      const orb = new cv.ORB(500); const kp1 = new cv.KeyPointVector(), kp2 = new cv.KeyPointVector()
      const d1 = new cv.Mat(), d2 = new cv.Mat()
      orb.detectAndCompute(g, new cv.Mat(), kp1, d1); orb.detectAndCompute(g2, new cv.Mat(), kp2, d2)
      const bf = new cv.BFMatcher(cv.NORM_HAMMING, true); const matches = new cv.DMatchVector()
      bf.match(d1, d2, matches)
      const out = new cv.Mat(); cv.drawMatches(g, kp1, g2, kp2, matches, out)
      g.delete(); g2.delete(); M.delete(); orb.delete(); kp1.delete(); kp2.delete(); d1.delete(); d2.delete(); bf.delete(); matches.delete()
      return out
    },
    codePy: `orb = cv.ORB_create(500)\nkp1, d1 = orb.detectAndCompute(img1, None)\nkp2, d2 = orb.detectAndCompute(img2, None)\nbf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)\nmatches = bf.match(d1, d2)\nout = cv.drawMatches(img1,kp1,img2,kp2,matches,None)`,
    codeCpp: 'BFMatcher bf(NORM_HAMMING, true);\nbf.match(d1, d2, matches);',
    codeJs:  'let bf = new cv.BFMatcher(cv.NORM_HAMMING, true);\nbf.match(d1, d2, matches);',
  },
  {
    id: 'homography', name: 'RANSAC 单应校正', group: '匹配与几何',
    desc: '先 ORB 匹配，再用 RANSAC 求 3×3 单应矩阵，可把歪文档/倾斜物体"掰正"。',
    params: [{ key: 'thresh', label: 'RANSAC 阈值', min: 1, max: 10, step: 1, value: 5 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      // 用原图中心 80% 做"目标"图，平移+旋转作模板
      const padx = g.cols*0.1|0, pady = g.rows*0.1|0
      const roi = new cv.Rect(padx,pady,g.cols-2*padx,g.rows-2*pady)
      const tgt = g.roi(roi); const g2 = new cv.Mat()
      const rM = cv.getRotationMatrix2D(new cv.Point(g.cols/2,g.rows/2),20,0.9)
      cv.warpAffine(g, g2, rM, new cv.Size(g.cols,g.rows))
      const orb = new cv.ORB(1000); const kp1=new cv.KeyPointVector(), kp2=new cv.KeyPointVector()
      const d1=new cv.Mat(),d2=new cv.Mat()
      orb.detectAndCompute(g2, new cv.Mat(), kp1, d1); orb.detectAndCompute(tgt, new cv.Mat(), kp2, d2)
      const bf=new cv.BFMatcher(cv.NORM_HAMMING); const matches=new cv.DMatchVectorVector()
      bf.knnMatch(d1, d2, matches, 2)
      const good = new cv.DMatchVector()
      for (let i=0;i<matches.size();i++){
        const m=matches.get(i)
        if (m.size()>=2 && m.get(0).distance < 0.7*m.get(1).distance) good.push_back(m.get(0))
      }
      const d = s.clone()
      if (good.size()>=4){
        const srcPts = new cv.Mat(good.size(),1,cv.CV_32FC2), dstPts = new cv.Mat(good.size(),1,cv.CV_32FC2)
        for (let i=0;i<good.size();i++){
          const m=good.get(i), p1=kp1.get(m.queryIdx).pt, p2=kp2.get(m.trainIdx).pt
          srcPts.data32F[i*2]=p1.x; srcPts.data32F[i*2+1]=p1.y
          dstPts.data32F[i*2]=p2.x; dstPts.data32F[i*2+1]=p2.y
        }
        const H = cv.findHomography(srcPts, dstPts, cv.RANSAC, p.thresh)
        const out = new cv.Mat(); cv.warpPerspective(d, out, H, new cv.Size(tgt.cols, tgt.rows))
        srcPts.delete(); dstPts.delete(); H.delete()
        g.delete(); tgt.delete(); g2.delete(); rM.delete(); orb.delete(); kp1.delete(); kp2.delete(); d1.delete(); d2.delete(); bf.delete(); matches.delete(); good.delete()
        return out
      }
      g.delete(); tgt.delete(); g2.delete(); rM.delete(); orb.delete(); kp1.delete(); kp2.delete(); d1.delete(); d2.delete(); bf.delete(); matches.delete(); good.delete()
      return d
    },
    codePy: (p) => `good = [m for m,n in knn_matches if m.distance < 0.7*n.distance]\nsrc_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)\ndst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)\nH, _ = cv.findHomography(src_pts, dst_pts, cv.RANSAC, ${p.thresh})\ndst = cv.warpPerspective(img, H, (w,h))`,
    codeCpp: (p) => `findHomography(srcPts, dstPts, RANSAC, ${p.thresh});\nwarpPerspective(img, dst, H, Size(w,h));`,
    codeJs:  (p) => `let H = cv.findHomography(srcPts, dstPts, cv.RANSAC, ${p.thresh});\ncv.warpPerspective(src, dst, H, new cv.Size(w,h));`,
  },
  {
    id: 'lkflow', name: 'LK 稀疏光流追踪', group: '匹配与几何',
    desc: '在 Shi-Tomasi 角点上用 Lucas-Kanade 假设"小运动邻域光流一致"，跟踪下一帧位置。',
    params: [{ key: 'winSize', label: '窗口大小', min: 5, max: 31, step: 2, value: 15 }],
    run: (s, p) => {
      // 直接在原图上做 2D 平移 (10,5) 来模拟两帧
      const g1 = new cv.Mat(); cv.cvtColor(s, g1, cv.COLOR_RGBA2GRAY)
      const g2 = new cv.Mat(); const M = cv.matFromArray(2,3,cv.CV_64FC1,[1,0,10,0,1,5])
      cv.warpAffine(g1, g2, M, new cv.Size(g1.cols,g1.rows))
      const pts = new cv.Mat(); cv.goodFeaturesToTrack(g1, pts, 100, 0.01, 10)
      const next = new cv.Mat(), st = new cv.Mat(), err = new cv.Mat()
      cv.calcOpticalFlowPyrLK(g1, g2, pts, next, st, err, new cv.Size(p.winSize,p.winSize), 3)
      const d = s.clone()
      // pts/next 都是 (N,1) CV_32FC2；st 是 (N,1) CV_8UC1
      const n = pts.rows
      const p1 = pts.data32F, p2 = next.data32F, sdata = st.data
      for (let i=0; i<n; i++){
        if (sdata[i]===0) continue
        const x1=p1[i*2], y1=p1[i*2+1], x2=p2[i*2], y2=p2[i*2+1]
        cv.line(d, new cv.Point(x1,y1), new cv.Point(x2,y2), [0,255,0,255],2)
        cv.circle(d, new cv.Point(x2,y2), 3, [0,0,255,255],-1)
      }
      g1.delete(); g2.delete(); M.delete(); pts.delete(); next.delete(); st.delete(); err.delete(); return d
    },
    codePy: (p) => `p0 = cv.goodFeaturesToTrack(old_gray, 100, 0.01, 10)\np1, st, err = cv.calcOpticalFlowPyrLK(old_gray, new_gray, p0, None,\n    winSize=(${p.winSize},${p.winSize}), maxLevel=3)\nfor (a,b), good in zip(p1[st==1], p0[st==1]):\n    cv.line(img, tuple(a.astype(int)), tuple(b.astype(int)), (0,255,0),2)`,
    codeCpp: (p) => `calcOpticalFlowPyrLK(prev, next, p0, p1, st, noArray(), Size(${p.winSize},${p.winSize}), 3);`,
    codeJs:  (p) => `cv.calcOpticalFlowPyrLK(p,g,p0,p1,st,err,new cv.Size(${p.winSize},${p.winSize}),3);`,
  },
  {
    id: 'gradient-flow', name: '稠密光流 (Farnebäck) 示意', group: '匹配与几何',
    desc: '每个像素都估计 (dx,dy)——用 HSV 编码方向/强度。',
    params: [],
    run: (s) => {
      const g1 = new cv.Mat(); cv.cvtColor(s, g1, cv.COLOR_RGBA2GRAY)
      const g2 = new cv.Mat(); const M = cv.matFromArray(2,3,cv.CV_64FC1,[1,0,6,0,1,6])
      cv.warpAffine(g1, g2, M, new cv.Size(g1.cols,g1.rows))
      const flow = new cv.Mat(); cv.calcOpticalFlowFarneback(g1, g2, flow, 0.5, 3, 15, 3, 5, 1.2, 0)
      // HSV 编码
      const hsv = new cv.Mat.zeros(s.rows, s.cols, cv.CV_8UC3); const mag = new cv.Mat(), ang = new cv.Mat()
      const fxy = new cv.MatVector(); cv.split(flow, fxy)
      cv.cartToPolar(fxy.get(0), fxy.get(1), mag, ang, true)
      // H: 角度 S:255 V: magnitude 归一化
      const nm = new cv.Mat(); cv.normalize(mag, nm, 0, 255, cv.NORM_MINMAX); nm.convertTo(nm, cv.CV_8U)
      const h8 = new cv.Mat(), a8 = new cv.Mat(); ang.convertTo(h8, cv.CV_8U, 0.5); const sCh = new cv.Mat.zeros(s.rows,s.cols,cv.CV_8U); sCh.setTo(255)
      const mv = new cv.MatVector(); mv.push_back(h8); mv.push_back(sCh); mv.push_back(nm)
      const bgr = new cv.Mat(); cv.merge(mv, bgr); const out = new cv.Mat(); cv.cvtColor(bgr, out, cv.COLOR_HSV2RGBA)
      g1.delete(); g2.delete(); M.delete(); flow.delete(); mag.delete(); ang.delete(); fxy.delete(); nm.delete(); h8.delete(); a8.delete(); sCh.delete(); mv.delete(); bgr.delete(); return out
    },
    codePy: `flow = cv.calcOpticalFlowFarneback(old, new, None, 0.5, 3, 15, 3, 5, 1.2, 0)\nmag, ang = cv.cartToPolar(flow[...,0], flow[...,1], angleInDegrees=True)\nhsv[...,0] = ang/2; hsv[...,1]=255; hsv[...,2]=cv.normalize(mag,None,0,255,cv.NORM_MINMAX)\nbgr = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)`,
    codeCpp: 'calcOpticalFlowFarneback(prev, next, flow, 0.5, 3, 15, 3, 5, 1.2, 0);',
    codeJs:  'cv.calcOpticalFlowFarneback(p,g,flow,0.5,3,15,3,5,1.2,0);',
  },
  {
    id: 'sobel-hog', name: '梯度幅值热力图', group: '匹配与几何',
    desc: 'HOG 的直觉：每个像素梯度方向和强度，用颜色表示——人轮廓里就能看到方向分布。',
    params: [],
    run: (s) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const gx=new cv.Mat(), gy=new cv.Mat(); cv.Sobel(g,gx,cv.CV_32F,1,0,3); cv.Sobel(g,gy,cv.CV_32F,0,1,3)
      const mag=new cv.Mat(), ang=new cv.Mat(); cv.cartToPolar(gx,gy,mag,ang,true)
      const nm=new cv.Mat(); cv.normalize(mag,nm,0,255,cv.NORM_MINMAX)
      const hsv=new cv.Mat.zeros(s.rows,s.cols,cv.CV_8UC3)
      const mv = new cv.MatVector()
      const a8=new cv.Mat(), v8=new cv.Mat(), s8=new cv.Mat.zeros(s.rows,s.cols,cv.CV_8U); s8.setTo(255)
      ang.convertTo(a8, cv.CV_8U, 0.5); nm.convertTo(v8, cv.CV_8U)
      mv.push_back(a8); mv.push_back(s8); mv.push_back(v8)
      cv.merge(mv, hsv); const bgr=new cv.Mat(); cv.cvtColor(hsv,bgr,cv.COLOR_HSV2RGBA)
      g.delete(); gx.delete(); gy.delete(); mag.delete(); ang.delete(); nm.delete(); a8.delete(); v8.delete(); s8.delete(); mv.delete(); hsv.delete(); return bgr
    },
    codePy: `gx = cv.Sobel(gray,cv.CV_32F,1,0,ksize=3)\ngy = cv.Sobel(gray,cv.CV_32F,0,1,ksize=3)\nmag, ang = cv.cartToPolar(gx, gy, angleInDegrees=True)\nhsv[...,0] = ang/2; hsv[...,1]=255; hsv[...,2]=cv.normalize(mag,None,0,255,cv.NORM_MINMAX)\ndst = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)`,
    codeCpp: 'Sobel(g,gx,CV_32F,1,0,3); Sobel(g,gy,CV_32F,0,1,3);\ncartToPolar(gx,gy,mag,ang,true);',
    codeJs:  'cv.cartToPolar(gx,gy,mag,ang,true);',
  },
  // —— 传统目标检测 ——
  {
    id: 'facedetect', name: 'Viola-Jones 人脸检测', group: '传统目标检测',
    desc: 'Haar 特征 + 积分图 + AdaBoost + 级联分类器——OpenCV 自带的经典人脸检测。',
    params: [{ key: 'scale', label: 'scaleFactor (x100)', min: 105, max: 150, step: 5, value: 110 }, { key: 'minNeighbors', label: 'minNeighbors', min: 1, max: 10, step: 1, value: 5 }],
    run: (s, p) => {
      if (!haarDetector) {
        const c = s.clone(); g_delete(); return c
      }
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); cv.equalizeHist(g, g)
      const faces = new cv.RectVector(); const d = s.clone()
      try {
        haarDetector.detectMultiScale(g, faces, p.scale/100, p.minNeighbors, 0, new cv.Size(30,30), new cv.Size(0,0))
        for (let i=0; i<faces.size(); i++){
          const r = faces.get(i); cv.rectangle(d, new cv.Point(r.x,r.y), new cv.Point(r.x+r.width,r.y+r.height), [0,255,0,255], 2)
        }
      } catch(e){}
      g.delete(); faces.delete(); return d
      function g_delete(){}
    },
    codePy: (p) => `face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')\ngray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)\nfaces = face_cascade.detectMultiScale(gray, ${(p.scale/100).toFixed(2)}, ${p.minNeighbors})\nfor (x,y,w,h) in faces:\n    cv.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)`,
    codeCpp: (p) => `CascadeClassifier cc("haarcascade_frontalface_default.xml");\ncc.detectMultiScale(gray, faces, ${(p.scale/100).toFixed(2)}, ${p.minNeighbors});`,
    codeJs:  (p) => `cc.detectMultiScale(gray, faces, ${(p.scale/100).toFixed(2)}, ${p.minNeighbors}, 0, new cv.Size(30,30));`,
  },
]

filters.forEach(f => { f.algoLink = ALGO_LINK[f.id] || null })

// 给有 string 形式 code 的算法转成函数
filters.forEach(f => {
  ['codePy','codeCpp','codeJs'].forEach(k => {
    if (typeof f[k] === 'string') { const raw = f[k]; f[k] = () => raw }
  })
})

const groups = [...new Set(filters.map((f) => f.group))]

import { loadOpenCV, isCVReady, getCVIfReady, resetCV, openCVUrl, getCVUrl } from '../lib/opencv-loader'

const languages = ['Python', 'C++', 'JavaScript']

/* ---------------- 响应式状态 ---------------- */
// 初始状态是 idle（未启动）：必须用户点击「启动真机实验」按钮才会开始下载 opencv.js，
// 避免首屏就自动下载 3.5MB，也避免后台预取堵并发连接。
// 加载方案：最朴素的 <script src> 追加，与"地址栏直接打开 opencv.js"行为一致。
const status = ref('idle') // 'idle' | 'loading' | 'initializing' | 'ready' | 'error'
const statusText = ref('')
const errorMsg = ref('')
const srcCanvas = ref(null)
const dstCanvas = ref(null)
const currentSample = ref('scene.png')
const currentFilter = ref('canny')
const paramValues = reactive({})
const lastMs = ref(-1)
const runError = ref('')
const lang = ref('Python')

let cv = null
let srcMat = null
let timer = null
let haarXml = null
let haarDetector = null

const activeFilter = computed(() => filters.find(f => f.id === currentFilter.value) || filters[0])
const embedAlgo = computed(() => !!props.initialAlgo)

// initialAlgo 兜底：传了不存在的 id 时回退到默认 canny，避免 activeFilter 变 undefined 白屏
const resolvedInitialAlgo = computed(() => {
  if (!props.initialAlgo) return ''
  return filters.some(f => f.id === props.initialAlgo) ? props.initialAlgo : ''
})

function start() {
  errorMsg.value = ''
  status.value = 'loading'
  statusText.value = '正在加载 OpenCV.js（首次约需 5~30 秒，后续会缓存）…'
  bootLoader()
}

function cancelAndRetry() {
  resetCV()
  errorMsg.value = ''
  status.value = 'loading'
  statusText.value = '正在重新加载 OpenCV.js…'
  bootLoader(true)
}

function retry() {
  cancelAndRetry()
}

// 直链预热：新标签打开 opencv.js（你亲测这种方式秒开），
// 让浏览器把文件写进 HTTP 缓存，回本页再点启动就秒加载。
function prewarm() {
  try { openCVUrl() } catch (_) {
    const a = document.createElement('a')
    a.href = getCVUrl()
    a.target = '_blank'
    a.rel = 'noopener'
    a.click()
  }
}

async function bootLoader(force = false) {
  try {
    if (isCVReady()) {
      cv = getCVIfReady()
      status.value = 'ready'
      initAfterReady()
      return
    }
    status.value = 'loading'
    statusText.value = '正在从 GitHub Pages 加载 OpenCV.js…'

    const cvMod = await loadOpenCV({
      force,
      onStage: (stage) => {
        if (stage === 'loading') {
          status.value = 'loading'
          statusText.value = '正在加载 OpenCV.js…'
        } else if (stage === 'initializing') {
          status.value = 'initializing'
          statusText.value = '正在你的浏览器里编译 WebAssembly（首次约 5~10 秒）…'
        }
      },
    })
    cv = cvMod
    status.value = 'ready'
    initAfterReady()
  } catch (e) {
    status.value = 'error'
    errorMsg.value = (e && e.message) || String(e)
    statusText.value = 'OpenCV.js 加载失败'
  }
}

function initAfterReady() {
  nextTick(() => {
    const init = readInitialAlgoFromUrl()
    if (init) currentFilter.value = init
    initParams()
    const sampleByAlgo = {
      facedetect:'face.png', 'sobel-hog':'pedestrian.png', houghcircles:'coins.png',
      chessboard_corner:'chessboard.png', harris:'chessboard.png', gftt:'chessboard.png',
      fast:'chessboard.png', orb:'street.png', brisk:'street.png', akaze:'street.png',
      bfmatch:'street.png', homography:'street.png', lkflow:'frame1.png',
      'gradient-flow':'frame1.png', kmeans:'fruits.png', watershed:'coins.png',
      connected:'coins.png', distance:'coins.png',
    }
    const s = sampleByAlgo[currentFilter.value]
    if (s) currentSample.value = s
    loadSample(); loadHaar()
  })
}

/* 读取 URL hash 对初始算法做锚定；?algo=xxx 或 #algo:xxx */
function readInitialAlgoFromUrl() {
  if (resolvedInitialAlgo.value) return resolvedInitialAlgo.value
  if (typeof window === 'undefined') return null
  const u = new URL(window.location.href)
  const fromQ = u.searchParams.get('algo')
  const fromH = (u.hash||'').match(/algo=([\w-]+)/)
  const cand = fromQ || (fromH && fromH[1])
  if (cand && filters.some(f=>f.id===cand)) return cand
  return null
}

const currentCode = computed(() => {
  const f = activeFilter.value
  const p = { ...paramValues }
  try {
    if (lang.value === 'Python') return f.codePy(p) || '# 暂无示例代码'
    if (lang.value === 'C++') return f.codeCpp(p) || '// 暂无示例代码'
    return f.codeJs(p) || '// 暂无示例代码'
  } catch(e){ return '// 代码生成失败：' + e.message }
})

async function copyCode() {
  try {
    await navigator.clipboard.writeText(currentCode.value)
    const el = document.querySelector('.ocv-copy-btn')
    if (el) { const old = el.textContent; el.textContent = '✅ 已复制'; setTimeout(()=>el.textContent=old, 1200) }
  } catch(e){}
}

function filtersByGroup(g) { return filters.filter(f => f.group === g) }

async function loadHaar() {
  if (haarXml) return
  try {
    const res = await fetch(HAAR_XML_URL)
    if (!res.ok) return
    const txt = await res.text()
    cv.FS_createDataFile('/', 'haar_face.xml', txt, true, false, false)
    const cc = new cv.CascadeClassifier()
    if (cc.load('haar_face.xml')) { haarDetector = cc; haarXml = txt } else cc.delete()
  } catch(e){}
}

/* ---------------- 图像 ---------------- */
function drawToSrcCanvas(img) {
  const c = srcCanvas.value
  const maxW = props.compact ? 360 : 480
  const scale = Math.min(1, maxW / img.width, maxW / img.height)
  c.width = Math.round(img.width * scale)
  c.height = Math.round(img.height * scale)
  const ctx = c.getContext('2d'); ctx.clearRect(0,0,c.width,c.height); ctx.drawImage(img,0,0,c.width,c.height)
}
function loadSample() {
  const img = new Image(); img.crossOrigin='anonymous'
  img.onload = () => { drawToSrcCanvas(img); run() }
  img.onerror = () => { runError.value = '示例图加载失败：' + currentSample.value }
  img.src = SAMPLE_BASE + currentSample.value
}
function onUpload(e) {
  const file = e.target.files && e.target.files[0]; if (!file) return
  const url = URL.createObjectURL(file); const img = new Image()
  img.onload = () => { drawToSrcCanvas(img); URL.revokeObjectURL(url); run() }
  img.src = url
}

/* ---------------- 执行 ---------------- */
function initParams() {
  for (const k of Object.keys(paramValues)) delete paramValues[k]
  for (const p of activeFilter.value.params) paramValues[p.key] = p.value
}
function scheduleRun() { if (timer) clearTimeout(timer); timer = setTimeout(run, 150) }

function run() {
  if (!cv || !srcCanvas.value) return
  runError.value = ''
  const c = srcCanvas.value, dcanvas = dstCanvas.value
  dcanvas.width = c.width; dcanvas.height = c.height
  let src = null, out = null
  try {
    src = cv.imread(c)
    const t0 = performance.now()
    out = activeFilter.value.run(src, { ...paramValues })
    const t1 = performance.now()
    if (out) cv.imshow(dcanvas, out)
    lastMs.value = t1 - t0
  } catch (err) {
    runError.value = '运行出错：' + (err && err.message ? err.message : String(err))
    const ctx = dcanvas.getContext('2d'); ctx.clearRect(0,0,dcanvas.width,dcanvas.height)
    ctx.fillStyle='#eee'; ctx.fillRect(0,0,dcanvas.width,dcanvas.height)
    ctx.fillStyle='#999'; ctx.font='14px sans-serif'
    ctx.fillText('该算法在当前 OpenCV.js 构建中可能不可用', 16, 28)
  } finally {
    if (src) src.delete()
    if (out && out !== src) { try { out.delete() } catch(e){} }
  }
}

function onAlgoChange() {
  const u = new URL(window.location.href)
  u.searchParams.set('algo', currentFilter.value)
  history.replaceState(null, '', u.toString())
}

// 🔴 关键改动：组件挂载后**不**自动启动 OpenCV.js 加载。
// 用户必须主动点击「启动真机实验」按钮才会下载 opencv.js，
// 彻底避免首屏自动下载 3.5MB 脚本拖慢页面、或后台并发被预取堵住。
onMounted(() => {
  // 如果 URL 带了 ?algo=xxx 或者组件传入 initialAlgo，只做算法预选，不触发加载
  const urlAlgo = new URLSearchParams(window.location.search).get('algo')
  if (resolvedInitialAlgo.value) currentFilter.value = resolvedInitialAlgo.value
  else if (urlAlgo && filters.some(f => f.id === urlAlgo)) currentFilter.value = urlAlgo
})

watch(currentFilter, async () => { initParams(); await nextTick(); run() })
</script>

<style scoped>
.ocv-root { margin: 24px 0; border: 1px solid var(--vp-c-divider); border-radius: 12px; background: var(--vp-c-bg-soft); padding: 14px; }
.ocv-compact { padding: 10px; }
.ocv-compact .ocv-loading { padding: 28px 18px; }
.ocv-compact .ocv-tip { font-size: 11px; }
.ocv-compact .ocv-start-btn { padding: 10px 22px; font-size: 14px; }
.ocv-loading { padding: 48px 24px; text-align: center; color: var(--vp-c-text-2); }
.ocv-spinner { width: 34px; height: 34px; margin: 0 auto 16px; border: 3px solid var(--vp-c-divider); border-top-color: var(--vp-c-brand-1); border-radius: 50%; animation: ocv-spin 0.9s linear infinite; }
@keyframes ocv-spin { to { transform: rotate(360deg) } }
.ocv-status-text { margin: 0; font-size: 15px; }
.ocv-progress-wrap { max-width: 420px; margin: 14px auto 0; }
.ocv-progress-bar { height: 6px; background: var(--vp-c-divider); border-radius: 3px; overflow: hidden; position: relative; }
.ocv-progress-inner { height: 100%; background: var(--vp-c-brand-1); transition: width 0.2s ease; }
/* 不确定进度条：一段蓝色条从左扫到右，循环 */
.ocv-progress-indeterminate {
  position: absolute;
  top: 0; left: 0; bottom: 0;
  width: 35%;
  animation: ocv-indet 1.4s ease-in-out infinite;
}
@keyframes ocv-indet {
  0% { left: -35%; }
  100% { left: 100%; }
}
.ocv-progress-meta { margin: 6px 0 0; font-size: 12px; color: var(--vp-c-text-3); }
.ocv-hint { color: var(--vp-c-danger-1); font-size: 13px; }
.ocv-tip { font-size: 12px; color: var(--vp-c-text-3); margin-top: 10px; line-height: 1.6; }
.ocv-retry-btn { margin-top: 14px; padding: 8px 20px; border: 1px solid var(--vp-c-brand-1); background: var(--vp-c-brand-1); color: #fff; border-radius: 6px; cursor: pointer; font-size: 14px; }
.ocv-retry-btn:hover { opacity: 0.88; }
.ocv-start-btn { padding: 12px 28px; font-size: 15px; font-weight: 600; border-radius: 8px; }
.ocv-toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; padding: 10px; background: var(--vp-c-bg); border: 1px solid var(--vp-c-divider); border-radius: 10px; }
.ocv-tool-group { display: flex; align-items: center; gap: 6px; }
.ocv-tool-group label { font-size: 13px; color: var(--vp-c-text-2); }
.ocv-tool-group select { padding: 4px 8px; border-radius: 6px; border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg); color: var(--vp-c-text-1); font-size: 13px; max-width: 260px; }
.ocv-upload { padding: 4px 10px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg); cursor: pointer; font-size: 13px; }
.ocv-upload input { display: none; }
.ocv-btn { padding: 5px 14px; border-radius: 6px; border: none; background: var(--vp-c-brand-1); color: #fff; cursor: pointer; font-size: 13px; font-weight: 600; }
.ocv-btn:hover { background: var(--vp-c-brand-2); }
.ocv-lang-group { margin-left: auto; }
.ocv-lang-switch { display: inline-flex; border: 1px solid var(--vp-c-divider); border-radius: 6px; overflow: hidden; }
.ocv-lang-btn { padding: 3px 10px; border: none; background: var(--vp-c-bg); color: var(--vp-c-text-2); cursor: pointer; font-size: 12px; border-right: 1px solid var(--vp-c-divider); }
.ocv-lang-btn:last-child { border-right: none; }
.ocv-lang-btn.active { background: var(--vp-c-brand-1); color: #fff; }
.ocv-main { display: grid; grid-template-columns: 1fr 0.9fr 1fr; gap: 12px; margin-top: 12px; }
.ocv-compact .ocv-main { grid-template-columns: 1fr 0.8fr 1fr; }
@media (max-width: 960px) { .ocv-main { grid-template-columns: 1fr; } }
.ocv-panel { background: var(--vp-c-bg); border: 1px solid var(--vp-c-divider); border-radius: 10px; padding: 10px; }
.ocv-panel-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--vp-c-text-1); }
.ocv-canvas { width: 100%; height: auto; border-radius: 6px; background: #fff; }
.ocv-controls { background: var(--vp-c-bg); border: 1px solid var(--vp-c-divider); border-radius: 10px; padding: 12px; }
.ocv-desc { font-size: 12px; color: var(--vp-c-text-2); line-height: 1.6; margin: 4px 0 12px; }
.ocv-param { margin-bottom: 10px; }
.ocv-param-head { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; color: var(--vp-c-text-2); }
.ocv-param-head code { color: var(--vp-c-brand-1); font-weight: 600; }
.ocv-param input[type="range"] { width: 100%; }
.ocv-time { font-size: 13px; margin-top: 8px; color: var(--vp-c-text-1); }
.ocv-error { color: var(--vp-c-danger-1); font-size: 12px; margin-top: 6px; }
.ocv-links { margin-top: 12px; font-size: 13px; }
.ocv-links a { color: var(--vp-c-brand-1); text-decoration: none; font-weight: 500; }
.ocv-links a:hover { text-decoration: underline; }
.ocv-code-panel { margin-top: 12px; background: #1e1e1e; border-radius: 10px; overflow: hidden; }
.ocv-code-head { display: flex; justify-content: space-between; align-items: center; padding: 8px 14px; background: #2d2d2d; color: #d4d4d4; font-size: 12px; font-family: ui-monospace, Menlo, Consolas, monospace; }
.ocv-copy-btn { padding: 3px 10px; border: 1px solid #555; border-radius: 4px; background: #3c3c3c; color: #ddd; font-size: 12px; cursor: pointer; }
.ocv-copy-btn:hover { background: #4c4c4c; }
.ocv-code { margin: 0; padding: 14px; color: #d4d4d4; font-size: 12.5px; line-height: 1.6; font-family: ui-monospace, Menlo, Consolas, monospace; white-space: pre; overflow-x: auto; }
.ocv-foot { font-size: 12px; color: var(--vp-c-text-3); margin-top: 12px; line-height: 1.7; }
.ocv-foot a { color: var(--vp-c-brand-1); text-decoration: none; }
.ocv-foot a:hover { text-decoration: underline; }
</style>
