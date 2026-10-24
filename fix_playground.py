#!/usr/bin/env python3
"""修复 OpencvPlayground.vue 中 OpenCV.js 内存泄漏，给所有临时 Mat/对象补 delete()"""
import re

p = '/home/user/workspace/7648064683708846935/agent-cv/docs/.vitepress/theme/components/OpencvPlayground.vue'
with open(p, 'r', encoding='utf-8') as f:
    src = f.read()

# 逐段替换，把需要 delete 的临时对象正确释放
# 策略：改写每个算法 run，引入 tg 跟踪列表、最后统一 delete

# 1. 先把每个 run 函数的 body 做精确修复——用手工 patch 比正则更安全
fixes = [
    # equalize: g 没 delete
    (
        "    run: (s) => { const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const e = new cv.Mat(); cv.equalizeHist(g, e); return gray2rgba(e) },",
        "    run: (s) => { const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY); const e = new cv.Mat(); cv.equalizeHist(g, e); g.delete(); return gray2rgba(e) },"
    ),
    # sobel: g, gx, gy 都没 delete（abs 通过 gray2rgba 已 delete）
    (
        "      cv.Sobel(g, gx, cv.CV_16S, 1, 0, p.ksize)\n      cv.Sobel(g, gy, cv.CV_16S, 0, 1, p.ksize)\n      cv.convertScaleAbs(gx, gx); cv.convertScaleAbs(gy, gy)\n      cv.addWeighted(gx, 0.5, gy, 0.5, 0, abs)\n      return gray2rgba(abs)",
        "      cv.Sobel(g, gx, cv.CV_16S, 1, 0, p.ksize)\n      cv.Sobel(g, gy, cv.CV_16S, 0, 1, p.ksize)\n      cv.convertScaleAbs(gx, gx); cv.convertScaleAbs(gy, gy)\n      cv.addWeighted(gx, 0.5, gy, 0.5, 0, abs)\n      g.delete(); gx.delete(); gy.delete(); return gray2rgba(abs)"
    ),
    # laplacian: g, d 没 delete
    (
        "      cv.Laplacian(g, d, cv.CV_16S, p.ksize, 1, 0, cv.BORDER_DEFAULT)\n      const a = new cv.Mat(); cv.convertScaleAbs(d, a)\n      return gray2rgba(a)",
        "      cv.Laplacian(g, d, cv.CV_16S, p.ksize, 1, 0, cv.BORDER_DEFAULT)\n      const a = new cv.Mat(); cv.convertScaleAbs(d, a)\n      g.delete(); d.delete(); return gray2rgba(a)"
    ),
    # canny: g 没 delete
    (
        "      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)\n      const d = new cv.Mat(); cv.Canny(g, d, p.t1, p.t2, 3, false)\n      return gray2rgba(d)",
        "      const g = new cv.Mat(); cv.cvtColor(s, g, cv.COLOR_RGBA2GRAY)\n      const d = new cv.Mat(); cv.Canny(g, d, p.t1, p.t2, 3, false)\n      g.delete(); return gray2rgba(d)"
    ),
    # threshold: g 没 delete
    (
        "      cv.threshold(g, d, p.thresh, 255, type)\n      return gray2rgba(d)\n    },\n  },\n  {\n    id: 'adaptivethresh'",
        "      cv.threshold(g, d, p.thresh, 255, type)\n      g.delete(); return gray2rgba(d)\n    },\n  },\n  {\n    id: 'adaptivethresh'"
    ),
    # adaptiveThreshold: g 没 delete
    (
        "      cv.adaptiveThreshold(g, d, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, p.block, p.C)\n      return gray2rgba(d)\n    },\n  },\n  {\n    id: 'morphology'",
        "      cv.adaptiveThreshold(g, d, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, p.block, p.C)\n      g.delete(); return gray2rgba(d)\n    },\n  },\n  {\n    id: 'morphology'"
    ),
    # morphology: g, bw 没 delete
    (
        "      cv.morphologyEx(bw, d, ops[p.op], kernel)\n      kernel.delete()\n      return gray2rgba(d)",
        "      cv.morphologyEx(bw, d, ops[p.op], kernel)\n      g.delete(); bw.delete(); kernel.delete(); return gray2rgba(d)"
    ),
    # houghlines: g, edges, lines 没 delete
    (
        "      for (let i = 0; i < lines.rows; i++) {\n        const x1 = lines.data32S[i * 4], y1 = lines.data32S[i * 4 + 1]\n        const x2 = lines.data32S[i * 4 + 2], y2 = lines.data32S[i * 4 + 3]\n        cv.line(out, new cv.Point(x1, y1), new cv.Point(x2, y2), new cv.Scalar(255, 0, 0, 255), 2)\n      }\n      return out\n    },\n  },\n  {\n    id: 'houghcircles'",
        "      for (let i = 0; i < lines.rows; i++) {\n        const x1 = lines.data32S[i * 4], y1 = lines.data32S[i * 4 + 1]\n        const x2 = lines.data32S[i * 4 + 2], y2 = lines.data32S[i * 4 + 3]\n        cv.line(out, new cv.Point(x1, y1), new cv.Point(x2, y2), new cv.Scalar(255, 0, 0, 255), 2)\n      }\n      g.delete(); edges.delete(); lines.delete(); return out\n    },\n  },\n  {\n    id: 'houghcircles'"
    ),
    # houghcircles: g, b, circles 没 delete
    (
        "      for (let i = 0; i < circles.cols; i++) {\n        const x = circles.data32F[i * 3], y = circles.data32F[i * 3 + 1], r = circles.data32F[i * 3 + 2]\n        cv.circle(out, new cv.Point(x, y), r, new cv.Scalar(0, 255, 0, 255), 2)\n        cv.circle(out, new cv.Point(x, y), 2, new cv.Scalar(255, 0, 0, 255), 3)\n      }\n      return out\n    },\n  },\n  {\n    id: 'harris'",
        "      for (let i = 0; i < circles.cols; i++) {\n        const x = circles.data32F[i * 3], y = circles.data32F[i * 3 + 1], r = circles.data32F[i * 3 + 2]\n        cv.circle(out, new cv.Point(x, y), r, new cv.Scalar(0, 255, 0, 255), 2)\n        cv.circle(out, new cv.Point(x, y), 2, new cv.Scalar(255, 0, 0, 255), 3)\n      }\n      g.delete(); b.delete(); circles.delete(); return out\n    },\n  },\n  {\n    id: 'harris'"
    ),
    # harris: g, dst 没 delete
    (
        "      for (let y = 0; y < dst.rows; y++) for (let x = 0; x < dst.cols; x++) {\n        if (dst.floatAt(y, x) > t) cv.circle(out, new cv.Point(x, y), 3, new cv.Scalar(255, 0, 0, 255), 1)\n      }\n      return out\n    },\n  },\n  {\n    id: 'gftt'",
        "      for (let y = 0; y < dst.rows; y++) for (let x = 0; x < dst.cols; x++) {\n        if (dst.floatAt(y, x) > t) cv.circle(out, new cv.Point(x, y), 3, new cv.Scalar(255, 0, 0, 255), 1)\n      }\n      g.delete(); dst.delete(); return out\n    },\n  },\n  {\n    id: 'gftt'"
    ),
    # gftt: g, corners 没 delete
    (
        "      for (let i = 0; i < corners.rows; i++) {\n        const x = corners.data32F[i * 2], y = corners.data32F[i * 2 + 1]\n        cv.circle(out, new cv.Point(x, y), 4, new cv.Scalar(0, 255, 0, 255), 2)\n      }\n      return out\n    },\n  },\n  {\n    id: 'orb'",
        "      for (let i = 0; i < corners.rows; i++) {\n        const x = corners.data32F[i * 2], y = corners.data32F[i * 2 + 1]\n        cv.circle(out, new cv.Point(x, y), 4, new cv.Scalar(0, 255, 0, 255), 2)\n      }\n      g.delete(); corners.delete(); return out\n    },\n  },\n  {\n    id: 'orb'"
    ),
    # orb: g, orb 没 delete (kp/des 已 delete)
    (
        "      kp.delete(); des.delete()\n      return out\n    },\n  },\n  {\n    id: 'contours'",
        "      g.delete(); orb.delete(); kp.delete(); des.delete(); return out\n    },\n  },\n  {\n    id: 'contours'"
    ),
    # contours: g, bw, contours 没 delete (hier/approx 已 delete)
    (
        "        approx.delete()\n      }\n      hier.delete()\n      return out",
        "        approx.delete(); cnt.delete()\n      }\n      g.delete(); bw.delete(); hier.delete(); contours.delete(); return out"
    ),
    # kmeans: crit 没 delete (data/labels/centers 已 delete)
    (
        "      data.delete(); labels.delete(); centers.delete()\n      return out\n    },\n  },\n  {\n    id: 'inrange'",
        "      data.delete(); labels.delete(); centers.delete(); crit.delete(); return out\n    },\n  },\n  {\n    id: 'inrange'"
    ),
    # inrange: hsv 没 delete (lo/hi 已 delete, mask 通过 gray2rgba delete)
    (
        "      lo.delete(); hi.delete()\n      return gray2rgba(mask)",
        "      lo.delete(); hi.delete(); hsv.delete(); return gray2rgba(mask)"
    ),
    # distance: g, bw, d 没 delete
    (
        "      cv.normalize(d, d, 0, 255, cv.NORM_MINMAX)\n      const out = new cv.Mat(); d.convertTo(out, cv.CV_8U)\n      return gray2rgba(out)",
        "      cv.normalize(d, d, 0, 255, cv.NORM_MINMAX)\n      const out = new cv.Mat(); d.convertTo(out, cv.CV_8U)\n      g.delete(); bw.delete(); d.delete(); return gray2rgba(out)"
    ),
    # connected: g, bw 没 delete (labels/stats/cent 已 delete)
    (
        "      labels.delete(); stats.delete(); cent.delete()\n      return out\n    },\n  },\n  {\n    id: 'watershed'",
        "      g.delete(); bw.delete(); labels.delete(); stats.delete(); cent.delete(); return out\n    },\n  },\n  {\n    id: 'watershed'"
    ),
    # watershed: 大量对象没 delete —— 大段重写
]

