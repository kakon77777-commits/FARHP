# 相對諧波相位、聲源模型與人類語音知覺的分層關係
## FARHP 的聲學可識別性、音類適用域、知覺效應與工程邊界

**英文題名：** *Relative Harmonic Phase, Source–Filter Models, and Human Speech Perception: Acoustic Identifiability, Phonetic Applicability, Perceptual Effects, and Engineering Boundaries of FARHP*  

**縮寫：** FARHP  
**中文簡稱：** 基錨相差  
**系列位置：** FARHP 系列第三篇／聲學與語音學邊界篇  
**作者：** Neo.K（EveMissLab）  
**AI 協作：** Aletheia（GPT-5.6 Thinking）  
**版本：** v0.1  
**日期：** 2026-07-25  
**文件性質：** 理論論文／聲學邊界論文／實驗規格前置篇

---

## 摘要

本文建立「基頻錨定相對諧波相位差」（Fundamental-Anchored Relative Harmonic Phase, FARHP）在語音聲學、聲源—聲道模型與人類聽覺知覺中的分層位置。系列前兩篇已分別提出 FARHP 的總體架構，並證明固定 $K$ 個諧波時，其自然狀態空間可表示為完整相位環面對共同週期平移群作用取商所得的 $(K-1)$ 維相位環面。本文進一步回答一個不能由純數學直接解決的問題：麥克風量測到的 FARHP 究竟來自哪裡，又能被人耳如何利用？

本文首先在複數頻域聲源—聲道模型下推導「觀測 FARHP 分解式」。若觀測語音的第 $k$ 個諧波由聲門源、聲道傳遞、唇端輻射與量測鏈共同形成，則觀測到的 FARHP 並不等於純聲門源的相對相位，而是多個子系統之相對相位貢獻的模 $2\pi$ 合成：

$$
\psi^{(y)}_k
=
\psi^{(g)}_k
+
\Delta_k\theta_v
+
\Delta_k\theta_r
+
\Delta_k\theta_m
\pmod{2\pi},
$$

其中：

$$
\Delta_k\theta_q
:=
\theta_q(k\omega_0)-k\theta_q(\omega_0).
$$

此結果顯示，FARHP 是「輸出波形週期內部形狀」的可觀測不變量，但在沒有額外假設或逆濾波的情況下，不能被直接歸因為聲門相位。本文據此提出 FARHP 的可識別性層級、聲源歸因條件及相位控制與生理控制之間的界線。

其次，本文分析 FARHP 對波形峰值聚集、週期內脈衝位置、峰均比、局部包絡起伏、極性相關形狀及聲碼器自然度的潛在控制力，同時明確指出：FARHP 不能單獨決定基頻、聲調、共振峰、音素身分、噪聲比例、音量或完整聲質。相位效應在人類知覺中具有高度條件性，會受到基頻、諧波是否在耳蝸中被解析、聲壓級、分析窗、頻譜包絡與任務類型影響。既有研究顯示，自然相位在特定聲碼器語音中可改善品質，相位改變也可影響低階諧波的內部表徵與諧波複合聲的遮蔽效果；但這些效應並不等同於相位可獨立承載語音類別。

本文最後建立音類適用矩陣：穩定有聲母音為 FARHP 的首要實驗域；近音、鼻音與有聲擦音屬條件性適用；無聲擦音、爆破瞬態及送氣段則需要噪聲、瞬態與非諧波模型共同描述。對華語而言，聲調應由 $f_0$ 軌跡、時長與強度等巨觀參數建模，FARHP 僅作為週期內部微觀波形層。本文提出六項可證偽命題、五級適用門控、十二項工程限制及第四篇離散表示所需的聲學規格，從而為後續相位碼本、抽取器、合成器與華語符號語言建立可操作而不還原論的聲學底座。

**關鍵詞：** 相對諧波相位、聲源—聲道模型、聲門源、語音知覺、聲質、諧波模型、相位失真、華語聲調、可識別性、分析—合成

---

# 0. 研究定位

## 0.1 本文的核心問題

FARHP 的數學定義相對簡潔：

$$
\psi_k(t)
=
\operatorname{wrap}
\left(
\phi_k(t)-k\phi_1(t)
\right).
$$

但一個數學上良定義的量，不必然具有單一的生理來源，也不必然對人耳具有同樣的重要性。本文要處理的不是「FARHP 是否存在」，而是以下四個問題：

1. 麥克風量到的 FARHP 由哪些物理子系統共同形成？
2. 哪些相位差可被解釋為聲門源特徵，哪些只能被解釋為輸出波形特徵？
3. FARHP 能控制哪些聲學屬性，又不能取代哪些傳統參數？
4. 哪些語音音類適合使用 FARHP，哪些必須交由殘差、噪聲或瞬態層處理？

## 0.2 本文拒絕的三種簡化

### 簡化一：觀測相位等於聲門相位

錄音訊號已經通過聲道、唇端輻射、空間傳播、麥克風與前端濾波。除非已知或逆轉這些系統，否則不能將輸出相位全部歸因於聲門。

### 簡化二：相位等於聲質

氣聲、緊聲、壓迫聲、沙啞聲或說話人個性，通常同時涉及諧波振幅斜率、開放商、閉合速度、非週期噪聲、次諧波、抖動、閃爍、聲道共振及時間變化。FARHP 可以描述其中一部分週期內部形狀，但不是完整聲質的同義詞。

### 簡化三：可聽差異等於語言差異

兩個聲音可被聽出不同，不代表它們會被辨識為不同音素、不同聲調或不同語義單位。本文因此區分：

$$
\text{可檢出}
\neq
\text{可區辨}
\neq
\text{可分類}
\neq
\text{具語言功能}.
$$

## 0.3 核心立場

本文的核心立場是：

> FARHP 首先是週期性輸出聲波內部形狀的相對相位描述；它是否能被進一步歸因為聲門源、聲道、說話人或語言對立，必須由模型假設與實驗證據逐層判定。

---

# 1. 語音生成的複數聲源—聲道模型

## 1.1 時域表示

在最基本的線性近似下，語音可寫為：

$$
y(t)
=
\left(
 g*v*r*m
\right)(t)
+n(t)+\tau(t),
$$

其中：

- $g(t)$：聲門激勵或聲門流導數相關訊號；
- $v(t)$：聲道傳遞系統；
- $r(t)$：唇端輻射與空間傳播；
- $m(t)$：麥克風、前級與數位前端量測鏈；
- $n(t)$：隨機、湍流或非週期殘差；
- $\tau(t)$：爆破、閉鎖解除與其他瞬態事件。

此模型只是局部線性近似。真實發聲存在聲源—聲道耦合、時變聲道、非線性聲帶振動及氣流湍流，因此不能將它當作完整生理本體。但對短時諧波分析而言，它提供了必要的第一層分解。

