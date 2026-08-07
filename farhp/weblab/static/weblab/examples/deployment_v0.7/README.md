# FARHP v0.7 研究部署示範資料

本資料夾為自動化測試產生的匿名模擬資料，不是人類知覺研究結果。

## 檔案

- `plan.json`：已鎖定研究計畫與指紋；
- `checkpoint.json`：不含音訊陣列的工作階段檢查點；
- `study.json`：單一匿名受試者研究輸出；
- `study_trials.csv`：單人逐輪表格；
- `group.json`：兩個納入工作階段與一個排除工作階段的群體分析；
- `group_hierarchy.csv`：受試者／刺激兩層描述摘要。

測試沙盒不提供 Web Crypto，因此範例計畫指紋標示為 `FNV32x8-fallback`。在支援 Web Crypto 的安全來源或本機 HTTP 服務中，網站會優先使用 SHA-256。
