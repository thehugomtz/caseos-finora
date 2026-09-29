---
name: clarification-protocol
description: CaseOS adaptation (no upstream skill with this exact name exists in alirezarezvani/claude-skills at the inspected commit). Decides when a framing conversation should ask a clarifying question and when it should state an assumption and keep going. Ask only what blocks the case; one question at a time; never interrogate. Built from the clarification step of alirezarezvani's research skill and the framing checklists of consulting-problem-solving (MIT).
license: MIT (CaseOS adaptation)
---

# Clarification Protocol

Clarify only what blocks progress. Everything else becomes an explicit assumption that Hugo can correct later.

## What can block a case (ask about these, in this order)
1. **Decision** — what the executive is trying to decide or understand. If unknown, the whole framing floats.
2. **Audience** — who must believe the answer (CEO, CRO, CFO, board…), because it changes the question.
3. **Scope** — what is in and out (period, segment, product, geography).
4. **Success** — what would count as a good answer, and at what precision.
5. **Change-my-mind** — what evidence would make Hugo drop his current view.

## Rules
- Ask **at most one** clarifying question per turn, and only if the answer would change what we do next.
- If a reasonable default exists, do not ask: state it as an ASSUMPTION ("Asumo que hablamos de 2022–2024; si no,
  dime") and continue.
- Never ask for information the case material already contains; cite it instead.
- Prefer closed or bounded questions ("¿El CFO quiere entender o decidir?") over open ones ("¿Qué más me puedes
  contar?").
- Do not bundle questions. Do not end every turn with a question: when Hugo is dumping ideas, capture and mirror.
- When Hugo answers, record the answer as a FACT only if it is about the case material; his reading of the situation
  stays an intuition or observation.

## Output
The clarifying question (if any) goes last in the reply, in Hugo's register. Unasked defaults go to the ledger as
ASSUMPTION items so they are visible and correctable.
