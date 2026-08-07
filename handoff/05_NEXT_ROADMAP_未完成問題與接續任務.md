# NEXT ROADMAP：未完成問題與接續任務

**用途：** 只記未來，不重抄歷史  
**版本：** Roadmap v1.0  
**日期：** 2026-08-07

---

# 1. 當前優先順序

建議主線排序：

$$
\boxed{
1.
\text{EMPSL v0.5}
\rightarrow
2.
\text{FARHP Paper 08}
\rightarrow
3.
\text{真實聲學 pilot}
\rightarrow
4.
\text{EMPSL Font/IME}
\rightarrow
5.
\text{Speech Bridge}
}
$$

FARHP WebLab 暫時不以功能膨脹為優先。

---

# 2. P0 — EMPSL v0.5：詞彙庫與 Typed AST

這是目前最推薦的下一步。

## 2.1 Versioned Lexicon

建立：

```text
lexicon/
├── registry.jsonl
├── concepts.jsonl
├── operators.jsonl
├── aliases.jsonl
└── migrations/
```

每個 lexeme 至少：

```json
{
  "lexeme_id": "eml.empsl:lexeme:000001",
  "concept_id": "eml.concept:item:physical-light",
  "glyph_recipe_ref": "...",
  "phonology": {},
  "farhp_profile_ref": "...",
  "semantic_signature": {},
  "status": "active",
  "version": "0.5.0"
}
```

## 2.2 Lifecycle

需要：

```text
draft
active
deprecated
superseded
reserved
```

stable ID 不回收。

## 2.3 Typed AST

初版 nodes：

```text
Literal
LexemeRef
OperatorCall
Sequence
Relation
Binder
Annotation
ProsodyGroup
```

## 2.4 Type system

最低 types：

```text
Entity
Event
Property
Relation
Number
Time
Location
TruthValue
Sound
Symbol
Any
```

之後可擴展 type variable／generic。

## 2.5 Type inference

需要：

- arity check；
- input type check；
- output inference；
- unresolved type；
- coercion policy；
- error certificate。

## 2.6 Compiler

AST → canonical token stream。

Compiler output 建議同時產生：

```text
canonical_tokens
glyph_plan
pronunciation_plan
farhp_refs
semantic_type
source_map
```

## 2.7 Decompiler

canonical token stream → AST candidate。

若有歧義：

```json
{
  "candidates": [...],
  "confidence": [...],
  "ambiguity": true
}
```

不要硬選唯一答案。

## 2.8 v0.5 測試目標

至少：

- 100–300 lexemes；
- 16+ operators；
- 1,000 valid AST；
- 1,000 invalid AST；
- compile/decompile round-trip；
- stable ID migration；
- v0.4 legality compatibility。

---

# 3. P0 — FARHP Paper 08 正式回寫

題名建議：

**《華語音節、聲調軌跡與基頻錨定相差的複合發音模型》**

不要重新開發，直接整理既有 WebLab v0.2–v0.4。

論文應包含：

1. 注音／音節表示；
2. 四呼；
3. 五聲 $f_0(t)$；
4. 聲調與 FARHP 分離；
5. 聲母殘差模型；
6. 鼻韻尾；
7. 三聲變調；
8. 一／不變調；
9. 輕聲語境；
10. 韻律 group；
11. sentence intonation；
12. coarticulation proxy；
13. JSON exchange schema；
14. 工程驗證與限制。

必須寫清楚：

- WebLab 是結構型合成 MVP；
- 不是真人 TTS；
- 聲道插值是 proxy；
- 變調規則仍是簡化規則；
- FARHP 與 tone 不混同。

---

# 4. P1 — FARHP 真實聲學 Pilot

目標：把 evidence level 從 synthetic regression 提升到 recorded natural data。

## 4.1 Corpus

初版可以很小：

- 3–5 speakers；
- 每人 5 vowels；
- 3 pitch bands；
- 每條 5 repeats；
- controlled microphone／distance。

## 4.2 指標

- FARHP-Y within-session variance；
- cross-session variance；
- speaker separability；
- vowel separability；
- $f_0$ dependence；
- SNR dependence；
- missing harmonic rate。

## 4.3 FARHP-G

加入至少一個 inverse filtering baseline。

比較：

$$
\Psi_Y
\quad\text{vs}\quad
\Psi_G.
$$

## 4.4 重要輸出

```text
FARHP_Natural_Vowel_Pilot_v0.1/
├── protocol.md
├── metadata.csv
├── extracted_farhp.parquet
├── plots/
├── stats/
└── report.md
```

---

# 5. P1 — 真人 ABX Pilot

不要一開始大規模招募。

先做 10–20 人 pilot：

- 2–4 stimuli；
- 2 phase conditions；
- 固定 headphones 建議；
- practice；
- quality screening；
- participant × stimulus analysis。

主要問題：

> 在固定 $f_0$、振幅包絡、音節與時長下，人類是否能穩定辨識 FARHP-only phase transformation？

不要把「是否喜歡」與「是否辨識」混成同一主終點。

---

# 6. P1 — FARHP WebLab v1.0.0 正式版條件

目前：`1.0.0-rc.1`。

升正式版前建議完成：

## Infrastructure

