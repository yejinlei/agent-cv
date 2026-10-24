<template>
  <div class="ocv-root">
    <!-- 加载状态 -->
    <div v-if="status !== 'ready'" class="ocv-loading">
      <div class="ocv-spinner"></div>
      <p>{{ statusText }}</p>
      <p class="ocv-hint" v-if="status === 'error'">{{ errorMsg }}</p>
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
            上传图片
            <input type="file" accept="image/*" @change="onUpload" />
          </label>
        </div>
        <div class="ocv-tool-group">
          <label>算法</label>
          <select v-model="currentFilter">
            <optgroup v-for="g in groups" :key="g" :label="g">
              <option v-for="f in filtersByGroup(g)" :key="f.id" :value="f.id">{{ f.name }}</option>
            </optgroup>
          </select>
        </div>
        <div class="ocv-tool-group">
          <button class="ocv-btn" @click="run">▶ 运行</button>
        </div>
      </div>

      <!-- 主体：原图 / 参数 / 结果 -->
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
        </div>

        <div class="ocv-panel">
          <div class="ocv-panel-title">结果</div>
          <canvas ref="dstCanvas" class="ocv-canvas"></canvas>
        </div>
      </div>

      <p class="ocv-foot">
        全部运算在你的浏览器里用 <b>OpenCV.js（WebAssembly）</b> 实时完成，不上传任何图片到服务器——所以本站可以纯静态部署在 GitHub Pages 上。
      </p>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'

const BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.BASE_URL) || '/'
const OCV_URL = BASE + 'lib/opencv.js'
const HAAR_XML_URL = BASE + 'lib/haarcascade_frontalface_default.xml'
const SAMPLE_BASE = BASE + 'samples/'

const samples = [
  { file: 'scene.png', name: '彩色色块（分割 / 聚类）' },
  { file: 'shapes.png', name: '黑白形状（轮廓 / 拟合）' },
  { file: 'corners.png', name: '棋盘格（角点 / 特征）' },
  { file: 'coins.png', name: '圆点（霍夫圆 / 连通域）' },
  { file: 'edges.png', name: '几何线条（边缘 / 霍夫直线）' },
  { file: 'noisy.png', name: '椒盐噪声（滤波去噪）' },
  { file: 'doc.png', name: '文档条码（阈值 / 形态学）' },
  { file: 'tex.png', name: '纹理（梯度 / 纹理分析）' },
]

const status = ref('loading')
const statusText = ref('正在加载本站内置的 OpenCV.js（约 11 MB，本地运算，不依赖外部 CDN）…')
const errorMsg = ref('')
const srcCanvas = ref(null)
const dstCanvas = ref(null)
const currentSample = ref('scene.png')
const currentFilter = ref('canny')
const paramValues = reactive({})
const lastMs = ref(-1)
const runError = ref('')
let cv = null
let srcMat = null
let timer = null
let haarXml = null
let haarDetector = null

