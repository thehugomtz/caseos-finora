# Finora · Phase 1 EDA — Working notes

> **Understand first. Explain later. Decide last.**
> This document describes what the data contains and how it behaves. It does not diagnose the CRO or CFO problems.

Generated 27 Sep 2026, 11:00 by `finora_eda.py` · every number below is recomputed from the raw files (no hand-typed figures).

---

## 0. Deliverables

| File | What it is |
|---|---|
| `finora_eda.html` | Self-contained exploration workspace (no external dependencies except optional Google Fonts; opens offline). |
| `finora_analytical_dataset.csv` | Customer-month analytical table — 66,674 rows, one per customer and month. |
| `finora_monthly_metrics.csv` | Company-level monthly metrics: customers, MRR bridge, value, rates, S&M components and groups, efficiency. |
| `finora_eda_notes.md` | This file: definitions, transformations, assumptions, anomalies, questions, limitations. |
| `finora_eda.py` | Reproducible pipeline (Python 3.13.7 · pandas 3.0.3 · numpy 2.4.4 · scipy 1.17.1). |
| `supporting/*.csv`, `supporting/data_audit.json` | Industry, cohort, correlation, decomposition, bridge and audit tables used by the workspace. |
| `templates/` | HTML/JS/Markdown templates the pipeline fills. |

Reproduce: `python3 finora_eda.py` (reads `data/raw/`, writes everything above in ~3 seconds).

---

## 1. Source audit

### 1.1 `Transactions.csv` — a customer × month snapshot, not transactions

| Check | Result |
|---|---|
| Columns | `ID`, `month`, `amount` (UTF-8 with BOM) |
| Rows | 66,674 = 1,961 customers × 34 months → **complete balanced panel** |
| Grain | one row per customer and calendar month (`month` is a month-end date, `M/D/YYYY` text) |
| Time range | Jan-22 → Oct-24 |
| Duplicates | 0 on (`ID`, `month`); 0 full-row duplicates |
| Missing / unparseable | 0 |
| Negative amounts | 0 |
| Zero amounts | 33,703 rows (50.5%) — inactive months are explicit zeros |
| Positive amounts | 32,971 rows; range COP 1.4K – COP 8.48M; median COP 52.5K; P99 COP 325.8K |
| Outliers | 614 customer-months (130 customers) above Q3 + 3·IQR (COP 227.3K). Kept. |
| Precision | up to 6 decimals (6,024 rows with 6 decimals) → compared exactly as integer micro-units |
| Naming | file name says “Transactions” but the grain is a monthly snapshot per customer |

### 1.2 `Industry.csv`

| Check | Result |
|---|---|
| Columns | `ID`, `Industria` (UTF-8 with BOM; mixed-language headers) |
| Rows | 1,962 read → 1 fully blank trailing row removed → 1,961 |
| Key | `"Cliente N"` → `N` (regex `^Cliente (\d+)$`); unique; contiguous 1…1,961 |
| Values | 6 industries, no case/accent/whitespace variants: Restaurantes, Producción, Retail, Tecnología, Servicios profesionales, Salud |
| Match with Transactions | 100% in both directions — no exceptions |

### 1.3 `S&M_spend.csv`

| Check | Result |
|---|---|
| Columns | `Month` (`YYYY-MM`) + `PaidMedia`, `Travel`, `PublicidadNoWeb`, `Freelance`, `SoftwareTools`, `Team`, `PayrollExpenses` |
| Rows | 34 months, identical to the Transactions months; no duplicates or missing values |
| Format | text with `$` prefix and `.` as decimal separator (`"$1.040"`, `"$0.120"`); negatives as `"-$0.016"` |
| Unit | **undocumented** — no scale factor was provided, so spend cannot be converted to COP. Kept in reported units (**u**). |
| Structure | In 17 of 34 months every component is a whole-percent share of the monthly total → consistent with top-down allocation |
| `Team` | exactly 12.0% of total S&M in 17 consecutive months (through May-23); an independent, slowly rising series from Jun-23 |
| `PayrollExpenses` | negative in 5 months (Nov-23, Dec-23, Feb-24, Mar-24, Jul-24); after Jun-23 it behaves like a balancing item |
| `Freelance` | zero from May-23 (17 of the last 18 months; exception: Jun-23) |
| Level shift | Total S&M 3.45 u (May-23) → 1.10 u (Aug-23), −68%; Paid Media −71% |

