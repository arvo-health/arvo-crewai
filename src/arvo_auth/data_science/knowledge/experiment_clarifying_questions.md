# Experiment — Phase 0 Clarifying Questions

This is the **canonical question checklist** that must be answered **before** running
`run_ds_experiment_spec`. It is an official step of the DS experiment process — not
optional, not ad-hoc.

**Status:** currently answered **manually** (a human fills the answers, or Claude asks
them interactively in a Claude Code session). It will be automated by a
`question_designer` agent once the process is mature enough to hand to teammates.

## How to use

1. Copy this file (or answer inline) and fill an answer under each question. `(unknown)`
   is a valid answer — it tells the experiment designer where the gaps are.
2. Put the answered version into `ARVO_DS_BRIEFING_MARKDOWN` (inline) or a file you
   reference there.
3. Run `uv run run_ds_experiment_spec`. The designer treats these answers as
   constraints, not suggestions.

Answer the **must** questions always; the **nice** ones improve the spec but can be
`(unknown)`.

---

## 1. Data availability  *(the recurring bottleneck — answer honestly)*

- **(must)** How much *labelled* data realistically exists for this task **today**? Give a
  number or range, not an aspiration.
- **(must)** Is there ground truth? If so, who/what produced the labels and how trustworthy
  are they?
- **(nice)** Can more labelled data be obtained? At what cost / time / who does it?
- **(nice)** What relevant data already flows through production that we could tap without
  new collection (BigQuery tables, GCS buckets, pipeline outputs)?

## 2. Approach & stack  *(stack-first principle)*

- **(must)** Any reason the first method should NOT reuse the existing production stack
  (Gemini/VLM prompting, mirroring `doc-extractor`)? Default is: it should.
- **(nice)** Is there an existing Arvo service or model that already does part of this?
- **(nice)** Any hard constraints on tools/frameworks (must use X, cannot use Y)?

## 3. Scope

- **(must)** Is the goal offline validation only, or already aiming at production
  integration?
- **(must)** Which partners / clinics / document types are in scope for this experiment?
- **(nice)** One-shot analysis, or a recurring pipeline that must run on every batch?

## 4. Success definition

- **(must)** What does "good enough" mean to the stakeholder? A concrete number if
  possible (precision target, recall, R$ saving, etc.).
- **(must)** What is the cost asymmetry — is a false positive or a false negative worse in
  this domain, and by how much?
- **(nice)** Who decides go/no-go after the offline validation?

## 5. Constraints

- **(nice)** Timeline or deadline?
- **(must)** Compliance constraints (LGPD, ANS rules) that bound data handling or method?
- **(must)** Infra budget — can we stand up new services, or must we reuse existing
  infrastructure only?

## 6. Prior art & context

- **(must)** Was a POC already done? By whom, with what tool, and what was the result?
- **(nice)** Any related work in other teams we should not duplicate?
