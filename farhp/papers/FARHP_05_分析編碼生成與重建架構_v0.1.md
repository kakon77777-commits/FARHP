# FARHP 發音合成系統：分析、編碼、生成與重建架構
## 從理論閉合到 FARHP-Core-v0.1 可執行原型

**英文題名：** *The FARHP Pronunciation Synthesis System: Analysis, Encoding, Generation, and Reconstruction Architecture — From Theoretical Closure to the Executable FARHP-Core-v0.1 Prototype*  

**縮寫：** FARHP  
**中文簡稱：** 基錨相差  
**系列位置：** FARHP 系列第五篇／技術架構總篇／第一工程篇  
**作者：** Neo.K（EveMissLab）  
**AI 協作：** Aletheia（GPT-5.6 Thinking）  
**版本：** v0.1  
**日期：** 2026-07-26  
**文件性質：** 系統架構論文／參考實作說明／工程驗證報告

---

## 摘要

本文提出「基頻錨定相對諧波相位差」（Fundamental-Anchored Relative Harmonic Phase, FARHP）的第一個端到端技術架構，並同步發布可執行參考原型 `FARHP-Core-v0.1`。前四篇已分別完成 FARHP 的總體定義、商環面數學、聲學與知覺邊界，以及離散編碼與 AI 可學習表示；本文的任務不是再增加一層抽象論述，而是回答：如何把這些理論條件轉換為一條可測試、可失敗、可修正的分析—編碼—生成—重建閉環。

本文將系統拆為七個模組：基頻估計器、諧波分析器、FARHP 抽取器、圓周量化器、環面碼本、諧波重建器與規格驗證器。對短時有聲框架，系統先估計基頻 $f_0$，再以複數諧波投影估計：

$$
X_k=A_ke^{i\phi_k},
$$

並建立：

$$
\psi_k
=
\operatorname{wrap}(\phi_k-k\phi_1),
\qquad k\ge 2.
$$

重建端保存基頻錨點相位 $\phi_1$，並以：

$$
\widehat\phi_k
=
k\phi_1+\psi_k
\pmod{2\pi}
$$

恢復各諧波絕對相位。本文採用圓周測地距離、缺失遮罩、每諧波置信度與適用門控，而不使用普通歐氏相位差或以數值零取代缺失值。

`FARHP-Core-v0.1` 的工程域被刻意限制在理想諧波、穩定合成母音及單一短時有聲框架。原型提供 YIN 風格單框架基頻估計、複數諧波投影、`FARHP-Y` 輸出域物件、十六相標量量化、加權環面 $k$-means 碼本、諧波重建、JSON Schema 驗證、命令列工具、診斷圖與自動測試。

在內建合成母音閉環中，目標基頻為 $125$ Hz，估計值為 125.003695 Hz，絕對誤差為 0.003695 Hz；24 個諧波均通過遮罩，適用門控為 $\Gamma=4$。十六相量化的環面均方根角誤差為 0.113412 rad，小於理論單座標最壞誤差上界 0.196350 rad。七項自動測試全部通過，其中包括精確諧波條件下的時間平移不變性、分析—重建數值往返、圓周量化誤差界、環面碼本聚類及 FARHP-Spec-v0.1 驗證。

本文同時明確指出：上述結果只證明參考閉環的內部一致性，不證明 FARHP 已能獨立產生自然語音，也不證明其在真實華語、聲門生理或人類知覺上的優越性。下一篇必須轉向自然語音中的基頻誤差、諧波錯配、跨框架相位追蹤、聲源—聲道混合及不確定性反演。

**關鍵詞：** 語音分析合成、諧波模型、相位重建、基頻估計、圓周量化、環面碼本、可執行規格、聲碼器原型、FARHP-Core

---

# 0. 研究轉折：從理論物件到失敗得了的系統

## 0.1 為什麼第五篇必須實作

FARHP 前四篇已形成：

