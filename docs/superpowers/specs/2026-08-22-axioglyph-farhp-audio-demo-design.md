# Axioglyph FARHP 聲音示範設計

## 1. 根因與範圍

FARHP 聲音合成沒有從專案消失。封存的 WebLab MVP v0.1–v0.9 與現行 v1.0.0-rc.1 都包含 Web Audio 合成；現行 `farhp/weblab/static/weblab/app.js` 仍有單框架、華語音節、語流、ABX 與 WAV 產生能力。

缺口發生在 Axioglyph：`empsl/v0.4` 只整合字形配方與合法性規則，公開包沒有任何 FARHP 音訊模組或播放控制。因此本版不是修復一顆壞掉的按鈕，而是把既有研究合成路徑以受限、可測試的方式接入 Axioglyph。

本版只完成互動聲音示範；更進階的真人語音、自然度、神經聲碼器、說話者建模與 FARHP-G 反演留待後續版本。

## 2. 使用者能力

在 Axioglyph 實驗室新增「讓這個符號發出聲音」區塊，提供：

- 播放目前合法配方；
- 停止播放；
- 匯出目前合成 WAV；
- 中性聲、男聲、女聲三種合成聲線；
- 一鍵自動示範；
- 一鍵隨機示範；
- 重播上一個隨機結果；
- 顯示讀法、聲線、PH16、聲學來源與隨機 seed；
- 顯示簡化波形與清楚的播放／拒絕原因。

瀏覽器不得在頁面載入時自行播放。自動示範仍要由使用者按一次按鈕開始，之後才能在同一個已解鎖的 AudioContext 內連續播放。

## 3. 模組邊界

新增 `empsl/v0.4/assets/farhp_audio.js`，採 UMD 形式，同時支援瀏覽器 `window.FARHPAudio` 與 Node `require()`。

模組負責純聲學計畫與波形，不讀寫 Axioglyph DOM：

```javascript
FARHPAudio.voiceProfiles
FARHPAudio.phaseSignatureVector(phaseId, harmonicCount)
FARHPAudio.recipeToPlan(recipe, voiceKey)
FARHPAudio.synthesize(recipe, options)
FARHPAudio.encodeWav(samples, sampleRate)
FARHPAudio.seededRandom(seed)
FARHPAudio.createPlayer()
```

`assets/app.js` 負責 DOM、目前配方、自動／隨機流程、按鈕狀態、波形圖與下載。

現行 WebLab 本版不重構。新模組的公式與映射需註明來源為 WebLab v0.8 相容的瀏覽器合成路徑，並以數值測試鎖定，不直接複製研究治理、ABX 或多人語料功能。

## 4. 配方到聲音的映射

### 4.1 音系

- `ONSET-*` 映射到現行 WebLab 的零聲母、塞音、送氣塞音、鼻音、擦音、塞擦音、邊音與近音模型。
- `HU-KAIKOU` 不加介音。
- `HU-QICHI` 使用 `/i/` 介音。
- `HU-HEKOU` 使用 `/u/` 介音。
- `HU-CUOKOU` 使用 `/y/` 介音。
- `RIME-A/O/E/AI/EI/AO/OU/AN/EN/ANG/ENG/ER` 映射到 WebLab 已有母音路徑與 `/n/`、`/ŋ/`、兒化尾模型。
- `T1/T2/T3/T4/T0` 使用現行 WebLab 連續 `f0(t)` 聲調輪廓。

音訊從結構欄位推導；`reading` 只用來顯示，不反向解析成音節。

### 4.2 PH16

`PH16-00…15` 是 Level P1 可視簽名，不是完整 FARHP 向量。每個簽名只表示主相位角落在 16 個圓周區間之一。

本版為每個 PH16 建立固定、可重現的代表向量：

1. 取該區間中心角；
2. 基頻相位固定為 0；
3. 其餘諧波以中心角加上一個零圓周平均的小幅正弦展開；
4. 驗證代表向量的 circular mean 仍量化回原 PH16。

介面固定顯示「PH16 代表性合成」，不得稱為唯一發音或完整碼本重建。

### 4.3 FARHP domain

- `FARHP-Y`：可使用輸出域代表性合成。
- `FARHP-G`：若配方沒有逆濾波方法與完整向量，拒絕播放並說明缺少反演資料。
- `NONE`、`silent`、`ST-BOUNDARY`：不產生假聲音，顯示靜音／邊界原因。
- FAIL 配方：先修正到 PASS 才能播放。

