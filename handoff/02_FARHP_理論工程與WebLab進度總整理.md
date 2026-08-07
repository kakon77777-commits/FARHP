# FARHP 理論、工程與 WebLab 進度總整理

**用途：** FARHP 技術主文件／本地 AI 技術聖經  
**版本：** Handoff v1.0  
**日期：** 2026-08-07

---

# 1. FARHP 的正式定位

FARHP = **Fundamental-Anchored Relative Harmonic Phase**。

核心定義：

$$
\psi_k(t)
=
\operatorname{wrap}
\left(
\phi_k(t)-k\phi_1(t)
\right),
\qquad k\ge2.
$$

這個式子本身與既有 Relative Phase Shift 類研究有直接關聯；本專案的新增價值不應宣稱為「首次發明相對相位」，而是其統一工程：

- 商環面形式化；
- 動態時間軌跡；
- 遮罩／可靠度；
- 離散碼本；
- FARHP-Y／FARHP-G；
- 受控相位變換；
- 華語發音層；
- 研究實驗與治理平台；
- EMPSL 語言整合。

---

# 2. 數學核心

完整 $K$ 諧波相位可視為：

$$
\boldsymbol\phi
\in
\mathbb T^K.
$$

共同時間平移作用為：

$$
\phi_k
\mapsto
\phi_k+k\theta.
$$

把共同週期時鐘自由度取商後：

$$
\boxed{
\mathbb T^K/\iota_K(\mathbb T)
\cong
\mathbb T^{K-1}
}.
$$

因此 FARHP 的自然狀態不是一般歐氏向量，而是：

$$
\boldsymbol\Psi
\in
(S^1)^{K-1}.
$$

圓周距離：

$$
d_{S^1}(a,b)
=
\left|
\operatorname{wrap}(a-b)
\right|.
$$

測地插值：

$$
\operatorname{GI}_{S^1}(a,b;\lambda)
=
\operatorname{wrap}
\left(
a+\lambda\operatorname{wrap}(b-a)
\right).
$$

---

# 3. FARHP-Y 與 FARHP-G

麥克風輸出相位不是純聲門相位。

可分解為：

$$
\psi_k^{(y)}
=
\psi_k^{(g)}
+
\Delta_k\theta_v
+
\Delta_k\theta_r
+
\Delta_k\theta_m
\pmod{2\pi}.
$$

因此：

- `FARHP-Y`：由輸出聲波直接估計；
- `FARHP-G`：經聲門逆濾波等程序估計聲門相位。

重要原則：

$$
\boxed{
\text{可觀測}
\neq
\text{可唯一歸因}
}.
$$

本地 AI 不應把 FARHP-Y 直接解讀為生理聲門真值。

---

# 4. FARHP 不能取代什麼

FARHP 是 phase subsystem，不是完整 speech model。

完整發音至少仍需：

$$
\text{Speech}
=
 f_0
+
A_k
+
\Psi
+
\text{spectral envelope}
+
\text{aperiodicity}
+
\text{duration}
+
\text{transients}.
$$

尤其：

- 華語聲調主要不是 FARHP；
- 共振峰不等於 FARHP；
- 擦音噪聲不應硬塞進諧波相位；
- 塞音爆破需要瞬態／殘差層；
- 自然音色不是單一相位座標可完全控制。

---

# 5. 論文系列狀態

## Paper 01 — 總論

完成：

- 靜態／動態 FARHP；
- 研究疆界；
- 九篇系列架構；
- 可證偽命題；
- 語言整合方向。

檔案：

`FARHP_基頻錨定相對諧波相位差_總論_v0.1.md`

## Paper 02 — 數學結構

完成：

- 商環面；
- kernel／surjection；
- 時間平移不變性；
- 失諧殘餘；
- 基頻誤差傳播；
- 繞行數；
- Bézout 合成錨與基頻缺失情況。

## Paper 03 — 聲源與知覺邊界

完成：

- FARHP-Y／G；
- 聲源／聲道／量測相位分解；
- 五級適用門控；
- 母音、鼻音、擦音、塞音適用邊界；
- 可觀測與可歸因分離。

## Paper 04 — 離散編碼與 AI 表示

完成：

- $(\cos\psi,\sin\psi)$ 表示；
- 多解析度標量量化；
- 環面聯合碼本；
- 遮罩、置信度、來源域；
- 動態 token；
- `FARHP-Spec-v0.1`。

## Paper 05 — 分析與重建架構

完成：

- 單框架 $f_0$；
- 諧波複數投影；
- FARHP 抽取；
- 量化／碼本；
- 波形重建；
- CLI；
- `FARHP-Core v0.1`。

