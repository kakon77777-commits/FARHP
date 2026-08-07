# Changelog

## 1.0.0-rc.1 — 2026-07-31

### Added

- SQLite／PostgreSQL 雙後端與 SQLAlchemy connection pre-ping。
- Alembic `0001_v09_baseline → 0002_v10rc_production` 遷移鏈。
- v0.9 legacy database adoption script。
- OIDC Authorization Code Flow、JWKS 簽章驗證、issuer／audience／nonce 驗證與角色映射。
- Content Security Policy、HSTS 選項、Trusted Hosts、Permissions Policy、request ID 與 API no-store。
- `/api/health/live` 與 `/api/health/ready`。
- SQLite 與 PostgreSQL 備份／還原指令與 SHA-256 manifest。
- PostgreSQL Docker Compose、Caddy HTTPS overlay、systemd 範例。
- 邀請名額原子扣除，避免併發超發。
- 資料庫化 audit head，為事件鏈更新建立單一頭部狀態。
- OIDC 使用者欄位、token version 與 last-login metadata。

### Changed

- 應用版本更新為 `1.0.0-rc.1`。
- 伺服器封存格式更新為 `1.0-rc.1`。
- 啟動流程先執行 Alembic migration，再啟動 Uvicorn。
- 生產環境拒絕 demo mode、預設秘密與 wildcard host。

### Known limitations

- 建置環境未提供 Docker daemon、PostgreSQL server 或 psycopg runtime，故 PostgreSQL 路徑完成靜態、遷移與命令層驗證，但未在本輪 artifact build 中執行真實 PostgreSQL E2E。
- OIDC 已以本機 RSA/JWKS 模擬完成完整驗證流程；各身份供應商仍需部署端 interoperability test。
- audit head 對 PostgreSQL 使用 row lock；SQLite 適合單節點或低併發，不建議多 worker 寫入部署。
