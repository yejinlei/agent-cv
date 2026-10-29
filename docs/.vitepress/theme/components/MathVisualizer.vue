<template>
  <div v-if="isMounted" class="math-vis">
    <div class="tab-bar">
      <button v-for="t in tabs" :key="t.id" :class="['tab-btn', {active: current === t.id}]" @click="current = t.id">{{ t.name }}</button>
    </div>

    <div class="vis-area">
      <!-- 1. 像素与邻域 -->
      <div v-if="current === 'pixel'" class="sub-vis">
        <h3>🧩 像素是什么？图像就是数字矩阵</h3>
        <p class="desc">图像是由一个个小格子（像素）组成的，每个格子存一个0~255的数字，0=黑，255=白，中间是灰。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="pixelCanvas" width="500" height="450" @mousemove="pixelHover" @mouseleave="pixelLeave"></canvas>
        <div class="ctrl-row">
          <label>鼠标悬停像素：坐标 ({{ hoverX }}, {{ hoverY }})，灰度值 = <b>{{ hoverVal }}</b></label>
        </div>
      </div>

      <!-- 2. 邻域与距离 -->
      <div v-if="current === 'neighbor'" class="sub-vis">
        <h3>📍 4邻域、8邻域、欧氏距离</h3>
        <p class="desc">红色是中心像素，橙色是4邻域（上下左右，距离=1），黄色是8邻域（加对角，距离=√2）。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="neighborCanvas" width="500" height="400"></canvas>
        <div class="ctrl-row">
          <label>距离类型：</label>
          <select v-model="distType">
            <option value="4">4邻域（曼哈顿距离，走直角）</option>
            <option value="8">8邻域（切比雪夫距离，可以斜走）</option>
            <option value="e" selected>欧氏距离（直线距离）</option>
          </select>
        </div>
      </div>

      <!-- 3. 卷积 -->
      <div v-if="current === 'conv'" class="sub-vis">
        <h3>🔲 卷积：滑动的3×3小窗口，每个位置做加权求和</h3>
        <p class="desc">卷积核就是一个小数字矩阵，在原图上滑，每个位置把对应位置相乘再加起来，就得到新图像的一个像素。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="convCanvas" width="640" height="380"></canvas>
        <div class="ctrl-row">
          <label>卷积核：</label>
          <select v-model="kernelType">
            <option value="blur">均值模糊（全1/9）</option>
            <option value="gauss">高斯模糊（中间大周围小）</option>
            <option value="sharpen" selected>锐化（突出中间）</option>
            <option value="edge">边缘检测（周围-1中间8）</option>
            <option value="emboss">浮雕</option>
          </select>
          <label style="margin-left:20px">滑动位置 x:</label>
          <input type="range" min="0" max="4" v-model.number="convX" />
          <label>y:</label>
          <input type="range" min="0" max="4" v-model.number="convY" />
        </div>
        <p class="calc">当前输出像素 = 加权求和 = <b>{{ convResult.toFixed(1) }}</b>（归一化后）</p>
      </div>

      <!-- 4. 梯度 Sobel -->
      <div v-if="current === 'grad'" class="sub-vis">
        <h3>📈 梯度：像素值变化有多快？边缘就是梯度大的地方</h3>
        <p class="desc">Sobel算子用两个3×3核，分别算x方向（左右变化）和y方向（上下变化）的梯度，合起来就是边缘强度。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="gradCanvas" width="600" height="300"></canvas>
        <div class="ctrl-row">
          <label>边缘方向：</label>
          <select v-model="edgeDir">
            <option value="v" selected>垂直边缘（左右明暗跳变）</option>
            <option value="h">水平边缘（上下明暗跳变）</option>
            <option value="d">斜边缘</option>
          </select>
        </div>
        <p class="calc">Gx = 左右差值；Gy = 上下差值；边缘强度 = √(Gx² + Gy²) = <b>{{ gradMag.toFixed(1) }}</b></p>
      </div>

      <!-- 5. 阈值分割 -->
      <div v-if="current === 'thresh'" class="sub-vis">
        <h3>✂️ 阈值分割：一刀把图切成"前景"和"背景"</h3>
        <p class="desc">灰度值大于阈值设为白（前景），小于设为黑（背景）。拖动阈值滑块看效果。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="threshCanvas" width="600" height="300" @mousedown="threshDown" @mousemove="threshMove" @mouseup="threshUp" @mouseleave="threshUp" style="cursor:ew-resize"></canvas>
        <div class="ctrl-row">
          <label>阈值 T = {{ threshT }}</label>
          <input type="range" min="0" max="255" v-model.number="threshT" />
          <span style="margin-left:20px;color:#666">👆 <b>在画布上左右拖动红色虚线</b>也能调阈值</span>
        </div>
      </div>

      <!-- 6. 霍夫直线 -->
      <div v-if="current === 'hough'" class="sub-vis">
        <h3>📐 霍夫变换：每个点"投票"，得票最多的线就是真直线</h3>
        <p class="desc">直角坐标系里的一个点(x,y)，在极坐标(ρ,θ)空间里对应一条正弦曲线；很多条曲线交于一点，说明这些点都在同一条直线上。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="houghCanvas" width="640" height="300"></canvas>
        <div class="ctrl-row">
          <label>点的数量：{{ houghN }}</label>
          <input type="range" min="3" max="20" v-model.number="houghN" />
        </div>
        <p class="calc">每个点投一票，交点处峰值 = <b>{{ houghPeak }}</b> 票 → 这就是检测出的直线</p>
      </div>

      <!-- 7. Harris 角点 -->
      <div v-if="current === 'harris'" class="sub-vis">
        <h3>🔺 Harris角点：往任何方向小窗口一动，灰度都大变的点就是角点</h3>
        <p class="desc">平坦区：怎么动灰度都不变；边缘：沿边动不变、跨边动变；角点：往哪动都变 → 这就是我们要找的特征点。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="harrisCanvas" width="600" height="220"></canvas>
        <div class="ctrl-row">
          <label>窗口类型：</label>
          <select v-model="harrisType">
            <option value="flat">平坦区（无特征）</option>
            <option value="edge">边缘（单方向特征）</option>
            <option value="corner" selected>角点（两个方向都有特征）</option>
          </select>
        </div>
      </div>

      <!-- 8. 傅里叶频域 -->
      <div v-if="current === 'fourier'" class="sub-vis">
        <h3>🌊 傅里叶变换：任何图像都能拆成不同频率的正弦波叠加</h3>
        <p class="desc">低频=整体明暗/大色块（模糊的"底色"），高频=细节/边缘/噪声（尖锐的跳变）。拖动滑块看不同频率组合出的效果。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="fourierCanvas" width="640" height="300"></canvas>
        <div class="ctrl-row">
          <label>保留低频：保留前{{ freqCut }}个频率分量</label>
          <input type="range" min="1" max="20" v-model.number="freqCut" />
        </div>
        <p class="calc">频率数越多，图像越清晰；只留低频 → 模糊（高斯模糊就是低通滤波），去掉低频只剩高频 → 只剩边缘</p>
      </div>

      <!-- 9. RANSAC -->
      <div v-if="current === 'ransac'" class="sub-vis">
        <h3>🎯 RANSAC：随机抽两个点画直线，看有多少点"站在这条线附近"，最多的就是真相</h3>
        <p class="desc">外点（噪声/错点）会干扰最小二乘法；RANSAC每次随机挑两个点试，谁支持的内点最多谁赢，对噪声超鲁棒。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="ransacCanvas" width="600" height="300"></canvas>
        <div class="ctrl-row">
          <button @click="ransacStep">点我试一次随机抽样</button>
          <span style="margin-left:20px">已迭代 {{ ransacIter }} 次，最佳内点数 = <b>{{ ransacBest }}</b></span>
          <button @click="ransacReset" style="margin-left:20px">重置</button>
        </div>
      </div>

      <!-- 10. 光流 Lucas-Kanade -->
      <div v-if="current === 'lk'" class="sub-vis">
        <h3>🏃 光流：同一个像素在相邻两帧之间移动了多少？</h3>
        <p class="desc">亮度恒定假设：同一个点在两帧里灰度一样；小运动假设：移动距离很小；邻域一致假设：小窗口里所有点动得一样。解Ax=b就能得到移动向量。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="lkCanvas" width="600" height="250"></canvas>
        <div class="ctrl-row">
          <label>物体移动速度：{{ lkSpeed }}</label>
          <input type="range" min="1" max="10" v-model.number="lkSpeed" />
        </div>
      </div>

      <!-- 11. 形态学 -->
      <div v-if="current === 'morph'" class="sub-vis">
        <h3>🧹 形态学：用小"刷子"（结构元）对二值图做腐蚀/膨胀</h3>
        <p class="desc">腐蚀：结构元贴住的区域必须全白才保留（毛刺被吃掉）；膨胀：只要有一点白就扩张（小洞被填上）；开运算=先腐后膨（去毛刺），闭运算=先膨后腐（填小洞）。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="morphCanvas" width="640" height="240"></canvas>
        <div class="ctrl-row">
          <label>操作：</label>
          <select v-model="morphOp">
            <option value="erode">腐蚀</option>
            <option value="dilate" selected>膨胀</option>
            <option value="open">开运算（去毛刺）</option>
            <option value="close">闭运算（填小洞）</option>
          </select>
          <label style="margin-left:20px">结构元大小：{{ morphK }}×{{ morphK }}</label>
          <input type="range" min="1" max="7" v-model.number="morphK" />
        </div>
      </div>

      <!-- 12. 高斯分布 -->
      <div v-if="current === 'gauss'" class="sub-vis">
        <h3>🔔 高斯函数：中间高、两边慢慢降的"钟形曲线"（最常用的权重）</h3>
        <p class="desc">离中心越近权重越大，越远越小。高斯模糊用它做加权平均，比均值模糊更自然，因为"近的像素更像"。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="gaussCanvas" width="600" height="280"></canvas>
        <div class="ctrl-row">
          <label>σ（平缓程度，越大越模糊）= {{ gaussSigma.toFixed(1) }}</label>
          <input type="range" min="0.5" max="5" step="0.1" v-model.number="gaussSigma" />
        </div>
      </div>

      <!-- 13. 颜色空间 -->
      <div v-if="current === 'color'" class="sub-vis">
        <h3>🎨 RGB / HSV 颜色空间：换一种"描述颜色"的方式</h3>
        <p class="desc">RGB是红/绿/蓝三盏灯的亮度；HSV是色相（什么颜色）、饱和度（鲜艳不鲜艳）、明度（亮不亮）——做颜色分割HSV更方便，因为颜色只由H决定。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="colorCanvas" width="600" height="260"></canvas>
        <div class="ctrl-row">
          <label>色相 H = {{ colorH }}°</label>
          <input type="range" min="0" max="360" v-model.number="colorH" />
          <label style="margin-left:20px">饱和度 S = {{ colorS }}%</label>
          <input type="range" min="0" max="100" v-model.number="colorS" />
        </div>
      </div>

      <!-- 14. 直方图 -->
      <div v-if="current === 'hist'" class="sub-vis">
        <h3>📊 灰度直方图：统计每个灰度值在图里有多少像素</h3>
        <p class="desc">直方图均衡化就是"把挤在一起的直方图拉开"，让暗图亮起来、亮图暗下去，对比度自动增强。</p>
        <div v-if="explains[current]" class="explain-card">
          <div class="ec-head">🧓 老奶奶也能懂</div>
          <div class="ec-row"><b>🍳 生活类比：</b><span v-html="explains[current].analogy"></span></div>
          <div class="ec-row"><b>💡 核心直觉：</b><span v-html="explains[current].intuition"></span></div>
          <div class="ec-row"><b>👣 分几步：</b><ol class="ec-steps"><li v-for="st in explains[current].steps" :key="st">{{ st }}</li></ol></div>
          <div class="ec-row"><b>📌 记住一句话：</b><span class="ec-kicker" v-html="explains[current].kicker"></span></div>
        </div>
        <canvas ref="histCanvas" width="640" height="280"></canvas>
        <div class="ctrl-row">
          <label>图像类型：</label>
          <select v-model="histType">
            <option value="dark">偏暗图像（直方图靠左）</option>
            <option value="bright" selected>偏亮图像（直方图靠右）</option>
            <option value="lowc">低对比度（挤在中间）</option>
            <option value="highc">高对比度（均匀分布）</option>
          </select>
          <label style="margin-left:20px"><input type="checkbox" v-model="histEq" /> 应用直方图均衡化</label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'

