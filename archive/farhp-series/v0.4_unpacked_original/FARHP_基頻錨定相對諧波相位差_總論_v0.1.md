# 基頻錨定相對諧波相位差總論  
## 相位不變量、動態發音物件與可生成符號語言的統一架構

**英文題名：** *Fundamental-Anchored Relative Harmonic Phase: A General Framework for Phase Invariants, Dynamic Pronunciation Objects, and Generative Symbolic Languages*  

**縮寫：** FARHP  
**中文簡稱：** 基錨相差  
**作者：** Neo.K（EveMissLab）  
**AI 協作：** Aletheia（GPT-5.6 Thinking）  
**版本：** v0.1  
**日期：** 2026-07-25  
**文件性質：** 系列總篇／母論文

---

## 摘要

語音與一般諧波聲音通常可由頻率、振幅、相位及非週期殘差共同描述。然而，在許多傳統語音分析與合成架構中，相位常被最小相位近似、隨機相位、既定相位規則或神經網路中的隱式波形生成所取代。這種做法能有效降低模型複雜度，卻也使相位不再成為可明確觀察、操作、交換與離散編碼的發音參數。

本文提出「基頻錨定相對諧波相位差」（Fundamental-Anchored Relative Harmonic Phase, FARHP）作為一個面向發音生成、語音分析、音色控制與符號語言整合的統一框架。其核心不是宣稱首次發明以基頻正規化諧波相位的數學式；相同或高度相近的關係已存在於 Relative Phase Shift（RPS）及相關諧波相位研究中。本文的主要貢獻，在於將此類相對相位關係重新組織為：一、具有明確等價關係與不變性條件的動態相位物件；二、能攜帶有效性遮罩、置信度、非諧波殘差與聲調軌跡的完整發音單位；三、可連續表示、離散量化並映射至新型符號字形的生成架構；四、能被傳統數位訊號處理、可微分合成器及人工智慧模型共同使用的中介層。

本文首先定義 FARHP 的靜態與動態形式，說明其時間平移不變性成立的條件，並將相位狀態置於圓周乘積空間而非一般歐氏空間。其次，本文區分相位、基頻、聲調、頻譜包絡、聲源、聲道濾波與非週期殘差，避免將國語聲調或完整語音差異錯誤還原成單一相位參數。接著，本文提出連續複數表示、離散相位碼本、相位有效性遮罩、置信度加權及合成—反演流程。最後，本文給出由純諧波訊號、持續母音、華語音節到以諾式擴充符號語言的分階段驗證方案，並規定哪些主張必須由可重複的聽覺實驗與波形重建實驗支持。

FARHP 因而不是一套以相位取代全部語音學的封閉理論，而是一個把相位從被動重建項轉化為可明示控制變數的研究綱領。其長期目標，是建立一個能在「字形—音節—相位聲學—形式語義」之間往返映射的 AI 原生發音與符號系統。

**關鍵詞：** 相對相位、諧波模型、基頻錨定、語音合成、聲碼器、相位量化、華語音節、符號語言、AI 原生語言

---

# 0. 研究定位與新穎性邊界

## 0.1 不是重新命名既有公式

設第 $k$ 個諧波的瞬時相位為 $\phi_k(t)$，基頻分量的瞬時相位為 $\phi_1(t)$。本文採用的核心相對量為：

$$
\psi_k(t)
=
\operatorname{wrap}
\left(
\phi_k(t)-k\phi_1(t)
\right).
$$

此式與既有 Relative Phase Shift（RPS）文獻中的核心關係一致或高度相近。RPS 已被用於諧波相位表示、語音辨識、說話者辨識、合成語音偵測、極性判定與相位操控。因此，本文不得將上述公式本身宣稱為首次提出。

本文所稱「FARHP」指的不是單一公式，而是包含以下要素的擴張框架：

1. 將相對諧波相位明確建模為位於圓環或環面上的狀態；
2. 將靜態框架擴張為跨時間的相位軌跡；
3. 引入相位有效性遮罩、估計置信度與錨定可靠度；
4. 將有聲諧波層與非諧波殘差層分開處理；
5. 將聲調軌跡與諧波相位差分層處理；
6. 建立可逆或近似可逆的離散相位碼本；
7. 建立相位碼、字形附標、AI 向量與聲波生成之間的映射；
8. 將分析、修改、合成、反演與感知驗證納入同一規格。

所以，FARHP 的新穎性若能成立，將主要存在於**系統化形式化、跨層整合、離散符號化與可生成架構**，而不在於對既有 RPS 關係的所有權主張。

## 0.2 研究對象

本文的主要研究對象是準週期或局部準週期的有聲訊號，特別是：

- 持續母音；
- 鼻音與近音的有聲區段；
- 帶有穩定基頻的音節核心；
- 可由諧波與殘差混合模型表示的語音；
- 人工設計的可發音符號單位。

擦音、爆破瞬間、氣流噪聲及其他顯著非週期區段，不能只依賴 FARHP 表示，而必須由非諧波殘差、事件模型或其他聲學層補足。

## 0.3 研究目的

FARHP 的目的不是把聲音神秘化為「一切皆相位」，而是回答一個較窄、可驗證的問題：

> 當頻率、振幅、頻譜包絡與非週期殘差已被明確建模時，諧波之間相對於基頻的相位結構，能否成為穩定、可操控、可學習且可符號化的發音參數？

---

# 1. 問題背景

## 1.1 語音中的相位缺席

對離散短時語音框架 $x_t[n]$ 進行傅立葉轉換，可得複數頻譜：

$$
X_t[\omega]
=
A_t[\omega]e^{i\Phi_t[\omega]}.
$$