## Paper 06 — 時間追蹤與反演

完成：

- 多候選 YIN 類 $f_0$；
- Viterbi；
- 錨相位傳播；
- FARHP temporal unwrap；
- phase velocity；
- 無聲 gap reset；
- `FARHP-Trajectory-Spec-v0.2`；
- `FARHP-Core v0.2`。

## Paper 07 — 受控相位變換

完成：

- zero／alternating／random phase；
- smooth random；
- geodesic interpolation；
- style transfer；
- FARHP-only invariance certificate；
- blind listening pack；
- `FARHP-Transform-Spec-v0.3`；
- `FARHP-Core v0.3`。

## Paper 08 — 華語複合發音

**正式論文未完成。**

但工程已在 WebLab v0.2–v0.4 中大量落地：

- 22 聲母選項；
- 37 韻母／舌尖元音；
- 四呼；
- 五聲；
- 鼻韻尾；
- 塞音／送氣／擦音殘差；
- 多音節；
- 三聲變調；
- 輕聲語境；
- 一／不變調；
- 韻律分組；
- 疑問／陳述／感嘆句調；
- 跨音節聲道參數插值。

未來要做的是把這些工程正式回寫成 Paper 08，而不是重新做一次。

## Paper 09 — EMPSL 統一編碼

已完成於 EMPSL v0.1。

---

# 6. FARHP-Core 進度

## v0.1

- 單框架分析；
- 合成母音；
- 基頻估計；
- FARHP 抽取；
- 16-phase quantization；
- codebook；
- WAV／JSON；
- 初始測試。

## v0.2

- trajectory；
- Viterbi $f_0$；
- anchor phase propagation；
- gap reset；
- trajectory JSON；
- multi-frame reconstruction。

## v0.3

- controlled transform；
- phase style transfer；
- blind listening pack；
- overlap-add edge fix；
- 21 tests。

參考工程包：

- `FARHP_Core_v0.1_完整工程包.zip`
- `FARHP_Core_v0.2_完整工程包.zip`
- `FARHP_Core_v0.3_完整工程包.zip`

---

# 7. FARHP WebLab 演化

## v0.1 — 相位實驗台

目的：證明 FARHP 能在瀏覽器中作為可操作控制座標。

支援：

- $f_0$；
- $A_k$；
- $\psi_k$；
- 波形；
- 諧波圖；
- WAV；
- JSON；
- WAV import／估計。

## v0.2 — 華語單音節

新增：

$$
\Sigma=(O,F,T,D,\Psi,R).
$$

其中：

- $O$：聲母；
- $F$：韻母；
- $T$：聲調；
- $D$：時長；
- $\Psi$：FARHP；
- $R$：殘差。

## v0.3 — 多音節語流

新增：

- 三聲變調；
- 輕聲；
- 語速；
- 短語下傾；
- 句末延長；
- 邊界交疊。

## v0.4 — 韻律層

新增：

- 一／不變調；
- prosodic group；
- group boundary pause；
- sentence intonation；
- 跨音節 resonance interpolation。

## v0.5 — ABX

新增：

- FARHP-only controlled condition；
- A／B／X blind mapping；
- balanced 4-cell design；
- deterministic seed；
- invariance certificate；
- JSON／CSV result。

## v0.6 — 多刺激正式知覺研究

新增：

- stimulus pool；
- participant ID；
- practice；
- rest node；
- counterbalanced order；
- pooled accuracy；
- Wilson CI；
- binomial test。

## v0.7 — 部署工作流

新增：

- research plan；
- fingerprint；
- lock；
- checkpoint；
- exclusion policy；
- participant/stimulus hierarchical summaries。

## v0.8 — 研究治理

新增：

- electronic consent；
- consent version；
- event hash chain；
- de-identification；
- governance QA；
- GLMM／GEE export templates。

## v0.9 — 伺服器協作

新增：

- FastAPI；
- SQLite；
- users／roles；
- invite；
- server session；
- server audit events；
- deidentified analyst view。

## v1.0.0-rc.1 — 生產化候選

新增：

- SQLite／PostgreSQL shared SQLAlchemy models；
- Alembic；
- v0.9 adoption；
- OIDC Authorization Code Flow；
- JWKS signature／issuer／audience／nonce；
- CSP／HSTS option／Trusted Host；
- liveness／readiness；
- SQLite backup；
- PostgreSQL pg_dump／pg_restore path；
- Docker Compose；
- Caddy overlay；
- invitation concurrency protection。

---

# 8. 已知測試證據

## FARHP-Core v0.1

