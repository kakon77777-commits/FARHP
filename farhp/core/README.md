# FARHP-Core v0.3

`FARHP-Core` 是「基頻錨定相對諧波相位差」的軌跡感知研究原型。v0.2 保留 v0.1 的單框架閉環，並加入：

$$
\text{多候選 }f_0
\rightarrow
\text{Viterbi 路徑}
\rightarrow
\text{錨相位傳播}
\rightarrow
\text{FARHP 環面軌跡}
\rightarrow
\text{多框架重建}.
$$

## 研究邊界

這不是完整聲碼器，也不是自然語音品質保證。目前適合：

- 穩定或緩慢變化的有聲訊號；
- 合成母音與研究用 WAV；
- `FARHP-Y` 輸出觀測域；
- 多框架 $f_0$、錨相位與 FARHP 軌跡研究；
- 諧波部分重建與資料交換驗證。

未納入完整非諧波殘差、塞音瞬態、聲門逆濾波、跨無聲間隙的強橋接、神經相位生成與自然語音盲聽驗證。

## 安裝

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

python -m pip install -e .
```

## 靜態閉環示範

```bash
farhp demo --out artifacts/demo
```

## 動態軌跡示範

```bash
farhp demo-track --out artifacts/trajectory_demo
```

輸出：

- `dynamic_synthetic_vowel.wav`
- `farhp_trajectory.json`
- `trajectory_reconstruction.wav`
- `trajectory_inspector.png`
- `trajectory_report.json`

## 分析完整 WAV

```bash
farhp track input.wav \
  --out output/farhp_trajectory.json \
  --plot output/farhp_trajectory.png \
  --f0-min 70 \
  --f0-max 350 \
  --frame-length 0.080 \
  --hop-length 0.010 \
  --k-max 24
```

## 重建軌跡

```bash
farhp reconstruct-track output/farhp_trajectory.json \
  --out output/harmonic_reconstruction.wav
```

## 測試

```bash
python -m unittest discover -s tests -v
```

v0.2 基礎測試加上 v0.3 轉換測試，目前共二十一項：

- 圓周包覆與距離；
- 標量量化誤差界；
- 靜態合成母音基頻；
- 理想時間平移不變性；
- 單框架分析—重建往返；
- 環面碼本；
- FARHP-Spec frame JSON；
- 動態 $f_0$ 追蹤；
- 錨相位局部連續；
- FARHP 軌跡邊界尖峰；
- 軌跡序列化與重建；
- FARHP-Trajectory Schema；
- 無聲間隙偵測與相位軌跡重啟；
- 跨 $\pm\pi$ 的圓周測地插值；
- 零相位與隨機相位條件；
- 相位風格移植端點及半程中點；
- 變換不變量保持；
- 盲聽 manifest 匿名性；
- Transform Schema；
- overlap-add 邊界尖峰防護。

## 核心動態關係

錨相位預測：

$$
\widehat\Phi_{t,1}^{-}
=
\widehat\Phi_{t-1,1}
+
2\pi
\frac{f_0(t-1)+f_0(t)}{2}
\Delta t.
$$

最近分支校正：

$$
\widehat\Phi_{t,1}
=
\widehat\Phi_{t,1}^{-}
+
\operatorname{wrap}
\left(
\widetilde\phi_{t,1}-\widehat\Phi_{t,1}^{-}
\right).
$$

FARHP 軌跡提升：

$$
\widehat\Psi_{t,k}
=
\widehat\Psi_{t-1,k}
+
\operatorname{wrap}
\left(
\widetilde\psi_{t,k}-\widehat\Psi_{t-1,k}
\right).
$$

## 專案結構

```text
src/farhp/
  analyzer.py       單框架 F0 與諧波投影
  tracking.py       多候選 F0、Viterbi、錨相位與 FARHP 軌跡
  model.py          FARHPFrame / FARHPTrajectory
  synth.py          靜態與動態合成母音
  reconstructor.py  單框架與多框架諧波重建
  quantizer.py      圓周標量量化
  codebook.py       加權環面碼本
  schema.py         FARHP-Spec 驗證
  inspector.py      框架與軌跡診斷圖
  io.py             WAV / JSON 讀寫
  cli.py            命令列入口
  transform.py      FARHP-only 條件、測地插值與風格移植
  experiment.py     客觀指標與匿名盲聽包
tests/              單框架與軌跡測試
spec/               FARHP-Spec-v0.1 / Trajectory-v0.2 / Transform-v0.3
```

## 授權與狀態

程式碼採 MIT License；論文與規格仍屬研究草案。自然語音、生理聲門與知覺結論都必須經資料集、客觀指標與盲聽實驗驗證。

---

# v0.3：相位控制、插值與盲聽輸出

v0.3 新增 FARHP-only 轉換層。其設計約束是：在指定對照實驗中保留內容軌跡的 $f_0$、逐諧波振幅、錨相位、時長與有聲狀態，只修改相對諧波相位座標。

## 主要操作

```bash
farhp transform-track input_trajectory.json \
  --mode zero \
  --strength 1.0 \
  --out output_zero.json \
  --wav output_zero.wav

farhp morph-track content.json style.json \
  --strength 0.5 \
  --out output_morph.json \
  --wav output_morph.wav

farhp blind-pack content.json style.json \
  --out artifacts/blind_listening_pack \
  --seed 20260726
```

支援的控制條件：

- `identity`：原 FARHP；
- `zero`：所有有效相對相位歸零；
- `alternating`：確定性的奇偶交替模板；
- `random_static`：每個諧波一個固定隨機相位；
- `random_smooth`：隨時間平滑變動的隨機相位；
- `morph-track`：以環面測地線進行相位風格插值或完整移植。

圓周插值不是普通線性插值，而是：

$$
\operatorname{slerp}_{S^1}(a,b;\lambda)
=
\operatorname{wrap}
\left(
 a+\lambda\operatorname{wrap}(b-a)
\right).
$$

盲聽包會產生公開 manifest、匿名 WAV、評分模板及獨立的秘密條件對照表。它只是實驗工具，不會自動把合成樣本的差異宣稱為人類知覺結論。
