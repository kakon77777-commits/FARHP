# 歷史封存

本目錄保存原始發行 ZIP、示範包與交接包。檔名及內容保持不變；當前可工作的解包版本位於上層 `farhp/` 與 `empsl/`。

| 目錄 | 內容 |
|---|---|
| `farhp-series/` | FARHP 系列 v0.4–v0.7 |
| `farhp-core/` | FARHP-Core v0.1–v0.2 獨立工程包 |
| `farhp-weblab/releases/` | WebLab MVP v0.1–v0.9 與 v1.0.0-rc.1 |
| `farhp-weblab/demos/` | 各階段研究／部署／協作示範包 |
| `empsl/` | EMPSL v0.1–v0.4 |
| `handoff/` | 原始 Local AI Handoff MD 與 FULL 包 |

全部 ZIP 的重新計算雜湊位於 [`ARCHIVE_SHA256SUMS.txt`](ARCHIVE_SHA256SUMS.txt)。

PowerShell 驗證單一檔案：

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath '<archive.zip>'
```
