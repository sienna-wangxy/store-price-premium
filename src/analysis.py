"""
analysis.py
Compare each store's prices with the online control price.

For each store:
    premium = log(store price / online control price)
    H0: mean premium = 0  (store price = online price on average)
    HA: mean premium != 0
Test: one-sample t-test, then Holm correction because we test several stores.

Run from the project folder (after clean_data.py):
    python src/analysis.py

Input:  data/clean/prices_long.csv
Output: outputs/store_vs_online.csv
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

MIN_PRODUCTS = 5     # stores with fewer products are not tested (Gazelle)

data = pd.read_csv("data/clean/prices_long.csv")

# Keep exact matches that have a store price AND an online control price
data = data[data["found"] & ~data["substitute"] & data["has_control"]].copy()

# Log premium for each product at each store
data["log_premium"] = np.log(data["regular_price"] / data["control_price"])

# ---------------------------------------------------------------
# 1. One t-test per store
# ---------------------------------------------------------------
results = []
for store, group in data.groupby("store"):
    x = group["log_premium"]
    n = len(x)
    mean = x.mean()
    sd = x.std()

    row = {
        "store": store,
        "store_type": group["store_type"].iloc[0],
        "n_products": n,
        "mean_premium_pct": (np.exp(mean) - 1) * 100,
    }

    if n >= MIN_PRODUCTS:
        t, p = stats.ttest_1samp(x, 0)
        # 95% confidence interval of the mean (log scale), then turn into %
        margin = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
        row["ci_low_pct"] = (np.exp(mean - margin) - 1) * 100
        row["ci_high_pct"] = (np.exp(mean + margin) - 1) * 100
        row["effect_size_dz"] = mean / sd
        row["t"] = t
        row["p_value"] = p
    results.append(row)

results = pd.DataFrame(results)

# ---------------------------------------------------------------
# 2. Holm correction (only for the stores that were tested)
# ---------------------------------------------------------------
tested = results["p_value"].notna()
reject, p_holm, _, _ = multipletests(results.loc[tested, "p_value"], alpha=0.05, method="holm")
results.loc[tested, "p_holm"] = p_holm
results.loc[tested, "significant"] = reject

results = results.round(3)
print("=== Each store vs online price (regular shelf price) ===")
print(results.to_string(index=False))
print()
print("Stores with fewer than", MIN_PRODUCTS, "products are only described, not tested.")

results.to_csv("outputs/store_vs_online.csv", index=False)
print("Saved outputs/store_vs_online.csv")
