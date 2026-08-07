# FARHP / EMPSL 總索引與當前狀態

**文件用途：** 本地端 AI 接手入口文件  
**建議閱讀順序：** 本文件 → `02_FARHP_理論工程與WebLab進度總整理.md` 或 `03_EMPSL_統一符號語言與字形系統進度總整理.md` → `04_Local_AI_工程交接與操作手冊.md` → `05_NEXT_ROADMAP_未完成問題與接續任務.md`  
**交接版：** v1.0  
**整理日期：** 2026-08-07  
**專案主體：** FARHP / EMPSL  

---

# 0. 接手 AI 先讀這一段

你現在接手的是一個**已經存在、具有論文、規格、網站、測試、語料、研究治理與伺服器原型的研究工程**，不是從零開始的概念討論。

請不要：

- 重新發明 FARHP 的基本定義；
- 把 EMPSL 當成單純替換字母；
- 把 FARHP 當成完整 TTS；
- 把合成回歸測試當成真人知覺證據；
- 把 WebLab v1.0 RC 當成已完成正式公開部署；
- 因為名稱含「以諾」而擴張成宗教權威、神秘學真實性或歷史復原主張；
- 用新版本覆寫舊版本而不保留驗證、差異與版本歷史。

正確的專案理解是：

$$
\boxed{
\text{FARHP}
\rightarrow
\text{相位聲學子系統}
\rightarrow
\text{華語發音整合}
\rightarrow
\text{EMPSL 統一符號語言}
\rightarrow
\text{字形／語義／語音工具鏈}
}
$$

---

# 1. 專案是什麼

## 1.1 FARHP

FARHP 全名：

**Fundamental-Anchored Relative Harmonic Phase**  
中文：**基頻錨定相對諧波相位差**。

核心座標為：

$$
\psi_k(t)
=
\operatorname{wrap}
\left(
\phi_k(t)-k\phi_1(t)
\right).
$$

其用途不是宣稱發現「聲音的唯一秘密」，而是建立一個：

- 對共同週期時間平移具有理想不變性的相對相位座標；
- 可提取、可編碼、可量化、可學習；
- 可控制波形週期內部結構；
- 可與音高、振幅、聲調、聲道、殘差分層；
- 可接入語音、符號語言與知覺實驗的聲學子系統。

其自然數學空間為：

$$
\mathbb T^K/\iota_K(\mathbb T)
\cong
\mathbb T^{K-1}.
$$

---

## 1.2 EMPSL

EMPSL 全名：

**Enochian–Mandarin Phase Symbol Language**。

它不是歷史以諾語復原，也不是把中文換一套神秘字母，而是一個現代人工符號語言工程，統一：

- 穩定身份；
- 字形配方；
- 華語／注音讀法；
- FARHP 聲學 profile；
- 型別化語義；
- AST 與未來編譯／反編譯接口。

統一符號物件目前採：

$$
\mathfrak s
=
(I,G,P,T,\Psi,\Sigma,M,V).
$$

其中：

- $I$：穩定身份；
- $G$：字形；
- $P$：音系／注音；
- $T$：聲調與韻律；
- $\Psi$：FARHP；
- $\Sigma$：型別／算子；
- $M$：語義；
- $V$：版本與命名空間。

---

# 2. FARHP 與 EMPSL 的關係

兩者不是平行專案，而是上下層：

$$
\text{EMPSL}
=
\text{Glyph}
+
\text{Phonology}
+
\text{FARHP}
+
\text{Typed Semantics}.
$$

FARHP 負責聲學相位子系統；EMPSL 負責把聲學、讀音、字形、語義與機器身份統合。

因此：

- FARHP 可以獨立存在，不必依賴 EMPSL；
- EMPSL 可以有不帶完整 FARHP profile 的純符號物件；
- 但完整「相位符號語言」版本會引用 FARHP profile 或相位簽名；
- 字形只顯示簡化相位簽名，精確 FARHP 向量仍保存在結構資料中。

---

# 3. 當前最高版本概覽

| 子系統 | 當前最高節點 | 狀態 |
|---|---|---|
| FARHP 理論論文 | 第 1–7 篇正式完成 | 完成 |
| FARHP 第 8 篇華語複合發音 | 工程內容已大量實作，正式論文未回寫 | 待補 |
| FARHP 第 9 篇／EMPSL 統一編碼 | 已完成 | 完成 |
| FARHP-Core | v0.3 | 完成參考實作 |
| FARHP WebLab | v1.0.0-rc.1 | Release Candidate |
| EMPSL 母規格 | v0.1 | 完成 |
| EMPSL 字形工程 | v0.2 | 完成 |
| EMPSL 受控變換／碰撞 | v0.3 | 完成 |
| EMPSL 字形語法／合法性 | v0.4 | 完成 |
| EMPSL 詞彙庫／AST 編譯 | v0.5 | 尚未開始 |

