# 自然語音中的基錨相差估計、追蹤與反演方法

## 從逐框架觀測到相位環面軌跡

**系列：基頻錨定相對諧波相位差（FARHP）第六篇**  
**英文題名：Estimation, Tracking, and Inversion of Fundamental-Anchored Relative Harmonic Phase in Natural Speech**  
**版本：v0.1**  
**日期：2026-07-26**  
**作者：Neo.K／EveMissLab；Aletheia／GPT-5.6 Thinking**  
**研究狀態：理論—工程橋接稿；含 FARHP-Core v0.2 參考實作**

---

## 摘要

前五篇已依序建立基頻錨定相對諧波相位差（Fundamental-Anchored Relative Harmonic Phase, FARHP）的母定義、商環面數學、聲源—聲道—知覺邊界、離散碼本與單框架分析—重建閉環。然而，自然語音不是一組彼此獨立的靜態框架。基本頻率會滑動，聲門週期會抖動，諧波會出生、消失、交錯，短時分析窗會移動，有聲與無聲區段會切換，聲道響應與聲源波形亦會持續變化。若每一框架單獨估計 $f_0$、絕對相位及 FARHP，再將結果直接串接，倍頻錯誤、相位包覆、弱諧波與有聲邊界會共同製造不可接受的跳變。

本文因此將 FARHP 從單框架物件提升為時間軌跡。核心方法分成兩條互相耦合、但不可混同的推論鏈：第一條以多候選 YIN 類週期證據與動態規劃取得 $f_0(t)$、有聲狀態及追蹤置信度；第二條以積分後的基頻預測錨相位，選擇最接近預測值的 $2\pi$ 分支，再於相位環面上對各諧波 FARHP 座標進行可靠度門控的時間解除包覆。本文亦定義未觀測值、無聲間隙、軌跡重啟、錨點殘差、相位速度、來源域及反演不唯一性，並提出 `FARHP-Trajectory-Spec-v0.2`。

配套工程 `FARHP-Core v0.2` 已完成多框架分析、動態 $f_0$ 追蹤、錨相位傳播、FARHP 軌跡解除包覆、JSON 交換、診斷圖與諧波式 overlap-add 重建。在一組具滑音、顫音、相位微擾及微量氣聲噪聲的動態合成母音回歸測試中，參考實作取得 $0.279$ Hz 的 $f_0$ 平均絕對誤差，以及 $0.108$ rad 的錨相位預測殘差中位數；十三項自動測試全部通過。這些結果只證明演算法與資料結構在受控訊號上的一致性，尚不構成自然語音品質或生理聲門反演的實證結論。

**關鍵詞：** 基頻錨定相對諧波相位差、FARHP、相位追蹤、相位解除包覆、基頻追蹤、動態規劃、諧波模型、自然語音、聲門反演、相位環面

---

# 1. 問題的真正轉折：從框架集合到軌跡物件

在單框架模型中，第 $t$ 個分析框架的第 $k$ 個諧波複係數寫為：

$$
X_{t,k}=A_{t,k}e^{i\phi_{t,k}}.
$$

以第一諧波為錨，FARHP 座標定義為：

$$
\psi_{t,k}
=
\operatorname{wrap}
\left(
\phi_{t,k}-k\phi_{t,1}
\right),
\qquad k\ge 2.
$$

這個定義消去了理想共同時間平移造成的線性相位項。但是，「單一框架對共同時間平移不變」不代表「跨框架估計天然連續」。至少有五個原因：

1. $f_0$ 的框架估計會出現整倍頻或半倍頻錯誤；
2. 每個絕對相位只在模 $2\pi$ 意義下可見；
3. 分析窗的位置、長度與頻率失配會改變複投影；
4. 弱諧波可能在相鄰框架間進出遮罩；
5. 自然語音的 FARHP 本來就可能隨聲門源、聲道與發音狀態演化。

因此，真正需要估計的不是：

$$
\{\boldsymbol\psi_t\}_{t=1}^{T}
$$

這種彼此無關的框架集合，而是：

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

其中：

- $\mathbf f_0$：基本頻率軌跡；
- $\mathbf v$：有聲／無聲狀態；
- $\mathbf c$：追蹤置信度；
- $\boldsymbol\Phi_1$：解除包覆後的錨相位軌跡；
- $\boldsymbol\Psi$：解除包覆後的 FARHP 軌跡代表；
- $\dot{\boldsymbol\Psi}$：FARHP 的時間速度；
- $\mathbf M$：諧波可用遮罩；
- $\mathbf C$：每諧波置信度；
- $\mathcal G$：間隙、重啟與來源域政策。

這個軌跡物件才是第七篇進行音色轉換、新音生成與動態相位控制時真正需要的資料基礎。

---

# 2. 與既有方法的關係

本文不是從零發明音高追蹤、正弦模型或相位解除包覆。其直接技術祖先至少包括：

- YIN 對語音與音樂基本頻率的差分函數及累積平均正規化；
- pYIN 將多個 $f_0$ 候選與機率分布送入序列解碼；
- McAulay–Quatieri 正弦模型對跨框架頻率、振幅與相位的追蹤；
- Relative Phase Shift 對諧波相對相位的表示；
- harmonic-model phase representation 對線性相位項、解除包覆與統計模型兼容性的處理；
- 時頻相位重建中對水平與垂直相位一致性的研究。

