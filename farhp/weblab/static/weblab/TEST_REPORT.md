# FARHP WebLab MVP v0.8 測試報告

測試日期：2026-07-31

## 結果摘要

| 測試 | 結果 |
|---|---:|
| JavaScript 語法 | PASS |
| Node 數值／治理回歸 | 42 組 PASS |
| Node WebCrypto SHA-256 | PASS |
| Chromium 端到端 | PASS |
| 瀏覽器控制台錯誤 | 0 |
| JSON Schema 範例 | 10 份 PASS |

## Chromium 實測流程

1. 驗證 22 個聲母、37 個韻母與原有 FARHP 時間平移測試。
2. 建立兩刺激研究，固定排除政策與同意版本。
3. 鎖定研究計畫並產生 64 字元指紋。
4. 確認未完成電子同意時無法建立研究。
5. 完成資格確認、電子同意與撤回代碼後建立研究。
6. 完成一輪練習、兩輪正式 ABX 與休息節點。
7. 保存不含音訊陣列的檢查點並恢復工作階段。
8. 驗證同意紀錄、八筆事件鏈及工作階段完成事件。
9. 建立兩個納入與一個過快反應排除的模擬工作階段。
10. 產生群體統計、治理品質、去識別研究檔及事件封存證書。

## 主要數值

| 指標 | 結果 |
|---|---:|
| 計畫／檢查點／研究／群體版本 | `0.8` |
| 計畫指紋長度 | 64 |
| 檢查點大小 | 4,488 bytes |
| 檢查點含音訊陣列 | 否 |
| 恢復後已答正式輪 | 1 |
| 事件數 | 8 |
| 即時事件鏈 | PASS |
| 電子同意紀錄 | PASS |
| 群體納入受試者 | 2 |
| 排除工作階段 | 1 |
| 有效正式輪 | 4 |
| 模擬正確率 | 75% |

模擬正確率只用來驗證程式邏輯，不是人類知覺證據。

## 篡改測試

自動測試建立三筆事件鏈，修改第二筆事件內容後，`verifyLiveAuditChain` 返回失敗。未修改鏈返回 PASS。

## 去識別測試

原始 `participant_id` 與 `session_id` 會轉換為：

```text
PID-<20 hex>
SID-<20 hex>
```

去識別研究檔會移除撤回代碼，並保留計畫指紋、同意版本、試驗資料與排除證書。

## WebCrypto

Node WebCrypto 測試確認：

- 計畫指紋使用 SHA-256；
- 摘要長度為 64 位十六進位；
- 研究專用受試者假名格式正確。

`set_content` Chromium 測試因無持久安全來源，計畫指紋會使用清楚標記的 `FNV32x8-fallback`；在 localhost／HTTPS 的一般瀏覽器環境中使用 Web Crypto SHA-256。

## Schema

通過驗證的 v0.8 物件：

- Research Plan
- Session Checkpoint
- Multi-Stimulus Study
- Deidentified Study
- Audit Archive
- Group Analysis

另保留四份 v0.6 模擬研究／群體範例的相容性驗證，共 10 份 JSON。