### 1.4 Consistency across sources

- Every Transactions `ID` has exactly one industry and vice versa (100%).
- The three files cover the same 34 months (Jan-22 → Oct-24).
- No customer is ever-zero: every customer has at least one positive month.

---

## 2. Transformations

1. **Read raw text** with `utf-8-sig` (removes the BOM) and keep every value as text first, so the audit sees exactly what was delivered. SHA-256 of each input is recorded.
2. **Industry key**: drop the blank row; extract `N` from `"Cliente N"`; assert uniqueness and full match.
3. **Transactions**: parse `ID` → int, `month` → monthly period, `amount` → float, then to **integer micro-units** (`round(amount × 1,000,000)`) so equality/ordering comparisons are exact.
4. **Panel**: pivot to customers × months (complete, no gaps to fill). Derive previous-month MRR, movement flags, movement values, tenure and cohort (definitions in §3).
5. **COP**: `paid_mrr_cop = observed_amount × 10,000` (1 micro-unit = COP 0.01).
6. **Monthly metrics**: aggregate flags and movement values per month; add rates, percentiles, rolling averages.
7. **S&M**: strip `$`, parse signed decimals, keep the 7 components, add analytical groups and totals, join by month.
8. **Views**: industries, cohorts, lag correlations, mix/within decomposition, bridge and movement diagnostics.
9. **Validation** (the pipeline stops if any fails):
   - row-level identity `curr − prev = New + Expansion + Reactivation + Contraction + Churn` for every customer-month;
   - monthly MRR bridge closes (max |residual| = COP 0.000000) and customer bridge closes exactly;
   - annual and last-month bridges close;
   - total paid MRR = raw amount total × 10,000; active customer-months = positive rows;
   - industry splits add up to company totals; movement flags are mutually exclusive;
   - Shapley mix + within = total change (to 1e-6);
   - the claims registry (§10).

---

## 3. Definitions

### 3.1 Three layers, kept apart

| Layer | Content |
|---|---|
| **Observed** | `observed_amount` exactly as delivered. Never overwritten. |
| **Derived** | `paid_mrr_cop` and every flag, rate and aggregate below. Mechanical, documented, reproducible. |
| **Interpreted** | Only in prose (HTML and this file), always labelled as a hypothesis. Never encoded as a field. |

> All movement categories describe the **observed paid amount**. With the current data we cannot tell whether an expansion or contraction comes from usage, plan, pricing, discounts, credits or any other commercial decision.

### 3.2 Customer-month table (`finora_analytical_dataset.csv`)

`curr` = paid MRR in month t, `prev` = paid MRR in t−1. Comparisons are exact (micro-units).