FARHP 第六篇的新增工作不是宣稱上述方法不存在，而是將它們重新組織到一個特定目標下：

$$
\boxed{
\text{在保持 FARHP 商環面語義的前提下，
建立可交換、可追蹤、可重建的時間軌跡。}
}
$$

主要差異包括：

1. $f_0$ 路徑與 FARHP 路徑分離建模；
2. 錨相位具有明確的積分預測與分支選擇規則；
3. FARHP 解除包覆被定義為環面座標上的局部代表選擇，而不是把包覆值誤當成唯一真值；
4. 無聲間隙、缺失諧波與低置信度被納入資料本體；
5. `FARHP-Y` 與 `FARHP-G` 的反演層級保持分離；
6. 軌跡資料提供 JSON 規格及可執行參考實作。

---

# 3. 觀測模型

## 3.1 局部諧波模型

在短時間有聲區段中，令：

$$
x_t[n]
\approx
\sum_{k=1}^{K_t}
A_{t,k}
\cos
\left(
2\pi f_{t,k}\frac{n}{F_s}
+
\phi_{t,k}
\right)
+
r_t[n].
$$

理想諧波條件為：

$$
f_{t,k}=k f_0(t).
$$

自然語音則可能具有：

$$
f_{t,k}=k f_0(t)+\delta_{t,k},
$$

其中 $\delta_{t,k}$ 包含估計誤差、非週期性、分析窗偏差、源—濾波耦合與局部失諧。

## 3.2 包覆相位觀測

實際取得的是：

$$
\widetilde\phi_{t,k}
=
\operatorname{wrap}
\left(
\Phi_{t,k}+\varepsilon_{t,k}
\right),
$$

其中 $\Phi_{t,k}\in\mathbb R$ 是某個連續相位代表，$\varepsilon_{t,k}$ 是投影與雜訊誤差。因為：

$$
\Phi_{t,k}
\sim
\Phi_{t,k}+2\pi m,
\qquad m\in\mathbb Z,
$$

單靠一個框架不能決定整數分支。跨框架追蹤的任務，就是用動力學預測、頻率連續性與可靠度，選擇局部一致的代表。

## 3.3 FARHP 觀測

框架內包覆 FARHP 為：

$$
\widetilde\psi_{t,k}
=
\operatorname{wrap}
\left(
\widetilde\phi_{t,k}
-k\widetilde\phi_{t,1}
\right).
$$

由於錨相位誤差會乘上 $k$，若：

$$
\widetilde\phi_{t,1}=\phi_{t,1}+\epsilon_{t,1},
$$

則一階近似下：

$$
\widetilde\psi_{t,k}-\psi_{t,k}
\approx
\epsilon_{t,k}-k\epsilon_{t,1}.
$$

這說明為什麼高次諧波的 FARHP 置信度不能只看自身振幅，也必須乘入錨點置信度。

---

# 4. 第一條推論鏈：$f_0$ 與有聲狀態追蹤

## 4.1 為什麼不能逐框架只選一個最低點

對每個框架直接取 YIN 類函數的單一最佳延遲，會在下列情況失敗：

- 第二或第三諧波較強；
- 聲道共振峰加權造成假週期低谷；
- 框架太短；
- 基頻快速滑動；
- 有聲邊界混入噪聲；
- 基頻候選彼此為倍頻關係。

因此，第六篇使用候選集合：

$$
\mathcal F_t
=
\left\{
(f_{t,j},p_{t,j})
\right\}_{j=1}^{J_t}
\cup
\{\varnothing\}.
$$

$\varnothing$ 表示無聲狀態。

## 4.2 YIN 類差分與正規化

差分函數為：

$$
d_t(\tau)
=
\sum_n
\left(
 x_t[n]-x_t[n+\tau]
\right)^2.
$$

累積平均正規化差分為：

$$
d'_t(\tau)
=
\begin{cases}
1,&\tau=0,\\[4pt]
\dfrac{d_t(\tau)}{\frac{1}{\tau}\sum_{j=1}^{\tau}d_t(j)},&\tau>0.
\end{cases}
$$

候選週期來自 $d'_t(\tau)$ 的局部極小值，候選基本頻率為：

$$
f_{t,j}=\frac{F_s}{\tau_{t,j}}.
$$

參考實作使用拋物線局部細化，並以：

$$
p_{t,j}\approx 1-d'_t(\tau_{t,j})
$$

形成簡化週期置信度。這不是 pYIN 的完整機率模型，只是一個低依賴、可審閱的研究原型。

## 4.3 動態路徑代價

令第 $t$ 框架選擇狀態 $s_t$。累積代價為：

$$
C_t(j)
=
E_t(j)
+
\min_i
\left[
C_{t-1}(i)+T(i,j)
\right].
$$

有聲候選的發射代價可寫為：

$$
E_t(j)
=-\log
\left(
\widetilde p_{t,j}+\epsilon
\right).
$$

有聲—有聲轉移代價使用對數頻率距離：

