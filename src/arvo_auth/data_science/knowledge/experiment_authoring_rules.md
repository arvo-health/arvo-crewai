# Experiment-spec authoring rules

These rules govern the structure and rigor expected in the final `experiment_spec.md` produced by `ExperimentSpecCrew`. The `experiment_designer` and `spec_author` agents must read these rules in full before generating their respective outputs.

## Mandatory sections in `experiment_spec.md`

The final document MUST contain these top-level sections in this order:

```
# <Project name> — Experiment Specification

## 1. Executive Summary
## 2. Business Case
## 3. Manual Analysis Findings
## 4. Current Pipeline State
## 5. Hypothesis
## 6. Proposed Approach
## 7. Data Requirements
## 8. Methods to Compare
## 9. Evaluation Plan
## 10. Phased Roadmap
## 11. Risks & Mitigation
## 12. Integration Touchpoints
## 13. Open Questions
## 14. Appendix: Source References
```

If a section has no content for the current spec, write `_Not applicable for this experiment._` — never silently omit a section.

## Per-section rules

### 1. Executive Summary (≤ 200 words)

- One paragraph stating: the problem in plain language, the proposed approach in one line, the offline success criterion, the projected business impact.
- MUST reference at least one concrete number from the manual analysis.

### 2. Business Case

- Reproduce **verbatim** every numeric finding from the discovery artefact (sample size, fraud counts, R$ savings, sessions, etc.).
- Project these numbers to a larger scale if the artefact suggests doing so. Show the math.
- State who benefits and how (which Arvo team, which downstream pipeline).

### 3. Manual Analysis Findings

- Enumerate **every signal** the discovery artefact identifies. Do not group into vague categories.
- For each signal: what it is, how it was observed, why it matters.
- This section is the bridge between manual analysis and automatable signals — be exhaustive.

### 4. Current Pipeline State

- Describe the production data flow today, citing repos and files.
- Identify what the pipeline does cover (e.g. presence/absence signature detection via DocAI).
- Identify what is MISSING that this experiment proposes to add.

### 5. Hypothesis

- **One** primary hypothesis, written as a falsifiable statement.
- Optional: 1–2 secondary hypotheses.
- Each hypothesis MUST be paired with the metric that would refute it.

### 6. Proposed Approach

- One paragraph describing the technical strategy at a high level.
- Cite prior art (papers, libraries, public datasets) with at least one reference per non-trivial technique.

### 7. Data Requirements

- Source of data (which BigQuery tables, GCS buckets, partner batches).
- Volume required (training, validation, test).
- Ground truth: how labels are obtained, who labels, expected label quality.
- Data privacy / compliance considerations (LGPD if applicable).

### 8. Methods to Compare

- A **baseline** that any model must beat (often: classical features or rule-based).
- A **primary** method (the one you propose).
- Optional **alternatives** to ablate.
- For each method: a short description and what would make it the chosen approach.

### 9. Evaluation Plan

- Primary metric (with target numeric threshold).
- Secondary metrics.
- Evaluation set construction.
- Statistical significance plan (sample size needed, what test to run).
- Failure modes to inspect manually.

### 10. Phased Roadmap

- **Phase 1 — Offline validation**: deliverables, exit criteria.
- **Phase 2 — Controlled pilot** (optional): deliverables, exit criteria.
- **Phase 3 — Productionization**: gated by Phase 1/2 success; refers out to `SolutionArchitectureCrew`.

### 11. Risks & Mitigation

- Technical risks (e.g. false positives flagging legitimate signatures from family members).
- Data risks (sample bias, label noise, distribution shift).
- Business risks (compliance, partner relationships, false-accusation harm).
- For each risk: likelihood, impact, mitigation.

### 12. Integration Touchpoints

- Where in the existing pipeline this experiment would plug in (e.g. after `ocr-processors-service`, before `uploader-service`).
- What downstream systems are affected (e.g. new column expected in `raw_tea_image_analyzer.raw_tiss_guide_ocr` consumed by `workflows_v2/filters/athena.py`).
- This section is the bridge to `SolutionArchitectureCrew`.

### 13. Open Questions

- Numbered list of decisions the author **cannot resolve** with current information.
- Each question MUST name who/what would resolve it (e.g. "needs input from `@compras` team", "resolved after Phase 1 results").

### 14. Appendix: Source References

- Path/URL of every artefact and code reference used.
- Discovery artefact path.
- Repo paths.
- Notion pages, if any.

## Formatting conventions

- Markdown only. No HTML except for the idempotency markers used by `LinearSyncCrew`.
- Headings use `#`, `##`, `###` (do not nest deeper than `####`).
- Tables for any comparison of ≥ 3 dimensions.
- Mermaid diagrams encouraged for pipeline flow; not required.
- Numbers: use thousands separator in business contexts (R$ 12.600), no separator in technical contexts (200 epochs).
- Code blocks for file paths, env vars, commands.
