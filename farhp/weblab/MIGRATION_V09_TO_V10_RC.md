# v0.9 → v1.0 RC 遷移

## 1. 停止 v0.9 寫入

先停止服務，並建立 v0.9 資料庫備份。

## 2. 設定相同資料庫 URL

```env
FARHP_DATABASE_URL=sqlite:////absolute/path/farhp_v09.sqlite3
```

或 PostgreSQL URL。

## 3. 採認舊資料庫

```bash
python scripts/adopt_v09.py
```

腳本會：

1. 確認不存在 `alembic_version`；
2. 確認六張 v0.9 核心表；
3. stamp 為 `0001_v09_baseline`；
4. upgrade 到 `0002_v10rc_production`；
5. 回填 audit heads。

## 4. 啟動 RC

```bash
./start.sh
```

## 新增資料

- 工作人員 authentication provider／external subject／email／display name。
- token version 與 last login。
- `audit_heads`。
- `alembic_version`。

v0.8 WebLab plan、checkpoint 與 study payload 仍保留原格式。