$$
T(i,j)
=
\lambda_f
\left|
\log_2\frac{f_{t,j}}{f_{t-1,i}}
\right|
+
\lambda_o
\max
\left(
0,
\left|
\log_2\frac{f_{t,j}}{f_{t-1,i}}
\right|-\frac12
\right).
$$

有聲—無聲切換另加：

$$
\lambda_{vu}.
$$

這個設計不宣稱所有語音都平滑，而是表達一個弱先驗：在沒有足夠觀測證據時，連續路徑比突發整倍頻跳躍更可信。

## 4.4 追蹤置信度

每框架置信度至少由以下因素組成：

$$
c_t^{(f_0)}
=
C
\left(
 p_t^{\mathrm{period}},
 e_t,
 \Delta f_t,
 m_t^{\mathrm{path}}
\right),
$$

其中：

- $p_t^{\mathrm{period}}$：週期證據；
- $e_t$：框架能量；
- $\Delta f_t$：相鄰頻率變化；
- $m_t^{\mathrm{path}}$：最佳與次佳路徑差距。

參考實作 v0.2 尚未計算完整路徑後驗，只輸出候選週期置信度與選定路徑。未來版本應加入前向—後向推論或候選邊際機率。

---

# 5. 第二條推論鏈：錨相位傳播

## 5.1 基頻積分是錨相位的動力學骨架

對連續基本頻率：

$$
\frac{d\Phi_1(t)}{dt}
=
2\pi f_0(t).
$$

因此：

$$
\Phi_1(t_b)
=
\Phi_1(t_a)
+
2\pi
\int_{t_a}^{t_b}f_0(u)\,du.
$$

在離散框架中，以梯形近似：

$$
\widehat\Phi_{t,1}^{-}
=
\widehat\Phi_{t-1,1}
+
2\pi
\frac{f_0(t-1)+f_0(t)}{2}
\Delta t.
$$

$\widehat\Phi_{t,1}^{-}$ 是先驗預測值。

## 5.2 最近分支選擇

觀測錨相位為 $\widetilde\phi_{t,1}\in(-\pi,\pi]$。選擇整數分支：

$$
m_t^*
=
\arg\min_{m\in\mathbb Z}
\left|
\widetilde\phi_{t,1}+2\pi m
-
\widehat\Phi_{t,1}^{-}
\right|.
$$

於是：

$$
\widehat\Phi_{t,1}
=
\widetilde\phi_{t,1}+2\pi m_t^*.
$$

等價地：

$$
\widehat\Phi_{t,1}
=
\widehat\Phi_{t,1}^{-}
+
\operatorname{wrap}
\left(
\widetilde\phi_{t,1}
-
\widehat\Phi_{t,1}^{-}
\right).
$$

定義錨相位創新殘差：

$$
r_{t,1}
=
\operatorname{wrap}
\left(
\widetilde\phi_{t,1}
-
\widehat\Phi_{t,1}^{-}
\right).
$$

$r_{t,1}$ 是重要診斷量：它同時反映 $f_0$ 積分誤差、局部相位投影誤差、框架時標不一致及真實非平穩性。

## 5.3 分支唯一性的局部條件

如果預測誤差滿足：

$$
\left|
\Phi_{t,1}
-
\widehat\Phi_{t,1}^{-}
\right|
<\pi,
$$

最近分支是唯一的。若誤差超過 $\pi$，局部最近分支可能選錯一個或多個週期。

因此需要：約束 $\Delta t$、控制 $f_0$ 粗差、監測有聲間隙，並在低置信度時停止連續傳播。

## 5.4 $f_0$ 誤差的積分累積

若：

$$
\widehat f_0(t)=f_0(t)+\epsilon_f(t),
$$

則錨相位預測誤差為：

$$
\epsilon_{\Phi_1}(t_b)
=
2\pi
\int_{t_a}^{t_b}
\epsilon_f(u)\,du.
$$

即使 $\epsilon_f$ 很小，長時間積分也會累積。這說明第六篇不能只依賴自由運行的相位積分；每一可靠框架都必須以包覆觀測重新校正分支。

---

# 6. FARHP 軌跡的環面解除包覆

## 6.1 包覆 FARHP 並不需要全域唯一解除

單框架 FARHP 位於：

$$
\boldsymbol\psi_t
\in
\mathbb T^{K_t-1}.
$$

時間序列則是環面上的路徑：

$$
\gamma:
 t\mapsto\boldsymbol\psi_t.
$$

「解除包覆」不是發現某個宇宙唯一的實數向量，而是在局部連續假設下，為環面路徑選擇一個方便計算的提升：

$$
\widetilde\gamma:
 t\mapsto\boldsymbol\Psi_t
\in
\mathbb R^{K-1},
$$

使得：

$$
\boldsymbol\Psi_t
\bmod 2\pi
=
\boldsymbol\psi_t.
$$

## 6.2 每諧波最近分支

若第 $k$ 個 FARHP 座標在相鄰框架皆有效，則：

$$
\widehat\Psi_{t,k}
=
\widehat\Psi_{t-1,k}
+
\operatorname{wrap}
\left(
\widetilde\psi_{t,k}
-
\widehat\Psi_{t-1,k}
\right).
$$

其局部速度為：

