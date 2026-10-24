<AlgorithmCard
  name="CSRT 通道与空间可靠性跟踪"
  enName="Channel and Spatial Reliability Tracking (Discriminative Correlation Filter with Channel and Spatial Reliability)"
  chapter="ch14"
  branch="detection"
  year="2017"
  author="Alan Lukežič / Tomáš Vojíř / Luka Čehovin / Jiří Matas / Matej Kristan"
  paper="CVPR 2017"
  level="mid"
  tagline="KCF 的进化版——不只认矩形框，还学会了「这个形状里哪部分是目标、哪部分应该被忽略、哪个特征通道更可信」，精度是 OpenCV 传统跟踪器里最高的一档"
  analogy="KCF 像你拿一张**矩形便利贴**在画面上找相似位置，贴到哪里响应最大就说目标在那；但如果目标是个走路的人，便利贴矩形里有一半是背景，模板会越跟越飘。CSRT 学会了两件事：①在便利贴上画一个**不规则的遮罩**（空间可靠性），只学目标本身的像素；②多通道（HoG+Colornames）投票时，给「靠谱的通道」更多权重（通道可靠性）。"
  scene="视频中单个目标的长时跟踪，尤其是目标**非矩形**（如行人、动物）、有**遮挡**（过柱子/过人）、有**形变**（转身、弯腰）的场景；速度稍慢于 KCF，但精度显著更高。"
  :pros='["精度是 OpenCV 传统跟踪器里最高的一档（VOT 2016/2017 冠军）", "支持非矩形空间掩膜", "多通道可靠性加权", "对遮挡/形变比 KCF 鲁棒", "OpenCV contrib 原生支持"]'
  :cons='["速度比 KCF 慢（CPU 约 25–50 FPS vs KCF 150+ FPS）", "需要 opencv-contrib-python 才有 TrackerCSRT", "参数比 KCF 多", "长时全遮挡仍会飘（需配检测器重检）"]'
/>


## 一分钟速览

**CSRT 通道与空间可靠性跟踪**（Channel and Spatial Reliability Tracking (Discriminative Correlation Filter with Channel and Spatial Reliability)，2017，Alan Lukežič / Tomáš Vojíř / Luka Čehovin / Jiří Matas / Matej Kristan）
在 DCF 框架里引入空间可靠性图（基于前景/背景颜色分割自动估计）和通道可靠性（基于 PSR 峰值旁瓣比），把 KCF 从「矩形刚性模板」升级为「感知形状和通道质量的鲁棒跟踪器」——是 OpenCV 里传统单目标跟踪的首选精度型算法。

<ChildPages />
