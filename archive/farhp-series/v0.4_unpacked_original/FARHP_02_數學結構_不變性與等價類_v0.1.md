# 基頻錨定相對諧波相位差的數學結構
## 商環面、不變量、等價類、動態幾何與不確定性傳播

**英文題名：** *Mathematical Structure of Fundamental-Anchored Relative Harmonic Phase: Quotient Tori, Invariants, Equivalence Classes, Dynamic Geometry, and Uncertainty Propagation*  

**縮寫：** FARHP  
**中文簡稱：** 基錨相差  
**系列位置：** FARHP 系列第二篇／數學基礎篇  
**作者：** Neo.K（EveMissLab）  
**AI 協作：** Aletheia（GPT-5.6 Thinking）  
**版本：** v0.1  
**日期：** 2026-07-25  
**文件性質：** 理論論文／形式化基礎

---

## 摘要

本文建立「基頻錨定相對諧波相位差」（Fundamental-Anchored Relative Harmonic Phase, FARHP）的數學基礎。系列總篇已將 FARHP 定義為第 $k$ 個諧波相位相對於 $k$ 倍基頻相位的圓周差：

$$
\psi_k
=
\operatorname{wrap}(\phi_k-k\phi_1).
$$

然而，若僅把此式理解為一般實數減法，就會忽略相位的模 $2\pi$ 結構、共同時間平移所形成的群作用、不同表示之間的等價關係、跨框架軌跡的提升問題，以及基頻估計誤差對所有高次諧波座標造成的相關性污染。

本文證明：固定 $K$ 個諧波時，完整相位空間為 $K$ 維環面 $\mathbb T^K$；共同週期平移沿權重向量 $(1,2,\ldots,K)$ 形成一維圓群軌道；FARHP 映射是一個連續滿射群同態，其核恰好是該共同平移軌道。因此：

$$
\mathbb T^K/\iota(\mathbb T)
\cong
\mathbb T^{K-1}.
$$

亦即，FARHP 的自然狀態空間不是歐氏向量空間，而是完整諧波相位空間對共同時間原點自由度取商後得到的 $(K-1)$ 維商環面。本文進一步建立時間平移不變性的精確條件、失諧殘餘項、估計誤差傳播矩陣、圓周與環面距離、遮罩化相位空間、動態軌跡提升、相位速度、繞行數、圓周平均與測地插值。對基頻缺失情形，本文以整數不變量格與 Bézout 錨定提出廣義相對相位構造，指出當可觀測諧波索引的最大公因數大於一時，只能恢復虛擬基本週期，原始基頻相位仍保留有限歧義。

本文亦分析極性反轉、時間反演、聲學串接與波形混合對 FARHP 的作用，並明確區分「相位空間上的群運算」與「真實聲波的線性相加」。最終，本文形成一套可供後續聲學論文、離散編碼論文與工程規格直接採用的形式化語言。

**關鍵詞：** 相位環面、商空間、群作用、相對相位、不變量、圓周統計、諧波模型、誤差傳播、動態相位、語音合成

---

# 0. 研究定位

## 0.1 本文處理什麼

本文處理 FARHP 的純數學與訊號形式問題，包括：

1. 相位應位於何種空間；
2. 共同時間平移形成何種等價關係；
3. FARHP 是否完整描述該等價類；
4. 應如何定義相位距離、平均與插值；
5. 基頻或諧波估計誤差如何傳入 FARHP；
6. 動態相位軌跡如何解除包覆並保持連續；
7. 當基頻不可觀測時，還能建立哪些相位不變量；
8. 極性、時間反演與聲學運算如何作用於 FARHP。

## 0.2 本文暫不處理什麼

本文不直接回答下列經驗問題：

- 人耳是否穩定感知特定 FARHP 差異；
- 哪些相位結構對母音、氣聲、緊聲或說話人辨識最重要；
- 聲道濾波與聲門波形各自貢獻多少 FARHP；
- 哪一種演算法最適合從真實錄音估計 FARHP；
- 離散相位碼本應取八相、十六相或更高解析度。

這些問題分別留給系列第三篇、第四篇及後續技術論文。本文的任務是先確保：後續實驗所操作的對象具有明確且不自相矛盾的數學定義。

## 0.3 核心觀點

本文的核心觀點可濃縮為：

> FARHP 不是把一組絕對相位改寫成另一組絕對相位，而是從完整諧波相位空間中消去共同週期時鐘自由度，留下決定週期內部相對形狀的商空間座標。

---

# 1. 預備定義

## 1.1 相位圓群

定義相位圓群：

$$
\mathbb T
:=
\mathbb R/(2\pi\mathbb Z).
$$

兩個實數 $\alpha,\beta$ 表示同一相位，當且僅當：

$$
\alpha-\beta\in 2\pi\mathbb Z.
$$

以等價類記號表示：

$$
[\alpha]_{2\pi}
=
\alpha+2\pi\mathbb Z.
$$

本文在不致混淆時，直接以 $\alpha\in\mathbb T$ 表示相位等價類。

$\mathbb T$ 是一個緊緻、連通、交換的一維李群。其群運算是模 $2\pi$ 的加法：

$$
[\alpha]+[\beta]
=
[\alpha+\beta].
$$

## 1.2 包覆函數只是座標圖

常用包覆函數為：

$$
\operatorname{wrap}(\alpha)
=
((\alpha+\pi)\bmod 2\pi)-\pi.
$$

其輸出通常取在：

$$
(-\pi,\pi].
$$

但必須注意：$\operatorname{wrap}$ 不是相位本體，只是把圓周等價類選入某個半開區間的座標表示。$-\pi$ 與 $\pi$ 在實數座標上不同，在 $\mathbb T$ 中卻是同一點。

因此，任何依賴 $\operatorname{wrap}$ 邊界的跳躍，都首先應被視為座標圖造成的人工不連續，而不必然是聲音狀態本身的不連續。

## 1.3 $K$ 諧波相位環面

若保留前 $K$ 個諧波，其完整相位狀態為：

$$
\boldsymbol\phi
=
(\phi_1,\phi_2,\ldots,\phi_K)
\in
\mathbb T^K.
$$

定義：

$$
\mathcal P_K
:=
\mathbb T^K.
$$

$\mathcal P_K$ 是 $K$ 維環面，也是 $K$ 個圓群的直積群。

## 1.4 正振幅約定與未定義相位

為避免振幅符號與相位之間的冗餘，本文要求諧波振幅滿足：

$$
A_k\ge 0.
$$

當 $A_k>0$ 時，$\phi_k$ 才是可辨識的相位座標。若 $A_k=0$，則：

$$
0\cdot e^{i\phi_k}
=0
$$

對所有 $\phi_k$ 都成立，因此該相位不可識別。這不是數值缺漏，而是參數化本身的退化。

所以實際 FARHP 狀態必須同時帶有有效性遮罩：

$$
m_k\in\{0,1\},
$$

其中 $m_k=0$ 表示該諧波相位在當前框架中沒有足夠振幅或可靠度，不能被當作有效觀測。

---

# 2. 共同週期平移的群作用

## 2.1 權重嵌入

定義權重向量：

$$
\mathbf h_K
=
(1,2,\ldots,K)^{\mathsf T}.
$$

定義圓群到完整相位環面的嵌入：

$$
\iota_K:\mathbb T\longrightarrow\mathbb T^K,
$$

$$
\iota_K(\theta)
=
(\theta,2\theta,\ldots,K\theta).
$$

由於第一座標就是 $\theta$，$\iota_K$ 是單射。

其像為：