const props = defineProps({
  // 嵌入算法页时，指定默认选中的原理标签（如 'grad'）
  initialTab: { type: String, default: '' },
  // 紧凑模式：算法页内嵌时用，收窄留白并加一行说明
  compact:    { type: Boolean, default: false },
})

const tabs = [
  {id:'pixel', name:'像素矩阵'},
  {id:'neighbor', name:'邻域与距离'},
  {id:'conv', name:'卷积'},
  {id:'grad', name:'梯度/边缘'},
  {id:'thresh', name:'阈值分割'},
  {id:'hough', name:'霍夫变换'},
  {id:'harris', name:'Harris角点'},
  {id:'fourier', name:'傅里叶频域'},
  {id:'ransac', name:'RANSAC'},
  {id:'lk', name:'Lucas-Kanade光流'},
  {id:'morph', name:'形态学运算'},
  {id:'gauss', name:'高斯分布'},
  {id:'color', name:'颜色空间'},
  {id:'hist', name:'直方图'},
]
const current = ref(tabs.some(t => t.id === props.initialTab) ? props.initialTab : 'pixel')
const isMounted = ref(false)

// ========== 🧓 老奶奶式讲解字典（每个概念：类比→直觉→步骤→口诀） ==========
const explains = {
  pixel: {
    analogy: '你家客厅的瓷砖墙。远看是一幅画，走近看全是一块块小瓷砖，每块砖只有一种颜色。图像就是这样一面大墙，「像素」就是那一块砖，「灰度值」就是这块砖涂的颜料深浅——0=刷了黑漆，255=刷了白漆，中间是各种灰。',
    intuition: '图像不是"画"，是一张<b>超大的数字表格</b>（矩阵）。所有"高级"操作（模糊、找边、识别人脸）追根究底，都是<b>对着这堆数字做加减乘除</b>。',
    steps: [
      '用手机拍一张照片 = 把现实中无数连续的颜色，硬切成几百万个小格子',
      '每个格子只留一个数字（彩色是3个：R/G/B）',
      '后面所有"智能"算法，本质都是在玩这堆数字',
    ],
    kicker: '图像 = 数字矩阵。你看到的画面，在计算机眼里就是 Excel 表格。',
  },
  neighbor: {
    analogy: '一桌人吃饭，正中间是你。「4邻域」就是坐你<b>上下左右</b>的4个亲戚（爸、妈、哥、妹）；「8邻域」再加上<b>四个对角</b>坐的表兄弟；「欧氏距离」就是"拿尺子量你俩的直线距离"。',
    intuition: '图像里几乎所有操作（模糊、找边、去噪）都不是"一个像素自己玩"，而是<b>一个像素拉着周围邻居一起算</b>——因为真实世界是连续的，一个像素的邻居才和它"最像"。',
    steps: [
      '4邻域（曼哈顿距离）：走直线+走直角，上下左右4格，适合棋盘式的网格计算',
      '8邻域（切比雪夫距离）：斜着也算，共8格，找轮廓/连通域常用',
      '欧氏距离：√(Δx²+Δy²)，就是生活中说的"直线距离"，最符合直觉',
    ],
    kicker: '做CV = 天天跟"邻居"打交道。「周围3×3」这9个格子，是90%传统算法的地盘。',
  },
  conv: {
    analogy: '就像你眯着眼睛看 LED 显示屏——你不会只盯着一个灯泡看，而是<b>用一片视野里的灯泡一起"综合"出一个颜色</b>。卷积核就是你眯眼的方式：模糊=让周围都进来，锐化=把自己放大、邻居往反方向减。',
    intuition: '一个小方块（3×3的数字矩阵，叫「核/kernel」），<b>在原图上一格一格滑</b>，每滑到一个位置，就把「核里的数字」和「底下对应的像素」<b>对应相乘再相加</b>，得到新图的一个像素。<b>换不同的核 = 换不同的"眼镜"，看到不同的东西</b>。',
    steps: [
      '把卷积核扣在当前像素上',
      '对应位置相乘：核的每个数 × 底下像素的灰度值',
      '9个乘积加起来，除以权重和（防止亮度跑偏）',
      '得到的新数字就是输出图该位置的像素值；核向右滑一格重复',
    ],
    kicker: '卷积 = 滑动加权求和。换核 = 换滤镜，1 行代码就能变模糊/锐化/浮雕/找边。',
  },
  grad: {
    analogy: '你站在山坡上，左脚踩在平地上、右脚踩在坑里——你能感觉到<b>"两边差很多"</b>，这就是「梯度大」，脚下就是<b>边缘</b>。如果两只脚都在平地上，梯度就是0，那就是天空/墙壁这种<b>平坦区</b>。',
    intuition: '边缘 = 像素值在空间里的<b>突变</b>。Sobel 用两个小核：一个只比"左边 vs 右边"（看竖边），一个只比"上面 vs 下面"（看横边），再把两个结果按勾股定理合成，就能知道"边缘强度"和"边缘方向"。',
    steps: [
      '用 Gx 核（左右对比）算水平梯度：Gx = 右列-左列',
      '用 Gy 核（上下对比）算垂直梯度：Gy = 下列-上列',
      '合成：边缘强度 = √(Gx² + Gy²)，方向 θ = arctan(Gy/Gx)',
      '强度越大，这个点越像边缘',
    ],
    kicker: '边缘 = 左右/上下邻居的差值。Sobel 不是"画图"，是在做减法。',
  },
  thresh: {
    analogy: '公司发年终奖，领导画条线：≥80分的发奖金（变白，前景），<80分的不发（变黑，背景）。一刀切，简单粗暴，但非常好用。',
    intuition: '阈值分割是最简单的<b>二值化</b>——把一张灰度图变成只有黑白两色，用来分离"想要的东西"和"不想要的东西"。阈值怎么选是门艺术：固定阈值、自适应阈值、Otsu 自动阈值……都是为了选对这条线。',
    steps: [
      '选一个阈值 T（通常128，或者让Otsu算法自动算）',
      '遍历每个像素：灰度 ≥ T → 设为255（白）',
      '灰度 < T → 设为0（黑）',
      '输出一张只有黑白两色的二值图',
    ],
    kicker: '阈值 = 一刀切。大于T是白、小于T是黑。二值图是后续轮廓查找、OCR的起点。',
  },
  hough: {
    analogy: '班级选班长：每个同学（边缘点）都可以"提名"自己支持的直线；大家都投票，<b>得票最多的那条线</b>，就是图像里真正的直线。即使有一些捣蛋鬼（噪声点）乱投，也挡不住大多数人的选择。',
    intuition: '直角坐标系里的"一个点"，在 (ρ, θ) 极坐标参数空间里对应<b>一条正弦曲线</b>；如果几个点在同一条直线上，它们的正弦曲线就会<b>交于同一点</b>——交点的 (ρ,θ) 就是那条直线的参数。这叫"投票机制"，能从一堆散点里找出线、圆、椭圆。',
    steps: [
      '先用 Canny 找出所有边缘点（候选选民）',
      '建一个"票数表"（累加器），行是θ、列是ρ',
      '每个边缘点对所有可能的θ算对应的ρ，在票数表对应的格子投一票',
      '找票数表里的"峰"——峰值高的格子对应的 (ρ,θ) 就是一条直线',
    ],
    kicker: '霍夫变换 = 让每个点"投票"，票最多的那根线就是答案。找直线、找圆都靠它。',
  },
  harris: {
    analogy: '你桌上放一块小玻璃片。如果玻璃片下面是<b>平整的桌面</b>，你往任何方向推它，玻璃片里看到的花纹都<b>不变</b>——平坦区。如果玻璃片<b>跨过桌沿</b>，你沿着桌边推，花纹不变；但<b>垂直桌沿推</b>，花纹突然变了——这是边。如果玻璃片刚好盖在<b>桌角</b>上，你<b>往任何方向推</b>，花纹都会大变——这就是角点！',
    intuition: '在图像上放一个小窗口，往任意方向挪一小段(u,v)，看窗里的亮度变化 E(u,v)。用泰勒展开把 E 近似成二次型 (u,v)·M·(u,v)ᵀ，M 就是<b>结构张量</b>（由梯度 Ix, Iy 在窗口里求和得到）。看 M 的两个<b>特征值 λ₁,λ₂</b>：两个都小=平坦；一个大一个小=边；两个都大=角点。',
    steps: [
      '对图像做高斯平滑，再用 Sobel 算出每个像素的水平梯度 Ix 和垂直梯度 Iy',
      '对每个像素，在它周围的小窗口里累加三个量：ΣIx²、ΣIy²、ΣIxIy，组成 2×2 矩阵 M',
      '算响应值 R = det(M) − k·tr(M)² = λ₁λ₂ − k(λ₁+λ₂)²，k 通常取 0.04~0.06',
      'R 大且是局部极大值 → 角点',
    ],
    kicker: 'M 的两个特征值都大 → 角点。R 函数让我们不用解特征值就能判断，快到实时。',
  },
  fourier: {
    analogy: '一盘菜端上来，傅里叶变换就是把它<b>拆回菜谱</b>——多少盐、多少糖、多少辣椒、火候多大。逆变换就是<b>按菜谱重新炒一盘</b>，炒出来的菜跟原来一模一样。低频=菜的主料（大色块、整体明暗），高频=调料和纹理（边缘、细节、噪声）。',
    intuition: '任何图像（哪怕是一张猫脸）都能被拆成<b>无数张不同频率/方向/相位的"波纹图"叠加</b>。频率低=变化慢=大色块=模糊=底色；频率高=变化快=细边/噪点=锐利。只保留低频 = 模糊（高斯模糊本质就是低通滤波）；只保留高频 = 只剩边缘/噪点。',
    steps: [
      '把整张图做二维离散傅里叶变换 DFT，得到频谱图（复杂的数字阵列）',
      '频谱中心是低频，外围是高频；亮度代表该频率的强度',
      '想模糊就把高频部分"乘0"抹掉（低通滤波）；想找边就把低频"乘0"（高通滤波）',
      '逆傅里叶变换回到图像域，得到处理后的图',
    ],
    kicker: '傅里叶 = 拆成波纹再拼回来。低频管"整体样子"，高频管"细节锐利"。',
  },
  ransac: {
    analogy: '广场上站着 100 个人，其中 80 个整齐排一条直线（内点），20 个乱跑（外点/噪声）。你想找出那条直线。最小二乘法会被乱跑的人带歪；RANSAC 的做法：闭着眼<b>随机抓两个人，画一条穿过他俩的线</b>，然后数"多少人站在这条线附近"（支持者）。抓很多次，<b>支持者最多的那条线</b>就是答案。',
    intuition: 'RANSAC = RANdom SAmple Consensus（随机抽样一致）。它的哲学是：<b>"真相"会被大多数内点支持</b>，外点是少数派。每次随机抽最小样本（直线抽2点、圆抽3点、单应矩阵抽4点）拟合模型，数内点，重复 N 次，取内点最多的模型。对超过 50% 外点的数据依然能拟合，这是最小二乘做不到的。',
    steps: [
      '随机抽最少数量的点（直线=2点，基础矩阵=8点）',
      '用这些点拟合模型（一条线、一个矩阵……）',
      '算所有其它点到模型的距离，距离小于阈值的算"内点"',
      '如果内点数量刷新纪录，更新"当前最佳模型"',
      '重复 N 次（通常几百~几千次），最终最佳模型就是答案',
    ],
    kicker: 'RANSAC = 闭着眼抽样→拟合→数支持者，重复很多次，票多的赢。专治各种外点/噪声。',
  },
  lk: {
    analogy: '你在人群中找一个穿红衣服的朋友——他上一帧在画面左边，这一帧稍微动了一点。你<b>盯着他周围一个小窗口</b>（而不是整张图）找"最像的那块"，就找到他的新位置。窗口里所有人移动方向都差不多（邻域一致），所以能比较稳地定位。',
    intuition: '光流 = 像素在相邻两帧之间的<b>位移向量 (u,v)</b>。Lucas-Kanade 做了三个假设：① 亮度恒定（同一个点移动时灰度不变）；② 小运动（位移很小，可以用泰勒一阶近似）；③ 邻域一致（一个小窗口里所有点移动方向相同）。用这三条把问题化成解一个 2×2 线性方程 AᵀA · d = Aᵀb。',
    steps: [
      '在第1帧用 Harris/Shi-Tomasi 找出好跟踪的特征点（角点）',
      '对每个点，在它周围取一个小窗口（比如 15×15）',
      '在第2帧同一个位置附近做小范围搜索，用梯度 Ix/Iy 和时间差 It 组方程',
      '解 (u,v) = (AᵀA)⁻¹ Aᵀb，得到这个点的位移向量',
      '把点挪到新位置，下一帧重复跟踪',
    ],
    kicker: 'LK光流 = 假设"小窗口里所有点一起动"，解一个2×2方程，就能知道每个角点跑哪儿去了。',
  },
  morph: {
    analogy: '形态学操作就像<b>用橡皮/笔修改二值图</b>：腐蚀 = 把白色区域"啃掉一圈"（毛刺没了，字变细）；膨胀 = 把白色区域"胖一圈"（小洞补上，字变粗）；开运算=先啃再胖（去外面的白点）；闭运算=先胖再啃（填里面的黑洞）。',
    intuition: '结构元（通常是3×3十字或方块）像个图章，在二值图上滑。腐蚀：图章下面必须<b>全白</b>才保留中心像素（否则变黑，白区缩小）；膨胀：图章下面<b>只要有一点白</b>就把中心设白（白区扩大）。两者组合就能去噪、填洞、连断线、分离粘连物体。',
    steps: [
      '选一个结构元（刷子形状+大小）',
      '腐蚀：遍历每个像素，如果结构元内有任何黑像素，中心就变黑 → 毛刺消失',
      '膨胀：遍历每个像素，如果结构元内有任何白像素，中心就变白 → 小缝补上',
      '开运算（先腐后膨）：去小突起/孤立亮点，主体不变',
      '闭运算（先膨后腐）：填小黑洞/窄裂缝，主体不变',
    ],
    kicker: '腐蚀瘦一圈、膨胀胖一圈；开运算去刺、闭运算填洞。二值图必备橡皮擦。',
  },
  gauss: {
    analogy: '全班考试平均分，但<b>跟你坐得越近的同学分数对你的影响越大</b>——同桌占20%，前后桌占12%，隔两排的只占1%，隔三排以上几乎不算。这就是高斯权重——"近的更像你"。',
    intuition: '一维高斯函数 G(x) = (1/√(2π)σ)·exp(−x²/(2σ²)) 画出来是个钟形：中心最高、往两边对称衰减。二维的就是个"小山包"。σ 越大，山包越平缓（越模糊，把更远的邻居也算进来）；σ 越小，山包越尖（几乎只看自己，没模糊效果）。高斯模糊是**唯一**能让图像"自然平滑"的核（不产生伪影、可分离加速、符合中心极限定理）。',
    steps: [
      '选 σ（平滑强度）和卷积核大小 ksize（通常是 6σ+1）',
      '用高斯公式算出每个格子的权重，离中心越远权重越小',
      '所有权重加起来必须=1（除以权重和，叫"归一化"），保证不会让图变亮或变暗',
      '把这个核套在图像上做卷积——高斯模糊完成',
    ],
    kicker: '高斯 = 近大远小的加权平均。σ 越大越糊，σ=0 就是原图。Canny/SIFT/降噪都离不开它。',
  },
  color: {
    analogy: 'RGB 是<b>三盏不同颜色的手电筒（红/绿/蓝）同时照在一面白墙上</b>——三盏都开到最亮就是白，都不开就是黑，调亮度组合出各种颜色。HSV 则像<b>画家调色盘</b>：色相（Hue）=你挤了哪种颜料（红？黄？蓝？），饱和度（Saturation）=颜料加了多少白色稀释（越饱和越鲜艳，加白多就变粉/变灰），明度（Value）=加了多少黑色（亮还是暗）。',
    intuition: '在RGB里"同一个颜色"因为光照不同会出现在 R/G/B 三个通道各种位置，很难用一个范围框住。在HSV里，<b>"颜色是什么"只由H一个通道决定</b>（红=0°，绿=120°，蓝=240°），不管亮暗、鲜艳不鲜艳。所以做颜色分割（"找出图里所有红色的东西"）几乎必转HSV。',
    steps: [
      'RGB：每个像素 (R,G,B) 三个数0-255，分别表示三盏灯的亮度',
      'HSV：H=色相（0-360°，在色环上的位置）；S=饱和度（0-100%，0=灰白，100%=最鲜艳）；V=明度（0-100%，0=黑，100%=最亮）',
      '做颜色检测：把图像转HSV，对 H 做范围筛选（如 H<10 或 H>170 = 红）',
      'S 和 V 也可以加范围（S不能太低否则白色灰色混进来，V不能太低否则黑色混进来）',
    ],
    kicker: 'RGB 适合显示（屏幕），HSV 适合"按颜色找东西"。做颜色分割 → 直接转 HSV。',
  },
  hist: {
    analogy: '假设你在排队打饭，统计每个身高（0~255cm）各站了<b>多少人</b>——这就是直方图。如果所有人都挤在150~170cm这个小区间（低对比度），老师说"你们散开站！"把大家均匀铺满0~255，最矮的站0、最高的站255——这就是<b>直方图均衡化</b>。散开后，人与人之间的身高差变大，照片就"清楚"了。',
    intuition: '灰度直方图 = 横轴是灰度值0-255，纵轴是该灰度值在图像里<b>出现的次数</b>。如果直方图"挤成一团"，说明图像对比度差（要么整体偏暗、要么整体偏亮、要么灰蒙蒙）。均衡化就是做一个灰度映射，让映射后的直方图<b>尽量均匀分布在0-255</b>，达到自动增强对比度的效果。',
    steps: [
      '统计256个灰度值各有多少像素，得到直方图 h[0..255]',
      '计算累计分布 cdf[i] = h[0]+h[1]+...+h[i]（即灰度≤i的像素总数）',
      '建立映射：新灰度[i] = (cdf[i] − cdf_min) / (总像素 − cdf_min) × 255',
      '查表替换每个像素的灰度值 → 输出对比度增强的图',
    ],
    kicker: '直方图 = "各亮度有多少像素"。均衡化 = "把挤在一起的像素拉开"，暗图/灰图一秒变清晰。',
  },
}