其中 $A_t[\omega]$ 是幅度頻譜，$\Phi_t[\omega]$ 是相位頻譜。兩者共同決定波形，但工程系統常優先保留幅度、梅爾頻譜、倒頻譜、基頻及週期性指標，再由最小相位、迭代重建、神經聲碼器或直接波形生成補回相位。

這並不代表相位必然不重要。更精確的說法是：

- 相位的週期包覆使學習與比較較困難；
- 絕對相位對分析窗口位置敏感；
- 不同頻率成分的相位不能直接當作普通線性變數；
- 部分相位改變在日常語音中感知影響細微；
- 高品質合成又要求跨框架相位連續，否則可能出現點擊、粗糙或失真；
- 端到端神經模型可隱式生成相位，但不一定提供可解釋、可交換的相位控制介面。

因此，問題不是「語音需不需要相位」，而是：

> 應保留哪一種相位關係，才能消除不必要的分析位置依賴，同時保留可操作的波形結構？

## 1.2 以基頻作為局部時鐘

在理想週期訊號中，基頻 $f_0$ 提供一個週期：

$$
T_0=\frac{1}{f_0}.
$$

第 $k$ 個諧波位於：

$$
f_k=kf_0.
$$

若所有諧波共享同一個基礎週期，基頻相位便可以被理解為局部週期時鐘。將第 $k$ 諧波相位扣除 $k$ 倍基頻相位，相當於移除共同時間平移造成的線性相位項，保留諧波之間對波形形狀更直接的相對關係。

這就是 FARHP 的物理直覺：

> 基頻不是唯一有意義的聲學成分，但它可以作為準週期發音中的局部相位座標原點。

---

# 2. 諧波聲音模型

## 2.1 局部諧波表示

在一個足夠短、可假定局部準平穩的有聲框架中，訊號可近似為：

$$
x_t[n]
=
\sum_{k=1}^{K_t}
A_{t,k}
\cos
\left(
\theta_{t,k}[n]
\right)
+
r_t[n],
$$

其中：

$$
\theta_{t,k}[n]
=
2\pi f_{t,k}\frac{n}{F_s}
+
\phi_{t,k},
$$

且：

- $A_{t,k}\ge 0$ 為第 $k$ 分量的振幅；
- $f_{t,k}$ 為其頻率；
- $\phi_{t,k}$ 為框架參考點上的相位；
- $F_s$ 為取樣率；
- $r_t[n]$ 為無法由有限諧波組精確表示的殘差；
- $K_t$ 為此框架中可可靠估計的諧波數。

理想諧波條件為：

$$
f_{t,k}=kf_{0,t}.
$$

真實語音則可能只有近似關係：

$$
f_{t,k}
=
kf_{0,t}
+
\epsilon_{t,k},
$$

其中 $\epsilon_{t,k}$ 代表失諧、估計誤差、調頻或非平穩性。

## 2.2 複數振幅

將每個諧波寫成複數係數：

$$
C_{t,k}
=
A_{t,k}e^{i\phi_{t,k}},
$$

可將振幅與相位放入同一物件。FARHP 不要求所有模型都採用同一種傅立葉分析法；只要能估計局部基頻、諧波振幅與相位，就可以建構相位差。

---

# 3. FARHP 的正式定義

## 3.1 相位包覆

定義：

$$
\operatorname{wrap}(\alpha)
=
\left(
(\alpha+\pi)\bmod 2\pi
\right)-\pi.
$$

其值域取為：

$$
(-\pi,\pi].
$$

任何相差都應被視為模 $2\pi$ 的等價類，而不是無界實數。

## 3.2 基頻錨定相對諧波相位差

對第 $t$ 個框架、第 $k$ 個諧波，定義：

$$
\boxed{
\psi_{t,k}
=
\operatorname{wrap}
\left(
\phi_{t,k}
-
k\phi_{t,1}
\right)
}
\qquad
k=2,\ldots,K_t.
$$

基頻本身滿足：

$$
\psi_{t,1}=0.
$$

單一框架的 FARHP 狀態為：

$$
\boldsymbol{\Psi}_t
=
\left(
\psi_{t,2},
\psi_{t,3},
\dots,
\psi_{t,K_t}
\right).
$$

若固定最大諧波數 $K$，則：

$$
\boldsymbol{\Psi}_t
\in
\left(S^1\right)^{K-1},
$$

亦即 $K-1$ 個圓周的笛卡兒積。這個空間是一個環面，而不是一般的歐氏向量空間。

## 3.3 動態 FARHP

語音不是一組固定相位，而是隨時間變動的軌跡：

$$
\boldsymbol{\Psi}
:
t
\mapsto
\boldsymbol{\Psi}(t).
$$

完整的動態 FARHP 物件定義為：

$$
\mathfrak{P}
=
\left(
\boldsymbol{\Psi}(t),
\mathbf{A}(t),
f_0(t),
\mathbf{m}(t),
\mathbf{c}(t)
\right),
$$

其中：

- $\boldsymbol{\Psi}(t)$：相對相位軌跡；
- $\mathbf{A}(t)$：諧波振幅軌跡；
- $f_0(t)$：基頻軌跡；
- $\mathbf{m}(t)$：相位有效性遮罩；
- $\mathbf{c}(t)$：相位估計置信度。

有效性遮罩：

$$
m_{t,k}\in\{0,1\},
$$

表示該框架中的第 $k$ 諧波是否具有足夠能量及可靠頻率對應，可被納入相位分析。

置信度則滿足：

$$
c_{t,k}\in[0,1].
$$

這兩個量是 FARHP 與簡單 RPS 向量的重要工程區分之一：真實語音中並非每個框架、每個諧波都值得被同等信任。

