# 以諾—華語相位符號語言：字形、音節、相位與語義的統一編碼

## 從以諾式構形種子到可逆的華語—FARHP—形式語義物件

**系列：基頻錨定相對諧波相位差（FARHP）第九篇**  
**英文題名：Enochian–Mandarin Phase Symbol Language: Unified Encoding of Glyph, Syllable, Phase, and Semantics**  
**系統名稱：Enochian–Mandarin Phase Symbol Language（EMPSL）**  
**規格命名空間：`eml.empsl`**  
**版本：v0.1**  
**日期：2026-07-31**  
**作者：Neo.K／EveMissLab；Aletheia／GPT-5.6 Thinking**  
**研究狀態：語言架構母規格；含 YAML、JSON Schema 與可驗證範例；尚未完成正式字型**

---

## 摘要

FARHP 系列前七篇已建立基頻錨定相對諧波相位差的數學、聲學、表示、抽取、追蹤與生成架構；後續 WebLab v0.2–v0.4 又以工程方式完成華語單音節、五聲、多音節、變調、輕聲、韻律分組與跨音節聲道插值。本文處理系列最後一個整合問題：如何讓一個新符號同時具有可辨識字形、可朗讀華語音節、可生成 FARHP 聲音、可參與形式語法，並指向版本穩定的語義物件。

本文提出「以諾—華語相位符號語言」（Enochian–Mandarin Phase Symbol Language, EMPSL）。其字形視覺以 John Dee 與 Edward Kelley 相關手稿傳統中的以諾式字母為歷史靈感，但不是歷史以諾語的復原、轉寫或宗教權威宣稱。英國圖書館目錄所載 Sloane MS 3188 收錄 Dee 於 1581–1583 年間的天使會談紀錄，本文只將此手稿傳統視為構形來源之一，而不將其原有語言學或神秘學主張當作本系統的語義基礎。[R1]

EMPSL 的最小符號不是單一圖片或單一 Unicode 碼位，而是一個具有穩定身份的結構物件：

$$
\mathfrak s
=
\left(
I,
G,
P,
T,
\Psi,
\Sigma,
M,
V
\right),
$$

其中 $I$ 是不可因字型改變而變動的身份；$G$ 是字形配方；$P$ 是注音音節序列；$T$ 是聲調與韻律；$\Psi$ 是 FARHP 相位表示；$\Sigma$ 是語法型別與算子結構；$M$ 是語義指涉；$V$ 是版本與命名空間。系統以 ASCII 安全 ID 與結構化 JSON／YAML 作為規範本體，Unicode 私用區只作本地顯示別名，OpenType GSUB／GPOS 則負責構件合字與定位。這是因為 Unicode 私用區雖提供大量私用碼位，但不賦予跨系統共享語義；UAX #31 與 UAX #15 亦表明，識別符與正規化需要明確的實作剖面，而不能依賴字形相似性。[R4][R5][R6]

華語發音層承接教育部國語注音符號手冊及 Unicode Bopomofo 編碼；合法音節以聲母、介音、韻腹、韻尾、四呼與五種調類建模。教育部音節表中的空白組合與「可發音但無常用文字」標記，為未來建立華語可發音空白音節提供了規範接口。[R2][R3] FARHP 層採雙表示：字形只呈現低維相位簽名，精確聲學資料則保存為碼本 ID、離散相位序列或連續圓周向量。語義層採穩定概念 ID、16 類頂層語義框架、型別、參數數量與抽象語法樹，避免「同形即同義」或「同音即同義」。

本文完成 `EMPSL-Spec-v0.1`、JSON Schema、詞彙與表達式範例，並提出可逆序列化、字形—資料分離、版本遷移、輸入法、字型及編譯器路線。EMPSL 可以降低未訓練讀者的直接可讀性，但不是密碼學系統；需要保密的資料仍應使用標準加密。本文的成功標準不是符號看起來神秘，而是同一個符號能在不同字型、裝置、AI 模型與聲音引擎中保持可驗證身份、讀法、相位與語義一致性。