- 7 tests PASS；
- 合成 $125$ Hz 母音估計約 $125.0037$ Hz；
- 理想整數諧波分析—重建 RMS 可到 $10^{-10}$ 以下。

這是受控合成閉環，不是自然語音結論。

## FARHP-Core v0.2

- 13 tests PASS；
- 動態合成母音 $f_0$ MAE 約 $0.279$ Hz；
- anchor prediction residual median 約 $0.108$ rad；
- gap restart 已驗證。

## FARHP-Core v0.3

- 21 tests PASS；
- 完整 style transfer 時 $f_0$、振幅、anchor phase 保持不變；
- FARHP geodesic displacement 可控；
- overlap-add edge spike 已修正。

## WebLab v1.0 RC

- 22 tests PASS；
- Uvicorn 實啟；
- SQLite backup/restore；
- OIDC mock end-to-end；
- Alembic migration；
- concurrency invite test；
- Chromium console error 0。

---

# 9. 哪些資料是假資料／模擬資料

本地 AI 必須知道：

- WebLab v0.5–v0.8 中的示範 ABX／群體資料主要是自動化模擬資料；
- 自動測試 100% accuracy 不代表人類辨識能力；
- 合成語音不是自然語音 corpus；
- OIDC 測試是本地模擬 RSA／JWKS／discovery；
- PostgreSQL 尚未完成真實 Container E2E。

---

# 10. 未完成的真正科研驗證

FARHP 如果要從「有趣且可工作的聲學框架」走向更強科學主張，需要：

1. 真實錄音；
2. 多說話者；
3. 不同 $f_0$／性別／聲線；
4. FARHP-Y 統計；
5. 聲門逆濾波後 FARHP-G；
6. 自然語音 analysis-synthesis；
7. FARHP-only 人類 ABX；
8. codebook generalization；
9. 受試者×刺激交叉統計；
10. 與 phase-aware vocoder baseline 比較。

---

# 11. 本地 AI 推進 FARHP 時的禁止事項

不要：

- 把絕對相位當 FARHP；
- 直接在線性角度上平均而忽略 $S^1$；
- 跨無聲區段硬接 phase unwrap；
- 忽略 mask／confidence；
- 把 waveform distance 等同 perceptual distance；
- 把 FARHP-only 變換同時修改 $f_0$ 或 $A_k$ 卻仍稱 controlled phase experiment；
- 把 PUA／字形層當聲學 profile；
- 把測試 PASS 當「理論已證明」；
- 把 simulated participant data 當真實人類資料。

---

# 12. FARHP 最佳下一步

短期不是新增 WebLab feature，而是：

## A. Paper 08 正式回寫

把 v0.2–v0.4 已完成的華語工程整理成正式論文。

## B. 真實母音 pilot

建立一個最小真實 corpus：

- 3–5 位說話者；
- /a i u y ə/；
- 多個 $f_0$；
- 固定麥克風條件；
- FARHP-Y extraction；
- 重複性／跨日穩定性。

## C. FARHP-G

加入 inverse filtering baseline，正式比較：

$$
\Psi_Y
\quad\text{vs}\quad
\Psi_G.
$$

## D. 真人 ABX

先做小型 pilot，而不是立刻大規模部署。

---

# 13. FARHP 檔案入口

核心文件位於 `/mnt/data` 歷史 artifact 中，建議本地端重新整理成：

```text
farhp/
├── papers/
├── specs/
├── core/
├── weblab/
├── experiments/
└── reports/
```

最關鍵檔名：

- `FARHP_基頻錨定相對諧波相位差_總論_v0.1.md`
- `FARHP_02_數學結構_不變性與等價類_v0.1.md`
- `FARHP_03_聲源模型與語音知覺邊界_v0.1.md`
- `FARHP_04_離散編碼_相位碼本與AI表示_v0.1.md`
- `FARHP_05_分析編碼生成與重建架構_v0.1.md`
- `FARHP_06_自然語音中的估計追蹤與反演_v0.1.md`
- `FARHP_07_相位控制重建_音色變換與新音生成_v0.1.md`
- `FARHP_Spec_v0.1.yaml`
- `FARHP_Trajectory_Spec_v0.2.yaml`
- `FARHP_Transform_Spec_v0.3.yaml`
- `FARHP_WebLab_v1.0.0-rc.1_完整網站與伺服器包.zip`

---

# 14. 一句話交接

> FARHP 的核心理論、數學、單框架／動態工程、相位控制與 WebLab 研究平台都已完成到 RC；現在真正缺的是 Paper 08 的正式回寫與自然語音／真人實驗，而不是繼續增加展示功能。