// ---- refs ----
const pixelCanvas = ref(null), neighborCanvas = ref(null), convCanvas = ref(null), gradCanvas = ref(null)
const threshCanvas = ref(null), houghCanvas = ref(null), harrisCanvas = ref(null), fourierCanvas = ref(null)
const ransacCanvas = ref(null), lkCanvas = ref(null), morphCanvas = ref(null), gaussCanvas = ref(null)
const colorCanvas = ref(null), histCanvas = ref(null)

// ---- state ----
const hoverX = ref(0), hoverY = ref(0), hoverVal = ref(128)
const distType = ref('e')
const kernelType = ref('sharpen'), convX = ref(2), convY = ref(2), convResult = ref(0)
const edgeDir = ref('v'), gradMag = ref(0)
const threshT = ref(128)
const houghN = ref(8), houghPeak = ref(0)
const harrisType = ref('corner')
const freqCut = ref(5)
const ransacIter = ref(0), ransacBest = ref(0), ransacPoints = ref([])
const ransacAuto = ref(false), ransacAutoTimer = ref(null)
const ransacOutRatioPct = ref(40), ransacThresh = ref(8)
const ransacCurrLine = ref(null)  // 本次抽样线（仅用于演示）
const lkSpeed = ref(5), lkPlay = ref(false), lkN = ref(15), lkFrame = ref(0), lkTimer = ref(null)
const neighborCx = ref(3), neighborCy = ref(3)
const threshDragging = ref(false)
const morphOp = ref('dilate'), morphK = ref(3)
const gaussSigma = ref(1.5)
const colorH = ref(0), colorS = ref(100)
const histType = ref('bright'), histEq = ref(false)