$$
\dot\Psi_{t,k}
\approx
\frac{
\widehat\Psi_{t,k}-\widehat\Psi_{t-1,k}
}{\Delta t}.
$$

這個速度不是第 $k$ 諧波的瞬時頻率；它描述的是**相對於基頻時鐘的諧波相位結構變化率**。

## 6.3 為什麼 FARHP 速度可能具有聲學意義

由：

$$
\Psi_k(t)
=
\Phi_k(t)-k\Phi_1(t),
$$

可得：

$$
\frac{d\Psi_k}{dt}
=
2\pi
\left(
 f_k(t)-k f_0(t)
\right).
$$

在純理想整數諧波且相對波形不變時：

$$
\dot\Psi_k(t)=0.
$$

若：

$$
\dot\Psi_k(t)\ne0,
$$

可能來自：

- 真實局部失諧；
- 聲門脈衝形狀變化；
- 聲道相位響應變化；
- 分析窗與頻率偏差；
- 錨點錯誤；
- 諧波身份錯配。

因此，$\dot\Psi_k$ 是診斷量，不可直接被解釋成單一生理機制。

## 6.4 環面整體距離

對相鄰框架，可定義加權環面速度尺度：

$$
D_t
=
\frac{1}{\Delta t}
\sqrt{
\frac{
\sum_{k=2}^{K}
 w_{t,k}
 d_{S^1}
 \left(
 \psi_{t,k},
 \psi_{t-1,k}
 \right)^2
}{
\sum_{k=2}^{K}w_{t,k}
}
},
$$

其中：

$$
w_{t,k}
=
m_{t,k}m_{t-1,k}
 c_{t,k}c_{t-1,k}.
$$

$D_t$ 可用於：

- 偵測相位結構突變；
- 找出錯誤 $f_0$ 路徑；
- 決定軌跡是否重啟；
- 建立動態碼本；
- 分析音節邊界與聲門狀態轉換。

---

# 7. 缺失值、無聲區段與軌跡重啟

## 7.1 零不是缺失值

若諧波不可用，必須記為：

$$
\mathrm{null}
$$

或：

$$
m_{t,k}=0,
$$

不能記為：

$$
\psi_{t,k}=0.
$$

因為 $0$ 是合法相位值，代表與錨時鐘對齊，不代表沒有觀測。

## 7.2 無聲間隙

當：

$$
v_t=0,
$$

第一諧波錨失去可操作意義。預設政策應是：

$$
\boxed{
\text{無聲間隙後重新初始化錨相位與 FARHP 提升。}
}
$$

除非系統另有：

- 聲門脈衝外部感測；
- 高可信度隱狀態模型；
- 跨間隙週期推斷；
- 特定發音機制先驗。

否則不應把無聲區段兩側的解除包覆相位假裝成天然連續。

## 7.3 弱諧波重現

若第 $k$ 個諧波在若干框架後重新出現，可有三種政策：

1. **重啟：** 直接以當前包覆值作為新代表；
2. **預測橋接：** 由歷史相位速度外推，再選最近分支；
3. **統計橋接：** 用動態碼本或序列模型估計後驗。

`FARHP-Core v0.2` 採保守重啟政策。這降低了錯誤延續，但犧牲跨缺失區段的全域連續性。

---

# 8. 可靠度與不確定性傳播

## 8.1 最低限度的可靠度因子

第 $t$ 框架第 $k$ 諧波的可靠度可分解為：

$$
c_{t,k}
=
C
\left(
 c_t^{(f_0)},
 c_{t,1}^{(A)},
 c_{t,k}^{(A)},
 c_{t,k}^{(\mathrm{fit})},
 c_{t,k}^{(\mathrm{track})}
\right).
$$

其中：

- $c_t^{(f_0)}$：基頻路徑置信度；
- $c_{t,1}^{(A)}$：錨諧波振幅可靠度；
- $c_{t,k}^{(A)}$：目標諧波振幅可靠度；
- $c_{t,k}^{(\mathrm{fit})}$：局部正弦擬合品質；
- $c_{t,k}^{(\mathrm{track})}$：跨框架身份一致性。

參考實作目前使用：

$$
c_{t,k}^{\mathrm{v0.2}}
=
 c_t^{(f_0)}
 c_{t,k}^{(A)}.
$$

這只是最低可行版本。

## 8.2 錨點誤差放大

FARHP 的誤差變異近似為：

$$
\operatorname{Var}(\epsilon_{\psi_k})
=
\operatorname{Var}(\epsilon_{\phi_k})
+k^2\operatorname{Var}(\epsilon_{\phi_1})
-2k\operatorname{Cov}
\left(
\epsilon_{\phi_k},
\epsilon_{\phi_1}
\right).
$$

若忽略協方差，高次諧波會因錨誤差呈 $k^2$ 放大。因此：

- 高次諧波應使用更嚴格的遮罩；
- 碼本權重不能只依頻譜能量；
- 錨點置信度下降時，整個 FARHP 向量都應降權；
- 不應把所有 $k$ 使用相同損失權重。

## 8.3 建議的動態權重

可定義：

$$
w_{t,k}
=
\frac{
 m_{t,k}
 c_{t,k}
 A_{t,k}^{\alpha}
}{
1+\beta k^2\sigma_{t,1}^2
},
$$

