"""FARHP WebLab v0.8 population-average analysis template.

Install: pip install pandas statsmodels
For confirmatory crossed participant/stimulus random effects, use the R/lme4
script or a preregistered Bayesian model reviewed by a statistician.
"""
from pathlib import Path
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

DATA = Path("farhp_analysis_long_v0.8.csv")
df = pd.read_csv(DATA)
df = df[df["included_by_policy"].astype(str).str.lower().isin(["true", "1"])]

model = smf.gee(
    "correct ~ C(condition)",
    groups="participant_id",
    data=df,
    family=sm.families.Binomial(),
).fit()

print(model.summary())
model.summary2().tables[1].to_csv("farhp_gee_results.csv")
