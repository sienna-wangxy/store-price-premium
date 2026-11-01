"""
anova.py
Do the stores differ from EACH OTHER in how much they charge above the online price?

Two-way ANOVA:  log_premium ~ store + item
    - "item" is in the model so that differences between products
      (e.g. beer vs snack bar) are removed before comparing stores.
    H0: all stores have the same mean premium
    HA: at least one store is different

Post hoc: paired t-tests between every two stores (using only the products
both stores have), with Holm correction.

Run from the project folder (after clean_data.py):
    python src/anova.py

Input:  data/clean/prices_long.csv
Output: outputs/anova_table.csv
        outputs/anova_posthoc.csv
"""

from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multitest import multipletests

MIN_PRODUCTS = 5        # stores with fewer products are left out (Gazelle)
MIN_SHARED = 3          # need at least 3 shared products for a pair test

data = pd.read_csv("data/clean/prices_long.csv")

# Keep exact matches that have a store price AND an online control price
data = data[data["found"] & ~data["substitute"] & data["has_control"]].copy()
data["log_premium"] = np.log(data["regular_price"] / data["control_price"])

# Leave out stores with too few products
counts = data.groupby("store")["item"].nunique()
keep = counts[counts >= MIN_PRODUCTS].index
print("Products per store:")
print(counts.to_string())
print("Stores used:", list(keep))
print()
data = data[data["store"].isin(keep)]

# ---------------------------------------------------------------
# 1. Two-way ANOVA
# ---------------------------------------------------------------
model = smf.ols("log_premium ~ C(store) + C(item)", data=data).fit()
anova_table = anova_lm(model, typ=2)

# Effect size for store: partial eta squared
ss_store = anova_table.loc["C(store)", "sum_sq"]
ss_resid = anova_table.loc["Residual", "sum_sq"]
anova_table["partial_eta_sq"] = np.nan
anova_table.loc["C(store)", "partial_eta_sq"] = ss_store / (ss_store + ss_resid)

print("=== Two-way ANOVA (store + item) ===")
print(anova_table.round(4).to_string())
print()

# ---------------------------------------------------------------
# 2. Check assumptions
# ---------------------------------------------------------------
# Normality of residuals (Shapiro-Wilk): p > 0.05 means no evidence against normal
w, p_normal = stats.shapiro(model.resid)
print(f"Shapiro-Wilk test on residuals: W = {w:.3f}, p = {p_normal:.3f}")

# Equal variance across stores (Levene): p > 0.05 means no evidence of unequal variance
groups = [model.resid[data["store"] == s] for s in keep]
lev, p_levene = stats.levene(*groups)
print(f"Levene test (equal variance):    W = {lev:.3f}, p = {p_levene:.3f}")
print()

# ---------------------------------------------------------------
# 3. Post hoc: paired t-test for every pair of stores
# ---------------------------------------------------------------
wide = data.pivot_table(index="item", columns="store", values="log_premium")

pairs = []
for a, b in combinations(keep, 2):
    both = wide[[a, b]].dropna()            # products both stores have
    n = len(both)
    row = {"store_A": a, "store_B": b, "shared_products": n}
    if n >= MIN_SHARED:
        diff = both[a] - both[b]
        t, p = stats.ttest_rel(both[a], both[b])
        # exp(mean diff) - 1 = "A is ...% more expensive than B"
        row["A_vs_B_pct"] = (np.exp(diff.mean()) - 1) * 100
        row["t"] = t
        row["p_value"] = p
    pairs.append(row)

posthoc = pd.DataFrame(pairs)
tested = posthoc["p_value"].notna()
reject, p_holm, _, _ = multipletests(posthoc.loc[tested, "p_value"], alpha=0.05, method="holm")
posthoc.loc[tested, "p_holm"] = p_holm
posthoc.loc[tested, "significant"] = reject
posthoc = posthoc.round(3)

print("=== Post hoc: paired t-tests between stores (Holm corrected) ===")
print(posthoc.to_string(index=False))
print()
print("Pairs with fewer than", MIN_SHARED, "shared products are not tested.")

anova_table.round(4).to_csv("outputs/anova_table.csv")
posthoc.to_csv("outputs/anova_posthoc.csv", index=False)
print("Saved outputs/anova_table.csv and outputs/anova_posthoc.csv")
