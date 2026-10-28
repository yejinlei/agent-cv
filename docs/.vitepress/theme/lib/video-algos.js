// ============================================================================
// 视频 / 时序算法的真机实现（基于 OpenCV.js）
// ----------------------------------------------------------------------------
// 这些算法本质上依赖"帧与帧之间"的信息，单张静态图演示不出来：
//   · 光流（LK 稀疏 / Farnebäck 稠密）
//   · 背景减除（帧差法 / MOG2 混合高斯）
//   · 目标跟踪（MeanShift / CamShift）
//
// ⚠️ 本文件的所有写法都基于对本站 opencv.js 构建（11MB 单文件版）的**实测**，
//    下面这些坑是实测出来的，不是照抄文档：
//    1) `Mat.copyTo(dst, mask)` 在这个构建里**会忽略 mask**（整幅覆盖）→ 一律改
//       手动逐像素叠加。
//    2) `cv.COLOR_HSV2RGBA` **不存在**，只有 `COLOR_HSV2RGB` → 走 HSV→RGB→RGBA。
//    3) `cv.calcHist` / `cv.calcBackProject` 在这个构建里**不可用**（任何参数组合
//       都抛 "Cannot convert undefined to unsigned int"）→ 直方图与反向投影用 JS 算。
//       这两个步骤只是"数数"，用 JS 实现同样精确。
//    4) `cv.meanShift` 返回的是 **数组** `[迭代次数, Rect]`；`cv.CamShift` 返回
//       `[RotatedRect, Rect]`；传入的 Rect **不会**被原地更新，必须取返回值。
//
// 统一接口：
//   runVideo(cv, prev, cur, p, state) -> cv.Mat(RGBA)
//     cv     : OpenCV.js Module 实例
//     prev   : 上一帧 RGBA Mat（第一帧为 null）
//     cur    : 当前帧 RGBA Mat
//     p      : 参数对象（键名与 params[].key 对应）
//     state  : 跨帧持久状态（切换算法 / 重置时会被清空）
//   返回   : 处理结果 RGBA Mat，由调用方负责 delete()
// ============================================================================

/* ---------------------------- 通用小工具 ---------------------------- */
function toGray(cv, m) { const g = new cv.Mat(); cv.cvtColor(m, g, cv.COLOR_RGBA2GRAY); return g }

// 4 条线画矩形（不依赖 cv.rectangle 是否存在，兼容性更稳）
function drawRectLines(cv, vis, x, y, w, h, color, thick) {
  const p1 = new cv.Point(x, y), p2 = new cv.Point(x + w, y)
  const p3 = new cv.Point(x + w, y + h), p4 = new cv.Point(x, y + h)
  cv.line(vis, p1, p2, color, thick)
  cv.line(vis, p2, p3, color, thick)
  cv.line(vis, p3, p4, color, thick)
  cv.line(vis, p4, p1, color, thick)
}

// 手动叠加：把 mask 非零处的像素染成 rgba 颜色。
// （原因见文件头注释 1：本构建的 copyTo(mask) 不可信）
function overlayMask(vis, mask, r, g, b) {
  const md = mask.data, vd = vis.data
  for (let i = 0; i < md.length; i++) {
    if (md[i]) { vd[i * 4] = r; vd[i * 4 + 1] = g; vd[i * 4 + 2] = b }
  }
}

// RGBA → HSV（跟踪都在 HSV 空间做；顺带规避 COLOR_HSV2RGBA 缺失）
function rgba2hsv(cv, m) {
  const rgb = new cv.Mat(); cv.cvtColor(m, rgb, cv.COLOR_RGBA2RGB)
  const hsv = new cv.Mat(); cv.cvtColor(rgb, hsv, cv.COLOR_RGB2HSV)
  rgb.delete()
  return hsv
}