**關鍵詞：** FARHP、EMPSL、以諾式字形、注音、華語音節、相位碼本、形式語義、Unicode 私用區、OpenType、抽象語法樹、可逆編碼

---

# 1. 問題設定：新符號語言不能只是一套替換字母

若將每個漢字、注音或概念直接換成一個陌生圖案，得到的是替換表，而不是新的語言架構。它通常有四個問題：

1. 字形一旦遺失，語義映射便無法恢復；
2. 同一概念在不同字型中可能被誤認為不同符號；
3. 語音、相位與語義混在單一碼位中，無法獨立修改；
4. AI 只能從大量對譯文本重新猜測規則，不能穩定驗證。

因此本文不採：

$$
\text{一個圖片}
=
\text{一個完整語言單位}.
$$

而採：

$$
\boxed{
\text{符號身份}
\neq
\text{字形顯示}
\neq
\text{朗讀形式}
\neq
\text{聲學實現}
\neq
\text{語義值}
}
$$

這五者可以互相映射，但不得互相取代。

## 1.1 系統名稱與歷史邊界

「以諾」在 EMPSL 中表示字形風格與構形種子的歷史來源，不表示：

- 本系統是歷史以諾語；
- 本系統忠實復原 Dee／Kelley 的語法或發音；
- 字形具有宗教、天使或超自然權威；
- 新增符號可被歸屬於原手稿作者。

因此本文使用「以諾式」而不是「真正以諾語」描述新字形。所有新增構件、音系映射、FARHP 相位碼與形式語義均屬 EMPSL 的現代設計。

## 1.2 設計目標

EMPSL 必須同時滿足：

- **穩定身份：** 字型改變不改變符號身份；
- **華語可讀：** 每個可朗讀單位具有明確注音與調類；
- **聲學可生成：** 可交給 FARHP 引擎合成；
- **語義可檢查：** 概念、型別、參數數量與關係可由機器驗證；
- **字形可擴張：** 不必為每個新概念申請一個 Unicode 字元；
- **AI 可學習：** 模型可讀取結構化物件，不依賴 OCR 猜字；
- **人類可書寫：** 字形仍能濃縮為有限構件；
- **版本可遷移：** 舊資料可被新規格讀取或明確拒絕；
- **公開可解碼：** 規格可公開，不以隱匿規則作為安全性來源。

---

# 2. 統一符號物件

## 2.1 八元組

定義一個規範符號：

$$
\mathfrak s
=
\left(
I,G,P,T,\Psi,\Sigma,M,V
\right).
$$

### 身份 $I$

$$
I
=
\left(
\text{namespace},
\text{kind},
\text{local-id}
\right).
$$

例如：

```text
eml.empsl:lexeme:000001
```

身份不包含字型名稱、像素位置或私用區碼位。

### 字形配方 $G$

$$
G
=
\left(
 g_0,
 f,
 \mathbf m_p,
 \mathbf m_\psi,
 \mathbf m_s,
 \mathbf m_o
\right),
$$

其中：

- $g_0$：以諾式種子構件；
- $f$：語義或語法外框；
- $\mathbf m_p$：音節構件；
- $\mathbf m_\psi$：可視相位簽名；
- $\mathbf m_s$：語義類別附標；
- $\mathbf m_o$：算子、參數數量、時態或模態附標。

### 音系 $P$

$$
P
=
\left(
S_1,S_2,\ldots,S_n
\right),
$$

每個音節為：

$$
S_j
=
\left(
O_j,M_j,N_j,C_j,Q_j
\right),
$$

其中 $O$ 是聲母，$M$ 是介音，$N$ 是韻腹，$C$ 是韻尾，$Q$ 是調類。

### 聲調與韻律 $T$

$$
T
=
\left(
\mathbf f_0,
\mathbf d,
\mathbf a,
\mathcal B
\right),
$$

包含基頻軌跡、時長、強度與韻律邊界。調類名稱不能取代實際軌跡。

### 相位 $\Psi$

$$
\Psi
=
\left(
\text{domain},
\text{representation},
\text{profile-id},
\boldsymbol\psi,
\mathbf m,
\mathbf c
\right).
$$