其中 $\sigma_{t,1}^2$ 是錨相位不確定性。這可直接接入第七篇的動態相位損失與感知實驗。

---

# 9. 反演：從 `FARHP-Y` 到 `FARHP-G`

## 9.1 輸出域的可測量性

麥克風輸出複頻譜可寫成：

$$
Y_{t,k}
=
G_{t,k}
V_{t,k}
R_{t,k}
M_{t,k},
$$

對應相位：

$$
\phi^{(Y)}_{t,k}
=
\phi^{(G)}_{t,k}
+
\theta^{(V)}_{t,k}
+
\theta^{(R)}_{t,k}
+
\theta^{(M)}_{t,k}
\pmod{2\pi}.
$$

因此輸出域 FARHP 為：

$$
\psi^{(Y)}_{t,k}
=
\psi^{(G)}_{t,k}
+
\Delta_k\theta^{(V)}_t
+
\Delta_k\theta^{(R)}_t
+
\Delta_k\theta^{(M)}_t
\pmod{2\pi}.
$$

`FARHP-Y` 是可直接量測的複合物件。

## 9.2 聲門域反演

若有聲道估計 $\widehat V_{t,k}$、輻射模型 $\widehat R_{t,k}$ 及量測校正 $\widehat M_{t,k}$，可估計：

$$
\widehat G_{t,k}
=
\frac{
Y_{t,k}
}{
\widehat V_{t,k}
\widehat R_{t,k}
\widehat M_{t,k}
}.
$$

再定義：

$$
\widehat\psi^{(G)}_{t,k}
=
\operatorname{wrap}
\left(
\arg\widehat G_{t,k}
-k\arg\widehat G_{t,1}
\right).
$$

但這個反演不是唯一的。不同聲源—聲道分解、全通成分、聲門閉合時刻假設與正則化都可能產生不同的 `FARHP-G`。

所以資料必須明確標示：

- `domain: Y` 或 `domain: G`；
- 逆濾波方法；
- 聲道階數；
- 閉合相位估計法；
- 極性政策；
- 外部 EGG 是否存在；
- 反演置信度。

## 9.3 正則化反演

一個可研究的目標函數是：

$$
\mathcal L
=
\mathcal L_{\mathrm{wave}}
+
\lambda_s\mathcal L_{\mathrm{spectral}}
+
\lambda_p\mathcal L_{\mathrm{phase}}
+
\lambda_t\mathcal L_{\mathrm{trajectory}}
+
\lambda_g\mathcal R_{\mathrm{glottal}}.
$$

其中：

$$
\mathcal L_{\mathrm{trajectory}}
=
\sum_{t,k}
 w_{t,k}
 d_{S^1}
 \left(
 \widehat\psi_{t,k},
 \psi_{t,k}
 \right)^2
+
\mu
\sum_{t,k}
 w_{t,k}
 \left|
 \dot{\widehat\Psi}_{t,k}
 \right|.
$$

$\mathcal R_{\mathrm{glottal}}$ 則只能在聲門域模型中使用，不能強加於一般輸出域相位。

---

# 10. FARHP-Trajectory-Spec-v0.2

## 10.1 頂層物件

本篇定義：

```yaml
farhp_trajectory_version: "0.2"
sample_rate_hz: 16000
frame_length_sec: 0.080
hop_length_sec: 0.010
frame_times_sec: [...]
f0_hz: [...]
voiced: [...]
track_confidence: [...]
frames: [...]
anchor_unwrapped_rad: [...]
anchor_residual_rad: [...]
farhp_unwrapped_rad: [...]
phase_velocity_rad_per_sec: [...]
method: farhp_viterbi_trajectory
method_version: "0.2"
metadata: {...}
```

## 10.2 長度不變式

所有時間索引陣列必須具有共同長度 $T$：

$$
\begin{aligned}
T
&=
|\mathbf t|
=
|\mathbf f_0|
=
|\mathbf v|
=
|\mathbf c|\\
&=
|\boldsymbol\Phi_1|
=
|\mathbf R_1|
=
|\boldsymbol\Psi|
=
|\dot{\boldsymbol\Psi}|.
\end{aligned}
$$

## 10.3 相容層級

定义四級軌跡相容性：

$$
\begin{aligned}
T_0&:\ f_0、\text{有聲狀態、置信度、時間標記},\\
T_1&:\ T_0+\text{逐框架 FARHP-Spec 物件},\\
T_2&:\ T_1+\text{錨相位與 FARHP 解除包覆軌跡},\\
T_3&:\ T_2+\text{相位速度、不確定性、間隙與來源政策}.
\end{aligned}
$$

`FARHP-Core v0.2` 實作到 $T_2$，並提供部分 $T_3$ 欄位。

## 10.4 `null` 的語義

`null` 表示：

- 無聲；
- 遮罩關閉；
- 無可靠估計；
- 軌跡重啟後尚未建立速度。

`null` 不是數字 $0$，也不是 NaN 的跨語言等價物；它是交換格式中的明確缺失狀態。

---

# 11. FARHP-Core v0.2 參考實作

## 11.1 新增模組