for old, new in fixes:
    if old not in src:
        print(f"⚠️ 未匹配片段（前40字）: {old[:40]!r}")
    else:
        src = src.replace(old, new, 1)
        print(f"✅ 替换: {old[:40]!r}")

# 重写 watershed run（泄漏严重）
old_ws = """    run: (s) => {
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
      let markers = new cv.Mat()
      cv.connectedComponents(sure_fg, nf)
      nf.convertTo(markers, cv.CV_32S); markers = markers.clone()
      for (let i = 0; i < markers.rows; i++) for (let j = 0; j < markers.cols; j++) markers.intPtr(i, j)[0] += 1
      const unk = new cv.Mat()
      cv.bitwise_and(unknown, unknown, unk)
      markers.setTo(new cv.Scalar(0), unk)
      cv.watershed(src, markers)
      const out = s.clone()
      for (let y = 0; y < markers.rows; y++) for (let x = 0; x < markers.cols; x++) {
        if (markers.intAt(y, x) === -1) {
          const o = (y * markers.cols + x) * 4
          out.data[o] = 255; out.data[o + 1] = 0; out.data[o + 2] = 0; out.data[o + 3] = 255
        }
      }
      return out
    },"""
new_ws = """    run: (s) => {
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
    },"""
if old_ws in src:
    src = src.replace(old_ws, new_ws, 1)
    print("✅ watershed 重写完成")