其中 `domain` 至少區分 `FARHP-Y` 與 `FARHP-G`。

### 語法 $\Sigma$

$$
\Sigma
=
\left(
\text{syntactic-kind},
\text{type},
\text{arity},
\text{binding}
\right).
$$

### 語義 $M$

$$
M
=
\left(
\text{concept-id},
\text{semantic-class},
\text{glosses},
\text{constraints}
\right).
$$

### 版本 $V$

$$
V
=
\left(
\text{spec-version},
\text{recipe-version},
\text{codebook-version},
\text{migration-path}
\right).
$$

## 2.2 三種等價關係

### 身份等價

$$
\mathfrak s_1
\equiv_I
\mathfrak s_2
$$

當且僅當兩者命名空間與穩定 ID 相同。

### 讀法等價

$$
\mathfrak s_1
\equiv_P
\mathfrak s_2
$$

表示注音序列、調類與規範變調條件相同。

### 顯示等價

$$
\mathfrak s_1
\equiv_G
\mathfrak s_2
$$

表示兩個字形配方在指定字型與渲染剖面下被視為同一顯示族。

一般而言：

$$
\equiv_I
\not\Rightarrow
\text{像素完全相同},
$$

而：

$$
\equiv_P
\not\Rightarrow
\equiv_I.
$$

同音詞可以是不同身份；同一身份也可以有不同書體。

---

# 3. 字形層：以諾式種子、外框與附標

## 3.1 種子庫不是字母表映射

v0.1 保留 21 個以諾式歷史靈感種子 ID：

```text
ENO-01 ... ENO-21
```

它們在本規格中只表示構形種子，不預先宣稱與拉丁字母、注音或歷史以諾字母存在一對一關係。正式字型階段才會依手稿字形研究建立向量輪廓與來源註記。

另加入 11 個現代結構構件：

```text
STR-01 ... STR-11
```

總計：

$$
21+11=32
$$

個核心構形原子。

32 個原子可透過鏡像、旋轉、開口、閉合、內嵌與交叉等受控操作生成更多字形，但這些操作必須寫入配方，不可只保存渲染結果。

## 3.2 字形槽位

每個標準字形使用六槽結構：

$$
G
=
\left[
\text{frame}
\mid
\text{seed}
\mid
\text{phonology}
\mid
\text{tone}
\mid
\text{phase}
\mid
\text{semantic/operator}
\right].
$$

建議位置：

| 槽位 | 功能 | 規範位置 |
|---|---|---|
| 外框 | 語義大類或語法種類 | 外圍 |
| 主種子 | 詞彙身份的視覺核心 | 中央 |
| 音系附標 | 四呼、韻尾或讀法索引 | 左／下 |
| 聲調附標 | 五種調類 | 上方 |
| 相位附標 | 8／16 類可視簽名 | 右上或內圈 |
| 算子附標 | 參數數量、否定、模態等 | 右／下 |

這只是規範槽位，不限制書法風格。

## 3.3 128 個初版可視原子

v0.1 建議可視原子規模：

$$
32_{\text{seed}}
+
16_{\text{semantic-frame}}
+
16_{\text{phase-mark}}
+
16_{\text{operator-mark}}
+
48_{\text{phonology/tone/structure}}
=
128.
$$

這 128 個原子不是 128 個完整詞，而是可以組合出大量詞彙字形的構件。

## 3.4 渲染函數

令 $F$ 為字型，$E$ 為書寫風格環境，則：

$$
\operatorname{Render}(G;F,E)
\rightarrow
\text{glyph image}.
$$

渲染不是規範解碼：

$$
\operatorname{ParseImage}
\left(
\operatorname{Render}(G)
\right)
\neq
G
$$

不保證成立。可靠往返必須依賴結構化配方。

---

# 4. 華語音節層

## 4.1 依據與範圍

Unicode Bopomofo 區段編碼主要注音符號；教育部國語注音符號手冊則提供聲符、韻符、調號與依開口呼、齊齒呼、合口呼、撮口呼排列的音節表。[R2][R3]