// ========== 1. 像素矩阵 ==========
function drawPixel() {
  const c = pixelCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  const size = 60, off = 50
  // 7x7 模拟灰度矩阵（中间有个亮块）
  const g = []
  for(let y=0;y<7;y++){
    const row=[]
    for(let x=0;x<7;x++){
      let v = 60 + Math.random()*30
      if(x>=2&&x<=4&&y>=2&&y<=4) v = 180 + Math.random()*40
      if(x===3&&y===3) v=255
      row.push(v|0)
    }
    g.push(row)
  }
  ctx.clearRect(0,0,c.width,c.height)
  for(let y=0;y<7;y++)for(let x=0;x<7;x++){
    const v = g[y][x]
    ctx.fillStyle = `rgb(${v},${v},${v})`
    ctx.fillRect(off+x*size, off+y*size, size-2, size-2)
    ctx.fillStyle = v>150?'#000':'#fff'
    ctx.font='14px monospace'
    ctx.textAlign='center'; ctx.textBaseline='middle'
    ctx.fillText(v, off+x*size+size/2, off+y*size+size/2)
  }
  ctx.fillStyle='#333';ctx.font='16px sans-serif'
  ctx.textAlign='left'
  ctx.fillText('← 每个格子就是一个像素，里面的数字是灰度值', off+7*size+20, off+size*3)
  ctx.fillText('0 = 纯黑，255 = 纯白', off+7*size+20, off+size*3+30)
  c._g = g
}
function pixelHover(e){
  const c = pixelCanvas.value
  const rect = c.getBoundingClientRect()
  const x = e.clientX - rect.left, y = e.clientY - rect.top
  const size=60, off=50
  const gx = ((x-off)/size)|0, gy=((y-off)/size)|0
  if(c._g && gx>=0&&gx<7&&gy>=0&&gy<7){
    hoverX.value=gx; hoverY.value=gy; hoverVal.value=c._g[gy][gx]
  }
}
function pixelLeave(){ hoverVal.value=128 }

// ========== 2. 邻域 ==========
function neighborClick(e){
  const c = neighborCanvas.value; if(!c) return
  const rect = c.getBoundingClientRect()
  const x = (e.clientX-rect.left)*(c.width/rect.width)
  const y = (e.clientY-rect.top)*(c.height/rect.height)
  const size=50, off=100
  const gx=((x-off)/size)|0, gy=((y-off)/size)|0
  if(gx>=0&&gx<7&&gy>=0&&gy<7){ neighborCx.value=gx; neighborCy.value=gy }
}
function drawNeighbor(){
  const c = neighborCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  const size=50, off=100
  ctx.clearRect(0,0,c.width,c.height)
  const cx=neighborCx.value, cy=neighborCy.value
  for(let y=0;y<7;y++)for(let x=0;x<7;x++){
    let color='#f5f5f5'
    if(x===cx&&y===cy) color='#ff6b6b'
    else if(distType.value==='4' && Math.abs(x-cx)+Math.abs(y-cy)===1) color='#ffa94d'
    else if(distType.value==='8' && Math.max(Math.abs(x-cx),Math.abs(y-cy))===1) color='#ffd43b'
    else if(distType.value==='e'){
      const d = Math.hypot(x-cx,y-cy)
      if(d<1.01) color='#ffa94d'
      else if(d<=1.5) color='#ffd43b'
    }
    ctx.fillStyle = color
    ctx.fillRect(off+x*size, off+y*size, size-2, size-2)
    ctx.strokeStyle='#ccc';ctx.strokeRect(off+x*size, off+y*size, size-2, size-2)
    // 显示距离数值
    ctx.fillStyle='#666';ctx.font='11px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle'
    const d = Math.hypot(x-cx,y-cy)
    if(color!=='#f5f5f5' && !(x===cx&&y===cy)){
      ctx.fillStyle='#333'
      ctx.fillText(d.toFixed(2), off+x*size+(size-2)/2, off+y*size+(size-2)/2)
    }
  }
  // 标注
  ctx.fillStyle='#333';ctx.font='15px sans-serif';ctx.textAlign='left'
  const labels = [
    `红色：中心像素 (${cx},${cy})`,
    distType.value==='4'?'橙色：4邻域（上下左右，距离=1，共4个）':
    distType.value==='8'?'橙色+黄色：8邻域（加对角，共8个）':
    '橙色：距离=1；黄色：距离≈√2≈1.414',
    '欧氏距离 = √((x1-x2)²+(y1-y2)²)  就是普通直线距离',
    '格子里的数字 = 该格到中心的欧氏距离',
  ]
  labels.forEach((t,i)=>ctx.fillText(t, off+8*size, off+i*26+30))
}

// ========== 3. 卷积 ==========
const kernels = {
  blur:   [[1,1,1],[1,1,1],[1,1,1]],
  gauss:  [[1,2,1],[2,4,2],[1,2,1]],
  sharpen:[[0,-1,0],[-1,5,-1],[0,-1,0]],
  edge:   [[-1,-1,-1],[-1,8,-1],[-1,-1,-1]],
  emboss: [[-2,-1,0],[-1,1,1],[0,1,2]],
}
function drawConv(){
  const c = convCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  // 7x7 原图
  const img = []
  for(let y=0;y<7;y++){
    const r=[]
    for(let x=0;x<7;x++){
      // 一个渐变+中间有一条边
      let v = 80 + x*25
      if(y>=3) v=180
      r.push(v|0)
    }
    img.push(r)
  }
  const ks=50, ox=30, oy=30
  // 画原图
  for(let y=0;y<7;y++)for(let x=0;x<7;x++){
    const v=img[y][x]
    ctx.fillStyle=`rgb(${v},${v},${v})`
    ctx.fillRect(ox+x*ks, oy+y*ks, ks-2, ks-2)
    ctx.fillStyle=v>150?'#000':'#fff'
    ctx.font='12px monospace';ctx.textAlign='center';ctx.textBaseline='middle'
    ctx.fillText(v, ox+x*ks+ks/2, oy+y*ks+ks/2)
  }
  // 高亮 3x3 窗口
  const kx=convX.value, ky=convY.value
  ctx.strokeStyle='#ff4757';ctx.lineWidth=3
  ctx.strokeRect(ox+kx*ks-1, oy+ky*ks-1, ks*3, ks*3)

  // 画卷积核
  const k = kernels[kernelType.value]
  const kox=ox+7*ks+50, koy=oy+ks
  ctx.fillStyle='#333';ctx.font='15px sans-serif';ctx.textAlign='center'
  ctx.fillText('卷积核', kox+ks*1.5, koy-20)
  for(let y=0;y<3;y++)for(let x=0;x<3;x++){
    ctx.fillStyle='#e3f2fd'
    ctx.fillRect(kox+x*ks, koy+y*ks, ks-2, ks-2)
    ctx.strokeStyle='#1976d2';ctx.strokeRect(kox+x*ks, koy+y*ks, ks-2, ks-2)
    ctx.fillStyle='#000';ctx.font='bold 14px monospace'
    ctx.fillText(k[y][x], kox+x*ks+ks/2, koy+y*ks+ks/2)
  }

  // 输出图 5x5
  const oox=kox+4*ks+50, ooy=oy+ks
  ctx.fillStyle='#333';ctx.font='15px sans-serif'
  ctx.fillText('输出图', oox+ks*2.5-ks, ooy-20)
  let sum=0, ksum=0
  for(let y=0;y<3;y++)for(let x=0;x<3;x++){
    sum += img[ky+y][kx+x]*k[y][x]
    ksum += k[y][x]
  }
  if(ksum===0) ksum=1
  let out = sum/ksum
  if(out<0) out=0; if(out>255) out=255
  convResult.value=out
  for(let y=0;y<5;y++)for(let x=0;x<5;x++){
    // 预先算所有输出
    let s=0
    for(let j=0;j<3;j++)for(let i=0;i<3;i++) s+=img[y+j][x+i]*k[j][i]
    let v=s/ksum; v=Math.max(0,Math.min(255,v))|0
    ctx.fillStyle=`rgb(${v},${v},${v})`
    ctx.fillRect(oox+x*ks, ooy+y*ks, ks-2, ks-2)
  }
  // 高亮当前位置
  ctx.strokeStyle='#ff4757';ctx.lineWidth=3
  ctx.strokeRect(oox+kx*ks-1, ooy+ky*ks-1, ks, ks)
  // 计算式
  ctx.fillStyle='#333';ctx.font='14px sans-serif';ctx.textAlign='left'
  let formula='当前窗口加权求和 = '
  const parts=[]
  for(let y=0;y<3;y++)for(let x=0;x<3;x++){
    parts.push(`${img[ky+y][kx+x]}×${k[y][x]}`)
  }
  ctx.fillText(formula, ox, oy+7*ks+30)
  ctx.font='12px monospace'
  for(let i=0;i<parts.length;i+=3) ctx.fillText(parts.slice(i,i+3).join(' + '), ox, oy+7*ks+55+(i/3)*20)
}
function convClick(e){
  const c = convCanvas.value; if(!c) return
  const rect = c.getBoundingClientRect()
  const x = (e.clientX-rect.left)*(c.width/rect.width)
  const y = (e.clientY-rect.top)*(c.height/rect.height)
  const ks=50, ox=30, oy=30
  const gx=((x-ox)/ks)|0, gy=((y-oy)/ks)|0
  // 只有 0..4 是合法卷积中心位置（因为 7x7 里 3x3 窗口起点范围 0~4）
  if(gx>=0&&gx<=4&&gy>=0&&gy<=4){ convX.value=gx; convY.value=gy }
}