else:
    print("⚠️ watershed 未匹配")

# template: rect 是普通对象不需要 delete，但 cv.Rect 构造要确认（其实是JS对象，不需要）—— tpl/res 已 delete，OK
# gradient-flow: g1 没 delete
old_gf = """      M.delete(); g2.delete(); flow.delete()
      return out
    },
  },
  {
    id: 'sobel-hog'"""
new_gf = """      M.delete(); g1.delete(); g2.delete(); flow.delete()
      return out
    },
  },
  {
    id: 'sobel-hog'"""
if old_gf in src:
    src = src.replace(old_gf, new_gf, 1); print("✅ gradient-flow 补 g1.delete")
else:
    print("⚠️ gradient-flow 未匹配")

# sobel-hog: g, gx, gy, mag, m8 没 delete
old_sh = """      cv.normalize(mag, mag, 0, 255, cv.NORM_MINMAX)
      const m8 = new cv.Mat(); mag.convertTo(m8, cv.CV_8U)
      const color = new cv.Mat()
      cv.applyColorMap(m8, color, cv.COLORMAP_JET)
      cv.cvtColor(color, color, cv.COLOR_RGB2RGBA)
      return color"""
new_sh = """      cv.normalize(mag, mag, 0, 255, cv.NORM_MINMAX)
      const m8 = new cv.Mat(); mag.convertTo(m8, cv.CV_8U)
      const color = new cv.Mat()
      cv.applyColorMap(m8, color, cv.COLORMAP_JET)
      cv.cvtColor(color, color, cv.COLOR_RGB2RGBA)
      g.delete(); gx.delete(); gy.delete(); mag.delete(); m8.delete(); return color"""
