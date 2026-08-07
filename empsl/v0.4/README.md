# EMPSL v0.4 — Glyph Grammar Lab

EMPSL v0.4 在 v0.3 的 128 原子、256 種子變體與六槽字形之上，新增華語音系、受控變換、型別語義與 FARHP 聲學合法性規則。

## 快速使用

直接開啟：

```text
index.html
```

驗證範例：

```bash
python -m pip install -r requirements.txt
python tools/empsl_v04_validate.py examples/EMPSL_legality_examples_v0.4.json
node tests/test_core_v0.4.js
```

## 主要內容

- `index.html`：互動式字形語法實驗室；
- `rules/`：30 條規則與相容性資料表；
- `spec/`：v0.4 YAML 與 JSON Schema；
- `corpus/`：4,096 筆符合性語料；
- `tools/`：Python 驗證器與批次交叉檢查；
- `tests/`：Node 與 Chromium 測試；
- `assets/charts/`：規則命中與語料摘要圖；
- `reference_v0.1/`：統一編碼母規格參考。

## 驗證原則

$$
\mathrm{PASS}
\Longleftrightarrow
\mathrm{error\_count}=0.
$$

警告仍會保留於證書中。

## 重要邊界

這是現代設計的形式符號語言與聲學研究工具，不是歷史以諾語復原，也不是加密系統。