$$
\mathcal G_K
:=
\iota_K(\mathbb T)
=
\left\{
(\theta,2\theta,\ldots,K\theta)
\mid
\theta\in\mathbb T
\right\}.
$$

$\mathcal G_K$ 是 $\mathbb T^K$ 中的一維閉子群。

## 2.2 共同時間原點的改變

對理想諧波訊號：

$$
x(t)
=
\sum_{k=1}^{K}
A_k\cos(k\omega_0 t+\phi_k),
$$

若把時間原點平移 $\tau$，則：

$$
x(t-\tau)
=
\sum_{k=1}^{K}
A_k
\cos
\left(
 k\omega_0 t+\phi_k-k\omega_0\tau
\right).
$$

令：

$$
\theta
=-\omega_0\tau,
$$

則相位向量變成：

$$
\boldsymbol\phi'
=
\boldsymbol\phi+
\iota_K(\theta).
$$

因此，改變共同時間原點會使相位狀態沿著子群 $\mathcal G_K$ 移動。

## 2.3 群作用

定義作用：

$$
\Gamma_K:
\mathbb T\times\mathbb T^K
\longrightarrow
\mathbb T^K,
$$

$$
\Gamma_K(\theta,\boldsymbol\phi)
=
\boldsymbol\phi+
\iota_K(\theta).
$$

此作用滿足：

$$
\Gamma_K(0,\boldsymbol\phi)
=
\boldsymbol\phi,
$$

以及：

$$
\Gamma_K
\left(
\theta_1,
\Gamma_K(\theta_2,\boldsymbol\phi)
\right)
=
\Gamma_K(\theta_1+\theta_2,\boldsymbol\phi).
$$

每個相位狀態的軌道為：

$$
\mathcal O(\boldsymbol\phi)
=
\boldsymbol\phi+
\mathcal G_K.
$$

軌道中的所有點，只差一個共同週期時間原點。

---

# 3. FARHP 映射與商環面主定理

## 3.1 矩陣形式

定義整數矩陣：

$$
B_K
=
\begin{pmatrix}
-2 & 1 & 0 & 0 & \cdots & 0\\
-3 & 0 & 1 & 0 & \cdots & 0\\
-4 & 0 & 0 & 1 & \cdots & 0\\
\vdots & \vdots & \vdots & \vdots & \ddots & \vdots\\
-K & 0 & 0 & 0 & \cdots & 1
\end{pmatrix}
\in
\mathbb Z^{(K-1)\times K}.
$$

其中第 $k-1$ 列對應第 $k$ 個諧波，$k=2,\ldots,K$。

有：

$$
B_K\mathbf h_K
=0.
$$

## 3.2 FARHP 映射

定義：

$$
Q_K:
\mathbb T^K
\longrightarrow
\mathbb T^{K-1},
$$

$$
Q_K(\boldsymbol\phi)
=
B_K\boldsymbol\phi
\pmod{2\pi}.
$$

逐座標寫為：

$$
\boxed{
\psi_k
=
\phi_k-k\phi_1
\pmod{2\pi}
}
\qquad
k=2,\ldots,K.
$$

因此：

$$
Q_K(\boldsymbol\phi)
=
(\psi_2,\psi_3,\ldots,\psi_K).
$$

## 3.3 定理一：FARHP 是完整的共同平移不變量

**定理 1。** $Q_K$ 是連續滿射交換群同態，且：

$$
\ker Q_K
=
\mathcal G_K.
$$

因此：

$$
\boxed{
\mathbb T^K/\mathcal G_K
\cong
\mathbb T^{K-1}
}
$$

且 $Q_K$ 完整分類共同週期平移軌道。

### 證明

首先，由矩陣 $B_K$ 具有整數係數，模 $2\pi$ 的線性作用是良定義的連續群同態。

對任意：

$$
\boldsymbol\psi
=
(\psi_2,\ldots,\psi_K)
\in
\mathbb T^{K-1},
$$

取：

$$
\boldsymbol\phi
=
(0,\psi_2,\ldots,\psi_K).
$$

則：

$$
Q_K(\boldsymbol\phi)
=
\boldsymbol\psi,
$$

故 $Q_K$ 為滿射。

若 $\boldsymbol\phi\in\ker Q_K$，則對所有 $k\ge 2$：

$$
\phi_k-k\phi_1
=0
\pmod{2\pi}.
$$

所以：

$$
\phi_k
=k\phi_1
\pmod{2\pi},
$$

因而：

$$
\boldsymbol\phi
=
\iota_K(\phi_1)
\in
\mathcal G_K.
$$

反之，若：

$$
\boldsymbol\phi
=
\iota_K(\theta),
$$

則：

$$
\phi_k-k\phi_1
=k\theta-k\theta
=0,
$$

故 $\boldsymbol\phi\in\ker Q_K$。

由群同態第一同構定理：

$$
\mathbb T^K/\ker Q_K
\cong
\operatorname{im}Q_K
=
\mathbb T^{K-1}.
$$

證畢。

## 3.4 軌道判別推論

**推論 1。** 對任意 $\boldsymbol\phi,\boldsymbol\chi\in\mathbb T^K$，以下敘述等價：

1. $Q_K(\boldsymbol\phi)=Q_K(\boldsymbol\chi)$；
2. $\boldsymbol\phi-\boldsymbol\chi\in\mathcal G_K$；
3. 存在唯一 $\theta\in\mathbb T$，使得：

$$
\boldsymbol\phi
=
\boldsymbol\chi+
\iota_K(\theta).
$$

所以，兩組完整諧波相位具有相同 FARHP，當且僅當它們只差一個共同週期時間原點。

## 3.5 規範固定與標準代表元

定義截面：

$$
s_K:
\mathbb T^{K-1}
\longrightarrow
\mathbb T^K,
$$

$$
s_K(\boldsymbol\psi)
=
(0,\psi_2,\ldots,\psi_K).
$$

則：

$$
Q_K\circ s_K
=
\operatorname{id}_{\mathbb T^{K-1}}.
$$

每個完整相位狀態都可唯一分解為：

$$
\boxed{
\boldsymbol\phi
=
s_K(Q_K\boldsymbol\phi)
+
\iota_K(\phi_1)
}
$$

亦即：

$$
\text{完整相位}
=
\text{相對形狀}
+
\text{共同週期時鐘}.
$$

把 $\phi_1$ 固定為零，是一種規範選擇；它不代表基頻在物理上真的沒有相位，而是選擇一個方便的軌道代表元。

---

# 4. 時間平移不變性與失諧殘餘

## 4.1 精確不變性

設一般複數諧波分量在時間平移 $\tau$ 後變為：

$$
\phi_k'
=
\phi_k-2\pi f_k\tau.
$$

若：

$$
f_k=kf_1,
$$

則：

$$
\begin{aligned}
\psi_k'
&=
\phi_k'-k\phi_1'\\
&=
\phi_k-2\pi kf_1\tau
-k(\phi_1-2\pi f_1\tau)\\
&=
\phi_k-k\phi_1\\
&=
\psi_k.
\end{aligned}
$$

因此，理想諧波條件下 FARHP 對共同時間平移精確不變。

## 4.2 失諧模型

令：

$$
f_k
=
kf_1+\varepsilon_k.
$$

則時間平移後：

$$
\psi_k'
=
\psi_k-2\pi\varepsilon_k\tau
\pmod{2\pi}.
$$

所以：

$$
\boxed{
\Delta\psi_k
=
-2\pi\varepsilon_k\tau
\pmod{2\pi}
}
$$

這表示 FARHP 的不變性是條件性的：