## 3.4 複數圓周表示

為避免 $-\pi$ 與 $\pi$ 的表面不連續，定義：

$$
z_{t,k}
=
e^{i\psi_{t,k}}
=
\cos\psi_{t,k}
+
i\sin\psi_{t,k}.
$$

AI 模型的實值輸入可寫成：

$$
\mathbf{p}_{t,k}
=
\left(
\cos\psi_{t,k},
\sin\psi_{t,k}
\right).
$$

如此，相位 $-\pi+\varepsilon$ 與 $\pi-\varepsilon$ 在向量空間中仍然彼此接近。

---

# 4. 不變性與等價關係

## 4.1 理想共同時間平移不變性

考慮訊號平移 $\tau$。在理想諧波條件下：

$$
\phi'_{t,k}
=
\phi_{t,k}
-
2\pi kf_0\tau,
$$

且：

$$
\phi'_{t,1}
=
\phi_{t,1}
-
2\pi f_0\tau.
$$

則：

$$
\begin{aligned}
\psi'_{t,k}
&=
\operatorname{wrap}
\left(
\phi'_{t,k}
-
k\phi'_{t,1}
\right)
\\
&=
\operatorname{wrap}
\left(
\phi_{t,k}
-
2\pi kf_0\tau
-
k\phi_{t,1}
+
2\pi kf_0\tau
\right)
\\
&=
\operatorname{wrap}
\left(
\phi_{t,k}
-
k\phi_{t,1}
\right)
\\
&=
\psi_{t,k}.
\end{aligned}
$$

所以，在以下條件成立時，FARHP 對共同時間平移不變：

1. 分量確實服從整數諧波關係；
2. 基頻估計正確；
3. 相位來自同一時間參考；
4. 框架內可近似局部平穩；
5. 沒有嚴重的頻率漂移或相位解纏錯誤。

因此本文只主張**條件性不變性**，不主張在任意非平穩聲音中絕對不變。

## 4.2 失諧時的殘餘項

若：

$$
f_k=kf_0+\epsilon_k,
$$

時間平移後可產生殘餘相差：

$$
\Delta\psi_k
\approx
-2\pi\epsilon_k\tau.
$$

這表示 FARHP 對時間平移的穩定程度，也可以反過來成為諧波模型是否適用的診斷量。

## 4.3 相位等價類

若兩組相位向量 $\boldsymbol{\phi}$ 與 $\boldsymbol{\phi}'$ 只相差由共同時間平移產生的線性相位項，則可定義：

$$
\boldsymbol{\phi}
\sim
\boldsymbol{\phi}'
$$

當且僅當存在 $\delta\in S^1$，使得：

$$
\phi'_k
=
\phi_k+k\delta
\pmod{2\pi}.
$$

FARHP 可以被理解為對此等價關係取商後的一組座標：

$$
\mathcal{H}/S^1.
$$

這裡的 $S^1$ 作用由：

$$
\delta\cdot\phi_k
=
\phi_k+k\delta
$$

給出。換句話說，FARHP 移除的是由共同週期時鐘造成的一維自由度，而保留其餘諧波相對結構。

## 4.4 圓周距離

單一相位差的距離定義為：

$$
d_{S^1}(\alpha,\beta)
=
\left|
\operatorname{wrap}
\left(
\alpha-\beta
\right)
\right|.
$$

加權 FARHP 距離可定義為：

$$
D_t
\left(
\boldsymbol{\Psi}^{(a)},
\boldsymbol{\Psi}^{(b)}
\right)
=
\frac{
\sum_{k=2}^{K}
w_{t,k}
d_{S^1}
\left(
\psi^{(a)}_{t,k},
\psi^{(b)}_{t,k}
\right)^2
}{
\sum_{k=2}^{K}w_{t,k}
},
$$

其中：

$$
w_{t,k}
=
m^{(a)}_{t,k}
m^{(b)}_{t,k}
c^{(a)}_{t,k}
c^{(b)}_{t,k}
g(A^{(a)}_{t,k},A^{(b)}_{t,k}).
$$

$g$ 可依振幅或訊噪比降低弱諧波的影響。

---

# 5. 聲學分層：相位不能取代什麼

## 5.1 發音不是單一相位向量

完整聲音至少可分為：

$$
\text{聲音}
=
\text{基頻軌跡}
+
\text{諧波振幅}
+
\text{相對相位}
+
\text{頻譜包絡}
+
\text{非諧波殘差}
+
\text{時間事件}.
$$

FARHP 只直接處理其中的「相對諧波相位」層。

## 5.2 聲源—濾波器關係

語音常以聲源—濾波器模型近似：

$$
X(\omega)
=
G(\omega)H(\omega)R(\omega),
$$

其中：

- $G(\omega)$：聲門聲源；
- $H(\omega)$：聲道濾波；
- $R(\omega)$：唇輻射或其他輸出效應。

其相位滿足：

$$
\Phi_X(\omega)
=
\Phi_G(\omega)
+
\Phi_H(\omega)
+
\Phi_R(\omega)
\pmod{2\pi}.
$$

因此，從最終語音抽出的 FARHP 是混合結果，不應直接被解釋為純聲門相位、純聲道相位或單一生理機制。若要做因果解釋，還需要聲門反演、共振峰模型或可微分聲源—濾波器模型。

## 5.3 國語聲調不是 FARHP

國語聲調主要體現在音高輪廓、時長、能量、音質及上下文協同變化。可將聲調物件表示為：

$$
\mathcal{T}_q
=
\left(
f_{0,q}(t),
a_q(t),
d_q,
v_q(t)
\right),
$$

