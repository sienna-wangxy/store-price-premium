# Beers and Bars: Regular Shelf-Price Premiums Relative to Online Benchmarks in Durham, North Carolina

Jothi Gupta & Sienna Wang

## Abstract

This observational study examined whether regular shelf prices for selected snack bars and beers at six Durham sellers differed from matched online reference prices. The analysis included 43 product–store observations representing 13 distinct products, with 2–12 matched products per seller. Each product was paired with an online benchmark from a manufacturer storefront or, when unavailable, Amazon or Total Wine as the preferred seller. Two-sided paired t-tests on log-transformed prices, implemented as one-sample tests of log price ratios, were conducted for the five sellers with at least five matched products. Holm adjustment controlled multiple testing. Bulldega had an estimated geometric mean premium of 81.7%  and Durham Co-op had a premium of 32.0%. Harris Teeter, Whole Foods, and Food Lion did not show statistically significant differences after adjustment; Gazelle was described without inference as there were two few relevant goods to meet sample requirements. Exploratory summaries suggested that snack-bar premiums exceeded beer premiums at several sellers. Small convenience samples, related products within brands, uneven product coverage, and differences between multipack online purchases and individual shelf purchases limit interpretation. The results, characterize the sampled products and locations rather than establish a universal ranking of Durham grocery stores, but they do suggest differential prices between select sellers.

## Background and Motivation

As the holiday season approached, seasonal displays of candy and pumpkins prompted our team to ask how prices for everyday goods vary across Durham sellers. Consumers may expect stores perceived as expensive to charge more and stores perceived as inexpensive to offer better value. However, a store's reputation may not describe prices consistently across products.

We selected packaged snack bars and beers as recognizable goods that could be matched across sellers and to external reference prices. The primary research question was: **For each sampled seller, does the average log ratio of regular shelf price to matched online reference price differ from zero?** A secondary descriptive question was whether patterns appeared different for snack bars and beers.

The online prices provide purchasing benchmarks, not manufacturing costs, wholesale costs, or an objectively correct price. Although seasonal observations motivated the study, the design did not test price changes over time. Likewise, the primary tests compare individual sellers with online benchmarks rather than directly compare sellers with one another.

## Null and Alternative Hypotheses

For product $j$ at seller $i$, we define the log price ratio as

$$
d_{ij}=\ln\left(\frac{P_{ij}}{C_j}\right),
$$

where P is the regular shelf price and C is the matched online reference price. Let $ μ_i $ denote the mean log price ratio for seller $i$ in the relevant product population.

For each eligible seller, the two-sided hypotheses were:

$$
H_{0,i}:\mu_i=0,\qquad H_{A,i}:\mu_i\ne0
$$

A mean of zero corresponds to a geometric mean store-to-reference price ratio of one. A positive mean indicates a premium and a negative mean indicates a discount. Each seller has its own hypothesis; the alternative does not require every seller to differ from its benchmark.

The six sampled sellers were Bulldega, Durham Co-op, Food Lion, Gazelle, Harris Teeter, and Whole Foods. Gazelle was excluded from inferential testing because it had only two matched products. Holm adjustment was applied across the five tests performed.

## Experimental Design

This was a cross-sectional, matched-product observational study. Prices were observed rather than experimentally assigned. 

- **Independent variables:** seller and product identity; product category and seller type provided descriptive context.
- **Dependent variables:** regular shelf price for a specified product and package size.
- **Primary analytical outcome:** log store-to-reference price ratio.
- **Control condition:** the corresponding online price (a manufacturer storefront, with Amazon or Total Wine used if otherwise unavailable).
- **Matching:** each eligible product–store observation was paired with its corresponding reference price.

The eligible dataset contained 43 observations across 13 distinct products. Product availability and matching eligibility varied across sellers, producing different product baskets. Several products were flavors within the same brand, which may share pricing decisions and are not necessarily independent sampling units. Store-type comparisons are also constrained by limited representation of individual locations.

## Power Analysis

The supplied power table targeted detection of a **50% geometric mean premium** with a two-sided test, family-wise α = .05, and target power of .80 or .90. Planning assumed six comparisons and used **Bonferroni** α = .05/6 = .00833 per test. The final analysis instead used **Holm adjustment** across five eligible sellers; these procedures serve related but distinct planning and analysis roles.

On the log scale, the target difference was

$$
\delta=\ln(1.50)\approx0.4055
$$

For each seller, the pilot standard deviation $s$ of log price ratios yielded a target standardized effect

$$
d_z=\frac{\ln(1.50)}{s}
$$

For example, Bulldega's pilot standard deviation was 0.3743, yielding $d_z ≈ 1.0832$. The table reported 14 matched products for 80% power and 17 for 90% power under the baseline variability assumption.

