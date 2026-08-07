# 基錨相差的離散編碼、相位碼本與 AI 可學習表示
## 從相位環面量化、可靠度遮罩到 FARHP-Spec-v0.1

**英文題名：** *Discrete Encoding, Phase Codebooks, and AI-Learnable Representations of Fundamental-Anchored Relative Harmonic Phase: From Torus Quantization and Reliability Masks to FARHP-Spec-v0.1*  

**縮寫：** FARHP  
**中文簡稱：** 基錨相差  
**系列位置：** FARHP 系列第四篇／理論閉合與工程交接篇  
**作者：** Neo.K（EveMissLab）  
**AI 協作：** Aletheia（GPT-5.6 Thinking）  
**版本：** v0.1  
**日期：** 2026-07-26  
**文件性質：** 理論論文／表示規格／碼本設計／工程前置規範

---

## 摘要

本文完成「基頻錨定相對諧波相位差」（Fundamental-Anchored Relative Harmonic Phase, FARHP）由連續數學物件轉換為可儲存、可傳輸、可學習、可重建與可書寫之離散表示的理論閉合。系列第二篇已證明，固定 $K$ 個諧波時，FARHP 的自然狀態空間是完整相位環面對共同週期平移群作用取商所得的 $(K-1)$ 維環面；第三篇則證明，觀測 FARHP 是聲門源、聲道、輻射與量測鏈相對相位貢獻的合成，且其聲學與知覺效益高度依賴音類、基頻、可靠度與任務。由此，FARHP 的離散化不能被簡化為對每個角度做無條件均勻切割。

本文提出三級表示架構。第一級是以單位圓嵌入表示每個相位座標：

$$
E(\psi_k)
=
(\cos\psi_k,\sin\psi_k),
$$

避免 $-\pi$ 與 $\pi$ 邊界造成的虛假不連續。第二級是多解析度圓周標量量化，允許依諧波階數、可靠度與聲學適用度在 $M\in\{8,16,32,64\}$ 等解析度間選擇。第三級是以加權環面距離為失真的聯合向量碼本，使相互關聯的多諧波相位形狀可被單一或分層 token 表示。

本文進一步建立：一、`FARHP-Y` 與 `FARHP-G` 雙軌碼本，分別表示觀測輸出相位與逆濾波聲門相位估計；二、音類、$f_0$ 區間、適用門控 $\Gamma$、說話條件與量測域的條件化碼本；三、缺失諧波遮罩、相位置信度、錨點置信度、碼本外距離與重建不確定性的共同封裝；四、靜態 token、差分 token、關鍵幀及殘差修正所構成的動態編碼；五、供神經網路使用的連續頭、離散頭、混合頭與 VQ 類碼本學習接口；六、JSON、CBOR、神經張量與字形附標之間的同構資料層。

本文提出「率—聲學失真—知覺失真—拓撲一致性—穩健性」五重目標，並明確拒絕以單一重建均方誤差決定碼本優劣。本文也給出 FARHP-Spec-v0.1 的最低規格：任何合規實作都必須保存諧波索引、相位表示域、錨點、遮罩、置信度、碼本識別碼、條件域、極性政策及版本資訊；不得以數值零代替缺失相位，也不得把 `FARHP-G` 標示為生理真值。

至此，FARHP 系列完成四篇理論基礎的閉合：總體定義、商環面數學、聲學與知覺邊界，以及離散表示與 AI 接口。下一篇可正式進入分析—編碼—修改—重建的技術架構與 Python 原型。

**關鍵詞：** 相位量化、環面碼本、圓周統計、向量量化、離散表示、神經音訊、相位 token、可靠度遮罩、語音合成、FARHP-Spec

---

# 0. 研究定位

## 0.1 本文要解決的問題

FARHP 的連續狀態為：

$$
\boldsymbol\psi
=
(\psi_2,\psi_3,\ldots,\psi_K)
\in
\mathbb T^{K-1},
$$

其中：

$$
\mathbb T
=
\mathbb R/(2\pi\mathbb Z).
$$

此表示在數學上完整，卻仍不足以直接形成工程系統。實際系統至少必須回答：

1. 相位應以角度、複數數、正弦—餘弦對，還是離散索引保存？
2. 八相、十六相或更高解析度應如何選擇？
3. 多個諧波應獨立量化，還是聯合形成碼本？
4. 缺失諧波、弱諧波與錯誤基頻如何表示？
5. 不同音類、說話人、基頻與量測鏈是否共用同一碼本？
6. 如何把 FARHP 轉成神經模型 token，而不破壞圓周拓撲？
7. 如何由 token 重建相位，並衡量聲學與知覺損失？
8. 人類書寫的相位附標，如何與機器表示保持一致？

本文的目的不是宣稱存在唯一最佳碼本，而是建立一個可被實驗替換、比較與版本化的表示框架。

## 0.2 本文在系列中的位置

系列四篇理論基礎形成：

$$
\boxed{
\text{總體定義}
\rightarrow
\text{商環面數學}
\rightarrow
\text{聲學與知覺邊界}
\rightarrow
\text{離散表示與 AI 接口}
}
$$

其中：

- 第一篇回答 FARHP 是什麼；
- 第二篇回答 FARHP 位於什麼數學空間；
- 第三篇回答 FARHP 在聲音中代表什麼、不能代表什麼；
- 本篇回答 FARHP 如何成為可計算與可生成的資料物件。

## 0.3 核心立場

本文採取以下立場：

> 離散化不是把連續角度粗略變成整數，而是在拓撲、聲學可靠度、知覺任務、碼率與可逆性之間建立受條件限制的表示映射。

因此：

$$
\text{離散碼}
\neq
\text{真實相位本身},
$$

但一個良好離散碼應保存任務需要的相位等價類與動態結構。

---

# 1. 表示需求與不可退讓條件

## 1.1 圓周拓撲條件

相位是週期變數。若：

$$
\psi_a=-\pi+\varepsilon,
\qquad
\psi_b=\pi-\varepsilon,
$$

則其真實圓周距離接近：

$$
2\varepsilon,
$$

而不是接近：

$$
2\pi-2\varepsilon.
$$

因此任何表示若直接以普通實數差：

$$
|\psi_a-\psi_b|
$$

訓練或聚類，都可能在包覆邊界產生錯誤。

## 1.2 諧波身份條件

FARHP 的每個座標都與諧波索引綁定：

$$
\psi_k
=
\operatorname{wrap}(\phi_k-k\phi_1).
$$

所以：

$$
\psi_2
\neq
\psi_5
$$

不只是數值可能不同，其聲學角色、可靠度與誤差結構也不同。資料格式不得省略 $k$。

## 1.3 錨點條件

所有基頻錨定座標共享同一個 $\phi_1$ 估計誤差。若：

$$
\widehat{\phi}_1
=
\phi_1+\varepsilon_1,
$$

則：

$$
\widehat{\psi}_k
=
\psi_k-k\varepsilon_1+\varepsilon_k.
$$

高階座標誤差具有相關性，因此不能把每一個相位碼視為完全獨立的分類標籤。

## 1.4 缺失值條件

當某諧波振幅不足、相位估計不穩或基頻身份有疑義時，該相位不是數值零，而是「未觀測／不可信」。故：

$$
\text{missing}
\neq
0.
$$

遮罩必須與數值分離。

## 1.5 雙軌來源條件

第三篇已區分：

- `FARHP-Y`：麥克風輸出可觀測相位；
- `FARHP-G`：逆濾波後的聲門相位估計。

二者不能共用未標示來源的碼本索引。即使碼本幾何相同，資料域仍應明確標注。

## 1.6 適用門控條件

第三篇提出：