// ========== 4. 梯度 Sobel ==========
function drawGrad(){
  const c = gradCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const w=120,h=80, cell=20, ox=30, oy=30
  // 构建图像
  const g=[]
  for(let y=0;y<h;y++){
    const r=[]
    for(let x=0;x<w;x++){
      let v = 80
      if(edgeDir.value==='v' && x>=60) v=220
      if(edgeDir.value==='h' && y>=40) v=220
      if(edgeDir.value==='d' && x-y>=20) v=220
      r.push(v|0)
    }
    g.push(r)
  }
  // 画（缩放）
  const scale=2
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
    const v=g[y][x]
    ctx.fillStyle=`rgb(${v},${v},${v})`
    ctx.fillRect(ox+x*scale, oy+y*scale, scale, scale)
  }
  // 取中心 3x3 算 Sobel
  const cx=60,cy=40
  const sobelX=[[-1,0,1],[-2,0,2],[-1,0,1]]
  const sobelY=[[-1,-2,-1],[0,0,0],[1,2,1]]
  let Gx=0,Gy=0
  for(let j=-1;j<=1;j++)for(let i=-1;i<=1;i++){
    Gx += g[cy+j][cx+i]*sobelX[j+1][i+1]
    Gy += g[cy+j][cx+i]*sobelY[j+1][i+1]
  }
  gradMag.value = Math.hypot(Gx,Gy)
  ctx.strokeStyle='#ff4757';ctx.lineWidth=2
  ctx.strokeRect(ox+(cx-1)*scale, oy+(cy-1)*scale, 3*scale, 3*scale)
  // 数值区
  const tx=ox+w*scale+40, ty=oy
  ctx.fillStyle='#333';ctx.font='15px sans-serif';ctx.textAlign='left'
  ctx.fillText(`取边缘附近的 3×3 窗口：`, tx, ty+20)
  ctx.fillText(`Sobel X核（测水平边缘？不，测垂直边缘）：`, tx, ty+50)
  ctx.font='13px monospace'
  ;[[-1,0,1],[-2,0,2],[-1,0,1]].forEach((r,i)=>ctx.fillText(r.join('  '), tx+20, ty+75+i*20))
  ctx.fillStyle='#333';ctx.font='15px sans-serif'
  ctx.fillText(`Gx = ${Gx}（x方向梯度）`, tx, ty+150)
  ctx.fillText(`Gy = ${Gy}（y方向梯度）`, tx, ty+175)
  ctx.fillText(`边缘强度 = √(Gx²+Gy²) = ${gradMag.value.toFixed(1)}`, tx, ty+200)
  ctx.fillStyle='#d63031';ctx.font='bold 14px sans-serif'
  ctx.fillText(gradMag.value>100 ? '✔ 这里是边缘！' : '✘ 这里是平坦区', tx, ty+230)
}

// ========== 5. 阈值分割 ==========
function drawThresh(){
  const c = threshCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const w=200
  // 生成原图（双峰：前景+背景）
  const g=[]
  for(let y=0;y<w;y++){
    const r=[]
    for(let x=0;x<w;x++){
      let v = 60 + Math.random()*40
      if((x-100)**2+(y-100)**2 < 60*60) v = 180+Math.random()*40
      r.push(v|0)
    }
    g.push(r)
  }
  const scale=1.2, ox=30, oy=30
  // 原图
  for(let y=0;y<w;y++)for(let x=0;x<w;x++){
    const v=g[y][x]
    ctx.fillStyle=`rgb(${v},${v},${v})`
    ctx.fillRect(ox+x*scale, oy+y*scale, scale, scale)
  }
  ctx.fillStyle='#333';ctx.font='14px sans-serif';ctx.textAlign='center'
  ctx.fillText('原图（灰度）', ox+w*scale/2, oy+w*scale+20)
  // 阈值后
  const oox=ox+w*scale+60
  for(let y=0;y<w;y++)for(let x=0;x<w;x++){
    const v = g[y][x]>threshT.value?255:0
    ctx.fillStyle=`rgb(${v},${v},${v})`
    ctx.fillRect(oox+x*scale, oy+y*scale, scale, scale)
  }
  ctx.fillStyle='#333';ctx.fillText(`阈值 T=${threshT.value} 分割结果`, oox+w*scale/2, oy+w*scale+20)
  // 直方图
  const hist = new Array(256).fill(0)
  for(let y=0;y<w;y++)for(let x=0;x<w;x++) hist[g[y][x]]++
  const hx=oox, hy=oy+w*scale+40, hw=w*scale, hh=60
  ctx.strokeStyle='#ccc';ctx.strokeRect(hx,hy,hw,hh)
  const maxH=Math.max(...hist)
  ctx.fillStyle='#1976d2'
  for(let i=0;i<256;i++){
    ctx.fillRect(hx+i*hw/256, hy+hh-hist[i]/maxH*hh, hw/256+0.5, hist[i]/maxH*hh)
  }
  ctx.strokeStyle='#ff4757';ctx.lineWidth=2
  ctx.beginPath()
  ctx.moveTo(hx+threshT.value*hw/256, hy)
  ctx.lineTo(hx+threshT.value*hw/256, hy+hh)
  ctx.stroke()
}
function threshDown(e){ threshDragging.value=true; threshMove(e) }
function threshMove(e){
  if(!threshDragging.value) return
  const c = threshCanvas.value; if(!c) return
  const rect = c.getBoundingClientRect()
  const x = (e.clientX-rect.left)*(c.width/rect.width)
  // drawThresh 中：原图 w=200, scale=1.2；直方图起点 hx=oox=ox+w*scale+60 = 330；hw=w*scale=240
  const hx=330, hw=240
  let v = Math.round(((x-hx)/hw)*255)
  v = Math.max(0, Math.min(255, v))
  threshT.value = v
}
function threshUp(){ threshDragging.value=false }


// ========== 6. 霍夫 ==========
function drawHough(){
  const c = houghCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  // 左边：原图点
  const W=280,H=280,ox=20,oy=10
  ctx.strokeStyle='#ccc';ctx.strokeRect(ox,oy,W,H)
  ctx.fillStyle='#333';ctx.font='14px sans-serif';ctx.textAlign='center'
  ctx.fillText('直角坐标系 (x,y)', ox+W/2, oy+H+20)
  // 生成一条直线上的点 + 一些噪点
  const pts=[]
  const lineA=0.5, lineB=80 // y=0.5x+80
  for(let i=0;i<houghN.value;i++){
    const x=30+Math.random()*220
    const y=lineA*x+lineB + (Math.random()-0.5)*20
    if(y>10&&y<270) pts.push({x,y})
  }
  // 加点噪声
  for(let i=0;i<3;i++){
    pts.push({x:Math.random()*W, y:Math.random()*H})
  }
  pts.forEach(p=>{
    ctx.fillStyle='#2196f3'
    ctx.beginPath();ctx.arc(ox+p.x,oy+p.y,4,0,Math.PI*2);ctx.fill()
  })
  // 画真值线
  ctx.strokeStyle='#ff9800';ctx.lineWidth=1;ctx.setLineDash([5,5])
  ctx.beginPath();ctx.moveTo(ox,oy+lineB);ctx.lineTo(ox+W,oy+lineA*W+lineB);ctx.stroke()
  ctx.setLineDash([])

  // 右边：霍夫空间
  const hox=ox+W+40, hoy=oy, hW=280, hH=280
  ctx.strokeStyle='#ccc';ctx.strokeRect(hox,hoy,hW,hH)
  ctx.fillStyle='#333';ctx.textAlign='center'
  ctx.fillText('霍夫空间 (ρ,θ) — 每个点对应一条正弦曲线', hox+hW/2, hoy+hH+20)
  // 累加器
  const acc = Array.from({length:180},()=>new Array(200).fill(0))
  const maxRho=Math.hypot(W,H)
  pts.forEach(p=>{
    ctx.strokeStyle='rgba(33,150,243,0.3)';ctx.lineWidth=1
    ctx.beginPath()
    for(let t=0;t<180;t+=3){
      const th=t*Math.PI/180
      const rho=p.x*Math.cos(th)+p.y*Math.sin(th)
      const rr = ((rho+maxRho)/(2*maxRho))*200|0
      acc[t][rr]++
      const px = hox+t/180*hW, py=hoy+hH-rr/200*hH
      if(t===0) ctx.moveTo(px,py); else ctx.lineTo(px,py)
    }
    ctx.stroke()
  })
  // 找峰值
  let peak=0,bestT=0,bestR=0
  for(let t=0;t<180;t++)for(let r=0;r<200;r++) if(acc[t][r]>peak){peak=acc[t][r];bestT=t;bestR=r}
  houghPeak.value=peak
  // 画峰值点
  ctx.fillStyle='#ff4757'
  ctx.beginPath();ctx.arc(hox+bestT/180*hW,hoy+hH-bestR/200*hH,8,0,Math.PI*2);ctx.fill()
  ctx.fillStyle='#d63031';ctx.font='bold 13px sans-serif';ctx.textAlign='left'
  ctx.fillText(`峰值 ${peak} 票 → 检测直线`, hox-10, hoy-5)
  // 把检出的直线画回左图
  const rho = (bestR/200)*2*maxRho - maxRho
  const th=bestT*Math.PI/180
  ctx.strokeStyle='#ff4757';ctx.lineWidth=2
  const x0=ox+rho*Math.cos(th), y0=oy+rho*Math.sin(th)
  const x1=x0+1000*(-Math.sin(th)), y1=y0+1000*Math.cos(th)
  const x2=x0-1000*(-Math.sin(th)), y2=y0-1000*Math.cos(th)
  ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke()
}

// ========== 7. Harris ==========
function drawHarris(){
  const c = harrisCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const cases = {
    flat: {title:'平坦区：窗口怎么动，灰度都不变 → E(u,v)≈0 任意方向', color:'#90caf9', arrow:'↔↕  灰度不变'},
    edge: {title:'边缘：沿边动不变，跨边动变 → 一个方向E大、一个方向E小', color:'#ffd54f', arrow:'→ 沿边不变  ↑ 跨边变'},
    corner:{title:'角点：往哪儿动灰度都变 → 两个方向E都大 ✔', color:'#ef5350', arrow:'↗↘↙↖ 往哪动都变'},
  }
  const cc = cases[harrisType.value]
  // 画图例
  ctx.fillStyle='#333';ctx.font='15px sans-serif';ctx.textAlign='left'
  ctx.fillText(cc.title, 30, 30)
  // 画大色块代表区域
  const size=180, ox=50, oy=60
  if(harrisType.value==='flat'){
    ctx.fillStyle='#e0e0e0';ctx.fillRect(ox,oy,size,size)
  } else if(harrisType.value==='edge'){
    ctx.fillStyle='#e0e0e0';ctx.fillRect(ox,oy,size/2,size)
    ctx.fillStyle='#616161';ctx.fillRect(ox+size/2,oy,size/2,size)
  } else {
    ctx.fillStyle='#e0e0e0';ctx.fillRect(ox,oy,size,size)
    ctx.fillStyle='#616161';ctx.fillRect(ox+size/2,oy,size/2,size)
    ctx.fillStyle=cc.color;ctx.fillRect(ox,oy+size/2,size,size/2)
  }
  // 小窗口
  const wx=ox+size/2-25, wy=oy+size/2-25
  ctx.strokeStyle=cc.color;ctx.lineWidth=4
  ctx.strokeRect(wx,wy,50,50)
  // 箭头示意
  ctx.fillStyle=cc.color;ctx.font='bold 24px sans-serif';ctx.textAlign='center'
  ctx.fillText(cc.arrow, ox+size/2, oy+size+40)

  // E(u,v) 响应曲面
  const gx=ox+size+80, gy=oy+30, gw=200, gh=180
  ctx.fillStyle='#333';ctx.font='14px sans-serif';ctx.textAlign='center'
  ctx.fillText('E(u,v) 响应曲面', gx+gw/2, gy-10)
  ctx.strokeStyle='#ccc';ctx.strokeRect(gx,gy,gw,gh)
  if(harrisType.value==='flat'){
    ctx.fillStyle='#90caf9';ctx.beginPath();ctx.ellipse(gx+gw/2,gy+gh/2,40,30,0,0,Math.PI*2);ctx.fill()
  } else if(harrisType.value==='edge'){
    ctx.fillStyle='#ffd54f';ctx.fillRect(gx+30,gy+20,gw-60,gh-40)
  } else {
    ctx.fillStyle='#ef5350';ctx.beginPath();ctx.arc(gx+gw/2,gy+gh/2,50,0,Math.PI*2);ctx.fill()
  }
  // 公式
  ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='left'
  ctx.fillText('Harris 响应 R = det(M) - k·tr(M)²', gx, gy+gh+25)
  ctx.fillText('平坦区 R≈0，边缘 R<0，角点 R>>0', gx, gy+gh+45)
}

