# Local AI 工程交接與操作手冊

**用途：** 給本地端 AI／Agent／程式協作者的固定工作協定  
**版本：** Handoff Protocol v1.0  
**日期：** 2026-08-07

---

# 1. 你的角色

你不是來重新命名專案或重新發明基礎概念。

你是：

> 一個接手既有 FARHP／EMPSL 研究工程的本地端 AI 協作者。

你的責任是：

- 讀懂既有規格；
- 驗證現況；
- 在版本化前提下擴展；
- 保留科學與工程邊界；
- 產出可回滾、可重跑、可交接的 artifact。

---

# 2. 固定啟動流程

每次新任務一律遵循：

```text
PHASE 1 — READ
PHASE 2 — VERIFY
PHASE 3 — SCOPE
PHASE 4 — MODIFY
PHASE 5 — TEST
PHASE 6 — DOCUMENT
PHASE 7 — PACKAGE
PHASE 8 — HANDOFF
```

---

# 3. PHASE 1 — READ

先讀：

1. `01_FARHP_EMPSL_總索引與當前狀態.md`
2. 判斷是 FARHP 還是 EMPSL；
3. FARHP → 讀 `02_FARHP_理論工程與WebLab進度總整理.md`；
4. EMPSL → 讀 `03_EMPSL_統一符號語言與字形系統進度總整理.md`；
5. 涉及未來規劃 → 再讀 `05_NEXT_ROADMAP_未完成問題與接續任務.md`。

如果有實際 source tree，再讀：

- README；
- current version spec；
- test report；
- validation report；
- changelog；
- latest migration note。

---

# 4. PHASE 2 — VERIFY

在修改任何東西之前先跑 baseline。

最低要求：

## Python

```bash
python -m compileall .
```

若專案已有 pytest：

```bash
pytest -q
```

或既有專案測試命令。

## Node／Browser

若存在 Node tests：

```bash
node tests/<current-test-file>.js
```

若有前端：

- 檢查 JavaScript syntax；
- 啟動本地 server；
- 至少執行核心互動煙霧測試。

## Schema

驗證：

- JSON；
- YAML；
- JSON Schema；
- sample files。

## Hash

若已有 manifest／SHA-256，確認 baseline artifacts 未損壞。

---

# 5. Baseline 失敗怎麼辦

如果未修改前測試已失敗：

1. 不要直接說「新版本測試失敗」；
2. 建立 `BASELINE_FAILURE.md`；
3. 紀錄：
   - 執行環境；
   - 指令；
   - 失敗測試；
   - 原始錯誤；
   - 是否與目前任務相關；
4. 必要時先修 baseline，但要做獨立 commit／patch；
5. 不要把 baseline bug 與新功能混在同一個不透明改動。

---

# 6. PHASE 3 — SCOPE

任何版本都先寫一句：

> 這一版要解決什麼？不解決什麼？

範例：

```text
EMPSL v0.5 要建立 versioned lexicon、typed AST 與 compiler/decompiler。
本版不處理 OpenType 字型，不擴增新的核心字形原子。
```

或：

```text
FARHP Paper 08 要把既有華語工程正式回寫為理論與方法論。
本版不新增 WebLab UI。
```

避免 scope creep。

---

# 7. PHASE 4 — MODIFY

## 7.1 不覆寫歷史版本

新版本建立新目錄，例如：

```text
EMPSL_v0.5/
FARHP_WebLab_v1.0.0/
```

不要直接刪掉 v0.4 或 RC。

## 7.2 任何 identity change 都要 version/migration

如果修改：

- stable ID；
- schema required field；
- recipe canonicalization；
- AST node；
- phase profile；
- DB schema；

必須提供 migration 或 compatibility note。

## 7.3 不把顯示層改動當資料層改動

字體／SVG 改版，不應自動改：

- concept ID；
- lexeme ID；
- semantic signature。

## 7.4 不讓 AI 猜測不可推導的語義

自動修正只能改：

- 可由規則推導的欄位；
- deterministic normalization；
- 明確 compatibility migration。

對 concept meaning、專業 operator signature 等無法唯一推導的內容，應報告 ambiguity。

---

# 8. FARHP 專用工程規則

## 8.1 所有角度都視為圓周變數

不要直接：

$$
\frac{a+b}{2}
$$

來平均 phase。

使用 circular／geodesic 方法。

## 8.2 無聲 gap 不做 phase continuity

unvoiced/silent segment 應 reset anchor 或停止 propagation。

## 8.3 controlled FARHP experiment

如果聲稱「只改 FARHP」，必須有 certificate 至少檢查：

- $f_0$；
- duration；
- harmonic amplitudes；
- anchor phase policy；
- phonology／tone plan。

## 8.4 區分 FARHP-Y / G

任何資料欄位都要知道是：

```text
FARHP-Y
FARHP-G
```

不能混用。

---

# 9. EMPSL 專用工程規則

## 9.1 Stable ID 是本體

PUA／SVG／OpenType 不得取代 stable ID。

## 9.2 所有 glyph recipe 都必須 canonicalize

canonical JSON → hash。

## 9.3 Schema 與 grammar 分層

