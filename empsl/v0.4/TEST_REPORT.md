# EMPSL v0.4 測試報告

- 日期：2026-07-31
- 平台：Linux / Python 3.13 / Node.js 22 / Chromium

## 自動測試

### Node 核心規則

```text
PASS EMPSL v0.4 core tests · 30 groups
```

涵蓋：

- 規則與語料數量；
- 合法／非法案例；
- FARHP 相位簽名錯誤；
- 算子參數數量錯誤；
- 聲母／四呼／韻類錯誤；
- 邊界靜音物件；
- 自動修正；
- v0.3 至 v0.4 升級；
- 配方雜湊。

### Python 獨立驗證

```text
PASS batch cross-validation · 4096 cases · rules=30 · valid=1024 · invalid=3072
```

### Chromium 互動測試

```text
PASS browser v0.4 · rules=30 · variants=8 · console_errors=0
```

實際測試流程：

1. 載入合法案例並得到 PASS；
2. 顯示 30 條規則；
3. 顯示目前種子的 8 個變體；
4. 載入非法案例並得到 FAIL；
5. 顯示規則問題卡；
6. 執行自動修正並回到 PASS；
7. 建立 `ONSET-G + HU-CUOKOU + RIME-AI`；
8. 同時命中 `P-002` 與 `P-003`；
9. 控制台錯誤為 0。

由於執行環境封鎖本機 HTTP URL，Chromium 測試將所有本地 JavaScript 資產內嵌後載入；網站本身仍可直接以 `index.html` 離線開啟。

## 靜態檢查

| 項目 | 結果 |
|---|---:|
| Python compileall | PASS |
| JavaScript 語法 | 2／2 PASS |
| JSON 解析 | 21／21 PASS |
| YAML 解析 | 4／4 PASS |
| v0.3 繼承驗證 | 21／21 PASS |
| 瀏覽器控制台錯誤 | 0 |

## 測試邊界

沒有宣稱完成：

- 真實人類語言學標註一致性；
- 所有國語方言與異讀；
- OpenType 字型測試；
- 行動裝置瀏覽器矩陣；
- 大型詞彙庫併發與版本合併。