/* --------------- 颜色直方图 + 反向投影（JS 实现） --------------- */
// 统计窗口内 H 通道的直方图（180 个 bin），归一化到 0~255 得到查找表。
//
// 两个工程上的必要处理（否则跟踪会"跟背景跑"）：
//   1) 忽略接近灰的像素（饱和度 < satMin）：真实场景背景大多低饱和，
//      把它们排除后，直方图里的"主角"才是彩色目标本身；
//   2) 按饱和度加权：越鲜艳的像素越像目标（背景残留也是灰扑扑的）。
// 若窗口内几乎没有彩色像素（目标是灰的/黑白视频），自动退回不加权的直方图。
function buildHistLut(hsv, rect, satMin = 40) {
  const cols = hsv.cols, rows = hsv.rows, d = hsv.data
  const x0 = Math.max(0, Math.min(rect.x | 0, cols - 4))
  const y0 = Math.max(0, Math.min(rect.y | 0, rows - 4))
  const x1 = Math.min(cols, x0 + Math.max(4, Math.abs(rect.width | 0)))
  const y1 = Math.min(rows, y0 + Math.max(4, Math.abs(rect.height | 0)))
  const hist = new Float64Array(180)

  const accum = (useSatFilter) => {
    hist.fill(0)
    for (let y = y0; y < y1; y++) {
      const base = (y * cols) * 3
      for (let x = x0; x < x1; x++) {
        const i = base + x * 3
        const s = d[i + 1]
        if (useSatFilter) {
          if (s < satMin) continue
          hist[d[i]] += s
        } else {
          hist[d[i]] += 1
        }
      }
    }
    let any = false
    for (let i = 0; i < 180; i++) if (hist[i] > 0) { any = true; break }
    return any
  }

  if (!accum(true)) accum(false) // 没有彩色像素 → 退回普通直方图

  let maxv = 1
  for (let i = 0; i < 180; i++) if (hist[i] > maxv) maxv = hist[i]
  const lut = new Uint8Array(180)
  for (let i = 0; i < 180; i++) lut[i] = Math.round((hist[i] / maxv) * 255)
  return lut
}

// 把跟踪窗口约束回画面内，防止数值漂移导致框跑到画面外/无限变大
function clampWin(win, cols, rows, minSize = 12) {
  let w = Math.max(minSize, Math.min(Math.round(win.width), cols))
  let h = Math.max(minSize, Math.min(Math.round(win.height), rows))
  let x = Math.round(win.x)
  let y = Math.round(win.y)
  x = Math.max(0, Math.min(x, cols - w))
  y = Math.max(0, Math.min(y, rows - h))
  return { x, y, width: w, height: h }
}

// 反向投影：每个像素的亮度 = 它的色相"有多像目标"
function backProjectJS(cv, hsv, lut) {
  const bp = new cv.Mat(hsv.rows, hsv.cols, cv.CV_8UC1)
  const d = hsv.data, o = bp.data
  const n = hsv.rows * hsv.cols
  for (let i = 0; i < n; i++) o[i] = lut[d[i * 3]]
  return bp
}

