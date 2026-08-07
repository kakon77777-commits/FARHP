# EMPSL v0.4 驗證報告

- 日期：2026-07-31
- 規格：EMPSL Glyph Grammar and Legality v0.4
- 規則數：30
- 規則集指紋：`84fecd66f230f4c52fd125e45a4164c96c7afc8fad5c6f40fa47c9f67f3cb689`

## 結果摘要

| 類別 | 數量 | 驗證結果 |
|---|---:|---:|
| 合法生成案例 | 1,024 | 1,024 PASS |
| 故意破壞案例 | 1,024 | 1,024 FAIL |
| 模糊測試案例 | 2,048 | 2,048 FAIL |
| 總計 | 4,096 | 與預期完全一致 |

因此：

$$
\operatorname{TPR}_{\mathrm{legal}}=1,
\qquad
\operatorname{TNR}_{\mathrm{invalid}}=1
$$

僅表示本規格內、由本輪生成器產生的符合性語料完全一致，不代表已覆蓋所有華語音系與形式語義錯誤。

## 規則域

| 域 | 規則數 |
|---|---:|
| 字形身份 | 4 |
| 華語音系 | 10 |
| 受控變換 | 3 |
| 型別化語義 | 6 |
| FARHP 聲學 | 7 |
| 合計 | 30 |

## 問題總量

在全部語料中，驗證器共產生：

- 錯誤：23,373；
- 警告：3,931。

同一案例可以同時命中多條規則，因此問題總量大於非法案例數。

## 雙引擎交叉驗證

Python 驗證器對 4,096 筆案例逐筆重新計算：

- `valid`、錯誤數、警告數一致；
- 規則 ID、嚴重度與欄位一致；
- 配方 SHA-256 全部往返一致；
- 合法案例全部通過 JSON Schema；
- 符合性案例外層全部通過 Validation Case Schema。

```text
PASS batch cross-validation · 4096 cases · rules=30 · valid=1024 · invalid=3072
```

## 繼承層驗證

v0.3 的 128 原子、256 變體與碰撞資產仍通過原驗證器：

```text
RESULT · 21/21 PASS
```

## 圖表

- `assets/charts/EMPSL_v0.4_rule_hits.png`
- `assets/charts/EMPSL_v0.4_corpus_summary.png`

## 限制

本驗證語料由規則生成器與模糊生成器建立，尚未取代：

- 完整國語音節資料庫；
- 專家人工標註詞彙庫；
- 真實 FARHP codebook；
- AST 級型別推論；
- 人類字形辨識與聽覺實驗。