```text
src/farhp/
  tracking.py       多候選 F0、Viterbi、錨相位與 FARHP 軌跡
  model.py          FARHPTrajectory 資料物件
  reconstructor.py  可含空框架的軌跡 overlap-add
  inspector.py      F0、置信度、錨相位與 FARHP 軌跡圖
  io.py             軌跡 JSON 讀寫
  cli.py            track、demo-track、reconstruct-track
```

## 11.2 分析流程

$$
\text{WAV}
\rightarrow
\text{切框}
\rightarrow
\text{YIN 候選}
\rightarrow
\text{Viterbi 路徑}
\rightarrow
\text{逐框架諧波投影}
\rightarrow
\text{錨相位傳播}
\rightarrow
\text{FARHP 解除包覆}
\rightarrow
\text{Trajectory JSON}.
$$

## 11.3 命令列

```bash
farhp demo-track --out artifacts/trajectory_demo
```

分析任意單聲道或立體聲 WAV：

```bash
farhp track input.wav \
  --out output/farhp_trajectory.json \
  --plot output/farhp_trajectory.png \
  --f0-min 70 \
  --f0-max 350 \
  --frame-length 0.080 \
  --hop-length 0.010 \
  --k-max 24
```

諧波軌跡重建：

```bash
farhp reconstruct-track output/farhp_trajectory.json \
  --out output/harmonic_reconstruction.wav
```

## 11.4 v0.2 的工程邊界

本版尚未實作：

- 完整 pYIN 機率閾值分布；
- 前向—後向候選後驗；
- 真正的瞬時頻率諧波追蹤；
- 跨無聲間隙橋接；
- 非諧波殘差重建；
- 聲門逆濾波；
- 神經軌跡模型；
- 自然語音資料集批次評估；
- 感知盲聽實驗。

所以它是參考實作，不是成熟聲碼器。

---

# 12. 受控動態回歸實驗

## 12.1 訊號設定

建立一段 $1.2$ 秒合成母音，包含：

- 基頻由 $110$ Hz 平滑上升至 $165$ Hz；
- 約 $4.7$ Hz 的小幅顫音；
- 隨時間緩慢變化的 FARHP 微擾；
- 隨基頻移動的共振峰式諧波振幅包絡；
- 微量白噪聲；
- 起訖淡入淡出。

這比第五篇的靜態框架更接近追蹤問題，但仍是完全已知的合成回歸夾具。

## 12.2 參數

$$
F_s=16000\ \mathrm{Hz},
$$

$$
L=80\ \mathrm{ms},
\qquad
H=10\ \mathrm{ms},
$$

$$
K_{\max}=24.
$$

## 12.3 結果

參考執行得到：

| 指標 | 結果 |
|---|---:|
| 框架數 | $113$ |
| 有聲比例 | $1.000$ |
| 平均追蹤置信度 | $0.906944$ |
| $f_0$ 最小估計值 | $110.815840$ Hz |
| $f_0$ 最大估計值 | $165.831365$ Hz |
| $f_0$ 平均絕對誤差 | $0.279059$ Hz |
| $f_0$ 均方根誤差 | $0.330740$ Hz |
| 錨相位預測殘差中位數 | $0.108389$ rad |
| 自動測試 | $13/13$ 通過 |

## 12.4 能證明什麼

這組結果能證明：

1. 多候選路徑在受控滑音上沒有發生倍頻跳躍；
2. $f_0$ 積分與包覆錨相位的最近分支規則數值一致；
3. FARHP 的時間解除包覆沒有因 $\pm\pi$ 邊界產生大規模人工尖峰；
4. 軌跡 JSON 可以往返序列化；
5. 軌跡可以驅動諧波 overlap-add 重建；
6. 規格物件可通過 JSON Schema 驗證。

## 12.5 不能證明什麼

它不能證明：

- 真實語者的 $f_0$ 精度相同；
- 有聲／無聲判定已成熟；
- 塞音、擦音與連續句可被良好處理；
- `FARHP-Y` 能唯一還原聲門波；
- 諧波重建具有自然語音品質；
- FARHP 動態差異必然可被人類穩定感知；
- 新符號語言的相位發音已成立。

---

# 13. 自然語音驗證計畫

## 13.1 第一階段：持續母音

語料至少包括：

$$
\{/a/,/i/,/u/,/e/,/o/\}
$$

及華語對應母音，採：

- 多語者；
- 多音高；
- 多聲級；
- 正常聲、氣聲、緊聲；
- 可選 EGG 同步。

評估：

- $f_0$ 誤差；
- 錨殘差分布；
- FARHP 軌跡平滑度；
- 跨重錄穩定性；
- 極性敏感度；
- `Y`／`G` 域差異。

## 13.2 第二階段：華語單音節與五聲

每個合法音節選擇代表集，涵蓋：

- 零聲母；
- 塞音、塞擦音、擦音、鼻音、邊音；
- 齊齒呼、合口呼、撮口呼；
- 一、二、三、四聲與輕聲。

要檢驗：

$$
\text{聲調引起的 }f_0(t)\text{ 變化}
$$

與：

$$
\text{FARHP 相對聲源／聲道結構變化}
$$

能否在模型中分離。

## 13.3 第三階段：連續語音

加入：

