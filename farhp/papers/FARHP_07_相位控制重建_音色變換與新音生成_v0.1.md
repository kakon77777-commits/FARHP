# 基於相對諧波相位控制的聲音重建、音色變換與新音生成

## 從相位環面測地插值到可盲聽的受控生成實驗

**系列：基頻錨定相對諧波相位差（FARHP）第七篇**  
**英文題名：Sound Reconstruction, Timbre Transformation, and Novel Sound Generation through Relative Harmonic Phase Control**  
**版本：v0.1**  
**日期：2026-07-26**  
**作者：Neo.K／EveMissLab；Aletheia／GPT-5.6 Thinking**  
**研究狀態：理論—工程整合稿；含 FARHP-Core v0.3 參考實作與合成盲聽包**

---

## 摘要

前六篇已建立基頻錨定相對諧波相位差（Fundamental-Anchored Relative Harmonic Phase, FARHP）的母定義、商環面數學、聲源—聲道—知覺邊界、離散碼本、單框架分析—重建閉環，以及多框架 $f_0$、錨相位與 FARHP 軌跡追蹤。第七篇處理下一個必要問題：當 FARHP 已成為可追蹤的聲學物件後，應如何對它進行合法控制、插值、風格移植與新音生成，而不把音高、振幅、聲道包絡、時長或非諧波殘差的變化錯誤歸因於相位。

本文提出「相位唯一介入」實驗原則。對內容軌跡 $	au_c$，預設固定其取樣率、時間軸、有聲狀態、$f_0(t)$、逐諧波振幅 $A_{t,k}$、錨相位 $	heta_t$ 與時長，只允許 FARHP 座標 $oldsymbol\psi_t$ 沿相位環面改變。單一圓周座標的插值採最短測地線：

$$
\operatorname{GI}_{S^1}(a,b;\lambda)
=
\operatorname{wrap}
\left(
 a+\lambda\operatorname{wrap}(b-a)
\right),
$$

並逐座標提升至相位環面。本文定義原相位、零相位、奇偶交替相位、固定隨機相位、平滑隨機相位、部分風格插值及完整風格移植等對照條件；同時提出跨長度軌跡的正規化時間對齊、缺失座標保留政策、相位速度重建與不變量證書。

配套工程 `FARHP-Core v0.3` 已完成圓周測地插值、FARHP-only 條件變換、動態相位風格移植、匿名盲聽包產生器、公開與秘密 manifest、客觀比較指標及 `FARHP-Transform-Spec-v0.3`。在一組受控動態合成母音上，完整風格移植使有效 FARHP 座標平均移動 $0.908849$ rad、最大移動 $2.619044$ rad，同時精確保留 $f_0$、逐諧波振幅與錨相位。二十一項自動測試全部通過。本文亦記錄並修正一項 overlap-add 邊界權重過小所造成的假尖峰，以避免將數值重建瑕疵誤判為相位效應。

上述結果證明的是相位控制架構、資料不變量與合成回歸材料的一致性，不是自然語音品質、語言辨識效果或人類知覺顯著性的最終實證。真正的知覺結論仍須由預註冊、隨機化、雙盲或至少單盲的受試者實驗建立。

**關鍵詞：** FARHP、相對諧波相位、相位環面、測地插值、相位風格移植、音色變換、新音生成、盲聽、受控實驗、聲音重建

---

# 1. 第七篇的核心轉折：從估計物件到干預物件

第六篇將 FARHP 從靜態向量提升為具有時間、遮罩、置信度、錨點與重啟政策的軌跡：

$$
\mathcal P
=
\left(
\mathbf f_0,
\mathbf v,
\mathbf c,
\boldsymbol\Phi_1,
\boldsymbol\Psi,
\dot{\boldsymbol\Psi},
\mathbf M,
\mathbf C,
\mathcal G
\right).
$$

但「能估計」並不自動等於「能合法修改」。若任意改變所有聲學參數，再將聽感差異歸因於相位，研究便失去可識別性。第七篇因此將研究問題改寫為：

$$
\boxed{
\text{在其他指定參數保持不變時，
只改變 FARHP，聲波與知覺會如何變化？}
}
$$

這是一個干預問題，而非單純相關問題。令完整聲學生成器為：

$$
\widehat x
=
\mathcal S
\left(
\mathbf f_0,
\mathbf A,
\boldsymbol\Phi_1,
\boldsymbol\Psi,
\mathbf R,
\mathbf D
\right),
$$

其中：

- $\mathbf f_0$ 是基頻軌跡；
- $\mathbf A$ 是逐框架逐諧波振幅；
- $\boldsymbol\Phi_1$ 是錨相位；
- $\boldsymbol\Psi$ 是 FARHP；
- $\mathbf R$ 是非諧波殘差；
- $\mathbf D$ 是時長與框架排列。

第七篇的最低對照條件是：