if old_sh in src:
    src = src.replace(old_sh, new_sh, 1); print("✅ sobel-hog 补 delete")
else:
    print("⚠️ sobel-hog 未匹配")

# clahe: g 没 delete
old_cl = """      const clahe = new cv.CLAHE(p.clip, new cv.Size(p.tile, p.tile))
      const d = new cv.Mat(); clahe.apply(g, d); clahe.delete()
      return gray2rgba(d)"""
new_cl = """      const clahe = new cv.CLAHE(p.clip, new cv.Size(p.tile, p.tile))
      const d = new cv.Mat(); clahe.apply(g, d); clahe.delete()
      g.delete(); return gray2rgba(d)"""
if old_cl in src:
    src = src.replace(old_cl, new_cl, 1); print("✅ clahe 补 g.delete")
else:
    print("⚠️ clahe 未匹配")

# gabor: g 没 delete
old_ga = """      k.delete(); resp.delete()
      return gray2rgba(d)
    },
  },
  {
    id: 'lbp'"""
new_ga = """      g.delete(); k.delete(); resp.delete(); d.delete()
      return gray2rgba(d)
    },
  },
  {
    id: 'lbp'"""
if old_ga in src:
    src = src.replace(old_ga, new_ga, 1); print("✅ gabor 补 delete")
else:
    print("⚠️ gabor 未匹配")

# lbp: g 没 delete
old_lbp = """        }
      }
      return gray2rgba(out)
    },
  },
  {
    id: 'haarwavelet'"""
new_lbp = """        }
      }
      g.delete(); return gray2rgba(out)
    },
  },
  {
    id: 'haarwavelet'"""
if old_lbp in src:
    src = src.replace(old_lbp, new_lbp, 1); print("✅ lbp 补 g.delete")
else:
    print("⚠️ lbp 未匹配")

# haarwavelet: g 没 delete
old_hw = """          out.ucharPtr(hh + y, hw + x)[0] = Math.max(0, Math.min(255, 128 + (a - b - c + d) / 4))
        }
      }
      return gray2rgba(out)
    },
  },
  // —— 特征检测（补充）——"""
new_hw = """          out.ucharPtr(hh + y, hw + x)[0] = Math.max(0, Math.min(255, 128 + (a - b - c + d) / 4))
        }
      }
      g.delete(); return gray2rgba(out)
    },
  },
  // —— 特征检测（补充）——"""
if old_hw in src:
    src = src.replace(old_hw, new_hw, 1); print("✅ haarwavelet 补 g.delete")
else:
    print("⚠️ haarwavelet 未匹配")