/* ------------------------- 1) 帧差法 ------------------------- */
const framediff = {
  id: 'framediff',
  name: '帧差法（前后帧相减）',
  group: '背景建模 / 运动检测',
  desc: '相邻两帧逐像素相减，差值超过阈值就判定为"运动"。最简单、最快（一次减法 + 一次阈值），背景静止时效果极好；缺点是只能框出"变化区域"，给不出完整物体轮廓。',
  resetNote: '第 1 帧没有"前一帧"，所以首帧结果为空——这是正常的。',
  params: [
    { key: 'thresh', label: '二值化阈值', min: 3, max: 90, step: 1, value: 25 },
    { key: 'open', label: '去噪核大小', min: 1, max: 11, step: 2, value: 5 },
    { key: 'dim', label: '背景压暗到 (x0.1)', min: 1, max: 9, step: 1, value: 3 },
  ],
  runVideo(cv, prev, cur, p, state) {
    const vis = cur.clone()
    vis.convertTo(vis, -1, p.dim / 10, 0) // 背景压暗，运动区更醒目
    if (!prev) return vis

    const g1 = toGray(cv, prev)
    const g2 = toGray(cv, cur)
    const d = new cv.Mat()
    cv.absdiff(g1, g2, d)
    const th = new cv.Mat()
    cv.threshold(d, th, p.thresh, 255, cv.THRESH_BINARY)
    if (p.open > 1) {
      const k = cv.getStructuringElement(cv.MORPH_ELLIPSE, new cv.Size(p.open, p.open))
      cv.morphologyEx(th, th, cv.MORPH_OPEN, k)
      cv.dilate(th, th, k)
      k.delete()
    }
    overlayMask(vis, th, 255, 50, 50) // 运动区域涂红

    g1.delete(); g2.delete(); d.delete(); th.delete()
    return vis
  },
  code: {
    py: `prev_gray = cv.cvtColor(prev, cv.COLOR_BGR2GRAY)
cur_gray  = cv.cvtColor(cur,  cv.COLOR_BGR2GRAY)
diff = cv.absdiff(prev_gray, cur_gray)          # 逐像素相减
_, mask = cv.threshold(diff, {thresh}, 255, cv.THRESH_BINARY)
mask = cv.morphologyEx(mask, cv.MORPH_OPEN, np.ones(({open},{open}), np.uint8))
motion = cv.bitwise_and(cur, cur, mask=mask)   # 只留下运动像素`,
    cpp: `absdiff(prevGray, curGray, diff);
threshold(diff, mask, {thresh}, 255, THRESH_BINARY);
morphologyEx(mask, mask, MORPH_OPEN, getStructuringElement(MORPH_ELLIPSE, Size({open},{open})));
bitwise_and(cur, cur, motion, mask);`,
    js: `cv.absdiff(prevGray, curGray, diff);
cv.threshold(diff, mask, {thresh}, 255, cv.THRESH_BINARY);
cv.morphologyEx(mask, mask, cv.MORPH_OPEN, k);
// 注意：本站 opencv.js 构建的 copyTo(掩码) 不可靠，叠加用逐像素写
for (let i = 0; i < mask.data.length; i++)
  if (mask.data[i]) { vis.data[i*4] = 255; vis.data[i*4+1] = 50; vis.data[i*4+2] = 50 }`,
  },
}

/* ------------------------- 2) MOG2 背景减除 ------------------------- */
const mog2 = {
  id: 'mog2',
  name: 'MOG2 混合高斯背景建模',
  group: '背景建模 / 运动检测',
  desc: '给每个像素维护若干个高斯分布，长期"占主导"的那个就是背景。新来的像素如果偏离背景分布，就判为前景（运动物体）。好处：能抗树叶晃动、水面波纹这类"背景里的小抖动"。',
  resetNote: '模型刚建立时（前若干帧）会把整幅画面都判为前景——那是在学习背景，1~2 秒后就干净了。',
  params: [
    { key: 'history', label: '历史帧数 history', min: 50, max: 1000, step: 50, value: 300 },
    { key: 'varThreshold', label: '方差阈值 varThreshold', min: 4, max: 80, step: 2, value: 16 },
    { key: 'lr', label: '学习率 (x0.01)', min: 1, max: 20, step: 1, value: 1 },
    { key: 'shadow', label: '检测阴影 0/1', min: 0, max: 1, step: 1, value: 1 },
  ],
  ensure(cv, p, state) {
    const need = !state.mog || state._hist !== p.history || state._shadow !== p.shadow
    if (need) {
      if (state.mog) state.mog.delete()
      state.mog = new cv.BackgroundSubtractorMOG2(p.history, p.varThreshold, p.shadow > 0)
      state._hist = p.history
      state._shadow = p.shadow
      state._vt = p.varThreshold
    } else if (state._vt !== p.varThreshold) {
      if (typeof state.mog.setVarThreshold === 'function') state.mog.setVarThreshold(p.varThreshold)
      state._vt = p.varThreshold
    }
  },
  runVideo(cv, prev, cur, p, state) {
    mog2.ensure(cv, p, state)
    const rgb = new cv.Mat()
    cv.cvtColor(cur, rgb, cv.COLOR_RGBA2RGB)
    const fg = new cv.Mat()
    state.mog.apply(rgb, fg, p.lr / 100)
    rgb.delete()

    // 前景=255(白)，阴影=127(蓝)，背景=0(黑)
    const n = fg.rows * fg.cols, s = fg.data
    const out = new cv.Mat(fg.rows, fg.cols, cv.CV_8UC4)
    const dst = out.data
    for (let i = 0; i < n; i++) {
      const v = s[i]
      let r = 0, g = 0, b = 0
      if (v === 255) { r = 255; g = 255; b = 255 }
      else if (v === 127) { r = 30; g = 80; b = 210 }
      dst[i * 4] = r; dst[i * 4 + 1] = g; dst[i * 4 + 2] = b; dst[i * 4 + 3] = 255
    }
    fg.delete()
    return out
  },
  code: {
    py: `mog2 = cv.createBackgroundSubtractorMOG2({history}, {varThreshold}, {shadow})
while True:
    fgmask = mog2.apply(frame, None, learningRate={lr_float})
    # 前景=255(白)  阴影=127(灰)  背景=0(黑)`,
    cpp: `auto mog2 = createBackgroundSubtractorMOG2({history}, {varThreshold}, {shadow});
Mat fgmask;
mog2->apply(frame, fgmask, {lr_float});`,
    js: `const mog2 = new cv.BackgroundSubtractorMOG2({history}, {varThreshold}, {shadow});
const fgmask = new cv.Mat();
mog2.apply(rgbFrame, fgmask, {lr_float});`,
  },
}