---

# 4. FARHP 論文進度

原始規劃共 9 篇：

$$
4\text{ 篇理論基礎}
\rightarrow
1\text{ 篇技術架構}
\rightarrow
2\text{ 篇核心工程}
\rightarrow
2\text{ 篇語言整合}.
$$

已完成：

1. FARHP 總論；
2. 數學結構、不變性與等價類；
3. 聲源模型與語音知覺邊界；
4. 離散編碼、相位碼本與 AI 表示；
5. 分析、編碼、生成與重建架構；
6. 自然語音中的估計、追蹤與反演；
7. 相位控制重建、音色變換與新音生成；
9. 以諾—華語相位符號語言：統一編碼。

尚缺正式回寫：

8. **《華語音節、聲調軌跡與基頻錨定相差的複合發音模型》**。

注意：第 8 篇不是「什麼都沒做」，而是**工程已先行**。FARHP WebLab v0.2–v0.4 已完成大量華語音節、五聲、三聲變調、一／不變調、輕聲、韻律分組、句調與共構音代理。

---

# 5. FARHP WebLab 版本線

WebLab 已從簡單相位實驗台一路推進到研究平台：

| 版本 | 主要內容 |
|---|---|
| v0.1 | 基頻、諧波、FARHP、WAV／JSON、相位實驗台 |
| v0.2 | 華語單音節、五聲、聲母殘差、鼻韻尾 |
| v0.3 | 多音節、三聲變調、輕聲、短語韻律 |
| v0.4 | 一／不變調、韻律分組、疑問句句調、跨音節聲道插值 |
| v0.5 | ABX 盲聽、固定種子、FARHP-only 不變量證書 |
| v0.6 | 多刺激、匿名受試者、練習、休息、群體統計 |
| v0.7 | 研究計畫鎖定、檢查點、排除政策、階層摘要 |
| v0.8 | 電子同意、事件鏈、去識別化、研究治理、分析模板 |
| v0.9 | FastAPI、SQLite、角色權限、多人工作階段、伺服器協作 |
| v1.0.0-rc.1 | PostgreSQL 路徑、Alembic、OIDC、安全標頭、備份還原、併發測試 |

當前 WebLab 是 **RC**，不是正式 production certification。

---

# 6. FARHP WebLab RC 已驗證與未驗證

## 已驗證

- 22 項自動回歸測試；
- Uvicorn 實際啟動；
- SQLite 實際備份／修改／還原；
- Alembic 新資料庫遷移；
- v0.9 legacy DB 採認升級；
- OIDC 本地 RSA／JWKS／issuer／audience／nonce 流程；
- 12 個併發請求競爭 5 個邀請名額時不超發；
- 安全標頭與 readiness；
- Chromium 工作台互動；
- Compose YAML 靜態驗證。

## 未驗證

- 真實 PostgreSQL Container E2E；
- 真實外部 OIDC IdP；
- 公網 TLS 與正式網域；
- 外部滲透測試；
- 真實多人長時間壓力測試；
- 真人受試者研究；
- IRB／倫理審查；
- 正式 production monitoring。

---

# 7. EMPSL 版本線

| 版本 | 狀態 | 核心成果 |
|---|---|---|
| v0.1 | 完成 | 統一身份、字形、注音、FARHP、型別語義母規格 |
| v0.2 | 完成 | 128 原子、32 種子、六槽字形組合器、SVG、配方雜湊 |
| v0.3 | 完成 | 8 種受控變換、256 種子變體、8,192 碰撞測試 |
| v0.4 | 完成 | 30 條合法性規則、4,096 符合性語料、Node／Python 雙引擎驗證 |
| v0.5 | 待開始 | 詞彙庫、Typed AST、型別推論、編譯／反編譯 |
| v0.6 | 待開始 | OpenType、字型、IME／輸入法 |
| v0.7 | 待開始 | EMPSL ↔ FARHP 發音引擎整合 |
| v1.0 | 待規劃 | 完整語言工具鏈 |

---

# 8. EMPSL 現有字形架構