$$
\mathbf f_0' = \mathbf f_0,
\qquad
\mathbf A' = \mathbf A,
\qquad
\boldsymbol\Phi_1' = \boldsymbol\Phi_1,
\qquad
\mathbf D'=\mathbf D,
$$

而：

$$
\boldsymbol\Psi'
=
\mathcal T_\psi(\boldsymbol\Psi).
$$

在目前諧波式參考實作中，$\mathbf R$ 尚未納入完整建模，因此本文所有「相位唯一介入」首先是對諧波子系統而言。自然語音若包含擦音、爆破、氣聲與非週期殘差，則必須明確標示殘差是固定、移除、重新估計或共同生成。

---

# 2. 相位空間不是普通向量空間

## 2.1 單座標的圓周幾何

一個相位角不是實直線上的唯一數值，而是：

$$
\psi
\in
S^1
\cong
\mathbb R/2\pi\mathbb Z.
$$

因此：

$$
\pi-\varepsilon
\quad\text{與}\quad
-\pi+\varepsilon
$$

彼此很近，而不是相距約 $2\pi$。圓周測地距離為：

$$
d_{S^1}(a,b)
=
\left|
\operatorname{wrap}(b-a)
\right|.
$$

若直接使用普通線性插值：

$$
(1-\lambda)a+\lambda b,
$$

當 $a=170^\circ$、$b=-170^\circ$ 時，中點會錯誤落在 $0^\circ$。真正的最短路徑中點應位於 $\pm180^\circ$。

## 2.2 圓周最短測地插值

本文採用：

$$
\operatorname{GI}_{S^1}(a,b;\lambda)
=
\operatorname{wrap}
\left(
 a+\lambda\operatorname{wrap}(b-a)
\right),
\qquad
0\le\lambda\le1.
$$

它滿足：

$$
\operatorname{GI}_{S^1}(a,b;0)=a,
$$

$$
\operatorname{GI}_{S^1}(a,b;1)=b.
$$

當 $a$ 與 $b$ 恰好對徑，即：

$$
d_{S^1}(a,b)=\pi,
$$

最短路徑不唯一。工程上必須指定一致的分支規則，或把此情況標記為插值歧義，而不能假裝只有一條天然路徑。

## 2.3 提升至 FARHP 相位環面

對 $K$ 個諧波，消除錨點自由度後的 FARHP 狀態位於：

$$
\mathbb T^{K-1}
=
(S^1)^{K-1}.
$$

逐座標插值為：

$$
\boldsymbol\psi_\lambda
=
\operatorname{wrap}
\left(
\boldsymbol\psi_a
+
\lambda
\operatorname{wrap}
\left(
\boldsymbol\psi_b-
\boldsymbol\psi_a
\right)
\right).
$$

若有遮罩 $m_k$ 與權重 $w_k$，則整體位移可量化為：

$$
d_{\mathbb T}
\left(
\boldsymbol\psi_a,
\boldsymbol\psi_b
\right)
=
\sqrt{
\frac{
\sum_{k=2}^{K}
w_km_k
d_{S^1}
\left(
\psi_{a,k},
\psi_{b,k}
\right)^2
}{
\sum_{k=2}^{K}w_km_k
}
}.
$$

這個距離不等於知覺距離，但它是相位干預大小的最低幾何記錄。

---

# 3. 相位唯一介入原則

## 3.1 預設保留量

本文將下列量列為預設不變量：

$$
\mathcal I
=
\left\{
F_s,
\mathbf t,
\mathbf v,
\mathbf f_0,
\mathbf A,
\boldsymbol\Phi_1,
\mathbf D
\right\}.
$$

其中 $F_s$ 是取樣率，$\mathbf t$ 是框架時間，$\mathbf v$ 是有聲狀態。若實驗額外保留非諧波殘差，則將 $\mathbf R$ 納入 $\mathcal I$。

## 3.2 可變量

可變量是：

$$
\mathcal V
=
\left\{
\boldsymbol\Psi,
\dot{\boldsymbol\Psi}
\right\}.
$$

修改包覆 FARHP 後，解除包覆軌跡與相位速度必須重新計算，不能保留舊值。否則資料物件會同時包含彼此矛盾的靜態座標與動態導數。

## 3.3 不變量證書

每一次相位變換應輸出至少以下檢查：

$$
\Delta f_0^{\max}
=
\max_t
\left|
f_0'(t)-f_0(t)
\right|,
$$

$$
\Delta A^{\max}
=
\max_{t,k}
\left|
A'_{t,k}-A_{t,k}
\right|,
$$

$$
\Delta\Phi_1^{\max}
=
\max_t
\left|
\Phi_1'(t)-\Phi_1(t)
\right|.
$$

在嚴格相位唯一介入中，應有：

$$
\Delta f_0^{\max}=0,
\qquad
\Delta A^{\max}=0,
\qquad
\Delta\Phi_1^{\max}=0.
$$

若不是零，則該實驗不能再稱為純 FARHP 介入。

---

# 4. 五種基礎相位對照條件