/* ------------------------- 3) LK 稀疏光流 ------------------------- */
const lkflow = {
  id: 'lkflow',
  name: 'LK 稀疏光流（KLT 特征点跟踪）',
  group: '光流',
  desc: '在第 1 帧挑一批"好跟"的角点，然后假设"每个点周围一小块区域在两帧间平移一致"，逐点解 2×2 最小二乘，算出它移动到哪了——这就是 KLT。绿色线段是每个点的运动矢量。',
  resetNote: '首帧挑选特征点，之后每帧都在"上一帧的点"基础上继续跟踪，所以是真正的跨帧跟踪（不是逐帧重新检测）。',
  params: [
    { key: 'maxPoints', label: '特征点上限', min: 20, max: 500, step: 20, value: 150 },
    { key: 'win', label: '窗口大小 winSize', min: 5, max: 41, step: 2, value: 15 },
    { key: 'maxDist', label: '剔除最大位移(px)', min: 5, max: 150, step: 5, value: 45 },
    { key: 'levels', label: '金字塔层数', min: 1, max: 5, step: 1, value: 3 },
  ],
  runVideo(cv, prev, cur, p, state) {
    const g = toGray(cv, cur)
    const vis = cur.clone()

    if (!state.pts) {
      state.pts = new cv.Mat()
      cv.goodFeaturesToTrack(g, state.pts, p.maxPoints, 0.01, 8)
      state.prevGray = g
      state.tracked = 0
      const d0 = state.pts.data32F
      for (let i = 0; i < state.pts.rows; i++) cv.circle(vis, new cv.Point(d0[i * 2], d0[i * 2 + 1]), 2, [255, 200, 0, 255], -1)
      return vis
    }

    if (state.pts.rows > 0) {
      const next = new cv.Mat(), st = new cv.Mat(), err = new cv.Mat()
      cv.calcOpticalFlowPyrLK(state.prevGray, g, state.pts, next, st, err,
        new cv.Size(p.win, p.win), p.levels)
      const n = state.pts.rows
      const a = state.pts.data32F, b = next.data32F, s = st.data
      const keep = []
      for (let i = 0; i < n; i++) {
        if (s[i] === 0) continue
        const x1 = a[i * 2], y1 = a[i * 2 + 1], x2 = b[i * 2], y2 = b[i * 2 + 1]
        if (Math.hypot(x2 - x1, y2 - y1) > p.maxDist) continue // 跟丢的剔除
        cv.line(vis, new cv.Point(x1, y1), new cv.Point(x2, y2), [0, 255, 0, 255], 2)
        cv.circle(vis, new cv.Point(x2, y2), 2, [0, 80, 255, 255], -1)
        keep.push(x2, y2)
      }
      state.tracked = keep.length / 2
      const nk = keep.length ? new cv.Mat(keep.length / 2, 1, cv.CV_32FC2) : new cv.Mat()
      if (keep.length) nk.data32F.set(keep)
      state.pts.delete()
      state.pts = nk
      next.delete(); st.delete(); err.delete()
    }

    state.prevGray.delete()
    state.prevGray = g

    if (state.pts.rows < 12) { // 点跑光了 → 重新挑一批
      state.pts.delete()
      state.pts = new cv.Mat()
      cv.goodFeaturesToTrack(g, state.pts, p.maxPoints, 0.01, 8)
      const d0 = state.pts.data32F
      for (let i = 0; i < state.pts.rows; i++) cv.circle(vis, new cv.Point(d0[i * 2], d0[i * 2 + 1]), 2, [255, 200, 0, 255], -1)
      state.tracked = 0
    }
    return vis
  },
  code: {
    py: `# 第 1 帧：挑一批好跟踪的角点
p0 = cv.goodFeaturesToTrack(old_gray, {maxPoints}, 0.01, 8)
# 之后每帧：用上一帧的点作为输入（链式跟踪）
p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, gray, p0, None,
        winSize=({win},{win}), maxLevel={levels})
good = st.ravel() == 1                      # 只看跟踪成功的点
for a, b in zip(p1[good], p0[good]):
    cv.line(frame, tuple(b.astype(int)), tuple(a.astype(int)), (0,255,0), 2)`,
    cpp: `goodFeaturesToTrack(prevGray, p0, {maxPoints}, 0.01, 8);
calcOpticalFlowPyrLK(prevGray, gray, p0, p1, st, err,
        Size({win},{win}), {levels});
// st[i]==1 表示第 i 个点跟踪成功`,
    js: `cv.goodFeaturesToTrack(prevGray, p0, {maxPoints}, 0.01, 8);
cv.calcOpticalFlowPyrLK(prevGray, gray, p0, p1, st, err,
        new cv.Size({win},{win}), {levels});`,
  },
}