## 1.2 頻域表示

對短時準平穩區段，複數頻譜可寫為：

$$
Y(\omega)
=
G(\omega)V(\omega)R(\omega)M(\omega)
+
N(\omega)+T(\omega).
$$

在穩定有聲區段，若暫時忽略 $N$ 與 $T$，並在諧波頻率：

$$
\omega_k=k\omega_0
$$

取樣，則：

$$
Y_k
=
G_kV_kR_kM_k.
$$

令：

$$
G_k=A^{(g)}_ke^{i\phi^{(g)}_k},
$$

$$
V_k=A^{(v)}_ke^{i\theta^{(v)}_k},
$$

$$
R_k=A^{(r)}_ke^{i\theta^{(r)}_k},
$$

$$
M_k=A^{(m)}_ke^{i\theta^{(m)}_k}.
$$

則：

$$
A^{(y)}_k
=
A^{(g)}_kA^{(v)}_kA^{(r)}_kA^{(m)}_k,
$$

且：

$$
\phi^{(y)}_k
=
\phi^{(g)}_k
+
\theta^{(v)}_k
+
\theta^{(r)}_k
+
\theta^{(m)}_k
\pmod{2\pi}.
$$

振幅在乘法系統中相乘，相位則在圓群上相加。

## 1.3 觀測 FARHP 分解定理

對任一子系統 $q\in\{g,v,r,m\}$，定義其基頻錨定相位貢獻：

$$
\Delta_k\theta_q
:=
\operatorname{wrap}
\left(
\theta_q(k\omega_0)
-k\theta_q(\omega_0)
\right).
$$

聲門源的 FARHP 為：

$$
\psi^{(g)}_k
:=
\operatorname{wrap}
\left(
\phi^{(g)}_k-k\phi^{(g)}_1
\right).
$$

觀測輸出的 FARHP 為：

$$
\psi^{(y)}_k
:=
\operatorname{wrap}
\left(
\phi^{(y)}_k-k\phi^{(y)}_1
\right).
$$

代入複數乘法關係可得：

$$
\boxed{
\psi^{(y)}_k
=
\operatorname{wrap}
\left(
\psi^{(g)}_k
+
\Delta_k\theta_v
+
\Delta_k\theta_r
+
\Delta_k\theta_m
\right)
}
$$

本文稱之為**觀測 FARHP 分解式**。

它表示：麥克風中的相對諧波相位，是聲門週期形狀與所有後續線性系統之「非純延遲相位」共同作用的結果。

## 1.4 純延遲為何被 FARHP 消去

若某個子系統只有固定時間延遲 $\tau_q$，則：

$$
\theta_q(\omega)
=
-\omega\tau_q.
$$

因此：

$$
\begin{aligned}
\Delta_k\theta_q
&=
-k\omega_0\tau_q
-k(-\omega_0\tau_q)
\\
&=0.
\end{aligned}
$$

所以固定傳播延遲、錄音切點平移及共同時鐘偏移不會改變 FARHP。只有偏離純線性相位的頻率依賴性，才會留下相對相位貢獻。

這使 FARHP 成為一種「移除共同延遲、保留週期內部形狀」的表示。

## 1.5 聲道相位並不必然消失

若聲道傳遞函數具有共振、反共振或全通成分，其相位一般不是純線性函數：

$$
\theta_v(\omega)
\neq
-a\omega+b.
$$

因此：

$$
\Delta_k\theta_v
\neq 0
$$

通常成立。尤其當諧波穿越共振峰、反共振或急遽群延遲區域時，聲道可對輸出 FARHP 產生明顯貢獻。

所以：

$$
\boxed{
\text{觀測 FARHP}
\neq
\text{純聲門 FARHP}
}
$$

除非使用逆濾波、已知合成聲道或其他約束完成來源分解。

---

# 2. 最小相位、全通相位與可識別性

## 2.1 振幅不能唯一決定一般相位

對一般穩定系統，已知振幅響應：

$$
|H(\omega)|
$$

並不足以唯一恢復所有相位。若系統被限制為最小相位，則其相位可在適當條件下由對數振幅的 Hilbert 轉換關係導出；但任何全通因子：

$$
H_{\mathrm{ap}}(\omega)
$$

都可在不改變振幅的情況下改變相位：

$$
|H_{\mathrm{ap}}(\omega)|=1.
$$

因此可寫：

$$
H(\omega)
=
H_{\min}(\omega)H_{\mathrm{ap}}(\omega)e^{-i\omega\tau}.
$$

FARHP 會消去純延遲 $e^{-i\omega\tau}$，但不會消去一般全通相位。

## 2.2 輸出分解的不唯一性

若：

$$
Y(\omega)=G(\omega)V(\omega),
$$

對任意非零複數函數 $A(\omega)$，皆可重寫為：

$$
Y(\omega)
=
\left[G(\omega)A(\omega)\right]
\left[V(\omega)A^{-1}(\omega)\right].
$$

因此，若沒有生理模型、因果性、穩定性、最小相位、頻帶平滑性或其他先驗限制，聲門源與聲道的複數分解並不唯一。

本文稱此結果為**相位歸因非唯一性原則**：

> FARHP 作為輸出波形特徵可以被穩定觀測，但其內部各來源的分配不能僅由單通道輸出唯一決定。

## 2.3 三種可識別性

本文區分三種不同層級：

### 層級 A：輸出可識別性

只要 $f_0$、諧波頻率與相位估計可靠，就可由錄音計算：

$$
\boldsymbol\Psi^{(y)}.
$$

這是最弱、也最容易滿足的可識別性。

### 層級 B：系統條件可識別性

若麥克風與前端響應已校正，或同一設備下保持不變，可以比較不同語音之間的相對變化：

$$
\Delta\boldsymbol\Psi^{(y)}.
$$

此時雖不能得到純聲門相位，卻可得到條件一致的輸出相位特徵。

### 層級 C：聲源可識別性

只有在以下條件之一成立時，才可近似估計：

$$
\boldsymbol\Psi^{(g)}.
$$

例如：

1. 使用已知聲道的合成資料；
2. 使用可靠的聲門逆濾波；
3. 同步量測電聲門圖或高速喉部影像；
4. 採用有明確參數限制的聲源—聲道模型；
5. 使用多感測器與物理先驗進行聯合反演。

## 2.4 FARHP 的保守命名原則

因此，工程資料欄位不應籠統命名為：

```text
voice_source_phase
```

除非確實完成聲源分解。一般錄音應命名為：

```text
observed_farhp
```

逆濾波後才可命名為：

```text
glottal_farhp_estimate
```

並附上：

```text
inverse_filter_method
confidence
assumptions
residual_error
```

---

# 3. FARHP 實際控制什麼

## 3.1 固定振幅時，相位改變波形時間結構