| Seller | Available matched products | Pilot log-ratio SD | Required for 80% power | Required for 90% power |
|---|---:|---:|---:|---:|
| Bulldega | 8 | 0.3743 | 14 | 17 |
| Durham Co-op | 12 | 0.2364 | 8 | 9 |
| Food Lion | 5 | 0.1430 | 5 | 6 |
| Gazelle | 2 | 0.1523 | 6 | 6 |
| Harris Teeter | 8 | 0.2469 | 9 | 10 |
| Whole Foods | 8 | 0.1745 | 6 | 7 |

The table increased pilot standard deviations by factors of 1.25 and 1.50 to assess sensitivity. At 1.50 times the pilot standard deviation, the 80% power requirements increased to 27, 13, 7, 8, 14, and 9 products, respectively, in the table's seller order.

The 50% target is a planning assumption, not a significance threshold. A smaller effect can be statistically significant. Conversely, meeting a sample requirement for a 50% effect does not ensure adequate power for a 10% effect. Requirements assume independent product-level observations and reliable variability estimates; both are uncertain here, especially for Gazelle.

## Data Collection and Cleaning Procedures

Shelf prices were recorded for specified snack bars and beers at six Durham sellers and  online reference prices for corresponding products were compiled afterwards. Reference prices were derived from the manufacturer site. If they were not sold on the manufacturing site (this was the case for all the beers), the reference prices came from Total Wine (the vendor of choice for each beer company). If this was the case for certain bars (as with KIND bars), the reference price came from Amazon (the vendor of choice for each snack company). Reference prices came from single bar prices but were converted to per-bar values if single bar costs were unavailable. Beer comparisons retained the recorded package definitions. Data was collected all on the same day to maintain standardization, which was on October 29, 2026.

Goods and vendors were chosen to maintain variety and reduce bias. Vendors were grocery stores in North Durham close to Duke University to be consistent. Initially, gas stations, such as Gazelle were included, but because of reduced item variety, they were excluded from analysis. Goods were chosen at random among goods likely to be at a majority of grocery store sellers. This ended up being select brands of beers and bars. 

The cleaning script standardizes brand and seller names, parses numeric prices, separates regular, sale, and member prices, and flags substitutions or other notes for exclusion from the main comparisons. Product references are joined using standardized brand-plus-product keys. Manufacturer storefront prices take priority when both reference sources are supplied. Missing benchmarks remain missing rather than being imputed.

The script retains the first row when duplicate product–store keys occur. Eligible comparisons require a regular shelf price, a matched reference price, and no substitution flag. The primary outcome uses regular prices rather than temporary sale or member prices.

Inferential testing requires at least five eligible products per seller so sellers with fewer than five products are excluded, such as Gazelle. The supplied eligible dataset contains 43 observations. While the team hoped to have more observations, a combination of variable goods at each store (both in variety and brand) made it difficult to gather a larger standard pool of goods. 

## Statistical Analysis

### Tests and rationale

The primary analysis used a two-sided paired t-test on log-transformed store and reference prices, implemented with `scipy.stats.ttest_1samp` on their log differences. Log ratios express proportional differences across products with different dollar prices. This differs from a paired t-test on untransformed dollar prices.

For $n$ products, the test statistic and effect size were

$$
t=\frac{\bar d}{s_d/\sqrt n},\qquad d_z=\frac{\bar d}{s_d},
$$

with $ n − 1 $ degrees of freedom. The geometric mean premium was calculated as $100[exp(d̄) − 1]$. A 95% $ t $ interval for the mean log ratio was exponentiated and expressed as a percentage premium.

Python code used pandas and NumPy for data handling, SciPy for the t-test, Shapiro–Wilk test, and Wilcoxon signed-rank check, and `statsmodels.stats.multitest.multipletests(method="holm")` for multiple comparisons. Independent recalculation from `pilot_premiums.csv` reproduced the primary p-values and Holm decisions.

### Primary results

| Seller | n | Geometric mean premium | Individual 95% CI | t (df) | Cohen's d_z | Raw p | Holm p |
|---|---:|---:|---|---:|---:|---:|---:|
| Bulldega | 8 | 81.7% | 32.9% to 148.5% | 4.513 (7) | 1.596 | .003 | .011 |
| Durham Co-op | 12 | 32.0% | 13.6% to 53.4% | 4.067 (11) | 1.174 | .002 | .009 |
| Food Lion | 5 | 9.9% | −8.0% to 31.2% | 1.472 (4) | 0.658 | .215 | .298 |
| Gazelle | 2 | 11.4% | Not estimated | — | — | — | — |
| Harris Teeter | 8 | 24.2% | 1.0% to 52.7% | 2.483 (7) | 0.878 | .042 | .126 |
| Whole Foods | 8 | 10.5% | −4.5% to 27.9% | 1.621 (7) | 0.573 | .149 | .298 |

Bulldega and Durham Co-op remained significant at family-wise α = .05. Confidence intervals are individual 95% intervals, not simultaneous intervals adjusted for multiple testing. Thus, Harris Teeter's interval excludes zero while its Holm-adjusted result is nonsignificant. Standardized effects refer to variability in log ratios, not dollar differences.