$$
\Gamma\in\{0,1,2,3,4\},
$$

表示 FARHP 對某音框或音類的適用程度。當：

$$
\Gamma=0,
$$

系統不應強制產生具有語義解讀的 FARHP token；最多只能標示為不可用或由其他模型接管。

## 1.7 可版本化條件

相位碼本會因資料、任務、取樣率、分析器與模型版本而改變。故任何離散 token 必須附帶：

$$
\text{codebook\_id}
+
\text{codebook\_version}.
$$

單獨的整數 token 沒有跨系統的固定意義。

---

# 2. 第一級：連續圓周表示

## 2.1 角度表示

最直接的表示是：

$$
\psi_k\in(-\pi,\pi].
$$

它適合人類閱讀與輸出，但不適合直接作為一般歐氏回歸目標。

## 2.2 單位圓嵌入

定義：

$$
E:\mathbb T\rightarrow\mathbb R^2,
$$

$$
E(\psi_k)
=
\begin{pmatrix}
\cos\psi_k\\
\sin\psi_k
\end{pmatrix}.
$$

則：

$$
\|E(\psi_k)\|_2=1.
$$

反解為：

$$
\psi_k
=
\operatorname{atan2}
(\sin\psi_k,\cos\psi_k).
$$

此表示把圓周嵌入平面，避免角度包覆邊界的不連續。

## 2.3 複數表示

等價地：

$$
z_k=e^{i\psi_k}.
$$

此時圓周群運算可直接寫為：

$$
z_a\odot z_b=z_az_b,
$$

對應：

$$
\operatorname{Arg}(z_az_b)
=
\operatorname{wrap}(\psi_a+\psi_b).
$$

複數表示適合數學與複數神經網路；正弦—餘弦表示則更容易放入一般實值張量。

## 2.4 單位圓投影

神經模型輸出：

$$
\widehat{\mathbf u}_k
=
(a_k,b_k)
$$

通常不會精確落在單位圓上，因此需要：

$$
\Pi_{S^1}(a_k,b_k)
=
\frac{(a_k,b_k)}{\sqrt{a_k^2+b_k^2+\epsilon}}.
$$

若：

$$
a_k^2+b_k^2
\approx0,
$$

則不應強行解讀為某個相位，而應同時降低置信度。

## 2.5 圓周損失

對真值與預測值，可使用弦距：

$$
\ell_{\mathrm{chord}}
=
\|E(\widehat\psi)-E(\psi)\|_2^2.
$$

展開後：

$$
\ell_{\mathrm{chord}}
=
2-2\cos(\widehat\psi-\psi).
$$

也可使用測地損失：

$$
\ell_{\mathrm{geo}}
=
\delta_{\mathbb T}(\widehat\psi,\psi)^p.
$$

弦距在數值上平滑；測地距離則更直接反映角度偏差。二者應由任務決定。

---

# 3. 第二級：圓周標量量化

## 3.1 均勻 $M$ 相量化

把圓周分為 $M$ 個區域。令：

$$
\Delta_M
=
\frac{2\pi}{M}.
$$

碼字中心可定義為：

$$
c_j
=
-\pi+
\left(j+\frac12\right)\Delta_M,
\qquad
j=0,1,\ldots,M-1.
$$

編碼器：

$$
Q_M(\psi)
=
\operatorname*{arg\,min}_{j}
\delta_{\mathbb T}(\psi,c_j).
$$

解碼器：

$$
D_M(j)=c_j.
$$

## 3.2 八相、十六相、三十二相與六十四相

候選解析度可設為：

$$
M\in\{8,16,32,64\}.
$$

其角寬分別為：

$$
\frac{\pi}{4},
\quad
\frac{\pi}{8},
\quad
\frac{\pi}{16},
\quad
\frac{\pi}{32}.
$$

八相適合人類附標、低碼率或初步分類；三十二相與六十四相更適合波形重建與高可靠度諧波。不能預先宣稱某一解析度普遍最佳。

## 3.3 最壞量化誤差

均勻量化的最大圓周誤差為：

$$
\varepsilon_{\max}
=
\frac{\Delta_M}{2}
=
\frac{\pi}{M}.
$$

若各座標獨立量化，則加權環面最壞誤差上界為：

$$
d_{2,\mathbf w}^{\max}
\le
\left(
\sum_{k=2}^{K}
 w_k
\left(\frac{\pi}{M_k}\right)^2
\right)^{1/2}.
$$

此上界只是幾何誤差，不等於波形誤差或知覺誤差。

## 3.4 多解析度量化

令每個諧波有自己的解析度：

$$
M_k
=
\mathcal M
(k,c_k,A_k,f_0,\Gamma,\chi),
$$

其中：

- $c_k$：相位置信度；
- $A_k$：諧波振幅；
- $f_0$：基頻；
- $\Gamma$：適用門控；
- $\chi$：音類或聲學條件。

例如，高可靠度低階諧波可以使用：

$$
M_k=32,
$$

低可靠度高階諧波則可使用：

$$
M_k=8
$$

或直接遮罩。

## 3.5 非均勻圓周量化

若相位資料分布高度集中，均勻碼字會浪費容量。設資料密度為：

$$
p_k(\psi\mid\chi).
$$

可以學習中心：

$$
\mathcal C_k
=
\{c_{k,1},\ldots,c_{k,M_k}\}
\subset\mathbb T,
$$

使期望失真最小：

$$
\mathcal D_k
=
\mathbb E
\left[
 w_k
 \delta_{\mathbb T}
 (\psi_k,D(Q(\psi_k)))^p
\right].
$$

但非均勻碼本會降低人類直觀性，因此應保留「規則碼」與「學習碼」兩種模式。

## 3.6 碼字邊界的抖動

當相位在兩個碼區邊界附近波動時，token 可能快速切換。可用軟指派：

$$
p(j\mid\psi)
=
\frac{
\exp[-\beta\delta_{\mathbb T}(\psi,c_j)^2]
}{
\sum_r
\exp[-\beta\delta_{\mathbb T}(\psi,c_r)^2]
}.
$$

也可使用時間遲滯：只有當新碼字距離改善超過門檻時才切換。

---

# 4. 第三級：環面聯合碼本

## 4.1 為何獨立量化不充分

FARHP 座標受共同錨點誤差、聲源形狀與聲道相位共同影響，因此：

$$
P(\psi_2,\ldots,\psi_K)
\neq
\prod_{k=2}^{K}P(\psi_k).
$$

若把每個座標完全獨立量化，會忽略：

- 跨諧波相關；
- 聲門脈衝形成的整體相位形狀；
- 共同錨點不確定性；
- 不同音類的特定環面子流形；
- 時間連續軌跡。

## 4.2 環面碼本

定義條件碼本：

