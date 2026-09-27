# Finora · Phase 1 EDA — Working notes

> **Understand first. Explain later. Decide last.**
> This document describes what the data contains and how it behaves. It does not diagnose the CRO or CFO problems.

Generated {{generated}} by `finora_eda.py` · every number below is recomputed from the raw files (no hand-typed figures).

---

## 0. Deliverables

| File | What it is |
|---|---|
| `finora_eda.html` | Self-contained exploration workspace (no external dependencies except optional Google Fonts; opens offline). |
| `finora_analytical_dataset.csv` | Customer-month analytical table — {{n_rows_tx}} rows, one per customer and month. |
| `finora_monthly_metrics.csv` | Company-level monthly metrics: customers, MRR bridge, value, rates, S&M components and groups, efficiency. |
| `finora_eda_notes.md` | This file: definitions, transformations, assumptions, anomalies, questions, limitations. |
| `finora_eda.py` | Reproducible pipeline (Python {{py_version}} · pandas {{pandas_version}} · numpy {{numpy_version}} · scipy {{scipy_version}}). |
| `supporting/*.csv`, `supporting/data_audit.json` | Industry, cohort, correlation, decomposition, bridge and audit tables used by the workspace. |
| `templates/` | HTML/JS/Markdown templates the pipeline fills. |

Reproduce: `python3 finora_eda.py` (reads `data/raw/`, writes everything above in ~3 seconds).

---

## 1. Source audit

### 1.1 `Transactions.csv` — a customer × month snapshot, not transactions

| Check | Result |
|---|---|
| Columns | `ID`, `month`, `amount` (UTF-8 with BOM) |
| Rows | {{n_rows_tx}} = {{n_customers}} customers × {{n_months}} months → **complete balanced panel** |
| Grain | one row per customer and calendar month (`month` is a month-end date, `M/D/YYYY` text) |
| Time range | {{window_start}} → {{window_end}} |
| Duplicates | 0 on (`ID`, `month`); 0 full-row duplicates |
| Missing / unparseable | 0 |
| Negative amounts | 0 |
| Zero amounts | {{zero_rows}} rows ({{zero_share}}) — inactive months are explicit zeros |
| Positive amounts | {{pos_rows}} rows; range {{amount_min_cop}} – {{amount_max_cop}}; median {{amount_p50_cop}}; P99 {{amount_p99_cop}} |
| Outliers | {{rows_above_fence}} customer-months ({{customers_above_fence}} customers) above Q3 + 3·IQR ({{iqr_fence_cop}}). Kept. |
| Precision | up to 6 decimals ({{rows_6_decimals}} rows with 6 decimals) → compared exactly as integer micro-units |
| Naming | file name says “Transactions” but the grain is a monthly snapshot per customer |

### 1.2 `Industry.csv`

| Check | Result |
|---|---|
| Columns | `ID`, `Industria` (UTF-8 with BOM; mixed-language headers) |
| Rows | {{ind_rows_read}} read → {{ind_blank_rows}} fully blank trailing row removed → {{ind_valid}} |
| Key | `"Cliente N"` → `N` (regex `^Cliente (\d+)$`); unique; contiguous 1…{{ind_valid}} |
| Values | {{n_industries}} industries, no case/accent/whitespace variants: Restaurantes, Producción, Retail, Tecnología, Servicios profesionales, Salud |
| Match with Transactions | {{id_match_rate}} in both directions — no exceptions |

### 1.3 `S&M_spend.csv`