考慮固定振幅與頻率的諧波和：

$$
x(t)
=
\sum_{k=1}^{K}
A_k
\cos
\left(
 k\omega_0t+	heta_k
\right).
$$

當 $A_k$ 固定而 $\theta_k$ 改變時，長時間功率頻譜不變，但週期內部波形可以顯著改變。相位可以重新配置：

- 各諧波峰值在週期中的對齊程度；
- 瞬時峰值出現的位置；
- 波形上升與下降的局部陡峭程度；
- 峰值是否集中成類脈衝；
- 正負半週的時間不對稱；
- 通過聽覺濾波器後的包絡起伏。

## 3.2 峰均比與時間集中度

定義峰均比：

$$
\operatorname{CF}(x)
=
\frac{\max_t|x(t)|}
{\sqrt{\frac{1}{T_0}\int_0^{T_0}|x(t)|^2dt}}.
$$

在諧波振幅固定時，分母的週期平均能量不因相位改變；分子則可隨諧波對齊而變化。因此 FARHP 可以控制波形的峰值集中程度。

亦可定義週期內能量集中度：

$$
C_\delta(x)
=
\max_{t_0}
\frac{
\int_{t_0-\delta/2}^{t_0+\delta/2}|x(t)|^2dt
}{
\int_0^{T_0}|x(t)|^2dt
}.
$$

較高的 $C_\delta$ 表示能量集中在較短的週期窗口中。FARHP 可在振幅頻譜不變時改變此量。

## 3.3 脈衝形狀與聲門閉合相關線索

聲門閉合通常會在時域形成較尖銳的事件，並影響高頻能量與諧波相位結構。相位失真或相對相位描述可攜帶聲門脈衝形狀資訊，既有工作亦曾以相位失真統計描述聲門源及聲質。

但必須區分：

$$
\text{聲門閉合形狀}
\rightarrow
\left(
\text{振幅結構},
\text{相位結構}
\right),
$$

而不是：

$$
\text{聲門閉合形狀}
\equiv
\text{FARHP}.
$$

FARHP 只能捕捉其中的相位投影。

## 3.4 極性與奇偶結構

若波形極性反轉：

$$
x(t)\mapsto -x(t),
$$

則所有諧波相位增加 $\pi$。由第二篇結果，FARHP 變換為：

$$
\psi_k
\mapsto
\operatorname{wrap}
\left(
\psi_k+(1-k)\pi
\right).
$$

因此：

- 奇數 $k$ 的 FARHP 不變；
- 偶數 $k$ 的 FARHP 平移 $\pi$。

這說明偶次諧波相位帶有極性敏感資訊，也解釋為何相對諧波相位可用於語音極性偵測。

## 3.5 通過耳蝸濾波後的包絡

外部波形的長時間振幅頻譜相同，不代表耳內表徵相同。聽覺濾波器將鄰近諧波共同投影到一個頻帶後，諧波間相位會影響濾波器輸出的時間包絡：

$$
z_b(t)
=
(h_b*x)(t),
$$

其中 $h_b$ 是第 $b$ 個聽覺濾波器。其包絡：

$$
e_b(t)=|\mathcal A\{z_b(t)\}|
$$

會受頻帶內各諧波相位關係影響，其中 $\mathcal A$ 表示解析訊號運算。

所以相位效應常不是人耳直接「讀取傅立葉相位」，而是相位改變了耳蝸濾波後的局部時間結構。

---

# 4. FARHP 不能單獨控制什麼

## 4.1 基頻與音高

基頻由週期或準週期重複率決定：

$$
f_0=\frac{1}{T_0}.
$$

FARHP 定義在給定 $f_0$ 的諧波框架之上。改變 FARHP 而保持諧波頻率不變，不會直接改變名義基頻。

然而，極端相位變化可能透過時域包絡、倍頻線索或聽覺非線性影響音高顯著性。這是二階知覺效應，不等於 FARHP 本身就是音高。

## 4.2 華語聲調

華語聲調的主要聲學載體是跨時間的 $f_0$ 軌跡，並受時長、強度、音質、語境與協同發音影響。可寫為：

$$
\mathcal T_q(t)
=
\left(
 f_{0,q}(t),
 a_q(t),
 d_q,
 \eta_q(t)
\right).
$$

FARHP 描述的是每個局部週期內部的相對諧波相位：

$$
\boldsymbol\Psi_q(t).
$$

因此：

$$
\boxed{
\text{聲調軌跡}
\neq
\text{FARHP 軌跡}
}
$$

但兩者可以耦合。當 $f_0$ 快速下降、上升或發聲型態改變時，FARHP 也可能隨聲門動力學發生系統性變化。

## 4.3 共振峰與母音身分

母音身分主要依賴聲道頻譜包絡與共振峰結構，例如：

$$
F_1,F_2,F_3,\ldots
$$

在振幅包絡固定時改變相位，通常不會把一個具有明確 $F_1,F_2$ 的穩定母音，自動變成另一個具有不同共振峰位置的母音。

但相位可能影響自然度、清晰度、脈衝感或低階諧波的局部知覺表徵。因此應區分：

$$
\text{音類核心身分}
\quad\text{與}\quad
\text{同一音類內的波形品質}.
$$

## 4.4 音量與響度

若所有 $A_k$ 固定，相位不改變總週期能量：

$$
E
=
\frac{1}{2}
\sum_{k=1}^{K}A_k^2
$$

在正交整週期積分下保持不變。但峰值、短時包絡與耳蝸非線性可能使主觀響度或遮蔽效果出現條件性差異。

所以：

$$
\text{相同能量}
\not\Rightarrow
\text{完全相同知覺響度}.
$$

## 4.5 噪聲、送氣與非週期性

氣聲、摩擦音、送氣段與粗糙聲通常含有：

- 非諧波湍流；
- 隨機相位；
- 寬頻噪聲；
- 次諧波或多重週期；
- 週期間不規則變化。

單一 FARHP 向量不能完整表示這些成分。必須加入：

$$
\mathcal N(t,\omega),
$$

作為噪聲或相位隨機度模型，並另行處理次諧波與非整數諧波。

---

# 5. 人類語音知覺中的相位

## 5.1 四種不同的知覺任務

相位效果必須依任務區分：

### 任務 A：檢出

聽者能否察覺聲音發生改變？

### 任務 B：區辨

聽者能否穩定區分兩種相位配置？

### 任務 C：品質判斷

哪一種聲音較自然、清晰、柔和、尖銳或接近真人？

### 任務 D：語言辨識

相位差是否改變音素、聲調、詞彙或語句辨識？

不能從任務 A 的成功直接推論任務 D。

## 5.2 已解析與未解析諧波

