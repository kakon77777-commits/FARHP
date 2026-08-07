# FARHP / EMPSL 研究工作區

這個目錄已於 2026-08-07 依「當前工作、交接文件、歷史封存」重新整理。FARHP 是相位聲學子系統；EMPSL 是在其上整合穩定身份、字形、華語音系與型別語義的人工符號語言工程。

## 建議入口

1. 先讀 [`handoff/01_FARHP_EMPSL_總索引與當前狀態.md`](handoff/01_FARHP_EMPSL_總索引與當前狀態.md)。
2. FARHP 任務從 [`farhp/README.md`](farhp/README.md) 進入。
3. EMPSL 任務從 [`empsl/README.md`](empsl/README.md) 進入。
4. 歷史 ZIP 與校驗方式見 [`archive/README.md`](archive/README.md)。
5. 本次實際驗證結果見 [`VERIFICATION_REPORT.md`](VERIFICATION_REPORT.md)。

## 當前版本

| 子系統 | 當前節點 | 狀態 |
|---|---|---|
| FARHP 論文 | 01–07 | 已完成；Paper 08 待正式回寫 |
| FARHP-Core | v0.3 | 研究參考實作 |
| FARHP WebLab | v1.0.0-rc.1 | Release Candidate，不是正式 production certification |
| EMPSL | v0.4 | 字形語法與合法性層完成；v0.5 為下一主線 |

## 目錄結構

```text
FARHP/
├── handoff/                 當前狀態、操作協定與 roadmap
├── farhp/
│   ├── papers/              論文 01–07
│   ├── specs/               FARHP 三層交換規格
│   ├── core/                FARHP-Core v0.3 可執行原始碼
│   ├── reports/             基準與驗證報告
│   ├── series/              v0.7 系列索引與原始 layout 校驗檔
│   └── weblab/              WebLab v1.0.0-rc.1 可工作原始碼
├── empsl/
│   └── v0.4/                EMPSL v0.4 完整可工作原始碼與資產
└── archive/                 歷史發行 ZIP、示範包與原始交接包
```

## 工作原則

- `farhp/` 與 `empsl/` 是目前可直接工作的解包版本。
- `archive/` 保留原始檔名與位元內容，作版本追溯，不在其中直接修改。
- 合成回歸與自動測試只代表工程證據，不等同自然語音或真人知覺結論。
- FARHP WebLab 仍是 RC；PostgreSQL 真實 E2E、外部 IdP、公網安全與真人研究都尚未完成。