- 連音；
- 變調；
- 音節弱化；
- 送氣；
- 清濁過渡；
- 句末下降；
- 情緒與語速差異。

此階段必須加入非諧波殘差與更成熟的有聲門控，否則重建品質評估沒有意義。

## 13.4 評估指標

建議至少包括：

1. $f_0$ 平均絕對誤差；
2. gross pitch error；
3. voiced decision error；
4. 錨相位創新殘差；
5. 加權環面一步距離；
6. 軌跡斷裂率；
7. 諧波重建誤差；
8. 頻譜包絡保持度；
9. 盲聽 ABX 或 MUSHRA 類品質實驗；
10. 語者、母音、音類與聲調條件下的統計效應。

---

# 14. 可證偽命題

## 命題一：序列 $f_0$ 路徑優於逐框架選擇

在含滑音、共振峰偏置及弱噪聲的有聲語音中：

$$
\operatorname{GPE}_{\mathrm{sequence}}
<
\operatorname{GPE}_{\mathrm{framewise}}.
$$

若在多語者自然語音中不成立，必須修改候選分布與轉移模型。

## 命題二：錨相位創新殘差可診斷倍頻錯誤

當 $f_0$ 路徑發生整倍頻跳變時：

$$
|r_{t,1}|
$$

及加權 FARHP 環面距離將顯著增加。若無法區分真實快速發音變化與追蹤錯誤，此診斷量的價值受限。

## 命題三：FARHP 軌跡比絕對諧波相位更具時間穩定性

在相同分析條件下：

$$
\operatorname{Var}_t
\left(
\Delta\psi_{t,k}
\right)
<
\operatorname{Var}_t
\left(
\Delta\phi_{t,k}
\right)
$$

應在穩定有聲區段成立。若不成立，FARHP 的時間表示優勢需要重新檢討。

## 命題四：可靠度門控可降低高次諧波假跳變

加入錨點、振幅與軌跡置信度後：

$$
\operatorname{FalseJumpRate}_{\mathrm{gated}}
<
\operatorname{FalseJumpRate}_{\mathrm{ungated}}.
$$

## 命題五：`FARHP-Y` 與 `FARHP-G` 的動態結構不同

經可靠逆濾波後，至少部分母音與聲質條件下：

$$
D
\left(
\Psi^{(Y)},
\Psi^{(G)}
\right)
>0
$$

且差異不能只以共同時間延遲解釋。

## 命題六：跨無聲間隙的強制連續會增加錯誤

在沒有外部聲門時鐘時，保守重啟相較於強制橋接應具有較低的分支錯配率：

$$
P_{\mathrm{branch\ error}}^{\mathrm{reset}}
<
P_{\mathrm{branch\ error}}^{\mathrm{forced\ bridge}}.
$$

## 命題七：相位速度可提供超出靜態碼本的資訊

對聲質分類、音節邊界或合成品質預測：

$$
I
\left(
Y;
\boldsymbol\Psi,\dot{\boldsymbol\Psi}
\right)
>
I
\left(
Y;
\boldsymbol\Psi
\right).
$$

若動態特徵沒有額外效益，第七篇不應增加不必要的序列複雜度。

---

# 15. 理論限制

## 15.1 局部連續不等於全域真相

解除包覆後的 $\widehat\Phi$ 與 $\widehat\Psi$ 是演算法選擇的局部代表。它們依賴：

- 初始框架；
- $f_0$ 路徑；
- 分支政策；
- 間隙政策；
- 諧波身份；
- 框架及時間原點。

因此不應把它們宣稱為與分析系統無關的絕對相位實體。

## 15.2 FARHP 不能解決所有相位問題

FARHP 消去的是理想共同時間平移的線性諧波相位項。它不自動消除：

- 頻率失配；
- 非最小相位聲道；
- 全通成分；
- 房間反射；
- 麥克風相位響應；
- 非整數諧波；
- 多聲源混合；
- 無聲噪聲。

## 15.3 自然語音不是純諧波訊號

擦音、爆破、送氣、聲門噪聲與混合激勵都需要殘差模型：

$$
x(t)
=
x_{\mathrm{harmonic}}(t)
+
x_{\mathrm{residual}}(t).
$$

若沒有殘差，任何「自然語音重建」主張都不完整。

## 15.4 生理反演不唯一

即使輸出波形完全已知，也不能在沒有額外假設時唯一分解聲門源與聲道。`FARHP-G` 必須被視為方法條件化估計，不是直接觀測。

---

# 16. 第七篇接口

第七篇將進入：

**《基於相對諧波相位控制的聲音重建、音色變換與新音生成》**。

第六篇提供的必要接口包括：

1. $f_0(t)$ 與有聲狀態；
2. 逐框架振幅、遮罩與置信度；
3. 包覆 FARHP；
4. 解除包覆 FARHP 局部代表；
5. FARHP 相位速度；
6. 錨相位及預測殘差；
7. 間隙及重啟標記；
8. `Y`／`G` 來源域；
9. 動態 JSON 規格；
10. 可執行軌跡分析及重建器。

第七篇不可直接在線性空間對包覆角度做普通插值，而應使用：