/* ------------------------- 4) Farnebäck 稠密光流 ------------------------- */
const farneback = {
  id: 'farneback',
  name: 'Farnebäck 稠密光流',
  group: '光流',
  desc: '不像 LK 只跟踪几百个角点，Farnebäck 给**每个像素**都算一个运动矢量。做法是用二次多项式拟合邻域，比较两帧多项式系数的变化来估计位移。颜色编码：色相 = 运动方向，亮度 = 运动快慢。',
  resetNote: '第 1 帧没有"上一帧"，所以首帧没有光流——正常。',
  params: [
    { key: 'win', label: '窗口大小 winsize', min: 5, max: 41, step: 2, value: 15 },
    { key: 'levels', label: '金字塔层数 levels', min: 1, max: 6, step: 1, value: 3 },
    { key: 'gain', label: '亮度增益', min: 1, max: 12, step: 1, value: 4 },
  ],
  runVideo(cv, prev, cur, p, state) {
    const g2 = toGray(cv, cur)
    if (!state.prevGray) {
      state.prevGray = g2
      return cur.clone()
    }
    const g1 = state.prevGray
    const flow = new cv.Mat()
    cv.calcOpticalFlowFarneback(g1, g2, flow, 0.5, p.levels, p.win, 3, 5, 1.2, 0)

    const fxy = new cv.MatVector()
    cv.split(flow, fxy)
    const mag = new cv.Mat(), ang = new cv.Mat()
    cv.cartToPolar(fxy.get(0), fxy.get(1), mag, ang, true)

    const nm = new cv.Mat()
    cv.normalize(mag, nm, 0, 255, cv.NORM_MINMAX)
    const v8 = new cv.Mat()
    nm.convertTo(v8, cv.CV_8U, p.gain)
    const h8 = new cv.Mat()
    ang.convertTo(h8, cv.CV_8U, 0.5)              // 0~360° → 0~180（H 通道量程）
    const s8 = new cv.Mat(g2.rows, g2.cols, cv.CV_8UC1)
    s8.setTo(new cv.Scalar(255))

    const mv = new cv.MatVector()
    mv.push_back(h8); mv.push_back(s8); mv.push_back(v8)
    const hsv = new cv.Mat()
    cv.merge(mv, hsv)

    // ⚠️ 本构建没有 COLOR_HSV2RGBA，必须 HSV→RGB→RGBA 两步走
    const rgb = new cv.Mat()
    cv.cvtColor(hsv, rgb, cv.COLOR_HSV2RGB)
    const out = new cv.Mat()
    cv.cvtColor(rgb, out, cv.COLOR_RGB2RGBA)

    state.prevGray.delete()
    state.prevGray = g2

    flow.delete(); fxy.delete(); mag.delete(); ang.delete()
    nm.delete(); v8.delete(); h8.delete(); s8.delete(); mv.delete(); hsv.delete(); rgb.delete()
    return out
  },
  code: {
    py: `# pyr_scale, levels, winsize, iterations, poly_n, poly_sigma, flags
flow = cv.calcOpticalFlowFarneback(prev_gray, gray, None,
         0.5, {levels}, {win}, 3, 5, 1.2, 0)
mag, ang = cv.cartToPolar(flow[...,0], flow[...,1], angleInDegrees=True)
hsv[...,0] = ang / 2                 # 方向 → 色相
hsv[...,1] = 255                     # 饱和度拉满
hsv[...,2] = cv.normalize(mag, None, 0, 255, cv.NORM_MINMAX)  # 速度 → 亮度
vis = cv.cvtColor(hsv, cv.COLOR_HSV2RGB)`,
    cpp: `calcOpticalFlowFarneback(prevGray, gray, flow, 0.5, {levels}, {win}, 3, 5, 1.2, 0);
cartToPolar(flowX, flowY, mag, ang, true);`,
    js: `cv.calcOpticalFlowFarneback(prevGray, gray, flow, 0.5, {levels}, {win}, 3, 5, 1.2, 0);
cv.cartToPolar(fx, fy, mag, ang, true);
// 本站构建需 HSV→RGB→RGBA 两步（没有 COLOR_HSV2RGBA）`,
  },
}