當低階諧波在耳蝸濾波器中較容易分離時，各諧波可能形成較穩定的頻率線索；當較高階諧波在同一聽覺頻帶內混合時，其相對相位會更直接影響頻帶輸出的時間包絡。

因此相位敏感度不應被視為固定常數，而應寫成：

$$
S_{\phi}
=
S_{\phi}
\left(
 f_0,
 k,
 A_k,
 \mathcal B,
 L,
 \text{task}
\right),
$$

其中：

- $\mathcal B$：聽覺頻帶或頻譜區域；
- $L$：聲壓級；
- $\text{task}$：知覺任務。

## 5.3 基頻依賴性

傅立葉相位量化對母音知覺的重要性，已被發現會受到基頻與分析窗長影響。原因之一是：基頻改變會同時改變諧波間距、耳蝸內解析程度及每個頻帶所含的諧波數。

因此 FARHP 實驗不能只使用單一說話人或單一 $f_0$。至少應分成：

$$
f_0\in
\{80,120,180,240\}\ \mathrm{Hz}
$$

或依實際語料建立低、中、高三個區間。

## 5.4 自然相位與聲碼器品質

既有聲碼器研究指出，保留或恢復較自然的聲門激勵相位，可在某些合成條件下改善知覺品質。這支持 FARHP 作為合成控制參數的可能性，但不代表所有相位自由度都同樣重要。

更合理的假設是：

$$
\boldsymbol\Psi
=
\boldsymbol\Psi_{\mathrm{structured}}
+
\boldsymbol\Psi_{\mathrm{weak}}
+
\boldsymbol\Psi_{\mathrm{random}},
$$

其中只有部分低維結構與自然度、聲門脈衝或聲質穩定相關。

## 5.5 相位對遮蔽的條件效應

不同諧波相位關係會改變複合聲的時域包絡，進而影響其遮蔽能力。研究顯示，這種效應會隨 $f_0$、聲壓級及相位配置而改變；在某些中等聲級條件下效應很小，在其他條件下則較明顯。

這提醒 FARHP 工程不能以「相位一定明顯可聽」為前提，而應實際測量：

$$
\Delta_{\mathrm{percept}}
=
f(
\Delta\boldsymbol\Psi,
\mathbf A,
f_0,
L,
\text{listener}
).
$$

## 5.6 低階諧波相位與內部表徵

低階單一諧波的相位改變，在特定合成母音與單共振峰複合聲中，可能改變聽者對共振位置的匹配判斷。這表示相位可透過聽覺神經相位鎖定與頻帶內交互作用，間接影響頻譜形狀的內部表徵。

但其結論仍應保守解讀：

> 相位可以偏移人耳對某些頻譜特徵的感知，不代表相位取代了頻譜包絡。

---

# 6. FARHP 與聲質的分層關係

## 6.1 聲質不是單參數

可將局部聲質狀態寫為：

$$
\mathcal Q(t)
=
\left(
\mathbf A^{(g)}(t),
\boldsymbol\Psi^{(g)}(t),
\mathcal N(t),
J(t),
S(t),
\mathbf V(t)
\right),
$$

其中：

- $\mathbf A^{(g)}$：聲門源諧波振幅；
- $\boldsymbol\Psi^{(g)}$：聲門源 FARHP；
- $\mathcal N$：送氣與噪聲；
- $J$：週期抖動；
- $S$：振幅閃爍及非平穩性；
- $\mathbf V$：聲道狀態。

因此 FARHP 是聲質空間的一個子座標，而非完整空間。

## 6.2 氣聲—緊聲連續體

氣聲、模態聲與壓迫聲常與以下參數相關：

- 聲門開放商；
- 閉合速度；
- 第一與第二諧波振幅差；
- 高頻譜傾斜；
- 送氣噪聲；
- 聲門脈衝相位形狀。

FARHP 可捕捉閉合事件在週期內的相對形狀及諧波對齊，但如果不保留振幅與噪聲，通常無法單獨重建完整氣聲—緊聲差異。

因此合成控制應至少使用：

$$
\mathcal C_{\mathrm{voice}}
=
\left(
\mathbf A^{(g)},
\boldsymbol\Psi^{(g)},
\mathcal N
\right).
$$

## 6.3 相位失真統計

相位失真方法常以相位偏離線性相位或脈衝基準的程度描述聲門源。FARHP 與這類方法具有親緣性，但二者不完全相同：

- 相位失真可依特定脈衝時刻或全頻帶模型定義；
- FARHP 以基頻相位作為內部錨；
- FARHP 的核心是諧波間相對配置與共同時間平移不變性；
- 相位失真統計可進一步壓縮或建模 FARHP 的分布。

所以後續可定義：

$$
\operatorname{PDD}_{\mathrm{FARHP}}
=
\mathcal S
\left(
\boldsymbol\Psi-oldsymbol\mu_{\Psi}
\right),
$$

其中 $\mathcal S$ 是圓周統計摘要，而不是直接把相位差當作線性高斯變數。

## 6.4 說話人與個體差異

不同說話人的聲帶形態、聲門動力學與聲道長度可能形成不同的 FARHP 分布；但錄音設備、麥克風方向、房間脈衝響應與音素分布也會產生差異。

因此說話人辨識實驗必須比較：

$$
I(
\boldsymbol\Psi;
\text{speaker}
\mid
\text{phone},
\text{device},
 f_0,
\mathbf A
),
$$

而不能只觀察未控制條件下的分類準確率。

---

# 7. 不同音類的適用邊界

## 7.1 適用度的五級門控

本文定義 FARHP 音類適用度：

$$
\Gamma(t)
\in
\{0,1,2,3,4\}.
$$

### $\Gamma=4$：高適用

條件：

- 穩定有聲；
- $f_0$ 明確；
- 諧波可追蹤；
- 非週期能量低；
- 框架內近似平穩。

### $\Gamma=3$：條件適用

存在較強聲道變化、鼻化或混合激勵，但主要週期仍可追蹤。

### $\Gamma=2$：混合適用

有聲與噪聲並存，FARHP 只能描述週期子空間。

### $\Gamma=1$：弱適用

只有短暫或低信賴度週期，僅能作局部輔助特徵。

### $\Gamma=0$：不適用

無穩定基頻或不存在可辨識的整數諧波結構。

## 7.2 穩定母音

持續母音通常具有：

- 明確 $f_0$；
- 穩定諧波；
- 可控共振峰；
- 較長準平穩區段。

因此：

$$
\Gamma_{\mathrm{vowel}}
\approx 4.
$$

母音是 FARHP 的第一實驗域，但實驗中仍需分離聲源與聲道貢獻。

## 7.3 近音與滑音

如華語的介音及近音，通常保持有聲，但聲道形狀快速轉換。其特點是：

$$
\frac{d\mathbf V(t)}{dt}
$$

較大，導致聲道相位貢獻隨時間變化。