其中：

- $q\in\{1,2,3,4,0\}$；
- $f_{0,q}(t)$：基頻軌跡；
- $a_q(t)$：能量或振幅包絡；
- $d_q$：時長；
- $v_q(t)$：發聲型態或音質輔助量。

FARHP 可與聲調協同，但不能把四聲與輕聲直接等同於五個相位值。

## 5.4 非週期聲音

擦音、爆破、送氣、氣聲及高頻噪聲需要額外殘差：

$$
r_t[n]
=
r^{\mathrm{noise}}_t[n]
+
r^{\mathrm{transient}}_t[n]
+
r^{\mathrm{model}}_t[n].
$$

因此，完整發音單位可寫成：

$$
\boxed{
\Pi
=
\left(
\mathcal{O},
\mathcal{R},
\mathcal{T},
\mathbf{A},
\boldsymbol{\Psi},
\mathcal{N},
\mathcal{E},
d
\right)
}
$$

其中：

- $\mathcal{O}$：聲母或起始事件；
- $\mathcal{R}$：介音、韻腹與韻尾；
- $\mathcal{T}$：聲調與韻律；
- $\mathbf{A}$：諧波振幅；
- $\boldsymbol{\Psi}$：FARHP；
- $\mathcal{N}$：非諧波殘差；
- $\mathcal{E}$：瞬態事件；
- $d$：時長。

---

# 6. FARHP 的表示方法

## 6.1 連續表示

最完整的表示為：

$$
\mathcal{F}_{\mathrm{cont}}
=
\left\{
f_0(t),
A_k(t),
\cos\psi_k(t),
\sin\psi_k(t),
m_k(t),
c_k(t)
\right\}_{k=2}^{K}.
$$

這適合：

- 高品質重建；
- 可微分合成；
- 相位軌跡學習；
- 說話者或音色分析；
- 連續變換。

## 6.2 離散相位量化

定義 $M$ 相位量化器：

$$
Q_M(\psi)
=
\left\lfloor
\frac{
M\left(
\operatorname{wrap}(\psi)+\pi
\right)
}{
2\pi
}
\right\rfloor
\bmod M.
$$

其代表角可取：

$$
\widehat{\psi}_q
=
-\pi
+
\frac{2\pi}{M}
\left(
q+\frac{1}{2}
\right),
\qquad
q=0,\ldots,M-1.
$$

第一版可比較：

$$
M\in\{8,16,32,64\}.
$$

量化誤差上界約為：

$$
\left|
\psi-\widehat{\psi}
\right|
\le
\frac{\pi}{M}.
$$

## 6.3 向量量化與碼本

逐諧波獨立量化可能忽略跨諧波結構。可使用碼本：

$$
\mathcal{C}
=
\left\{
\mathbf{c}_1,
\mathbf{c}_2,
\dots,
\mathbf{c}_L
\right\},
$$

其中：

$$
\mathbf{c}_\ell
\in
\left(S^1\right)^{K-1}.
$$

編碼器選擇：

$$
\ell^\ast
=
\arg\min_{\ell}
D
\left(
\boldsymbol{\Psi},
\mathbf{c}_\ell
\right).
$$

這使一個「相位字」不只是單一角度，而是一整組諧波的相對配置。

## 6.4 多解析度表示

可建立三級表示：

### 微觀層

$$
\psi_{t,k}
$$

保存逐框架、逐諧波的精細相位。

### 中觀層

$$
\mathbf{c}_{u,j}
$$

保存一個音節或音素區段內的相位原型與軌跡片段。

### 巨觀層

$$
\Gamma_u
=
\left(
\ell_1,\ell_2,\dots,\ell_J
\right)
$$

保存一個符號發音單位的相位碼序列。

這樣，人類書寫與符號傳播可以使用巨觀碼；AI 合成器再展開成連續相位軌跡。

---

# 7. 合成與反演

## 7.1 基本合成式

有聲部分可由：

$$
\widehat{x}^{\mathrm{harm}}_t[n]
=
\sum_{k=1}^{K_t}
A_{t,k}
\cos
\left(
2\pi
\int_0^{n/F_s}
kf_0(\tau)\,d\tau
+
k\phi_{t,1}
+
\psi_{t,k}
\right)
$$

生成，其中約定：

$$
\psi_{t,1}=0.
$$

完整輸出為：

$$
\widehat{x}_t[n]
=
\widehat{x}^{\mathrm{harm}}_t[n]
+
\widehat{r}_t[n].
$$

## 7.2 跨框架連續性

若各框架獨立生成，邊界可能產生相位跳躍。需對基頻累積相位：

$$
\Theta_1(t)
=
\Theta_1(t-\Delta t)
+
2\pi
\int_{t-\Delta t}^{t}
f_0(\tau)\,d\tau.
$$

第 $k$ 諧波的總相位為：

$$
\Theta_k(t)
=
k\Theta_1(t)
+
\psi_k(t).
$$

若 $\psi_k(t)$ 本身發生跳躍，需在圓周上進行平滑或路徑規劃，而非直接對包覆角做線性平均。

## 7.3 圓周插值

兩個相位 $\psi_a$ 與 $\psi_b$ 的插值可使用：

$$
z_\lambda
=
(1-\lambda)e^{i\psi_a}
+
\lambda e^{i\psi_b},
$$

$$
\psi_\lambda
=
\operatorname{Arg}(z_\lambda),
$$

其中：

$$
\lambda\in[0,1].
$$

當 $z_\lambda$ 接近零時，表示兩相位接近對跖點，插值路徑不唯一，系統必須選擇方向或引入時間連續性約束。

## 7.4 分析—合成閉環