### Assumptions and robustness

Shapiro–Wilk p-values ranged from .193 to .709 among tested sellers, providing no detected departure from normality. Samples of 5–12 products give these tests limited sensitivity, so nonsignificant normality tests do not establish that the assumption holds. Independence must be assessed from the sampling and pricing structure, not from Shapiro–Wilk results. Related flavors within brands are a particular concern.

The Wilcoxon signed-rank p-values were .008 for Bulldega, .004 for Durham Co-op, .375 for Food Lion, .039 for Harris Teeter, and .297 for Whole Foods. These unadjusted checks are broadly consistent with the primary pattern but are not additional multiplicity-controlled findings. Wilcoxon does not require normality, but it has its own assumptions, including symmetry for a location-shift interpretation; it does not resolve dependence among products.

### Secondary analysis and post hoc tests

Exploratory, unadjusted category summaries showed a 42.6% snack-bar premium versus a −1.3% beer premium at Harris Teeter, and 18.2% versus 3.4% at Whole Foods. These estimates use different, small category samples and are descriptive; they do not establish a statistically significant category effect.

## Interpretation of Results

For the sampled products, Bulldega and Durham Co-op showed evidence of regular shelf-price premiums relative to their online benchmarks. Bulldega's estimate was largest but imprecise, while Durham Co-op's estimate was smaller with a narrower interval.

Harris Teeter's unadjusted result did not remain significant after Holm correction. Food Lion and Whole Foods had smaller positive estimates but insufficient evidence of a difference after adjustment. These outcomes do not demonstrate price equivalence, and Gazelle's two observations cannot support a reliable general conclusion.

Overall, bars tended to have a higher premium than beers as aggregated across vendors. However, because sellers were represented by different product baskets, the results do not establish a statistically tested ranking between stores. Nor does significance for one seller and nonsignificance for another prove that the two sellers differ significantly from each other.

## Limitations

1. **Small, uneven samples:** Only 2–12 products represented each seller, with different eligible baskets and limited precision.
2. **Related observations:** Flavors within brands may share prices and benchmark values. Treating them as independent could understate uncertainty.
3. **Convenience sampling:** Products and locations were limited in variety due to a limited geographic scope.
4. **Reference comparability:** Online sources differed across products. Per-unit multipack prices may not reflect the same purchasing conditions as single bars; shipping, taxes, availability, and minimum purchases were not established in the supplied analysis.
5. **Regular prices only:** Temporary discounts and member prices could change the prices consumers actually face. The study estimates regular shelf-price differences.
7. **Restricted coverage:** Two product categories and six individual sellers cannot characterize the cost of a complete grocery basket or all Durham retailers.
8. **Uncertain power inputs:** Pilot variability estimates are imprecise, particularly for Gazelle, and do not account for possible brand dependence.
10. **Randomization**: The team attempted to get a variety of goods (local and national) such as Big Spoon and Ponysaurus as local Durham sellers, but the limitiation is that Big Spoon bars weren't available in every store and thus couldn't be used in the analysis. 

## Conclusion and Recommendations

The study found evidence of regular shelf-price premiums at Bulldega and Durham Co-op relative to matched online benchmarks for the sampled products. Other tested sellers did not show significant differences after adjustment, but those results should not be interpreted as evidence of equal prices. Descriptive category differences further caution against assuming that a seller's pricing reputation applies uniformly across products.

Consumers may benefit from checking the specific product and purchase quantity rather than relying solely on a store's reputation. Online unit-price comparisons should include the full cost and feasibility of the purchase.

Future collection sample more independent brands and locations, it would be helpful to expand the scope geographically to boost sample size. A brand-level sensitivity analysis would help assess the stability of current conclusions. 

## References and Supporting Materials

Price reference urls:
- KIND: https://www.kindsnacks.com/?srsltid=AYCX9vKNc-20om-9MtcbwvwqC_lK-wVIa8R4VpepT1FleSVQkE79T8k1
  - https://www.amazon.com/kind-bars/s?k=kind+bars
- Luna: https://www.clifbar.com/collections/luna-bar
- Rx Bars: https://shop.rxbar.com/shop/protein-bars.html
- Blue Ribbon beer: https://www.totalwine.com/theme/pabst-beverage?srsltid=AYCX9vIExAi3BUGw2n9RYx9lNHkvVfqNKR-GBYSFVIGOkf0_y4t6f3sm
- Pisgah: https://www.totalwine.com/theme/pisgah-ale?srsltid=AYCX9vI8WX7mBU57hY0GS8wK7hoEN8dzs5SX62xpNX2s73DonPuFp_dW
- Sierra Nevada: https://www.totalwine.com/beer/brand/sierra-nevada?srsltid=AYCX9vJkMV-Z4g-Z5C68cY7H6hadAMZc4WKGQ_Y3ni8UHqZrnHS_Ii-Q
- Ponysaurus: https://www.ponysaurusbrewing.com/