$$
\mathcal C^{(\chi)}
=
\left
\{
\mathbf c^{(\chi)}_1,
\ldots,
\mathbf c^{(\chi)}_J
\right
\subset
\mathbb T^{K-1},
$$

其中 $\chi$ 表示條件域。

硬編碼器為：

$$
Q_{\mathcal C}
(\boldsymbol\psi)
=
\operatorname*{arg\,min}_{j}
 d_{\chi}
(\boldsymbol\psi,
 \mathbf c^{(\chi)}_j).
$$

解碼器為：

$$
D_{\mathcal C}(j)
=
\mathbf c^{(\chi)}_j.
$$

## 4.3 加權環面距離

基本距離可寫為：

$$
d_{2,\mathbf w}
(\boldsymbol\psi,
 \boldsymbol\varphi)
=
\left(
\sum_{k=2}^{K}
 w_k
 \delta_{\mathbb T}
 (\psi_k,\varphi_k)^2
\right)^{1/2}.
$$

權重不應只由諧波階數決定，而可分解為：

$$
w_k
=
\widetilde w_k^{(A)}
\widetilde w_k^{(c)}
\widetilde w_k^{(H)}
\widetilde w_k^{(P)}
\widetilde w_k^{(\Gamma)},
$$

其中：

- $\widetilde w_k^{(A)}$：振幅或能量權重；
- $\widetilde w_k^{(c)}$：估計置信度權重；
- $\widetilde w_k^{(H)}$：聽覺解析權重；
- $\widetilde w_k^{(P)}$：任務知覺權重；
- $\widetilde w_k^{(\Gamma)}$：音類適用權重。

## 4.4 馬氏型局部距離

若知道 FARHP 誤差協方差：

$$
\Sigma_{\psi},
$$

可在局部解除包覆後定義：

$$
d_{\Sigma}^2
=
\boldsymbol\delta^{\mathsf T}
(\Sigma_{\psi}+\lambda I)^{-1}
\boldsymbol\delta,
$$

其中：

$$
\delta_k
=
\operatorname{wrap}(\psi_k-\varphi_k).
$$

此距離能降低共享錨點誤差方向的過度懲罰，但只在局部差異不跨越多個包覆分支時可靠。

## 4.5 圓周質心

對被分配到同一碼字的樣本集合 $S_j$，第 $k$ 個座標的圓周質心為：

$$
\overline z_{j,k}
=
\sum_{n\in S_j}
\alpha_{n,k}e^{i\psi_{n,k}}.
$$

若：

$$
|\overline z_{j,k}|>\tau,
$$

則：

$$
c_{j,k}
=
\operatorname{Arg}(\overline z_{j,k}).
$$

若：

$$
|\overline z_{j,k}|\le\tau,
$$

表示該群在此座標可能多峰、近似均勻或資料不足，不應用單一平均相位表示。

## 4.6 多峰碼本與混合成分

單一碼字中心不能表示互為對向的雙峰分布。可使用：

$$
p(\boldsymbol\psi\mid j)
=
\sum_{r=1}^{R_j}
\pi_{j,r}
 p_{j,r}(\boldsymbol\psi),
$$

或把同一語音類別拆成多個相位 token。碼本的目的不是讓每個音素只對應一個 token，而是描述可重建的相位原型。

## 4.7 乘積量化

當 $K$ 很大時，完整聯合碼本會遭遇維度與資料稀疏問題。可把諧波分為群組：

$$
\mathcal H
=
H_1\cup H_2\cup\cdots\cup H_B,
$$

並對各區塊建立碼本：

$$
Q(\boldsymbol\psi)
=
(Q_1(\boldsymbol\psi_{H_1}),
 \ldots,
 Q_B(\boldsymbol\psi_{H_B})).
$$

自然分組可以是：

- 低階已解析諧波；
- 中階過渡諧波；
- 高階未解析或低可靠度諧波。

## 4.8 分層碼本

另一方案是：

$$
\boldsymbol\psi
\approx
\mathbf c^{(0)}_{j_0}
\oplus
\mathbf r^{(1)}_{j_1}
\oplus\cdots\oplus
\mathbf r^{(L)}_{j_L},
$$

其中 $\oplus$ 表示環面上的逐座標相位加法。第一層提供粗略形狀，後續層提供殘差修正。這使低碼率與高保真可以共用同一表示族。

---

# 5. 遮罩、可靠度與不確定性

## 5.1 四種不同狀態

每一諧波至少應區分：

1. **有效且可信；**
2. **有效但低可信；**
3. **未觀測或低於振幅門檻；**
4. **模型不適用。**

這四種狀態不能全部壓成一個布林遮罩。

## 5.2 建議欄位

對每個 $k$，保存：

$$
(m_k,c_k,a_k,s_k),
$$

其中：

- $m_k\in\{0,1\}$：是否存在可用相位估計；
- $c_k\in[0,1]$：相位估計置信度；
- $a_k$：諧波振幅或正規化能量；
- $s_k$：狀態枚舉。

## 5.3 錨點置信度

除了各諧波置信度，還必須保存：

$$
c_{\mathrm{anchor}}
\in[0,1].
$$

因為錨點錯誤會共同污染所有座標。有效權重可設為：

$$
\widetilde c_k
=
 m_kc_kc_{\mathrm{anchor}}^{\rho_k},
$$

其中 $\rho_k$ 可隨 $k$ 增加，反映高階座標對錨點誤差更敏感。

## 5.4 碼本外距離

即使某樣本被迫分配到最近碼字，也可能遠離訓練分布。應保存：

$$
d_{\mathrm{ood}}
=
\min_j
 d_{\chi}
(\boldsymbol\psi,
 \mathbf c_j^{(\chi)}).
$$

若：

$$
d_{\mathrm{ood}}>\tau_{\chi},
$$

則 token 應標示為碼本外，而不是假裝它是正常原型。

## 5.5 熵與軟碼

軟指派分布：

$$
p(j\mid\boldsymbol\psi,\chi)
$$

的熵：

$$
H_Q
=
-\sum_j
 p_j\log p_j
$$

可作為碼字歧義度。低熵表示碼字明確；高熵表示處於邊界、多峰或資料域外。

## 5.6 缺失諧波的距離

對兩個樣本 $a,b$，共同有效集合為：

$$
I_{ab}
=
\{k:m_{a,k}=m_{b,k}=1\}.
$$

條件距離可寫為：

$$
d_{ab}
=
\left(
\frac{
\sum_{k\in I_{ab}}
 w_{ab,k}
 \delta_{\mathbb T}
 (\psi_{a,k},\psi_{b,k})^2
}{
\sum_{k\in I_{ab}}w_{ab,k}+\epsilon
}
\right)^{1/2}.
$$

但若共同有效諧波過少，應同時輸出覆蓋率：

$$
r_{ab}
=
\frac{|I_{ab}|}{K-1}.
$$

不能只回傳一個看似精確的距離。

---

# 6. 雙軌與條件化碼本

## 6.1 `FARHP-Y` 與 `FARHP-G`

建立兩個來源域：

$$
\mathcal D_Y
\quad\text{與}\quad
\mathcal D_G.
$$

其碼本分別為：

$$
\mathcal C_Y^{(\chi)},
\qquad
\mathcal C_G^{(\chi)}.
$$

`FARHP-Y` 描述最終輸出波形；`FARHP-G` 描述依特定逆濾波方法估計的聲門源。後者必須附帶：

- 逆濾波方法；
- 參數；
- 模型假設；
- 失敗標記；
- 置信度。

## 6.2 條件變數

條件集合可寫為：

$$
\chi
=
(d,
 \Gamma,
 b_{f_0},
 p,
 s,
 r,
 q,
 v),
$$

其中：

- $d$：來源域，`Y` 或 `G`；
- $\Gamma$：適用門控；
- $b_{f_0}$：基頻區間；
- $p$：音類或發音方式；
- $s$：說話人或匿名說話群；
- $r$：錄音／量測域；
- $q$：品質層級；
- $v$：分析器版本。

## 6.3 為何要做 $f_0$ 條件化

相同的諧波階數在不同基頻下落於不同絕對頻率，也可能處於不同聽覺解析區域。故：

$$
\mathcal C(\boldsymbol\psi\mid f_0=90\text{ Hz})
$$

不必等於：

$$
\mathcal C(\boldsymbol\psi\mid f_0=300\text{ Hz}).
$$

第一版可先使用粗區間，而不是每個赫茲建立碼本。

## 6.4 音類條件化

穩定母音、鼻音、有聲擦音與多週期聲的相位幾何不同。第一版建議：

- $\Gamma=4$：完整 FARHP 碼本；
- $\Gamma=3$：完整碼本加較強遮罩；
- $\Gamma=2$：週期子空間碼本；
- $\Gamma=1$：研究性或廣義相位碼；
- $\Gamma=0$：不產生標準 FARHP token。

## 6.5 說話人條件化的界線

說話人碼本可以提高重建品質，但可能把說話人身份與發音符號綁定。新符號語言若追求跨說話人一致性，應至少分離：

$$
\text{語言相位原型}
\quad\text{與}\quad
\text{說話人相位殘差}.
$$

可寫為：

$$
\boldsymbol\psi
=
\boldsymbol\mu_{\mathrm{ling}}
\oplus
\boldsymbol\rho_{\mathrm{speaker}}
\oplus
\boldsymbol\epsilon.
$$

此分解目前只是建模假設，必須由跨說話人實驗驗證。

## 6.6 碼本退化與碎片化

條件越多，資料越稀疏。若為每一個條件組合建立獨立碼本，將出現：

$$
|\mathcal C|
\times
|\chi|
$$

的資料碎片化。可採：

1. 共享基礎碼本加條件殘差；
2. 超網路產生碼字修正；
3. 分層碼本；
4. 只對最重要的條件分域；
5. 使用條件嵌入而非完全獨立碼本。

---

# 7. 動態 FARHP token

## 7.1 靜態幀不足

語音是一條路徑：

$$
\boldsymbol\psi(t)
\in
\mathbb T^{K-1}.
$$

逐幀獨立 token 會產生：

- 碼字抖動；
- 時間不連續；
- 不必要高碼率；
- 難以保留相位速度與繞行結構。

## 7.2 關鍵幀與差分 token

在關鍵幀 $t_0$ 保存：

$$
q_{t_0}^{\mathrm{abs}}.
$$

後續保存環面差分：

$$
\Delta\boldsymbol\psi_t
=
\operatorname{wrap}
(\boldsymbol\psi_t-
 \boldsymbol\psi_{t-1}).
$$

差分碼本為：

$$
q_t^{\Delta}
=
Q_{\Delta}
(\Delta\boldsymbol\psi_t).
$$

解碼時：

$$
\widehat{\boldsymbol\psi}_t
=
\widehat{\boldsymbol\psi}_{t-1}
\oplus
D_{\Delta}(q_t^{\Delta}).
$$

## 7.3 漂移與重同步

差分編碼會累積錯誤，因此必須定期插入絕對關鍵幀。若：

$$
d(
\widehat{\boldsymbol\psi}_t,
\boldsymbol\psi_t)
>
\tau_{m sync},
$$

或置信度突然下降，就建立新關鍵幀。

## 7.4 碼字遲滯

令當前碼字為 $j_{t-1}$，候選碼字為 $j^*$。只有當：

$$
d(\boldsymbol\psi_t,\mathbf c_{j^*})
+
\eta
<
 d(\boldsymbol\psi_t,
 \mathbf c_{j_{t-1}})
$$

時才切換。$\eta$ 是遲滯門檻。

## 7.5 軌跡碼本

除了幀級碼本，也可直接對短軌跡片段建立 token：

$$
\mathcal S_t
=
\{
\boldsymbol\psi_{t-L+1},
\ldots,
\boldsymbol\psi_t
\}.
$$

此方法可以保留：

- 進入相位；
- 穩態相位；
- 離開相位；
- 聲門週期形狀的轉換模式。

## 7.6 繞行數與拓撲事件

若解除包覆後某座標跨越完整週期，單純逐幀最近中心可能遺失繞行資訊。動態格式可另存：

$$
n_k
\in
\mathbb Z,
$$

表示區段內的繞行數。但在一般穩定母音中，它應先作診斷量，而不是預設的語言符號。

---

# 8. AI 可學習表示

## 8.1 連續頭

模型輸出：

$$
\widehat U
\in
\mathbb R^{(K-1)\times2},
$$

每列經單位圓投影後得到預測相位。損失為：

$$
\mathcal L_{m cont}
=
\frac{
\sum_k
 m_kw_k
 \|\widehat U_k-U_k\|_2^2
}{
\sum_km_kw_k+\epsilon
}.
$$

優點是精細、可插值；缺點是缺少明確離散符號。

## 8.2 離散分類頭

若每個座標使用 $M_k$ 相，模型輸出：

$$
p(q_k=j\mid x).
$$

可用交叉熵：

$$
\mathcal L_{m cls}
=
-\sum_km_kw_k
\log p(q_k^*\mid x).
$$

但普通分類損失把相鄰碼字與對向碼字視為同樣錯誤。應加入圓周成本：

$$
\mathcal L_{m circ}
=
\sum_km_kw_k
\sum_j
p_{k,j}
\delta_{\mathbb T}(c_{k,j},\psi_k)^2.
$$

## 8.3 聯合 VQ 類表示

編碼器產生連續潛變量：

$$
\mathbf z_e(x).
$$

選擇最近碼字：

$$
j^*
=
\operatorname*{arg\,min}_j
 d_{\chi}
(\Pi_{\mathbb T}(\mathbf z_e),
 \mathbf c_j).
$$

得到離散表示：

$$
\mathbf z_q
=
\mathbf c_{j^*}.
$$

與一般歐氏 VQ 不同，FARHP 碼字必須位於環面，更新也應使用圓周質心或單位複數平均。

## 8.4 混合頭

最佳工程方案可能是：

$$
\text{粗 token}
+
\text{連續殘差}.
$$

令：

$$
\boldsymbol\psi
=
\mathbf c_j
\oplus
\boldsymbol\rho,
$$

其中：

$$
\boldsymbol\rho
\in
[-\rho_{m max},\rho_{m max}]^{K-1}.
$$

粗 token 提供可解釋類別，連續殘差提供高保真重建。

## 8.5 機率分布頭

相位具有不確定性時，不宜只輸出點估計。單座標可用圓周分布：

$$
p(\psi_k\mid\mu_k,\kappa_k)
\propto
\exp
\left[
\kappa_k\cos(\psi_k-\mu_k)
\right].
$$

其中：

- $\mu_k$：平均方向；
- $\kappa_k$：集中程度。

低 $\kappa_k$ 表示高不確定性。多諧波可使用條件分解、混合分布或環面正規化流，但第一版不必一開始採用最複雜模型。

## 8.6 遮罩預測頭

模型必須同時預測：

$$
\widehat m_k,
\qquad
\widehat c_k,
$$

而不是假設每一個諧波相位都存在。總損失可以寫為：

$$
\mathcal L
=
\lambda_{\rm phase}\mathcal L_{\rm phase}
+
\lambda_{\rm mask}\mathcal L_{\rm mask}
+
\lambda_{\rm conf}\mathcal L_{\rm conf}
+
\lambda_{\rm wav}\mathcal L_{\rm wav}
+
\lambda_{\rm perc}\mathcal L_{\rm perc}.
$$

## 8.7 群一致性資料增強

對輸入波形做純時間平移時，FARHP 理論上應不變。可用一致性損失：

$$
\mathcal L_{\rm inv}
=
 d
\left(
F(x),
F(T_\tau x)
\right),
$$

其中 $T_\tau$ 是時間平移。若結果不一致，可能表示分析器、窗函數、基頻追蹤或模型未學到預期不變量。

## 8.8 極性政策

波形極性反轉會依諧波奇偶改變 FARHP。系統必須選擇：

1. 保留極性並把它當作資訊；
2. 在前處理中校正極性；
3. 建立對極性作用等變的碼本；
4. 把極性作為獨立 bit。

不得在不同資料來源中混用而不記錄。

---

# 9. 率—失真—知覺—拓撲目標

## 9.1 單一均方誤差不充分

若只最小化波形均方誤差，可能偏好高能量區段而忽略微弱但可聽的相位結構；若只最小化角度誤差，又可能高估低振幅諧波的重要性。

## 9.2 五重目標

本文提出：

$$
\mathcal J
=
\lambda_R R
+
\lambda_A D_A
+
\lambda_P D_P
+
\lambda_T D_T
+
\lambda_S D_S,
$$

其中：

- $R$：碼率或 token 複雜度；
- $D_A$：聲學重建失真；
- $D_P$：知覺失真；
- $D_T$：拓撲不一致失真；
- $D_S$：穩健性或跨條件失真。

## 9.3 聲學失真

可包含：

$$
D_A
=
\alpha_1D_{\rm phase}
+
\alpha_2D_{\rm wav}
+
\alpha_3D_{\rm envelope}
+
\alpha_4D_{\rm peak}.
$$

其中：

- $D_{\rm phase}$：加權環面相位誤差；
- $D_{\rm wav}$：波形重建誤差；
- $D_{\rm envelope}$：聽覺包絡差異；
- $D_{\rm peak}$：週期峰值與脈衝形狀差異。

## 9.4 知覺失真

知覺失真必須由聽覺實驗或經驗模型估計。最低限度應區分：

- 可檢出差異；
- 可區辨差異；
- 自然度；
- 說話人相似度；
- 音素與聲調辨識。

不同任務不可被壓成單一「品質分數」。

## 9.5 拓撲失真

拓撲失真用來懲罰：

- 把相鄰圓周位置分得很遠；
- 把跨包覆邊界的鄰近樣本分到不相干碼字；
- 破壞時間平移不變性；
- 動態軌跡出現不合理跳躍。

可寫為：

$$
D_T
=
D_{\rm neighborhood}
+
D_{\rm invariance}
+
D_{\rm trajectory}.
$$

## 9.6 穩健性失真

測試條件包括：

- 不同麥克風；
- 不同取樣起點；
- 輕度噪聲；
- 基頻估計擾動；
- 振幅縮放；
- 相位包覆；
- 說話人變化；
- 音高變化。

真正可用的碼本不能只在訓練錄音鏈上成立。

---

# 10. Token 語法與資料序列

## 10.1 Token 不是裸整數

完整 token 應概念性表示為：

$$
\tau
=
(
\text{domain},
\text{codebook},
\text{condition},
\text{index},
\text{mask},
\text{confidence},
\text{residual},
\text{time}
).
$$

實際序列模型可把其中部分資訊置於上下文，但交換格式必須能恢復。

## 10.2 建議 token 類型

第一版至少定義：

- `ABS`：絕對環面碼字；
- `DELTA`：環面差分碼字；
- `RESIDUAL`：連續或量化殘差；
- `MASK`：諧波可用性更新；
- `CONF`：置信度更新；
- `DOMAIN`：`Y`／`G` 切換；
- `SYNC`：重同步關鍵幀；
- `NA`：FARHP 不適用；
- `OOD`：碼本外樣本；
- `END`：區段結束。

## 10.3 文本形式

人類可讀形式可寫為：

```text
@FARHP/0.1
DOMAIN:Y
CB:fy-vowel-f0b2-cb03
SYNC:t=1.240
ABS:0187
MASK:0x00FF
CONF:0.92
DELTA:004
DELTA:004
DELTA:011
END
```

此形式適合除錯，不建議作為大量音訊儲存格式。

## 10.4 JSON 形式

```json
{
  "farhp_version": "0.1",
  "domain": "Y",
  "anchor": {
    "type": "fundamental",
    "harmonic_index": 1,
    "confidence": 0.98
  },
  "analysis": {
    "sample_rate_hz": 48000,
    "frame_time_sec": 1.24,
    "f0_hz": 121.7,
    "applicability_grade": 4
  },
  "codebook": {
    "id": "fy-vowel-f0b2-cb03",
    "version": "0.1",
    "kind": "joint_torus"
  },
  "token": {
    "type": "ABS",
    "index": 187,
    "ood_distance": 0.11
  },
  "harmonics": {
    "indices": [2, 3, 4, 5, 6, 7, 8, 9],
    "mask": [1, 1, 1, 1, 1, 1, 1, 1],
    "confidence": [0.97, 0.96, 0.94, 0.91, 0.88, 0.80, 0.74, 0.69]
  },
  "polarity_policy": "preserve"
}
```

## 10.5 二進位形式

二進位交換可採用既有可擴充結構化格式，而非自行發明不透明封包。本文附帶的規格以欄位語義為核心，具體序列化可以替換。第一個參考實作可支援：

- JSON：除錯與跨語言可讀；
- CBOR：較緊湊的結構化二進位交換；
- NumPy／張量：模型訓練；
- WAV 附帶 sidecar：聲學重建實驗。

## 10.6 神經張量形式

固定最大諧波數 $K_{\max}$ 時，可用：

$$
X
\in
\mathbb R^{T\times(K_{\max}-1)\times C},
$$

通道 $C$ 可包含：

1. $\cos\psi_k$；
2. $\sin\psi_k$；
3. 遮罩；
4. 置信度；
5. 正規化振幅；
6. 諧波索引嵌入；
7. 來源域；
8. 適用門控。

離散 token 則可表示為：

$$
Q
\in
\mathbb Z^{T\times B},
$$

其中 $B$ 是乘積碼本區塊數。

---

# 11. 相位字形與人類介面

## 11.1 字形不是完整浮點資料

人類書寫不適合直接保存數十個高精度相位值。因此字形層應表達：

- 粗相位類別；
- 語言上有功能的相位原型；
- 可選的風格或發音附標；
- 非完整聲學真值。

## 11.2 八方向附標

最初可使用：

$$
M_{\rm glyph}=8.
$$

八個方向對應八相中心。附標可用：

- 點位；
- 開口方向；
- 小短線方向；
- 內圈刻度；
- 外圈節點。

但應避免依賴整個主字形旋轉，因為旋轉可能改變字形辨識與書寫習慣。

## 11.3 多諧波如何壓縮到字形

不能在一個字旁放數十個相位記號。可採三種方案：

### 方案一：原型索引

一個附標對應環面聯合碼字：

$$
g_j
\leftrightarrow
\mathbf c_j.
$$

### 方案二：低階諧波摘要

只書寫：

$$
(\psi_2,\psi_3,\psi_4),
$$

高階部分交由默認碼本或 AI 補全。

### 方案三：功能性相位類

把大量連續相位聚成少量可感知、可模仿的發音類別。這必須通過人類實驗，不能只由聚類演算法決定。

## 11.4 字形—音節—聲學分層

建議資料映射為：

$$
\text{glyph}
\rightarrow
\text{phonological unit}
\rightarrow
\text{phase token}
\rightarrow
\text{continuous FARHP}
\rightarrow
\text{waveform}.
$$

字形不應直接等同波形，也不應把碼本版本永久焊死。字形指向的是語言層原型，具體聲學實現可以隨合成器版本演進。

## 11.5 可讀性與機器性分離

同一符號可具有：

- `glyph_id`：視覺字形；
- `reading_id`：華語或新音節讀法；
- `phase_class`：人類可辨識相位類；
- `farhp_codebook_id`：機器碼本；
- `semantic_id`：形式語義。

這能避免「改字型就改語義」或「更新聲碼器就破壞文字」的耦合。

---

# 12. 碼本訓練程序

## 12.1 資料前置條件

每一筆訓練資料至少需要：

- 原始 WAV；
- 取樣率；
- 分析框位置；
- $f_0$ 與置信度；
- 諧波複數係數；
- FARHP-Y；
- 可選 FARHP-G；
- 振幅與殘差比例；
- 音類／音節標籤；
- $\Gamma$；
- 麥克風與處理鏈資訊；
- 說話人匿名識別；
- 分析器版本。

## 12.2 清理與門控

訓練前依序：

1. 排除錯誤檔案；
2. 檢查取樣率與削波；
3. 估計有聲區段；
4. 計算 $f_0$ 與倍頻／半頻風險；
5. 抽取諧波複數係數；
6. 形成 FARHP；
7. 建立 $m_k,c_k$；
8. 計算 $\Gamma$；
9. 依來源域與條件分桶；
10. 只在足夠覆蓋的資料上訓練碼本。

## 12.3 初始化

碼字可由：

- 隨機資料點；
- 圓周均勻格；
- 分層聚類；
- 低維嵌入後初始化；
- 已知人工相位原型；

開始。不同初始化需多次重跑，避免局部最優被誤認為自然類別。

## 12.4 環面 Lloyd 型迭代

重複：

### 指派步驟

$$
j_n
=
\operatorname*{arg\,min}_j
 d_{\chi}
(\boldsymbol\psi_n,
 \mathbf c_j).
$$

### 更新步驟

對每個碼字與每個座標使用加權圓周平均：

$$
\mathbf c_{j,k}
=
\operatorname{Arg}
\left(
\sum_{n:j_n=j}
\alpha_{n,k}
 e^{i\psi_{n,k}}
\right).
$$

若合向量長度過低，應：

- 拆分群；
- 增加混合成分；
- 移除該座標；
- 降低碼字有效維度；
- 或重建碼字。

## 12.5 碼字死亡

若某碼字長期沒有樣本指派，稱為死亡碼字。可：

- 用最高失真樣本重置；
- 拆分高變異群；
- 減少碼本大小；
- 增加碼字使用均衡正則。

## 12.6 版本發布

碼本發布時應附帶：

- 訓練資料摘要；
- 排除條件；
- 分析器版本；
- 距離函數；
- 權重政策；
- 碼字數；
- 量化失真；
- OOD 門檻；
- 已知偏差；
- SHA-256；
- 授權與隱私說明。

---

# 13. 評估協定

## 13.1 幾何評估

至少報告：

- 平均加權環面誤差；
- 中位數誤差；
- 高分位誤差；
- 每階諧波誤差；
- 遮罩覆蓋率；
- 碼本外比例；
- 碼字使用熵；
- 碼字死亡率。

## 13.2 波形重建評估

控制振幅與 $f_0$ 不變，只替換或量化 FARHP，測量：

- 時域誤差；
- 峰均比偏差；
- 週期峰值位置；
- 波形相關；
- 聽覺頻帶包絡；
- 合成器穩定性。

## 13.3 消融實驗

至少比較：

1. 不保存相位；
2. 最小相位重建；
3. 八相獨立量化；
4. 三十二相獨立量化；
5. 聯合環面碼本；
6. 聯合碼本加連續殘差；
7. 自然連續 FARHP 上限。

## 13.4 知覺實驗

最初採用穩定母音與同振幅頻譜條件。可測：

- ABX 可區辨性；
- 自然度；
- 相似度；
- 相位 token 辨認；
- 跨說話人泛化；
- 是否影響原有華語音素與聲調辨識。

## 13.5 跨條件評估

訓練與測試需切分：

- 說話人；
- 麥克風；
- 錄音環境；
- $f_0$ 範圍；
- 音類；
- 語速；
- 聲級。

若同一說話人的相鄰音框同時出現在訓練與測試，會嚴重高估泛化能力。

## 13.6 碼率評估

對離散表示報告：

$$
R
=
\frac{\text{總位元數}}{\text{秒數}},
$$

以及每音節、每幀與每有效諧波的碼率。若 token 還需大量 side information，不能只計算碼字索引。

---

# 14. FARHP-Spec-v0.1

## 14.1 規格目的

FARHP-Spec-v0.1 不是固定某個分析演算法或聲碼器，而是規定不同實作交換資料時必須保留的語義。

## 14.2 必填欄位

每個 FARHP 物件必須包含：

1. `farhp_version`；
2. `domain`；
3. `anchor.type`；
4. `anchor.harmonic_index` 或廣義錨描述；
5. `anchor.confidence`；
6. `frame_time_sec` 或時間索引；
7. `f0_hz` 與置信度；
8. `harmonic_indices`；
9. `phase_representation`；
10. `phase_values` 或 `token`；
11. `mask`；
12. `confidence`；
13. `applicability_grade`；
14. `polarity_policy`；
15. `analysis_method` 與版本；
16. 若為離散碼，`codebook_id` 與版本。

## 14.3 可選欄位

可選：

- 諧波振幅；
- 協方差或不確定性；
- 逆濾波資訊；
- 量測鏈；
- 音類；
- 說話人匿名群；
- OOD 距離；
- 連續殘差；
- 繞行數；
- 知覺權重；
- 原始資料雜湊。

## 14.4 表示模式

`phase_representation` 至少允許：

- `angle_rad`；
- `unit_circle_xy`；
- `complex_pair`；
- `scalar_quantized`；
- `joint_torus_codebook`；
- `product_codebook`；
- `joint_plus_residual`；
- `not_applicable`。

## 14.5 禁止行為

合規實作不得：

1. 用 $0$ 取代缺失相位而不設遮罩；
2. 省略諧波索引；
3. 省略錨點類型；
4. 把 `FARHP-G` 標示為聲門生理真值；
5. 讓同一碼本 ID 在不同版本指向不同碼字；
6. 在極性政策不同時混合資料；
7. 在 $\Gamma=0$ 時產生正常 FARHP 語言 token；
8. 把裸 token 索引宣稱為跨碼本通用語義；
9. 在未知分析器版本下假定資料完全可比較；
10. 把碼本聚類直接宣稱為人類音韻類別。

## 14.6 最小相容性層級

定義：

### Level 0：連續交換

保存角度或單位圓表示、遮罩與置信度。

### Level 1：標量離散

支援每諧波圓周量化與解析度資訊。

### Level 2：聯合碼本

支援環面碼字、條件域及 OOD 距離。

### Level 3：動態 token

支援關鍵幀、差分、重同步與殘差。

### Level 4：語言整合

支援字形、音節、相位類與語義映射。

第五篇原型最低應先完成 Level 0，再逐步達到 Level 2。

---

# 15. 形式命題與可證偽推論

## 命題 R1：圓周嵌入邊界連續性

若兩相位在圓周上收斂，則其單位圓嵌入的歐氏距離亦收斂，不會在 $-\pi/\pi$ 邊界產生有限跳躍。

## 命題 R2：均勻量化誤差上界

$M$ 相均勻量化的單座標最大測地誤差為：

$$
\frac{\pi}{M}.
$$

## 命題 R3：條件碼本優勢命題

若兩個條件域的 FARHP 分布顯著不同，且各域資料量足夠，則條件化碼本在相同總碼率下可低於單一全域碼本的條件期望失真；若資料不足，則可能因過擬合而失敗。

## 命題 R4：聯合碼本相關收益命題

當 FARHP 座標存在可重現跨諧波相關時，聯合或乘積碼本在相同有效碼率下應優於完全獨立標量量化；若各座標近似條件獨立，收益將下降。

## 命題 R5：可靠度加權穩健性命題

在相位估計誤差與置信度校準相關的條件下，可靠度加權碼本應比等權碼本具有更低的乾淨波形重建誤差與更低的 OOD 誤判率。

## 命題 R6：雙軌碼本不可互換命題

若聲道與量測鏈相位貢獻不可忽略，則 `FARHP-Y` 碼本與 `FARHP-G` 碼本的碼字分布不應被假設可直接互換。

## 命題 R7：動態碼本碼率命題

對平滑 FARHP 軌跡，關鍵幀加差分碼本可在相近重建失真下降低平均 token 熵；對快速不規則軌跡，收益可能消失。

## 命題 R8：碼字不等於音韻類別

無監督碼本的穩定聚類不充分推出人類可模仿、可區辨或具語言功能；只有在跨說話人知覺與產生實驗成立後，碼字才可升格為候選發音類別。

---

# 16. 第五篇技術架構的強制接口

第四篇完成後，第五篇不得從任意 FFT 相位直接跳到新語言字形，而必須先建立下列模組：

## 16.1 `farhp-analyzer`

輸入 WAV，輸出：

- $f_0$；
- 諧波複數係數；
- FARHP-Y；
- 遮罩；
- 置信度；
- $\Gamma$；
- 分析診斷。

## 16.2 `farhp-reconstructor`

輸入振幅、$f_0$、連續 FARHP 與殘差，重建波形。這是驗證表示是否真的保留相位作用的必要基線。

## 16.3 `farhp-quantizer`

至少支援：

- 八／十六／三十二相均勻量化；
- 圓周誤差；
- 遮罩；
- 多解析度；
- 碼本外標記。

## 16.4 `farhp-codebook`

支援：

- 環面聚類；
- 圓周質心；
- 聯合與乘積碼本；
- 條件域；
- 碼本版本；
- 訓練摘要。

## 16.5 `farhp-inspector`

視覺化：

- 原始與重建波形；
- 諧波振幅；
- 相位圓；
- FARHP 環面投影；
- token 軌跡；
- 遮罩與置信度；
- 碼本距離。

## 16.6 `farhp-spec`

輸出並驗證：

- JSON；
- JSON Schema；
- 可選 CBOR；
- sidecar 檔；
- SHA-256。

## 16.7 最低成功條件

第五篇與第一版原型的最低成功條件是：

1. 對合成理想諧波訊號，時間平移前後 FARHP 在數值容差內不變；
2. 連續 FARHP 可重建預期波形；
3. 八、十六、三十二相量化誤差符合幾何上界；
4. 缺失諧波不被填成零相位；
5. 錯誤基頻能被診斷或降低置信度；
6. `FARHP-Y` 與 `FARHP-G` 分域；
7. 所有輸出通過 FARHP-Spec-v0.1 驗證；
8. 同一資料與版本可重現相同 token。

---

# 17. 本文的理論貢獻

## 貢獻一：三級表示架構

建立：

$$
\boxed{
\text{連續圓周表示}
\rightarrow
\text{多解析度標量量化}
\rightarrow
\text{環面聯合碼本}
}
$$

## 貢獻二：把碼本建立在商環面而非普通歐氏空間

碼字、距離、平均與插值均尊重相位圓周拓撲。

## 貢獻三：可靠度與缺失值成為表示本體的一部分

不再把遮罩視為資料清理細節，而是 FARHP 物件的必要欄位。

## 貢獻四：建立 `FARHP-Y`／`FARHP-G` 雙軌碼本

避免觀測輸出相位與聲門估計相位的來源混淆。

## 貢獻五：建立條件化碼本

音類、$f_0$、適用門控、量測域與分析器版本均可進入條件。

## 貢獻六：建立動態 token 語法

以絕對碼、差分碼、重同步、遮罩與殘差表示相位軌跡。

## 貢獻七：建立五重最佳化目標

碼率、聲學、知覺、拓撲與穩健性共同決定表示品質。

## 貢獻八：建立字形與聲學解耦接口

字形指向語言相位類，而非永久綁定某一浮點相位向量或聲碼器。

## 貢獻九：封閉 FARHP-Spec-v0.1

使第五篇可直接進入可驗證的工程實作。

---

# 18. 限制與開放問題

## 18.1 碼本仍依賴資料

任何學習碼本都會反映訓練資料中的說話人、語言、麥克風與分析器偏差。

## 18.2 知覺權重尚未實驗校準

本文提出權重分解，但不同諧波與不同音類的感知權重仍需聽覺實驗。

## 18.3 環面聚類可能存在多重局部最優

不同初始化可能得到不同碼本。碼字不能被過早本體化。

## 18.4 `FARHP-G` 受逆濾波方法影響

不同聲門逆濾波器可能產生不同碼本，必須保留方法版本。

## 18.5 人類可書寫不等於人類可發音

八方向附標容易書寫，但對應聲音能否被人類穩定模仿仍未知。

## 18.6 token 可預測不等於有語義

模型能預測某個相位 token，只代表資料中存在規律，不代表它天然承載概念或語法。

## 18.7 高階諧波可能需要可變維度

固定 $K_{\max}$ 容易實作，但不同 $f_0$、頻寬與聲級下，可用諧波數不同。後續可研究集合模型與可變長序列。

## 18.8 編碼安全性不是密碼學安全性

相位 token 與新字形可以降低直接可讀性，但若映射與資料足夠，仍可被統計學習。真正機密內容必須另用標準加密。

---

# 19. 結論

FARHP 的離散化問題，不是把：

$$
(-\pi,\pi]
$$

平均切成若干段就結束。FARHP 是一個帶有諧波身份、共享錨點誤差、遮罩、可靠度、音類條件、來源域與動態軌跡的商環面資料物件。任何忽略這些結構的 token 化，都可能得到可儲存但不可解釋、可分類但不可重建，或可重建卻無法跨條件泛化的表示。

本文因此建立三級架構：

$$
\boxed{
E(\boldsymbol\psi)
\rightarrow
Q_{\{M_k\}}(\boldsymbol\psi)
\rightarrow
Q_{\mathcal C^{(\chi)}}(\boldsymbol\psi)
}
$$

其中：

- $E$ 保存連續圓周幾何；
- $Q_{\{M_k\}}$ 提供規則、多解析度及人類可理解的離散碼；
- $Q_{\mathcal C^{(\chi)}}$ 學習跨諧波相關並形成 AI 可用 token。

完整 FARHP 物件可表示為：

$$
\boxed{
\mathfrak F_t
=
(
\boldsymbol\psi_t,
\mathbf m_t,
\mathbf c_t,
\mathbf A_t,
f_0(t),
\Gamma_t,
d_t,
\chi_t,
q_t,
\mathcal V
)
}
$$

其中 $d_t$ 表示 `Y` 或 `G` 來源域，$q_t$ 表示離散 token，$\mathcal V$ 表示分析器與碼本版本。

本文也建立最重要的邊界：

$$
\boxed{
\text{碼字相同}
\not\Rightarrow
\text{聲音完全相同}
}
$$

$$
\boxed{
\text{聚類穩定}
\not\Rightarrow
\text{人類音韻成立}
}
$$

$$
\boxed{
\text{AI 可生成}
\not\Rightarrow
\text{人類可模仿}
}
$$

只有在聲學重建、知覺區辨、跨說話人穩定與人類產生實驗成立後，FARHP token 才可能從工程碼字升格為新符號語言的發音類別。

至此，FARHP 四篇理論基礎正式閉合：

$$
\boxed{
\text{總論}
\rightarrow
\text{數學結構}
\rightarrow
\text{聲學邊界}
\rightarrow
\text{離散表示}
}
$$

下一篇將進入：

**《FARHP 發音合成系統：分析、編碼、生成與重建架構》**。

它不再只是理論論文，而會同步形成第一版 Python 原型、合成資料測試、WAV 分析器、相位量化器、碼本工具與規格驗證器。

---

# 參考文獻

[1] N. I. Fisher, *Statistical Analysis of Circular Data*, Cambridge University Press, 1993.

[2] K. V. Mardia and P. E. Jupp, *Directional Statistics*, Wiley, 2000.

[3] S. P. Lloyd, “Least Squares Quantization in PCM,” *IEEE Transactions on Information Theory*, vol. 28, no. 2, pp. 129–137, 1982.

[4] Y. Linde, A. Buzo, and R. M. Gray, “An Algorithm for Vector Quantizer Design,” *IEEE Transactions on Communications*, vol. 28, no. 1, pp. 84–95, 1980.

[5] R. M. Gray, “Vector Quantization,” *IEEE ASSP Magazine*, vol. 1, no. 2, pp. 4–29, 1984.

[6] A. van den Oord, O. Vinyals, and K. Kavukcuoglu, “Neural Discrete Representation Learning,” *Advances in Neural Information Processing Systems 30*, 2017.

[7] S. Takamichi, Y. Saito, N. Takamune, D. Kitamura, and H. Saruwatari, “Phase Reconstruction from Amplitude Spectrograms Based on von-Mises-Distribution Deep Neural Network,” *International Workshop on Acoustic Signal Enhancement*, 2018.

[8] Y. Masuyama, K. Yatabe, Y. Koizumi, Y. Oikawa, and N. Harada, “Phase Reconstruction Based on Recurrent Phase Unwrapping with Deep Neural Networks,” *ICASSP*, 2020.

[9] P. Magron, R. Badeau, and B. David, “Phase Reconstruction of Spectrograms with Linear Unwrapping: Application to Audio Signal Restoration,” *EUSIPCO*, 2016.

[10] P. Magron, R. Badeau, and B. David, “Phase Reconstruction of Spectrograms Based on a Model of Repeated Audio Events,” *IEEE Workshop on Applications of Signal Processing to Audio and Acoustics*, 2017.

[11] R. Espic, T. Raitio, and P. Alku, “Direct Modelling of Magnitude and Phase Spectra for Statistical Parametric Speech Synthesis,” *INTERSPEECH 2017*.

[12] S. Seelamantula and collaborators, “Phase-Encoded Speech Spectrograms,” *INTERSPEECH 2016*.

[13] I. Saratxaga, I. Hernáez, I. Odriozola, E. Navas, I. Luengo, and D. Erro, “Using Harmonic Phase Information to Improve ASR Rate,” *INTERSPEECH 2010*.

[14] P. Mowlaee, R. Saeidi, and Y. Stylianou, “Phase Importance in Speech Processing Applications,” *INTERSPEECH 2014*.

[15] C. Bormann and P. Hoffman, “Concise Binary Object Representation (CBOR),” RFC 8949, Internet Engineering Task Force, 2020.

[16] G. Fant, *Acoustic Theory of Speech Production*, Mouton, 1960.

[17] M. Airas, H. Pulakka, T. Bäckström, and P. Alku, “A Toolkit for Voice Inverse Filtering and Parametrisation,” *INTERSPEECH 2005*.

[18] G. Degottex and N. Obin, “Phase Distortion Statistics as a Representation of the Glottal Source: Application to the Classification of Voice Qualities,” *INTERSPEECH 2014*.

---

# 附錄 A：FARHP-Spec-v0.1 YAML 範例

```yaml
farhp_version: "0.1"
domain: "Y"

anchor:
  type: "fundamental"
  harmonic_index: 1
  confidence: 0.98

analysis:
  method: "harmonic_tracker_reference"
  method_version: "0.1"
  sample_rate_hz: 48000
  frame_time_sec: 1.240
  frame_length_sec: 0.040
  f0_hz: 121.7
  f0_confidence: 0.97
  applicability_grade: 4

phase:
  representation: "unit_circle_xy"
  harmonic_indices: [2, 3, 4, 5, 6, 7, 8, 9]
  values:
    - [0.0000, 1.0000]
    - [-0.7071, 0.7071]
    - [-1.0000, 0.0000]
    - [-0.3827, -0.9239]
    - [0.1951, -0.9808]
    - [0.7071, -0.7071]
    - [0.9808, -0.1951]
    - [1.0000, 0.0000]
  mask: [1, 1, 1, 1, 1, 1, 1, 1]
  confidence: [0.97, 0.96, 0.94, 0.91, 0.88, 0.80, 0.74, 0.69]

codebook:
  id: "fy-vowel-f0b2-cb03"
  version: "0.1"
  kind: "joint_torus"
  token_type: "ABS"
  token_index: 187
  ood_distance: 0.11

polarity_policy: "preserve"

provenance:
  recording_chain_id: "mic-domain-a"
  source_sha256: null
```

---

# 附錄 B：建議 JSON Schema 邏輯

最小驗證規則：

1. `farhp_version` 必須存在；
2. `domain` 只能是 `Y` 或 `G`；
3. `applicability_grade` 必須位於 $0$ 到 $4$；
4. `harmonic_indices`、`mask`、`confidence` 與 `values` 的長度必須相符；
5. `confidence` 必須位於 $[0,1]$；
6. `unit_circle_xy` 的每個值必須是長度為 $2$ 的數值陣列；
7. 若使用離散 token，碼本 ID 與版本必須存在；
8. 若 `domain=G`，逆濾波方法資訊應存在；
9. 若 $\Gamma=0$，表示模式應為 `not_applicable` 或附帶研究性例外標記；
10. 缺失座標必須由遮罩表示。

---

# 附錄 C：第一版碼本建議

## C.1 基準標量碼本

- `U8`：每座標八相；
- `U16`：每座標十六相；
- `U32`：每座標三十二相。

## C.2 基準聯合碼本

對前八個相對諧波座標：

$$
(\psi_2,\ldots,\psi_9),
$$

建立：

- `JT64`：64 個聯合碼字；
- `JT256`：256 個聯合碼字；
- `PQ4x16`：四個區塊，每區塊 16 個碼字。

這些只是第一輪比較基線，不是最終規格。

## C.3 條件分桶

第一輪只使用：

- `domain`：`Y`；
- $\Gamma=4$；
- 音類：穩定母音；
- $f_0$：低、中、高三區間；
- 說話人：只作測試切分，不建立個人碼本。

這可避免第一版因條件過多而資料碎片化。

---

# 附錄 D：工程資料夾建議

```text
farhp/
├─ papers/
├─ spec/
│  ├─ FARHP_Spec_v0.1.yaml
│  └─ FARHP_Spec_v0.1.schema.json
├─ src/
│  ├─ analyzer/
│  ├─ harmonic_tracker/
│  ├─ phase/
│  ├─ quantizer/
│  ├─ codebook/
│  ├─ reconstructor/
│  └─ inspector/
├─ tests/
│  ├─ synthetic/
│  ├─ invariance/
│  ├─ quantization/
│  ├─ reconstruction/
│  └─ schema/
├─ data/
│  ├─ raw/
│  ├─ derived/
│  └─ manifests/
├─ examples/
└─ README.md
```

---

# 附錄 E：系列四篇閉合摘要

| 篇次 | 核心問題 | 主要成果 |
|---|---|---|
| 第一篇 | FARHP 是什麼？ | 總體定義、研究邊界、系列架構 |
| 第二篇 | FARHP 位於什麼空間？ | 商環面、不變量、等價類、動態幾何 |
| 第三篇 | FARHP 在聲音中代表什麼？ | 聲源—聲道分解、知覺與音類邊界 |
| 第四篇 | FARHP 如何成為可運算資料？ | 圓周表示、相位碼本、AI token、FARHP-Spec-v0.1 |

---

**文件結束**