因此：

$$
\Gamma_{\mathrm{approximant}}
\approx 3.
$$

需要更短的分析窗與動態聲道模型。

## 7.4 鼻音與鼻化母音

鼻腔耦合可引入額外共振與反共振，使振幅與相位在特定頻帶急遽變化。FARHP 仍可計算，但聲道相位貢獻不再平滑。

因此：

$$
\Gamma_{\mathrm{nasal}}
\approx 3,
$$

並需保留反共振附近的低置信度標記。

## 7.5 有聲擦音

有聲擦音同時包含週期源與湍流噪聲：

$$
y(t)
=
y_{\mathrm{harm}}(t)+y_{\mathrm{noise}}(t).
$$

FARHP 只能描述：

$$
y_{\mathrm{harm}}(t).
$$

因此：

$$
\Gamma_{\mathrm{voiced\ fricative}}
\approx 2.
$$

## 7.6 無聲擦音

無聲擦音通常缺乏穩定 $f_0$，主要由湍流噪聲形成：

$$
\Gamma_{\mathrm{unvoiced\ fricative}}
\approx 0.
$$

此時應使用：

- 頻譜包絡；
- 噪聲相位統計；
- 時變功率；
- 隨機種子或生成式殘差模型。

## 7.7 塞音

塞音包含：

1. 閉鎖；
2. 爆破；
3. 送氣或聲帶起振；
4. 進入後續母音。

爆破瞬態本身不是穩定諧波物件。FARHP 可用於起振後的有聲段，但不能取代爆破事件模型。

可寫成：

$$
\Sigma_{\mathrm{stop}}
=
\left(
\mathcal E_{\mathrm{closure}},
\mathcal E_{\mathrm{burst}},
\mathcal N_{\mathrm{asp}},
\mathcal H_{\mathrm{voicing}}
\right).
$$

其中只有 $\mathcal H_{\mathrm{voicing}}$ 進入 FARHP。

## 7.8 塞擦音

塞擦音是瞬態與摩擦噪聲的混合：

$$
\Gamma_{\mathrm{affricate}}
\approx 0\text{--}2,
$$

取決於是否含有可追蹤的有聲部分。

## 7.9 喉塞、嘎裂與次諧波

若發聲出現倍週期、次諧波或多重基頻候選，單一 $f_0$ 錨可能失效。此時需要：

- 多週期模型；
- 次諧波索引；
- 廣義整數不變量；
- 非單一環面狀態空間。

不能強迫所有框架進入普通 FARHP。

---

# 8. 動態發音物件與門控模型

## 8.1 完整局部狀態

本文將局部語音狀態寫為：

$$
\mathcal X_t
=
\left(
 f_0(t),
\mathbf A(t),
\boldsymbol\Psi(t),
\mathbf V(t),
\mathcal N(t),
\mathcal E(t),
\mathbf c(t)
\right),
$$

其中：

- $\mathbf A(t)$：諧波振幅；
- $\boldsymbol\Psi(t)$：觀測或估計聲源 FARHP；
- $\mathbf V(t)$：頻譜包絡與聲道參數；
- $\mathcal N(t)$：噪聲與非週期殘差；
- $\mathcal E(t)$：瞬態事件；
- $\mathbf c(t)$：各參數信賴度。

## 8.2 FARHP 有效門

定義相位有效門：

$$
g_{\phi}(t,k)
=
\mathbb I
\left[
 c_{f_0}(t)>\tau_f
\land
 c_{h_k}(t)>\tau_h
\land
 \rho_{\mathrm{harm}}(t)>\tau_\rho
\right].
$$

其中：

- $c_{f_0}$：基頻信賴度；
- $c_{h_k}$：第 $k$ 諧波信賴度；
- $\rho_{\mathrm{harm}}$：諧波能量比例。

只有當：

$$
g_{\phi}(t,k)=1
$$

時，該相位座標才進入碼本訓練或損失函數。

## 8.3 軟門控

比二元遮罩更穩定的作法是使用：

$$
w_{\phi}(t,k)
=
 c_{f_0}(t)
 c_{h_k}(t)
 \rho_{\mathrm{harm}}(t)
 \chi_{\mathrm{stationary}}(t),
$$

其中：

$$
w_{\phi}(t,k)\in[0,1].
$$

相位損失則為：

$$
\mathcal L_{\phi}
=
\frac{
\sum_{t,k}w_{\phi}(t,k)
\left[1-\cos(\hat\psi_{t,k}-\psi_{t,k})\right]
}{
\sum_{t,k}w_{\phi}(t,k)+\varepsilon
}.
$$

## 8.4 聲源與輸出雙通道

第五篇工程架構應同時保留：

$$
\boldsymbol\Psi^{(y)}
$$

與：

$$
\widehat{\boldsymbol\Psi}^{(g)}.
$$

前者是可直接觀測的輸出相位；後者是依賴逆濾波的聲門估計。兩者不得混合覆寫。

---

# 9. FARHP 的控制層級

## 9.1 第一層：波形重建控制

目標：在振幅、$f_0$ 與聲道固定時，提高原波形重建精度。

評估：

$$
\operatorname{SI\text{-}SDR},
\quad
\operatorname{LSD},
\quad
\operatorname{waveform\ error},
\quad
\operatorname{phase\ error}.
$$

## 9.2 第二層：週期形狀控制

目標：可獨立操控峰值集中、脈衝位置與波形不對稱。

評估：

$$
\operatorname{CF},
\quad
C_\delta,
\quad
\operatorname{skew}_{T_0},
\quad
\operatorname{closure\ alignment}.
$$

## 9.3 第三層：聲質控制

目標：在不改變音素與聲調的情況下，產生可重複的自然度、緊實度、氣聲感或說話人風格差異。

此層必須與振幅及噪聲聯合控制，不能只測 FARHP。

## 9.4 第四層：音韻對立控制

目標：以相位差建立新符號語言中穩定可學習的發音對立。

這是最強命題，必須滿足：

1. 人類可區辨；
2. 不同說話人可模仿；
3. 不易被一般協同發音抹除；
4. AI 可穩定辨識；
5. 不與既有音素或聲調衝突。

第四層不能由前三層的成功自動推出。

---

# 10. 六項可證偽命題

## 命題 A：觀測分解命題

在已知合成聲源與聲道的條件下，觀測 FARHP 應滿足：

$$
\boldsymbol\Psi^{(y)}
\approx
\boldsymbol\Psi^{(g)}
\oplus
\Delta\boldsymbol\Theta_v
\oplus
\Delta\boldsymbol\Theta_r
\oplus
\Delta\boldsymbol\Theta_m.
$$

若系統性不成立，代表諧波追蹤、模型線性或相位估計假設需要修正。

## 命題 B：純延遲不變命題

