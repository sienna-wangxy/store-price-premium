PRICE STUDY VISUALIZATIONS

Copy visualizations.py to your project src directory.
Install dependencies: pip install numpy pandas scipy matplotlib
From your project root, after correcting reference prices, run:
    python src/clean_data.py
    python src/pilot_power.py
    python src/visualizations.py

Charts are saved in outputs/figures as PNG and PDF, with a summary CSV.
The script recalculates estimates directly from prices_long.csv, avoiding stale analysis output.

PREVIEW STATUS
The preliminary_preview folder uses the originally attached data, including the old KIND reference.
These charts demonstrate layout only. Regenerate before reporting corrected-data findings.

INTERPRETATION
Report all sampled stores, regardless of whether their sample meets a planning target.
Power is a design consideration, not a reporting filter or a guarantee for a realized sample.
The five-product convention follows analysis.py; it does not establish adequate power or valid assumptions.
Gazelle has two pairs in the available data and is shown descriptively without an interval or p-value.
Intervals are individual 95% t intervals; Holm p-values cover the stores actually tested.
A 50% premium is the planning effect, not the test null or a significance cutoff.
Heatmap cells show product percentage differences; store points show geometric mean premiums.
Different stores have different baskets: these estimates are not a controlled ranking of store types.
The missing-price category includes unavailable or unparseable prices and does not establish absence.
Notes currently trigger substitution exclusion in clean_data.py; review ambiguous notes manually.
Mixed benchmark sources and multipack unit prices limit interpretation as official-seller comparisons.
Small nonrandom samples and related products limit generalization and independence.
Inspect paired log ratios for outliers/normality before final inference.
A nonsignificant result does not establish equivalent prices.
