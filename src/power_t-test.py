"""Plan paired store-versus-reference price comparisons using relative prices.

Run after clean_data.py from the project root:
    python src/pilot_power.py
Dependencies: numpy, pandas, scipy.
Input: data/clean/prices_long.csv
Outputs: outputs/pilot_premiums.csv, outputs/power_table.csv

The target is a geometric mean premium of 50% versus a null premium of 0%.
This does NOT plan a test proving that the premium exceeds 50%.
Two-sided tests match analysis.py. Bonferroni planning is conservative for
its Holm-adjusted final tests. Power targets apply to each individual store,
not the probability of detecting effects at every store simultaneously.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

INPUT_FILE = Path('data/clean/prices_long.csv')
OUTPUT_DIR = Path('outputs')
TARGET_PREMIUM_PCT = 50.0
POWER_TARGETS = (0.80, 0.90)
FAMILY_ALPHA = 0.05
# Keep the planned family fixed even if a store currently has few matches.
PLANNED_STORES = ('Bulldega', 'Durham Co-op', 'Food Lion', 'Gazelle',
                  'Harris Teeter', 'Whole Foods')
# Higher SD scenarios illustrate sensitivity, not formal uncertainty bounds.
SD_MULTIPLIERS = (1.0, 1.25, 1.5)


def paired_power(n_pairs, effect_size, alpha):
    """Exact two-sided t-test power under normal independent differences."""
    df = n_pairs - 1
    critical = stats.t.isf(alpha / 2, df)
    noncentrality = effect_size * np.sqrt(n_pairs)
    return float(stats.nct.sf(critical, df, noncentrality)
                 + stats.nct.sf(critical, df, -noncentrality))


def required_pairs(effect_size, alpha, target_power):
    """Find the smallest integer sample size attaining the requested power."""
    if not np.isfinite(effect_size) or effect_size <= 0:
        raise ValueError('Effect size must be finite and positive.')
    low, high = 2, 2
    while paired_power(high, effect_size, alpha) < target_power:
        high *= 2
        if high > 10_000_000:
            raise ValueError('Required sample size exceeds numerical search limit.')
    while low < high:
        mid = (low + high) // 2
        if paired_power(mid, effect_size, alpha) >= target_power:
            high = mid
        else:
            low = mid + 1
    return low


def boolean_column(series, name):
    """Reject ambiguous flags instead of silently treating strings as True."""
    mapped = series.astype(str).str.strip().str.lower().map(
        {'true': True, 'false': False, '1': True, '0': False})
    if mapped.isna().any():
        raise ValueError(f'{name} contains missing or invalid boolean flags.')
    return mapped.astype(bool)


def main():
    if TARGET_PREMIUM_PCT <= 0 or not np.isfinite(TARGET_PREMIUM_PCT):
        raise ValueError('Target premium must be positive and finite.')
    if not 0 < FAMILY_ALPHA < 1 or any(not 0 < p < 1 for p in POWER_TARGETS):
        raise ValueError('Alpha and power targets must be between zero and one.')
    if not PLANNED_STORES or len(set(PLANNED_STORES)) != len(PLANNED_STORES):
        raise ValueError('Planned stores must be nonempty and unique.')
    if any(not np.isfinite(m) or m <= 0 for m in SD_MULTIPLIERS):
        raise ValueError('SD multipliers must be positive and finite.')
    data = pd.read_csv(INPUT_FILE)
    required = {'store', 'item', 'regular_price', 'control_price',
                'found', 'substitute', 'has_control'}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    flags = {name: boolean_column(data[name], name)
             for name in ('found', 'substitute', 'has_control')}
    data = data[flags['found'] & ~flags['substitute'] & flags['has_control']
                & data.store.isin(PLANNED_STORES)].copy()
    if data[['store', 'item']].isna().any().any():
        raise ValueError('Eligible rows must have store and product identifiers.')
    if data.duplicated(['store', 'item']).any():
        raise ValueError('Duplicate store/product pairs; resolve before planning.')
    for column in ('regular_price', 'control_price'):
        data[column] = pd.to_numeric(data[column], errors='raise')
        if (~np.isfinite(data[column]) | (data[column] <= 0)).any():
            raise ValueError(f'Eligible {column} values must be positive and finite.')

    # Each matched product contributes equally, regardless of its dollar price.
    data['premium_pct'] = 100 * (data.regular_price / data.control_price - 1)
    data['log_premium'] = np.log(data.regular_price / data.control_price)
    target_log_premium = np.log1p(TARGET_PREMIUM_PCT / 100)
    alpha = FAMILY_ALPHA / len(PLANNED_STORES)
    rows = []
    for store in PLANNED_STORES:
        group = data[data.store == store]
        n = len(group)
        sd = group.log_premium.std(ddof=1)
        observed = (100 * np.expm1(group.log_premium.mean())) if n else np.nan
        status = ('insufficient pilot pairs' if n < 2 else
                  'zero or invalid pilot SD; planning unavailable'
                  if not np.isfinite(sd) or sd <= 0 else
                  'very small pilot; SD highly uncertain' if n < 5 else
                  'preliminary; verify controls and independence')
        for multiplier in SD_MULTIPLIERS:
            assumed_sd = sd * multiplier
            dz = target_log_premium / assumed_sd if n >= 2 and sd > 0 else np.nan
            for power in POWER_TARGETS:
                needed = (required_pairs(dz, alpha, power)
                          if np.isfinite(dz) and dz > 0 else None)
                rows.append({
                    'store': store, 'current_matched_products': n,
                    'observed_geometric_premium_pct': observed,
                    'target_premium_pct': TARGET_PREMIUM_PCT,
                    'pilot_log_ratio_sd': sd, 'sd_multiplier': multiplier,
                    'assumed_log_ratio_sd': assumed_sd, 'target_effect_size_dz': dz,
                    'family_alpha': FAMILY_ALPHA, 'planned_tests': len(PLANNED_STORES),
                    'planning_alpha_per_test': alpha, 'alternative': 'two-sided',
                    'target_power': power, 'required_matched_products': needed,
                    'additional_matched_products': max(0, needed - n) if needed else None,
                    'status': status,
                })
    output = pd.DataFrame(rows)
    for column in ('required_matched_products', 'additional_matched_products'):
        output[column] = output[column].astype('Int64')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUTPUT_DIR / 'pilot_premiums.csv', index=False)
    output.to_csv(OUTPUT_DIR / 'power_table.csv', index=False)
    print(f'Target: detect a {TARGET_PREMIUM_PCT:g}% geometric mean premium versus 0%.')
    print(f'Two-sided; {len(PLANNED_STORES)} planned tests; alpha per test = {alpha:.6f}.')
    print(output[output.sd_multiplier == 1][[
        'store', 'current_matched_products', 'target_power',
        'required_matched_products', 'additional_matched_products', 'status'
    ]].to_string(index=False))
    print('\nSaved pilot_premiums.csv and power_table.csv in', OUTPUT_DIR)
    print('Power estimates use pilot variability, not observed-effect post hoc power.')
    print('Verify reference prices before using these sample-size targets.')
    print('Sample sizes assume independent matched products and normal log ratios.')
    print('Extra visits to the same products do not add independent product pairs.')
    print('If enough eligible products cannot be collected, reconsider scope or precision goals.')


if __name__ == '__main__':
    main()