// ========== 8. 傅里叶 ==========
function drawFourier(){
  const c = fourierCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  // 构造一维信号：方波
  const N=200, signal=[]
  for(let i=0;i<N;i++) signal.push(i<N/2?0:1)
  // 用前K个正弦重建
  const K=freqCut.value
  const recon = new Array(N).fill(0.5)
  // 方波傅里叶级数：f(x) = 0.5 + 2/π Σ sin((2k-1)ωx)/(2k-1)
  for(let k=1;k<=K;k++){
    const n=2*k-1
    for(let i=0;i<N;i++){
      recon[i] += 2/Math.PI * Math.sin(n*2*Math.PI*i/N)/n
    }
  }
  // 画原信号
  const ox=30, oy=50, w=280, h=180
  ctx.strokeStyle='#ccc';ctx.strokeRect(ox,oy,w,h)
  ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='center'
  ctx.fillText('原始信号（方波 = 跳变边缘）', ox+w/2, oy-15)
  ctx.strokeStyle='#1976d2';ctx.lineWidth=2;ctx.beginPath()
  signal.forEach((v,i)=>{
    const px=ox+i*w/N, py=oy+h-v*h*0.7-h*0.15
    if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py)
  });ctx.stroke()
  // 画重建
  const rx=ox+w+40
  ctx.strokeStyle='#ccc';ctx.strokeRect(rx,oy,w,h)
  ctx.fillStyle='#333';ctx.fillText(`前 ${K} 个频率重建 = 留前${K}大频率（低通）`, rx+w/2, oy-15)
  ctx.strokeStyle='#e91e63';ctx.lineWidth=2;ctx.beginPath()
  recon.forEach((v,i)=>{
    const px=rx+i*w/N, py=oy+h-v*h*0.7-h*0.15
    if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py)
  });ctx.stroke()
  // 频谱
  ctx.fillStyle='#333';ctx.textAlign='left';ctx.font='13px sans-serif'
  ctx.fillText('🟦 低频 = 整体亮度/大色块（图像"底色"）', ox, oy+h+30)
  ctx.fillText('🟥 高频 = 边缘/细节/噪声（尖锐跳变）', ox, oy+h+50)
  ctx.fillText('👉 高斯模糊 = 只留低频（去掉高频细节）', ox, oy+h+70)
  ctx.fillText('👉 边缘检测 = 只留高频（去掉低频底色）', ox, oy+h+90)
}

// ========== 9. RANSAC ==========
const ransacW=560, ransacH=300, ransacOx=20, ransacOy=20
function genRansacPoints(){
  const pts=[]
  const ratio = ransacOutRatioPct.value/100
  const N=50
  const nOut = Math.round(N*ratio/(1-ratio))  // 按比例算出外点数
  const nIn = N
  // 真值线：y = 0.45x + 60（斜线，比之前的0.5更明显）
  for(let i=0;i<nIn;i++){
    const x=Math.random()*(ransacW-40)+20
    const y=0.45*x+60+(Math.random()-0.5)*20
    pts.push({x,y,inlier:true})
  }
  for(let i=0;i<nOut;i++){
    pts.push({x:Math.random()*ransacW+ransacOx-ransacOx, y:Math.random()*ransacH+ransacOy-ransacOy, inlier:false})
  }
  return pts
}
function ransacFitTwoPoints(){
  const pts=ransacPoints.value
  if(pts.length<2) return null
  let i1=0,i2=0,tries=0
  while(i1===i2 && tries<20){i1=(Math.random()*pts.length)|0;i2=(Math.random()*pts.length)|0;tries++}
  if(i1===i2) return null
  const p1=pts[i1],p2=pts[i2]
  if(Math.hypot(p2.x-p1.x,p2.y-p1.y)<20) return null  // 两点太近，跳过
  const a=p2.y-p1.y, b=p1.x-p2.x, c=p2.x*p1.y-p1.x*p2.y
  const n=Math.hypot(a,b)
  return {a,b,c,n,p1,p2}
}
function ransacCountInliers(line){
  if(!line) return 0
  const {a,b,c,n}=line
  let cnt=0; const th=ransacThresh.value
  ransacPoints.value.forEach(p=>{
    if(Math.abs(a*p.x+b*p.y+c)/n < th) cnt++
  })
  return cnt
}
function ransacStep(){
  const c = ransacCanvas.value; if(!c) return
  const line = ransacFitTwoPoints()
  if(!line) return
  const inliers = ransacCountInliers(line)
  ransacCurrLine.value = line
  if(inliers>ransacBest.value){
    ransacBest.value=inliers
    c._best=line
  }
  ransacIter.value++
}
function ransacReset(){
  ransacPoints.value=genRansacPoints()
  ransacIter.value=0
  ransacBest.value=0
  ransacCurrLine.value=null
  if(ransacCanvas.value) ransacCanvas.value._best=null
}
function ransacClick(e){
  const c = ransacCanvas.value; if(!c) return
  const rect = c.getBoundingClientRect()
  const x = (e.clientX-rect.left)*(c.width/rect.width) - ransacOx
  const y = (e.clientY-rect.top)*(c.height/rect.height) - ransacOy
  if(x<0||x>ransacW||y<0||y>ransacH) return
  // 靠近已有外点：删除；否则加一个外点
  let hit=-1
  ransacPoints.value.forEach((p,i)=>{
    if(!p.inlier && Math.hypot(p.x-x,p.y-y)<8) hit=i
  })
  if(hit>=0) ransacPoints.value.splice(hit,1)
  else ransacPoints.value.push({x,y,inlier:false})
  // 重新评估最佳（点数变了）
  ransacIter.value=0; ransacBest.value=0; ransacCurrLine.value=null
  c._best=null
  // 快速跑 50 步，立刻给出新最佳
  for(let k=0;k<80;k++){
    const line=ransacFitTwoPoints()
    if(!line) continue
    const n=ransacCountInliers(line)
    if(n>ransacBest.value){ransacBest.value=n; c._best=line}
    ransacIter.value++
  }
}
function drawRansac(){
  const c = ransacCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const {ox:ox0,oy:oy0,w,h} = {ox:ransacOx,oy:ransacOy,w:ransacW,h:ransacH}
  // 画布区域
  ctx.fillStyle='#fafbfc';ctx.fillRect(ox0,oy0,w,h)
  ctx.strokeStyle='#ccc';ctx.strokeRect(ox0,oy0,w,h)
  ctx.fillStyle='#333';ctx.font='14px sans-serif';ctx.textAlign='left'
  ctx.fillText('🔵 内点（在真线上） + 🔴 外点（噪声/错配点）', ox0+10, oy0-5)
  // 真值线（淡灰虚线）
  ctx.save()
  ctx.strokeStyle='rgba(150,150,150,0.5)';ctx.setLineDash([5,5]);ctx.lineWidth=1
  ctx.beginPath()
  const y0=0.45*0+60, y1=0.45*w+60
  ctx.moveTo(ox0,oy0+y0);ctx.lineTo(ox0+w,oy0+y1);ctx.stroke()
  ctx.restore()
  // 本次抽样线（橙色虚线，只有单步时显示一下）
  if(ransacCurrLine.value){
    const {a,b,c:n}=ransacCurrLine.value
    ctx.save()
    ctx.strokeStyle='rgba(255,152,0,0.8)';ctx.setLineDash([6,4]);ctx.lineWidth=2
    const ly0=(-n-a*0)/b, ly1=(-n-a*w)/b
    if(isFinite(ly0)&&isFinite(ly1)){
      ctx.beginPath();ctx.moveTo(ox0,oy0+ly0);ctx.lineTo(ox0+w,oy0+ly1);ctx.stroke()
    }
    ctx.restore()
  }
  // 点
  ransacPoints.value.forEach(p=>{
    ctx.fillStyle=p.inlier?'#2196f3':'#ff5252'
    ctx.beginPath();ctx.arc(ox0+p.x,oy0+p.y,p.inlier?3.5:4,0,Math.PI*2);ctx.fill()
  })
  // 最佳线（绿色粗线）
  if(c._best){
    const {a,b,c:n}=c._best
    ctx.strokeStyle='#4caf50';ctx.lineWidth=3
    const ly0=(-n-a*0)/b, ly1=(-n-a*w)/b
    if(isFinite(ly0)&&isFinite(ly1)){
      ctx.beginPath();ctx.moveTo(ox0,oy0+ly0);ctx.lineTo(ox0+w,oy0+ly1);ctx.stroke()
    }
    ctx.fillStyle='#4caf50';ctx.font='bold 14px sans-serif'
    ctx.fillText(`✅ 最佳拟合线（${ransacBest.value}个点支持，内点率 ${(ransacBest.value/ransacPoints.value.length*100)|0}%）`, ox0+10, oy0+h+22)
  }else{
    ctx.fillStyle='#999';ctx.font='13px sans-serif'
    ctx.fillText('还没找到最佳线，点"单步"或"自动跑"开始吧。', ox0+10, oy0+h+22)
  }
  ctx.fillStyle='#666';ctx.font='12px sans-serif'
  ctx.fillText('灰色虚线=真实直线；橙色虚线=本次随机抽样；绿色粗线=目前找到的最佳线。外点比例越高越难，试拉到 60% 看看 RANSAC 还能不能找对。', ox0+10, oy0+h+46)
}