$$
\boxed{
\text{總體定義}
\rightarrow
\text{商環面數學}
\rightarrow
\text{聲學／知覺邊界}
\rightarrow
\text{離散表示與 AI 接口}
}
$$

若此時仍只繼續增加抽象層，會出現三個危險：

1. 數學不變量可能無法在有限窗、失諧及估計誤差下穩定取得；
2. 資料規格可能在真正序列化與重建時缺少必要欄位；
3. 「相位可控制聲音」可能被錯誤擴張成「相位足以生成語音」。

因此，本文採取工程可證偽立場：

> 一個聲學理論若無法形成可執行分析器、可逆資料物件及明確失敗條件，就仍未完成工程意義上的定義。

## 0.2 本篇的最低成功條件

本文不以「聽起來像真人」作為第一階段成功條件，而設定五個更基礎的門檻：

$$
\begin{aligned}
C_1&:\text{已知諧波訊號可被正確分析},\\
C_2&:\text{共同時間平移不改變 FARHP},\\
C_3&:\text{分析後的諧波模型可數值重建},\\
C_4&:\text{離散化誤差符合圓周理論界},\\
C_5&:\text{資料輸出符合 FARHP-Spec-v0.1}.
\end{aligned}
$$

只有這些條件成立，才值得進入真實語音、連續句及神經模型。

## 0.3 本篇不處理的事項

`v0.1` 明確排除：

- 完整聲門逆濾波；
- `FARHP-G` 的生理估計；
- 無聲擦音與爆破瞬態；
- 混合週期、雙基頻與強烈失諧；
- 聲道殘差及噪聲模型；
- 自然華語五聲的端到端合成；
- 主觀盲聽品質結論；
- 神經聲碼器訓練。

這不是功能不足的掩飾，而是為避免第一版同時失去數學可驗證性與工程可診斷性。

---

# 1. 系統總架構

## 1.1 七模組閉環

FARHP-Core 的最小閉環為：

$$
\boxed{
\text{Waveform}
\xrightarrow{A_0}
\widehat f_0
\xrightarrow{A_1}
\{\widehat A_k,\widehat\phi_k\}
\xrightarrow{A_2}
\widehat{\boldsymbol\psi}
\xrightarrow{E}
q
\xrightarrow{D}
\widetilde{\boldsymbol\psi}
\xrightarrow{S}
\widehat x[n]
}
$$

其中：

- $A_0$：基頻估計；
- $A_1$：諧波複係數估計；
- $A_2$：FARHP 抽取；
- $E$：連續或離散編碼；
- $D$：解碼；
- $S$：諧波合成；
- 旁路模組：遮罩、置信度、適用門控與規格驗證。

## 1.2 資料平面與控制平面

系統必須分離兩類資訊。

### 資料平面

$$
\mathcal D_t
=
\left(
\mathbf A_t,
\boldsymbol\psi_t,
\mathbf m_t,
\mathbf c_t
\right).
$$

### 控制平面

$$
\mathcal C_t
=
\left(
f_0(t),
\phi_1(t),
\Gamma_t,
\chi_t,
\mathcal V
\right).
$$

其中 $\chi_t$ 表示來源與分析條件，$\mathcal V$ 表示規格與碼本版本。若只傳送 $\boldsymbol\psi_t$ 而遺失基頻、錨相位、振幅或遮罩，則無法形成可重建聲音。

## 1.3 FARHP 不是單獨聲碼器

本文將 FARHP 定位為**相位子系統**。完整語音聲碼器至少需要：

$$
\mathfrak S
=
\left(
\text{pitch},
\text{spectral envelope},
\text{aperiodicity},
\text{phase},
\text{duration},
\text{transient}
\right).
$$

WORLD 等聲碼器也將基頻、頻譜包絡與非週期性分解為不同參數；本文的 FARHP 應被理解為在此類分層架構中補充或重構相位表達，而不是以一個相位向量取代整套語音參數。

---

# 2. 輸入、分框與適用門控

## 2.1 單框架模型