| Check | Result |
|---|---|
| Columns | `Month` (`YYYY-MM`) + `PaidMedia`, `Travel`, `PublicidadNoWeb`, `Freelance`, `SoftwareTools`, `Team`, `PayrollExpenses` |
| Rows | 34 months, identical to the Transactions months; no duplicates or missing values |
| Format | text with `$` prefix and `.` as decimal separator (`"$1.040"`, `"$0.120"`); negatives as `"-$0.016"` |
| Unit | **undocumented** — no scale factor was provided, so spend cannot be converted to COP. Kept in reported units (**u**). |
| Structure | In {{whole_pct_months}} of 34 months every component is a whole-percent share of the monthly total → consistent with top-down allocation |
| `Team` | exactly 12.0% of total S&M in {{team_fixed_months}} consecutive months (through {{team_fixed_until}}); an independent, slowly rising series from {{team_break}} |
| `PayrollExpenses` | negative in {{payroll_neg_n}} months ({{payroll_neg_list}}); after {{team_break}} it behaves like a balancing item |
| `Freelance` | zero from {{freelance_zero_from}} ({{freelance_zero_n}} of the last {{freelance_months_since}} months; exception: {{freelance_exceptions}}) |
| Level shift | Total S&M {{sm_peak}} ({{sm_peak_month}}) → {{sm_trough}} ({{sm_trough_month}}), {{sm_drop}}; Paid Media {{pm_drop}} |

### 1.4 Consistency across sources

- Every Transactions `ID` has exactly one industry and vice versa ({{id_match_rate}}).
- The three files cover the same 34 months ({{window_start}} → {{window_end}}).
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
   - monthly MRR bridge closes (max |residual| = COP {{bridge_max_diff}}) and customer bridge closes exactly;
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
| `previous_month_mrr` | prev (empty in {{window_start}}) |
| `mrr_change` | curr − prev (empty in {{window_start}}) |
| `first_positive_month` = `cohort_month` | first month with curr > 0 |
| `cohort_flag` | `left_censored` (first positive = {{window_start}}), `suspected_spillover` (Feb-22), `clean` |
| `tenure_month` | months since cohort month (M0 = cohort month); empty before it |
| `movement_type` | one of: `window_start_active`, `window_start_inactive`, `new`, `expansion`, `contraction`, `flat`, `churn`, `reactivation`, `not_yet_active`, `inactive_after_churn` |
| `new_customer` | curr > 0 and never > 0 before (not identifiable in {{window_start}}) |
| `churned_customer` | prev > 0 and curr = 0 (observed churn) |
| `reactivated_customer` | curr > 0, prev = 0, positive at some earlier month |
| `expanded_customer` | curr > prev > 0 |
| `contracted_customer` | 0 < curr < prev |
| `flat_customer` | curr = prev > 0 |
| `new_mrr_cop`, `reactivation_mrr_cop` | curr on new / reactivation rows |
| `expansion_mrr_cop`, `contraction_mrr_cop` | curr − prev on expansion (positive) / contraction (negative) rows |
| `churned_mrr_cop` | −prev on churn rows (negative) |
| `months_to_return` | churn rows: months until the next positive month (empty if none by {{window_end}}) |
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
| `window_flag` | `left_censored_start` ({{window_start}}), `suspected_spillover` (Feb-22), `clean` |
| `*_3m_avg` | trailing 3-month averages (flows only inside the clean window) |

### 3.4 S&M groupings

| Group | Components | Rationale (hypothesis, not accounting truth) |
|---|---|---|
| Demand Generation | PaidMedia + PublicidadNoWeb | spend meant to create demand |
| Sales / Acquisition capacity | Team + PayrollExpenses + Travel | people and field capacity to convert demand |
| Enablement / Support | SoftwareTools + Freelance | tools and external support |
| Total S&M | all seven | as delivered |
| Total S&M ex-Payroll | Total − PayrollExpenses | sensitivity only |

**Why keep all seven in Total S&M, and when to exclude one.** Nothing proves a component is not S&M, so all are kept. Technical reasons to test an alternative: `PayrollExpenses` has {{payroll_neg_n}} negative months, behaves like a balancing item after {{team_break}} and may overlap `Team` (hence `total_sm_ex_payroll`). `Team` has a definitional break in {{team_break}} (fixed 12% allocation → independent series), so trends across that month are not like-for-like. `Freelance`, `SoftwareTools` and `Travel` may contain non-S&M costs; the data cannot split them.