對同一準週期聲音加入任意固定延遲後，可靠諧波上的 FARHP 距離應接近零：

$$
d_{\mathbb T^{K-1}}
\left(
\boldsymbol\Psi,
\boldsymbol\Psi_{\tau}
\right)
<\epsilon.
$$

## 命題 C：週期形狀控制命題

固定 $f_0$ 與 $\mathbf A$，僅改變 FARHP，應能顯著改變至少一項週期內形狀指標：

$$
\operatorname{CF},
C_\delta,
\operatorname{skew}_{T_0}.
$$

若不能，表示選用的相位參數缺乏有效控制維度。

## 命題 D：自然相位品質命題

在同一振幅與頻率條件下，自然或模型預測 FARHP 的合成品質，應優於固定零相位或隨機相位基線。

若聽覺評分無顯著差異，FARHP 對該條件的知覺收益應被判定為低。

## 命題 E：音類適用門命題

FARHP 的重建與知覺收益應隨諧波性與有聲穩定度增加：

$$
\operatorname{Benefit}
\left(
\Gamma=4
\right)
>
\operatorname{Benefit}
\left(
\Gamma=2
\right)
>
\operatorname{Benefit}
\left(
\Gamma=0
\right).
$$

若無此趨勢，五級適用門控需重定義。

## 命題 F：語言對立獨立命題

若 FARHP 要成為新符號語言的對立特徵，則在控制 $f_0$、共振峰、振幅與時長後，不同相位碼仍須達到顯著高於機率的：

- 人類 ABX 區辨率；
- AI 分類率；
- 跨說話人泛化率。

若只在單一合成器或單一說話人中有效，則不得宣稱形成可泛化的音韻對立。

---

# 11. 實驗設計

## 11.1 實驗一：純諧波可控基準

生成：

$$
x(t)
=
\sum_{k=1}^{K}A_k
\cos
\left(
 k\omega_0t+k\phi_1+\psi_k
\right).
$$

控制變項：

- $K\in\{8,16,32,64\}$；
- $f_0\in\{80,120,180,240\}\ \mathrm{Hz}$；
- 平坦、傾斜及類聲門振幅包絡；
- 零相位、隨機相位、Schroeder 類相位、自然相位與碼本相位。

測量：

- 時間平移不變性；
- 峰均比；
- 時間集中度；
- 聽覺濾波器包絡；
- ABX 區辨。

## 11.2 實驗二：已知聲源—聲道合成母音

使用可控聲門源與已知聲道濾波器生成母音。分別記錄：

$$
\boldsymbol\Psi^{(g)},
\quad
\Delta\boldsymbol\Theta_v,
\quad
\boldsymbol\Psi^{(y)}.
$$

驗證觀測分解式，並測量不同共振峰配置對輸出 FARHP 的影響。

## 11.3 實驗三：自然持續母音

語料至少包含：

$$
\{\text{ㄚ},\text{ㄧ},\text{ㄨ},\text{ㄩ},\text{ㄜ}\}
$$

並涵蓋：

- 不同說話人；
- 不同音高；
- 模態、氣聲與緊聲；
- 同一麥克風與跨麥克風條件；
- 原始輸出 FARHP 與逆濾波聲門 FARHP。

## 11.4 實驗四：華語五聲

對同一音節產生：

$$
q\in\{1,2,3,4,0\}
$$

五種聲調版本，分離分析：

- $f_0$ 軌跡；
- 時長；
- 強度；
- FARHP 軌跡；
- 聲門源估計；
- 聲道共振變化。

核心問題不是「相位能否取代聲調」，而是：

> 在聲調主軌跡之外，FARHP 是否攜帶可重複的聲門動態與自然度線索？

## 11.5 實驗五：音類邊界

比較：

- 穩定母音；
- 近音；
- 鼻音；
- 有聲擦音；
- 無聲擦音；
- 塞音爆破；
- 送氣段。

驗證五級適用門控與相位信賴度。

## 11.6 聽覺實驗

至少包含：

### ABX 區辨

判定不同 FARHP 配置是否可被聽出。

### 自然度評分

比較自然、零、隨機、最小相位與量化相位。

### 屬性標記

要求聽者標記：

- 尖銳／柔和；
- 脈衝／平滑；
- 緊實／氣聲；
- 自然／合成。

### 音素與聲調辨識

驗證相位操控是否意外破壞既有語言類別。

### 跨說話人模仿

測試新相位符號能否由不同人穩定重現。

## 11.7 統計分析

對圓周資料應使用：

- 圓周均值；
- 平均合向量長度；
- 圓周—線性相關；
- 混合效應模型；
- 說話人與聽者隨機效應。

不得將包覆相位直接當作普通線性實數進行未校正平均。

---

# 12. 第四篇離散表示所需的聲學限制

第四篇不能只研究數學量化誤差，還必須遵守以下條件。

## 12.1 不同諧波不可等權

低階與高階諧波的振幅、可解析度、信賴度與知覺作用不同。碼本距離應為：

$$
d^2
=
\sum_{k=2}^{K}
w_k
\left[
1-\cos(\psi_k-\tilde\psi_k)
\right],
$$

其中：

$$
w_k
=
f
\left(
A_k,
 c_k,
\text{auditory band},
\Gamma
\right).
$$

## 12.2 輸出相位與聲門相位分開建碼本

應至少建立：

1. `FARHP-Y`：輸出波形相位碼本；
2. `FARHP-G`：逆濾波聲門相位碼本。

兩者可能具有不同的統計分布與知覺作用。

## 12.3 音類條件碼本

不應把所有音類混入單一碼本。初版至少分成：

- 穩定母音；
- 鼻音與近音；
- 混合有聲噪聲；
- 非適用區域。

## 12.4 $f_0$ 條件化

相位碼本應檢驗是否需要條件化於：

$$
f_0
$$

或標準化諧波頻帶，因為相同諧波索引在不同 $f_0$ 下落入不同絕對頻率與聽覺頻帶。

## 12.5 感知導向量化

量化誤差不只測：

$$
d_{\mathbb T^{K-1}},
$$

還要測：

- 重建波形誤差；
- 聽覺濾波器包絡誤差；
- 自然度下降；
- ABX 可區辨性。

## 12.6 相位碼不是生理碼

離散碼本可以有效重建或生成聲音，不代表每個碼位都對應唯一聲門姿態。文件中必須保留：

```text
acoustic_code
```

與：

```text
physiological_interpretation
```

的區分。

---

# 13. 第五篇工程架構所需的十二項規範

## 規範一：雙相位軌

同時保存觀測 FARHP 與聲門估計 FARHP。

## 規範二：量測鏈校正

記錄麥克風、前級、取樣率、濾波與房間條件。

## 規範三：有聲信賴度

每一框架必須附帶 $f_0$ 及諧波信賴度。

