# FARHP / EMPSL 整理驗證報告

- **日期：** 2026-08-07
- **環境：** Windows／PowerShell，Python 3.14.5，Node.js 24.16.0

## 通過項目

| 區域 | 驗證 | 結果 |
|---|---|---:|
| FARHP 系列 v0.7 | 原始 `SHA256SUMS.txt` | 114／114 |
| FARHP 系列 v0.4 | 原始 SHA-256 清單 | 8／8 |
| FARHP-Core v0.3 | `unittest` | 21／21 |
| WebLab v1.0.0-rc.1 | 原始 `SHA256SUMS.txt` | 220／220 |
| WebLab v1.0.0-rc.1 | Windows pytest，啟用 UTF-8 | 21 passed／1 platform-specific failure |
| EMPSL v0.4 | 原始 `SHA256SUMS.txt` | 1102／1102 |
| EMPSL v0.4 | Node 核心規則 | 30 groups PASS |
| EMPSL v0.4 | Python corpus 交叉驗證 | 4096 cases PASS |

## 已知來源問題

1. WebLab 的 `tests/test_browser.py` 把 Chromium 固定為 Linux 路徑 `/usr/bin/chromium`。因此本次 Windows 重跑為 21 passed、1 failed；原發行報告是在 Linux／Chromium 環境得到 22 passed。這是測試可攜性問題，不是此次整理造成的產品邏輯失敗。
2. WebLab 兩個 API 測試在 Windows 預設 CP950 下會讀取 UTF-8 JSON 失敗；設定 `PYTHONUTF8=1` 後通過。原始碼未在本次目錄整理中修改。
3. 兩份 Handoff v1.0 ZIP 內的 `README.md` 實際 SHA-256 為 `bbcefb4164cdb4bfa747ef8d199c94320f0b88d7976c87740c74e9067ae79e44`，但包內 `HANDOFF_SHA256_*.txt` 記載舊值 `3db321fc...`。其餘 FULL manifest 10 筆均通過，且兩個交接包中的 README 位元一致。
4. EMPSL v0.4 ZIP 未標示 UTF-8 filename flag；一般 Windows 解包器可能產生亂碼檔名。本工作區已以 UTF-8 metadata override 解包，並由 1102／1102 雜湊確認內容與正確檔名。

## 整理結果

- 當前工作內容與歷史 ZIP 已完全分離。
- 原始歷史 ZIP 均保留，另建立整體 archive SHA-256 清單。
- 根目錄原有的 Paper 06 單獨檔已確認與 `farhp/papers/` 版本完全相同後移除；內容仍保留於當前論文與歷史發行包。
- 暫存虛擬環境、錯誤編碼解包副本與測試 cache 不屬於交付內容，已排除於最終工作區。
