# FARHP v0.8 分析模型說明

網站內建的 Wilson 區間與二項檢定只提供瀏覽器端描述性摘要。正式分析資料以逐輪長表輸出，每列是一個正式 ABX 試驗。

建議的最小確認性模型為：

$$
\operatorname{logit}\Pr(Y_{ijst}=1)
=
\beta_0+\beta_1 C_{ijst}+u_i+v_j,
$$

其中 $i$ 為受試者、$j$ 為刺激、$C$ 為 FARHP 條件，且

$$
u_i\sim\mathcal N(0,\sigma_u^2),
\qquad
v_j\sim\mathcal N(0,\sigma_v^2).
$$

`farhp_glmm_template_v0.8.R` 使用 `lme4::glmer` 提供交叉隨機截距模板。`farhp_gee_template_v0.8.py` 提供以受試者群聚的 GEE，屬於人口平均模型，不等同於交叉隨機效應模型。

正式研究前仍應預先指定主要對比、排除政策、停止規則、缺失資料處理與多重比較方法。
