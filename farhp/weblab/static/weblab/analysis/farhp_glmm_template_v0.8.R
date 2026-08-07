# FARHP WebLab v0.8 logistic mixed-effects template
# Install once: install.packages(c("readr", "lme4", "broom.mixed"))
library(readr)
library(lme4)
library(broom.mixed)

d <- read_csv("farhp_analysis_long_v0.8.csv", show_col_types = FALSE)
d <- subset(d, included_by_policy == TRUE)
d$participant_id <- factor(d$participant_id)
d$stimulus_key <- factor(d$stimulus_key)
d$condition <- factor(d$condition)

# Minimal crossed-random-intercept model.
# Expand only according to a preregistered analysis plan and supported sample size.
model <- glmer(
  correct ~ condition + (1 | participant_id) + (1 | stimulus_key),
  data = d,
  family = binomial,
  control = glmerControl(optimizer = "bobyqa")
)

print(summary(model))
write.csv(
  tidy(model, effects = "fixed", conf.int = TRUE),
  "farhp_glmm_fixed_effects.csv",
  row.names = FALSE
)
