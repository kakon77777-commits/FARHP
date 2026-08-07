# 生產部署指南

## 推薦拓撲

```text
Internet
  → TLS termination reverse proxy
  → FARHP container (single process per container)
  → PostgreSQL
  → encrypted backup target
```

## HTTPS

FARHP 本身預期位於 TLS termination proxy 後方。`start.sh` 啟用 Uvicorn proxy headers，但只信任 `FARHP_FORWARDED_ALLOW_IPS`。請勿在不受控網路設定為 `*`；Compose HTTPS overlay 中的 `*` 僅適用於隔離的容器內部網路。

## Workers

- SQLite：使用 `FARHP_WORKERS=1`。
- PostgreSQL：可依 CPU 與負載水平擴展；每個容器通常保持一個 process，再由容器平台擴展。
- 調整 `FARHP_DB_POOL_SIZE` 與 `FARHP_DB_MAX_OVERFLOW`，確保所有 replica 的總連線數不超過 PostgreSQL 限制。

## 安全標頭

預設加入 CSP、X-Content-Type-Options、X-Frame-Options、Referrer-Policy、Permissions-Policy、COOP、CORP、request ID 與 API `Cache-Control: no-store`。HTTPS 請求在 `FARHP_FORCE_HTTPS=1` 時加入 HSTS。

## 上線檢查

- [ ] 關閉 demo mode。
- [ ] 更換兩個彼此獨立的秘密。
- [ ] 限定 allowed hosts 與 proxy IP。
- [ ] 啟用 PostgreSQL 與 Alembic migration。
- [ ] 啟用 HTTPS，確認 callback URL。
- [ ] 驗證備份與還原。
- [ ] 建立監控：live、ready、錯誤率、DB 連線與磁碟。
- [ ] 執行第三方安全測試與組織倫理審查。
