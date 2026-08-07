# FARHP WebLab v1.0.0-rc.1

FARHP WebLab v1.0 RC 將 v0.9 的多人研究協作 MVP 推進到可部署候選版本。聲學合成、華語語流、ABX、研究治理與 v0.8 WebLab 格式保持相容；伺服器層新增 PostgreSQL、Alembic、OIDC、安全標頭、備份還原與健康檢查。

## 快速啟動：SQLite

```bash
python -m pip install -r requirements.txt
cp .env.example .env
# 開發環境可使用預設 SQLite；正式環境必須更換兩個秘密值。
./start.sh
```

開啟：

- 工作台：`http://127.0.0.1:8000/`
- 互動 API：`http://127.0.0.1:8000/docs`
- WebLab：`http://127.0.0.1:8000/weblab/`
- Ready probe：`http://127.0.0.1:8000/api/health/ready`

## PostgreSQL 容器部署

```bash
export POSTGRES_PASSWORD='replace-me'
export FARHP_SECRET_KEY='at-least-32-random-characters'
export FARHP_DEIDENTIFICATION_SALT='a-second-independent-random-secret'
docker compose up --build
```

HTTPS 反向代理範例：

```bash
export FARHP_DOMAIN='farhp.example.org'
docker compose -f docker-compose.yml -f docker-compose.https.yml up --build
```

## 資料庫遷移

```bash
python scripts/migrate.py
alembic current
alembic history
```

既有 v0.9 `create_all` 資料庫：

```bash
python scripts/adopt_v09.py
```

請先備份。此腳本只接受可辨識的 v0.9 六張核心表，先將資料庫標記為 `0001_v09_baseline`，再執行 RC 遷移。

## OIDC

設定 `FARHP_OIDC_ENABLED=1` 後，工作台顯示機構登入按鈕。實作採 Authorization Code Flow，回呼會驗證：

- discovery issuer；
- ID Token 簽章；
- `iss`、`aud`、`exp`、`iat`、`sub`；
- 登入請求 nonce；
- 角色 claim 映射。

OIDC 設定詳見 [OIDC_CONFIGURATION.md](OIDC_CONFIGURATION.md)。

## 備份與還原

```bash
python scripts/backup.py --out backups
python scripts/restore.py backups/<file> --confirm
```

- SQLite 使用 Python `sqlite3.Connection.backup()` 建立一致性副本。
- PostgreSQL 使用 `pg_dump --format=custom` 與 `pg_restore`。
- 每份備份附帶 SHA-256 manifest。

詳見 [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md)。

## 版本邊界

這是 **Release Candidate**，不是安全認證、臨床系統、IRB 核准平台或不可撤回的第三方預註冊服務。實際公開部署仍需：秘密管理、網域與 TLS、郵件／身份供應商設定、監控、外部滲透測試、資料保留政策及組織倫理流程。