## 規範四：逐諧波遮罩

振幅過低、頻率錯配或受噪聲污染的諧波不可強制填值。

## 規範五：聲源—聲道分解可插拔

逆濾波器不得被寫死為單一演算法。

## 規範六：殘差層獨立

非週期噪聲不得被偽裝成隨機 FARHP。

## 規範七：瞬態事件層獨立

爆破、閉鎖與起振事件需要事件模型。

## 規範八：圓周插值

所有相位平均、插值與損失必須尊重圓周拓撲。

## 規範九：相位連續性

跨框架使用相位累積、解除包覆或狀態空間追蹤，避免人工跳躍。

## 規範十：多基頻模式

偵測次諧波、倍週期及基頻歧義時，不得強行輸出單錨 FARHP。

## 規範十一：感知基線

每次相位模型都必須與零相位、隨機相位、最小相位及自然相位比較。

## 規範十二：失敗檔案

保存：

- 不可辨識相位；
- 無知覺收益；
- 逆濾波失敗；
- 跨設備崩潰；
- 音類門控誤判；
- 相位碼不可模仿。

---

# 14. 本文的核心貢獻

## 貢獻一：觀測 FARHP 分解式

本文將麥克風中的 FARHP 分解為聲門源、聲道、輻射與量測鏈的相對相位貢獻：

$$
\psi^{(y)}_k
=
\psi^{(g)}_k
+
\Delta_k\theta_v
+
\Delta_k\theta_r
+
\Delta_k\theta_m
\pmod{2\pi}.
$$

## 貢獻二：相位歸因非唯一性

本文明確指出，輸出 FARHP 可被觀測，不代表聲門 FARHP 可由單通道錄音無條件唯一恢復。

## 貢獻三：控制與歸因分離

即使無法唯一歸因，輸出 FARHP 仍可作為合成與波形控制參數。可控制不等於已知生理來源。

## 貢獻四：相位效應的知覺分層

本文區分檢出、區辨、品質與語言辨識，避免把一般可聽差異直接升格為音韻對立。

## 貢獻五：五級音類適用門控

本文用 $\Gamma\in\{0,1,2,3,4\}$ 描述不同音類與框架的 FARHP 適用度，使系統不必對所有語音強行套用同一模型。

## 貢獻六：拒絕聲調與相位混同

華語聲調仍由跨時間 $f_0$ 軌跡主導；FARHP 被定位為局部週期內部波形層。

## 貢獻七：建立第四、第五篇的聲學接口

本文提出音類條件碼本、$f_0$ 條件化、感知加權距離、雙相位軌及十二項工程規範。

---

# 15. 限制與開放問題

## 15.1 線性聲源—聲道近似有限

真實發聲存在聲源—聲道耦合，尤其在高音、強發聲、特定母音與喉腔共振條件下，聲門源與聲道不能完全獨立。

## 15.2 基頻估計誤差會污染全部高階座標

第二篇已證明錨點誤差按諧波階數放大。因此高階 FARHP 的聲學解讀必須附帶不確定性。

## 15.3 聽覺效應高度依賴條件

相位效應會因 $f_0$、聲級、頻帶、分析窗、聽者與任務而改變，不宜宣稱存在單一普遍門檻。

## 15.4 自然度改善不等於語言可用

聲碼器中自然相位的品質收益，與新符號語言是否能建立穩定發音對立，是兩個不同問題。

## 15.5 逆濾波不是真值保證

不同聲門逆濾波方法可能產生不同的聲源估計。`glottal_farhp_estimate` 必須保留演算法與信賴度，而不能被標示為絕對真值。

## 15.6 人類模仿能力尚未證明

AI 可以生成精細相位波形，不代表人類可以用自然發聲器官穩定控制同樣的相位碼。符號語言的人類可發音性必須另行實驗。

---

# 16. 結論

FARHP 的聲學價值不在於把整個語音學還原為相位，而在於把「週期內部相對時間結構」從常被忽略或隱式補回的參數中獨立出來。對穩定有聲訊號，FARHP 消除了共同時間原點與純延遲自由度，並保留各諧波在一個基頻週期中的相對配置。這種配置可以改變峰值聚集、波形不對稱、脈衝形狀與聽覺濾波後的時間包絡，也可能影響聲碼器自然度、極性偵測及部分低階諧波知覺。

但本文同時建立了嚴格邊界。麥克風觀測到的 FARHP 是聲門源、聲道、輻射與量測鏈共同形成的結果：

$$
\boxed{
\boldsymbol\Psi^{(y)}
=
\boldsymbol\Psi^{(g)}
\oplus
\Delta\boldsymbol\Theta_v
\oplus
\Delta\boldsymbol\Theta_r
\oplus
\Delta\boldsymbol\Theta_m
}
$$

因此：

$$
\text{可觀測}
\neq
\text{可唯一歸因}.
$$

同樣地：

$$
\text{可控制波形}
\neq
\text{可控制全部聲質}
\neq
\text{可建立語言對立}.
$$

FARHP 的正確位置是一個中介層：

$$
\boxed{
\text{聲門與聲道動力學}
\longrightarrow
\text{FARHP 週期形狀}
\longrightarrow
\text{聽覺時間表徵}
\longrightarrow
\text{品質、辨識與語言功能}
}
$$

每一個箭頭都需要額外條件與實驗驗證。

對後續系列而言，本文確立了三項不可退讓的原則：

1. 第四篇的相位離散化必須是音類、$f_0$、可靠度與知覺加權的；
2. 第五篇的工程系統必須分離輸出相位、聲門估計、噪聲殘差與瞬態事件；
3. 新符號語言只能在跨說話人可區辨、可模仿且不破壞既有華語音韻後，才把 FARHP 升格為正式發音對立。

至此，FARHP 已完成第三層封閉：第一篇建立總體理論，第二篇建立商環面數學，第三篇建立聲學與知覺邊界。下一篇將進入：

**《基錨相差的離散編碼、相位字形與 AI 可學習表示》**。

它的任務不是任意把圓周切成八份或十六份，而是依本文建立的聲學適用域，設計可重建、可感知、可學習且不混淆聲源歸因的多解析度相位碼本。

---

# 參考文獻

[1] G. Fant, *Acoustic Theory of Speech Production*, Mouton, 1960.

[2] M. Airas, H. Pulakka, T. Bäckström, and P. Alku, “A Toolkit for Voice Inverse Filtering and Parametrisation,” *INTERSPEECH 2005*, DOI: 10.21437/Interspeech.2005-434.

[3] L. Juvela, B. Bollepalli, J. Yamagishi, and P. Alku, “Reducing Mismatch in Training of DNN-Based Glottal Excitation Models in a Statistical Parametric Text-to-Speech System,” *INTERSPEECH 2017*.

