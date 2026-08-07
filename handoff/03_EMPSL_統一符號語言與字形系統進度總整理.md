# EMPSL 統一符號語言與字形系統進度總整理

**用途：** EMPSL 主規範交接文件  
**版本：** Handoff v1.0  
**日期：** 2026-08-07

---

# 1. EMPSL 的正確理解

EMPSL = **Enochian–Mandarin Phase Symbol Language**。

它是一個現代人工符號／形式語言工程，不是：

- 歷史以諾語復原；
- 天使語真實性主張；
- 密碼學安全機制；
- 單純字體替換；
- 只給人看的圖形系統。

其真正目標是把：

$$
\boxed{
\text{Identity}
+
\text{Glyph}
+
\text{Mandarin Phonology}
+
\text{FARHP}
+
\text{Typed Semantics}
}
$$

放進同一個機器可驗證結構。

---

# 2. 統一符號物件

目前母規格：

$$
\mathfrak s
=
(I,G,P,T,\Psi,\Sigma,M,V).
$$

## $I$ — Identity

穩定 ID，例如：

```text
eml.empsl:lexeme:000001
eml.concept:item:physical-light
eml.concept:operator:cause
```

身份必須獨立於：

- 字形；
- PUA code point；
- 翻譯；
- 字體版本。

## $G$ — Glyph

六槽字形配方。

## $P$ — Phonology

注音、聲母、四呼、韻類、結構。

## $T$ — Tone / Prosody

聲調與未來韻律描述。

## $\Psi$ — FARHP

完整 profile 或可視 PH16 signature。

## $\Sigma$ — Typed Semantics

- kind；
- inputs；
- output；
- arity；
- operator role。

## $M$ — Meaning

概念身份、定義、語義分類。

## $V$ — Version / Namespace

版本、來源、命名空間與 compatibility。

---

# 3. 為何字形不能是唯一身份

Unicode PUA 可用於本地渲染，但不應作規範本體。

原因：

- 不同字型可對同一 PUA 顯示不同圖形；
- 不同系統可能有不同 PUA 分配；
- 字形可能改版；
- OpenType 合字本身不是資料身份；
- 語義與讀音可能更新而不應迫使身份改變。

因此：

$$
\boxed{
\text{Stable ID}
\neq
\text{PUA}
\neq
\text{Glyph Shape}
}
$$

PUA 與字體只作顯示層。

---

# 4. EMPSL v0.1 — 統一編碼母規格

已完成：

- 穩定身份；
- 字形 recipe；
- 注音層；
- FARHP-Y／G；
- PH16 可視簽名；
- 16 類頂層語義；
- typed operator；
- AST example；
- NFC normalization；
- JSON Schema；
- YAML spec；
- validator；
- sample lexicon。

核心原則：

$$
\text{Glyph Signature}(\Psi)
\neq
\Psi_{\text{exact}}.
$$

完整 FARHP 不能硬塞進肉眼字形。

---

# 5. EMPSL v0.2 — 字形工程

建立 128 原子：

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

## 5.1 32 核心種子

- 21 個以諾式歷史視覺靈感種子；
- 11 個現代結構種子。

這 32 個種子是現代構形原子，不等同於歷史字母的真實音值或語義。

## 5.2 16 語義外框

用於 broad semantic class。

## 5.3 16 PH16 相位簽名

只作可視 phase signature。

## 5.4 16 算子／語義附標

用於 operator／semantic role。

## 5.5 48 音系／聲調／結構附標

包含：

- 21 聲母；
- 4 四呼；
- 12 韻類；
- 5 詞典聲調；
- 6 結構附標。

---

# 6. 六槽字形

v0.2 核心：

$$
G
=
[F\mid S\mid P\mid T\mid\Phi\mid O].
$$

其中：

- $F$：semantic frame；
- $S$：seed；
- $P$：phonology/structure marks；
- $T$：tone；
- $\Phi$：visible phase signature；
- $O$：operator/semantic mark。

配方雜湊：

$$
H_G
=
\operatorname{SHA256}
\left(
\operatorname{CanonicalJSON}
(F,S,P,T,\Phi,O)
\right).
$$

