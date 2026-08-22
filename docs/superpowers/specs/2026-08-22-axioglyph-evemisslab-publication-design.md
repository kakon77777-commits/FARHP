# Axioglyph × EveMissLab 發布整合設計

## 決策

Axioglyph｜理符正式成為 EveMissLab 網站群的獨立姊妹站，公開網址固定為：

```text
https://axioglyph.evemisslab.com/
```

網站使用 Cloudflare Workers Static Assets 的 assets-only Worker。`evemisslab.com` 繼續由現有 Cloudflare Pages 專案 `evemisslab` 提供，不改 DNS 歸屬，也不改成 Worker。

## 角色分工

- `D:\Ai\work together\FARHP`：Axioglyph 原始碼、EMPSL v0.4 引擎、公開資產建置、Worker 設定與子網域發布。
- `D:\Ai\網站群\evemisslab`：EveMissLab 入口索引，新增 Axioglyph 中英文卡片及專屬色票。
- `D:\Ai\網站群\neok-evemisslab-source`：個人／MSSP 網站，本次不修改。

入口站只負責可發現性，不承擔主要流量。Axioglyph 的內容、後續宣傳與直接連結才是主要進站來源。

## Axioglyph 公開包

不得把整個 `empsl/v0.4` 目錄當成公開資產根目錄。建置腳本只複製瀏覽器執行所需檔案：

- `index.html`；
- `assets/site.css`、`assets/site.js`、`assets/app.js`、`assets/empsl_core.js`；
- 六個目前頁面直接載入的 data／rules／examples JavaScript 註冊表；
- 專用 `404.html`、`robots.txt`、`sitemap.xml` 與 `llms.txt`。

測試、Python 工具、語料、規格 Markdown、封存檔與工作文件都不進入公開資產包。公開包輸出至被 Git 忽略的 `site/dist/`。

Worker 設定：

- Worker 名稱：`axioglyph`；
- compatibility date：`2026-08-22`；
- custom domain：`axioglyph.evemisslab.com`；
- HTML handling：`auto-trailing-slash`；
- not-found handling：`404-page`；
- observability：啟用。

## 中文文案原則

保留必要的技術精度，但把介紹文案改成人會自然說出口的中文。

### 避免

- 連續堆疊「可驗證、可稽核、可追溯、權威節點」；
- 用抽象名詞代替動作；
- 每段都先定義、再補邊界、最後列證據；
- 像計畫書或 AI 摘要的對偶句型。

### 採用

- 先說訪客會遇到的問題，再說工具怎麼幫忙；
- 句子短一點，允許「先說清楚」「直接試試看」「故意弄錯」等口語；
- 技術名稱只在真正需要精確的地方出現；
- 邊界直接說，不使用防禦性的文件腔。

首頁主文案改為：

> 畫一個符號不難。難的是說清楚：它怎麼讀、代表什麼，改了一筆之後還是不是同一個東西。Axioglyph 就是拿來做這件事的。

章節標題改採自然語氣，例如：

- `先不講規格。你只要想一件事。`
- `一個字，六個位置。動一個，其他也可能跟著變。`
- `別只看，直接動手改。`
- `不是「我這邊有跑過」就算數。`
- `現在先把字做好；下一步才是把語言跑起來。`

表單欄位、規則名稱、PASS／FAIL、Stable ID、Schema、Typed AST 與 FARHP 等技術詞不做口語化改名。

## EveMissLab 索引更新

Axioglyph 加入 `Working systems／運行中的系統`，成為第 17 個入口。

英文說明：

> A glyph lab where a symbol is more than a picture. Change its form, sound and meaning, then see exactly why the recipe passes or fails.

中文說明：

> 畫一個符號不難；難的是說清楚它怎麼讀、代表什麼，改了一筆之後還是不是同一個東西。你可以直接動手改，故意弄錯，再看它為什麼通過或失敗。

索引色票取自 Axioglyph 的銅色系：light `#8e4d23`，dark `#e8aa6d`，兩者需在入口站背景上保持可讀對比。

## 發布順序

1. 先在 FARHP repo 建置與驗證公開包。
2. 提交並推送 FARHP `main`，確認遠端包含 Axioglyph 來源與發布設定。
3. 部署 assets-only Worker；等待 `https://axioglyph.evemisslab.com/` 回傳新頁面。
4. 驗證首頁、404、必要資產、互動、下載與 cache-busting URL。
5. 在 EveMissLab repo 新增中英文索引卡與色票，建置並確認 17 個站點。
6. 提交並推送 EveMissLab `main`。
7. 部署既有 Pages 專案 `evemisslab`，不建立新 Pages／Sites 專案。
8. 以線上 HTTP、內容文字、連結與站點數驗證兩站，必要時以 cache-busting 重試邊緣傳播。

## 完成條件

- `https://axioglyph.evemisslab.com/` 回傳 HTTP 200，標題與 canonical 正確。
- 不存在的 Axioglyph 路徑回傳 404，而不是首頁 200。
- 線上實驗室能載入錯誤案例、修正、切換 R90，SVG／JSON 下載仍工作。
- Axioglyph 主要中文介紹不再包含 `可稽核`、`目前權威節點`、`形式符號語言工程` 等文件腔。
- `https://evemisslab.com/` 與 `/zh/` 均列出 Axioglyph，總數為 17，連結指向正式子網域。
- 兩個 repo 工作樹乾淨，`main` 與各自 `origin/main` 一致。