| Column | Definition |
|---|---|
| `customer_id` | numeric ID (from `"Cliente N"`) |
| `industry` | industry as delivered (static per customer) |
| `month`, `month_index` | calendar month (`YYYY-MM`) and 0…33 |
| `observed_amount` | raw amount |
| `paid_mrr_cop` | observed_amount × 10,000 |
| `active_customer` | 1 if curr > 0 |
| `previous_month_mrr` | prev (empty in Jan-22) |
| `mrr_change` | curr − prev (empty in Jan-22) |
| `first_positive_month` = `cohort_month` | first month with curr > 0 |
| `cohort_flag` | `left_censored` (first positive = Jan-22), `suspected_spillover` (Feb-22), `clean` |
| `tenure_month` | months since cohort month (M0 = cohort month); empty before it |
| `movement_type` | one of: `window_start_active`, `window_start_inactive`, `new`, `expansion`, `contraction`, `flat`, `churn`, `reactivation`, `not_yet_active`, `inactive_after_churn` |
| `new_customer` | curr > 0 and never > 0 before (not identifiable in Jan-22) |
| `churned_customer` | prev > 0 and curr = 0 (observed churn) |
| `reactivated_customer` | curr > 0, prev = 0, positive at some earlier month |
| `expanded_customer` | curr > prev > 0 |
| `contracted_customer` | 0 < curr < prev |
| `flat_customer` | curr = prev > 0 |
| `new_mrr_cop`, `reactivation_mrr_cop` | curr on new / reactivation rows |
| `expansion_mrr_cop`, `contraction_mrr_cop` | curr − prev on expansion (positive) / contraction (negative) rows |
| `churned_mrr_cop` | −prev on churn rows (negative) |
| `months_to_return` | churn rows: months until the next positive month (empty if none by Oct-24) |
| `returned_next_month`, `returned_same_amount_next_month` | churn rows: 1 if positive (at the same amount) in t+1 |
| `reverts_next_month` | expansion/contraction rows: 1 if amount in t+1 equals prev (one-month spike/dip) |
| `usual_amount_cop` | the customer's most frequent positive amount (ties → smallest) |
| `amount_vs_usual_ratio` | curr ÷ usual amount |
| `multi_month_payment_signature` | k (2…12) when curr = k × usual amount (±0.5%) and the usual amount appears ≥ 3 times; else 0 |

Bridge identity (every row with a previous month): `mrr_change = new + expansion + reactivation + contraction + churned`.

### 3.3 Monthly metrics (`finora_monthly_metrics.csv`)

| Metric | Definition |
|---|---|
| Active / New / Churned / Reactivated / Expanded / Contracted / Flat customers | counts of the flags |
| Net customer adds | New + Reactivated − Churned (= Δ active customers, validated) |
| Total paid MRR | Σ paid_mrr_cop |
| New / Expansion / Reactivation / Contraction / Churned MRR | Σ of movement values (contraction and churn negative) |
| Net MRR change | Σ of the five (= Δ MRR, validated) |
| MRR per active customer | Total paid MRR ÷ active customers |
| New MRR per new customer | New MRR ÷ new customers (mean); `median`, `p25`, `p75`, `p90` over the same first amounts |
| Logo churn rate | churned(t) ÷ active(t−1) |
| Gross MRR churn / contraction / expansion rate | movement(t) ÷ MRR(t−1) |
| Reactivation rate | reactivated(t) ÷ dormant pool(t−1) (inactive at t−1 but positive before) |
| Net MRR retention (existing) | (MRR(t−1) + expansion + contraction + churn) ÷ MRR(t−1) |
| Quick ratio | (new + expansion + reactivation) ÷ −(contraction + churn) |
| `window_flag` | `left_censored_start` (Jan-22), `suspected_spillover` (Feb-22), `clean` |
| `*_3m_avg` | trailing 3-month averages (flows only inside the clean window) |

### 3.4 S&M groupings

| Group | Components | Rationale (hypothesis, not accounting truth) |
|---|---|---|
| Demand Generation | PaidMedia + PublicidadNoWeb | spend meant to create demand |
| Sales / Acquisition capacity | Team + PayrollExpenses + Travel | people and field capacity to convert demand |
| Enablement / Support | SoftwareTools + Freelance | tools and external support |
| Total S&M | all seven | as delivered |
| Total S&M ex-Payroll | Total − PayrollExpenses | sensitivity only |

**Why keep all seven in Total S&M, and when to exclude one.** Nothing proves a component is not S&M, so all are kept. Technical reasons to test an alternative: `PayrollExpenses` has 5 negative months, behaves like a balancing item after Jun-23 and may overlap `Team` (hence `total_sm_ex_payroll`). `Team` has a definitional break in Jun-23 (fixed 12% allocation → independent series), so trends across that month are not like-for-like. `Freelance`, `SoftwareTools` and `Travel` may contain non-S&M costs; the data cannot split them.