第一版處理長度 $N$ 的實數框架：

$$
x_t[n],
\qquad n=0,1,\ldots,N-1.
$$

原型預設：

- 取樣率：$16\,000$ Hz；
- 框架長度：$80$ ms；
- 目標基頻範圍：$70$–$350$ Hz；
- 最大諧波數：24 或受 Nyquist 頻率限制的更小值。

較長框架可提高低基頻週期解析度，卻會增加聲音非平穩性；因此框架長度不是固定真理，而是估計偏差與時間解析度的折衷。

## 2.2 平均值移除與窗函數

分析前可移除直流分量：

$$
x'[n]=x[n]-\frac1N\sum_{n=0}^{N-1}x[n].
$$

一般分析採 Hann 窗：

$$
w[n]=\frac12\left(1-\cos\frac{2\pi n}{N-1}\right).
$$

但形式測試使用矩形窗與整數週期框架，以建立近乎精確的代數基準。這兩種模式不可混為同一種誤差條件。

## 2.3 適用門控

第三篇定義：

$$
\Gamma\in\{0,1,2,3,4\}.
$$

原型依基頻置信度與有效諧波比例產生初步門控：

- $\Gamma=4$：高可信、強週期、足夠諧波；
- $\Gamma=3$：可作正常研究分析；
- $\Gamma=2$：僅限條件性使用；
- $\Gamma=1$：探索性輸出；
- $\Gamma=0$：不應輸出普通語言相位 token。

此規則只是參考啟發式，不是語音學標準。第六篇需改為可校準分類器或機率門控。

---

# 3. 基頻估計器

## 3.1 YIN 風格差分函數

原型使用 YIN 風格單框架估計。對延遲 $\tau$：

$$
d(\tau)
=
\sum_{j=0}^{N-\tau-1}
\left(x[j]-x[j+\tau]\right)^2.
$$

再定義累積平均正規差分：

$$
d'(\tau)
=
\begin{cases}
1,&\tau=0,\\
\displaystyle
\frac{d(\tau)}{\frac1\tau\sum_{j=1}^\tau d(j)},&\tau>0.
\end{cases}
$$

理想週期處，$d'(\tau)$ 接近零。YIN 原始論文提出此類差分與正規化以降低自相關音高估計的部分錯誤；本文只實作其適合單框架原型的簡化形式，不能宣稱與完整 YIN 追蹤器等價。

## 3.2 候選選擇修正

第一輪測試發現，合成母音的共振峰加權可在真正週期之前形成局部低谷，導致錯選較高基頻。因此參考實作不是單純選「第一個低於門檻」的延遲，而是：

1. 收集合法範圍內的局部極小值；
2. 找出全域最佳正規差分值；
3. 保留接近最佳值的候選；
4. 在近最佳候選中選最早延遲。

這仍只是倍頻／半頻錯誤的第一道防線。自然語音需加入跨框架動態、頻譜諧波一致性與音高先驗。

## 3.3 基頻置信度

原型定義：