$$
\psi_{\lambda}
=
\operatorname{Arg}
\left(
(1-\lambda)e^{i\psi_a}
+
\lambda e^{i\psi_b}
\right)
$$

或在已驗證的解除包覆局部區段進行受約束插值。動態轉換還必須保持：

$$
\frac{d\Phi_1}{dt}=2\pi f_0(t)
$$

及跨框架振幅—相位的一致性。

---

# 17. 結論

第五篇證明 FARHP 可以在單一受控框架中完成分析、編碼與重建。第六篇則指出，真正的自然語音問題不是多做幾次單框架分析，而是建立兩條有明確依賴關係的軌跡：

$$
\boxed{
\text{$f_0$／有聲狀態路徑}
}
$$

與：

$$
\boxed{
\text{錨相位／FARHP 環面路徑}
}.
$$

前者決定週期時鐘及候選身份，後者描述相對諧波結構如何演化。若前者錯誤，錨點誤差會以諧波階數放大；若後者被當成普通線性資料，$\pm\pi$ 邊界會製造人工跳變；若無聲與缺失被寫成零，資料語義便會被破壞。

因此，本篇的核心結論是：

$$
\boxed{
\text{自然語音中的 FARHP 必須被建模為
具遮罩、置信度、分支及重啟政策的相位環面軌跡。}
}
$$

`FARHP-Core v0.2` 已建立這個最小可執行物件，但自然語音語料、聲門反演、殘差建模與知覺實驗仍是尚未完成的實證工作。這個限制不是缺陷掩飾，而是第七篇與後續華語相位發音系統必須遵守的研究邊界。

---

# 參考文獻

1. de Cheveigné, A., & Kawahara, H. (2002). YIN, a fundamental frequency estimator for speech and music. *The Journal of the Acoustical Society of America, 111*(4), 1917–1930. DOI: `10.1121/1.1458024`.
2. Mauch, M., & Dixon, S. (2014). pYIN: A fundamental frequency estimator using probabilistic threshold distributions. *ICASSP 2014*, 659–663.
3. McAulay, R. J., & Quatieri, T. F. (1986). Speech analysis/synthesis based on a sinusoidal representation. *IEEE Transactions on Acoustics, Speech, and Signal Processing, 34*(4), 744–754.
4. Saratxaga, I., Hernáez, I., Odriozola, I., Navas, E., Luengo, I., & Erro, D. (2010). Using harmonic phase information to improve ASR rate. *INTERSPEECH 2010*.
5. Saratxaga, I., Erro, D., Hernáez, I., Sainz, I., & Navas, E. (2009). Use of harmonic phase information for polarity detection in speech signals. *INTERSPEECH 2009*.
6. Degottex, G., & Erro, D. (2014). A uniform phase representation for the harmonic model in speech synthesis applications. *EURASIP Journal on Audio, Speech, and Music Processing*, Article 38. DOI: `10.1186/s13636-014-0038-1`.
7. Krawczyk, M., & Gerkmann, T. (2015). Harmonic phase estimation in single-channel speech enhancement using phase decomposition and SNR information. *IEEE/ACM Transactions on Audio, Speech, and Language Processing*. DOI: `10.1109/TASLP.2015.2439038`.
8. Magron, P., Badeau, R., & David, B. (2017). Phase reconstruction of spectrograms with linear unwrapping: Application to audio signal restoration. *EUSIPCO / related phase-reconstruction work*.
9. Masuyama, Y., Yatabe, K., Koizumi, Y., Oikawa, Y., & Harada, N. (2020). Phase reconstruction based on recurrent phase unwrapping with deep neural networks. arXiv: `2002.05832`.
10. EveMissLab FARHP Series (2026). Papers 1–5 and `FARHP-Spec-v0.1`.

---

## 附錄 A：核心演算法摘要

```text
輸入：波形 x[n]、取樣率 Fs
輸出：FARHPTrajectory

1. 依 frame_length 與 hop_length 切框。
2. 每框計算 YIN 類 CMND。
3. 保留多個局部最低點作為 F0 候選，加入無聲狀態。
4. 以發射代價與對數頻率轉移代價進行 Viterbi 解碼。
5. 對有聲框架，以選定 F0 投影各次諧波複係數。
6. 計算包覆 FARHP、振幅遮罩與每諧波置信度。
7. 由相鄰 F0 積分預測下一框錨相位。
8. 以最近 2π 分支校正包覆錨相位。
9. 對有效 FARHP 座標選取最接近上一代表的分支。
10. 在無聲或失效區段重啟軌跡。
11. 輸出包覆值、解除包覆代表、相位速度、遮罩與置信度。
```

## 附錄 B：最低工程成功條件

第六篇工程階段的最低成功條件為：

- 動態合成訊號 $f_0$ MAE 小於 $1.5$ Hz；
- 有聲比例判定大於 $95\%$；
- 錨相位預測殘差中位數小於 $0.35$ rad；
- 前七次非錨諧波的 FARHP 一步跳變 $95$ 百分位小於 $1.5$ rad；
- 軌跡 JSON 可往返；
- 軌跡 JSON 通過 Schema；
- 諧波重建輸出為有限數值；
- 舊版單框架測試不得退化。

目前 `FARHP-Core v0.2` 已通過上述受控測試。