## 5. 合成聲線

三種聲線都是人工參數預設，不是對生理性別、性別認同或真人聲音的分類：

| key | 顯示名稱 | 中值基頻 | 共振峰縮放 | 頻譜傾斜 |
|---|---|---:|---:|---:|
| `neutral` | 中性聲 | 132 Hz | 1.00 | 0.86 |
| `male` | 男聲（低域合成） | 108 Hz | 0.90 | 0.82 |
| `female` | 女聲（高域合成） | 205 Hz | 1.10 | 0.94 |

聲線選擇會同時改變 `f0`、共振峰中心與諧波衰減，不做單純 pitch shift。介面旁固定標示「合成聲線，不代表生理分類」。

## 6. 音訊產生

- sample rate：24,000 Hz；
- 單音節預設長度：0.72 秒，輕聲縮短；
- 諧波上限：24，並受 Nyquist 限制；
- 波形包含連續聲調、母音共振包絡、代表性 PH16、聲母瞬態與鼻／兒化尾殘差；
- 每個輸出用 15 ms fade-in／fade-out；
- peak 正規化到不高於 0.72；
- 殘差噪聲由 recipe ID、phase、voice 與 seed 決定，確保相同輸入逐樣本重現。

輸出 metadata 至少包括：

```text
voice_key
voice_label
base_f0_hz
f0_min_hz
f0_max_hz
formant_scale
phase_signature
phase_center_rad
representative_phase=true
domain=FARHP-Y
sample_rate_hz
duration_sec
seed
```

## 7. 示範流程

### 7.1 自動示範

使用者按下後：

1. 保存目前配方與聲線；
2. 若目前配方不可播放，選擇第一份合法、非靜音、FARHP-Y 範例；
3. 依序播放同一音節的中性聲、男聲、女聲；
4. 三步使用 `PH16-current`、`PH16-current+5`、`PH16-current+10`，並同步更新畫面；
5. 每步結束後間隔 180 ms；
6. 完成或停止後還原原始配方與聲線；
7. 任何新播放、隨機示範或停止動作都能立即取消舊序列。

### 7.2 隨機示範

1. 以 `crypto.getRandomValues()` 取得 32-bit seed；若不可用則以時間建立 seed；
2. seeded PRNG 從合法、非靜音、FARHP-Y 範例選一份；
3. 隨機選三種聲線之一與 16 種 PH16 之一；
4. 同步更新 `phase` 與 `acoustic.phase_signature`，重新驗證並更新畫面；
5. 播放一次並顯示 seed；
6. 「重播這次隨機」以同一 seed 重建相同配方、聲線與逐樣本相同波形。

## 8. 介面與可及性

- 聲音區置於 Lab 主工作區之後、研究證據之前。
- 聲線使用三個 `aria-pressed` 按鈕，不只用顏色表示選取。
- `soundStatus` 使用 `role=status` 與 `aria-live=polite`。
- 播放、自動示範與隨機示範期間，對應按鈕顯示明確狀態；停止永遠可用。
- 波形 canvas 有文字替代說明；關閉 JavaScript 時仍可讀到限制說明。
- `prefers-reduced-motion` 不影響聲音，但停用非必要視覺動畫。

## 9. 測試與發布

### 純模組

- PH16 向量量化回原簽名；
- 三聲線的 `f0`、formant scale 與波形確實不同；
- 同 recipe／voice／seed 逐樣本一致；
- 改 PH16 會改波形，但不改聲線 `f0`、時長與諧波振幅模型；
- 所有樣本 finite、peak ≤ 0.72；
- silent、NONE、FARHP-G 與 FAIL 正確拒絕；
- WAV header、sample rate 與資料長度正確。

### 真實瀏覽器

- 播放目前聲音可建立／恢復 AudioContext；
- 聲線按鈕更新 metadata；
- 自動示範可完成與停止；
- 隨機示範產生 seed，重播保留 seed；
- WAV 下載事件可觀察；
- 原有案例、修正、R90、SVG／JSON 匯出不回歸；
- console errors 為 0。

公開包新增 `assets/farhp_audio.js`。測試通過後更新 cache-busting query、提交、推送、部署既有 `axioglyph` Worker，最後以線上瀏覽器實際操作。