// ========== 10. LK光流 ==========
function drawLK(){
  const c = lkCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const W=420, H=220, ox=20, oy=25
  // 画一帧场景
  ctx.strokeStyle='#ccc';ctx.strokeRect(ox,oy,W,H)
  ctx.fillStyle='#f5f5f5';ctx.fillRect(ox,oy,W,H)
  // 时间标题
  ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='left'
  ctx.fillText(lkPlay.value?`▶ 第 ${lkFrame.value} 帧（方块在动，绿箭头=LK算出来的光流向量）`:'⏸ 暂停中（点播放看动画）', ox+5, oy-8)
  // 蓝色运动方块
  const bw=50, bh=50
  let bx, by
  if(lkPlay.value){
    const t = lkFrame.value
    bx = 40 + ((t*lkSpeed.value)%(W-bw-80))
    by = 80 + Math.sin(t*0.15)*40
  }else{
    bx = 80; by = 100
  }
  // 背景静态纹理（给特征点附着的"角点"环境）
  ctx.fillStyle='#d0d0d0'
  for(let i=0;i<20;i++){
    const rx=(i*53+20)%(W-10), ry=(i*37+40)%(H-10)
    ctx.fillRect(ox+rx,oy+ry,6,6)
  }
  // 蓝色方块
  ctx.fillStyle='#2196f3';ctx.fillRect(ox+bx,oy+by,bw,bh)
  ctx.strokeStyle='#1565c0';ctx.lineWidth=1;ctx.strokeRect(ox+bx,oy+by,bw,bh)
  // 生成 N 个特征点（均匀撒在场景里，其中在方块上的点会"跟动"）
  const N = lkN.value
  const dx = lkPlay.value? lkSpeed.value : 0
  const dy = lkPlay.value? Math.cos(lkFrame.value*0.15)*40*0.15 : 0  // 瞬时dy
  const feats = []
  for(let i=0;i<N;i++){
    // 随机分布：一部分附着在方块上，一部分附着在静态背景
    const onBox = i%3!==0  // 2/3 点在方块上跟着动
    let px, py
    if(onBox){
      px = bx + ((i*17)%bw)
      py = by + ((i*23)%bh)
    }else{
      px = 20 + (i*41)%(W-40)
      py = 20 + (i*29)%(H-40)
      // 避开方块区域以免歧义
      if(px>bx&&px<bx+bw&&py>by&&py<py+bh){ px = 20+(px+80)%(W-40) }
    }
    feats.push({px,py,onBox,u:onBox?dx:0, v:onBox?dy:0})
  }
  // 画特征点+光流箭头
  feats.forEach(f=>{
    // 旧位置（黄点）
    ctx.fillStyle='#ffc107'
    ctx.beginPath();ctx.arc(ox+f.px-f.u, oy+f.py-f.v, 2.5, 0, Math.PI*2);ctx.fill()
    // 新位置（绿点）
    ctx.fillStyle='#4caf50'
    ctx.beginPath();ctx.arc(ox+f.px, oy+f.py, 3, 0, Math.PI*2);ctx.fill()
    // 箭头
    if(Math.abs(f.u)+Math.abs(f.v)>0.5){
      ctx.strokeStyle='#4caf50';ctx.lineWidth=1.5
      ctx.beginPath()
      ctx.moveTo(ox+f.px-f.u, oy+f.py-f.v)
      ctx.lineTo(ox+f.px, oy+f.py)
      ctx.stroke()
      // 箭头尖
      const ang=Math.atan2(f.v,f.u)
      ctx.beginPath()
      ctx.moveTo(ox+f.px, oy+f.py)
      ctx.lineTo(ox+f.px-5*Math.cos(ang-0.5), oy+f.py-5*Math.sin(ang-0.5))
      ctx.lineTo(ox+f.px-5*Math.cos(ang+0.5), oy+f.py-5*Math.sin(ang+0.5))
      ctx.closePath();ctx.fillStyle='#4caf50';ctx.fill()
    }
  })
  // 右侧文字解释
  const tx=ox+W+30
  ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='left'
  ctx.fillText('🟡 上一帧位置（t）', tx, oy+20)
  ctx.fillText('🟢 这一帧位置（t+1）', tx, oy+40)
  ctx.fillText('绿箭头 = LK 算出的位移向量', tx, oy+60)
  ctx.fillStyle='#1976d2';ctx.font='bold 13px'
  ctx.fillText(`速度 = ${lkSpeed.value} px/帧`, tx, oy+90)
  ctx.fillStyle='#333';ctx.font='12px'
  ctx.fillText('三个假设：', tx, oy+115)
  ctx.fillText('① 亮度恒定（点的灰度不变）', tx, oy+135)
  ctx.fillText('② 运动小（相邻帧位移小）', tx, oy+155)
  ctx.fillText('③ 邻域一致（窗口内点同方向）', tx, oy+175)
  ctx.fillText('解 AᵀA·d = Aᵀb 得每个点的(u,v)', tx, oy+195)
}

// ========== 11. 形态学 ==========
function drawMorph(){
  const c = morphCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const w=180,oy=30, scale=15
  // 原图：方块+毛刺+小洞
  const g=[]
  const N=12
  for(let y=0;y<N;y++){const r=[];for(let x=0;x<N;x++) r.push(0);g.push(r)}
  for(let y=3;y<9;y++)for(let x=2;x<10;x++) g[y][x]=1
  // 毛刺
  g[2][5]=1; g[9][6]=1; g[5][1]=1
  // 小洞
  g[5][5]=0; g[6][7]=0
  function drawGrid(g0,ox,title){
    ctx.strokeStyle='#ccc';ctx.strokeRect(ox-2,oy-2,N*scale+4,N*scale+4)
    for(let y=0;y<N;y++)for(let x=0;x<N;x++){
      ctx.fillStyle=g0[y][x]?'#212121':'#fff'
      ctx.fillRect(ox+x*scale,oy+y*scale,scale-1,scale-1)
    }
    ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='center'
    ctx.fillText(title, ox+N*scale/2, oy+N*scale+20)
  }
  drawGrid(g, 20, '原图（带毛刺+小洞）')
  // 处理
  const k=morphK.value
  function morph(g0, op){
    const out=g0.map(r=>r.slice())
    const r=(k-1)/2|0
    for(let y=0;y<N;y++)for(let x=0;x<N;x++){
      let found0=false, found1=false
      for(let j=-r;j<=r;j++)for(let i=-r;i<=r;i++){
        const ny=y+j,nx=x+i
        if(ny<0||ny>=N||nx<0||nx>=N) continue
        if(g0[ny][nx]===1) found1=true
        if(g0[ny][nx]===0) found0=true
      }
      if(op==='erode') out[y][x] = found0?0:1
      if(op==='dilate') out[y][x] = found1?1:0
    }
    return out
  }
  let out
  if(morphOp.value==='erode') out=morph(g,'erode')
  else if(morphOp.value==='dilate') out=morph(g,'dilate')
  else if(morphOp.value==='open') out=morph(morph(g,'erode'),'dilate')
  else out=morph(morph(g,'dilate'),'erode')
  drawGrid(out, 20+N*scale+60, {erode:'腐蚀后（毛刺被吃掉，图变小）',dilate:'膨胀后（小洞被填上，图变大）',open:'开运算=先腐后膨（去毛刺）',close:'闭运算=先膨后腐（填小洞）'}[morphOp.value])
  // 结构元
  const kox=20+N*scale*2+120
  ctx.fillStyle='#333';ctx.font='13px';ctx.textAlign='center'
  ctx.fillText(`结构元 ${k}×${k}`, kox+k*scale/2, oy-10)
  for(let y=0;y<k;y++)for(let x=0;x<k;x++){
    ctx.fillStyle='#1976d2'
    ctx.fillRect(kox+x*scale, oy+y*scale+20, scale-1, scale-1)
  }
}

// ========== 12. 高斯 ==========
function drawGauss(){
  const c = gaussCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const ox=60,oy=30,w=500,h=220
  ctx.strokeStyle='#ccc';ctx.strokeRect(ox,oy,w,h)
  // 画坐标轴
  ctx.strokeStyle='#999';ctx.beginPath()
  ctx.moveTo(ox,oy+h);ctx.lineTo(ox+w,oy+h)
  ctx.moveTo(ox,oy);ctx.lineTo(ox,oy+h);ctx.stroke()
  ctx.fillStyle='#666';ctx.font='12px';ctx.textAlign='center'
  ctx.fillText('-3σ', ox+w*0.1, oy+h+15)
  ctx.fillText('0', ox+w/2, oy+h+15)
  ctx.fillText('+3σ', ox+w*0.9, oy+h+15)
  // 画高斯曲线
  const σ=gaussSigma.value
  ctx.strokeStyle='#e91e63';ctx.lineWidth=3;ctx.beginPath()
  for(let i=0;i<=w;i++){
    const x = (i/w-0.5)*6*σ
    const y = Math.exp(-x*x/(2*σ*σ))
    const px=ox+i, py=oy+h-y*h*0.9
    if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py)
  }
  ctx.stroke()
  // 填充
  ctx.fillStyle='rgba(233,30,99,0.2)'
  ctx.lineTo(ox+w,oy+h);ctx.lineTo(ox,oy+h);ctx.fill()
  // 3x3 核
  const kox=ox+w+40,koy=oy,ks=40
  ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='center'
  ctx.fillText(`对应 3×3 高斯核（σ=${σ.toFixed(1)}）`, kox+ks*1.5, koy-10)
  const kern=[];let ksum=0
  for(let j=-1;j<=1;j++){const r=[];for(let i=-1;i<=1;i++){
    const v=Math.exp(-(i*i+j*j)/(2*σ*σ));r.push(v);ksum+=v
  };kern.push(r)}
  for(let y=0;y<3;y++)for(let x=0;x<3;x++){
    const v=kern[y][x]/ksum
    const g=255-(v*255*8|0)
    ctx.fillStyle=`rgb(${g},${100+v*155|0},255)`
    ctx.fillRect(kox+x*ks,koy+y*ks+20,ks-2,ks-2)
    ctx.fillStyle='#000';ctx.font='12px monospace';ctx.textAlign='center';ctx.textBaseline='middle'
    ctx.fillText(v.toFixed(2),kox+x*ks+ks/2,koy+y*ks+ks/2+20)
  }
  ctx.fillStyle='#333';ctx.font='13px sans-serif';ctx.textAlign='left';ctx.textBaseline='alphabetic'
  ctx.fillText(`G(x,y) = (1/2πσ²) · e^(-(x²+y²)/2σ²)`, ox, oy+h+40)
  ctx.fillText(`σ越大 → 曲线越"矮胖" → 模糊越厉害`, ox, oy+h+60)
}