- 對精確諧波鎖定，完全不變；
- 對局部失諧，產生與失諧量及時間平移成正比的殘餘相位；
- 對明顯非諧波區段，不應宣稱 FARHP 仍具有同樣意義。

## 4.3 圓周誤差界

定義圓周測地距離：

$$
\delta_{\mathbb T}(\alpha,\beta)
=
\left|
\operatorname{wrap}(\alpha-\beta)
\right|.
$$

則：

$$
\delta_{\mathbb T}(\psi_k',\psi_k)
\le
\min
\left
\{
\pi,
2\pi|\varepsilon_k||\tau|
\right\}.
$$

在沒有跨越相位包覆邊界的局部區域中：

$$
\delta_{\mathbb T}(\psi_k',\psi_k)
=
2\pi|\varepsilon_k||\tau|.
$$

## 4.4 近似不變性的工程判準

給定容許相位誤差 $\eta_k\in(0,\pi]$，若：

$$
2\pi|\varepsilon_k||\tau|
\le
\eta_k,
$$

則第 $k$ 座標在該平移尺度下可視為近似不變。

等價地：

$$
|\tau|
\le
\frac{\eta_k}{2\pi|\varepsilon_k|}.
$$

這個界線提供了一個直接工程含義：分析窗口可允許的位移尺度，取決於局部諧波失諧程度。

---

# 5. 相位估計誤差與錨點放大

## 5.1 線性化誤差模型

設真實相位為 $\boldsymbol\phi$，估計相位為：

$$
\widehat{\boldsymbol\phi}
=
\boldsymbol\phi+
\boldsymbol\eta
\pmod{2\pi}.
$$

在局部誤差足夠小、可選擇一致提升的條件下：

$$
\widehat{\boldsymbol\psi}
-
\boldsymbol\psi
\approx
B_K\boldsymbol\eta.
$$

逐座標為：

$$
\boxed{
\Delta\psi_k
\approx
\eta_k-k\eta_1
}
$$

## 5.2 錨點誤差放大

若只考慮基頻相位誤差 $\eta_1$，則：

$$
\Delta\psi_k
\approx
-k\eta_1.
$$

因此，高次諧波會把錨點相位誤差按諧波階數放大。

這意味著：

> 「以基頻為錨」消除了共同時間平移自由度，但也把基頻估計的不確定性共享到所有 FARHP 座標。

所以，FARHP 系統不能只輸出 $\psi_k$，還必須輸出基頻錨定置信度。

## 5.3 協方差傳播

設小誤差向量的協方差矩陣為：

$$
\Sigma_{\phi}
=
\operatorname{Cov}(\boldsymbol\eta).
$$

則線性化後：

$$
\boxed{
\Sigma_{\psi}
=
B_K
\Sigma_{\phi}
B_K^{\mathsf T}
}
$$

若各諧波原始相位估計相互獨立，且：

$$
\Sigma_{\phi}
=
\operatorname{diag}
(\sigma_1^2,\sigma_2^2,\ldots,\sigma_K^2),
$$

則：

$$
\operatorname{Var}(\Delta\psi_k)
=
\sigma_k^2+k^2\sigma_1^2,
$$

且對 $j\neq k$：

$$
\operatorname{Cov}
(\Delta\psi_j,\Delta\psi_k)
=
jk\sigma_1^2.
$$

因此，即使原始諧波相位誤差獨立，經過共同基頻錨定後，各 FARHP 座標也會因共享 $\eta_1$ 而產生正相關。

## 5.4 不應假設座標獨立

若 AI 模型使用逐座標獨立損失：

$$
\mathcal L
=
\sum_{k=2}^{K}
\ell(\widehat\psi_k,\psi_k),
$$

它可能忽略共同錨點誤差造成的協方差結構。

在局部切空間中，可以考慮：

$$
\mathcal L_{\mathrm{cov}}
=
\Delta\widetilde{\boldsymbol\psi}^{\mathsf T}
\left(
\Sigma_{\psi}+\lambda I
\right)^{-1}
\Delta\widetilde{\boldsymbol\psi},
$$

其中 $\Delta\widetilde{\boldsymbol\psi}$ 是選定局部提升後的最短相位差，$\lambda>0$ 用於正則化。

這不是要求所有模型都必須使用 Mahalanobis 損失，而是指出：FARHP 的不確定性原則上不是座標獨立的。

---

# 6. FARHP 狀態空間上的距離

## 6.1 圓周測地距離

對 $\alpha,\beta\in\mathbb T$，定義：

$$
\delta_{\mathbb T}(\alpha,\beta)
=
\left|
\operatorname{Arg}
\left(
e^{i(\alpha-\beta)}
\right)
\right|.
$$

其值域為：

$$
[0,\pi].
$$

此距離等於圓周上兩點之間的最短弧長。

## 6.2 加權環面距離

給定固定正權重：

$$
w_k>0,
$$

以及 $p\ge1$，定義：

$$
\boxed{
 d_{p,\mathbf w}
 (\boldsymbol\psi,\boldsymbol\chi)
=
\left(
\frac{
\sum_{k=2}^{K}
 w_k
\delta_{\mathbb T}(\psi_k,\chi_k)^p
}{
\sum_{k=2}^{K}w_k
}
\right)^{1/p}
}
$$

這是 $\mathbb T^{K-1}$ 上的度量。

常用情形包括：

$$
p=1
$$

的平均絕對圓周距離，以及：

$$
p=2
$$

的均方根環面距離。

## 6.3 緊緻性與完備性

**定理 2。** 對任意有限 $K$、$p\ge1$ 與固定正權重 $\mathbf w$，空間：

$$
(\mathbb T^{K-1},d_{p,\mathbf w})
$$

是緊緻、完備且可分的度量空間。

### 理由

$\mathbb T$ 在測地距離下是緊緻完備空間；有限個緊緻完備空間的加權 $\ell^p$ 直積仍然緊緻且完備。

此結果保證：

- 任意序列都有收斂子序列；
- Cauchy 相位序列不會逃離狀態空間；
- 連續損失函數在緊緻碼本候選集上可取到極值；
- 聚類與量化問題至少具有存在性基礎。

## 6.4 複數弦距

將相位嵌入單位圓：

$$
E(\psi)
=e^{i\psi}
=(\cos\psi,\sin\psi).
$$

定義弦距：

$$
c(\alpha,\beta)
=
\left|
e^{i\alpha}-e^{i\beta}
\right|.
$$

有：

$$
c(\alpha,\beta)
=
2\sin
\left(
\frac{\delta_{\mathbb T}(\alpha,\beta)}{2}
\right).
$$

且：

$$
\frac{2}{\pi}
\delta_{\mathbb T}(\alpha,\beta)
\le
c(\alpha,\beta)
\le
\delta_{\mathbb T}(\alpha,\beta).
$$

因此，弦距與測地距離產生相同拓撲。

平方弦距為：

$$
c^2(\alpha,\beta)
=
2-2\cos(\alpha-\beta).
$$

這正是常見的圓周相位損失。

## 6.5 局部歐氏近似

當：

$$
\delta_{\mathbb T}(\alpha,\beta)
\ll 1,
$$

有：

$$
2-2\cos(\alpha-\beta)
\approx
(\alpha-\beta)^2.
$$

因此歐氏誤差只在局部相位差小、且沒有跨越包覆邊界時才是合理近似。

---

# 7. 遮罩、缺失諧波與可變維度

## 7.1 為什麼不能替缺失相位填零

若某個諧波振幅太低，將其相位強行設為零會混淆兩種完全不同的狀態：

1. 相位真的接近零；
2. 相位不可觀測。

因此資料結構至少應包含：

$$
(\psi_k,m_k,c_k),
$$

其中：

- $\psi_k\in\mathbb T$；
- $m_k\in\{0,1\}$ 是有效性遮罩；
- $c_k\in[0,1]$ 是估計置信度。

## 7.2 固定最大維度表示

實作上可選擇最大諧波數 $K_{\max}$，並把每個框架表示為：

$$
\mathcal X_{K_{\max}}
=
\left(
\mathbb T\times\{0,1\}\times[0,1]
\right)^{K_{\max}-1}.
$$

這避免每個框架使用不同長度張量，同時保留哪些座標是真實可觀測的資訊。

## 7.3 交集距離不是全域度量

對兩個遮罩狀態，可定義只比較共同有效座標的距離：

$$
d_{\cap}(x,y)
=
\left(
\frac{
\sum_k
m_k^{(x)}m_k^{(y)}w_k
\delta_{\mathbb T}(\psi_k^{(x)},\psi_k^{(y)})^p
}{
\sum_k
m_k^{(x)}m_k^{(y)}w_k
}
\right)^{1/p}.
$$

但當共同有效座標集合改變時，$d_{\cap}$ 未必滿足三角不等式；若沒有任何共同有效座標，它甚至未定義。

所以它應稱為「條件比較量」，不能自動稱為全域度量。

## 7.4 帶缺失符號的度量

令：

$$
\overline{\mathbb T}
=
\mathbb T\cup\{\bot\},
$$

其中 $\bot$ 表示相位缺失。

先將圓周距離正規化：

$$
\bar\delta(\alpha,\beta)
=
\frac{
\delta_{\mathbb T}(\alpha,\beta)
}{\pi}
\in[0,1].
$$

選擇缺失成本：

$$
\lambda\in
\left[
\frac12,1
\right].
$$

定義：

$$
\rho_{\lambda}(a,b)
=
\begin{cases}
0,
& a=b=\bot,\\
\lambda,
& \text{恰有一者為 }\bot,\\
\bar\delta(a,b),
& a,b\in\mathbb T.
\end{cases}
$$

由於任意兩個有效相位的最大距離為 $1$，而經由缺失狀態的兩段路徑成本為 $2\lambda\ge1$，$\rho_{\lambda}$ 滿足三角不等式。

因此可在：

$$
\overline{\mathbb T}^{K-1}
$$

上建立真正的加權乘積度量。

## 7.5 樣本依賴權重的限制

若權重由樣本本身決定，例如：

$$
w_k(x,y)
=
c_k^{(x)}c_k^{(y)},
$$

所得比較函數很實用，但未必仍是數學上的度量，因為不同點對使用不同權重，可能破壞三角不等式。

因此本文區分：

- **固定權重度量：** 用於理論、索引與保證；
- **置信度加權相異度：** 用於工程判斷與損失設計。

---

# 8. 動態 FARHP 軌跡

## 8.1 相位路徑

對時間區間：

$$
I=[t_0,t_1],
$$

動態 FARHP 是連續或分段連續映射：

$$
\boldsymbol\Psi:
I\longrightarrow
\mathbb T^{K-1}.
$$

它不只記錄單一框架的相位形狀，而是記錄相位形狀如何隨時間演化。

## 8.2 路徑提升

由於 $I$ 是單連通區間，任意連續圓周路徑：

$$
\psi_k:I\to\mathbb T
$$

在指定初始實數代表元後，都存在唯一連續提升：

$$
\widetilde\psi_k:I\to\mathbb R,
$$

使得：

$$
e^{i\widetilde\psi_k(t)}
=
e^{i\psi_k(t)}.
$$

這就是相位解除包覆的拓撲基礎。

解除包覆不是任意把跳躍加減 $2\pi$，而是在選定初始分支後，尋找與圓周路徑相容的連續實數提升。

## 8.3 動態相位速度

若完整相位路徑有可微提升：

$$
\widetilde\phi_k(t),
$$

定義：

$$
\widetilde\psi_k(t)
=
\widetilde\phi_k(t)-k\widetilde\phi_1(t).
$$

則：

$$
\boxed{
\dot{\widetilde\psi}_k(t)
=
\dot{\widetilde\phi}_k(t)
-k\dot{\widetilde\phi}_1(t)
}
$$

若：

$$
\omega_k(t)
=
\dot{\widetilde\phi}_k(t),
$$

則：

$$
\dot{\widetilde\psi}_k(t)
=
\omega_k(t)-k\omega_1(t).
$$

因此，FARHP 的時間導數直接測量局部瞬時角頻率偏離整數諧波鎖定的程度，以及額外相位形狀變化。

## 8.4 定常波形與形狀變化

若存在共同週期相位 $\theta(t)$ 與固定偏移 $\beta_k$，使：

$$
\widetilde\phi_k(t)
=
k\theta(t)+\beta_k,
$$

則：

$$
\widetilde\psi_k(t)
=
\beta_k-k\beta_1.
$$

若把 $\beta_1=0$ 吸收到 $\theta(t)$ 中，則：

$$
\widetilde\psi_k(t)
=
\beta_k
$$

為常數。

所以理想上：

- 共同音高變化由 $\theta(t)$ 承擔；
- 週期內波形形狀變化由 $\boldsymbol\Psi(t)$ 承擔。

## 8.5 軌跡長度與能量

對絕對連續路徑，定義加權速度：

$$
\|\dot{\boldsymbol\Psi}(t)\|_{p,\mathbf w}
=
\left(
\frac{
\sum_{k=2}^{K}
w_k
|\dot{\widetilde\psi}_k(t)|^p
}{
\sum_{k=2}^{K}w_k
}
\right)^{1/p}.
$$

路徑長度為：

$$
L(\boldsymbol\Psi)
=
\int_{t_0}^{t_1}
\|\dot{\boldsymbol\Psi}(t)\|_{p,\mathbf w}
\,dt.
$$

平方速度能量可定義為：

$$
E(\boldsymbol\Psi)
=
\frac12
\int_{t_0}^{t_1}
\sum_{k=2}^{K}
w_k
|\dot{\widetilde\psi}_k(t)|^2
\,dt.
$$

這些量可用於：

- 懲罰跨框架相位抖動；
- 比較兩種發音的相位動態複雜度；
- 建立平滑生成器；
- 區分穩定音節核心與瞬態過渡。

## 8.6 閉合路徑與繞行數

若：

$$
\psi_k(t_0)=\psi_k(t_1)
\quad\text{於 }\mathbb T,
$$

則其提升可能滿足：

$$
\widetilde\psi_k(t_1)
-
\widetilde\psi_k(t_0)
=
2\pi n_k,
$$

其中：

$$
n_k\in\mathbb Z.
$$

$n_k$ 是第 $k$ 個 FARHP 座標的繞行數。完整閉合軌跡的拓撲類可由：

$$
\mathbf n
=(n_2,\ldots,n_K)
\in
\mathbb Z^{K-1}
$$

表示。

對一般短音節，繞行數未必具有直接知覺意義；但在週期調變、合成循環或長時相位動畫中，它可區分局部看似相同、全域卻具有不同拓撲纏繞的軌跡。

---

# 9. 平均、統計與插值

## 9.1 圓周平均

對樣本：

$$
\psi^{(1)},\ldots,\psi^{(N)}
\in\mathbb T,
$$

以及權重 $a_n\ge0$，定義複數合量：

$$
R
=
\sum_{n=1}^{N}
a_n e^{i\psi^{(n)}}.
$$

若 $R\neq0$，圓周平均為：

$$
\bar\psi
=
\operatorname{Arg}(R).
$$

正規化合量長度：

$$
r
=
\frac{|R|}{\sum_n a_n}
\in[0,1]
$$

可用作集中程度：

- $r\approx1$：相位高度集中；
- $r\approx0$：相位分散或多峰對消。

當 $R=0$ 時，平均方向不唯一，不能強行輸出零相位。

## 9.2 環面平均

對 FARHP 向量，可逐座標計算：

$$
\bar\psi_k
=
\operatorname{Arg}
\left(
\sum_{n=1}^{N}
a_n e^{i\psi_k^{(n)}}
\right).
$$

同時保留每個座標的集中度 $r_k$。

低 $r_k$ 可能表示：

- 該諧波相位本來就不穩定；
- 樣本包含多個不同發音類；
- 存在極性或對齊混合；
- 相位估計噪聲過高；
- 使用單一平均代表多峰分布並不適當。

## 9.3 最短測地插值

對 $\alpha,\beta\in\mathbb T$，令：

$$
\Delta
=
\operatorname{wrap}(\beta-\alpha).
$$

當：

$$
|\Delta|<\pi,
$$

最短測地插值為：

$$
\boxed{
\gamma(\lambda)
=
\operatorname{wrap}
(\alpha+\lambda\Delta)
}
$$

其中：

$$
\lambda\in[0,1].
$$

若：

$$
|\Delta|=\pi,
$$

則順時針與逆時針兩條最短弧同長，插值不唯一，必須由上下文、前一框架速度或額外方向規則選擇。

## 9.4 環面插值

FARHP 向量的插值可逐座標進行：

$$
\gamma_k(\lambda)
=
\operatorname{wrap}
\left(
\psi_k^{(a)}
+
\lambda
\operatorname{wrap}
(\psi_k^{(b)}-\psi_k^{(a)})
\right).
$$

但若多個座標位於對跖點，整體最短測地線可能不唯一。實作系統應明確記錄所選分支，而不是把不唯一性隱藏在函式庫預設值中。

## 9.5 複數線性插值的退化

常見作法是：

$$
z(\lambda)
=
(1-\lambda)e^{i\alpha}
+
\lambda e^{i\beta},
$$

再正規化：

$$
\gamma(\lambda)
=
\operatorname{Arg}z(\lambda).
$$

若：

$$
\beta-\alpha=\pi
$$

且：

$$
\lambda=\frac12,
$$

則：

$$
z(\lambda)=0,
$$

相位未定義。因此，任何複數插值實作都必須處理對跖退化。

---

# 10. 基頻缺失時的廣義整數相位不變量

## 10.1 問題

標準 FARHP 需要觀測第一諧波相位 $\phi_1$。但在真實錄音中，基頻分量可能：

- 被高通濾波削弱；
- 低於噪聲底；
- 因麥克風或聲道響應而不可可靠估計；
- 出現「缺失基頻」知覺，即人耳能感知基頻，但頻譜中第一諧波不明顯。

因此需要研究：沒有 $\phi_1$ 時，哪些共同時間平移不變量仍可構造。

## 10.2 任意諧波索引集合

設可觀測諧波索引為：

$$
H
=
(h_1,h_2,\ldots,h_m)^{\mathsf T}
\in
\mathbb N^m.
$$

對應相位向量：

$$
\boldsymbol\phi_H
=
(\phi_{h_1},\ldots,\phi_{h_m})
\in
\mathbb T^m.
$$

共同時間平移作用為：

$$
\boldsymbol\phi_H
\longmapsto
\boldsymbol\phi_H+H\theta.
$$

## 10.3 整數不變量格

定義：

$$
L_H
=
\left\{
\mathbf a\in\mathbb Z^m
\mid
\mathbf a^{\mathsf T}H=0
\right\}.
$$

對任意 $\mathbf a\in L_H$，定義：

$$
I_{\mathbf a}(\boldsymbol\phi_H)
=
\mathbf a^{\mathsf T}
\boldsymbol\phi_H
\pmod{2\pi}.
$$

則：

$$
\begin{aligned}
I_{\mathbf a}
(\boldsymbol\phi_H+H\theta)
&=
\mathbf a^{\mathsf T}
\boldsymbol\phi_H
+
\mathbf a^{\mathsf T}H\theta\\
&=
I_{\mathbf a}(\boldsymbol\phi_H).
\end{aligned}
$$

所以 $L_H$ 中每個整數向量都生成一個共同時間平移不變量。

## 10.4 成對不變量

對任意兩個可觀測索引 $h_a,h_b$，有簡單不變量：

$$
\boxed{
\chi_{a,b}
=
 h_b\phi_{h_a}
-
 h_a\phi_{h_b}
\pmod{2\pi}
}
$$

因為係數向量在第 $a$ 座標取 $h_b$、第 $b$ 座標取 $-h_a$，其與 $H$ 的內積為零。

若 $h_a=1$、$h_b=k$，則：

$$
\chi_{a,b}
=
k\phi_1-
\phi_k
=
-\psi_k.
$$

因此標準 FARHP 是一般整數相位不變量的一個特別基底。

## 10.5 最大公因數與虛擬基本週期

令：

$$
g
=
\gcd(h_1,\ldots,h_m),
$$

並定義原始索引向量：

$$
H'
=
\frac{1}{g}H.
$$

$H'$ 的座標最大公因數為一。

由於圓群上的乘 $g$ 映射是滿射，$H\theta$ 與 $H'\theta'$ 產生相同軌道子群。因此商空間仍然由原始向量 $H'$ 決定。

但物理上，若所有觀測諧波索引都有共同因數 $g>1$，則只能建立以：

$$
g f_0
$$

為局部時鐘的虛擬錨。原始基頻週期內仍保留 $g$ 重相位歧義。

例如，只觀測第二與第四諧波時：

$$
H=(2,4),
$$

其原始向量為：

$$
H'=(1,2).
$$

系統可建立以 $2f_0$ 為基礎的相對相位，但不能只憑這兩個分量唯一決定原始 $f_0$ 週期中的前半週或後半週。

## 10.6 Bézout 合成錨

因為：

$$
\gcd(H'_1,\ldots,H'_m)=1,
$$

存在整數向量：

$$
\mathbf c\in\mathbb Z^m
$$

使：

$$
\mathbf c^{\mathsf T}H'=1.
$$

定義合成錨：

$$
\alpha_H
=
\mathbf c^{\mathsf T}
\boldsymbol\phi_H
\pmod{2\pi}.
$$

在作用：

$$
\boldsymbol\phi_H
\mapsto
\boldsymbol\phi_H+H'\theta
$$

下：

$$
\alpha_H
\mapsto
\alpha_H+\theta.
$$

所以可定義廣義錨定座標：

$$
\psi_{H,j}
=
\phi_{h_j}
-H'_j\alpha_H
\pmod{2\pi}.
$$

這提供了在第一諧波缺失時的整數合成錨。

## 10.7 合成錨並非唯一

Bézout 向量 $\mathbf c$ 通常不唯一。不同 $\mathbf c$ 會產生不同座標表示，但它們描述同一商空間。

因此：

- 商空間本體是座標無關的；
- 合成錨是規範選擇；
- 工程規格必須記錄使用哪一組 Bézout 係數；
- 比較不同系統時，應先做座標轉換，不能直接比較數值欄位。

## 10.8 廣義商空間定理

**定理 3。** 對任意非零整數索引向量 $H\in\mathbb Z^m$，令 $H'=H/\gcd(H)$。共同平移子群：

$$
\mathcal G_H
=
\{H'\theta:\theta\in\mathbb T\}
$$

是一維閉子群，且：

$$
\mathbb T^m/\mathcal G_H
\cong
\mathbb T^{m-1}.
$$

任一整數格基底：

$$
\mathbf a_1,\ldots,\mathbf a_{m-1}
\in L_H
$$

若構成原始商格基底，即可建立完整的相位不變量座標。

此結論可透過整數矩陣的 Smith 正規形或原始整數向量可擴張為 $\mathbb Z^m$ 基底來證明。

---

# 11. 離散對稱：極性與時間反演

## 11.1 波形極性反轉

把實訊號乘以 $-1$：

$$
x(t)
\longmapsto
-x(t)
$$

等價於每個非零諧波相位都加上 $\pi$：

$$
\phi_k
\longmapsto
\phi_k+\pi.
$$

因此：

$$
\begin{aligned}
\psi_k'
&=
(\phi_k+\pi)
-k(\phi_1+\pi)\\
&=
\psi_k+(1-k)\pi
\pmod{2\pi}.
\end{aligned}
$$

所以極性作用在 FARHP 空間上為：

$$
\boxed{
\mathfrak P_K(\psi_k)
=
\psi_k+(1-k)\pi
}
$$

進一步：

- 若 $k$ 為奇數，$1-k$ 為偶數，故 $\psi_k$ 不變；
- 若 $k$ 為偶數，$1-k$ 為奇數，故 $\psi_k$ 增加 $\pi$。

亦即，波形極性反轉只翻轉偶數諧波的 FARHP 座標。

## 11.2 極性作用是對合

有：

$$
\mathfrak P_K^2
=
\operatorname{id}.
$$

因此它是一個二階離散對稱。

若應用需要保留聲門極性與波形方向，則不應消除此作用。若應用只關心極性無關的發音類型，可另定義：

$$
d_{\mathrm{pol}}(\psi,\chi)
=
\min
\left\{
 d(\psi,\chi),
 d(\mathfrak P_K\psi,\chi)
\right\}.
$$

這等於再對極性群 $\mathbb Z_2$ 取商。

## 11.3 時間反演

對實餘弦諧波模型，時間反演：

$$
x(t)
\longmapsto
x(-t)
$$

使相位近似變為：

$$
\phi_k
\longmapsto
-\phi_k.
$$

因此：

$$
\boxed{
\psi_k
\longmapsto
-\psi_k
}
$$

時間反演在 FARHP 環面上是取逆映射。

它同樣是對合及等距映射：

$$
\mathfrak R_K^2
=
\operatorname{id}.
$$

## 11.4 半週期平移不是極性反轉

把週期訊號平移半個基頻週期：

$$
\tau
=
\frac{T_0}{2}
$$

會使第 $k$ 諧波相位增加：

$$
k\pi.
$$

這屬於共同時間平移軌道，所以 FARHP 不變。

但極性反轉使所有諧波都增加同一個 $\pi$，兩者對偶次諧波的作用不同。因此：

$$
\text{半週期平移}
\neq
\text{波形乘以 }-1.
$$

FARHP 能區分這兩種變換。

---

# 12. 群運算、聲學串接與波形混合

## 12.1 FARHP 空間的群結構

因為：

$$
\mathbb T^{K-1}
$$

是交換群，所以兩個 FARHP 狀態可做座標加法：

$$
(\boldsymbol\psi+\boldsymbol\chi)_k
=
\psi_k+\chi_k
\pmod{2\pi}.
$$

其單位元為：

$$
\mathbf 0
=(0,\ldots,0),
$$

逆元為：

$$
-\boldsymbol\psi.
$$

但這個群加法不能被直接解釋成「兩段聲波相加」。

## 12.2 複數頻率響應串接

若在相同諧波頻率上，複數頻譜因串接而相乘：

$$
X_k
=S_kH_k,
$$

則相位相加：

$$
\phi_k^{(X)}
=
\phi_k^{(S)}
+
\phi_k^{(H)}.
$$

由 $Q_K$ 是群同態：

$$
\boxed{
Q_K
(\boldsymbol\phi^{(S)}+
 \boldsymbol\phi^{(H)})
=
Q_K(\boldsymbol\phi^{(S)})
+
Q_K(\boldsymbol\phi^{(H)})
}
$$

所以在理想對齊的複數乘法模型下，輸出 FARHP 可分解為來源與濾波器相對相位項之和。

這一點也表明：觀測到的語音 FARHP 不必然只屬於聲門源；聲道與錄音系統的非線性相位響應也可能貢獻 FARHP。

## 12.3 波形線性混合不是相位加法

若：

$$
X_k
=S_k+H_k,
$$

則：

$$
\arg(X_k)
=
\arg(S_k+H_k)
$$

一般不等於：

$$
\arg S_k+
\arg H_k.
$$

所以：

$$
Q_K
\left(
\arg(\mathbf S+
\mathbf H)
\right)
\neq
Q_K(\arg\mathbf S)
+
Q_K(\arg\mathbf H)
$$

通常成立。

因此必須區分：

- 複數傳遞函數的乘法；
- 相位環面上的群加法；
- 真實聲波或頻譜的線性疊加。

三者不是同一種運算。

---

# 13. FARHP 的資訊分解意義

## 13.1 完整相位資訊的分解

由標準截面分解：

$$
\boldsymbol\phi
=
s_K(\boldsymbol\psi)
+
\iota_K(\phi_1),
$$

完整相位資訊可拆成：

1. 一個共同週期相位 $\phi_1\in\mathbb T$；
2. 一個相對相位形狀 $\boldsymbol\psi\in\mathbb T^{K-1}$。

因此，在沒有振幅退化與索引錯配時：

$$
\mathbb T^K
\cong
\mathbb T
\times
\mathbb T^{K-1}
$$

作為此特定截面下的群與拓撲分解。

## 13.2 被消去的是座標自由度，不是物理時間

FARHP 消去的是「在單一局部週期中，選哪個時間點作為相位零點」的自由度。它沒有消除：

- 基頻值 $f_0$；
- 音高軌跡；
- 音節時長；
- 跨框架絕對時間；
- 聲調輪廓；
- 振幅包絡；
- 語音事件順序。

所以 FARHP 的時間平移不變性不能被誤讀為「聲音不再需要時間」。

## 13.3 維度降低

完整 $K$ 諧波相位具有 $K$ 個圓周自由度。共同週期平移佔一個自由度，因此商空間有：

$$
K-1
$$

個圓周自由度。

這不是一般線性降維，而是精確消除已知群作用所形成的冗餘自由度。

## 13.4 最大不變量

定理一意味著 $Q_K$ 是共同平移作用下的最大不變量：任何只依賴軌道、而不依賴軌道內代表元的函數：

$$
F:\mathbb T^K\to Y
$$

若滿足：

$$
F(\boldsymbol\phi+
\iota_K(\theta))
=
F(\boldsymbol\phi)
$$

則存在函數：

$$
\widetilde F:
\mathbb T^{K-1}
\to Y
$$

使：

$$
F
=
\widetilde F\circ Q_K.
$$

亦即，任何共同時間平移不變的相位特徵，原則上都可以視為 FARHP 的函數。

---

# 14. 計算表示與數值守則

## 14.1 不直接回歸包覆角度

模型若直接回歸：

$$
\psi_k\in(-\pi,\pi],
$$

會在 $-\pi$ 與 $\pi$ 附近產生人工大誤差。

建議主要表示為：

$$
\mathbf u_k
=
(\cos\psi_k,
 \sin\psi_k).
$$

並要求：

$$
\|\mathbf u_k\|_2
\approx1.
$$

## 14.2 單位圓投影

若模型輸出：

$$
\widehat{\mathbf v}_k
\in\mathbb R^2,
$$

可投影為：

$$
\widehat{\mathbf u}_k
=
\frac{
\widehat{\mathbf v}_k
}{
\|\widehat{\mathbf v}_k\|_2+\epsilon
}.
$$

但當：

$$
\|\widehat{\mathbf v}_k\|_2
\approx0,
$$

方向高度不穩定。此時應降低置信度，而不是把任意方向當作可靠相位。

## 14.3 相位差計算

兩個角度的最短差應計算為：

$$
\Delta_k
=
\operatorname{atan2}
\left(
\sin(\widehat\psi_k-
\psi_k),
\cos(\widehat\psi_k-
\psi_k)
\right).
$$

而不是直接使用：

$$
\widehat\psi_k-
\psi_k.
$$

## 14.4 諧波索引不可省略

FARHP 座標不是可任意排列的無名向量。每一座標必須攜帶諧波索引 $k$，因為：

$$
\psi_k
=
\phi_k-k\phi_1
$$

中的係數依賴 $k$。

因此資料格式至少需要：

```yaml
phase_coordinate:
  harmonic_index: 7
  cos: 0.382
  sin: -0.924
  valid: true
  confidence: 0.91
```

不能只儲存無索引的浮點陣列，除非規格已固定且外部明確知道第幾欄對應哪個 $k$。

## 14.5 解除包覆需要連續性條件

離散框架的相位解除包覆通常假設相鄰框架變化不超過 $\pi$，或藉由預測模型選擇最合理分支。若真實相位變化過快、框架間隔過大或估計噪聲過高，單純最近鄰解除包覆可能選錯整數圈數。

因此應同時使用：

- 較高時間解析度；
- 相位速度先驗；
- 諧波追蹤身份；
- 錨點置信度；
- 瞬態與無聲邊界重置規則。

---

# 15. 形式命題與可檢驗推論

## 命題 M1：商環面命題

在固定有效諧波數 $K$、振幅非零且諧波索引正確的條件下，FARHP 完整表示完整諧波相位對共同週期時間平移取商後的等價類。

此命題已由定理一形式證明。

## 命題 M2：精確不變性命題

若所有諧波頻率滿足：

$$
f_k=kf_1,
$$

則 FARHP 對任意共同時間平移精確不變。

## 命題 M3：失諧線性殘餘命題

局部無包覆條件下，時間平移造成的 FARHP 偏差滿足：

$$
\Delta\psi_k
=
-2\pi(f_k-kf_1)\tau.
$$

此命題可用人工失諧諧波訊號直接驗證。

## 命題 M4：錨點相關誤差命題

若原始各諧波相位估計誤差獨立，FARHP 座標誤差仍因共享基頻錨點而相關，且：

$$
\operatorname{Cov}
(\Delta\psi_j,\Delta\psi_k)
=
jk\sigma_1^2.
$$

## 命題 M5：極性奇偶命題

波形極性反轉使奇數諧波 FARHP 不變，使偶數諧波 FARHP 增加 $\pi$。

此命題可作為極性偵測與資料對齊測試。

## 命題 M6：缺失基頻不變量命題

即使第一諧波不可觀測，只要至少有兩個可靠諧波，仍可透過整數不變量格構造共同時間平移不變特徵；但若所有索引最大公因數大於一，原始基頻相位保留有限歧義。

## 命題 M7：平均退化命題

若某一 FARHP 座標的複數合量為零，則其單一圓周平均方向未定義。任何強制輸出的平均角都屬額外規則，而非資料本身決定。

---

# 16. 與第三篇聲學論文的接口

本篇完成後，第三篇不必再重新證明 FARHP 的商空間結構，而可以直接研究下列問題。

## 16.1 聲源與聲道的相位分解

由群同態性可知，線性時不變濾波在諧波頻點上的相位貢獻會加到 FARHP。第三篇需要判定：

$$
\boldsymbol\Psi_{\mathrm{observed}}
=
\boldsymbol\Psi_{\mathrm{source}}
+
\boldsymbol\Psi_{\mathrm{filter}}
+
\boldsymbol\Psi_{\mathrm{measurement}}
$$

在何種近似下成立，以及能否被辨識。

## 16.2 哪些座標具有知覺穩定性

數學上每個 $\psi_k$ 都是合法座標，但聲學上不代表每個座標都：

- 可可靠估計；
- 可被人耳感知；
- 對不同說話人穩定；
- 對錄音設備穩健；
- 值得被符號語言離散化。

第三篇必須以知覺與聲學證據建立權重，而不能由數學對稱性直接推出。

## 16.3 有聲—無聲邊界

本篇已證明零振幅時相位未定義。第三篇需要進一步定義：

- 何種週期性門檻啟用 FARHP；
- 擦音與送氣如何交給殘差層；
- 爆破瞬間如何使用事件模型；
- 相位軌跡在無聲區段是否重置或保持潛在狀態。

## 16.4 聲調與相位動態

本篇區分共同週期時鐘與相對形狀軌跡。第三篇需回答：

- 華語聲調主要由何種 $f_0(t)$ 軌跡表示；
- 聲調變化是否伴隨系統性的 FARHP 變化；
- FARHP 是否可在音高正規化後描述額外音色與聲源差異。

---

# 17. 限制與未解問題

## 17.1 商空間正確不等於聲學效益顯著

本文證明 FARHP 是共同時間平移作用的完整不變量，但沒有證明它一定比其他相位表示更適合所有語音任務。

數學上的自然性，只能證明表示沒有任意保留共同時間原點；不能單獨證明其感知價值、壓縮效率或模型性能。

## 17.2 諧波身份可能交換

真實語音中的峰值追蹤可能發生：

- 諧波漏失；
- 峰值錯配；
- 基頻倍頻或半頻錯誤；
- 共振峰附近的幅相干擾；
- 跨框架索引身份交換。

一旦 $k$ 的身份錯誤，$\phi_k-k\phi_1$ 的數學計算雖仍可執行，語義卻已錯位。

## 17.3 圓周平均可能遮蔽多峰結構

兩群相位若位於相反方向，平均合量可能接近零。此時使用單一平均會抹去真實的雙峰或多峰分布。後續碼本應考慮圓周混合模型，而不是只使用一個中心。

## 17.4 基頻相位未必是最可靠單一錨

第一諧波可能比某些高次諧波更弱。標準 FARHP 的理論優勢是座標簡單、商空間透明；工程上卻可能需要：

- 多諧波合成錨；
- 貝葉斯錨點估計；
- 以整數不變量直接建模；
- 對基頻候選進行多假設追蹤。

這些方法仍應保持與本篇商空間結構相容。

## 17.5 廣義 Bézout 錨可能放大噪聲

合成錨：

$$
\alpha_H
=
\mathbf c^{\mathsf T}\boldsymbol\phi_H
$$

若 Bézout 係數絕對值很大，會放大相位估計誤差。因此應在所有可行整數解中，尋找低範數、低方差或高可靠度的係數，而不是任取一組解。

## 17.6 拓撲軌跡不等於發音語義

繞行數與測地長度是合法數學量，但是否對人類發音、AI 語言或符號語義具有價值，必須由後續研究驗證，不能因為拓撲結構存在就自動賦予語義。

---

# 18. 結論

本文把 FARHP 從一條相位差公式提升為完整的商空間理論。

固定 $K$ 個諧波時，完整相位狀態位於：

$$
\mathbb T^K.
$$

共同週期時間原點的改變沿：

$$
\iota_K(\theta)
=
(\theta,2\theta,\ldots,K\theta)
$$

形成一維圓群軌道。FARHP 映射：

$$
Q_K(\boldsymbol\phi)
=
(\phi_2-2\phi_1,
 \ldots,
 \phi_K-K\phi_1)
\pmod{2\pi}
$$

的核恰好等於該軌道子群，因此：

$$
\boxed{
\mathbb T^K/
\iota_K(\mathbb T)
\cong
\mathbb T^{K-1}
}
$$

這給出 FARHP 最核心的本體位置：

> 它是完整諧波相位在消除共同週期時鐘自由度後的自然座標。

本文同時得到幾個對後續研究關鍵的結論：

1. FARHP 的不變性依賴諧波鎖定，失諧會留下可量化殘餘；
2. 基頻錨點誤差會按諧波階數放大，並在所有座標間造成相關誤差；
3. 相位比較必須使用圓周或環面距離，不能直接使用普通實數差；
4. 零振幅與低可靠度相位必須以遮罩表示，不能填入任意角度；
5. 動態 FARHP 是環面上的路徑，解除包覆是路徑提升問題；
6. 基頻缺失時，仍可由整數不變量格建立廣義相位座標；
7. 極性反轉、時間反演與聲學串接在 FARHP 空間中具有明確作用；
8. 相位群加法不等於聲波線性混合。

因此，FARHP 後續系列可以在一個已封閉的數學底座上繼續發展。第三篇將把本篇的抽象結構帶回聲學與語音學，研究哪些環面座標真正對應可估計、可知覺、可生成的發音差異。

系列目前的推進關係為：

$$
\boxed{
\text{總篇}
\rightarrow
\text{商環面數學}
\rightarrow
\text{聲學邊界}
\rightarrow
\text{離散表示}
\rightarrow
\text{技術實作}
}
$$

---

# 參考文獻

[1] I. Saratxaga, I. Hernáez, D. Erro, and J. Sanchez, “Simple Representation of Signal Phase for Harmonic Speech Models,” *Electronics Letters*, 2009.

[2] I. Saratxaga, I. Hernáez, I. Odriozola, E. Navas, I. Luengo, and D. Erro, “Using Harmonic Phase Information to Improve ASR Rate,” *INTERSPEECH 2010*, DOI: 10.21437/Interspeech.2010-372.

[3] I. Saratxaga, I. Hernaez, M. Pucher, E. Navas, and I. Sainz, “Perceptual Importance of the Phase Related Information in Speech,” *INTERSPEECH 2012*, DOI: 10.21437/Interspeech.2012-411.

[4] P. Mowlaee, R. Saeidi, and Y. Stylianou, “Phase Importance in Speech Processing Applications,” *INTERSPEECH 2014*.

[5] K. V. Mardia and P. E. Jupp, *Directional Statistics*, Wiley, 2000.

[6] N. I. Fisher, *Statistical Analysis of Circular Data*, Cambridge University Press, 1993.

[7] A. V. Oppenheim and R. W. Schafer, *Discrete-Time Signal Processing*, Pearson.

[8] J. M. Lee, *Introduction to Topological Manifolds*, Springer.

[9] J. M. Lee, *Introduction to Smooth Manifolds*, Springer.

[10] E. M. Stein and R. Shakarchi, *Fourier Analysis: An Introduction*, Princeton University Press.

[11] S. Lang, *Algebra*, Springer；關於有限生成阿貝爾群、整數格與 Smith 正規形的標準背景。

---

# 附錄 A：主映射的最小機器規格

```yaml
farhp_math_spec:
  version: 0.1
  phase_domain: circle_R_mod_2piZ

  harmonic_phase_space:
    K: integer_ge_2
    domain: torus_K
    harmonic_indices: [1, 2, ..., K]

  gauge_action:
    parameter_domain: circle
    action: phi_k <- phi_k + k * theta
    interpretation: common_period_time_origin

  quotient_map:
    name: Q_K
    output_dimension: K_minus_1
    coordinate: psi_k = wrap(phi_k - k * phi_1)
    kernel: weighted_circle_subgroup

  representation:
    primary:
      - cos_psi_k
      - sin_psi_k
    auxiliary:
      - valid_mask
      - confidence
      - harmonic_index

  distance:
    circle: abs(atan2(sin(delta), cos(delta)))
    torus: weighted_lp_product

  uncertainty:
    linear_map: B_K
    covariance: Sigma_psi = B_K * Sigma_phi * transpose(B_K)

  dynamic:
    path_space: continuous_paths_on_torus
    unwrapping: path_lift_with_initial_branch
    derivative: dpsi_k = dphi_k - k * dphi_1
```

---

# 附錄 B：核心矩陣範例

當：

$$
K=5,
$$

有：

$$
\mathbf h_5
=
\begin{pmatrix}
1\\2\\3\\4\\5
\end{pmatrix},
$$

以及：

$$
B_5
=
\begin{pmatrix}
-2&1&0&0&0\\
-3&0&1&0&0\\
-4&0&0&1&0\\
-5&0&0&0&1
\end{pmatrix}.
$$

直接驗證：

$$
B_5\mathbf h_5
=
\begin{pmatrix}
0\\0\\0\\0
\end{pmatrix}.
$$

FARHP 座標為：

$$
\begin{pmatrix}
\psi_2\\
\psi_3\\
\psi_4\\
\psi_5
\end{pmatrix}
=
B_5
\begin{pmatrix}
\phi_1\\
\phi_2\\
\phi_3\\
\phi_4\\
\phi_5
\end{pmatrix}
\pmod{2\pi}.
$$

若完整相位估計誤差協方差為對角矩陣：

$$
\Sigma_{\phi}
=
\operatorname{diag}
(\sigma_1^2,
 \sigma_2^2,
 \sigma_3^2,
 \sigma_4^2,
 \sigma_5^2),
$$

則 FARHP 誤差協方差為：

$$
\Sigma_{\psi}
=
\begin{pmatrix}
\sigma_2^2+4\sigma_1^2
&6\sigma_1^2
&8\sigma_1^2
&10\sigma_1^2\\
6\sigma_1^2
&\sigma_3^2+9\sigma_1^2
&12\sigma_1^2
&15\sigma_1^2\\
8\sigma_1^2
&12\sigma_1^2
&\sigma_4^2+16\sigma_1^2
&20\sigma_1^2\\
10\sigma_1^2
&15\sigma_1^2
&20\sigma_1^2
&\sigma_5^2+25\sigma_1^2
\end{pmatrix}.
$$

此矩陣清楚顯示：基頻錨點不確定性會形成跨諧波的共享相關結構。

---

# 附錄 C：後續論文必須沿用的符號

| 符號 | 定義 |
|---|---|
| $\mathbb T$ | 相位圓群 $\mathbb R/(2\pi\mathbb Z)$ |
| $\mathcal P_K$ | 完整 $K$ 諧波相位環面 $\mathbb T^K$ |
| $\mathbf h_K$ | 諧波權重向量 $(1,2,\ldots,K)^{\mathsf T}$ |
| $\iota_K$ | 共同週期相位嵌入 |
| $\mathcal G_K$ | 共同週期平移子群 |
| $B_K$ | FARHP 整數差分矩陣 |
| $Q_K$ | 商映射／FARHP 映射 |
| $\boldsymbol\psi$ | FARHP 狀態 |
| $m_k$ | 相位有效性遮罩 |
| $c_k$ | 相位估計置信度 |
| $\delta_{\mathbb T}$ | 圓周測地距離 |
| $d_{p,\mathbf w}$ | 加權環面距離 |
| $L_H$ | 廣義整數相位不變量格 |
| $\mathfrak P_K$ | 極性反轉作用 |
| $\mathfrak R_K$ | 時間反演作用 |

