# EMPSL 字形語法與合法性技術規格 v0.4

- 專案：Enochian–Mandarin Phase Symbol Language
- 簡稱：EMPSL
- 版本：0.4
- 狀態：字形語法與合法性 MVP
- 日期：2026-07-31

## 摘要

EMPSL v0.3 已經建立 128 個原子、256 個可追溯種子變體、六槽字形配方與大規模碰撞檢查。然而，「可以被繪製」不等於「是合法語言物件」。v0.4 因此增加跨欄位規則引擎，使字形配方必須同時通過字形身份、華語音系、受控變換、型別化語義與 FARHP 聲學五個檢查域。

一個 v0.4 詞素物件記為：

$$
\mathfrak g
=
\left(
G,P,T,\Phi,O,R_s,\Sigma,A,C
\right),
$$

其中：

- $G$：六槽字形配方；
- $P$：華語音系附標；
- $T$：詞典聲調；
- $\Phi$：可視 FARHP 相位簽名；
- $O$：語義／算子附標；
- $R_s$：受控種子變換角色；
- $\Sigma$：型別化語義簽名；
- $A$：聲學物件；
- $C$：合法性證書。

## 一、合法性不是單一布林值

驗證結果定義為：

$$
C(\mathfrak g)
=
\left(
\mathrm{status},E,W,I,H_R
\right),
$$

其中：

- $E$：錯誤數；
- $W$：警告數；
- $I$：具規則 ID、欄位與修正建議的問題序列；
- $H_R$：規則集指紋。

通過條件是：

$$
\mathrm{PASS}
\Longleftrightarrow
E=0.
$$

警告不會阻止資料交換，但必須保留在證書中，避免低信心度或弱適用性的資料被誤讀為無條件成立。

## 二、五個驗證域

### 2.1 字形身份域

字形身份域檢查：

1. 所有原子 ID 均已註冊；
2. `seed_base`、`seed_transform` 與 `seed_variant` 一致；
3. 音系附標不超過四個；
4. 配方版本為 `0.4`。

種子變體必須滿足：

$$
V=S\mathbin{@}T_r,
$$

其中 $S$ 是基礎種子，$T_r$ 是受控變換。

### 2.2 華語音系域

音系區最多包含：

$$
P=[O,H,R,S],
$$

其中 $O$ 為聲母、$H$ 為四呼、$R$ 為韻類、$S$ 為結構附標。每一類最多一個。

v0.4 檢查：

- 聲母與四呼相容性；
- 四呼與韻類相容性；
- `RIME-ER` 的零聲母／開口呼限制；
- 輕聲與 `ST-LIGHT` 的一致性；
- 鼻韻與 `ST-NASAL` 的一致性；
- `ST-ZERO` 與聲母互斥；
- `ST-BOUNDARY` 排他性；
- 兒化不得重複編碼；
- 非邊界詞素必須具有韻核。

這是一個為 EMPSL 工程使用的縮減音系模型，不聲稱覆蓋所有國語異讀、方言、歷史音或語流變體。

### 2.3 受控變換域

幾何變換不再自動等於語義變換。每個配方必須聲明：

```text
identity
allographic
semantic_modifier
structural
```

例如：

- `ID` 可作身份或異體角色；
- `R90`、`R180`、`MX` 可作異體或語義修飾；
- `OPEN-R` 必須作語義修飾；
- `INSET` 可作結構或語義修飾；
- `CROSS` 只允許述詞／算子類物件；
- 邊界符號只可使用 `ID`。

因此：

$$
\mathrm{TransformValid}
=
f(T_r,R_s,K_s),
$$

其中 $K_s$ 是語義種類。

### 2.4 型別化語義域

語義物件包含：

```json
{
  "kind": "operator",
  "concept_id": "eml.concept:operator:cause",
  "signature": {
    "inputs": ["Event", "Event"],
    "output": "Relation",
    "arity": {"mode": "fixed", "value": 2}
  }
}
```

固定參數算子必須滿足：

$$
|\mathrm{inputs}|=\mathrm{arity.value}.
$$

可變參數算子則滿足：

$$
|\mathrm{inputs}|\geq\mathrm{arity.min}.
$$

v0.4 為 16 個算子附標建立參數規則，例如：

- `OP-NULL`：固定 $0$；
- `OP-UNARY`：固定 $1$；
- `OP-BINARY`：固定 $2$；
- `OP-TERNARY`：固定 $3$；
- `OP-CAUSE`：固定 $2$；
- `OP-BIND`：固定 $2$；
- `OP-VARIADIC`、`OP-AGG`：可變參數。

