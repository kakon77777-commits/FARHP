# OIDC 設定指南

## 必填環境變數

```env
FARHP_OIDC_ENABLED=1
FARHP_OIDC_ISSUER=https://id.example.org/realms/research
FARHP_OIDC_CLIENT_ID=farhp
FARHP_OIDC_CLIENT_SECRET=...
FARHP_OIDC_REDIRECT_URI=https://farhp.example.org/api/auth/oidc/callback
```

Identity Provider 必須允許上述 redirect URI。

## 角色映射

```env
FARHP_OIDC_ROLE_CLAIM=groups
FARHP_OIDC_DEFAULT_ROLE=analyst
FARHP_OIDC_ROLE_MAP={"farhp-pi":"principal_investigator","farhp-collector":"data_collector","farhp-analyst":"analyst"}
```

允許角色只有：

- `principal_investigator`
- `data_collector`
- `analyst`

## 驗證流程

1. 從 `/.well-known/openid-configuration` 取得 discovery document。
2. 要求 discovery `issuer` 與設定值完全一致。
3. 產生簽章 state 與隨機 nonce。
4. 以 authorization code 交換 token。
5. 依 `kid` 從 JWKS 選取公鑰。
6. 驗證簽章、演算法、issuer、audience、時效與必要 claims。
7. 驗證 nonce。
8. 以 `(issuer, sub)` 綁定本地工作人員帳號。

## 建議

- 正式環境關閉 demo mode。
- 可保留一個受保護的本機 break-glass PI 帳號；或在驗證完成後設定 `FARHP_LOCAL_AUTH_ENABLED=0`。
- 身份供應商 group／role 變更會在下次登入同步到本地角色。
- 上線前以實際 IdP 測試 key rotation、logout、停用帳號與 clock skew。