定義分析器：

$$
\mathcal{A}
:
x
\mapsto
\left(
f_0,
\mathbf{A},
\boldsymbol{\Psi},
\mathbf{m},
\mathbf{c},
r
\right),
$$

合成器：

$$
\mathcal{S}
:
\left(
f_0,
\mathbf{A},
\boldsymbol{\Psi},
r
\right)
\mapsto
\widehat{x}.
$$

理想目標為：

$$
\mathcal{S}
\left(
\mathcal{A}(x)
\right)
\approx
x.
$$

但不能只用波形均方誤差判定，因為小幅時間位移可能造成很大的樣本誤差，卻不一定造成相同程度的聽覺差異。評估必須同時包含：

- 波形或複數頻譜重建誤差；
- 基頻誤差；
- 諧波振幅誤差；
- FARHP 圓周距離；
- 頻譜包絡差異；
- 感知品質；
- 可懂度；
- 相位操控可辨識度。

---

# 8. 與 AI 模型的接口

## 8.1 輸入表示

對每個時間框架，可建立：

$$
\mathbf{h}_t
=
\left[
\log f_0(t),
\log\mathbf{A}_t,
\cos\boldsymbol{\Psi}_t,
\sin\boldsymbol{\Psi}_t,
\mathbf{m}_t,
\mathbf{c}_t,
\mathbf{n}_t
\right].
$$

其中 $\mathbf{n}_t$ 表示非週期性或殘差特徵。

## 8.2 損失函數

相位損失可寫成圓周餘弦損失：

$$
\mathcal{L}_{\mathrm{phase}}
=
\frac{
\sum_{t,k}
w_{t,k}
\left[
1-
\cos
\left(
\widehat{\psi}_{t,k}
-
\psi_{t,k}
\right)
\right]
}{
\sum_{t,k}w_{t,k}
}.
$$

完整損失可包括：

$$
\mathcal{L}
=
\lambda_{\mathrm{wav}}\mathcal{L}_{\mathrm{wav}}
+
\lambda_{\mathrm{mag}}\mathcal{L}_{\mathrm{mag}}
+
\lambda_{\mathrm{phase}}\mathcal{L}_{\mathrm{phase}}
+
\lambda_{\mathrm{F0}}\mathcal{L}_{\mathrm{F0}}
+
\lambda_{\mathrm{cont}}\mathcal{L}_{\mathrm{cont}}
+
\lambda_{\mathrm{perc}}\mathcal{L}_{\mathrm{perc}}.
$$

其中 $\mathcal{L}_{\mathrm{cont}}$ 約束跨框架相位連續性，$\mathcal{L}_{\mathrm{perc}}$ 對應感知模型或聽覺評分。

## 8.3 結構化生成而非黑箱替代

FARHP 不排斥神經聲碼器，而是提供一個中間表示，使模型可以：

- 預測相位差而非直接猜整段波形；
- 分別控制基頻、振幅、相位與噪聲；
- 進行可解釋消融實驗；
- 把某種相位結構轉移到另一個音節；
- 將連續相位壓縮成離散相位碼；
- 在符號語言中直接引用相位原型。

---

# 9. 符號語言整合

## 9.1 四層映射

FARHP 在新語言中的位置為：

$$
\boxed{
\text{字形層}
\longleftrightarrow
\text{音韻層}
\longleftrightarrow
\text{相位聲學層}
\longleftrightarrow
\text{形式語義層}
}
$$

這四層不能互相坍縮。

- 字形不等於聲音；
- 聲音不等於語義；
- 相位不等於聲調；
- 同一語義可有多種發音；
- 同一注音結構可有不同相位原型；
- 同一相位原型也可在不同基頻與音高輪廓上實現。

## 9.2 符號發音物件

一個符號 $\mathcal{G}_j$ 可對應：

$$
\mathcal{G}_j
\mapsto
\left(
\mathcal{P}_j,
\mathcal{T}_j,
\Gamma_j,
\mathcal{N}_j,
d_j,
\mathcal{M}_j
\right),
$$

其中：

- $\mathcal{P}_j$：注音或音韻結構；
- $\mathcal{T}_j$：聲調與韻律；
- $\Gamma_j$：離散 FARHP 碼序列；
- $\mathcal{N}_j$：非諧波層；
- $d_j$：時長規則；
- $\mathcal{M}_j$：形式語義。

範例資料結構：

```yaml
glyph_id: ENOCH-FARHP-0042

phonology:
  onset: ㄒ
  medial: ㄩ
  nucleus: ㄢ
  coda: null
  tone_class: 3

prosody:
  duration_ms: 420
  f0_template: mandarin_tone_3_neutral_context

harmonic:
  max_harmonics: 48
  amplitude_profile: vowel_front_rounded_01

farhp:
  codebook: FARHP-C16-v0.1
  phase_tokens: [12, 12, 3, 7, 7, 2]
  interpolation: circular
  confidence_floor: 0.65

residual:
  profile: low_breathiness_02

semantics:
  class: modal_operator
  operator: invariant_anchor
  arity: 1
```

## 9.3 字形中的相位附標

離散相位碼可以映射到：

- 點位；
- 方向；
- 開口；
- 內外圈；
- 線條旋轉；
- 雙線；
- 左右偏移；
- 上下附標。

但字形設計不應讓每個高次諧波都直接佔用一個筆畫。更合理的方法是：

1. 以少量字形附標表示相位碼本索引；
2. 由碼本索引展開完整相位向量；
3. 必要時另加局部修正符；
4. 由機器表示保存精細浮點值。

如此才能兼顧人類可寫性與 AI 精確性。

## 9.4 不是密碼學