語義外框同時限制可用算子；例如因果、否定、時態與模態算子不能任意放入不相干外框。

### 2.5 FARHP 聲學域

聲學物件包含：

```json
{
  "source": "FARHP-Y",
  "class": "voiced_harmonic",
  "phase_signature": "PH16-05",
  "profile_id": "eml.farhp:profile:light-v01",
  "confidence": 0.92
}
```

可視簽名必須滿足：

$$
\Phi_{\mathrm{glyph}}
=
\Phi_{\mathrm{acoustic}}.
$$

聲學類別由音系推導：

$$
\Gamma_A
\in
\{\text{voiced-harmonic},\text{mixed},\text{noise-dominant},\text{silent}\}.
$$

靜音邊界必須滿足：

$$
\mathrm{source}=\mathrm{NONE},
\qquad
\Phi=\mathrm{PH16\mbox{-}00},
\qquad
\mathrm{profile\_id}=\varnothing.
$$

非靜音物件則必須指定 `FARHP-Y` 或 `FARHP-G` 與 profile ID。噪聲主導音使用非零 PH16、或非靜音物件的信心度低於 $0.5$ 時，驗證器會產生警告而非偽裝成高可靠度相位控制。

## 三、結構驗證與語法驗證分離

JSON Schema 只回答：

> 欄位、型別、枚舉與格式是否正確？

規則引擎回答：

> 多個欄位放在一起是否形成合法語言物件？

因此：

$$
\mathrm{SchemaValid}
\not\Rightarrow
\mathrm{GrammarValid}.
$$

例如一份 JSON 可以在結構上包含合法的 `ONSET-G`、`HU-CUOKOU` 與 `RIME-AI`，但三者的組合仍會被音系規則拒絕。

## 四、配方指紋

v0.4 指紋包含會改變身份的全部結構欄位：

$$
H_G
=
\operatorname{SHA256}
\left(
\operatorname{CanonicalJSON}
\left(
G,R_s,\Sigma,A
\right)
\right).
$$

讀法與自然語言義註不納入核心指紋，允許註解修訂；字形、相位、型別或聲學資料改變時，指紋必須改變。

## 五、保守式自動修正

網站提供自動修正，但遵守：

1. 不猜測新的專業語義；
2. 優先修正可機械推導的欄位；
3. 邊界物件轉為完全靜音；
4. 算子參數依算子表重建；
5. FARHP 類別依音系重新推導；
6. 若變換與語義種類無交集，退回 `ID`；
7. 修正後重新產生完整證書與指紋。

自動修正是工程輔助，不是理論上的唯一正規形。

## 六、符合性語料

v0.4 建立 $4{,}096$ 筆語料：

$$
4{,}096
=
1{,}024_{\mathrm{legal}}
+
1{,}024_{\mathrm{mutated}}
+
2{,}048_{\mathrm{fuzz}}.
$$

驗證結果：

- 合法生成器：$1{,}024/1{,}024$ 通過；
- 故意破壞案例：$1{,}024/1{,}024$ 被攔截；
- 模糊測試：$2{,}048/2{,}048$ 被攔截。

語料保存每個案例的配方、預期結果、問題證書與配方指紋，供不同語言實作做交叉驗證。

## 七、軟體介面

### 瀏覽器

`index.html` 提供：

- 六槽字形即時預覽；
- 音系、變換、語義與聲學控制；
- 規則 ID 與修正建議；
- 合法／非法案例載入；
- 保守式自動修正；
- SVG／JSON 匯出；
- 30 條規則與語料命中次數。

### Python

```bash
python tools/empsl_v04_validate.py \
  examples/EMPSL_legality_examples_v0.4.json
```

### Node

```bash
node tests/test_core_v0.4.js
```

## 八、已知邊界

v0.4 尚未完成：

- 全部國語合法音節表；
- 韻律詞與句法變調；
- 真實 FARHP codebook 的簽名推導；
- AST 表達式的完整型別推論；
- 詞彙庫的版本衝突處理；
- OpenType 字型與輸入法；
- 人類可辨識度實驗。

因此 v0.4 是**語法與合法性底座**，不是完整自然語言編譯器。

## 九、下一版本

EMPSL v0.5 應進入「詞彙庫與型別化 AST 編譯層」：

$$
\text{合法詞素}
\rightarrow
\text{詞彙庫}
\rightarrow
\text{AST}
\rightarrow
\text{型別檢查}
\rightarrow
\text{可朗讀／可合成序列}.
$$
