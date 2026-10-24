# 🏗 算法流程

```mermaid
flowchart TD
  S[第 t 帧 I_t] --> INIT{已有背景模型?}
  INIT --否--> INITM[用第一帧初始化 K 个高斯]
  INIT --是--> MATCH
  INITM --> MATCH[对每个像素 x]
  MATCH --> TEST[对 K 个高斯: |I[x]-μ_k|<2.5σ_k ?]
  TEST --匹配到一个--> UPD[更新该高斯的 μ,σ,权重 w]
  TEST --一个都没匹配--> NEW[若 K<上限: 新建一个高斯<br/>否则替换权重最小的]
  UPD --> RANK[按 w/σ 从大到小排序高斯]
  NEW --> RANK
  RANK --> TH[取前 B 个: Σw > T → 这 B 个是"背景高斯"]
  TH --> JUDGE{x 落在前 B 个里?}
  JUDGE --是--> BGM[前景掩码=0 背景]
  JUDGE --否--> FGM[前景掩码=255 运动物体]
  FGM --> SH{阴影检测开?}
  SH --是且亮度低于背景--> SHD[掩码=127 阴影]
  SH --否--> END
  BGM --> END[输出 fgMask]
  SHD --> END
```

## 后处理必备 3 步（裸 MOG2 掩码噪声很大）

```mermaid
flowchart LR
  A[MOG2 原始掩码] --> B[开运算 MORPH_OPEN 3x3<br/>去椒盐噪声]
  B --> C[闭运算 MORPH_CLOSE 7x7<br/>填洞]
  C --> D[找轮廓 findContours<br/>过滤掉小于 100 像素的小块]
  D --> E[干净的运动区域框]
```

没有后处理的 MOG2 掩码基本没法用——满屏雪花。

## 阴影检测原理（MOG2 的杀手锏）

阴影不会改变颜色**色调**，只会让亮度变暗。所以 MOG2 检查「新像素是不是比背景暗了 0.5~0.8 倍，但色相差不多」——是就是阴影，标成 127 灰色而不是 255 白色。**不要把阴影当运动目标**。