- PostgreSQL real container E2E；
- psycopg runtime；
- Alembic PostgreSQL migration；
- real restore test；
- multi-worker Uvicorn／Gunicorn test。

## OIDC

至少一個 real IdP：

- Keycloak；
- Auth0；
- Entra ID；
- Google Workspace。

## Security

- secrets manager；
- rate limiting；
- CSRF policy review；
- session revocation；
- log redaction；
- dependency scan；
- external penetration baseline。

## Ops

- monitoring；
- structured logs；
- alerting；
- backup rotation；
- retention policy；
- disaster recovery drill。

---

# 7. P2 — EMPSL v0.6：Font / OpenType / IME

在 v0.5 AST 穩定後再做。

## Font

- component glyphs；
- GSUB composition；
- GPOS mark placement；
- canonical witness；
- debug no-ligature mode；
- fallback font strategy。

## PUA

只作 rendering profile：

```text
EMPSL-PUA-Profile-v0.1
```

不可成為 stable identity。

## IME

輸入模式可同時支援：

- stable ID search；
- 注音讀音；
- semantic search；
- component composition；
- AST operator input。

---

# 8. P2 — EMPSL v0.7：Speech Bridge

目標：

$$
\text{EMPSL AST}
\rightarrow
\text{Pronunciation Plan}
\rightarrow
\text{FARHP Profile}
\rightarrow
\text{Speech}
$$

反向：

$$
\text{Speech}
\rightarrow
\text{Phonology/FARHP}
\rightarrow
\text{Candidate Lexemes}
\rightarrow
\text{Candidate AST}.
$$

反向流程一定有不確定性，不要設計成「聲音唯一映射文字」。

---

# 9. P2 — EMPSL v0.8：Editor / Runtime

可以做：

- visual editor；
- AST tree；
- type errors；
- glyph preview；
- pronunciation playback；
- concept inspector；
- lexicon migration inspector；
- compiler output；
- decompiler ambiguity viewer。

---

# 10. P3 — AI 讀寫接口

在語言本體穩定後再接 LLM／Agent。

需要避免模型只學 glyph image 而不知道 stable structure。

優先讓 AI 接收：

```json
{
  "lexeme_id": "...",
  "ast": {},
  "glyph_recipe": {},
  "phonology": {},
  "semantics": {},
  "farhp_ref": "..."
}
```

而不是只餵 PUA 字元。

---

# 11. 長期研究問題

## FARHP

1. FARHP 是否有 speaker-specific stable manifold？
2. FARHP-G 是否比 FARHP-Y 更跨聲道穩定？
3. 哪些 harmonic order 對知覺最重要？
4. PH16 是否足以作 human-readable signature？
5. phase codebook 是否可跨 speaker transfer？

## EMPSL

1. 多少 glyph complexity 才開始降低人類識別？
2. 128 atom 是否過多／過少？
3. 變換 witness 的最佳視覺尺寸？
4. semantic frame 是否造成過強視覺先驗？
5. pronunciation 與 semantic ID 是否應一對多？
6. AST 語法要多接近 functional language？
7. 可否存在人類簡寫層與 AI canonical layer？

---

# 12. 不要做的下一步

目前不建議：

- 再擴 512／1024 個字形原子；
- 再新增大量 WebLab UI；
- 宣稱 FARHP 已被人類實驗證明；
- 直接把 EMPSL 當加密系統；
- 在 typed AST 尚未完成前先大規模造詞；
- 在 lexicon versioning 尚未完成前分配大量永久 PUA；
- 在真實錄音 pilot 前訓練大型神經 FARHP 模型。

---

# 13. 建議的 10 個下一任務

按順序：

1. 建立 EMPSL v0.5 project skeleton；
2. 定義 Lexicon Registry Schema；
3. 定義 Typed AST Schema；
4. 建立 50 個 seed lexemes；
5. 建立 16 個核心 operators；
6. 實作 type checker；
7. 實作 compiler；
8. 實作 decompiler；
9. 建立 2,000 筆 AST conformance corpus；
10. 同步撰寫 FARHP Paper 08。

完成後，再進 Font／IME。

---

# 14. 本地 AI 的下一輪推薦 prompt

```text
PROJECT: EMPSL
CURRENT: v0.4
TARGET: v0.5
TASK:
建立 Versioned Lexicon、Typed AST、Type Checker、Compiler、Decompiler。

MUST PRESERVE:
- stable ID architecture
- v0.4 glyph legality
- FARHP profile reference separation
- recipe SHA-256 rules
- transform witness semantics = none

MUST PRODUCE:
- YAML spec
- JSON Schemas
- 50+ seed lexemes
- 16+ operators
- AST examples
- compiler/decompiler
- round-trip tests
- invalid corpus
- README
- TEST_REPORT
- VALIDATION_REPORT
- ZIP
- SHA256
```

---

# 15. 最終方向

短中期目標不是追求「神秘符號很多」，而是建立一個真正具備：

$$
\boxed{
\text{Identity}
+
\text{Visual Form}
+
\text{Pronunciation}
+
\text{Acoustics}
+
\text{Typed Semantics}
+
\text{Compilation}
}
$$

的人工語言工具鏈。

這也是 FARHP 與 EMPSL 從有趣實驗轉成可持續研究工程的真正分水嶺。