## 4.1 原相位條件

$$
\boldsymbol\Psi'=
\boldsymbol\Psi.
$$

它是所有比較的參考，不代表原始自然波形；在目前系統中，它是以估計出的諧波振幅與 FARHP 重建出的 harmonic-only identity。

## 4.2 零相位條件

$$
\psi'_{t,k}=0,
\qquad
k\ge2.
$$

此時所有諧波的相對相位對齊於基頻錨所決定的線性相位關係。零相位不是「沒有相位」，而是一個非常特殊的相位組態。

## 4.3 奇偶交替條件

可使用確定性模板：

$$
\psi_k^{\mathrm{alt}}
=
\operatorname{wrap}
\left(
0.72\pi(k\bmod2)+0.11k
\right).
$$

此條件提供可重複、非隨機且與原始軌跡不同的結構化對照。

## 4.4 固定隨機相位條件

對每個諧波抽取一個固定角度：

$$
\xi_k
\sim
\operatorname{Uniform}(-\pi,\pi),
$$

並對所有框架使用同一 $\xi_k$：

$$
\psi'_{t,k}=\xi_k.
$$

此條件破壞原始諧波間相對結構，但不額外引入快速時間抖動。

## 4.5 平滑隨機相位條件

先在稀疏控制點上生成隨機增量：

$$
\eta_{j,k}
\sim
\mathcal N(0,\sigma_k^2),
$$

建立解除包覆的隨機游走：

$$
\Xi_{j,k}
=
\sum_{q\le j}\eta_{q,k},
$$

再沿時間插值並包覆：

$$
\psi'_{t,k}
=
\operatorname{wrap}
\left(
\operatorname{Interp}_t
\left(
\Xi_{j,k}
\right)
\right).
$$

它測試的是動態相位結構被替換後的效果，而非逐框架白噪聲式跳變。

---

# 5. 相位風格的操作性定義

## 5.1 「風格」不是本體真值

本文使用「相位風格」作為工程性術語，指一段 FARHP 軌跡在諧波階數與正規化時間上的可移植結構。它不代表說話者身份、人格、生理聲門真值或完整音色。

令內容軌跡為：

$$
\tau_c
=
\left(
\mathbf f_0^c,
\mathbf A^c,
\boldsymbol\Phi_1^c,
\boldsymbol\Psi^c
\right),
$$

風格軌跡為：

$$
\tau_s
=
\left(
\mathbf f_0^s,
\mathbf A^s,
\boldsymbol\Phi_1^s,
\boldsymbol\Psi^s
\right).
$$

純相位風格移植只取：

$$
\boldsymbol\Psi^s,
$$

而保留內容側：

$$
\mathbf f_0^c,
\quad
\mathbf A^c,
\quad
\boldsymbol\Phi_1^c.
$$

因此輸出為：

$$
\tau_{c\leftarrow s}^{(\lambda)}
=
\left(
\mathbf f_0^c,
\mathbf A^c,
\boldsymbol\Phi_1^c,
\operatorname{GI}_{\mathbb T}
\left(
\boldsymbol\Psi^c,
\mathcal R_t
\left[
\boldsymbol\Psi^s
\right];
\lambda
\right)
\right).
$$

$\mathcal R_t$ 表示時間對齊或重取樣。

## 5.2 正規化時間對齊

若內容與風格長度不同，本文第一版使用：

$$
u_c(t)
=
\frac{t}{T_c},
\qquad
u_s(t)
=
\frac{t}{T_s},
$$

將兩者映射到：

$$
[0,1].
$$

風格解除包覆相位先在有效點上插值，再重新包覆。這種對齊只保存相對進度，不理解音素、音節、重音或語義邊界，因此只是基線方法。

更完整的語音系統應改用：

- 音素或注音邊界對齊；
- 動態時間校正；
- 發音部位事件對齊；
- 聲門閉合事件對齊；
- 語義或韻律節點對齊。

## 5.3 缺失座標政策

若風格側某一座標缺失，而內容側有效，第一版採：

$$
\psi'_{t,k}=\psi^c_{t,k}.
$$

也就是保留內容座標，不用零填補。因為：

$$
0
\neq
\text{missing}.
$$

若內容側本來缺失，則不因風格側存在而自動創造一個新諧波；否則會改變有效諧波集合與振幅語義。

---

# 6. 部分插值與連續生成路徑

令插值強度為：

$$
\lambda
\in
[0,1].
$$

則：

$$
\boldsymbol\Psi^{(\lambda)}
=
\operatorname{GI}_{\mathbb T}
\left(
\boldsymbol\Psi^c,
\boldsymbol\Psi^s;
\lambda
\right).
$$

其中：

$$
\lambda=0
$$

是內容原相位；

$$
\lambda=1
$$

是完整相位風格移植；

$$
0<\lambda<1
$$

形成一條相位環面上的連續生成路徑。

若每個座標的最短分支在整段路徑中固定，則幾何位移近似線性：