注意：雜湊是配方身份／完整性工具，不等於語義 ID。

---

# 7. EMPSL v0.3 — 受控變換

建立 8 種變換：

```text
ID
R90
R180
MX
OPEN-R
CLOSED
INSET
CROSS
```

因此：

$$
32\times8=256
$$

個種子變體。

穩定變體 ID：

```text
<base-seed>@<transform-id>
```

例如：

```text
ENO-07@OPEN-R
STR-04@INSET
```

---

# 8. 為何需要 transform witness

純幾何變換會因對稱性而產生碰撞。

v0.3 實測：

- 256 raw geometry variants；
- 40 組 exact collision；
- 104 個變體受影響。

因此定義：

$$
\widetilde G_{s,t}
=
G_{s,t}\oplus w(t),
$$

其中 $w(t)$ 是 3-bit transform witness。

加入 witness 後：

$$
N_{\mathrm{exact}}^{\mathrm{canonical}}=0.
$$

重要：witness 只表示「變換身份」，不承載語義。

---

# 9. v0.3 大規模碰撞測試

建立 8,192 個唯一六槽配方。

每個配方保存：

- recipe SHA-256；
- normalized pixel SHA-256；
- 64-bit dHash；
- slot parameters；
- transform identity。

結果：

$$
N_{\mathrm{exact}}^{\mathrm{composite}}=0.
$$

near collision：

- dHash Hamming distance $\le4$；
- 只作人工審查；
- 不等於語義 collision。

---

# 10. EMPSL v0.4 — 字形語法與合法性

v0.4 的核心思想：

> 「能畫出來」不代表「是合法 EMPSL 符號」。

合法性要求：

$$
\boxed{
\text{Identity}
\land
\text{Phonology}
\land
\text{Transform}
\land
\text{Typed Semantics}
\land
\text{FARHP Compatibility}
}
$$

完整 object 擴展為：

$$
\mathfrak g
=
(G,P,T,\Phi,O,R_s,\Sigma,A,C).
$$

$C$ 是 legality certificate。

---

# 11. 30 條規則

| Domain | Count |
|---|---:|
| Glyph identity | 4 |
| Mandarin phonology | 10 |
| Controlled transform | 3 |
| Typed semantics | 6 |
| FARHP acoustics | 7 |

PASS 條件：

$$
\mathrm{PASS}
\Longleftrightarrow
\mathrm{error\_count}=0.
$$

warnings 仍可交換，但必須保留。

---

# 12. 音系合法性目前涵蓋

v0.4 檢查：

- onset × 四呼；
- 四呼 × 韻類；
- `RIME-ER` 零聲母限制；
- 輕聲 × `ST-LIGHT`；
- 鼻韻 × `ST-NASAL`；
- 零聲母／有聲母互斥；
- boundary marker 排他；
- 兒化重複；
- 非 boundary 詞素必須有韻核。

注意：這不是完整教育部全部音節資料庫，只是目前工程 legality layer。

---

# 13. 型別化語義

範例 operator：

```json
{
  "kind": "operator",
  "concept_id": "eml.concept:operator:cause",
  "signature": {
    "inputs": ["Event", "Event"],
    "output": "Relation",
    "arity": {
      "mode": "fixed",
      "value": 2
    }
  }
}
```

固定 arity：

$$
|\mathrm{inputs}|
=
\mathrm{arity.value}.
$$

variadic：

$$
|\mathrm{inputs}|
\ge
\mathrm{arity.min}.
$$

v0.5 將把這一層正式提升為 AST type inference。

---

# 14. FARHP 相容性

visible phase signature 必須與 acoustic profile 一致：

$$
\Phi_{\mathrm{glyph}}
=
\Phi_{\mathrm{acoustic}}.
$$

聲學 category：

```text
voiced-harmonic
mixed
noise-dominant
silent
```

靜音 boundary 應滿足：

$$
\mathrm{source}=NONE,
$$

$$
\Phi=PH16\mbox{-}00,
$$

$$
\mathrm{profile\_id}=\varnothing.
$$

---

# 15. v0.4 4,096 筆符合性語料

$$
4{,}096
=
1{,}024_{\text{legal}}
+
1{,}024_{\text{mutated}}
+
2{,}048_{\text{fuzz}}.
$$