### 3.5 Efficiency

Monthly: spend (u) ÷ new customers, and spend (u) ÷ New MRR in COP millions — for Total S&M, Demand Gen and Paid Media. Trailing-3-month versions use sums over three clean months. Inverses (new customers or New MRR per unit of spend) are provided. Not computed in Jan-22 (new customers not identifiable) and Feb-22 (spillover); no clean month has a zero denominator. Yearly figures pool sums (Σ spend ÷ Σ outcome).

### 3.6 Lag relationships

For spend ∈ {Paid Media, Demand Gen, Total S&M}, outcome ∈ {New customers, New MRR}, lag k ∈ {0,1,2,3}: pairs (spend(t−k), outcome(t)) for outcome months in the clean window (n = 30–32). Pearson r and Spearman ρ with p-values, on levels and on month-over-month changes (both series differenced). Sensitivity including Feb-22 in `supporting/lag_correlations_incl_feb22.csv`. Language is associative only.

### 3.7 Mix vs within decomposition

Average entry ticket `A = Σ sᵢ·aᵢ` (sᵢ = industry share of new customers, aᵢ = industry mean first-month MRR). Two-factor **Shapley (midpoint)** decomposition, exact with no residual:

- mix = Σ (sᵢ¹ − sᵢ⁰) · (aᵢ⁰ + aᵢ¹)/2
- within = Σ (aᵢ¹ − aᵢ⁰) · (sᵢ⁰ + sᵢ¹)/2

Laspeyres (mix at base rates, within at base mix, plus interaction) reported as a cross-check. Uncertainty: 2,000 bootstrap resamples of new customers within each period (seed fixed) → 90% intervals. Variants: M0 (primary), M0 winsorised at pooled P99 (COP 595.2K), early run-rate (median of positive amounts in M0–M2). Periods: 2022 (Mar–Dec), 2023, 2024 (Jan–Oct); half-year evolution vs the 2022 base.

### 3.8 Cohorts

Cohort = first positive month. Jan-22 actives (377) are left-censored and tracked separately in calendar time; Feb-22 entries are flagged. Logo retention at Mₖ = share of the cohort with paid MRR > 0 at tenure k (point-in-time; a customer can return). Revenue retention at Mₖ = cohort MRR at Mₖ ÷ the same customers' MRR at M0. MRR per original customer = cohort MRR at Mₖ ÷ customers observable at Mₖ. Every Mₖ uses only customers with at least k months of history (right-censoring). Quarterly cohorts pool monthly cohorts; 2022 Q1 = Mar only and 2024 Q4 = Oct only.

---

## 4. Assumptions (explicit)

1. `amount × 10,000 = COP`, as stated by Finora. Applied without questioning the factor.
2. A customer is **active** in a month if and only if the paid amount is > 0.
3. **Left censoring**: customers paying in Jan-22 may have been acquired earlier; no movement is assigned to Jan-22.
4. **Spillover**: 30% of Feb-22 “new” customers pay exactly 2× their second amount (vs 3.0% in later cohorts) and Feb-22 has 4.0× the 2022 monthly average of new customers. Feb-22 entries are flagged and excluded from acquisition rates, correlations and cohort trends. Clean window for flows: Mar-22 → Oct-24.
5. **No tolerance** on “flat”: any change in the paid amount counts as expansion or contraction.
6. **Industry is static** per customer.
7. **S&M unit unknown**: kept as reported; efficiency ratios are relative over time, not a CAC in COP.
8. S&M group roles (what Team, Travel, Freelance represent) are hypotheses.
9. **Outliers are kept**; their influence is tested (winsorised and median variants).
10. **Right censoring**: churn near Oct-24 may be temporary; “not back by Oct-24” is censored.

---

## 5. Anomalies and contra-intuitive patterns (investigated before being reported)