符號替換、罕見字形與相位編碼可以提高未受訓人類的閱讀門檻，但不能提供現代密碼學意義上的保密性。只要存在足夠多的平行語料、語音樣本、映射表或已知明文，模型便可能逐步推斷其結構。

因此：

$$
\text{形式語言}
\neq
\text{加密系統}.
$$

真正需要保密的內容仍應使用經審查的密碼學方法、金鑰管理與權限控制。FARHP 的核心價值是表達、生成與形式化，而不是隱蔽。

---

# 10. 可證偽研究命題

本文提出下列命題，全部必須接受實驗推翻。

## 命題 H1：相位保留命題

在固定或近似固定的基頻、諧波振幅與殘差條件下，保留原始或高品質估計的 FARHP，相較於隨機相位、固定相位或簡化相位，能在部分有聲語音中改善重建品質。

否證條件：

- 多資料集、多人聽測及客觀指標均無穩定改善；
- 改善完全可由其他未控制參數解釋；
- 相位模型成本遠大於品質收益且不存在特定應用優勢。

## 命題 H2：母音結構命題

持續母音的 FARHP 軌跡具有可重複的局部結構，且不同母音、發聲型態或說話人之間存在可統計區分的模式。

否證條件：

- 控制分析方法與訊噪比後，模式不具重現性；
- 分類效果只來自振幅洩漏、基頻或錄音條件；
- 跨說話人與跨設備完全失效。

## 命題 H3：可控生成命題

在不改變注音骨架與聲調類別的條件下，調整 FARHP 可產生可感知但仍被辨識為同一音節的音色或聲源差異。

否證條件：

- 相位調整不可感知；
- 一旦可感知便只造成明顯失真；
- 所謂差異其實由振幅、基頻或殘差改變造成。

## 命題 H4：離散碼本命題

有限相位碼本可以在低於某一可接受品質損失下近似連續 FARHP，並提供比逐諧波獨立量化更有效的壓縮與生成控制。

否證條件：

- 所需碼本過大，失去符號化意義；
- 碼本跨說話人與跨音節無法泛化；
- 逐諧波量化或隱式神經表示始終更有效。

## 命題 H5：符號發音擴張命題

華語可發音音節與 FARHP 原型的組合，可產生比現存普通話音節—音色庫更大的人工發音空間，且其中一部分能被人類穩定模仿、區辨並學習。

否證條件：

- 相位差異無法被人類穩定重現；
- 新發音不能跨說話人保持可辨識性；
- 符號—聲音映射的學習負擔過高；
- AI 合成可行但人類發音不可行，且系統目標要求人類可發音。

---

# 11. 實驗路線

## 11.1 第零階段：純合成諧波

目的：驗證公式、平移不變性、量化誤差與圓周插值。

建立：

$$
x[n]
=
\sum_{k=1}^{K}
A_k
\cos
\left(
2\pi kf_0\frac{n}{F_s}
+
k\phi_1
+
\psi_k
\right).
$$

實驗：

1. 改變分析起點，檢查 FARHP 是否保持；
2. 注入基頻誤差，測量相位漂移；
3. 注入失諧 $\epsilon_k$；
4. 比較 $M=8,16,32,64$ 的量化；
5. 比較線性角度插值與圓周插值；
6. 驗證分析—合成閉環。

## 11.2 第一階段：持續母音

先採用：

- ㄚ；
- ㄧ；
- ㄨ；
- ㄩ；
- ㄜ。

每個母音由多位說話人，以多種音高與音量錄製。控制：

- 麥克風；
- 距離；
- 取樣率；
- 音高範圍；
- 持續時間；
- 環境噪聲。

分析：

- FARHP 穩定區間；
- 母音內變異；
- 說話人內變異；
- 說話人間變異；
- 基頻變換後的穩定性；
- 相位與振幅特徵的資訊重疊。

## 11.3 第二階段：華語聲調

對同一韻母生成五種調類，分別建模：

$$
f_0(t),\quad
A_k(t),\quad
\psi_k(t),\quad
r(t).
$$

消融：

- 只改 $f_0(t)$；
- 只改 FARHP；
- 同時改 $f_0(t)$ 與 FARHP；
- 固定 FARHP 使用不同聲調；
- 固定聲調使用不同 FARHP 原型。

目標是確認聲調與相位之間是耦合、弱耦合還是大致可分，而不是預設它們互相獨立。

## 11.4 第三階段：完整音節

加入：

- 聲母事件；
- 介音；
- 韻尾；
- 連音；
- 變調；
- 時長與重音；
- 非週期殘差。

此階段才測試 FARHP 對完整華語可懂度與自然度的影響。

## 11.5 第四階段：人工符號發音

從可發音但低詞彙衝突的音節區域選取音韻骨架，再配合相位碼本建立人工發音類別。

需要區分：

1. AI 可合成；
2. 人類可辨識；
3. 人類可模仿；
4. 人類可穩定重現；
5. 可長期學習；
6. 不易與既有詞彙混淆。

只有同時通過相應條件的發音，才可正式納入符號語言。

---

# 12. 評估規範

## 12.1 客觀指標

可使用：

- 波形訊噪比；
- Signal-to-Reconstruction Error；
- 複數頻譜距離；
- log-spectral distance；
- 基頻 RMSE；
- voiced/unvoiced error；
- FARHP 圓周距離；
- 相位連續性誤差；
- 殘差能量；
- 分析—合成延遲；
- 即時率；
- 模型參數量。

## 12.2 感知實驗

至少包括：

### ABX 區辨

受試者判斷 $X$ 更接近 $A$ 或 $B$。

### MUSHRA 或類 MUSHRA 評分