結果：

- legal：1024/1024 PASS；
- mutated：1024/1024 被攔截；
- fuzz：2048/2048 被攔截。

Python 與 Node／browser engine 進行交叉驗證。

這只是 generated conformance corpus，不代表完整語言正確率為 100%。

---

# 16. EMPSL v0.5 應該做什麼

下一個自然節點不是再增加原子，而是建立「可組合語言」。

$$
\boxed{
\text{v0.5}
=
\text{Versioned Lexicon}
+
\text{Typed AST}
+
\text{Type Inference}
+
\text{Compiler}
+
\text{Decompiler}
}
$$

建議子模組：

## 16.1 Lexicon Registry

每個 lexeme 保存：

- stable lexeme ID；
- concept ID；
- glyph recipe；
- phonology；
- tone；
- FARHP profile reference；
- semantic signature；
- lifecycle；
- version；
- aliases；
- provenance。

## 16.2 Typed AST

建議 AST node：

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

## 16.3 Type Inference

最低要求：

- operator arity；
- input type compatibility；
- output type inference；
- unresolved type variable；
- type error certificate。

## 16.4 Compiler

輸入：AST／lexeme IDs。  
輸出：canonical token sequence／glyph sequence／pronunciation plan／acoustic references。

## 16.5 Decompiler

輸入：canonical token／glyph recipe sequence。  
輸出：AST candidate。

注意：如果語言允許歧義，decompiler 應輸出候選集合與 confidence，不應假裝永遠唯一。

---

# 17. v0.6 之後

## v0.6 — Font / Input

- OpenType GSUB；
- GPOS；
- component sequence → ligature；
- debug non-ligature mode；
- PUA mapping profile；
- IME／input method；
- keyboard scheme。

## v0.7 — Speech Integration

- EMPSL sequence → Mandarin phonology；
- phonology → FARHP WebLab／vocoder request；
- speech → phonology／FARHP extraction → candidate EMPSL tokens。

## v0.8+ — Editor／Runtime

- syntax highlighting；
- AST inspector；
- lexicon version migration；
- compiler diagnostics；
- speech playback；
- language model tokenizer／agent API。

---

# 18. EMPSL 禁止事項

本地 AI 不應：

- 讓 PUA 成為唯一 stable ID；
- 直接把完整 FARHP vector 畫進字形；
- 無限制擴原子而不做 collision／legality；
- 用像素近似就判定語義相同；
- 把 transform witness 當語義；
- 自動修正專業語義而沒有確定規則；
- 把 Schema Valid 當 Grammar Valid；
- 讓 lexeme definition 更新造成 stable ID 任意變動；
- 忽略版本與 migration。

---

# 19. 重要現有檔案

EMPSL v0.1：

- `FARHP_09_以諾華語相位符號語言_統一編碼_v0.1.md`
- `EMPSL_Spec_v0.1.yaml`
- `EMPSL_Unified_Encoding_Spec_v0.1.schema.json`

EMPSL v0.2：

- `EMPSL_atom_registry_v0.2.json`
- `EMPSL_Glyph_Recipe_Spec_v0.2.schema.json`
- 128 SVG atoms；
- 32 seed chart。

EMPSL v0.3：

- `EMPSL_Controlled_Transform_Spec_v0.3.yaml`
- `EMPSL_seed_variant_registry_v0.3.json`
- `EMPSL_composite_collision_corpus_v0.3.jsonl`
- `EMPSL_collision_report_v0.3.json`

EMPSL v0.4：

- `EMPSL_Glyph_Grammar_Spec_v0.4.yaml`
- `EMPSL_rule_catalog_v0.4.json`
- `EMPSL_legality_corpus_v0.4.jsonl`
- `EMPSL_legality_report_v0.4.json`
- `empsl_v04_validate.py`
- `empsl_v04_batch_check.py`

---

# 20. 一句話交接

> EMPSL 的身份、字形、受控變換與 legality 已完成；下一步的瓶頸已不是「還缺什麼符號」，而是如何把合法詞素升級為 versioned lexicon 與 typed AST，正式建立可編譯、可反編譯的語言工具鏈。