$$
c_{f_0}
=
\operatorname{clip}
\left(1-d'(\widehat\tau),0,1\right).
$$

這不是校準後機率，只是內部品質分數。規格中使用 `f0_confidence`，不應將它直接解讀為「估計正確的真實機率」。

---

# 4. 諧波複係數與 FARHP 抽取

## 4.1 複數投影

給定 $\widehat f_0$，第 $k$ 次諧波複係數估計為：

$$
\widehat X_k
=
\frac{2}{\sum_n w[n]}
\sum_{n=0}^{N-1}
x[n]w[n]
\exp\left(-i2\pi k\widehat f_0\frac n{F_s}\right).
$$

再取：

$$
\widehat A_k=|\widehat X_k|,
\qquad
\widehat\phi_k=\arg\widehat X_k.
$$

這是固定頻率的局部複數投影，而非完整峰值追蹤器。當諧波偏離 $k\widehat f_0$、窗函數洩漏或框架內 $f_0$ 變動時，係數會同時產生振幅與相位偏差。

## 4.2 基錨相差

抽取式為：

$$
\widehat\psi_k
=
\operatorname{wrap}
\left(
\widehat\phi_k-k\widehat\phi_1
\right).
$$

向量形式：

$$
\widehat{\boldsymbol\psi}
=
\left(
\widehat\psi_2,
\ldots,
\widehat\psi_K
\right)
\in\mathbb T^{K-1}.
$$

第一諧波位置在資料物件中保留為零：

$$
\widehat\psi_1=0,
$$

但 FARHP 的真正自由座標仍從 $k=2$ 開始。

## 4.3 時間平移不變性測試

若理想訊號平移 $\tau$：

$$
\phi'_k
=
\phi_k+2\pi kf_0\tau,
$$

則：

$$
\begin{aligned}
\psi'_k
&=
\operatorname{wrap}
\left(
\phi_k+2\pi kf_0\tau
-k(\phi_1+2\pi f_0\tau)
\right)\\
&=
\operatorname{wrap}(\phi_k-k\phi_1)\\
&=\psi_k.
\end{aligned}
$$

內建測試使用整數週期框架、矩形窗與已知 $f_0$，比較兩個不同時間原點的同一諧波訊號；環面距離小於 $10^{-9}$ rad。此結果驗證實作符合第二篇的理想不變性定理，但不代表有限窗自然語音也會達到同一數值精度。

## 4.4 遮罩與置信度

每個諧波建立：

$$
m_k\in\{0,1\},
\qquad
c_k\in[0,1].
$$

原型以相對振幅門檻決定遮罩，並將振幅品質與 $f_0$ 置信度相乘形成座標置信度。這是一個容易診斷的基線，而不是最終統計估計器。

重要規則仍然是：

$$
\boxed{\text{missing}\neq 0}.
$$

---

# 5. FARHPFrame 與 FARHP-Spec-v0.1

## 5.1 內部資料物件

原型使用：

$$
\mathfrak F_t
=
\left(
F_s,t,N,
\widehat f_0,c_{f_0},\Gamma,
\mathbf k,
\mathbf A,
\boldsymbol\phi,
\boldsymbol\psi,
\mathbf m,
\mathbf c,
\phi_1,
\chi
\right).
$$

其 `FARHPFrame` 同時保存：

- 基頻與框架資訊；
- 諧波索引；
- 振幅；
- 絕對相位；
- FARHP；
- 遮罩與置信度；
- 錨相位；
- `Y/G` 來源域；
- 分析器版本與中繼資料。

## 5.2 交換物件

輸出的 JSON 符合 FARHP-Spec-v0.1 Level 0，並加入參考實作所需的 `harmonics` 擴充欄位。核心相位欄位為：

```json
{
  "phase": {
    "representation": "angle_rad",
    "harmonic_indices": [2, 3, 4],
    "values": [0.3, -1.1, 2.2],
    "mask": [1, 1, 0],
    "confidence": [0.98, 0.91, 0.08]
  }
}
```

規格容許額外欄位，使分析器、聲碼器與研究資料集可擴充，但不得破壞必要語義。

## 5.3 來源域

本原型只正式輸出：

$$
\texttt{domain = Y}.
$$

`FARHP-G` 需要逆濾波方法、版本與不確定性欄位。任何未經聲門逆濾波的輸出都不得標示為 `G`。

---

# 6. 圓周量化與環面碼本

## 6.1 標量圓周量化

對 $M$ 相量化：

$$
q_k
=
\operatorname{round}
\left(
\frac{M}{2\pi}
(\psi_k\bmod 2\pi)
\right)
\bmod M.
$$

解碼：

$$
\widetilde\psi_k
=
\operatorname{wrap}
\left(
\frac{2\pi q_k}M
\right).
$$

單座標最壞測地誤差為：

$$
\epsilon_{\max}
=
\frac\pi M.
$$

當 $M=16$：

$$
\epsilon_{\max}
=
\frac\pi{16}
\approx 0.19635\text{ rad}.
$$

內建隨機測試驗證所有樣本均不超過此界。

## 6.2 加權環面距離

對兩個相位向量：

$$
d_\mathbb T
(\boldsymbol\psi,\boldsymbol\eta)
=
\sqrt{
\frac{
\sum_k w_km_k
\operatorname{wrap}(\psi_k-\eta_k)^2
}{
\sum_k w_km_k
}
}.
$$

這個距離同時避免包覆邊界錯誤，並排除缺失座標。

## 6.3 環面 $k$-means

聯合碼本中心不是普通算術平均，而是逐座標圓周平均：

$$
\mu_k
=
\arg
\left(
\sum_j m_{j,k}e^{i\psi_{j,k}}
\right).
$$

參考實作提供：

- 隨機樣本初始化；
- 加權環面分派；
- 圓周中心更新；
- 空碼字以最遠樣本重新初始化；
- OOD 距離輸出。

它是研究用小型碼本，不適合直接處理大規模資料。後續可替換為 mini-batch、乘積碼本、分層殘差碼本或可微向量量化。

---

# 7. 諧波重建器

## 7.1 重建公式

保存錨相位 $\phi_1$ 後，各諧波相位為：

$$
\widehat\phi_k
=
\operatorname{wrap}
\left(k\phi_1+\psi_k\right).
$$

框架重建：

$$
\widehat x[n]
=
\sum_{k=1}^K
m_kA_k
\cos\left(
2\pi kf_0\frac n{F_s}
+k\phi_1+\psi_k
\right).
$$

## 7.2 為什麼必須保存錨相位

FARHP 消除了共同時間平移自由度，因此只保存 $\boldsymbol\psi$ 時，訊號仍缺少一個週期時鐘座標。若只要求聲音等價類，任意選擇 $\phi_1$ 即可；若要求框架波形數值重建，就必須保存或連續傳播 $\phi_1$。

因此：

$$
\boxed{
\text{FARHP 不變量}
+
\text{錨相位規範}
=
\text{可定位諧波相位}
}
$$

## 7.3 分框與重疊相加

原型提供基本 overlap-add 接口，但尚未宣稱連續語音重建穩定。跨框架系統必須處理：

- $\phi_1(t)$ 的時間連續性；
- $f_0(t)$ 積分形成的瞬時相位；
- token 重同步；
- 窗函數平方和；
- 諧波出生與消失；
- 有聲／無聲邊界。

這些將成為第六與第七篇的核心。

## 7.4 殘差缺口

真實聲音應寫成：

$$
x[n]
=
x_{\mathrm{harm}}[n]
+r[n].
$$

`v0.1` 只重建 $x_{\mathrm{harm}}$。若輸入包含送氣、摩擦、爆破、混響或噪聲，重建一定遺失 $r[n]$。因此本文的 WAV 範例不是完整語音壓縮結果，而是諧波相位閉環證書。

---

# 8. 可執行參考實作

## 8.1 模組

```text
src/farhp/
  analyzer.py       基頻估計、諧波投影與 FARHP 抽取
  model.py          FARHPFrame 與 Spec 交換物件
  synth.py          理想諧波與合成母音
  reconstructor.py  框架重建與基本 overlap-add
  quantizer.py      圓周標量量化
  codebook.py       加權環面碼本
  schema.py         JSON Schema 驗證
  inspector.py      波形、振幅與 FARHP 診斷圖
  io.py             WAV／JSON 讀寫
  cli.py            命令列介面
```

## 8.2 命令列閉環

```bash
python -m farhp demo --out artifacts/demo
```

輸出：

```text
synthetic_vowel.wav
farhp_frame.json
reconstructed_frame.wav
farhp_inspector.png
demo_report.json
```

規格驗證：

```bash
python -m farhp validate \
  artifacts/demo/farhp_frame.json \
  --schema spec/FARHP_Spec_v0.1.schema.json
```

## 8.3 合成母音不是語音真值

原型以幾個高斯共振峰模板塑造諧波振幅包絡：

$$
A_k
\propto
\frac1{k^\alpha}
\left(
\epsilon+
\sum_jg_j
\exp\left[-\frac12
\left(\frac{kf_0-F_j}{\sigma_j}
\right)^2
\right]
\right).
$$

此訊號只用於回歸測試，不代表標準華語母音、特定說話者或生理聲道模型。

---

# 9. 驗證與基準

## 9.1 七項自動測試

`FARHP-Core-v0.1` 目前通過：

1. 相位包覆與圓周距離；
2. 十六相量化誤差上界；
3. 合成母音基頻估計；
4. 精確諧波的時間平移不變性；
5. 諧波分析—重建數值往返；
6. 二群環面碼本聚類；
7. FARHP-Spec-v0.1 JSON Schema 驗證。

測試結果：

```text
Ran 7 tests
OK
```

## 9.2 形式閉環測試

在矩形窗、整數週期、已知 $f_0$ 與純諧波條件下：

$$
\operatorname{RMS}
\left(x-\widehat x\right)
<10^{-10}.
$$

此測試證明程式中的分析與合成相位符號一致，不證明自然語音可無損重建。

## 9.3 合成母音示範

示範條件：

- 母音模板：`a`；
- $F_s=16\,000$ Hz；
- $f_0=125$ Hz；
- 框架長度：$80$ ms；
- 最大諧波數：24；
- Hann 窗；
- 十六相量化。

結果：

| 指標 | 結果 |
|---|---:|
| 目標 $f_0$ | $125.000000$ Hz |
| 估計 $f_0$ | 125.003695 Hz |
| 絕對誤差 | 0.003695 Hz |
| $f_0$ 置信度 | 1.000 |
| 適用門控 | $\Gamma=4$ |
| 有效諧波 | 24/24 |
| 十六相環面 RMSE | 0.113412 rad |
| 單座標理論最壞界 | 0.196350 rad |
| 原框架 RMS | 0.316120 |
| 重建框架 RMS | 0.316030 |

## 9.4 可以主張與不可以主張的結果

### 可以主張

- FARHP 定義已形成可執行資料流；
- 理想諧波條件下，時間平移不變性可由程式驗證；
- 保存振幅、基頻、錨相位及 FARHP 時，可重建諧波波形；
- 圓周標量量化符合幾何誤差界；
- 交換物件可通過既定 Schema。

### 不可以主張

- FARHP 已優於最小相位、WORLD、STRAIGHT 或神經聲碼器；
- 合成母音結果代表自然語音品質；
- `FARHP-Y` 等於聲門源相位；
- 十六相足以保存所有知覺重要相位；
- 當前基頻估計可可靠處理連續華語；
- 環面碼本已產生語言學音位。

---

# 10. 主要失敗模式

## 10.1 基頻倍頻與半頻錯誤

若：

$$
\widehat f_0=mf_0,
\qquad m\neq1,
$$

則諧波身份本身被重新索引，FARHP 不再只是小角度擾動，而可能成為不同座標系中的物件。因此 $f_0$ 錯誤是 FARHP 分析最重要的上游故障。

## 10.2 錨點相位誤差的階數放大

若：

$$
\widehat\phi_1=\phi_1+\epsilon_1,
$$

則：

$$
\widehat\psi_k
\approx
\psi_k+\epsilon_k-k\epsilon_1.
$$

高次諧波受到 $k$ 倍錨誤差，因此高階相位不能只依振幅門檻判斷可靠度。

## 10.3 失諧

若第 $k$ 部分頻率為：

$$
f_k=kf_0+\delta_k,
$$

則不同框架位置會留下：

$$
2\pi\delta_k\tau
$$

的殘餘相位。理想不變性會退化為近似不變性。

## 10.4 窗函數與框架位置

有限窗會混合鄰近頻率，且框架內的振幅、頻率與相位變化會破壞固定正弦模型。Hann 窗降低洩漏，但不會自動消除偏差。

## 10.5 聲源—聲道不可唯一分解

第三篇已證明：

$$
\psi_k^{(y)}
=
\psi_k^{(g)}
+
\Delta_k\theta_v
+
\Delta_k\theta_r
+
\Delta_k\theta_m.
$$

所以輸出 FARHP 的可重建性不等於聲門來源的可識別性。

## 10.6 殘差與瞬態

對 $\Gamma=0$ 或 $1$ 的框架，強行輸出正常相位 token 會把噪聲或瞬態偽裝成諧波結構。系統需要 `NA`、`OOD`、殘差與非諧波路徑。

---

# 11. 工程安全與可重現性原則

## 11.1 不隱藏失敗

每個輸出應附：

- 分析器版本；
- $f_0$ 置信度；
- 每諧波遮罩；
- 每諧波置信度；
- 適用門控；
- 碼本識別碼；
- OOD 距離；
- 來源域。

## 11.2 不用 token 取代規格

裸整數 `187` 沒有可攜語義。必須至少附：

$$
(
\text{codebook-id},
\text{version},
\text{condition},
\text{token-index}
).
$$

## 11.3 測試資料與自然語音分離

合成測試可建立精確真值，但不能取代自然資料。兩種資料的用途不同：

- 合成資料：驗證代數與數值正確性；
- 自然語音：驗證穩健性、聲學效益與知覺價值。

## 11.4 輸出音訊不代表成功證書

「能產生 WAV」只表示程式可執行。真正研究證書應包括：

$$
\text{輸入條件}
+
\text{參數}
+
\text{誤差}
+
\text{失敗案例}
+
\text{版本雜湊}.
$$

---

# 12. 可證偽命題

## 命題 H5-1：理想不變性

在整數諧波、正確 $f_0$、共同時間平移與一致分析窗條件下：

$$
d_\mathbb T
\left(
\widehat{\boldsymbol\psi}(x),
\widehat{\boldsymbol\psi}(T_\tau x)
\right)
\rightarrow0.
$$

## 命題 H5-2：失諧線性殘餘

小失諧條件下，時間平移造成的 FARHP 殘餘相位與 $\delta_k\tau$ 近似線性。

## 命題 H5-3：聯合碼本優勢是條件性的

當多諧波相位存在穩定相關結構時，加權環面聯合碼本在相同碼率下應優於獨立標量量化；若資料接近獨立均勻分布，此優勢可消失。

## 命題 H5-4：置信度遮罩改善碼本穩定性

將弱諧波當作有效零角度輸入會造成碼本中心偏移；顯式遮罩及可靠度加權應降低跨分析器重訓偏差。

## 命題 H5-5：錨誤差主導高階座標

固定局部諧波估計誤差時，FARHP 高階座標的誤差方差應隨 $k^2\operatorname{Var}(\epsilon_1)$ 增長。

## 命題 H5-6：諧波閉環不等於知覺閉環

即使波形諧波重建誤差很低，若移除殘差、瞬態或聲道條件，人類知覺品質仍可能顯著下降。

---

# 13. 第六篇的直接接口

下一篇為：

**《自然語音中的基錨相差估計、追蹤與反演方法》**

其最低工作包應包括：

1. 多種 $f_0$ 估計器的可替換接口；
2. 跨框架動態規劃或機率音高追蹤；
3. 正弦峰值追蹤與失諧 $\delta_k$ 估計；
4. 相位解除包覆與錨相位連續傳播；
5. 有聲／無聲／混合門控；
6. 真實母音資料匯入；
7. `FARHP-Y` 的重測信度；
8. 第一版 `FARHP-G` 逆濾波實驗，但必須標示模型依賴；
9. 基頻、窗函數、麥克風及取樣率擾動基準；
10. 失敗案例資料集與回歸測試。

工程上可將目前閉環擴張為：

$$
\boxed{
\text{單框架理想諧波}
\rightarrow
\text{多框架合成母音}
\rightarrow
\text{短時真實母音}
\rightarrow
\text{連續自然語音}
}
$$

---

# 14. 結論

本文完成 FARHP 系列第一次真正的理論—工程閉環。其成果不是「一個已完成的新語音合成器」，而是一套不再只存在於公式中的研究核心：

$$
\boxed{
\text{FARHP 理論}
\rightarrow
\text{可執行分析器}
\rightarrow
\text{可驗證資料物件}
\rightarrow
\text{圓周離散碼}
\rightarrow
\text{可重建諧波波形}
}
$$

最重要的工程結論有三個。

第一，FARHP 必須和基頻、振幅、錨相位、遮罩、置信度與來源域一起存在。孤立相位 token 不是可攜聲學物件。

第二，理想時間平移不變性可以被數值測試，但自然語音中的失諧、有限窗與估計偏差會把精確不變量改造成帶誤差的近似不變量。

第三，第一版最有價值的成果不是音質，而是失敗可定位性：基頻錯誤、諧波錯配、錨誤差、缺失座標、碼本外樣本與殘差缺口都被分離為可測模組。

因此，FARHP 現在已從「可能的相位發音概念」進入「具備參考實作、規格、測試與反例接口的研究系統」。第六篇可以不再猜測如何抽取，而是直接拿本篇原型去撞擊自然語音，並讓實驗結果反過來修正理論。

---

# 附錄 A：FARHP-Core-v0.1 最低執行流程

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python -m farhp demo --out artifacts/demo
python -m farhp validate artifacts/demo/farhp_frame.json \
  --schema spec/FARHP_Spec_v0.1.schema.json
python -m unittest discover -s tests -v
```

# 附錄 B：核心 Python 介面

```python
from farhp.analyzer import AnalysisConfig, analyze_frame
from farhp.reconstructor import reconstruct_frame

frame = analyze_frame(
    waveform,
    sample_rate_hz=16000,
    config=AnalysisConfig(k_max=24),
)

farhp_object = frame.to_spec_object()
reconstructed = reconstruct_frame(frame)
```

# 附錄 C：版本相容性

| 層級 | 本版狀態 |
|---|---|
| Level 0：連續交換 | 已完成 |
| Level 1：標量離散 | 已完成參考實作 |
| Level 2：聯合碼本 | 已完成小型參考實作 |
| Level 3：動態 token | 僅完成規格，未完成序列器 |
| Level 4：語言整合 | 尚未開始 |

# 附錄 D：參考文獻

1. de Cheveigné, A., & Kawahara, H. (2002). *YIN, a fundamental frequency estimator for speech and music*. Journal of the Acoustical Society of America, 111(4), 1917–1930. DOI: 10.1121/1.1458024.
2. Saratxaga, I., Hernáez, I., Navas, E., & Sánchez, J. (2010). *Using harmonic phase information to improve ASR rate*. Interspeech 2010.
3. Mowlaee, P., Kulmer, J., Stahl, J., & Mayer, F. (2014). *Phase Importance in Speech Processing Applications*. Interspeech 2014.
4. Degottex, G., & Erro, D. (2014). *A uniform phase representation for the harmonic model in speech synthesis applications*. EURASIP Journal on Audio, Speech, and Music Processing, 2014:38.
5. Morise, M., Yokomori, F., & Ozawa, K. (2016). *WORLD: A Vocoder-Based High-Quality Speech Synthesis System for Real-Time Applications*. IEICE Transactions on Information and Systems, E99.D(7), 1877–1884.
6. McAulay, R. J., & Quatieri, T. F. (1986). *Speech analysis/synthesis based on a sinusoidal representation*. IEEE Transactions on Acoustics, Speech, and Signal Processing, 34(4), 744–754.
7. FARHP 系列第一至第四篇與 FARHP-Spec-v0.1，EveMissLab，2026。

---

**本文結束**