1. **`amount` behaves like monthly collections, not contracted MRR.** 512 customer-months (325 customers) equal 2–12× the customer's usual amount; 44% of 751 observed churn events return the next month (62% at some point); 29% of Expansion MRR reverts the next month; 13% of Contraction MRR is the normalisation after a one-month spike. Examples in the HTML (customers 14, 40, 516, 637).
2. **Feb-22 spillover** (assumption 4).
3. **Entry-ticket step in Jan-23**: from Jan-23 every monthly median entry ticket is below the 2022 median (COP 63.0K). Mean COP 128.7K (2022) → COP 50.8K (2024); median COP 63.0K → COP 42.0K.
4. **2022 first-month spikes**: 15% of 2022 entrants paid > 1.5× their second month in M0 (4% in 2023, 9% in 2024) → the 2022 mean ticket and 2022 M0-based revenue retention are distorted. Robust metrics shrink the decline (−18% to −60% depending on the metric) but never reverse it.
5. **Spend down, acquisition up**: Total S&M fell 68% (May-23 → Aug-23) while new customers per month went from 27 (2022) to 54 (2023) and 55 (2024).
6. **Negative level correlation** between spend and new customers (Total S&M, lag 0: r = −0.57); it vanishes on month-over-month changes (max |r| = 0.27).
7. **S&M file built top-down** (whole-percent shares; Team fixed at 12% through May-23; Freelance → 0 when Team jumps in Jun-23; PayrollExpenses negative).
8. **Small ± adjustments and off-grid amounts**: expansion events smaller than 10% went from 9% (2022 H1) to 75% (2024 H2); contractions 9% → 56%. Share of paid amounts on the COP 2,100 grid: 81% (2022 H2) → 58% (2024 H2).
9. **Concentration at the top**: the largest account (customer 94, Restaurantes) pays a median COP 3.1M per month, 60× the median customer-month; some customers show periodic large payments (e.g. COP 2.14M roughly once a year).
10. **Monthly MRR is noisy**: it fell month-over-month in 10 of 33 months (e.g. −20% in Jun-22) while customers kept growing; gross movements (COP 404M) are 6.5× the net change (COP 62M).

---

## 6. Descriptive findings by theme

**Growth.** Active customers 377 → 1,678 (4.5×); paid MRR COP 35.0M → COP 97.0M (2.8×); MRR per active customer COP 92.8K → COP 57.8K (−38%). Net adds positive in 32 of 33 months (negative only in Jun-22). Annual net MRR change: 2022 COP 27.4M, 2023 COP 15.5M, 2024 COP 19.1M.

**Monetization.** Customers active in Jan-22 kept their ARPA (COP 92.8K → COP 97.4K). In Oct-24, ARPA by vintage: 2022 COP 65.4K, 2023 COP 46.3K, 2024 COP 43.0K. The 2023–24 vintages are 65% of active customers and 50% of MRR.

**Sales & Marketing.** Average monthly Total S&M: 2022 2.87 u, 2023 2.09 u, 2024 1.98 u (−31% vs 2022). Total S&M per new customer: 0.105 u → 0.039 u → 0.036 u (−66%); per COP 1M of New MRR: 0.82 u → 0.81 u → 0.70 u (−14%).

**Spend relationships.** Levels vs new customers: r from −0.60 to −0.26 (all negative). Levels vs New MRR: |r| ≤ 0.14. Month-over-month: |r| ≤ 0.27, smallest p = 0.14. 9 of 48 tests have p < 0.05 (2.4 expected by chance alone); all 9 are negative level correlations with new customers.

**Industries.** Retail's share of new customers: 18% (2022) → 26% (2023) → 24% (2024); Retail entry ticket 2024 COP 36.9K. Restaurantes' MRR share 39% (Dec-22) → 32% (Oct-24). Mean entry ticket fell in 6 of 6 industries 2022 → 2024 (median in 6 of 6).

**Mix vs within.** 2022 → 2024 average entry ticket COP 128.7K → COP 50.8K (−60%): within −COP 75.4K (97%), mix −COP 2.4K (3%); within share 90% interval 91–102%; 96%–97% across variants. At 2022 mix, 2024 would be COP 52.1K. 2022 → 2023 within share 95%. 2023 → 2024: COP 2.9K (within 90% interval −COP 3.2K to COP 6.9K).