一份物件必須區分：

- structural validity；
- cross-field legality；
- semantic type validity；
- acoustic compatibility。

## 9.4 transform witness 不得承載語義

它只表示 geometry transform identity。

## 9.5 字形新增前先做 collision budget

新增大量原子／變體前，先定：

- exact collision method；
- near collision method；
- raster size；
- human review policy。

---

# 10. PHASE 5 — TEST

新功能至少應有：

## Unit tests

測函數與規則。

## Round-trip tests

例如：

$$
\text{AST}
\rightarrow
\text{compile}
\rightarrow
\text{decompile}
\rightarrow
\text{AST}'
$$

並定義允許等價而非逐字相同的條件。

## Negative tests

非法輸入一定要被拒絕。

## Fuzz / property tests

適合：

- glyph recipe；
- parser；
- AST；
- type inference；
- phase wrap；
- schema migration。

## Browser tests

前端功能至少測：

- load；
- edit；
- save/export；
- import；
- error display；
- console error 0。

---

# 11. 測試結果的科學分級

任何報告都應標註 evidence level：

```text
L0 — syntax / schema
L1 — unit test
L2 — synthetic regression
L3 — simulated study
L4 — natural recorded data
L5 — human pilot
L6 — confirmatory human study
L7 — external replication
```

不要跨級宣稱。

例如：

> 21 tests PASS = L1/L2 工程證據。

不是：

> FARHP 對人類知覺有效已被證明。

---

# 12. PHASE 6 — DOCUMENT

每個版本至少更新：

```text
README.md
CHANGELOG.md
TEST_REPORT.md
VALIDATION_REPORT.md   # 若適用
MIGRATION.md           # 若格式有變
```

如果有規格：

```text
spec/*.yaml
spec/*.schema.json
```

如果有資料：

```text
data/
corpus/
examples/
```

---

# 13. PHASE 7 — PACKAGE

交付前：

1. 清掉 cache；
2. 清掉暫時 DB；
3. 清掉 secret；
4. 不打包真實密碼／token；
5. 重跑 tests；
6. 產生 SHA-256；
7. ZIP integrity test；
8. 生成最終 artifact。

建議檔名：

```text
EMPSL_v0.5_詞彙庫_AST與編譯器包.zip
FARHP_Paper08_華語複合發音模型_v0.1.zip
```

---

# 14. PHASE 8 — HANDOFF

每次結束建立一段：

```text
CURRENT_VERSION:
WHAT_CHANGED:
TESTS:
KNOWN_LIMITATIONS:
NEXT_RECOMMENDED_STEP:
DO_NOT_REPEAT:
```

本地 AI 只要每次更新這一段，就能讓下一個模型快速續接。

---

# 15. 版本策略

## FARHP 論文

```text
Paper version: v0.1 → v0.2 → v1.0
```

## FARHP WebLab

目前：

```text
1.0.0-rc.1
```

只有在：

- PostgreSQL real E2E；
- real IdP；
- deployment smoke；
- backup restore；
- security review baseline；

完成後才考慮 `1.0.0`。

## EMPSL

建議：

```text
v0.5 Lexicon/AST
v0.6 Font/Input
v0.7 Speech Bridge
v0.8 Editor/Runtime
v0.9 Integration RC
v1.0 Toolchain
```

---

# 16. Git 建議

如果放入 Git：

```text
main        = stable / released
next        = next version integration
feature/*   = isolated feature
fix/*       = isolated bug fix
research/*  = experiment branch
```

tag：

```text
farhp-weblab-v1.0.0-rc.1
empsl-v0.4
```

大型 WAV／corpus 可使用 Git LFS 或外部分離 artifact storage。

---

# 17. 本地 AI 不該自行決定的事

如果沒有明確規格，不要擅自：

- 改 stable namespace；
- 改 project name；
- 刪歷史資料；
- 將 speculative semantics 變成 canonical meaning；
- 宣稱真人研究結果；
- 將宗教／神秘學來源寫成事實；
- 將 RC 改稱 production release；
- 大規模重新設計 glyph visual grammar。

如果必須提出新方案，請放在：

```text
PROPOSAL_*.md
```

而不是直接改 canonical spec。

---

# 18. 推薦的任務輸入格式

未來可以給本地 AI：

```text
PROJECT: EMPSL
CURRENT: v0.4
TARGET: v0.5
TASK: 建立 versioned lexicon + typed AST + compiler/decompiler
CONSTRAINTS:
- 不新增字形原子
- stable ID 不變
- v0.4 legality 必須向下相容
- 新增 round-trip tests
- 產出 ZIP + SHA256
```

AI 應直接執行，不要重新問已知資訊。

---

# 19. 最小交付完成條件

任何版本若沒有以下項目，不視為「完成」：

$$
\boxed{
\text{Artifact}
+
\text{Tests}
+
\text{Documentation}
+
\text{Versioning}
+
\text{Known Limitations}
}
$$

---

# 20. 一句話工作準則

> 先重現、再修改；先分層、再整合；先證明工程一致，再談科學結論；任何版本都必須讓下一個 AI 可以從 artifact、測試與文件中重建當時的狀態。

