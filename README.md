# Store Price Premium: Durham Stores vs. Online Prices

AIPI 510 – Module Project 2

## Overview

Are you really paying more at some grocery stores? We recorded shelf prices for the same
products (mainly **beer** and **snack bars**) at six stores in Durham, NC, and compared each
store's price with an **online reference price** for the same product (the brand's official
storefront, or Amazon / Total Wine when no official storefront exists).

**Research question:** For each store, is the average price different from the online
reference price?

**Analysis:** one-sample t-test per store on the log price premium
(equivalent to a paired t-test of store price vs. online price), with Holm correction
for testing several stores.

Full methods, results and interpretation are in [`outputs/written_report.md`](outputs/written_report.md).

## Stores

| Store | Type |
|---|---|
| Bulldega | small store |
| Gazelle | small store |
| Durham Co-op | co-op |
| Food Lion | chain |
| Harris Teeter | chain |
| Whole Foods | chain |

## Repository structure

```
store-price-premium/
├── data/
│   ├── raw/
│   │   ├── raw_prices.xlsx        # prices recorded in stores (one row = one product at one store)
│   │   ├── ground_truth.xlsx      # online reference prices (read first by clean_data.py)
│   │   └── ground_truth.csv       # same reference prices in CSV (used if the .xlsx is missing)
│   └── clean/
│       ├── prices_long.csv        # cleaned data, one row = one product at one store
│       └── price_table.xlsx       # product x store price tables
├── src/
│   ├── clean_data.py              # 1. clean raw data and attach reference prices
│   ├── power_t-test.py            # 2. power analysis / sample size planning
│   ├── analysis.py                # 3. statistical tests: each store vs online price
│   └── visualizations.py          # 4. figures
└── outputs/
    ├── written_report.md          # final report
    ├── pilot_premiums.csv         # per-product premiums used for planning
    ├── power_table.csv            # required sample size per store
    ├── store_vs_online.csv        # test results per store
    └── figures/                   # charts (PNG + PDF) and summary tables
```

## What each script does

### 1. `src/clean_data.py` — data cleaning

- Standardizes store names and brand names (e.g. "Rx bar" → "RXBAR").
- Converts price text to numbers and separates regular, sale and member prices.
- Flags **substitutes** (a different flavor or pack size than the target product);
  these are kept for review but excluded from all comparisons.
- Loads the online reference prices and matches them to each product by brand + product name.
  If both a storefront price and an Amazon / Total Wine price exist, the storefront price is used.
- Computes the premium vs. the online price:
  - `regular_premium_pct` = (regular shelf price / online price − 1) × 100
  - `paid_premium_pct` = (price actually paid, after discounts / online price − 1) × 100

**Output:** `data/clean/prices_long.csv`, `data/clean/price_table.xlsx`
(sheets: regular price, paid price, removed substitutes, long data, reference data)

### 2. `src/power_t-test.py` — power analysis

- Uses the pilot data to estimate how variable the log premium is at each store.
- Asks: how many matched products does each store need to detect a **50% premium**
  vs. the online price, with a two-sided test, Bonferroni-adjusted α = 0.05 / 6,
  and power of 0.80 or 0.90?
- Also shows a sensitivity check where the pilot standard deviation is multiplied by 1.25 and 1.5.

**Output:** `outputs/pilot_premiums.csv`, `outputs/power_table.csv`

### 3. `src/analysis.py` — statistical tests (each store vs. online price)

For every store with at least 5 matched products:

- **Premium:** log(store regular price / online price) for each product.
- **Test:** one-sample t-test of H₀: mean log premium = 0.
- **Multiple comparisons:** Holm correction across the stores tested.
- **Reported:** mean premium (%), 95% confidence interval, effect size (Cohen's dz), t, p, Holm p.
- **Assumption check:** Shapiro-Wilk normality test on the log premiums.
- **Robustness check:** Wilcoxon signed-rank test (does not assume normality).

Gazelle (2 matched products) is reported descriptively only.

**Output:** `outputs/store_vs_online.csv`

### 4. `src/visualizations.py` — figures

Saved to `outputs/figures/` as PNG and PDF:

- `store_premiums` — mean premium vs. online price for each store, with 95% CIs
- `product_heatmap` — premium of each product at each store
- `product_coverage` — how many products per store were usable, and why others were excluded

Also writes `visualization_summary.csv` and `outcomes.txt`.

## How to run

**Requirements:** Python 3, with:

```bash
pip install pandas numpy scipy statsmodels matplotlib openpyxl
```

**Run from the project root, in this order:**

```bash
python src/clean_data.py
python src/power_t-test.py
python src/analysis.py
python src/visualizations.py
```

Every script after `clean_data.py` reads `data/clean/prices_long.csv`, so re-run
`clean_data.py` first whenever the raw data or reference prices change.

## Notes on the data

- **Online reference prices** come from the brand's official storefront where available
  (RXBAR, Big Spoon, Luna), otherwise Amazon's official brand store (Kind) or Total Wine (beer).
  Multipack prices were converted to a per-unit price (see the `Notes` column of `ground_truth`).
- Product names in `raw_prices.xlsx` and `ground_truth` must match exactly
  (case and outer spaces are ignored); otherwise the product gets no reference price.
- Analyses use the **regular shelf price**, not sale prices, because temporary discounts
  depend on the day of the visit.
- Not every product was found at every store, so each store's sample contains a
  different set of products. See `outputs/figures/product_coverage.png`.
