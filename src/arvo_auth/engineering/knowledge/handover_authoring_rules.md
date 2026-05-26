# Handover-doc authoring rules

These rules govern the structure of the final `<service>_handover.md` produced by `ServiceHandoverCrew`. The `handover_author` agent MUST read this file in full before generating its output.

## Mandatory sections

The final document MUST contain these top-level sections in this exact order:

```
# <Service Name> — Handover

## 1. TL;DR
## 2. Lifecycle & Status
## 3. What the Service Does Today
## 4. Architecture in One Paragraph
## 5. How to Run It
## 6. How to Debug It
## 7. Who Consumes It (Downstream Impact)
## 8. Decisions Worth Preserving
## 9. Known WIP & Pending Next Steps
## 10. Survival Guide
## 11. Open Questions
## 12. References
```

If a section has no content for the current service, write `_Not captured in source artefacts._` — never silently omit a section.

## Per-section rules

### 1. TL;DR (≤ 120 words)

Five lines, no fluff:

- **Status**: one of `active`, `paused`, `deprecated`, `experimental`, `unclear` (with a parenthetical if "unclear").
- **What it is**: one sentence.
- **Where it lives**: repo + path + (if applicable) deployed location.
- **Last meaningful activity**: date + author.
- **If you're here because something broke**: one-line redirect to Section 6.

### 2. Lifecycle & Status

- Verdict (active / paused / deprecated / experimental / unclear) WITH justification.
- Explicit status strings found in source (FROZEN, SUNSET, etc.), quoted verbatim with location.
- If there's a replacement service mentioned in the sources, name it and link/cite.
- If the service is on a migration path, summarise where it stands.

### 3. What the Service Does Today

- Concrete capabilities (endpoints, jobs, pipelines) — list, not narrative.
- Inputs (what triggers it) and outputs (what it produces).
- Domain context if relevant (TISS / TEA / specific partner).

### 4. Architecture in One Paragraph

- Tech stack (language, framework, key libraries).
- Key abstractions (what reading 3 files would teach you).
- Pointer to deeper docs (`memory-bank/systemPatterns.md`, `docs/`, etc.) if they exist — do not duplicate them.

### 5. How to Run It

Two subsections:

- **Local dev**: exact commands, env vars to set, mocked dependencies.
- **Deploy**: how it gets to prod (gcloud command, GitHub Action, manual step), where the image is built.

### 6. How to Debug It

- Where to look (Cloud Run logs URL or log filter; dashboards; traces).
- Common failure modes documented in source (cite location).
- Local repro pattern if testable offline.

### 7. Who Consumes It (Downstream Impact)

- List of known consumers (other services, pipelines, dashboards).
- For each: what they read (table / topic / endpoint) and what happens if this service stops.
- Coverage caveat: state explicitly what your search could not cover.

### 8. Decisions Worth Preserving

This is where you mine `memory-bank/` (especially `productContext.md`, `systemPatterns.md`, `activeContext.md`) and any in-code decision records.

For each decision:
- The decision (one line).
- The reason (one sentence, paraphrased or quoted).
- Source (file:line or memory-bank/X.md).

Pick the 5–10 most load-bearing. Skip trivia.

### 9. Known WIP & Pending Next Steps

Two distinct groups — keep them as separate subsections:

**9.1 In-code signals** (TODOs, FIXMEs, dead code, unmerged branches):
- Load-bearing TODOs / FIXMEs (not stylistic).
- Half-finished features (empty stubs, commented blocks).
- Branches mentioned in docs but not merged.
- Configs gated behind feature flags that never went on.

**9.2 Pending plan items from external backlog** (if provided):
- A table reproducing every row from the backlog whose `Estado` indicates not-done (`Pending`, `Pronto para começar`, `Testes e correções`) AND that plausibly applies to this service.
- Columns to preserve: `Estado`, `Agente ID` (if any), `Tipo`, `Inteligência/Descrição`, `Código ANS`.
- If relevance to this specific service is ambiguous, include with a `(scope unclear)` note rather than dropping silently.
- If no backlog was provided, write `_No external backlog provided._` and rely on 9.1 only.

### 10. Survival Guide

THREE subsections in this order, each starting with "If you need to ...":

#### If you need to KEEP IT ALIVE
- Minimum monthly maintenance.
- Dependency upgrade cadence.
- Known fragile areas — pin versions / avoid touching.

#### If you need to EXTEND IT
- Where the seams are (file paths).
- The pattern to follow (with one concrete example).
- The tests to mirror.

#### If you need to DEPRECATE OR REMOVE IT
- Consumers to notify (cross-reference Section 7).
- Data retention obligations (BigQuery tables you can't just drop).
- Order of operations (turn off traffic → wait period → delete infra → archive code).

### 11. Open Questions

Numbered list. For each:
- The question (specific, not "what is the architecture").
- Who or what would resolve it (a person, a Slack channel, a dashboard, a meeting).

This section MUST exist. If you do not have at least 3 honest unknowns, you are over-confident — re-read `state.md` and `operations.md` to find the gaps.

### 12. References

- Every file path read (with one-line note on what it provided).
- External links found in source (Notion pages, Linear projects, Slack channels, partner docs).
- Names of people mentioned (last contact, last author).

## Formatting conventions

- Markdown only.
- Headings use `#`, `##`, `###` (do not nest deeper).
- Tables for any comparison ≥ 3 dimensions.
- Code blocks for commands, paths, env var names, queries.
- Numeric and named identifiers preserved exactly as in source (do not normalise casing, do not translate).
- Length: 800–2000 lines is reasonable for a meaningful service. Less is suspicious; more probably means you duplicated content from the lower-level artefacts instead of synthesising.