[4] I. Saratxaga, D. Erro, I. Hernáez, I. Sainz, and E. Navas, “Use of Harmonic Phase Information for Polarity Detection in Speech Signals,” *INTERSPEECH 2009*.

[5] I. Saratxaga, I. Hernáez, I. Odriozola, E. Navas, I. Luengo, and D. Erro, “Using Harmonic Phase Information to Improve ASR Rate,” *INTERSPEECH 2010*, DOI: 10.21437/Interspeech.2010-372.

[6] I. Saratxaga, I. Hernaez, M. Pucher, E. Navas, and I. Sainz, “Perceptual Importance of the Phase Related Information in Speech,” *INTERSPEECH 2012*, DOI: 10.21437/Interspeech.2012-411.

[7] P. Mowlaee, R. Saeidi, and Y. Stylianou, “Phase Importance in Speech Processing Applications,” *INTERSPEECH 2014*.

[8] G. Degottex and N. Obin, “Phase Distortion Statistics as a Representation of the Glottal Source: Application to the Classification of Voice Qualities,” *INTERSPEECH 2014*, DOI: 10.21437/Interspeech.2014-387.

[9] G. Degottex and collaborators, “A Measure of Phase Randomness for the Harmonic Model in Speech Synthesis,” *INTERSPEECH 2014*.

[10] T. Raitio, L. Juvela, A. Suni, M. Vainio, and P. Alku, “Phase Perception of the Glottal Excitation of Vocoded Speech,” *INTERSPEECH 2015*.

[11] K. K. Paliwal and L. Alsteris, “Usefulness of Phase Spectrum in Human Speech Perception,” *EUROSPEECH 2003*, pp. 2117–2120, DOI: 10.21437/Eurospeech.2003-611.

[12] C. Ma, Y. Kamp, and L. F. Willems, “A Psychophysical Study of Fourier Phase and Amplitude Coding of Speech,” *EUROSPEECH 1993*.

[13] J. D. McKeown and C. J. Darwin, “Effects of Phase Changes in Low-Numbered Harmonics on the Internal Representation of Complex Sounds,” *Quarterly Journal of Experimental Psychology A*, vol. 43, no. 3, pp. 401–421, 1991, DOI: 10.1080/14640749108400979.

[14] T. Green and S. Rosen, “Phase Effects on the Masking of Speech by Harmonic Complexes: Variations with Level,” *Journal of the Acoustical Society of America*, vol. 134, no. 4, pp. 2876–2883, 2013, DOI: 10.1121/1.4820899.

[15] M. L. Deroche and collaborators, “Phase Effects in Masking by Harmonic Complexes: Speech Recognition,” *Hearing Research*, 2013, DOI: 10.1016/j.heares.2013.09.008.

[16] G. Mai, “Relative Importance of Temporal Envelope and Fine Structure Cues in Low- and High-Order Harmonic Regions for Mandarin Lexical-Tone Recognition,” *INTERSPEECH 2012*, pp. 1856–1859, DOI: 10.21437/Interspeech.2012-406.

[17] N. P. Narendra, M. Airaksinen, and P. Alku, “Glottal Source Estimation from Coded Telephone Speech Using a Deep Neural Network,” *INTERSPEECH 2017*, pp. 3931–3935, DOI: 10.21437/Interspeech.2017-882.

[18] A. Sorin, S. Shechtman, and A. Rendel, “Semi-Parametric Concatenative TTS with Instant Voice Modification Capabilities,” *INTERSPEECH 2017*, DOI: 10.21437/Interspeech.2017-1202.

[19] S. Chen and T. Toda, “QHM-GAN: Neural Vocoder Based on Quasi-Harmonic Modeling,” *INTERSPEECH 2024*.

[20] H. Kawahara, K.-I. Sakakibara, M. Morise, H. Banno, T. Toda, and T. Irino, “A New Cosine Series Antialiasing Function and Its Application to Aliasing-Free Glottal Source Models for Speech and Singing Synthesis,” *INTERSPEECH 2017*, DOI: 10.21437/Interspeech.2017-15.

---

# 附錄 A：建議資料結構

```yaml
frame:
  time_sec: 0.000
  applicability_grade: 4

f0:
  hz: 120.0
  confidence: 0.98
  ambiguity:
    octave_error_risk: 0.01
    subharmonic_risk: 0.00

observed_farhp:
  anchor: fundamental
  harmonics:
    - k: 2
      cos: 0.00
      sin: 1.00
      confidence: 0.95
    - k: 3
      cos: -0.70
      sin: 0.71
      confidence: 0.91

glottal_farhp_estimate:
  method: IAIF_or_replaceable_method
  harmonics: []
  confidence: 0.70
  assumptions:
    - linear_source_filter
    - vocal_tract_inverse_filter

spectral_envelope:
  representation: configurable
  values: []

residual:
  harmonic_energy_ratio: 0.92
  noise_representation: separate

transient:
  active: false
  event_type: null

recording_chain:
  microphone_id: required
  preamp_id: optional
  room_condition: required
  calibration: optional
```

---

# 附錄 B：音類門控建議表

| 音類 | 建議 $\Gamma$ | FARHP 角色 | 必要附加層 |
|---|---:|---|---|
| 穩定母音 | 4 | 核心週期形狀 | 頻譜包絡、殘差 |
| 近音／滑音 | 3 | 動態週期形狀 | 時變聲道 |
| 鼻音 | 3 | 條件性相位 | 反共振、低信賴度遮罩 |
| 有聲擦音 | 2 | 週期子空間 | 湍流噪聲 |
| 嘎裂／多週期聲 | 1–2 | 廣義相位 | 次諧波、多基頻模型 |
| 無聲擦音 | 0 | 不使用 | 噪聲模型 |
| 爆破瞬態 | 0 | 不使用 | 事件模型 |
| 送氣段 | 0–1 | 局部輔助 | 寬頻殘差 |

---

# 附錄 C：最低可接受的聲學主張

在完成實驗前，FARHP 系列可以主張：

1. FARHP 是良定義的相對諧波相位表示；
2. 它在理想諧波條件下消除共同時間平移；
3. 它描述固定頻率與振幅下仍可變動的週期內部波形形狀；
4. 觀測 FARHP 包含聲門、聲道、輻射與量測鏈貢獻；
5. 它適合穩定有聲區段，對非週期聲音需另加模型；
6. 它具有成為合成控制量與符號發音層的研究價值。

在完成實驗前，不應主張：

1. FARHP 是全新的相對相位公式；
2. FARHP 等於聲門源真值；
3. FARHP 單獨決定聲質；
4. FARHP 可以取代共振峰、聲調或噪聲模型；
5. 人類必然能穩定控制任意相位碼；
6. 相位符號天然形成保密語言；
7. FARHP 已形成可泛化的音韻對立。

---

**文件結束**
