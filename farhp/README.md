# FARHP 當前工作區

目前權威節點為 FARHP 系列 v0.7、FARHP-Core v0.3 與 WebLab v1.0.0-rc.1。

| 路徑 | 內容 |
|---|---|
| [`papers/`](papers/) | 論文 01–07；第 08 篇華語複合發音尚待正式回寫 |
| [`specs/`](specs/) | FARHP-Spec v0.1、Trajectory v0.2、Transform v0.3 |
| [`core/`](core/) | Python 研究參考實作、21 項單元／合成回歸測試 |
| [`reports/`](reports/) | FARHP-Core v0.3 基準與驗證報告 |
| [`series/`](series/) | 系列索引、原始 README 與原始目錄版 SHA-256 清單 |
| [`weblab/`](weblab/) | FastAPI／SQLite／PostgreSQL 路徑與研究 WebLab RC |

## Core 快速驗證

```powershell
cd core
$env:PYTHONPATH = (Resolve-Path .\src).Path
python -m unittest discover -s tests -v
```

## 研究邊界

FARHP 是 phase subsystem，不是完整 TTS、自然語音品質保證或人類知覺證明。當前最重要的 FARHP 後續工作是 Paper 08 正式回寫、真實母音 pilot、FARHP-Y／G 比較與小型真人 ABX pilot。