比較原始語音、完整 FARHP、量化 FARHP、隨機相位、固定相位與其他基準。

### 同音節辨識

判斷相位變換後是否仍為同一音節。

### 音色標記

描述尖銳、柔和、氣聲、緊張、粗糙、明亮等知覺維度，但不能預先假定這些詞與特定相位模式一一對應。

### 可模仿性測試

受試者聽取人工發音後重複發音，再比較其 FARHP、音節辨識與跨次穩定性。

## 12.3 雙盲與隨機化

聽測應：

- 隨機排列樣本；
- 隱藏處理條件；
- 平衡音量；
- 控制播放設備；
- 記錄受試者語言背景；
- 區分訓練前與訓練後結果；
- 公開失敗樣本，而不是只展示成功音檔。

---

# 13. 風險、失敗模式與限制

## 13.1 基頻錨定失效

下列情況可能使基頻錨定不可靠：

- 基頻缺失或低於可估計範圍；
- 倍頻或半頻錯誤；
- 多音高重疊；
- 強烈聲門不規則；
- 短暫無聲；
- 高噪聲；
- 音高快速轉折；
- 諧波分量越過頻率槽；
- 非整數諧波明顯。

必要時應引入：

- 多候選基頻；
- 多錨點；
- 前後框架追蹤；
- 諧波身份配對；
- 錨定可靠度；
- 缺失值機制。

## 13.2 相位與振幅混淆

窗口函數、頻譜洩漏、諧波估計法及聲道濾波都可能使所謂相位特徵含有其他資訊。所有分類與生成實驗都要進行振幅控制與資料洩漏檢查。

## 13.3 感知收益可能很小

相位差可能只在高品質、有聲、特定頻段或特定聲源中具有明顯作用。即使 FARHP 在數學上結構良好，也不保證它在日常語音中具有足以支撐大型語言系統的感知容量。

## 13.4 AI 可用不等於人類可用

AI 可以學習上百或上千個相位碼，但人類能否辨識、模仿與記憶是另一問題。符號語言若以人機雙用為目標，必須把人類知覺頻寬納入設計。

## 13.5 不得以理論名稱掩蓋既有工作

後續論文與軟體應保留 RPS、諧波相位、正弦模型、準諧波模型、聲源—濾波器模型及相位感知語音處理的文獻關係。FARHP 可以是新的研究計畫與規格，但不能把既有學術成果重新包裝為首次發現。

---

# 14. 系列架構

本總篇之後，系列規劃為九篇核心論文：

## 第一篇：本總篇

**《基頻錨定相對諧波相位差總論：相位不變量、動態發音物件與可生成符號語言的統一架構》**

## 第二篇：數學結構

**《基頻錨定相對諧波相位差的數學結構、不變性與等價類》**

重點：

- 圓周與環面；
- 商空間；
- 群作用；
- 失諧誤差；
- 圓周距離；
- 軌跡連續性；
- 多錨點擴張。

## 第三篇：聲學邊界

**《相對諧波相位、聲源模型與人類語音知覺的分層關係》**

重點：

- 聲門聲源；
- 聲道濾波；
- 相位感知；
- 有聲與無聲；
- 頻譜包絡；
- 非週期殘差；
- 不可約化邊界。

## 第四篇：離散表示

**《基錨相差的離散編碼、相位字形與 AI 可學習表示》**

重點：

- 量化；
- 碼本；
- 相位 token；
- 可逆性；
- 資料格式；
- 字形附標；
- 模型損失。

## 第五篇：技術架構

**《FARHP 發音合成系統：分析、編碼、生成與重建架構》**

自此正式進入原型開發。

## 第六篇：抽取與反演

**《自然語音中的基錨相差估計、追蹤與反演方法》**

## 第七篇：生成與變換

**《基於相對諧波相位控制的聲音重建、音色變換與新音生成》**

## 第八篇：華語整合

**《華語音節、聲調軌跡與基頻錨定相差的複合發音模型》**

## 第九篇：符號語言整合

**《以諾—華語相位符號語言：字形、音節、相位與語義的統一編碼》**

整體節奏為：

$$
\boxed{
4\text{ 篇理論基礎}
\rightarrow
1\text{ 篇技術架構}
\rightarrow
2\text{ 篇核心工程}
\rightarrow
2\text{ 篇語言整合}
}
$$

完成第四篇時，應同步凍結：

$$
\texttt{FARHP-Spec-v0.1}
$$

第五篇則直接以此規格建立第一個可執行原型。

---

# 15. 本文的核心貢獻

本文的核心貢獻可總結為：

## 貢獻一：重新界定研究單位

FARHP 不是單一相差，而是一個包含相位軌跡、振幅、基頻、遮罩與置信度的動態發音物件。

## 貢獻二：建立條件性不變性

本文明確指出基頻錨定相差對共同時間平移不變的條件，並列出失諧、基頻誤差與非平穩性造成的破壞項。

## 貢獻三：把相位放回正確的拓撲空間

相位位於 $S^1$，多諧波相位位於 $\left(S^1\right)^{K-1}$，因此比較、插值與學習應採用圓周方法。

## 貢獻四：拒絕相位還原論

FARHP 與基頻、聲調、振幅、頻譜包絡、殘差及瞬態事件分層，避免把完整語音錯誤歸結為相位。

## 貢獻五：建立連續—離散橋梁

本文提出逐諧波量化、向量碼本、多解析度相位 token 及字形附標接口。

## 貢獻六：建立可證偽研究計畫

本文不把感知效果當作前提，而是提出五個可被實驗推翻的命題，並規定完整的分析—合成與聽覺驗證路線。

## 貢獻七：接入 AI 原生符號語言