EMPSL v0.1 使用：

- 21 個現代國語聲符；
- 零聲母；
- 介音 $\{\varnothing,\text{ㄧ},\text{ㄨ},\text{ㄩ}\}$；
- 規範韻腹與韻尾；
- 一、二、三、四聲與輕聲；
- 音節合法性狀態。

## 4.2 音節合法性

定義：

$$
\mathcal S_{\text{all}}
=
I\times M\times N\times C\times Q.
$$

合法音節集合為：

$$
\mathcal S_{\text{legal}}
=
\left\{
s\in\mathcal S_{\text{all}}
\mid
L(s)=1
\right\}.
$$

狀態分成：

```text
attested        已有常見漢字／詞例
pronounceable   國語可發音但缺乏常用詞例
reserved        EMPSL 保留的人工音節
illegal         不符合本版華語音系
```

這使 EMPSL 可以利用：

$$
\mathcal S_{\text{vacant}}
=
\mathcal S_{\text{pronounceable}}
\setminus
\mathcal S_{\text{attested}}
$$

建立低衝突的符號讀法，而不需要強迫每個新概念借用常見漢語詞。

## 4.3 多音節與一形多讀

一個符號可以有一至四個規範音節：

$$
1\le n\le4.
$$

但每個版本只指定一個 `canonical_reading`。方言、快速語流或歷史讀法放在別名表，不可覆寫規範讀法。

## 4.4 讀法不是語義

$$
P(\mathfrak s_1)=P(\mathfrak s_2)
$$

不表示：

$$
M(\mathfrak s_1)=M(\mathfrak s_2).
$$

同音是允許的，但識別符、字形核心或語義框架必須不同。

---

# 5. FARHP 相位層

## 5.1 完整相位不可直接畫進單一字形

若一個音節使用 $K$ 個諧波，則 FARHP 狀態為：

$$
\boldsymbol\psi
=
(\psi_2,\ldots,\psi_K)
\in
\mathbb T^{K-1}.
$$

當 $K=32$ 或 $64$ 時，將所有相位座標畫進一個字形會使書寫不可行。因此 EMPSL 分成：

### 可視相位簽名

$$
\pi_{\text{vis}}
=
Q_{16}
\left(
\operatorname{Project}
(\boldsymbol\psi)
\right),
$$

使用 16 類附標，表示主導相位形狀或碼本族。

### 精確相位資料

$$
\pi_{\text{exact}}
\in
\left
\{
\text{codebook-ref},
\text{discrete-vector},
\text{continuous-vector}
\right\}.
$$

## 5.2 三級相位表示

### Level P0：無相位指定

由合成器採用預設相位。

### Level P1：可視簽名

只保存 `PH16-00 ... PH16-15`。

### Level P2：碼本引用

例如：

```text
FARHP-Y:CB-v0.1:0042
```

### Level P3：完整向量

保存：

$$
\left(
\cos\psi_k,
\sin\psi_k
\right),
$$

遮罩與置信度。

## 5.3 字形簽名與精確相位的一致性

規格要求：

$$
\operatorname{Signature}
(\pi_{\text{exact}})
=
\pi_{\text{vis}}.
$$

若不一致，資料應標記：

```text
phase_signature_mismatch
```

而不是默默相信字形或聲學其中一方。

## 5.4 聲音生成

符號的聲學實現為：

$$
\operatorname{Speak}
(\mathfrak s)
=
\mathcal S
\left(
P,T,\Psi,R
\right),
$$

其中 $R$ 是聲母、摩擦、爆破、鼻韻尾與其他非諧波殘差。FARHP 不取代聲調或聲道包絡。

---

# 6. 語義與型別層

## 6.1 16 個頂層語義類

v0.1 定義：

1. `entity`：實體；
2. `process`：過程；
3. `relation`：關係；
4. `property`：性質；
5. `quantity`：數量；
6. `time`：時間；
7. `space`：空間；
8. `modality`：模態；
9. `causality`：因果；
10. `evidence`：證據與認知狀態；
11. `agent`：行動者；
12. `information`：資訊；
13. `permission`：權限與規範；
14. `negation`：否定與排除；
15. `aggregation`：集合與組合；
16. `meta`：語言、型別與版本的後設物件。