**Cohorts.** M1 logo retention: 2022 quarters 89%–95%; full 2023–24 quarters 95%–98%. M12 logo retention 83%–91%. Revenue retention M1: 2022 quarters ≤ 47% (M0 spikes); 2023–24 ≥ 80%. Left-censored base: 79% still paying in Oct-24, 83% of its Jan-22 MRR.

**MRR movements.** Sep-24 → Oct-24: COP 92.7M + COP 2.2M new + COP 2.1M expansion + COP 4.5M reactivation − COP 2.1M contraction − COP 2.3M churn = COP 97.0M (residual COP 0.00). Observed monthly logo churn: 3.5% (2022), 2.2% (2023), 1.9% (2024).

---

## 7. What we know · suspect · cannot know

**Know** — the panel is complete and consistent; customers 4.5× vs MRR 2.8×; new customers per month doubled while New MRR per month did not; the entry ticket stepped down in Jan-23 in every industry and 97% of the fall is within industries; the Jan-22 base kept its ARPA; S&M fell sharply in mid-2023 while acquisition rose; spend and acquisition are not positively associated at any tested lag; recent cohorts retain at least as well early on; 44% of observed churn events return the next month; all bridges close.

**Suspect** (to validate) — `amount` is cash collected/billed per month; part of Feb-22 “new” customers are returning pre-existing customers; the Jan-23 step reflects pricing/packaging/discounting or smaller customers within each industry; acquisition growth in H2-2023 came from channels not in the S&M file, lags beyond three months, or a cheaper entry point; the S&M file was allocated top-down and Freelance was reclassified into Team; small ± adjustments reflect indexation, discounts, prorations or usage components; 2022 first-month spikes are setup fees or prepayments.

**Cannot know** (not in the files; never filled by assumption) — funnel stages (New → Working → Engaged → SQL → Demo → Proposal → Won) and conversion; stage timestamps, speed to lead, response time, deal velocity; lead source and attribution; SDR/AE owner; self-serve vs sales-assisted; pricing, plans, list vs paid price, contract/subscription value, billing frequency; discounts, promotions, credits; churn/downgrade/reactivation reason codes; whether `amount` is invoiced, collected or contracted; S&M unit and allocation rules; customer size or geography; history before Jan-22 and after Oct-24.

---

## 8. Questions that emerged (for Finora)

1. What exactly is `amount`: invoiced, collected or contracted MRR? Are bi-monthly, annual or prepaid plans billed upfront?
2. What changed in Jan-23: price list, packaging, a new entry plan, discounts, a new channel or segment?
3. What is the unit of `S&M_spend`, and how are Team, PayrollExpenses and Freelance defined? Why is Team 12% of the total until May-23?
4. Were there acquisition activities outside this file (partners, referrals, organic, events) in H2-2023?
5. Are the negative PayrollExpenses reversals of earlier accruals?
6. Is a zero month followed by a double payment a missed collection, a pause or a billing cycle? Should it count as churn?
7. Do Feb-22 entrants have contract start dates before 2022?
8. Which temporary discounts are planned (CFO), and how will they show up in `amount`?
9. Is there any customer attribute beyond industry (size, plan, city, channel) that could be joined by `ID`?

---

## 9. Limitations

- **Short time series.** 34 months; correlations use n = 30–32. Series are autocorrelated and trending, which inflates level correlations; month-over-month changes are the stricter read.
- **Multiple testing.** 48 correlation tests → about 2.4 with p < 0.05 expected by chance.
- **Semantics of `amount`.** If it is cash rather than contracted MRR, every movement category mixes commercial events with billing timing.
- **Censoring.** Left (acquisition before Jan-22 unknown; spillover into Feb-22) and right (recent churn may be temporary; late cohorts have short histories).
- **Segmentation.** Industry is the only attribute; “within-industry” effects may hide mix effects on unobserved dimensions (size, plan, channel).
- **S&M data.** Unknown unit, allocation-like construction, definitional break in Jun-23, negative payroll months.
- **No causal identification.** Nothing here separates the effect of spend, price or product from other changes that happened at the same time.