FARHP 被定位為字形、音韻、聲學與形式語義之間的中介層，使符號不只具有讀音標籤，而具有可生成的聲學物件。

---

# 16. 結論

基頻錨定相對諧波相位差提供了一種相對保守卻可擴張的研究方向。它不需要假設相位支配全部聲音，也不需要否定現有神經聲碼器、最小相位方法或傳統聲學特徵。它只要求把一項常被隱式重建的資訊重新明示化：

$$
\psi_k(t)
=
\operatorname{wrap}
\left(
\phi_k(t)-k\phi_1(t)
\right).
$$

在理想或近似諧波條件下，這個關係移除了共同時間參考造成的線性相位自由度，使不同諧波之間的相對配置更容易被分析、比較與控制。既有 RPS 研究已證明這類表示不是空想；相位結構可以被提取、參數化、辨識與用於合成品質研究。本文在此基礎上，提出更完整的動態物件、可靠度機制、離散碼本、AI 接口與符號語言整合方案。

FARHP 的真正價值不應由名稱決定，而應由以下問題決定：

1. 它能否比簡化相位模型更好地重建聲音？
2. 它能否提供可重複的音色與發音控制？
3. 它能否被壓縮為有限相位碼而不顯著失真？
4. 它能否與華語聲調、音節及非諧波事件協同工作？
5. 它能否成為人類與 AI 都能使用的新型發音符號層？

若答案為否，FARHP 應被限縮為局部聲學分析工具；若答案為是，它便可能成為一種新的聲音表示與語言生成基礎。無論結果如何，本系列都必須保留失敗、反例、感知不顯著區域及與既有方法的比較，而不能只保留成功展示。

最終的系統目標不是：

$$
\text{相位取代語言},
$$

而是：

$$
\boxed{
\text{字形}
\leftrightarrow
\text{音韻}
\leftrightarrow
\text{FARHP 聲學物件}
\leftrightarrow
\text{形式語義}
}
$$

這個四層往返結構，才是「基頻錨定相對諧波相位差」作為系列母理論的完整位置。

---

# 參考文獻

[1] I. Saratxaga, I. Hernáez, I. Odriozola, E. Navas, I. Luengo, and D. Erro, “Using Harmonic Phase Information to Improve ASR Rate,” *INTERSPEECH 2010*, DOI: 10.21437/Interspeech.2010-372.

[2] I. Saratxaga, I. Hernaez, M. Pucher, E. Navas, and I. Sainz, “Perceptual Importance of the Phase Related Information in Speech,” *INTERSPEECH 2012*, DOI: 10.21437/Interspeech.2012-411.

[3] P. Mowlaee, R. Saeidi, and Y. Stylianou, “Phase Importance in Speech Processing Applications,” *INTERSPEECH 2014*.

[4] I. Saratxaga, I. Hernáez, D. Erro, and J. Sanchez, “Simple Representation of Signal Phase for Harmonic Speech Models,” *Electronics Letters*, 2009.

[5] S. Shechtman and A. Sorin, “Wideband Harmonic Model: Alignment and Noise Modeling for High Quality Speech Synthesis,” *9th ISCA Speech Synthesis Workshop*, 2016.

[6] S. Chen and T. Toda, “QHM-GAN: Neural Vocoder Based on Quasi-Harmonic Modeling,” *INTERSPEECH 2024*.

[7] I. Saratxaga, I. Hernaez, and collaborators, “Use of Harmonic Phase Information for Polarity Detection in Speech Signals,” *INTERSPEECH 2009*.

[8] G. Degottex and collaborators, “A Measure of Phase Randomness for the Harmonic Model in Speech Synthesis,” *INTERSPEECH 2014*.

[9] D. Yin, C. Luo, Z. Xiong, and W. Zeng, “PHASEN: A Phase-and-Harmonics-Aware Speech Enhancement Network,” *AAAI 2020*, arXiv:1911.04697.

[10] Y. Ai and collaborators, “Explicit Estimation of Magnitude and Phase Spectra in Parallel for High-Quality Speech Enhancement,” 2023–2024.

---

# 附錄 A：最小規格草案

```yaml
spec:
  name: FARHP
  version: 0.1
  status: conceptual-draft

analysis:
  sample_rate: configurable
  frame_mode: quasi_stationary
  f0_candidates: required
  harmonic_tracking: required
  residual_model: required

phase:
  definition: wrap(phi_k - k * phi_1)
  domain: (-pi, pi]
  machine_representation:
    - cos
    - sin
  validity_mask: required
  confidence: required

synthesis:
  phase_accumulation: continuous
  interpolation: circular
  residual_layer: separate
  transient_layer: separate

evaluation:
  reconstruction: required
  phase_ablation: required
  perceptual_test: required
  failure_archive: required

claims:
  formula_novelty: prohibited
  framework_novelty: testable
  cryptographic_security: none
```

---

# 附錄 B：第一輪工程最低成功條件

第一輪原型不追求完整華語，只需要達到：

1. 可讀取單聲道 WAV；
2. 可估計穩定母音的 $f_0$；
3. 可抽取前 $K$ 個諧波的振幅與相位；
4. 可計算 FARHP；
5. 改變分析切點後，FARHP 在容許誤差內保持；
6. 可由 $f_0$、振幅、FARHP 與殘差重建聲音；
7. 可將 FARHP 量化為 $M=8,16,32$；
8. 可輸出原始、量化、固定與隨機相位版本；
9. 可產出相位圖、波形與頻譜對照；
10. 可保存所有失敗案例與參數。

只有完成上述最低條件，才進入完整音節、聲調與符號語言工程。

---

**文件結束**