此分類只作頂層路由，不宣稱是完整本體論。

## 6.2 穩定概念 ID

人類釋義可變，概念 ID 不因翻譯修改：

```text
eml.concept:item:physical-light
```

若概念本身改變，必須建立新 ID 或新 major version，而不是只改 `gloss`。

## 6.3 型別與參數數量

每個詞彙或算子具有：

$$
\Sigma
=
\left(
\tau_{\text{in}},
\tau_{\text{out}},
 a
\right),
$$

其中 $a$ 是參數數量。

例：因果算子可寫成：

$$
\operatorname{CAUSE}
:
\text{Event}
\times
\text{Event}
\rightarrow
\text{Proposition}.
$$

## 6.4 抽象語法樹

完整表達式不靠字形排列猜測，而以 AST 表示：

$$
E
=
\operatorname{Apply}
\left(
\operatorname{CAUSE},
E_1,
E_2
\right).
$$

字形序列只是 AST 的一種表面形式。

## 6.5 語義檢查

定義型別檢查器：

$$
\operatorname{TypeCheck}(E,\Gamma)
\rightarrow
\left(
\text{valid},
\tau,
\mathbf e
\right),
$$

其中 $\Gamma$ 是詞彙與型別環境，$\mathbf e$ 是錯誤列表。

---

# 7. 編碼本體：ASCII ID、結構化資料與顯示別名

## 7.1 為何不能只用 Unicode 私用區

Unicode 17.0 的基本私用區為 U+E000–U+F8FF，共 6,400 個碼位；它允許私人協議自行定義用途，但 Unicode 不賦予這些碼位標準字義。[R4]

因此若兩個字型都使用 U+E001，它們可以顯示完全不同的符號。EMPSL 規定：

$$
\boxed{
\text{PUA code point}
\neq
\text{canonical symbol identity}
}
$$

## 7.2 三軌編碼

### 規範軌

ASCII 安全身份與 JSON／YAML：

```text
eml.empsl:lexeme:000001
```

### 緊湊交換軌

未來可採 CBOR 或其他明確版本化二進位格式，但必須可還原規範物件。

### 顯示軌

- Unicode 私用區；
- OpenType 合字；
- SVG；
- Canvas；
- Web Component。

顯示軌可替換，規範軌不得因此變動。

## 7.3 私用區剖面

v0.1 建議本地使用：

```text
U+E000–U+E7FF  EMPSL local glyph cache
```

但每個 PUA 映射表都必須附：

- `font_id`；
- `font_version`；
- `mapping_version`；
- `recipe_hash`。

離開該字型環境後，PUA 字串不得被當成自足資料。

## 7.4 識別符剖面

受 UAX #31 的識別符設計原則啟發，EMPSL v0.1 規範 ID 採 ASCII 子集：

```text
^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*:[a-z][a-z0-9_-]*:[0-9a-z_-]+$
```

這避免雙向文字、相似字元及正規化差異進入核心身份。[R5]

## 7.5 Unicode 正規化

所有人類可讀 Unicode 欄位在序列化前採 NFC；規範鍵名使用 ASCII。UAX #15 提供 Unicode 正規化形式與冪等性要求，EMPSL 不自行發明另一套字串正規化。[R6]

## 7.6 OpenType 字型

OpenType 的 GSUB 可依構件序列替換為合字，GPOS 可精確定位聲調、相位與語義附標。[R7][R8]

建議輸入序列：

```text
<frame><seed><phonology><tone><phase><operator>
```

由 GSUB 合成主字形，再由 GPOS 定位附標。字型必須保留「不合字顯示」模式，供除錯與可及性用途。

---

# 8. 規範序列化與雜湊

## 8.1 規範 JSON

序列化前：