### 3.5 Efficiency

Monthly: spend (u) ÷ new customers, and spend (u) ÷ New MRR in COP millions — for Total S&M, Demand Gen and Paid Media. Trailing-3-month versions use sums over three clean months. Inverses (new customers or New MRR per unit of spend) are provided. Not computed in {{window_start}} (new customers not identifiable) and Feb-22 (spillover); no clean month has a zero denominator. Yearly figures pool sums (Σ spend ÷ Σ outcome).

### 3.6 Lag relationships

For spend ∈ {Paid Media, Demand Gen, Total S&M}, outcome ∈ {New customers, New MRR}, lag k ∈ {0,1,2,3}: pairs (spend(t−k), outcome(t)) for outcome months in the clean window (n = {{corr_n_min}}–{{corr_n_levels}}). Pearson r and Spearman ρ with p-values, on levels and on month-over-month changes (both series differenced). Sensitivity including Feb-22 in `supporting/lag_correlations_incl_feb22.csv`. Language is associative only.

### 3.7 Mix vs within decomposition

Average entry ticket `A = Σ sᵢ·aᵢ` (sᵢ = industry share of new customers, aᵢ = industry mean first-month MRR). Two-factor **Shapley (midpoint)** decomposition, exact with no residual:

- mix = Σ (sᵢ¹ − sᵢ⁰) · (aᵢ⁰ + aᵢ¹)/2
- within = Σ (aᵢ¹ − aᵢ⁰) · (sᵢ⁰ + sᵢ¹)/2

Laspeyres (mix at base rates, within at base mix, plus interaction) reported as a cross-check. Uncertainty: 2,000 bootstrap resamples of new customers within each period (seed fixed) → 90% intervals. Variants: M0 (primary), M0 winsorised at pooled P99 ({{winsor_cap}}), early run-rate (median of positive amounts in M0–M2). Periods: 2022 (Mar–Dec), 2023, 2024 (Jan–Oct); half-year evolution vs the 2022 base.

### 3.8 Cohorts

Cohort = first positive month. {{window_start}} actives ({{base_size}}) are left-censored and tracked separately in calendar time; Feb-22 entries are flagged. Logo retention at Mₖ = share of the cohort with paid MRR > 0 at tenure k (point-in-time; a customer can return). Revenue retention at Mₖ = cohort MRR at Mₖ ÷ the same customers' MRR at M0. MRR per original customer = cohort MRR at Mₖ ÷ customers observable at Mₖ. Every Mₖ uses only customers with at least k months of history (right-censoring). Quarterly cohorts pool monthly cohorts; 2022 Q1 = Mar only and 2024 Q4 = Oct only.

---

## 4. Assumptions (explicit)

1. `amount × 10,000 = COP`, as stated by Finora. Applied without questioning the factor.
2. A customer is **active** in a month if and only if the paid amount is > 0.
3. **Left censoring**: customers paying in {{window_start}} may have been acquired earlier; no movement is assigned to {{window_start}}.
4. **Spillover**: {{feb_sig_share}} of Feb-22 “new” customers pay exactly 2× their second amount (vs {{later_sig_share}} in later cohorts) and Feb-22 has {{feb_vs_typical_new}} the 2022 monthly average of new customers. Feb-22 entries are flagged and excluded from acquisition rates, correlations and cohort trends. Clean window for flows: Mar-22 → {{window_end}}.
5. **No tolerance** on “flat”: any change in the paid amount counts as expansion or contraction.
6. **Industry is static** per customer.
7. **S&M unit unknown**: kept as reported; efficiency ratios are relative over time, not a CAC in COP.
8. S&M group roles (what Team, Travel, Freelance represent) are hypotheses.
9. **Outliers are kept**; their influence is tested (winsorised and median variants).
10. **Right censoring**: churn near {{window_end}} may be temporary; “not back by Oct-24” is censored.

---

## 5. Anomalies and contra-intuitive patterns (investigated before being reported)