---

## 10. Verified claims (assertions in `finora_eda.py`)

Every insight-driven title in the workspace is backed by one of these checks. If the data changes and a statement stops being true, the pipeline stops instead of publishing it.

| Check | Claim | Status |
|---|---|---|
| `growth_gap` | Active customers grew faster than paid MRR (Jan-22 → Oct-24) | ✅ verified |
| `arpa_down` | MRR per active customer is lower in Oct-24 than in Jan-22 by more than 30% | ✅ verified |
| `net_adds_positive` | Net customer adds were negative in exactly one month | ✅ verified |
| `entry_ticket_down` | Median first-month MRR of new customers is lower in 2023 and 2024 than in 2022 | ✅ verified |
| `ticket_all_metrics` | Every ticket metric (M0 mean/median/winsorised, early run-rate, M1) is lower in 2024 than 2022 | ✅ verified |
| `base_stable` | The left-censored base's ARPA in Oct-24 is within ±10% of Jan-22 | ✅ verified |
| `vintage_order` | At Oct-24, 2023 and 2024 vintages have lower ARPA than the 2022 vintage and the base | ✅ verified |
| `within_dominates` | Within-industry effect explains > 80% of the 2022→2024 change in every variant; bootstrap 90% CI lower bound > 50% | ✅ verified |
| `all_industries_down` | Mean entry ticket fell in all six industries between 2022 and 2024 | ✅ verified |
| `no_positive_assoc` | Level correlations of spend vs new customers (lags 0–1) are all negative; no month-over-month correlation reaches \|r\| ≥ 0.3 or p < 0.05 | ✅ verified |
| `sm_cut` | Total S&M fell more than 60% from its 2023 peak to its 2023 trough | ✅ verified |
| `team_fixed` | Team equals 12.0% of total S&M in every month through May-23 | ✅ verified |
| `recent_cohorts_m1` | The lowest M1 logo retention among full 2023–24 quarterly cohorts exceeds the highest among full 2022 quarters | ✅ verified |
| `ticket_step` | The step month (after which every monthly median entry ticket stays below the 2022 median) falls in Q1-2023 | ✅ verified |
| `cohorts_stay_lower` | MRR per original customer of 2023 cohorts is below that of 2022 cohorts at M1, M6 and M12 | ✅ verified |
| `churn_transient` | More than 40% of observed churn events return the next month | ✅ verified |
| `gross_vs_net` | Gross MRR movements exceed 5× the net change over the window | ✅ verified |
| `last_react_largest` | In the last month, reactivation is the largest inflow | ✅ verified |
| `spend_per_customer_down` | Total S&M per new customer is lower in 2024 than 2022 by more than 50% | ✅ verified |
| `sig_only_negative_levels` | Every correlation with p < 0.05 is a negative level correlation with new customers | ✅ verified |
| `feb_spillover` | Feb-22 entries show the double-payment signature at > 5× the pooled rate of later cohorts | ✅ verified |

---

## 11. Reproducibility

- Command: `python3 finora_eda.py` (optional `--raw-dir`, `--out-dir`).
- Environment: Python 3.13.7, pandas 3.0.3, numpy 2.4.4, scipy 1.17.1. Bootstrap seed fixed.
- Input SHA-256:
  - `Transactions.csv` `2dcbe59e9ac497c441f3c019963b11e9848ce4916e5773d257a36f83d953ae95`
  - `Industry.csv` `b4330fc6d7df60429849b3b176746f5389c65931f281308eb8224c8efd440ff5`
  - `S&M_spend.csv` `41fbb6499f2b0ad4565ccc0e96ec490c72599e15fd46d64086fd98e3443c4c13`