1. 使用 UTF-8；
2. 字串採 NFC；
3. 物件鍵以碼點順序排序；
4. 不保存無意義空白；
5. 浮點數使用有限十進位或字串化角度；
6. 陣列順序具有語義，不得重排。

## 8.2 配方雜湊

$$
H_G
=
\operatorname{SHA256}
\left(
\operatorname{CanonicalJSON}(G)
\right).
$$

## 8.3 符號內容雜湊

$$
H_S
=
\operatorname{SHA256}
\left(
\operatorname{CanonicalJSON}
(I,P,T,\Psi,\Sigma,M,V)
\right).
$$

字型更新只改變渲染資產，不應改變 $H_S$；若字形配方改變，$H_G$ 會改變，但身份是否升版由遷移規則決定。

## 8.4 往返條件

規範編碼器 $E$ 與解析器 $D$ 必須滿足：

$$
D(E(\mathfrak s))
=
\mathfrak s.
$$

對非規範輸入，允許：

$$
E(D(x))
=
\operatorname{Canonicalize}(x).
$$

---

# 9. 語言表達與編譯流程

## 9.1 四種表面形式

同一表達式可以呈現為：

1. **EMPSL 字形串；**
2. **注音朗讀串；**
3. **ASCII token 串；**
4. **AST／JSON。**

其中 AST 是語義運算的主要形式。

## 9.2 編譯管線

$$
\text{glyph/token input}
\rightarrow
\text{lexical IDs}
\rightarrow
\text{AST}
\rightarrow
\text{type checking}
\rightarrow
\text{semantic form}
\rightarrow
\text{speech plan}
\rightarrow
\text{FARHP synthesis}.
$$

## 9.3 朗讀管線

$$
\text{lexical IDs}
\rightarrow
P
\rightarrow
\text{變調／韻律}
\rightarrow
T
\rightarrow
\Psi
\rightarrow
\text{audio}.
$$

## 9.4 書寫管線

$$
\text{concept/AST}
\rightarrow
\text{lexical IDs}
\rightarrow
G
\rightarrow
\text{OpenType/SVG render}.
$$

---

# 10. v0.1 初始字形與語義碼表

## 10.1 可視相位碼

16 類可視相位附標：

```text
PH16-00 ... PH16-15
```

對應圓周區間：

$$
\left[
\frac{2\pi j}{16},
\frac{2\pi(j+1)}{16}
\right),
\qquad
j=0,\ldots,15.
$$

若使用投影後的主相位角 $\bar\psi$：

$$
Q_{16}(\bar\psi)
=
\left\lfloor
\frac{16(\operatorname{wrap}(\bar\psi)+\pi)}{2\pi}
\right\rfloor
\bmod16.
$$

## 10.2 語法／算子附標

v0.1 預留：

```text
OP-NULL       非算子
OP-UNARY      一元
OP-BINARY     二元
OP-TERNARY    三元
OP-VARIADIC   可變參數
OP-BIND       綁定
OP-QUOTE      引用
OP-META       後設
OP-TEMP       時態
OP-MODAL      模態
OP-NEG        否定
OP-CAUSE      因果
OP-AGG        聚合
OP-MAP        映射
OP-REDUCE     歸約
OP-GUARD      條件／守衛
```

## 10.3 聲調附標

```text
T1 T2 T3 T4 T0
```

聲調附標只表示詞典調類；表層變調結果放在 utterance／speech-plan 物件中，避免永久改寫詞彙。

---

# 11. 最小範例

## 11.1 詞彙「光」

```json
{
  "id": "eml.empsl:lexeme:000001",
  "kind": "lexeme",
  "glyph_recipe": {
    "seed": "ENO-07",
    "frame": "SEM-ENTITY",
    "phonology_marks": ["ONSET-G", "MEDIAL-U", "RIME-ANG"],
    "tone_mark": "T1",
    "phase_mark": "PH16-05",
    "operator_marks": ["OP-NULL"]
  },
  "pronunciation": {
    "system": "zhuyin",
    "canonical_reading": ["ㄍㄨㄤ"],
    "four_hu": ["hekou"]
  },
  "phase": {
    "domain": "FARHP-Y",
    "representation": "codebook_ref",
    "profile_id": "FARHP-Y:CB-v0.1:0042",
    "visible_signature": "PH16-05"
  },
  "syntax": {
    "kind": "noun",
    "type": "PhysicalPhenomenon",
    "arity": 0
  },
  "semantics": {
    "concept_id": "eml.concept:item:physical-light",
    "semantic_class": "entity",
    "glosses": {
      "zh-Hant": "光",
      "en": "physical light"
    }
  }
}
```

