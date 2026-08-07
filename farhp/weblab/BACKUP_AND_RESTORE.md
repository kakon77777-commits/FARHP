# 備份與還原

## SQLite

```bash
python scripts/backup.py --out backups
python scripts/restore.py backups/farhp_sqlite_*.sqlite3 --confirm
```

備份透過 SQLite online backup API 建立，即使來源資料庫正在被讀取也能產生一致副本。還原前會保留 `.pre_restore` 副本，完成後執行 `PRAGMA integrity_check`。

## PostgreSQL

```bash
python scripts/backup.py --out backups
python scripts/restore.py backups/farhp_postgres_*.dump --confirm
```

所需系統指令：`pg_dump`、`pg_restore`。備份使用 custom archive；還原使用 `--clean --if-exists --no-owner`。

## Manifest

每個檔案旁會產生：

```text
<backup>.manifest.json
```

包含後端、建立時間、檔名、大小與 SHA-256。還原前若 manifest 存在，工具會先驗證雜湊。

## 正式營運最低要求

- 排程備份到與主機不同的儲存位置。
- 加密靜態備份。
- 固定執行還原演練，而不只確認備份指令成功。
- 分別記錄資料庫、應用版本與 Alembic revision。
- PostgreSQL 大型部署另行規劃 WAL／PITR；本 RC 未實作持續歸檔。