1. **`amount` behaves like monthly collections, not contracted MRR.** {{multi_sig_rows}} customer-months ({{multi_sig_customers}} customers) equal 2–12× the customer's usual amount; {{churn_back_1m}} of {{churn_events}} observed churn events return the next month ({{churn_back_any}} at some point); {{exp_mrr_revert}} of Expansion MRR reverts the next month; {{con_mrr_post_spike}} of Contraction MRR is the normalisation after a one-month spike. Examples in the HTML (customers 14, 40, 516, 637).
2. **Feb-22 spillover** (assumption 4).
3. **Entry-ticket step in {{step_month}}**: from {{step_month}} every monthly median entry ticket is below the 2022 median ({{m0_median_2022}}). Mean {{m0_mean_2022}} (2022) → {{m0_mean_2024}} (2024); median {{m0_median_2022}} → {{m0_median_2024}}.
4. **2022 first-month spikes**: {{spike_share_2022}} of 2022 entrants paid > 1.5× their second month in M0 ({{spike_share_2023}} in 2023, {{spike_share_2024}} in 2024) → the 2022 mean ticket and 2022 M0-based revenue retention are distorted. Robust metrics shrink the decline ({{m1_mean_chg_22_24}} to {{m0_mean_chg_22_24}} depending on the metric) but never reverse it.
5. **Spend down, acquisition up**: Total S&M fell {{sm_drop_abs}} ({{sm_peak_month}} → {{sm_trough_month}}) while new customers per month went from {{new_avg_2022}} (2022) to {{new_avg_2023}} (2023) and {{new_avg_2024}} (2024).
6. **Negative level correlation** between spend and new customers (Total S&M, lag 0: r = {{r_new_sm_l0}}); it vanishes on month-over-month changes (max |r| = {{r_mom_absmax}}).
7. **S&M file built top-down** (whole-percent shares; Team fixed at 12% through {{team_fixed_until}}; Freelance → 0 when Team jumps in {{team_break}}; PayrollExpenses negative).
8. **Small ± adjustments and off-grid amounts**: expansion events smaller than 10% went from {{small_exp_first}} ({{small_half_first}}) to {{small_exp_last}} ({{small_half_last}}); contractions {{small_con_first}} → {{small_con_last}}. Share of paid amounts on the COP 2,100 grid: {{grid_2022h2}} (2022 H2) → {{grid_2024h2}} (2024 H2).
9. **Concentration at the top**: the largest account (customer {{top_account_id}}, {{top_account_industry}}) pays a median {{top_account_median}} per month, {{top_account_x_median}} the median customer-month; some customers show periodic large payments (e.g. {{periodic_amount}} roughly once a year).
10. **Monthly MRR is noisy**: it fell month-over-month in {{mrr_mom_negative_months}} of 33 months (e.g. {{mrr_jun22_change}} in Jun-22) while customers kept growing; gross movements ({{gross_movement}}) are {{gross_net_ratio}} the net change ({{net_movement}}).

---

## 6. Descriptive findings by theme

**Growth.** Active customers {{active_start}} → {{active_end}} ({{active_multiple}}); paid MRR {{mrr_start}} → {{mrr_end}} ({{mrr_multiple}}); MRR per active customer {{arpa_start}} → {{arpa_end}} ({{arpa_change}}). Net adds positive in {{net_adds_positive_months}} of {{months_with_flows}} months (negative only in {{net_adds_negative_list}}). Annual net MRR change: 2022 {{ab_net_2022}}, 2023 {{ab_net_2023}}, 2024 {{ab_net_2024}}.

**Monetization.** Customers active in {{window_start}} kept their ARPA ({{base_arpa_start}} → {{base_arpa_end}}). In Oct-24, ARPA by vintage: 2022 {{v2022_arpa_end}}, 2023 {{v2023_arpa_end}}, 2024 {{v2024_arpa_end}}. The 2023–24 vintages are {{recent_vintage_customer_share}} of active customers and {{recent_vintage_mrr_share}} of MRR.

