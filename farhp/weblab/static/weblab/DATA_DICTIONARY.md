# FARHP WebLab v0.8 資料字典

## Research Plan

- `farhp_weblab_plan_version`：`0.8`。
- `design`：刺激、FARHP 條件、介入強度、排序與盲化。
- `exclusion_policy`：事前程序品質排除規則。
- `governance.research_role`：計畫建立者角色。
- `governance.consent_template`：同意版本、標題與摘要。
- `plan_fingerprint`：規範化計畫的 64 字元指紋及演算法。

## Consent Record

- `consent_version`、`consent_title`：綁定計畫的同意文件。
- `consented_at`：同意時間。
- `affirmative_consent`、`eligibility_attested`：主動同意與資格確認。
- `withdrawal_code`：撤回查詢用代碼；去識別輸出會移除。
- `plan_fingerprint`：同意所對應的鎖定計畫。

## Audit Event

- `index`：事件順序。
- `type`：事件類型。
- `payload`：最小事件內容。
- `prev_hash`：前一事件雜湊或 `GENESIS`。
- `hash`：本事件雜湊。

## Study

- `governance`：同意紀錄及是否蒐集直接識別資訊。
- `audit_log`：即時事件鏈。
- `audit_validation`：鏈條驗證結果。
- `exclusion_certificate`：試驗及工作階段排除證書。

## Deidentified Study

- `participant_id`：`PID-` 加 20 位單向摘要。
- `session_id`：`SID-` 加 20 位單向摘要。
- `deidentification`：方法、演算法與產生時間。
- 撤回代碼會被移除。

## Group Analysis

- `governance_quality`：同意缺失、事件鏈失敗、計畫問題、不變量失敗與重複工作階段數。
- `by_participant`、`by_stimulus`、`by_condition_and_stimulus`：描述性階層摘要。

## Long-format CSV

每列為一個正式 ABX 試驗，包含 `participant_id`、`stimulus_key`、`condition`、`correct`、`rt_ms`、`included_by_policy` 與 `plan_fingerprint`，供外部 GLMM／GEE 分析。
