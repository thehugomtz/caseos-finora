---
name: data-modeling
description: CaseOS core skill for the Data Engineering / Data Modeling Agent. Designs source-of-truth models — grain, fact tables, dimensions, event models, temporal validity, identity, subscription and billing modeling (list price, discount, amount paid, MRR/ARR classification), slowly changing dimensions, joins, observability and data contracts — returning a conceptual model, entities, fields, temporal behavior, business definitions, classification logic, example records, edge cases, data-quality rules and implementation considerations. Not only SQL.
license: MIT (CaseOS)
---

# Data Modeling

Typical question: "¿Cómo distinguir subscription value, discount y amount paid?" The answer is a model the business
can trust, not a query.

## Principles
- **Name the grain before anything else.** One row = one what, at what time? Mixed grains are the root of most metric
  disputes.
- **Separate what was contracted, what was priced, what was discounted and what was paid.** For subscriptions:
  list price (catalog) → contracted value (plan × quantity × term) → discount (amount, type, start/end, reason) →
  invoiced → collected. MRR is a classification over contracted value over time, not over cash.
- **Time is a first-class dimension.** Use effective-dated records (valid_from / valid_to) for prices, plans and
  discounts; snapshot tables for month-end state; events for changes. State which one answers which question.
- **Classification logic is explicit and testable.** New / expansion / contraction / churn / reactivation must be
  defined as rules over consecutive states — including what a temporary discount does (it changes collected value,
  not contracted MRR, unless the business decides otherwise — say so as a decision, not as a fact).
- **Identity**: customer vs account vs subscription vs billing entity; merges and splits; the key that survives.
- **Data contracts and quality rules**: every field has an owner, a type, allowed values, and a test.

## Required output (specialist block)
conceptual_model (text + relationships) · entities (name, description, grain, primary key) · fields (entity, field,
type, definition, example) · temporal_behavior · business_definitions (term, definition) · classification_logic
(case, rule) · example_records (entity, records) · edge_cases · data_quality_rules · implementation_considerations.
Then the case-research-synthesis fields for the COS handoff.

## Guardrails
Never silently change a metric definition. When the case data cannot distinguish two states (e.g. contraction vs
discount with only customer + month + amount), say so plainly and list the fields that would.