$$
d_{\mathbb T}
\left(
\boldsymbol\Psi^c,
\boldsymbol\Psi^{(\lambda)}
\right)
=
\lambda
d_{\mathbb T}
\left(
\boldsymbol\Psi^c,
\boldsymbol\Psi^s
\right).
$$

但知覺差異不必對 $\lambda$ 線性。可能存在：

- 低強度幾乎不可察覺；
- 某個閾值後突然可辨；
- 中間值比端點更自然；
- 不同諧波階數具有不同敏感度；
- 不同 $f_0$、音量與聲道條件改變敏感性。

因此 $\lambda$ 是幾何控制量，不是知覺百分比。

---

# 7. 動態相位速度與平滑性

## 7.1 只插值包覆值可能產生假跳變

即使每框架的角度都合法，若時間上分支不一致，仍可能出現：

$$
\psi_{t,k}
\approx
\pi-\varepsilon,
$$

下一框架卻表示為：

$$
\psi_{t+1,k}
\approx
-\pi+\varepsilon.
$$

包覆值看似跳了約 $2\pi$，實際圓周位移很小。因此變換後必須重新建立解除包覆代表：

$$
\widehat\Psi_{t,k}
=
\widehat\Psi_{t-1,k}
+
\operatorname{wrap}
\left(
\psi_{t,k}-
\widehat\Psi_{t-1,k}
\right).
$$

## 7.2 相位速度

$$
\dot\Psi_{t,k}
=
\frac{
\widehat\Psi_{t,k}-
\widehat\Psi_{t-1,k}
}{
\Delta t
}.
$$

對生成模型，可加入速度正則項：

$$
\mathcal L_{\mathrm{vel}}
=
\sum_{t,k}
w_{t,k}
\left|
\dot\Psi'_{t,k}
-
\dot\Psi^{\mathrm{target}}_{t,k}
\right|^2.
$$

或加速度正則：

$$
\mathcal L_{\mathrm{acc}}
=
\sum_{t,k}
w_{t,k}
\left|
\dot\Psi'_{t,k}-
\dot\Psi'_{t-1,k}
\right|^2.
$$

這些正則不能取代知覺評估，但可避免模型以高速相位擾動達成數值目標。

---

# 8. 重建公式與控制邊界

對第 $t$ 個框架，修改後的諧波相位為：

$$
\phi'_{t,k}
=
\operatorname{wrap}
\left(
k\phi_{t,1}+
\psi'_{t,k}
\right).
$$

重建框架：

$$
\widehat x'_t[n]
=
\sum_{k=1}^{K_t}
M_{t,k}A_{t,k}
\cos
\left(
2\pi kf_0(t)
\frac{n}{F_s}
+
\phi'_{t,k}
\right).
$$

多框架以窗函數 $w[n]$ overlap-add：

$$
\widehat x'[n]
=
\frac{
\sum_t
w[n-tH]
\widehat x'_t[n-tH]
}{
\sum_t
w[n-tH]^2
}.
$$

其中 $H$ 是 hop size。

## 8.1 邊界除權問題

若窗函數在檔案外緣接近零，而程式仍以極小權重相除，會出現非物理尖峰。這種尖峰可能大幅提高峰均比，甚至被錯誤解讀成相位對脈衝集中的影響。

因此 `FARHP-Core v0.3` 加入支撐閾值：

$$
W[n]
=
\sum_t w[n-tH]^2,
$$

只有：

$$
W[n]
>
10^{-3}\max_n W[n]
$$

時才進行除權；不具充分窗支撐的外緣樣本設為零。這是一項重建器修正，不是 FARHP 理論更動。

---

# 9. 新音生成的三種層級

## 9.1 受控模板生成

由人工規則生成：

$$
\psi_{t,k}
=
F(k,t;\boldsymbol\theta).
$$

例如：

- 奇偶交替；
- 階數螺旋；
- 緩慢旋轉；
- 局部諧波群相位聚合；
- 特定階數的相位缺口。

此層最可解釋，適合建立測試庫。

## 9.2 碼本與插值生成

從環面碼本中心：

$$
\mathbf c_j
\in
\mathbb T^{K-1}
$$

抽取或插值：

$$
\boldsymbol\psi
=
\operatorname{GI}_{\mathbb T}
\left(
\mathbf c_i,
\mathbf c_j;
\lambda
\right).
$$

它可形成有限但可組合的相位音色字彙。

## 9.3 條件生成模型

未來可建模：

$$
p
\left(
\boldsymbol\Psi
\mid
\mathbf f_0,
\mathbf A,
\text{phoneme},
\text{speaker},
\text{style},
\Gamma
\right).
$$

模型輸出必須尊重圓周拓撲，可使用：

- 正弦—餘弦回歸；
- von Mises 或混合圓周分布；
- 環面 flow；
- 離散碼本 token；
- 圓周 diffusion；
- 具相位速度約束的序列模型。

