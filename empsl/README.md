# EMPSL 當前工作區

**Axioglyph｜理符** 是 EMPSL 的獨立對外網站品牌；EMPSL 保留為技術系統名稱。網站目前直接建立在權威節點 [`v0.4/`](v0.4/) 上，因此介紹內容、互動實驗室、規則與驗證資料使用同一份來源，不另複製研究資料。

v0.4 已包含 128 原子、256 受控種子變體、六槽字形、30 條合法性規則、4,096 筆符合性語料，以及 Node／Python 雙引擎驗證。

## 本機網站

```powershell
cd v0.4
python -B -m http.server 8765 --bind 127.0.0.1
```

開啟 `http://127.0.0.1:8765/`。目前保持相對路徑與部署位置中立，待後續再決定使用子網域或既有網站的單獨分頁。

## 快速驗證

```powershell
cd v0.4
node tests/test_core_v0.4.js
python -B tools/empsl_v04_batch_check.py
python -B tests/test_site_content_v0.4.py -v
```

下一個主線版本是 v0.5：Versioned Lexicon、Typed AST、Type Inference、Compiler 與 Decompiler。Stable ID 不得被 PUA、字形或字型檔取代。