# fast/brisk/akaze/mser/blob: g 没 delete
for key, next_key in [
    ('fast', "'brisk'"),
    ('brisk', "'akaze'"),
    ('akaze', "'mser'"),
    ('mser', "'blob'"),
]:
    # 匹配模式：kp.delete(); det.delete()\n      return out
    old = "      kp.delete(); det.delete()\n      return out\n    },\n  },\n  {\n    id: " + next_key
    new = "      g.delete(); kp.delete(); det.delete(); return out\n    },\n  },\n  {\n    id: " + next_key
    if old in src:
        src = src.replace(old, new, 1); print(f"✅ {key} 补 g.delete")
    else:
        print(f"⚠️ {key} 未匹配")

# bfmatch: matches 没 delete; canvas 本身由外层 delete
old_bf = """      g1.delete(); g2.delete(); s2.delete(); d1.delete(); d2.delete(); m0.delete()
      k1.delete(); k2.delete(); bf.delete(); orb.delete()
      return canvas"""
new_bf = """      g1.delete(); g2.delete(); s2.delete(); d1.delete(); d2.delete(); m0.delete()
      k1.delete(); k2.delete(); bf.delete(); orb.delete(); matches.delete()
      return canvas"""
if old_bf in src:
    src = src.replace(old_bf, new_bf, 1); print("✅ bfmatch 补 matches.delete")
else:
    print("⚠️ bfmatch 未匹配")

# homography: matches, M 没 delete (M.delete() 在前面但 M 重定义了) —— 仔细看：有 M.delete() 但后面 M 被重定义？
# 看代码: M = getRotationMatrix2D... warpAffine(s, s2, M) 然后 M.delete() OK；g1/g2/d1/d2/m0/k1/k2/bf/orb/s2/aligned 已 delete；缺 matches, s1m/s2m/mask/Hm 已 delete
old_hg = """      g1.delete(); g2.delete(); s2.delete(); aligned.delete(); d1.delete(); d2.delete(); m0.delete()
      k1.delete(); k2.delete(); bf.delete(); orb.delete()
      return canvas"""
new_hg = """      g1.delete(); g2.delete(); s2.delete(); aligned.delete(); d1.delete(); d2.delete(); m0.delete()
      k1.delete(); k2.delete(); bf.delete(); orb.delete(); matches.delete(); M.delete()
      return canvas"""
if old_hg in src:
    src = src.replace(old_hg, new_hg, 1); print("✅ homography 补 delete")
else:
    print("⚠️ homography 未匹配")

# lkflow: 缺 M.delete? 已 delete；缺 g1/g2/s2/p0/p1/st/err 已 delete，但 canvas 返回前 r1/r2 roi 已 delete——OK，无泄漏

# facedetect: g 没 delete
old_fd = """      faces.delete()
      return out
    },
  },
]

const groups"""
new_fd = """      g.delete(); faces.delete()
      return out
    },
  },
]

const groups"""
if old_fd in src:
    src = src.replace(old_fd, new_fd, 1); print("✅ facedetect 补 g.delete")
else:
    print("⚠️ facedetect 未匹配")

# filter2d/gaussian/median/bilateral: 返回 d 直接给外层，d 被外层 delete，OK；但 filter2d 里 kernel 已 delete OK；
# grayscale: d 是灰度图，gray2rgba(d) 会 delete d，OK
# equalize 已补 g.delete

# 修复 gabor 中 resp.convertTo 后 resp 还会被 normalize 复用（OK，原代码顺序正确），但 d 被 gray2rgba delete，注意我刚才加了 d.delete() 会双删
# 修正：gray2rgba(d) 会 d.delete()，所以不能再 d.delete()
src = src.replace(
    "g.delete(); k.delete(); resp.delete(); d.delete()\n      return gray2rgba(d)",
    "g.delete(); k.delete(); resp.delete(); return gray2rgba(d)"
)
print("✅ 修正 gabor 双删问题")

with open(p, 'w', encoding='utf-8') as f:
    f.write(src)

print("\n🔧 修复完成，文件已写回")