「新音」不等於任意亂相位。真正可用的新音生成，還需要振幅、聲道、殘差與發音動作共同合法。

---

# 10. 客觀量測：能量相同不代表波形相同

## 10.1 均方根能量

$$
\operatorname{RMS}(x)
=
\sqrt{
\frac{1}{N}
\sum_n x[n]^2
}.
$$

理想無限時間正交諧波的總能量主要由振幅決定，但有限窗、動態 $f_0$、overlap-add 與邊界會使實際 RMS 略有變化。

## 10.2 峰均比

$$
\operatorname{CF}(x)
=
\frac{
\max_n|x[n]|
}{
\operatorname{RMS}(x)
}.
$$

FARHP 改變諧波在時間上的聚合方式，因此可能明顯改變峰值結構。但峰均比也會被窗邊界、正規化與殘差影響，不能單獨當作知覺自然度。

## 10.3 與原相位的波形相關

$$
\rho(x,x')
=
\frac{
\operatorname{Cov}(x,x')
}{
\sigma_x\sigma_{x'}
}.
$$

低相關表示波形改變大，但不直接代表聽感差異大或品質低。

## 10.4 對數頻譜距離

$$
D_{\log}
=
\sqrt{
\frac{1}{TF}
\sum_{t,f}
\left(
20\log_{10}|X_{t,f}|
-
20\log_{10}|X'_{t,f}|
\right)^2
}.
$$

即使逐框架諧波振幅被保存，跨框架窗疊加與局部相位干涉仍可能改變短時頻譜。這正說明「保存諧波振幅」不等於「所有時頻幅度完全不變」。

## 10.5 相位環面位移

$$
D_\psi
=
\frac{1}{T}
\sum_t
d_{\mathbb T}
\left(
\boldsymbol\psi_t,
\boldsymbol\psi'_t
\right).
$$

它記錄干預量，應與知覺評分分開報告。

---

# 11. 盲聽實驗設計

## 11.1 為什麼不能只聽幾個檔案後下結論

相位效應容易受到下列因素影響：

- 播放音量；
- 耳機與揚聲器；
- 基頻；
- 聲音持續時間；
- 訓練程度；
- 是否知道條件；
- 檔名暗示；
- 樣本順序；
- 重複聆聽次數；
- 是否以自然度、差異、清晰度或偏好作答。

因此盲聽包至少應隱藏條件名稱並隨機化順序。

## 11.2 公開 manifest

公開檔只包含：

- 匿名 trial 編號；
- 匿名 WAV 路徑；
- 評分尺度；
- 使用說明；
- 不透露條件的評分模板。

## 11.3 秘密對照表

獨立保存：

- 隨機種子；
- 匿名檔名與真實條件映射；
- 變換強度；
- 變換報告；
- 客觀指標。

評分完成前不應開啟秘密對照表。

## 11.4 建議評分維度

每項可使用 $1$ 至 $7$ 分：

- 與參考差異；
- 自然度；
- 尖銳感；
- 氣聲感；
- 偏好。

不同維度必須分開，不能把「不同」等同「不好」。

## 11.5 正式實驗所需改進

目前 v0.3 只產生單人可用的盲聽包。正式研究至少應加入：

- 受試者數與檢定力分析；
- 預註冊假設；
- 拉丁方或平衡順序；
- 重複樣本檢查內部一致性；
- 參考樣本與錨定樣本；
- 耳機檢測；
- 音量校準；
- 混合效果模型；
- 多重比較校正；
- 自然語音與不同 $f_0$ 分層。

---

# 12. FARHP-Transform-Spec-v0.3

## 12.1 變換報告

每次操作輸出：

```yaml
operation: style_transfer
strength: 0.5
changed_coordinates: 1921
mean_geodesic_shift_rad: 0.454424
max_geodesic_shift_rad: 1.309522
metadata:
  style_frame_count: 83
```

## 12.2 操作類型

第一版支援：

```text
identity
zero
alternating
random_static
random_smooth
style_transfer
```

部分風格插值由 `style_transfer` 加上：

$$
0<\lambda<1
$$

表示。

## 12.3 預設不變量

```text
sample_rate_hz
frame_times_sec
voiced_state
f0_hz
harmonic_amplitude
anchor_phase
duration
```

## 12.4 缺失策略

```text
style missing + content valid -> preserve content
content missing -> remain missing
zero phase -> valid value, not missing
```

## 12.5 盲聽包

公開部分：

```text
public_manifest.json
rating_template.json
audio/*.wav
```

秘密部分：

```text
secret_key.json
trajectories/*.json
```

---

# 13. FARHP-Core v0.3 參考實作

## 13.1 新增模組

```text
src/farhp/transform.py
src/farhp/experiment.py
tests/test_transform.py
spec/FARHP_Transform_Spec_v0.3.yaml
spec/FARHP_Transform_Spec_v0.3.schema.json
```

## 13.2 新增命令列

### 條件變換

```bash
farhp transform-track input.json \
  --mode zero \
  --strength 1.0 \
  --out zero.json \
  --wav zero.wav
```

### 相位風格插值

```bash
farhp morph-track content.json style.json \
  --strength 0.5 \
  --out morph_050.json \
  --wav morph_050.wav
```

### 盲聽包

```bash
farhp blind-pack content.json style.json \
  --out artifacts/blind_listening_pack \
  --seed 20260726
```

## 13.3 版本邊界

v0.3 尚未完成：

- 自然語音語料驗證；
- 完整非諧波殘差保持；
- 音素對齊式風格移植；
- 聲門逆濾波域 `FARHP-G` 變換；
- 神經相位生成；
- 多受試者盲聽統計；
- 可直接用於產品級 TTS 的低延遲重建。

---

# 14. 受控合成回歸實驗

## 14.1 內容與風格材料

內容軌跡：

- 動態合成母音近似 `/a/`；
- 時長 $1.20$ 秒；
- $f_0$ 約由 $108$ Hz 滑向 $162$ Hz；
- $18$ 個諧波上限；
- $113$ 個分析框架。

風格軌跡：

- 動態合成母音近似 `/i/`；
- 時長 $0.90$ 秒；
- $f_0$ 約由 $135$ Hz 滑向 $118$ Hz；
- 先以 $0.85$ 強度注入奇偶交替相位模板；
- $83$ 個分析框架。

風格側的音高與振幅不會移植到內容側，只使用其 FARHP 軌跡。

## 14.2 不變量證書

完整風格移植得到：

| 指標 | 結果 |
|---|---:|
| $f_0$ 是否逐框架精確保存 | 是 |
| 最大諧波振幅差 | $0$ |
| 最大錨相位差 | $0$ rad |
| 平均 FARHP 測地位移 | $0.908849$ rad |
| 最大 FARHP 測地位移 | $2.619044$ rad |

因此本次輸出符合相位唯一介入的最低工程定義。

## 14.3 各條件結果

| 條件 | 平均相位位移 | 波形相關 | 對數頻譜距離 | 峰均比 |
|---|---:|---:|---:|---:|
| 原相位 | $0.000000$ rad | $1.000000$ | $0.000000$ dB | $17.0556$ |
| 零相位 | $1.090001$ rad | $0.632474$ | $5.404131$ dB | $10.6749$ |
| 奇偶交替 | $1.054756$ rad | $0.037989$ | $6.851739$ dB | $14.5760$ |
| 固定隨機 | $1.524481$ rad | $0.113860$ | $6.442079$ dB | $17.8550$ |
| 平滑隨機 | $1.300048$ rad | $0.443769$ | $5.878621$ dB | $14.3594$ |
| 風格插值 $0.25$ | $0.227212$ rad | $0.935072$ | $3.370066$ dB | $18.1938$ |
| 風格插值 $0.50$ | $0.454424$ rad | $0.755005$ | $4.818818$ dB | $18.5806$ |
| 風格插值 $0.75$ | $0.681637$ rad | $0.498552$ | $5.854799$ dB | $17.0727$ |
| 完整風格移植 | $0.908849$ rad | $0.218477$ | $6.701508$ dB | $16.0093$ |

## 14.4 幾何控制的線性與聲波反應的非線性

風格插值的平均測地位移近似依 $\lambda$ 線性增加：

$$
0.227212,
\quad
0.454424,
\quad
0.681637,
\quad
0.908849.
$$

但波形相關與頻譜距離並非簡單線性。這符合前述區分：

$$
\text{相位幾何距離}
\neq
\text{聲波距離}
\neq
\text{知覺距離}.
$$

## 14.5 盲聽包

v0.3 自動產生七個匿名樣本，涵蓋：

- 原相位；
- 零相位；
- 奇偶交替；
- 固定隨機；
- 平滑隨機；
- $0.5$ 風格插值；
- 完整風格移植。

公開 manifest 不包含條件名稱；秘密檔保存映射與客觀指標。

## 14.6 自動測試

共有二十一項測試，涵蓋：

- 舊版單框架與軌跡功能；
- 跨 $\pm\pi$ 的測地插值；
- 零相位條件；
- 隨機種子可重現性；
- 風格移植端點；
- 半程測地中點；
- $f_0$、振幅與錨相位保持；
- 盲聽包匿名性；
- Transform Schema；
- overlap-add 邊界尖峰防護。

結果：

```text
Ran 21 tests
OK
```

---

# 15. 本次實驗能證明與不能證明的事

## 15.1 能證明

1. FARHP 軌跡可被獨立修改並重新重建；
2. 圓周測地插值正確處理 $\pm\pi$ 邊界；
3. 相位風格可在不同長度軌跡間以正規化時間移植；
4. 內容側 $f_0$、逐諧波振幅及錨相位可精確保持；
5. 不同 FARHP 條件會產生顯著不同的重建波形；
6. 盲聽材料可以自動匿名、隨機化與附帶秘密對照表；
7. overlap-add 邊界假尖峰可被檢測並修正。

## 15.2 不能證明

1. 相位變換一定能改善自然語音；
2. 任一條件在人類聽感上必然可辨；
3. 波形相關低就代表品質低；
4. FARHP 就是完整音色；
5. 相位風格等於說話者風格；
6. 合成母音結果可直接外推到華語音節；
7. 零相位、隨機相位或移植相位在所有播放條件下具有相同效果；
8. 目前方法已能安全承載語義編碼。

---

# 16. 可證偽命題

## 命題一：測地插值優於普通線性角度插值

對跨越 $\pm\pi$ 的 FARHP 座標，普通線性角度插值將產生較大的圓周路徑與不必要的聲波突變；測地插值應降低此類錯誤。

若在嚴格控制實驗中兩者沒有任何差異，或普通插值系統性更穩定，則需修正目前選擇。

## 命題二：相位位移與波形差異相關但不等價

平均環面位移增加時，波形相關應整體下降，但不呈固定一對一函數。

若不同相位位移總是映射到單一、穩定且跨材料不變的波形距離，則可建立更強的映射；反之本文的非等價判斷得到支持。

## 命題三：平滑隨機相位優於逐框架獨立隨機相位

在相同相位分布下，具時間平滑性的隨機軌跡應減少非自然高速調變與瞬態。

若逐框架獨立隨機在客觀與知覺上不劣，則相位速度約束的重要性需重新評估。

## 命題四：部分風格插值可形成連續知覺路徑

隨 $\lambda$ 增加，受試者對「與原相位不同」的評分應整體增加，但可能具有閾值與非線性。

若評分完全不隨 $\lambda$ 變化，則相位風格插值在該材料與播放條件下缺乏可感知控制力。

## 命題五：低階諧波相位的知覺權重高於極弱高階諧波

在等環面距離下，將位移集中於高振幅低階諧波，應比集中於低振幅高階諧波更易辨識。

若結果相反或無差異，需重新估計知覺權重。

## 命題六：相位唯一介入能分離部分峰值結構變化

在固定諧波振幅下，FARHP 仍應能改變峰均比與局部脈衝集中度。

若嚴格修正窗與邊界後這些量始終不變，則相位控制對時間波形結構的作用被高估。

## 命題七：相位風格移植不等於完整音色移植

只移植 FARHP 的結果應與同時移植振幅包絡、$f_0$、殘差及聲道參數的完整轉換有可測差異。

若兩者在大規模自然語音與知覺實驗中不可區分，則 FARHP 的承載能力遠高於目前保守估計。

---

# 17. 理論與工程限制

## 17.1 聲源—聲道不可唯一分解

輸出域 `FARHP-Y` 包含聲門源、聲道相位、唇端輻射與量測鏈貢獻。移植 `FARHP-Y` 不等於移植純聲門形狀。

## 17.2 目前只處理共享諧波索引

風格側不存在的高階座標不會被外推。不同 $f_0$ 使諧波頻率落在不同聲道區域，單靠階數對齊可能不足。

## 17.3 正規化時間不是語音事件對齊

不同音節、輔音或聲調之間，單純將時間壓到 $[0,1]$ 可能把不相干事件對齊。

## 17.4 諧波重建不是完整自然語音

非週期殘差、瞬態、送氣與摩擦成分未被完整保持，盲聽材料不可視為產品級語音。

## 17.5 客觀指標不等於知覺

RMS、峰均比、相關與頻譜距離只是診斷量。真正結論需由受試者資料建立。

## 17.6 相位可承載資訊不等於適合隱密通信

FARHP 可被編碼、量化與生成，但若映射規則、資料或大量樣本可得，模型可以分析其規律。真正機密仍需標準密碼學保護。

---

# 18. 第八篇接口：華語音節與聲調整合

第八篇將把 FARHP 變換系統接入華語音節結構：

$$
\Sigma
=
\left(
O,
M,
N,
C,
T,
D,
\boldsymbol\Psi,
R
\right).
$$

其中：

- $O$：聲母；
- $M$：介音；
- $N$：韻腹；
- $C$：韻尾；
- $T$：聲調與 $f_0$ 軌跡；
- $D$：時長；
- $\boldsymbol\Psi$：FARHP；
- $R$：非諧波殘差。

第八篇需要完成：

1. 注音音節合法組合表；
2. 四呼與韻母結構；
3. 五種聲調的基頻、時長與強度軌跡；
4. 母音與鼻韻尾的 FARHP 基線；
5. 塞音、擦音、送氣音的殘差層；
6. 聲調與相位不可混同的資料規格；
7. 同音節不同 FARHP 的最小可辨識實驗；
8. 華語可發音但現代詞彙較少使用的音節空間；
9. 相位附標與新符號語言的朗讀接口。

第八篇不應直接追求完整華語 TTS，而應先建立：

$$
\boxed{
\text{母音／鼻音核心}
+
\text{五聲軌跡}
+
\text{FARHP 控制}
+
\text{殘差插槽}
}
$$

的最小音節生成器。

---

# 19. 結論

第七篇把 FARHP 從「可以估計與保存的相位軌跡」推進為「可以受控干預、連續插值、移植、生成與盲測的聲學子系統」。其核心不是宣稱相位可以取代整個語音系統，而是建立一個嚴格分離變量的研究方法：

$$
\boxed{
\text{固定內容側的音高、振幅、錨點與時間，
只讓 FARHP 在相位環面上移動。}
}
$$

合法插值必須尊重：

$$
S^1
\quad\text{與}\quad
\mathbb T^{K-1}
$$

的拓撲，而不是把角度當成普通實數。相位風格移植則被限制為 FARHP 軌跡的操作性轉移，不宣稱等同完整音色、生理聲門或說話者身份。

`FARHP-Core v0.3` 已完成：

- 圓周測地插值；
- 五種相位對照條件；
- 不同長度軌跡的相位風格移植；
- 解除包覆軌跡與速度重建；
- 不變量證書；
- 匿名盲聽包；
- Transform Spec；
- 二十一項測試；
- overlap-add 邊界尖峰修正。

這使 FARHP 系列的兩篇核心工程已完成。下一階段不再主要回答「相位能不能被抽取與修改」，而是回答：

$$
\boxed{
\text{如何把它嵌入華語音節、五聲、注音與新符號語言？}
}
$$

---

# 參考文獻

1. de Cheveigné, A., & Kawahara, H. “YIN, a Fundamental Frequency Estimator for Speech and Music.” *Journal of the Acoustical Society of America*, 2002.
2. McAulay, R. J., & Quatieri, T. F. “Speech Analysis/Synthesis Based on a Sinusoidal Representation.” *IEEE Transactions on Acoustics, Speech, and Signal Processing*, 1986.
3. Saratxaga, I., Erro, D., Hernáez, I., Sainz, I., & Navas, E. “Use of Harmonic Phase Information for Speaker Recognition.” *Interspeech*, 2010.
4. Sanchez, J., Saratxaga, I., Hernáez, I., Navas, E., & Erro, D. “The AHOCoder: An Harmonic Model for Speech Coding.” 相關相位表示研究。
5. Mowlaee, P., Kulmer, J., Stahl, J., & Mayer, F. *Single Channel Phase-Aware Signal Processing in Speech Communication*. Wiley, 2017.
6. Paliwal, K. K., Wójcicki, K., & Shannon, B. “The Importance of Phase in Speech Enhancement.” *Speech Communication*, 2011.
7. Schroeder, M. R. “New Results Concerning Monaural Phase Sensitivity.” *Journal of the Acoustical Society of America*, 1959.
8. Plomp, R., & Steeneken, H. J. M. “Effect of Phase on the Timbre of Complex Tones.” *Journal of the Acoustical Society of America*, 1969.
9. Oppenheim, A. V., & Lim, J. S. “The Importance of Phase in Signals.” *Proceedings of the IEEE*, 1981.
10. Griffin, D., & Lim, J. “Signal Estimation from Modified Short-Time Fourier Transform.” *IEEE Transactions on Acoustics, Speech, and Signal Processing*, 1984.

---

## 附錄 A：圓周測地插值偽程式

```text
function geodesic_interpolate(a, b, lambda):
    delta = wrap(b - a)
    return wrap(a + lambda * delta)
```

## 附錄 B：相位風格移植偽程式

```text
input:
    content trajectory C
    style trajectory S
    strength lambda

1. extract wrapped FARHP matrices Psi_C and Psi_S
2. unwrap each valid style harmonic across time
3. resample style time to content normalized time
4. for every content-valid and style-valid coordinate:
       Psi_out = geodesic_interpolate(Psi_C, Psi_S_resampled, lambda)
5. preserve content F0, amplitudes, anchor phase, voicing, and duration
6. recompute unwrapped FARHP and phase velocity
7. emit transform report and invariant certificate
```

## 附錄 C：最低盲聽資料結構

```text
blind_listening_pack/
  README.md
  public_manifest.json
  rating_template.json
  secret_key.json
  audio/
    sample_<anonymous>.wav
  trajectories/
    sample_<anonymous>.json
```

## 附錄 D：第七篇最低成功條件

- [x] 跨 $\pm\pi$ 的圓周插值正確；
- [x] 原相位、零相位與隨機相位對照；
- [x] 部分及完整相位風格移植；
- [x] $f_0$、振幅與錨相位保持；
- [x] 動態解除包覆與速度重算；
- [x] 盲聽匿名化輸出；
- [x] 客觀指標與相位位移分開報告；
- [x] overlap-add 邊界尖峰修正；
- [x] Transform Schema；
- [x] 二十一項自動測試；
- [ ] 自然語音與多人知覺驗證；
- [ ] 完整殘差保持與產品級聲碼器。

---

**第七篇完。**