**Sales & Marketing.** Average monthly Total S&M: 2022 {{sm_avg_2022}}, 2023 {{sm_avg_2023}}, 2024 {{sm_avg_2024}} ({{sm_chg_22_24}} vs 2022). Total S&M per new customer: {{cac_sm_2022}} → {{cac_sm_2023}} → {{cac_sm_2024}} ({{total_sm_per_new_customer_chg}}); per COP 1M of New MRR: {{sm_per_mrr_2022}} → {{sm_per_mrr_2023}} → {{sm_per_mrr_2024}} ({{total_sm_per_new_mrr_mm_chg}}).

**Spend relationships.** Levels vs new customers: r from {{r_new_levels_min}} to {{r_new_levels_max}} (all negative). Levels vs New MRR: |r| ≤ {{r_mrr_levels_absmax}}. Month-over-month: |r| ≤ {{r_mom_absmax}}, smallest p = {{r_mom_minp}}. {{n_corr_sig}} of {{n_corr_tests}} tests have p < 0.05 ({{n_corr_false_pos}} expected by chance alone); all {{n_corr_sig}} are negative level correlations with new customers.

**Industries.** Retail's share of new customers: {{retail_new_share_2022}} (2022) → {{retail_new_share_2023}} (2023) → {{retail_new_share_2024}} (2024); Retail entry ticket 2024 {{retail_ticket_2024}}. Restaurantes' MRR share {{rest_mrr_share_2022}} (Dec-22) → {{rest_mrr_share_2024}} (Oct-24). Mean entry ticket fell in {{industries_ticket_fell_22_24}} of 6 industries 2022 → 2024 (median in {{industries_median_fell_22_24}} of 6).

**Mix vs within.** 2022 → 2024 average entry ticket {{dec_a0}} → {{dec_a1}} ({{dec_delta_pct}}): within {{dec_within}} ({{dec_within_share}}), mix {{dec_mix}} ({{dec_mix_share}}); within share 90% interval {{dec_within_ci}}; {{dec_within_share_min}}–{{dec_within_share_max}} across variants. At 2022 mix, 2024 would be {{dec_cf}}. 2022 → 2023 within share {{dec23_within_share}}. 2023 → 2024: {{dec34_delta}} (within 90% interval {{dec34_ci}}).

**Cohorts.** M1 logo retention: 2022 quarters {{m1_logo_2022_min}}–{{m1_logo_2022_max}}; full 2023–24 quarters {{m1_logo_recent_min}}–{{m1_logo_recent_max}}. M12 logo retention {{m12_logo_min}}–{{m12_logo_max}}. Revenue retention M1: 2022 quarters ≤ {{rev_m1_2022_max}} (M0 spikes); 2023–24 ≥ {{rev_m1_recent_min}}. Left-censored base: {{base_logo_end}} still paying in Oct-24, {{base_rev_end}} of its Jan-22 MRR.

**MRR movements.** {{lb_from}} → {{lb_to}}: {{lb_opening_mrr_cop}} + {{lb_new_mrr_cop}} new + {{lb_expansion_mrr_cop}} expansion + {{lb_reactivation_mrr_cop}} reactivation − {{lb_contraction_abs}} contraction − {{lb_churn_abs}} churn = {{lb_closing_mrr_cop}} (residual COP {{lb_check}}). Observed monthly logo churn: {{churn_rate_2022}} (2022), {{churn_rate_2023}} (2023), {{churn_rate_2024}} (2024).

---

## 7. What we know · suspect · cannot know

**Know** — the panel is complete and consistent; customers {{active_multiple}} vs MRR {{mrr_multiple}}; new customers per month doubled while New MRR per month did not; the entry ticket stepped down in {{step_month}} in every industry and {{dec_within_share}} of the fall is within industries; the {{window_start}} base kept its ARPA; S&M fell sharply in mid-2023 while acquisition rose; spend and acquisition are not positively associated at any tested lag; recent cohorts retain at least as well early on; {{churn_back_1m}} of observed churn events return the next month; all bridges close.