/* ---------------- 算法注册表 ---------------- */
/* 每个算法：id/name/group/desc/params/run(srcRGBA, p) -> 返回展示用 Mat（RGBA） */
const filters = [
  // —— 图像预处理 ——
  {
    id: 'grayscale', name: '灰度化', group: '图像预处理',
    desc: '把彩色图转成灰度图，是绝大多数算法第一步。',
    params: [],
    run: (s) => { const d = new cv.Mat(); cv.cvtColor(s, d, cv.COLOR_RGBA2GRAY); return gray2rgba(d) },
  },
  {
    id: 'gaussian', name: '高斯滤波', group: '图像预处理',
    desc: '按钟形权重加权平均去噪，可分离卷积提速。',
    params: [
      { key: 'ksize', label: '核大小 ksize', min: 1, max: 21, step: 2, value: 5 },
      { key: 'sigma', label: 'σ 标准差', min: 0, max: 6, step: 0.5, value: 0 },
    ],
    run: (s, p) => { const d = new cv.Mat(); cv.GaussianBlur(s, d, new cv.Size(p.ksize, p.ksize), p.sigma, p.sigma); return d },
  },
  {
    id: 'median', name: '中值滤波', group: '图像预处理',
    desc: '邻域取中位数，椒盐噪声的克星。',
    params: [{ key: 'ksize', label: '核大小 ksize', min: 3, max: 15, step: 2, value: 3 }],
    run: (s, p) => { const d = new cv.Mat(); cv.medianBlur(s, d, p.ksize); return d },
  },
  {
    id: 'bilateral', name: '双边滤波', group: '图像预处理',
    desc: '保边去噪：颜色近且位置近才参与平均。',
    params: [
      { key: 'd', label: '邻域直径 d', min: 1, max: 15, step: 2, value: 9 },
      { key: 'sigmaColor', label: '颜色 σ', min: 10, max: 200, step: 10, value: 75 },
      { key: 'sigmaSpace', label: '空间 σ', min: 10, max: 200, step: 10, value: 75 },
    ],
    run: (s, p) => { const d = new cv.Mat(); cv.bilateralFilter(s, d, p.d, p.sigmaColor, p.sigmaSpace); return d },
  },
  {
    id: 'equalize', name: '直方图均衡化', group: '图像预处理',
    desc: '拉伸灰度分布，提升整体对比度。',
    params: [],
    run: (s) => { const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const e = new cv.Mat(); cv.equalizeHist(g, e); g.delete(); return gray2rgba(e) },
  },
  {
    id: 'filter2d', name: '锐化滤波 (filter2D)', group: '图像预处理',
    desc: '自定义卷积核做锐化，突出细节。',
    params: [{ key: 'alpha', label: '锐化强度', min: 0, max: 5, step: 1, value: 1 }],
    run: (s, p) => {
      const d = new cv.Mat()
      const a = p.alpha
      const kernel = cv.matFromArray(3, 3, cv.CV_32F, [0, -a, 0, -a, 1 + 4 * a, -a, 0, -a, 0])
      cv.filter2D(s, d, cv.CV_8U, kernel)
      kernel.delete()
      return d
    },
  },
  // —— 边缘与基元 ——
  {
    id: 'sobel', name: 'Sobel 梯度', group: '边缘与基元',
    desc: '一阶差分算水平/垂直梯度，边缘定位的基础。',
    params: [{ key: 'ksize', label: '核大小', min: 1, max: 7, step: 2, value: 3 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const gx = new cv.Mat(), gy = new cv.Mat(), abs = new cv.Mat()
      cv.Sobel(g, gx, cv.CV_16S, 1, 0, p.ksize)
      cv.Sobel(g, gy, cv.CV_16S, 0, 1, p.ksize)
      cv.convertScaleAbs(gx, gx); cv.convertScaleAbs(gy, gy)
      cv.addWeighted(gx, 0.5, gy, 0.5, 0, abs)
      g.delete(); gx.delete(); gy.delete(); return gray2rgba(abs)
    },
  },
  {
    id: 'laplacian', name: 'Laplacian 拉普拉斯', group: '边缘与基元',
    desc: '二阶导数，对细节和噪声都敏感。',
    params: [{ key: 'ksize', label: '核大小', min: 1, max: 7, step: 2, value: 3 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const d = new cv.Mat()
      cv.Laplacian(g, d, cv.CV_16S, p.ksize, 1, 0, cv.BORDER_DEFAULT)
      const a = new cv.Mat(); cv.convertScaleAbs(d, a)
      g.delete(); d.delete(); return gray2rgba(a)
    },
  },
  {
    id: 'canny', name: 'Canny 边缘检测', group: '边缘与基元',
    desc: '经典多阶段边缘检测：去噪→梯度→非极大抑制→双阈值。',
    params: [
      { key: 't1', label: '低阈值', min: 0, max: 300, step: 5, value: 50 },
      { key: 't2', label: '高阈值', min: 0, max: 500, step: 5, value: 150 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const d = new cv.Mat(); cv.Canny(g, d, p.t1, p.t2, 3, false)
      g.delete(); return gray2rgba(d)
    },
  },
  {
    id: 'threshold', name: '阈值二值化 / Otsu', group: '边缘与基元',
    desc: 'Otsu 自动求最佳阈值，把图分成前景背景。',
    params: [
      { key: 'thresh', label: '手动阈值（Otsu 时忽略）', min: 0, max: 255, step: 1, value: 127 },
      { key: 'otsu', label: '启用 Otsu（0 关 / 1 开）', min: 0, max: 1, step: 1, value: 1 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const d = new cv.Mat()
      const type = p.otsu ? cv.THRESH_BINARY + cv.THRESH_OTSU : cv.THRESH_BINARY
      cv.threshold(g, d, p.thresh, 255, type)
      g.delete(); return gray2rgba(d)
    },
  },
  {
    id: 'adaptivethresh', name: '自适应阈值', group: '边缘与基元',
    desc: '局部算阈值，适合光照不均的文档。',
    params: [
      { key: 'block', label: '邻域块 blockSize', min: 3, max: 51, step: 2, value: 11 },
      { key: 'C', label: '常数 C', min: -10, max: 20, step: 1, value: 2 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const d = new cv.Mat()
      cv.adaptiveThreshold(g, d, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, p.block, p.C)
      g.delete(); return gray2rgba(d)
    },
  },
  {
    id: 'morphology', name: '形态学（腐蚀/膨胀/开/闭）', group: '边缘与基元',
    desc: '用结构元素改变形状：开运算去噪点，闭运算补空洞。',
    params: [
      { key: 'op', label: '操作 0侵蚀1膨胀2开3闭', min: 0, max: 3, step: 1, value: 2 },
      { key: 'ksize', label: '核大小', min: 3, max: 21, step: 2, value: 5 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const bw = new cv.Mat(); cv.threshold(g, bw, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
      const d = new cv.Mat()
      const kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, new cv.Size(p.ksize, p.ksize))
      const ops = [cv.MORPH_ERODE, cv.MORPH_DILATE, cv.MORPH_OPEN, cv.MORPH_CLOSE]
      cv.morphologyEx(bw, d, ops[p.op], kernel)
      g.delete(); bw.delete(); kernel.delete(); return gray2rgba(d)
    },
  },
  {
    id: 'houghlines', name: '霍夫直线检测', group: '边缘与基元',
    desc: '参数空间投票找出图中的直线。',
    params: [
      { key: 'threshold', label: '投票阈值', min: 10, max: 200, step: 5, value: 60 },
      { key: 'minLen', label: '最短长度', min: 5, max: 200, step: 5, value: 50 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const edges = new cv.Mat(); cv.Canny(g, edges, 50, 150)
      const lines = new cv.Mat()
      cv.HoughLinesP(edges, lines, 1, Math.PI / 180, p.threshold, p.minLen, 10)
      const out = s.clone()
      for (let i = 0; i < lines.rows; i++) {
        const x1 = lines.data32S[i * 4], y1 = lines.data32S[i * 4 + 1]
        const x2 = lines.data32S[i * 4 + 2], y2 = lines.data32S[i * 4 + 3]
        cv.line(out, new cv.Point(x1, y1), new cv.Point(x2, y2), new cv.Scalar(255, 0, 0, 255), 2)
      }
      g.delete(); edges.delete(); lines.delete(); return out
    },
  },
  {
    id: 'houghcircles', name: '霍夫圆检测', group: '边缘与基元',
    desc: '沿梯度投票找圆心，检测圆形目标。',
    params: [
      { key: 'minDist', label: '圆心最小间距', min: 10, max: 200, step: 5, value: 40 },
      { key: 'param2', label: '圆心累加阈值', min: 10, max: 120, step: 2, value: 40 },
      { key: 'minR', label: '最小半径', min: 5, max: 200, step: 5, value: 15 },
      { key: 'maxR', label: '最大半径', min: 20, max: 300, step: 10, value: 120 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const b = new cv.Mat(); cv.medianBlur(g, b, 5)
      const circles = new cv.Mat()
      cv.HoughCircles(b, circles, cv.HOUGH_GRADIENT, 1.2, p.minDist, 100, p.param2, p.minR, p.maxR)
      const out = s.clone()
      for (let i = 0; i < circles.cols; i++) {
        const x = circles.data32F[i * 3], y = circles.data32F[i * 3 + 1], r = circles.data32F[i * 3 + 2]
        cv.circle(out, new cv.Point(x, y), r, new cv.Scalar(0, 255, 0, 255), 2)
        cv.circle(out, new cv.Point(x, y), 2, new cv.Scalar(255, 0, 0, 255), 3)
      }
      g.delete(); b.delete(); circles.delete(); return out
    },
  },
  {
    id: 'harris', name: 'Harris 角点', group: '边缘与基元',
    desc: '用梯度协方差矩阵的响应值找角点。',
    params: [
      { key: 'block', label: '邻域窗口', min: 2, max: 10, step: 1, value: 2 },
      { key: 'ksize', label: 'Sobel 核', min: 3, max: 7, step: 2, value: 3 },
      { key: 'thresh', label: '阈值（×1e-4）', min: 1, max: 500, step: 1, value: 100 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const dst = new cv.Mat()
      cv.cornerHarris(g, dst, p.block, p.ksize, 0.04)
      const out = s.clone()
      const t = p.thresh * 1e-4
      for (let y = 0; y < dst.rows; y++) for (let x = 0; x < dst.cols; x++) {
        if (dst.floatAt(y, x) > t) cv.circle(out, new cv.Point(x, y), 3, new cv.Scalar(255, 0, 0, 255), 1)
      }
      g.delete(); dst.delete(); return out
    },
  },
  {
    id: 'gftt', name: 'Shi-Tomasi 角点 (GFTT)', group: '边缘与基元',
    desc: '用较小特征值判角点，工程界角点首选。',
    params: [
      { key: 'maxCorners', label: '最大角点数', min: 10, max: 500, step: 10, value: 100 },
      { key: 'quality', label: '质量系数 ×0.01', min: 1, max: 50, step: 1, value: 1 },
      { key: 'minDist', label: '最小间距', min: 1, max: 50, step: 1, value: 10 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const corners = new cv.Mat()
      cv.goodFeaturesToTrack(g, corners, p.maxCorners, p.quality * 0.01, p.minDist)
      const out = s.clone()
      for (let i = 0; i < corners.rows; i++) {
        const x = corners.data32F[i * 2], y = corners.data32F[i * 2 + 1]
        cv.circle(out, new cv.Point(x, y), 4, new cv.Scalar(0, 255, 0, 255), 2)
      }
      g.delete(); corners.delete(); return out
    },
  },
  {
    id: 'orb', name: 'ORB 特征点', group: '边缘与基元',
    desc: 'FAST 角点 + rBRIEF 描述子，免费快速的二合一特征。',
    params: [{ key: 'n', label: '最多特征点数', min: 50, max: 1000, step: 50, value: 300 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const orb = new cv.ORB(p.n)
      const kp = new cv.KeyPointVector(), des = new cv.Mat()
      orb.detect(g, kp)
      const out = s.clone()
      for (let i = 0; i < kp.size(); i++) {
        const pt = kp.get(i).pt
        cv.circle(out, new cv.Point(pt.x, pt.y), 3, new cv.Scalar(255, 0, 0, 255), 1)
      }
      g.delete(); orb.delete(); kp.delete(); des.delete(); return out
    },
  },
  {
    id: 'contours', name: '轮廓提取 + 多边形逼近', group: '边缘与基元',
    desc: 'findContours 找轮廓，approxPolyDP 用折线概括。',
    params: [{ key: 'eps', label: '逼近精度 ×0.005 周长', min: 1, max: 20, step: 1, value: 4 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const bw = new cv.Mat(); cv.threshold(g, bw, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
      const contours = new cv.MatVector(), hier = new cv.Mat()
      cv.findContours(bw, contours, hier, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
      const out = s.clone()
      for (let i = 0; i < contours.size(); i++) {
        const cnt = contours.get(i)
        const area = cv.contourArea(cnt)
        if (area < 50) continue
        const eps = 0.005 * p.eps * cv.arcLength(cnt, true)
        const approx = new cv.Mat()
        cv.approxPolyDP(cnt, approx, eps, true)
        const pts = []
        for (let j = 0; j < approx.rows; j++) pts.push(new cv.Point(approx.data32S[j * 2], approx.data32S[j * 2 + 1]))
        for (let j = 0; j < pts.length; j++) cv.line(out, pts[j], pts[(j + 1) % pts.length], new cv.Scalar(255, 0, 0, 255), 2)
        approx.delete(); cnt.delete()
      }
      g.delete(); bw.delete(); hier.delete(); contours.delete(); return out
    },
  },
  // —— 分割 ——
  {
    id: 'kmeans', name: 'K-Means 颜色聚类', group: '图像分割',
    desc: '把像素按颜色聚成 K 类，图像量化/卡通风。',
    params: [{ key: 'K', label: '聚类数 K', min: 2, max: 16, step: 1, value: 6 }],
    run: (s, p) => {
      const data = new cv.Mat(s.rows * s.cols, 3, cv.CV_32F)
      let idx = 0
      for (let y = 0; y < s.rows; y++) for (let x = 0; x < s.cols; x++) {
        const o = (y * s.cols + x) * 4
        data.floatPtr(idx, 0)[0] = s.data[o]
        data.floatPtr(idx, 0)[1] = s.data[o + 1]
        data.floatPtr(idx, 0)[2] = s.data[o + 2]
        idx++
      }
      const K = p.K
      const labels = new cv.Mat(), centers = new cv.Mat()
      const crit = new cv.TermCriteria(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
      cv.kmeans(data, K, labels, crit, 3, cv.KMEANS_PP_CENTERS, centers)
      const out = s.clone()
      for (let i = 0; i < s.rows * s.cols; i++) {
        const l = labels.intAt(i, 0)
        const o = i * 4
        out.data[o] = centers.floatAt(l, 0)
        out.data[o + 1] = centers.floatAt(l, 1)
        out.data[o + 2] = centers.floatAt(l, 2)
      }
      data.delete(); labels.delete(); centers.delete(); crit.delete(); return out
    },
  },
  {
    id: 'inrange', name: '颜色阈值分割 (inRange)', group: '图像分割',
    desc: '按 HSV 色相范围提取特定颜色区域。',
    params: [
      { key: 'hmin', label: '色相下限 H', min: 0, max: 179, step: 1, value: 0 },
      { key: 'hmax', label: '色相上限 H', min: 0, max: 179, step: 1, value: 20 },
    ],
    run: (s, p) => {
      const hsv = new cv.Mat(); cv.cvtColor(s, hsv, cv.COLOR_RGBA2RGB)
      cv.cvtColor(hsv, hsv, cv.COLOR_RGB2HSV)
      const mask = new cv.Mat()
      const lo = new cv.Mat(hsv.rows, hsv.cols, hsv.type(), new cv.Scalar(p.hmin, 60, 60, 0))
      const hi = new cv.Mat(hsv.rows, hsv.cols, hsv.type(), new cv.Scalar(p.hmax, 255, 255, 255))
      cv.inRange(hsv, lo, hi, mask)
      lo.delete(); hi.delete(); hsv.delete(); return gray2rgba(mask)
    },
  },
  {
    id: 'distance', name: '距离变换', group: '图像分割',
    desc: '每个前景像素到最近背景的距离，分水岭的骨架。',
    params: [],
    run: (s) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const bw = new cv.Mat(); cv.threshold(g, bw, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
      const d = new cv.Mat()
      cv.distanceTransform(bw, d, cv.DIST_L2, 3)
      cv.normalize(d, d, 0, 255, cv.NORM_MINMAX)
      const out = new cv.Mat(); d.convertTo(out, cv.CV_8U)
      g.delete(); bw.delete(); d.delete(); return gray2rgba(out)
    },
  },
  {
    id: 'connected', name: '连通域分析', group: '图像分割',
    desc: '给每个连通块一个编号并随机着色，工业计数神器。',
    params: [{ key: 'minArea', label: '最小面积过滤', min: 0, max: 3000, step: 50, value: 100 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const bw = new cv.Mat(); cv.threshold(g, bw, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
      const labels = new cv.Mat(), stats = new cv.Mat(), cent = new cv.Mat()
      const n = cv.connectedComponentsWithStats(bw, labels, stats, cent)
      const out = new cv.Mat(s.rows, s.cols, s.type(), new cv.Scalar(0, 0, 0, 255))
      const rng = (i) => (i * 97 + 40) % 255
      for (let y = 0; y < labels.rows; y++) for (let x = 0; x < labels.cols; x++) {
        const l = labels.intAt(y, x)
        if (l === 0) continue
        if (stats.intAt(l, cv.CC_STAT_AREA) < p.minArea) continue
        const o = (y * labels.cols + x) * 4
        out.data[o] = rng(l); out.data[o + 1] = rng(l * 3); out.data[o + 2] = rng(l * 7); out.data[o + 3] = 255
      }
      g.delete(); bw.delete(); labels.delete(); stats.delete(); cent.delete(); return out
    },
  },
  {
    id: 'watershed', name: '分水岭分割', group: '图像分割',
    desc: '把图当海拔灌水，水汇合处拉警戒线——切粘连物体。',
    params: [],
    run: (s) => {
      const src = s.clone()
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const bw = new cv.Mat(); cv.threshold(g, bw, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
      const kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, new cv.Size(3, 3))
      const sure_bg = new cv.Mat(); cv.dilate(bw, sure_bg, kernel)
      const dist = new cv.Mat(); cv.distanceTransform(bw, dist, cv.DIST_L2, 3)
      cv.normalize(dist, dist, 0, 1.0, cv.NORM_MINMAX)
      const sure_fg = new cv.Mat(); cv.threshold(dist, sure_fg, 0.5, 255, cv.THRESH_BINARY)
      sure_fg.convertTo(sure_fg, cv.CV_8U)
      const unknown = new cv.Mat(); cv.subtract(sure_bg, sure_fg, unknown)
      const nf = new cv.Mat()
      cv.connectedComponents(sure_fg, nf)
      const markers = new cv.Mat()
      nf.convertTo(markers, cv.CV_32S)
      for (let i = 0; i < markers.rows; i++) for (let j = 0; j < markers.cols; j++) markers.intPtr(i, j)[0] += 1
      markers.setTo(new cv.Scalar(0), unknown)
      cv.watershed(src, markers)
      const out = s.clone()
      for (let y = 0; y < markers.rows; y++) for (let x = 0; x < markers.cols; x++) {
        if (markers.intAt(y, x) === -1) {
          const o = (y * markers.cols + x) * 4
          out.data[o] = 255; out.data[o + 1] = 0; out.data[o + 2] = 0; out.data[o + 3] = 255
        }
      }
      src.delete(); g.delete(); bw.delete(); kernel.delete(); sure_bg.delete(); dist.delete()
      sure_fg.delete(); unknown.delete(); nf.delete(); markers.delete()
      return out
    },
  },
  // —— 匹配与几何 ——
  {
    id: 'template', name: '模板匹配 (matchTemplate)', group: '匹配与几何',
    desc: '拿模板在图上滑动找最相似位置，最简单的目标定位。',
    params: [{ key: 'tplRatio', label: '模板占比 ×0.05', min: 1, max: 8, step: 1, value: 4 }],
    run: (s, p) => {
      const ratio = p.tplRatio * 0.05
      const tw = Math.round(s.cols * ratio), th = Math.round(s.rows * ratio)
      const x0 = Math.round((s.cols - tw) / 2), y0 = Math.round((s.rows - th) / 2)
      const rect = new cv.Rect(x0, y0, tw, th)
      const tpl = s.roi(rect)
      const res = new cv.Mat()
      cv.matchTemplate(s, tpl, res, cv.TM_CCOEFF_NORMED)
      const mm = cv.minMaxLoc(res)
      const out = s.clone()
      cv.rectangle(out, mm.maxLoc, new cv.Point(mm.maxLoc.x + tw, mm.maxLoc.y + th), new cv.Scalar(255, 0, 0, 255), 2)
      tpl.delete(); res.delete()
      return out
    },
  },
  {
    id: 'gradient-flow', name: '稠密光流 (Farnebäck) 示意', group: '匹配与几何',
    desc: '对整幅图估算像素级运动矢量（此处用平移模拟一帧）。',
    params: [{ key: 'shift', label: '模拟位移(像素)', min: 1, max: 20, step: 1, value: 5 }],
    run: (s, p) => {
      const g1 = new cv.Mat(); cv.cvtColor(s, g1, cv.COLOR_RGBA2GRAY)
      const M = cv.matFromArray(2, 3, cv.CV_64F, [1, 0, p.shift, 0, 1, 0])
      const g2 = new cv.Mat()
      cv.warpAffine(g1, g2, M, new cv.Size(s.cols, s.rows))
      const flow = new cv.Mat()
      cv.calcOpticalFlowFarneback(g1, g2, flow, 0.5, 3, 15, 3, 5, 1.2, 0)
      const out = s.clone()
      const step = 12
      for (let y = step; y < s.rows - step; y += step) for (let x = step; x < s.cols - step; x += step) {
        const fx = flow.floatAt(y, x, 0), fy = flow.floatAt(y, x, 1)
        if (Math.hypot(fx, fy) < 0.3) continue
        cv.line(out, new cv.Point(x, y), new cv.Point(x + fx * 3, y + fy * 3), new cv.Scalar(255, 0, 0, 255), 1)
      }
      M.delete(); g1.delete(); g2.delete(); flow.delete()
      return out
    },
  },
  {
    id: 'sobel-hog', name: '梯度幅值热力图', group: '匹配与几何',
    desc: '把梯度强度映射成伪彩色，直观看到结构强度（HOG 的可视化基础）。',
    params: [{ key: 'ksize', label: 'Sobel 核', min: 1, max: 7, step: 2, value: 3 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const gx = new cv.Mat(), gy = new cv.Mat()
      cv.Sobel(g, gx, cv.CV_32F, 1, 0, p.ksize)
      cv.Sobel(g, gy, cv.CV_32F, 0, 1, p.ksize)
      const mag = new cv.Mat()
      cv.magnitude(gx, gy, mag)
      cv.normalize(mag, mag, 0, 255, cv.NORM_MINMAX)
      const m8 = new cv.Mat(); mag.convertTo(m8, cv.CV_8U)
      const color = new cv.Mat()
      cv.applyColorMap(m8, color, cv.COLORMAP_JET)
      cv.cvtColor(color, color, cv.COLOR_RGB2RGBA)
      g.delete(); gx.delete(); gy.delete(); mag.delete(); m8.delete(); return color
    },
  },
  // —— 图像预处理（补充）——
  {
    id: 'clahe', name: 'CLAHE 限制对比度自适应均衡', group: '图像预处理',
    desc: '分块做直方图均衡并裁剪对比度，专治局部过暗/过曝。',
    params: [
      { key: 'clip', label: '对比度上限 clipLimit', min: 1, max: 10, step: 0.5, value: 3 },
      { key: 'tile', label: '分块边长', min: 2, max: 16, step: 1, value: 8 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const clahe = new cv.CLAHE(p.clip, new cv.Size(p.tile, p.tile))
      const d = new cv.Mat(); clahe.apply(g, d); clahe.delete()
      g.delete(); return gray2rgba(d)
    },
  },
  {
    id: 'gabor', name: 'Gabor 纹理滤波', group: '图像预处理',
    desc: '方向 + 频率选择性的滤波核，能提出某一方向的纹理条带。',
    params: [
      { key: 'ksize', label: '核大小', min: 3, max: 31, step: 2, value: 15 },
      { key: 'sigma', label: 'σ 包络宽度', min: 1, max: 10, step: 0.5, value: 4 },
      { key: 'theta', label: '方向角 θ (度)', min: 0, max: 170, step: 10, value: 45 },
      { key: 'lambda', label: '波长 λ', min: 3, max: 20, step: 1, value: 8 },
    ],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const half = (p.ksize - 1) / 2
      const th = (p.theta * Math.PI) / 180
      const gamma = 0.5
      const kernel = []
      for (let y = -half; y <= half; y++) {
        for (let x = -half; x <= half; x++) {
          const xr = x * Math.cos(th) + y * Math.sin(th)
          const yr = -x * Math.sin(th) + y * Math.cos(th)
          kernel.push(Math.exp(-(xr * xr + gamma * gamma * yr * yr) / (2 * p.sigma * p.sigma)) * Math.cos((2 * Math.PI * xr) / p.lambda))
        }
      }
      const k = cv.matFromArray(p.ksize, p.ksize, cv.CV_32F, kernel)
      const resp = new cv.Mat()
      cv.filter2D(g, resp, cv.CV_32F, k)
      cv.normalize(resp, resp, 0, 255, cv.NORM_MINMAX)
      const d = new cv.Mat(); resp.convertTo(d, cv.CV_8U)
      g.delete(); k.delete(); resp.delete(); return gray2rgba(d)
    },
  },
  {
    id: 'lbp', name: 'LBP 局部二值模式', group: '图像预处理',
    desc: '把每个像素与 8 邻域比大小编成 0/1 码，得到纹理编码图。',
    params: [],
    run: (s) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const out = new cv.Mat.zeros(g.rows, g.cols, cv.CV_8UC1)
      const nb = [[-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1]]
      for (let y = 1; y < g.rows - 1; y++) {
        for (let x = 1; x < g.cols - 1; x++) {
          const c = g.ucharAt(y, x)
          let code = 0
          for (let b = 0; b < 8; b++) if (g.ucharAt(y + nb[b][0], x + nb[b][1]) >= c) code |= 1 << b
          out.ucharPtr(y, x)[0] = code
        }
      }
      g.delete(); return gray2rgba(out)
    },
  },
  {
    id: 'haarwavelet', name: 'Haar 小波一级分解', group: '图像预处理',
    desc: '左上=低频近似，其余三块=水平/垂直/对角细节。',
    params: [],
    run: (s) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const w = g.cols, h = g.rows, hw = w >> 1, hh = h >> 1
      const out = new cv.Mat.zeros(h, w, cv.CV_8UC1)
      for (let y = 0; y < hh; y++) {
        for (let x = 0; x < hw; x++) {
          const a = g.ucharAt(2 * y, 2 * x), b = g.ucharAt(2 * y, 2 * x + 1)
          const c = g.ucharAt(2 * y + 1, 2 * x), d = g.ucharAt(2 * y + 1, 2 * x + 1)
          out.ucharPtr(y, x)[0] = (a + b + c + d) / 4
          out.ucharPtr(y, hw + x)[0] = Math.max(0, Math.min(255, 128 + (a + b - c - d) / 4))
          out.ucharPtr(hh + y, x)[0] = Math.max(0, Math.min(255, 128 + (a - b + c - d) / 4))
          out.ucharPtr(hh + y, hw + x)[0] = Math.max(0, Math.min(255, 128 + (a - b - c + d) / 4))
        }
      }
      g.delete(); return gray2rgba(out)
    },
  },
  // —— 特征检测（补充）——
  {
    id: 'fast', name: 'FAST 角点', group: '边缘与基元',
    desc: '圆周 16 像素亮度判定，比 Harris 快一个量级的角点检测。',
    params: [{ key: 'th', label: '亮度阈值', min: 1, max: 80, step: 1, value: 20 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const det = new cv.FastFeatureDetector(p.th, true)
      const kp = new cv.KeyPointVector()
      det.detect(g, kp, new cv.Mat())
      const out = s.clone()
      for (let i = 0; i < kp.size(); i++) {
        const pt = kp.get(i).pt
        cv.circle(out, new cv.Point(pt.x, pt.y), 3, new cv.Scalar(255, 0, 0, 255), 1)
      }
      g.delete(); kp.delete(); det.delete(); return out
    },
  },
  {
    id: 'brisk', name: 'BRISK 特征点', group: '边缘与基元',
    desc: 'AGAST 检测 + 同心圆采样二进制描述子，尺度旋转不变。',
    params: [{ key: 'th', label: '阈值', min: 5, max: 100, step: 5, value: 30 }],
    run: (s, p) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const det = new cv.BRISK(p.th, 3, 1.0)
      const kp = new cv.KeyPointVector()
      det.detect(g, kp, new cv.Mat())
      const out = s.clone()
      for (let i = 0; i < kp.size(); i++) {
        const pt = kp.get(i).pt
        cv.circle(out, new cv.Point(pt.x, pt.y), 3, new cv.Scalar(0, 160, 255, 255), 1)
      }
      g.delete(); kp.delete(); det.delete(); return out
    },
  },
  {
    id: 'akaze', name: 'AKAZE 特征点', group: '边缘与基元',
    desc: '非线性扩散尺度空间 + M-LDB 描述子，免费特征里的性能王。',
    params: [],
    run: (s) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const det = new cv.AKAZE()
      const kp = new cv.KeyPointVector()
      det.detect(g, kp, new cv.Mat())
      const out = s.clone()
      for (let i = 0; i < kp.size(); i++) {
        const pt = kp.get(i).pt
        cv.circle(out, new cv.Point(pt.x, pt.y), 3, new cv.Scalar(0, 200, 0, 255), 1)
      }
      g.delete(); kp.delete(); det.delete(); return out
    },
  },
  {
    id: 'mser', name: 'MSER 稳定极值区域', group: '边缘与基元',
    desc: '在连续阈值上保持不变的区域，抗仿射、常用来找文字和斑块。',
    params: [],
    run: (s) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const mser = new cv.MSER()
      const kp = new cv.KeyPointVector()
      mser.detect(g, kp)
      const out = s.clone()
      for (let i = 0; i < kp.size(); i++) {
        const k = kp.get(i)
        const r = Math.max(3, k.size / 2)
        cv.rectangle(out, new cv.Point(k.pt.x - r, k.pt.y - r), new cv.Point(k.pt.x + r, k.pt.y + r), new cv.Scalar(255, 0, 255, 255), 1)
      }
      kp.delete(); mser.delete()
      g.delete(); return out
    },
  },
  {
    id: 'blob', name: 'SimpleBlob 斑点检测', group: '边缘与基元',
    desc: '按面积、圆度、惯量比筛选斑点，适合细胞/气泡计数。',
    params: [],
    run: (s) => {
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      const det = new cv.SimpleBlobDetector()
      const kp = new cv.KeyPointVector()
      det.detect(g, kp)
      const out = s.clone()
      for (let i = 0; i < kp.size(); i++) {
        const k = kp.get(i)
        cv.circle(out, new cv.Point(k.pt.x, k.pt.y), Math.max(3, k.size / 2), new cv.Scalar(0, 255, 255, 255), 2)
      }
      g.delete(); kp.delete(); det.delete()
      return out
    },
  },
  // —— 特征匹配与几何 ——
  {
    id: 'bfmatch', name: 'ORB + BFMatcher 特征匹配', group: '匹配与几何',
    desc: '左：原图；右：旋转平移后的同一张图。连线是暴力匹配结果。',
    params: [{ key: 'max', label: '最多画多少条', min: 10, max: 200, step: 10, value: 60 }],
    run: (s, p) => {
      const w = s.cols, h = s.rows
      const M = cv.getRotationMatrix2D(new cv.Point(w / 2, h / 2), 6, 1)
      M.data64F[2] += 12; M.data64F[5] += 6
      const s2 = new cv.Mat()
      cv.warpAffine(s, s2, M, new cv.Size(w, h), cv.INTER_LINEAR, cv.BORDER_REPLICATE)
      M.delete()
      const g1 = new cv.Mat(), g2 = new cv.Mat()
      cv.cvtColor(s, g1, cv.COLOR_RGBA2GRAY); cv.cvtColor(s2, g2, cv.COLOR_RGBA2GRAY)
      const orb = new cv.ORB(500)
      const k1 = new cv.KeyPointVector(), k2 = new cv.KeyPointVector()
      const d1 = new cv.Mat(), d2 = new cv.Mat(), m0 = new cv.Mat()
      orb.detectAndCompute(g1, m0, k1, d1)
      orb.detectAndCompute(g2, m0, k2, d2)
      const bf = new cv.BFMatcher(cv.NORM_HAMMING, true)
      const matches = new cv.DMatchVector()
      bf.match(d1, d2, matches)
      const canvas = new cv.Mat(h, w * 2, cv.CV_8UC4, new cv.Scalar(245, 245, 245, 255))
      const r1 = canvas.roi(new cv.Rect(0, 0, w, h)); s.copyTo(r1); r1.delete()
      const r2 = canvas.roi(new cv.Rect(w, 0, w, h)); s2.copyTo(r2); r2.delete()
      const n = Math.min(matches.size(), p.max)
      for (let i = 0; i < n; i++) {
        const mt = matches.get(i)
        const a = k1.get(mt.queryIdx).pt, b = k2.get(mt.trainIdx).pt
        cv.line(canvas, new cv.Point(a.x, a.y), new cv.Point(b.x + w, b.y), new cv.Scalar(0, 200, 0, 255), 1)
      }
      g1.delete(); g2.delete(); s2.delete(); d1.delete(); d2.delete(); m0.delete()
      k1.delete(); k2.delete(); bf.delete(); orb.delete(); matches.delete()
      return canvas
    },
  },
  {
    id: 'homography', name: 'RANSAC 单应校正', group: '匹配与几何',
    desc: '用匹配点估单应矩阵，把右侧歪斜的图"掰正"回来。',
    params: [{ key: 'thr', label: 'RANSAC 重投影阈值', min: 1, max: 10, step: 1, value: 3 }],
    run: (s, p) => {
      const w = s.cols, h = s.rows
      const M = cv.getRotationMatrix2D(new cv.Point(w / 2, h / 2), 10, 0.95)
      M.data64F[2] += 15; M.data64F[5] += 8
      const s2 = new cv.Mat()
      cv.warpAffine(s, s2, M, new cv.Size(w, h), cv.INTER_LINEAR, cv.BORDER_REPLICATE)
      const g1 = new cv.Mat(), g2 = new cv.Mat()
      cv.cvtColor(s, g1, cv.COLOR_RGBA2GRAY); cv.cvtColor(s2, g2, cv.COLOR_RGBA2GRAY)
      const orb = new cv.ORB(800)
      const k1 = new cv.KeyPointVector(), k2 = new cv.KeyPointVector()
      const d1 = new cv.Mat(), d2 = new cv.Mat(), m0 = new cv.Mat()
      orb.detectAndCompute(g1, m0, k1, d1)
      orb.detectAndCompute(g2, m0, k2, d2)
      const bf = new cv.BFMatcher(cv.NORM_HAMMING, true)
      const matches = new cv.DMatchVector()
      bf.match(d1, d2, matches)
      const p1 = [], p2 = []
      for (let i = 0; i < matches.size(); i++) {
        const mt = matches.get(i)
        const a = k1.get(mt.queryIdx).pt, b = k2.get(mt.trainIdx).pt
        p1.push(a.x, a.y); p2.push(b.x, b.y)
      }
      let aligned = s2.clone()
      if (p1.length >= 16) {
        const s1m = cv.matFromArray(p1.length / 2, 1, cv.CV_32FC2, p1)
        const s2m = cv.matFromArray(p2.length / 2, 1, cv.CV_32FC2, p2)
        const mask = new cv.Mat()
        const Hm = cv.findHomography(s2m, s1m, cv.RANSAC, p.thr, mask)
        const fixed = new cv.Mat()
        cv.warpPerspective(s2, fixed, Hm, new cv.Size(w, h))
        aligned.delete(); aligned = fixed
        Hm.delete(); mask.delete(); s1m.delete(); s2m.delete()
      }
      const canvas = new cv.Mat(h, w * 2, cv.CV_8UC4, new cv.Scalar(245, 245, 245, 255))
      const r1 = canvas.roi(new cv.Rect(0, 0, w, h)); s.copyTo(r1); r1.delete()
      const r2 = canvas.roi(new cv.Rect(w, 0, w, h)); aligned.copyTo(r2); r2.delete()
      g1.delete(); g2.delete(); s2.delete(); aligned.delete(); d1.delete(); d2.delete(); m0.delete()
      k1.delete(); k2.delete(); bf.delete(); orb.delete(); matches.delete(); M.delete()
      return canvas
    },
  },
  {
    id: 'lkflow', name: 'LK 稀疏光流追踪', group: '匹配与几何',
    desc: '左：原图角点；右：移动后的图，绿线是光流跟踪到的位移。',
    params: [{ key: 'max', label: '角点数', min: 10, max: 200, step: 10, value: 60 }],
    run: (s, p) => {
      const w = s.cols, h = s.rows
      const M = cv.matFromArray(2, 3, cv.CV_64F, [1, 0, 10, 0, 1, 5])
      const s2 = new cv.Mat()
      cv.warpAffine(s, s2, M, new cv.Size(w, h), cv.INTER_LINEAR, cv.BORDER_REPLICATE)
      M.delete()
      const g1 = new cv.Mat(), g2 = new cv.Mat()
      cv.cvtColor(s, g1, cv.COLOR_RGBA2GRAY); cv.cvtColor(s2, g2, cv.COLOR_RGBA2GRAY)
      const p0 = new cv.Mat()
      cv.goodFeaturesToTrack(g1, p0, p.max, 0.01, 10)
      const p1 = new cv.Mat(), st = new cv.Mat(), err = new cv.Mat()
      if (p0.rows > 0) cv.calcOpticalFlowPyrLK(g1, g2, p0, p1, st, err)
      const canvas = new cv.Mat(h, w * 2, cv.CV_8UC4, new cv.Scalar(245, 245, 245, 255))
      const r1 = canvas.roi(new cv.Rect(0, 0, w, h)); s.copyTo(r1); r1.delete()
      const r2 = canvas.roi(new cv.Rect(w, 0, w, h)); s2.copyTo(r2); r2.delete()
      for (let i = 0; i < p0.rows; i++) {
        const x0 = p0.data32F[i * 2], y0 = p0.data32F[i * 2 + 1]
        const x1 = p1.data32F[i * 2], y1 = p1.data32F[i * 2 + 1]
        cv.circle(canvas, new cv.Point(x0, y0), 2, new cv.Scalar(255, 0, 0, 255), 2)
        cv.circle(canvas, new cv.Point(x1 + w, y1), 2, new cv.Scalar(255, 0, 0, 255), 2)
        cv.line(canvas, new cv.Point(x0, y0), new cv.Point(x1 + w, y1), new cv.Scalar(0, 200, 0, 255), 1)
      }
      g1.delete(); g2.delete(); s2.delete(); p0.delete(); p1.delete(); st.delete(); err.delete()
      return canvas
    },
  },
  // —— 传统目标检测 ——
  {
    id: 'facedetect', name: 'Viola-Jones 人脸检测', group: '传统目标检测',
    desc: 'Haar 特征 + AdaBoost 级联，经典实时人脸检测（示例图非人脸时可能检不到）。',
    params: [
      { key: 'scale', label: '尺度步长', min: 1.05, max: 1.5, step: 0.05, value: 1.1 },
      { key: 'minN', label: '最小邻居数', min: 2, max: 10, step: 1, value: 3 },
    ],
    run: (s, p) => {
      if (!haarXml) throw new Error('人脸模型尚未加载完成，请稍候重试')
      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)
      cv.equalizeHist(g, g)
      const faces = new cv.RectVector()
      haarDetector.detectMultiScale(g, faces, p.scale, p.minN, 0, new cv.Size(30, 30))
      const out = s.clone()
      for (let i = 0; i < faces.size(); i++) {
        const f = faces.get(i)
        cv.rectangle(out, new cv.Point(f.x, f.y), new cv.Point(f.x + f.width, f.y + f.height), new cv.Scalar(0, 255, 0, 255), 2)
      }
      g.delete(); faces.delete()
      return out
    },
  },
]

const groups = [...new Set(filters.map((f) => f.group))]
const filtersByGroup = (g) => filters.filter((f) => f.group === g)
const activeFilter = computed(() => filters.find((f) => f.id === currentFilter.value) || filters[0])

/* ---------------- 工具函数 ---------------- */
function gray2rgba(gray) {
  const rgba = new cv.Mat()
  cv.cvtColor(gray, rgba, cv.COLOR_GRAY2RGBA)
  gray.delete()
  return rgba
}
function rgba2color(rgba) {
  const rgb = new cv.Mat()
  cv.cvtColor(rgba, rgb, cv.COLOR_RGBA2RGB)
  return rgb
}

/* ---------------- 加载 opencv.js ---------------- */
function loadOpencv() {
  return new Promise((resolve, reject) => {
    // 统一出口：把真正的 Module 对象写回 window.cv，供其它逻辑直接使用
    const finish = (mod) => {
      if (mod && mod.Mat) { window.cv = mod; resolve(mod) }
      else reject(new Error('opencv.js 已加载，但未暴露可用的 Mat'))
    }
    // 已经加载过（含 HMR 热更新场景）
    if (window.cv) {
      if (window.cv.Mat) return finish(window.cv)
      // 该构建使用 MODULARIZE，window.cv 是一个 Promise，需要 await 它拿到 Module
      if (typeof window.cv.then === 'function') {
        return window.cv.then(finish).catch(reject)
      }
    }
    const prev = document.getElementById('opencv-js-loader')
    if (prev) prev.remove()
    const s = document.createElement('script')
    s.id = 'opencv-js-loader'
    s.src = OCV_URL
    s.async = true
    s.onload = async () => {
      let mod = window.cv
      // 情况一：window.cv 是 Promise（本构建即如此），await 后即得 Module
      if (mod && typeof mod.then === 'function') {
        try { mod = await mod } catch (e) { return reject(e) }
        return finish(mod)
      }
      // 情况二：已经是就绪的 Module
      if (mod && mod.Mat) return finish(mod)
      // 情况三：老式构建，等 onRuntimeInitialized 回调（并加超时兜底）
      if (mod) {
        let settled = false
        const done = () => { if (!settled) { settled = true; finish(mod) } }
        mod['onRuntimeInitialized'] = done
        const t = setInterval(() => {
          if (mod.Mat) { settled = true; clearInterval(t); finish(mod) }
        }, 200)
        setTimeout(() => clearInterval(t), 60000)
      } else {
        reject(new Error('opencv.js 已加载，但未暴露 cv 全局对象'))
      }
    }
    s.onerror = () => reject(new Error('无法加载 ' + OCV_URL))
    document.head.appendChild(s)
  })
}

/* ---------------- 加载级联人脸模型 ---------------- */
async function loadHaar() {
  if (haarXml) return
  try {
    const res = await fetch(HAAR_XML_URL)
    if (!res.ok) return
    const txt = await res.text()
    cv.FS_createDataFile('/', 'haar_face.xml', txt, true, false, false)
    const cc = new cv.CascadeClassifier()
    if (cc.load('haar_face.xml')) {
      haarDetector = cc
      haarXml = txt
    } else {
      cc.delete()
    }
  } catch (e) { /* 模型不可用时静默跳过，人脸检测会给出提示 */ }
}

/* ---------------- 图像加载 ---------------- */
function drawToSrcCanvas(img) {
  const c = srcCanvas.value
  const maxW = 480
  const scale = Math.min(1, maxW / img.width, maxW / img.height)
  c.width = Math.round(img.width * scale)
  c.height = Math.round(img.height * scale)
  const ctx = c.getContext('2d')
  ctx.clearRect(0, 0, c.width, c.height)
  ctx.drawImage(img, 0, 0, c.width, c.height)
}
function loadSample() {
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.onload = () => { drawToSrcCanvas(img); run() }
  img.onerror = () => { runError.value = '示例图加载失败：' + currentSample.value }
  img.src = SAMPLE_BASE + currentSample.value
}
function onUpload(e) {
  const file = e.target.files && e.target.files[0]
  if (!file) return
  const url = URL.createObjectURL(file)
  const img = new Image()
  img.onload = () => { drawToSrcCanvas(img); URL.revokeObjectURL(url); run() }
  img.src = url
}

/* ---------------- 执行 ---------------- */
function initParams() {
  for (const k of Object.keys(paramValues)) delete paramValues[k]
  for (const p of activeFilter.value.params) paramValues[p.key] = p.value
}
function scheduleRun() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(run, 120)
}
function run() {
  if (!cv || !srcCanvas.value) return
  runError.value = ''
  const c = srcCanvas.value
  const dcanvas = dstCanvas.value
  dcanvas.width = c.width
  dcanvas.height = c.height
  let src = null, out = null
  try {
    src = cv.imread(c)
    const t0 = performance.now()
    const params = {}
    for (const k of Object.keys(paramValues)) params[k] = paramValues[k]
    out = activeFilter.value.run(src, params)
    const t1 = performance.now()
    if (out) cv.imshow(dcanvas, out)
    lastMs.value = t1 - t0
  } catch (err) {
    runError.value = '运行出错：' + (err && err.message ? err.message : String(err))
    const ctx = dcanvas.getContext('2d')
    ctx.clearRect(0, 0, dcanvas.width, dcanvas.height)
    ctx.fillStyle = '#eee'; ctx.fillRect(0, 0, dcanvas.width, dcanvas.height)
    ctx.fillStyle = '#999'; ctx.font = '14px sans-serif'
    ctx.fillText('该算法在当前 OpenCV.js 构建中可能不可用', 16, 28)
  } finally {
    if (src) src.delete()
    if (out && out !== src) { try { out.delete() } catch (e) {} }
  }
}

onMounted(async () => {
  try {
    cv = await loadOpencv()
    status.value = 'ready'
    await nextTick()
    initParams()
    loadSample()
    loadHaar()
  } catch (e) {
    status.value = 'error'
    errorMsg.value = (e && e.message) || String(e)
    statusText.value = 'OpenCV.js 加载失败'
  }
})

// 切换算法时重置参数并重跑
import { watch } from 'vue'
watch(currentFilter, async () => {
  initParams()
  await nextTick()
  run()
})
</script>

<style scoped>
.ocv-root { margin: 24px 0; }
.ocv-loading { padding: 48px; text-align: center; color: var(--vp-c-text-2); border: 1px dashed var(--vp-c-divider); border-radius: 10px; }
.ocv-spinner { width: 34px; height: 34px; margin: 0 auto 16px; border: 3px solid var(--vp-c-divider); border-top-color: var(--vp-c-brand-1); border-radius: 50%; animation: ocv-spin 0.9s linear infinite; }
@keyframes ocv-spin { to { transform: rotate(360deg); } }
.ocv-hint { color: var(--vp-c-danger-1); font-size: 13px; }
.ocv-toolbar { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; padding: 12px; background: var(--vp-c-bg-soft); border: 1px solid var(--vp-c-divider); border-radius: 10px; }
.ocv-tool-group { display: flex; align-items: center; gap: 6px; }
.ocv-tool-group label { font-size: 13px; color: var(--vp-c-text-2); }
.ocv-tool-group select { padding: 4px 8px; border-radius: 6px; border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg); color: var(--vp-c-text-1); font-size: 13px; max-width: 240px; }
.ocv-upload { padding: 4px 10px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg); cursor: pointer; font-size: 13px; }
.ocv-upload input { display: none; }
.ocv-btn { padding: 5px 14px; border-radius: 6px; border: none; background: var(--vp-c-brand-1); color: #fff; cursor: pointer; font-size: 13px; font-weight: 600; }
.ocv-btn:hover { background: var(--vp-c-brand-2); }
.ocv-main { display: grid; grid-template-columns: 1fr 0.9fr 1fr; gap: 14px; margin-top: 14px; }
@media (max-width: 860px) { .ocv-main { grid-template-columns: 1fr; } }
.ocv-panel { background: var(--vp-c-bg-soft); border: 1px solid var(--vp-c-divider); border-radius: 10px; padding: 10px; }
.ocv-panel-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--vp-c-text-1); }
.ocv-canvas { width: 100%; height: auto; border-radius: 6px; background: #fff; image-rendering: auto; }
.ocv-controls { background: var(--vp-c-bg-soft); border: 1px solid var(--vp-c-divider); border-radius: 10px; padding: 12px; }
.ocv-desc { font-size: 12px; color: var(--vp-c-text-2); line-height: 1.6; margin: 4px 0 12px; }
.ocv-param { margin-bottom: 12px; }
.ocv-param-head { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; color: var(--vp-c-text-2); }
.ocv-param-head code { color: var(--vp-c-brand-1); font-weight: 600; }
.ocv-param input[type="range"] { width: 100%; }
.ocv-time { font-size: 13px; margin-top: 8px; color: var(--vp-c-text-1); }
.ocv-error { color: var(--vp-c-danger-1); font-size: 12px; margin-top: 6px; }
.ocv-foot { font-size: 12px; color: var(--vp-c-text-3); margin-top: 14px; line-height: 1.7; }
</style>