## 11.2 因果表達式

$$
\operatorname{CAUSE}
(\text{light},\text{change}).
$$

AST：

```json
{
  "kind": "application",
  "operator": "eml.empsl:operator:cause",
  "arguments": [
    {"kind": "reference", "target": "eml.empsl:lexeme:000001"},
    {"kind": "reference", "target": "eml.empsl:lexeme:000002"}
  ]
}
```

---

# 12. 輸入法與人機協作

## 12.1 人類輸入

建議輸入法提供三種模式：

### 注音模式

輸入注音後列出具有相同讀法的 EMPSL 詞彙，依語義類別與上下文排序。

### 概念模式

輸入自然語言、概念 ID 或語義類別，選擇詞彙。

### 構形模式

直接選擇種子、外框、相位及算子附標，用於創造新符號。

## 12.2 AI 輸入

AI 不應輸出只有 PUA 字元的裸字串，而應輸出：

```json
{
  "tokens": ["eml.empsl:lexeme:000001"],
  "ast": {},
  "render_profile": "EMPSL-Default-v0.1"
}
```

介面再負責渲染。

## 12.3 語言模型 token

初期不需要為每個完整字形訓練單獨 tokenizer token。可以使用：

- 穩定 ID token；
- 字形構件 token；
- 語義類與型別 token；
- FARHP 碼本 token。

這使模型能學習組合結構，而不是死記數萬個圖片。

---

# 13. 安全性、可讀性與保密邊界

EMPSL 對未學習者可能不易直接閱讀，但：

$$
\boxed{
\text{陌生字形}
\neq
\text{密碼學安全}
}
$$

只要映射表、語料與規格公開，AI 或人類都能解析。即使規格不公開，大量對譯文本也可能讓模型推測對應關係。

因此：

- 公開理論可使用 EMPSL 作形式化載體；
- 未公開資料仍需使用標準加密；
- 權限控制不可只靠自訂字型；
- PUA 字串不可當作存取控制；
- 不將「難懂」誤當成「不可取得」。

---

# 14. 可證偽命題與測試

## 命題一：序列化往返

對所有合法符號：

$$
D(E(\mathfrak s))
=
\mathfrak s.
$$

## 命題二：字型獨立身份

對兩個相容字型 $F_1,F_2$：

$$
\operatorname{ResolveID}
(\operatorname{Render}(G;F_1))
=
\operatorname{ResolveID}
(\operatorname{Render}(G;F_2))
$$

必須透過伴隨資料或輸入序列成立，而不是依賴像素 OCR。

## 命題三：相位簽名一致性

$$
\operatorname{Signature}
(\pi_{\text{exact}})
=
\pi_{\text{vis}}.
$$

## 命題四：語音可重現性

固定：

$$
(P,T,\Psi,R,\text{engine-version},\text{seed})
$$

時，輸出 WAV 應在指定數值容差內可重現。

## 命題五：語義型別可檢查

非法參數數量或型別組合必須被拒絕，而不是只生成外觀合理的字形。

## 命題六：PUA 可替換性

改變 PUA 映射與字型後，規範 JSON 的 $I,P,\Psi,\Sigma,M$ 不應改變。

## 命題七：版本遷移確定性

同一舊版物件經同一遷移器應產生相同新版規範物件與內容雜湊。

---

# 15. 技術路線

## Phase A：規格閉合

本輪完成：

- 統一符號八元組；
- 32 種子／結構原子命名；
- 16 語義類；
- 16 相位可視碼；
- 16 算子附標；
- PUA 與規範身份分離；
- YAML、JSON Schema 與範例。