**Suspect** (to validate) — `amount` is cash collected/billed per month; part of Feb-22 “new” customers are returning pre-existing customers; the {{step_month}} step reflects pricing/packaging/discounting or smaller customers within each industry; acquisition growth in H2-2023 came from channels not in the S&M file, lags beyond three months, or a cheaper entry point; the S&M file was allocated top-down and Freelance was reclassified into Team; small ± adjustments reflect indexation, discounts, prorations or usage components; 2022 first-month spikes are setup fees or prepayments.

**Cannot know** (not in the files; never filled by assumption) — funnel stages (New → Working → Engaged → SQL → Demo → Proposal → Won) and conversion; stage timestamps, speed to lead, response time, deal velocity; lead source and attribution; SDR/AE owner; self-serve vs sales-assisted; pricing, plans, list vs paid price, contract/subscription value, billing frequency; discounts, promotions, credits; churn/downgrade/reactivation reason codes; whether `amount` is invoiced, collected or contracted; S&M unit and allocation rules; customer size or geography; history before {{window_start}} and after {{window_end}}.

---

## 8. Questions that emerged (for Finora)

1. What exactly is `amount`: invoiced, collected or contracted MRR? Are bi-monthly, annual or prepaid plans billed upfront?
2. What changed in {{step_month}}: price list, packaging, a new entry plan, discounts, a new channel or segment?
3. What is the unit of `S&M_spend`, and how are Team, PayrollExpenses and Freelance defined? Why is Team 12% of the total until {{team_fixed_until}}?
4. Were there acquisition activities outside this file (partners, referrals, organic, events) in H2-2023?
5. Are the negative PayrollExpenses reversals of earlier accruals?
6. Is a zero month followed by a double payment a missed collection, a pause or a billing cycle? Should it count as churn?
7. Do Feb-22 entrants have contract start dates before 2022?
8. Which temporary discounts are planned (CFO), and how will they show up in `amount`?
9. Is there any customer attribute beyond industry (size, plan, city, channel) that could be joined by `ID`?

---

## 9. Limitations

- **Short time series.** {{n_months}} months; correlations use n = {{corr_n_min}}–{{corr_n_levels}}. Series are autocorrelated and trending, which inflates level correlations; month-over-month changes are the stricter read.
- **Multiple testing.** {{n_corr_tests}} correlation tests → about {{n_corr_false_pos}} with p < 0.05 expected by chance.
- **Semantics of `amount`.** If it is cash rather than contracted MRR, every movement category mixes commercial events with billing timing.
- **Censoring.** Left (acquisition before {{window_start}} unknown; spillover into Feb-22) and right (recent churn may be temporary; late cohorts have short histories).
- **Segmentation.** Industry is the only attribute; “within-industry” effects may hide mix effects on unobserved dimensions (size, plan, channel).
- **S&M data.** Unknown unit, allocation-like construction, definitional break in {{team_break}}, negative payroll months.
- **No causal identification.** Nothing here separates the effect of spend, price or product from other changes that happened at the same time.

---

## 10. Verified claims (assertions in `finora_eda.py`)

Every insight-driven title in the workspace is backed by one of these checks. If the data changes and a statement stops being true, the pipeline stops instead of publishing it.

| Check | Claim | Status |
|---|---|---|
<!--CLAIMS-->

---

## 11. Reproducibility

- Command: `python3 finora_eda.py` (optional `--raw-dir`, `--out-dir`).
- Environment: Python {{py_version}}, pandas {{pandas_version}}, numpy {{numpy_version}}, scipy {{scipy_version}}. Bootstrap seed fixed.
- Input SHA-256:
  - `Transactions.csv` `{{hash_tx}}`
  - `Industry.csv` `{{hash_ind}}`
  - `S&M_spend.csv` `{{hash_sm}}`
