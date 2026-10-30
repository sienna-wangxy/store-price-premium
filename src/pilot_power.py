"""
pilot_power.py
Use the pilot data to estimate the price premium, then do a power analysis
to find how many products we need.

Run from the project folder (after clean_data.py):
    python src/pilot_power.py

Input:  data/clean/prices_long.csv
Output: outputs/pilot_premiums.csv
        outputs/power_table.csv
"""

import numpy as np
import pandas as pd
from statsmodels.stats.power import TTestPower, TTestIndPower

data = pd.read_csv("data/clean/prices_long.csv")

# Use only exact matches that have a price
data = data[(data["found"]) & (~data["substitute"])].copy()
data["log_price"] = np.log(data["regular_price"])


# ---------------------------------------------------------------
# 1. Premium for each product
#    premium = average log price at store type X - average log price at chain
#    exp(premium) - 1 = "X is ...% more expensive than chain"
# ---------------------------------------------------------------
def premium_per_item(data, store_type):
    results = []
    for item, group in data.groupby("item"):
        chain = group[group["store_type"] == "chain"]["log_price"]
        other = group[group["store_type"] == store_type]["log_price"]
        if len(chain) > 0 and len(other) > 0:      # need both to compare
            diff = other.mean() - chain.mean()
            results.append({
                "comparison": store_type + " vs chain",
                "item": item,
                "category": group["category"].iloc[0],
                "log_premium": diff,
                "premium_pct": (np.exp(diff) - 1) * 100,
            })
    return pd.DataFrame(results)


premiums = pd.concat([
    premium_per_item(data, "small store"),
    premium_per_item(data, "co-op"),
])
premiums.to_csv("outputs/pilot_premiums.csv", index=False)

print("=== Premium of each product (pilot data) ===")
print(premiums.round(2).to_string(index=False))
print()


# ---------------------------------------------------------------
# 2. Effect size from the pilot
#    Paired design: each product is compared with itself at a chain store.
#    Cohen's dz = mean of differences / SD of differences
# ---------------------------------------------------------------
paired_power = TTestPower()        # for paired t-test
ind_power = TTestIndPower()        # for comparing two categories
power_rows = []

for comparison, group in premiums.groupby("comparison"):
    d = group["log_premium"]
    dz = d.mean() / d.std()
    print(f"=== {comparison} ===")
    print(f"  products in pilot: {len(d)}")
    print(f"  average premium:   {(np.exp(d.mean()) - 1) * 100:.1f}%")
    print(f"  effect size dz:    {dz:.2f}")

    # Pilot effect sizes from tiny samples are too optimistic,
    # so we also try smaller, more careful effect sizes.
    for label, es in [("pilot dz", dz), ("half of pilot", dz / 2),
                      ("medium (0.5)", 0.5), ("small (0.3)", 0.3)]:
        n = paired_power.solve_power(effect_size=abs(es), alpha=0.05,
                                     power=0.80, alternative="two-sided")
        power_rows.append({
            "question": comparison + " (paired t-test)",
            "assumed effect": label,
            "effect size": round(abs(es), 2),
            "products needed": int(np.ceil(n)),
        })
    print()


# ---------------------------------------------------------------
# 3. Interaction: is the small-store premium different for beer vs snacks?
#    Compare the premiums of beer products and snack products
#    (two different groups of products -> independent t-test)
# ---------------------------------------------------------------
small = premiums[premiums["comparison"] == "small store vs chain"]
beer = small[small["category"] == "beer"]["log_premium"]
snack = small[small["category"] == "snack bar"]["log_premium"]

print("=== Beer vs snack bar (small store premium) ===")
print(f"  beer:  n={len(beer)}, average premium {(np.exp(beer.mean()) - 1) * 100:.1f}%")
print(f"  snack: n={len(snack)}, average premium {(np.exp(snack.mean()) - 1) * 100:.1f}%")

if len(beer) >= 2 and len(snack) >= 2:
    pooled_sd = np.sqrt((beer.var() + snack.var()) / 2)
    d_inter = (beer.mean() - snack.mean()) / pooled_sd
    print(f"  effect size d:  {d_inter:.2f}")
    for label, es in [("pilot d", d_inter), ("half of pilot", d_inter / 2),
                      ("large (0.8)", 0.8), ("medium (0.5)", 0.5)]:
        n = ind_power.solve_power(effect_size=abs(es), alpha=0.05,
                                  power=0.80, alternative="two-sided")
        power_rows.append({
            "question": "beer vs snack premium (interaction)",
            "assumed effect": label,
            "effect size": round(abs(es), 2),
            "products needed": str(int(np.ceil(n))) + " per category",
        })
print()

power_table = pd.DataFrame(power_rows)
power_table.to_csv("outputs/power_table.csv", index=False)
print("=== Power analysis (alpha = 0.05, power = 0.80) ===")
print(power_table.to_string(index=False))