## 8.1 128 原子

$$
32
+
16
+
16
+
16
+
48
=
128.
$$

包括：

- 32 核心構形種子；
- 16 語義外框；
- 16 PH16 相位簽名；
- 16 算子／語義附標；
- 48 音系／聲調／結構附標。

## 8.2 六槽字形

$$
G=
[F\mid S\mid P\mid T\mid\Phi\mid O].
$$

v0.3 後中央種子可帶受控變換：

$$
V=S@\tau,
\qquad
\tau\in
\{ID,R90,R180,MX,OPEN\mbox{-}R,CLOSED,INSET,CROSS\}.
$$

## 8.3 256 受控變體

$$
32\times8=256.
$$

純幾何變體用來研究碰撞；規範變體加入 3-bit transform witness 以保持身份可逆。

## 8.4 碰撞驗證

- 純幾何變體：40 組 exact collision；
- 規範見證變體：0 組 exact collision；
- 8,192 複合字形配方：0 組像素 exact collision；
- near collision 僅作人工審查候選。

---

# 9. EMPSL v0.4 合法性層

目前共有 30 條規則：

| 規則域 | 數量 |
|---|---:|
| 字形身份 | 4 |
| 華語音系 | 10 |
| 受控變換 | 3 |
| 型別化語義 | 6 |
| FARHP 聲學 | 7 |

驗證語料：

$$
4{,}096
=
1{,}024_{\text{legal}}
+
1{,}024_{\text{mutated}}
+
2{,}048_{\text{fuzz}}.
$$

本輪生成語料內：

- 1,024 合法案例全通過；
- 1,024 故意破壞案例全攔截；
- 2,048 fuzz 案例全攔截。

這不代表已覆蓋所有華語音系、語義與聲學錯誤，只代表目前規則生成空間內一致。

---

# 10. 專案重要技術原則

## 10.1 穩定身份優先於字形

不要用 PUA code point 當唯一身份。

正式身份應使用類似：

```text
eml.empsl:lexeme:000001
eml.concept:item:physical-light
```

字形、PUA、OpenType 都是顯示層。

## 10.2 字形不保存完整 FARHP

精確 FARHP 應保存在：

- profile ID；
- codebook ID；
- 連續／離散相位向量；
- mask；
- confidence。

字形僅顯示 PH16 類視覺簽名。

## 10.3 Schema 驗證不等於語法合法

$$
\mathrm{SchemaValid}
\not\Rightarrow
\mathrm{GrammarValid}.
$$

因此結構 Schema 與跨欄位規則引擎必須同時保留。

## 10.4 合成成功不等於科學證實

請嚴格區分：

1. 理論命題；
2. 數學證明；
3. 工程單元測試；
4. 合成回歸測試；
5. 自動模擬受試者資料；
6. 真人知覺實驗；
7. 自然語音／多說話者實證。

---

# 11. 建議的本地資料夾

```text
FARHP_EMPSL/
├── handoff/
│   ├── 01_FARHP_EMPSL_總索引與當前狀態.md
│   ├── 02_FARHP_理論工程與WebLab進度總整理.md
│   ├── 03_EMPSL_統一符號語言與字形系統進度總整理.md
│   ├── 04_Local_AI_工程交接與操作手冊.md
│   └── 05_NEXT_ROADMAP_未完成問題與接續任務.md
├── farhp/
│   ├── papers/
│   ├── specs/
│   ├── core/
│   └── weblab/
└── empsl/
    ├── specs/
    ├── glyphs/
    ├── corpus/
    ├── tools/
    └── roadmap/
```

---

# 12. 目前最推薦的下一步

如果要繼續主線，**不要再先擴 FARHP WebLab UI**。

下一個最有價值的節點是：

$$
\boxed{
\text{EMPSL v0.5}
=
\text{Versioned Lexicon}
+
\text{Typed AST}
+
\text{Type Inference}
+
\text{Compiler / Decompiler}
}
$$

其次是把 FARHP 第 8 篇正式論文補寫，將 v0.2–v0.4 WebLab 中已完成的華語發音工程回收到理論體系。

---

# 13. 接手 AI 的一句話摘要

> FARHP 已完成理論、參考實作、華語 WebLab 與研究平台 RC；EMPSL 已完成統一編碼、字形工程、受控變換與合法性層。下一步不是重新定義，而是建立 versioned lexicon、typed AST、compiler/decompiler，並補寫 FARHP 第 8 篇與真實聲學／人類知覺驗證。

