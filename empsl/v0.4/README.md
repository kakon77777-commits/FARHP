# Axioglyph｜理符 — EMPSL v0.4 Glyph Grammar Lab

Axioglyph 是 EMPSL 的獨立對外網站品牌；EMPSL v0.4 仍是底層技術名稱與目前權威版本。v0.4 在 128 原子、256 種子變體與六槽字形之上，整合華語音系、受控變換、型別語義與 FARHP 聲學合法性規則。

## 本機開啟

請從這個目錄啟動本機 HTTP 服務：

```powershell
python -B -m http.server 8765 --bind 127.0.0.1
```

然後開啟：

```text
http://127.0.0.1:8765/
```

HTTP 是正式驗收入口；不要用直接雙擊 `index.html` 取代瀏覽器測試。

## 網站內容

- `概念`：一般訪客可在 60–90 秒內理解身份、構形、語義與證書；
- `系統`：六槽字形模型與「構形 → 驗證 → 證書 → 交換」流程；
- `實驗室`：完整 v0.4 配方控制器、合法／錯誤案例、自動修正及 SVG／JSON 匯出；
- `證據`：30 條規則、4,096 筆語料、Node／Python 交叉檢查與兩層 SHA-256；
- `方法`：Schema、規則引擎、八個受控變體與完整規則目錄；
- `路線圖`：目前 v0.4 與規劃中的 v0.5 工具鏈；
- `FAQ`：字型、自然語言、歷史復原、加密與研究邊界。

所有網站相依項目皆使用相對路徑；同一目錄未來可掛在既有網站的路徑前綴，或作為獨立子網域根目錄。目前尚未選定正式 URL。

## 驗證

核心、批次與網站契約：

```powershell
node tests/test_core_v0.4.js
python -B tools/empsl_v04_batch_check.py
python -B tests/test_site_content_v0.4.py -v
```

真實 HTTP、互動與下載驗證：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B tests/test_browser_v0.4.py
```

單檔配方驗證仍可使用：

```powershell
python tools/empsl_v04_validate.py examples/EMPSL_legality_examples_v0.4.json
```

## 主要內容

- `index.html`：Axioglyph 內容網站與互動式字形語法實驗室；
- `assets/site.css`、`assets/site.js`：品牌視覺、響應式導覽與漸進增強；
- `assets/app.js`、`assets/empsl_core.js`：實驗室狀態、互動與 EMPSL 核心；
- `rules/`：30 條規則與相容性資料表；
- `spec/`：v0.4 YAML 與 JSON Schema；
- `corpus/`：4,096 筆符合性語料；
- `tools/`：Python 驗證器與批次交叉檢查；
- `tests/`：網站契約、Node 核心與真實 HTTP 瀏覽器測試；
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

這是現代設計的形式符號語言與聲學研究工具，不是歷史以諾語復原，也不是加密系統。合成回歸與批次符合性是工程證據，不等同真人知覺實驗或自然語音結論。