/* ------------------------- 跟踪器公共部分 ------------------------- */
// 用窗口内颜色直方图 + 反向投影准备"目标相似度图"
function prepareProb(cv, hsv, state, rect) {
  const lut = buildHistLut(hsv, rect)
  state.lut = lut
  return backProjectJS(cv, hsv, lut)
}

const WHITE = [0, 255, 0, 255]
const REDPT = [255, 60, 60, 255]

/* ------------------------- 5) MeanShift 跟踪 ------------------------- */
const meanshift = {
  id: 'meanshift',
  name: 'MeanShift 目标跟踪',
  group: '目标跟踪',
  desc: '先给目标拍一张"颜色画像"（色相直方图），下一帧就在附近搜索：把窗口反复往"颜色最像目标"的重心方向挪，直到收敛。窗口大小固定，只找颜色最相似的位置。',
  resetNote: '窗口默认在画面中心；在左侧「当前帧」上直接**拖拽画框**可以重新指定要跟踪的目标。',
  params: [
    { key: 'boxW', label: '初始框宽', min: 30, max: 180, step: 10, value: 90 },
    { key: 'boxH', label: '初始框高', min: 30, max: 180, step: 10, value: 90 },
    { key: 'iters', label: '最大迭代次数', min: 5, max: 60, step: 5, value: 20 },
    { key: 'showProb', label: '显示相似度图 0/1', min: 0, max: 1, step: 1, value: 0 },
  ],
  runVideo(cv, prev, cur, p, state) {
    const vis = cur.clone()
    const hsv = rgba2hsv(cv, cur)

    if (!state.win || state._bw !== p.boxW || state._bh !== p.boxH) {
      state.win = clampWin({
        x: (cur.cols - p.boxW) / 2, y: (cur.rows - p.boxH) / 2,
        width: p.boxW, height: p.boxH,
      }, cur.cols, cur.rows)
      state._bw = p.boxW; state._bh = p.boxH
      state.lut = null
    }
    if (!state.lut || state._needHist) {
      state.lut = buildHistLut(hsv, state.win)
      state._needHist = false
    }
    const bp = backProjectJS(cv, hsv, state.lut)

    const term = new cv.TermCriteria(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, p.iters, 1)
    let rect = state.win
    try {
      // ⚠️ 本构建返回 [迭代次数, Rect] 数组；传入的 Rect 不会被原地更新
      const r = cv.meanShift(bp, new cv.Rect(state.win.x, state.win.y, state.win.width, state.win.height), term)
      if (r && r[1] && typeof r[1].x === 'number') rect = r[1]
      else if (r && typeof r.x === 'number') rect = r
    } catch (e) { rect = state.win }
    state.win = clampWin({ x: rect.x, y: rect.y, width: rect.width, height: rect.height }, cur.cols, cur.rows)

    if (p.showProb > 0) {
      const prob = new cv.Mat()
      cv.cvtColor(bp, prob, cv.COLOR_GRAY2RGBA)
      prob.copyTo(vis)
      prob.delete()
    }
    drawRectLines(cv, vis, state.win.x, state.win.y, state.win.width, state.win.height, WHITE, 2)
    cv.circle(vis, new cv.Point(state.win.x + state.win.width / 2, state.win.y + state.win.height / 2), 3, REDPT, -1)

    bp.delete(); hsv.delete()
    return vis
  },
  code: {
    py: `# 1) 第一帧：给目标区域算 H 通道直方图（"颜色画像"）
roi_hist = cv.calcHist([hsv], [0], mask, [180], [0,180])
cv.normalize(roi_hist, roi_hist, 0, 255, cv.NORM_MINMAX)
# 2) 之后每帧：反向投影 → MeanShift 迭代找最像的位置
dst = cv.calcBackProject([hsv], [0], roi_hist, [0,180], 1)
_, track_window = cv.meanShift(dst, track_window, term_crit)`,
    cpp: `calcBackProject(&hsv, 1, chans, roiHist, dst, ranges);
meanShift(dst, trackWindow, termCrit);   // 窗口被移动到目标重心`,
    js: `// 本站 opencv.js 构建的 calcHist/calcBackProject 不可用，
// 这里直方图与反向投影用 JS 等价的统计实现（同样是精确的"数数"）
const lut = buildHistLut(hsv, win);
const bp  = backProjectJS(hsv, lut);
const r = cv.meanShift(bp, new cv.Rect(win.x, win.y, win.width, win.height), term);
const rect = r[1];   // ⚠️ 返回 [迭代次数, Rect]`,
  },
}

