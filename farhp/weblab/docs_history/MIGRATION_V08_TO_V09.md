# 從 WebLab v0.8 遷移到 Server v0.9

1. 在 v0.8 匯出鎖定或草稿研究計畫 JSON。
2. 登入 v0.9 儀表板並匯入。
3. v0.9 一律先建立新的伺服器草稿 revision，不直接信任外部鎖定狀態。
4. 由 principal investigator 在伺服器端重新鎖定；伺服器生成新的 SHA-256 指紋。
5. 建立邀請後，受試者從 `/participant/{code}` 進入。
6. v0.8 WebLab 透過 `server_bridge.js` 自動載入伺服器計畫並同步檢查點。
7. 完成後，原生 v0.8 study JSON 會提交到 v0.9，不需要轉換研究本體。

舊有 v0.8 離線檔案仍可獨立使用；v0.9 並未取消離線模式。
