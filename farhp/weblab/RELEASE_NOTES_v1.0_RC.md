# FARHP WebLab v1.0.0-rc.1 Release Notes

v1.0 RC 是 FARHP 從研究 MVP 轉向部署候選版的第一個封閉節點。聲學層與研究格式沒有重新發明；本輪集中處理資料庫生命週期、身份、傳輸邊界、備份與併發一致性。

## RC 接受標準

- 全新 SQLite DB 可由 Alembic 建立。
- v0.9 DB 有採認與升級路徑。
- Ready probe 會拒絕落後 migration。
- 邀請名額在併發下不超發。
- OIDC Token 驗證 issuer、audience、nonce 與簽章。
- 備份產生 SHA-256 manifest，SQLite 可完成還原往返。
- UI、API、WebLab 與 v0.8 payload 保持可用。

## 不宣稱

- 未宣稱 PostgreSQL 真實 E2E 已在本建置環境跑完。
- 未宣稱任一 OIDC 供應商已取得正式相容認證。
- 未宣稱系統已通過滲透測試、法規或研究倫理認證。