## Phase B：字形生成器

下一階段：

- 建立 32 個 SVG 原子；
- 實作六槽構形；
- 產生 128 原子字形圖表；
- 輸出 SVG／PNG／字形配方；
- 建立字形碰撞檢測。

## Phase C：OpenType 字型與輸入法

- GSUB 合字；
- GPOS 附標定位；
- PUA 本地映射；
- 注音／概念／構形三模式輸入；
- 不合字除錯模式。

## Phase D：EMPSL 編譯器

- 詞彙庫；
- AST parser；
- 型別檢查器；
- 語義驗證；
- FARHP speech plan；
- WebLab 播放接口。

## Phase E：公開語料與模型接口

- 平行語料；
- 結構化 tokenizer；
- AI 生成限制；
- 版本遷移；
- 人類可讀教材。

---

# 16. 與 FARHP 系列的閉合關係

FARHP 系列原定：

$$
4\text{ 篇理論}
\rightarrow
1\text{ 篇架構}
\rightarrow
2\text{ 篇工程}
\rightarrow
2\text{ 篇語言整合}.
$$

第八篇的華語音節與聲調整合尚待補成正式論文，但其工程內容已在 WebLab v0.2–v0.4 中實作：

- 注音聲母與韻母；
- 五聲；
- 三聲、一、不變調；
- 輕聲；
- 韻律分組；
- 句調；
- 跨音節聲道插值；
- FARHP 音節與語流 JSON Schema。

本文以這些工程物件為已存在接口，完成第九篇的符號—語音—相位—語義統一規格。後續可從實作反寫第八篇，而不必讓第九篇等待。

---

# 17. 結論

EMPSL 的核心不是「畫出一批神秘字」，而是建立以下可驗證同構鏈：

$$
\boxed{
\text{穩定身份}
\leftrightarrow
\text{字形配方}
\leftrightarrow
\text{華語讀法}
\leftrightarrow
\text{FARHP 聲學}
\leftrightarrow
\text{型別化語義}
}
$$

其規範本體是 ASCII ID 與結構化資料；以諾式字形是可替換的顯示層；注音是朗讀層；FARHP 是聲學實現層；AST 與穩定概念 ID 是語義運算層。

因此，同一個符號可以：

- 被人類書寫；
- 被華語朗讀；
- 被 FARHP 引擎合成；
- 被 AI 精確解析；
- 被編譯器進行型別檢查；
- 在字型更新後仍保有同一身份。

這使 EMPSL 從一套視覺替換符號，轉變為一個可以持續擴張、公開規範、機器驗證與聲音生成的形式語言底座。

---

# 參考資料

**[R1]** British Library, *Sloane MS 3188*, catalogue record: John Dee's conferences with angels, 1581–1583.  
https://searcharchives.bl.uk/catalog/040-002115572

**[R2]** The Unicode Consortium, *Bopomofo, U+3100–U+312F*, Unicode Standard Version 17.0.  
https://www.unicode.org/charts/PDF/U3100.pdf

**[R3]** 中華民國教育部，*國語注音符號手冊*。  
https://language.moe.gov.tw/001/Upload/files/site_content/M0001/juyin/html_ch/index.html

**[R4]** The Unicode Consortium, *The Unicode Standard, Chapter 23: Special Areas and Format Characters*, Private Use Area.  
https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/

**[R5]** The Unicode Consortium, *Unicode Standard Annex #31: Unicode Identifiers and Syntax*.  
https://www.unicode.org/reports/tr31/

**[R6]** The Unicode Consortium, *Unicode Standard Annex #15: Unicode Normalization Forms*.  
https://www.unicode.org/reports/tr15/

**[R7]** Microsoft, *OpenType Specification: GSUB — Glyph Substitution Table*.  
https://learn.microsoft.com/en-us/typography/opentype/otspec140/gsub

**[R8]** Microsoft, *OpenType Specification: GPOS — Glyph Positioning Table*.  
https://learn.microsoft.com/en-us/typography/opentype/spec/gpos

---

**論文結束**