/* ------------------------- 6) CamShift 跟踪 ------------------------- */
const camshift = {
  id: 'camshift',
  name: 'CamShift 自适应跟踪',
  group: '目标跟踪',
  desc: 'MeanShift 的升级版：窗口大小和目标一起自适应——目标靠近相机就变大、远离就变小，还能给出目标的旋转角度（旋转椭圆）。CamShift 全称里的 "Continuously Adaptive" 就是这个意思。',
  resetNote: '窗口默认在画面中心；在左侧「当前帧」上直接**拖拽画框**可以指定要跟踪的目标。',
  params: [
    { key: 'boxW', label: '初始框宽', min: 30, max: 180, step: 10, value: 90 },
    { key: 'boxH', label: '初始框高', min: 30, max: 180, step: 10, value: 90 },
    { key: 'iters', label: '最大迭代次数', min: 5, max: 60, step: 5, value: 20 },
    { key: 'showProb', label: '显示相似度图 0/1', min: 0, max: 1, step: 1, value: 0 },
  ],
  runVideo(cv, prev, cur, p, state) {
    const vis = cur.clone()
    const hsv = rgba2hsv(cv, cur)

    if (!state.win || state._bw !== p.boxW || state._bh !== p.boxH) {
      state.win = clampWin({
        x: (cur.cols - p.boxW) / 2, y: (cur.rows - p.boxH) / 2,
        width: p.boxW, height: p.boxH,
      }, cur.cols, cur.rows)
      state._bw = p.boxW; state._bh = p.boxH
      state.lut = null
    }
    if (!state.lut || state._needHist) {
      state.lut = buildHistLut(hsv, state.win)
      state._needHist = false
    }
    const bp = backProjectJS(cv, hsv, state.lut)
    const term = new cv.TermCriteria(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, p.iters, 1)

    let rot = null
    try {
      // ⚠️ 本构建返回 [RotatedRect, Rect]
      const r = cv.CamShift(bp, new cv.Rect(state.win.x, state.win.y, state.win.width, state.win.height), term)
      if (r && r[0] && r[0].center && r[0].size) rot = r[0]
    } catch (e) { rot = null }

    if (p.showProb > 0) {
      const prob = new cv.Mat()
      cv.cvtColor(bp, prob, cv.COLOR_GRAY2RGBA)
      prob.copyTo(vis)
      prob.delete()
    }

    if (rot) {
      const cx = rot.center.x, cy = rot.center.y
      const w = rot.size.width / 2, h = rot.size.height / 2
      const ang = (rot.angle || 0) * Math.PI / 180
      const ca = Math.cos(ang), sa = Math.sin(ang)
      const P = (dx, dy) => new cv.Point(cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)
      const c1 = P(-w, -h), c2 = P(w, -h), c3 = P(w, h), c4 = P(-w, h)
      cv.line(vis, c1, c2, WHITE, 2)
      cv.line(vis, c2, c3, WHITE, 2)
      cv.line(vis, c3, c4, WHITE, 2)
      cv.line(vis, c4, c1, WHITE, 2)
      cv.circle(vis, new cv.Point(cx, cy), 3, REDPT, -1)
      state.win = clampWin({
        x: cx - rot.size.width / 2, y: cy - rot.size.height / 2,
        width: rot.size.width, height: rot.size.height,
      }, cur.cols, cur.rows)
      state.angle = rot.angle
      state.size = [Math.round(rot.size.width), Math.round(rot.size.height)]
    } else {
      drawRectLines(cv, vis, state.win.x, state.win.y, state.win.width, state.win.height, WHITE, 2)
    }

    bp.delete(); hsv.delete()
    return vis
  },
  code: {
    py: `dst = cv.calcBackProject([hsv], [0], roi_hist, [0,180], 1)
ret, track_window = cv.CamShift(dst, track_window, term_crit)
# ret = ((中心x, 中心y), (宽, 高), 旋转角) —— 大小与角度都自适应
cv.ellipse(frame, ret, (0,255,0), 2)`,
    cpp: `calcBackProject(&hsv, 1, chans, roiHist, dst, ranges);
RotatedRect rot = CamShift(dst, trackWindow, termCrit);`,
    js: `const r = cv.CamShift(bp, new cv.Rect(win.x, win.y, win.width, win.height), term);
const rot = r[0];    // RotatedRect: center / size / angle
const box = r[1];    // 外接矩形`,
  },
}

/* ------------------------------ 导出 ------------------------------ */
export const VIDEO_ALGOS = [framediff, mog2, lkflow, farneback, meanshift, camshift]

export const VIDEO_ALGO_MAP = VIDEO_ALGOS.reduce((m, a) => { m[a.id] = a; return m }, {})

/* 释放 state 里持有的所有 Mat，避免内存泄漏 */
export function resetVideoState(state) {
  if (!state) return
  for (const k of Object.keys(state)) {
    const v = state[k]
    if (v && typeof v.delete === 'function') {
      try { v.delete() } catch (_) {}
    }
  }
  for (const k of Object.keys(state)) delete state[k]
}

/* 简单的 {key} 占位符替换，用于把当前参数值插进代码片段 */
export function fillCode(tpl, params, extra = {}) {
  const all = { ...params, ...extra }
  return String(tpl).replace(/\{(\w+)\}/g, (m, k) => (all[k] !== undefined ? all[k] : m))
}
