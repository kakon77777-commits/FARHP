# 安全與部署邊界

v1.0 RC 改善了部署基礎，但不代表已取得安全認證。

## 已實作

- Argon2 本機密碼雜湊。
- 有時效、可撤銷版本的工作人員權杖。
- OIDC code flow 與 ID Token 驗證。
- 角色型 API authorization。
- Trusted Host、CSP、HSTS 選項及其他安全標頭。
- 計畫／工作階段 SHA-256 事件鏈。
- 原子邀請名額扣除。
- SQLAlchemy 參數化查詢與 DB migration。
- 去識別分析視圖。

## 尚未實作

- 集中式 rate limiter／帳號鎖定。
- OIDC RP-initiated logout 與 back-channel logout。
- KMS／Vault 整合與金鑰輪替工作流。
- WAF、SIEM、集中日誌與異常偵測。
- 檔案惡意內容掃描。
- PostgreSQL row-level security。
- 外部可信時間戳或第三方不可撤回預註冊。

## 重要界線

FARHP 研究資料可能涉及受試者資訊。即使採匿名與去識別設計，部署者仍須依所在地法律、研究倫理、同意內容與資料保留政策處理。RC 不能自行取代 IRB、法律意見或資安審查。
