# FARHP WebLab v1.0.0-rc.1 測試報告

測試日期：2026-07-31

## 自動回歸

```text
22 passed in 8.42s
```

覆蓋：

- v0.9 既有 API 與角色權限；
- Alembic 全新資料庫升級；
- readiness migration head；
- CSP 與安全標頭；
- 12 個併發請求競爭 5 次邀請名額；
- SQLite 備份／修改／還原往返；
- PostgreSQL pg_dump／pg_restore dry-run 命令；
- OIDC RSA／JWKS、issuer、audience、nonce、角色映射；
- Chromium 工作台互動。

## 實際 Uvicorn smoke

實際以獨立 SQLite DB 啟動 Uvicorn，取得：

```json
{
  "status": "ready",
  "version": "1.0.0-rc.1",
  "database": "sqlite",
  "migrations": {
    "current": "0002_v10rc_production",
    "head": "0002_v10rc_production",
    "up_to_date": true
  },
  "users": 3
}
```

並驗證 CSP、X-Content-Type-Options、X-Frame-Options、request ID 與 no-store。

## v0.9 legacy adoption

建立 v0.9 baseline DB、移除 Alembic metadata 後執行 `scripts/adopt_v09.py`，成功 stamp baseline 並升級至：

```text
0002_v10rc_production
```

## 靜態與交換格式

- Python compileall：PASS
- JavaScript syntax：PASS
- Compose YAML：2／2 PASS
- Deployment manifest Schema：PASS
- OpenAPI：24 paths
- Chromium console errors：0

## 已知未完成驗證

本 artifact build 環境沒有 Docker daemon、PostgreSQL server 或 psycopg runtime，因此：

- PostgreSQL schema 由 Alembic／SQLAlchemy 跨後端設計與 dry-run command 驗證；
- Docker／Caddy 檔案通過 YAML 與靜態檢查；
- 沒有宣稱已完成真正 PostgreSQL Container E2E。

OIDC 使用本機產生的 RSA key、JWKS 與模擬 discovery／token endpoint 驗證完整流程；外部 IdP 仍須部署端測試。