// ========== 13. 颜色空间 ==========
function hsv2rgb(h,s,v){
  s/=100;v/=100
  const c=v*s, x=c*(1-Math.abs(((h/60)%2)-1)), m=v-c
  let r,g,b
  if(h<60)[r,g,b]=[c,x,0];else if(h<120)[r,g,b]=[x,c,0];else if(h<180)[r,g,b]=[0,c,x]
  else if(h<240)[r,g,b]=[0,x,c];else if(h<300)[r,g,b]=[x,0,c];else[r,g,b]=[c,0,x]
  return [(r+m)*255|0,(g+m)*255|0,(b+m)*255|0]
}
function drawColor(){
  const c = colorCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  // RGB 三灯
  const ox=40,oy=40,sz=80
  const [r,g,b]=hsv2rgb(colorH.value,colorS.value,100)
  ctx.fillStyle=`rgb(${r},0,0)`;ctx.fillRect(ox,oy,sz,sz)
  ctx.fillStyle=`rgb(0,${g},0)`;ctx.fillRect(ox+sz+10,oy,sz,sz)
  ctx.fillStyle=`rgb(0,0,${b})`;ctx.fillRect(ox+2*sz+20,oy,sz,sz)
  ctx.fillStyle='#333';ctx.font='13px';ctx.textAlign='center'
  ctx.fillText(`R=${r}`, ox+sz/2, oy+sz+20)
  ctx.fillText(`G=${g}`, ox+sz+10+sz/2, oy+sz+20)
  ctx.fillText(`B=${b}`, ox+2*sz+20+sz/2, oy+sz+20)
  ctx.fillText('+', ox+sz+5, oy+sz/2);ctx.fillText('+', ox+2*sz+15, oy+sz/2)
  // 混合结果
  ctx.fillStyle=`rgb(${r},${g},${b})`
  ctx.fillRect(ox+3*sz+50,oy,sz,sz)
  ctx.strokeStyle='#333';ctx.strokeRect(ox+3*sz+50,oy,sz,sz)
  ctx.fillText('混合色', ox+3*sz+50+sz/2, oy+sz+20)
  // HSV 色相环
  const cx=480,cy=150,rad=60
  for(let a=0;a<360;a++){
    const [rr,gg,bb]=hsv2rgb(a,colorS.value,100)
    ctx.strokeStyle=`rgb(${rr},${gg},${bb})`;ctx.lineWidth=8
    ctx.beginPath()
    ctx.arc(cx,cy,rad,a*Math.PI/180,(a+1)*Math.PI/180);ctx.stroke()
  }
  // 选中标
  const th=colorH.value*Math.PI/180
  ctx.fillStyle='#fff';ctx.beginPath()
  ctx.arc(cx+Math.cos(th)*rad, cy+Math.sin(th)*rad, 6,0,Math.PI*2);ctx.fill()
  ctx.strokeStyle='#000';ctx.stroke()
  ctx.fillStyle='#333';ctx.textAlign='center';ctx.font='13px'
  ctx.fillText(`H=${colorH.value}°（色相=是什么颜色）`, cx, cy+rad+30)
  ctx.fillText(`S=${colorS.value}%（饱和度=鲜艳程度）`, cx, cy+rad+50)
  ctx.fillText('V=100%（明度=亮暗）', cx, cy+rad+70)
}

// ========== 14. 直方图 ==========
function drawHist(){
  const c = histCanvas.value; if(!c) return
  const ctx = c.getContext('2d')
  ctx.clearRect(0,0,c.width,c.height)
  const W=200
  // 生成图像
  const g=[]
  for(let y=0;y<W;y++){const r=[];for(let x=0;x<W;x++){
    let v
    if(histType.value==='dark') v = 30+Math.random()*60
    else if(histType.value==='bright') v = 160+Math.random()*60
    else if(histType.value==='lowc') v = 100+Math.random()*60
    else v = Math.random()*255
    r.push(v|0)
  };g.push(r)}
  function drawImg(g0,ox,oy,title){
    const scale=1
    for(let y=0;y<W;y++)for(let x=0;x<W;x++){
      const v=g0[y][x]
      ctx.fillStyle=`rgb(${v},${v},${v})`
      ctx.fillRect(ox+x*scale,oy+y*scale,scale,scale)
    }
    ctx.fillStyle='#333';ctx.font='13px';ctx.textAlign='center'
    ctx.fillText(title, ox+W/2, oy+W+20)
  }
  function drawHist0(g0,ox,oy,title){
    const h=new Array(256).fill(0)
    for(let y=0;y<W;y++)for(let x=0;x<W;x++) h[g0[y][x]]++
    const maxH=Math.max(...h)
    ctx.strokeStyle='#ccc';ctx.strokeRect(ox,oy,W,100)
    ctx.fillStyle='#1976d2'
    for(let i=0;i<256;i++){
      ctx.fillRect(ox+i*W/256, oy+100-h[i]/maxH*95, W/256+0.5, h[i]/maxH*95)
    }
    ctx.fillStyle='#333';ctx.font='13px';ctx.textAlign='center'
    ctx.fillText(title, ox+W/2, oy+120)
  }
  function equalize(g0){
    const h=new Array(256).fill(0)
    for(let y=0;y<W;y++)for(let x=0;x<W;x++) h[g0[y][x]]++
    const N=W*W, cdf=new Array(256).fill(0)
    cdf[0]=h[0];for(let i=1;i<256;i++)cdf[i]=cdf[i-1]+h[i]
    const map=[]
    const min=cdf.find(v=>v>0)
    for(let i=0;i<256;i++) map[i]=Math.round((cdf[i]-min)/(N-min)*255)
    const out=[]
    for(let y=0;y<W;y++){const r=[];for(let x=0;x<W;x++)r.push(map[g0[y][x]]);out.push(r)}
    return out
  }
  // 原图 + 直方图
  drawImg(g,30,30,'原图')
  drawHist0(g,30,30+W+40,'原图直方图')
  if(histEq.value){
    const eq=equalize(g)
    drawImg(eq,30+W+60,30,'均衡化后')
    drawHist0(eq,30+W+60,30+W+40,'均衡化后直方图（拉开了）')
  }
}

// ========== 统一绘制调度 ==========
// 每个 drawXXX 内部都会自行判空（const c = xxxCanvas.value; if(!c) return），
// 所以这里绝不能用某个具体 canvas（如 pixelCanvas）是否存在当"总开关"：
// 当页面初始 tab 不是 pixel（例如算法页用 initial-tab="lk" 嵌入）时，
// pixelCanvas 因 v-if 根本没挂载，总守卫会让整个渲染直接退出，表现为"原理图一片空白"。
function render(){
  drawPixel(); drawNeighbor(); drawConv(); drawGrad()
  drawThresh(); drawHough(); drawHarris(); drawFourier()
  drawRansac(); drawLK(); drawMorph(); drawGauss()
  drawColor(); drawHist()
}

// tab 切换会先卸载旧 canvas、再挂载新 canvas，必须等 DOM 更新完再画：
// nextTick 保证 v-if 已完成切换，rAF 再补一次以确保拿到稳定布局尺寸。
function renderStable(){
  nextTick(()=>{
    render()
    requestAnimationFrame(()=>render())
  })
}

onMounted(()=>{
  isMounted.value = true
  ransacPoints.value = genRansacPoints()
  // 多重保险：nextTick / rAF / 50ms / 200ms 共 4 次，应对水合时序、v-if 切换
  renderStable()
  setTimeout(renderStable, 50)
  setTimeout(renderStable, 200)
  // 周期兜底重绘（100ms 一次），保证 canvas 不白屏 + LK/RANSAC 动画流畅
  const timer = setInterval(()=>{
    // LK 播放：推进帧
    if(lkPlay.value && current.value==='lk'){
      lkFrame.value++
    }
    // RANSAC 自动跑：每 tick 走 3 步
    if(ransacAuto.value && current.value==='ransac'){
      for(let k=0;k<3;k++) ransacStep()
    }
    render()
  }, 100)
  // tab 切换后重绘
  watch(current, ()=>{ renderStable() })
  // state 变化重绘
  ;[distType,kernelType,convX,convY,edgeDir,threshT,houghN,harrisType,freqCut,
    lkSpeed,lkN,morphOp,morphK,gaussSigma,colorH,colorS,histType,histEq,
    neighborCx,neighborCy,ransacThresh,ransacOutRatioPct,ransacIter,ransacBest,ransacPoints
  ].forEach(s=>watch(s, render))
  // 外点比例变化 → 重新生成点
  watch(ransacOutRatioPct, ()=>{ ransacReset() })
  onBeforeUnmount(()=>{
    clearInterval(timer)
    if(ransacAutoTimer.value){ clearInterval(ransacAutoTimer.value); ransacAutoTimer.value=null }
    if(lkTimer.value){ clearInterval(lkTimer.value); lkTimer.value=null }
  })
})
</script>

<style scoped>
.math-vis{border:1px solid #e0e0e0;border-radius:10px;background:#fafafa;padding:15px;margin:20px 0}
.math-vis-compact{padding:10px 12px;margin:14px 0}
.math-vis-compact .tab-bar{margin-bottom:10px}
.embed-hint{font-size:13px;line-height:1.6;color:#4a5568;background:#eef6ff;border-left:3px solid #4a90d9;padding:8px 12px;border-radius:4px;margin:0 0 10px}
.tab-bar{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:15px}
.tab-btn{padding:8px 14px;border:1px solid #ddd;border-radius:20px;background:#fff;cursor:pointer;font-size:13px;transition:.2s}
.tab-btn:hover{background:#f0f7ff}
.tab-btn.active{background:#1976d2;color:#fff;border-color:#1976d2}
.vis-area{background:#fff;border-radius:8px;padding:20px;min-height:400px;overflow-x:auto}
.sub-vis h3{margin:0 0 8px;font-size:17px;color:#222}
.sub-vis .desc{color:#666;font-size:13px;margin:0 0 12px;line-height:1.6}
.sub-vis canvas{border:1px solid #eee;border-radius:6px;display:block;margin:10px 0;background:#fff}
.ctrl-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:10px 0;font-size:13px;color:#333}
.ctrl-row input[type=range]{width:140px}
.ctrl-row select{padding:4px 8px;border:1px solid #ccc;border-radius:4px}
.ctrl-row button{padding:5px 12px;border:1px solid #1976d2;background:#fff;color:#1976d2;border-radius:6px;cursor:pointer;font-size:13px;transition:.2s}
.ctrl-row button:hover{background:#e3f2fd}
.tip-row{font-size:12.5px;color:#666;background:#f5f9ff;border-left:3px solid #90caf9;padding:6px 12px;border-radius:4px;margin:8px 0 4px;line-height:1.6}
.calc{background:#fff3e0;padding:8px 12px;border-left:3px solid #ff9800;font-size:13px;color:#333;border-radius:4px;margin:10px 0}
.explain-card{background:linear-gradient(135deg,#fff9e6 0%,#fff3c2 100%);border:1px solid #f0d978;border-left:4px solid #e6a700;border-radius:8px;padding:14px 18px;margin:10px 0 14px;font-size:13.5px;line-height:1.7;color:#3a2e00}
.explain-card .ec-head{font-size:15px;font-weight:700;color:#a06e00;margin-bottom:8px}
.explain-card .ec-row{margin:6px 0}
.explain-card .ec-row b{color:#6b4f00;margin-right:4px}
.explain-card .ec-steps{margin:4px 0 4px 20px;padding:0}
.explain-card .ec-steps li{margin:3px 0}
.explain-card .ec-kicker{display:inline-block;background:#fff;border:1px dashed #d4a017;padding:4px 10px;border-radius:4px;color:#8a5a00;font-weight:600;margin-top:2px}
</style>
