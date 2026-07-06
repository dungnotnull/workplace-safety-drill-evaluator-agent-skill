---
name: workplace-safety-drill-evaluator-sub-quality-reviewer
description: Devil's-advocate review of drill realism, scoring soundness, and gap-closure logic before the final report; emit the revised, validated final payload.
---

## Role
Stage 4 sub-skill of `workplace-safety-drill-evaluator`. Acts as the
**quality-gate / devil's-advocate stage**: it attacks the scoring payload before it
becomes the user-facing artifact, fixes unsound scores, and certifies the quality gates.

## Purpose
Devil's-advocate review of drill realism and gap closure; verify every gate; force
revision of any unjustified score or roadmap item before the final report.

## Inputs
- The validated payload from `sub-scoring-engine`
  (`scores`, `composite_index`, `roadmap`, `evidence_sources`, `limitations`).
- The stakeholder map + requirements payloads (for cross-checks).

## Procedure
1. **Inherit the scoring payload.** Re-run the gate checks defined in earlier stages.
2. **Realism audit.** For each dimension, ask:
   - Is the observed data consistent with the role map and occupancy?
   - Did participation justify the score (e.g., <50% turnout must cap Communication
     and Evacuation-effectiveness below 70 unless explicitly justified)?
   - Are there over-optimistic assumptions (e.g., "everyone evacuated" with low
     accountability)?
3. **Soundness audit.**
   - Recompute the composite index from `scoring_weights` × `scores`; if it differs
     from `composite_index` by >0.1, reject and correct.
   - Confirm every `score.citation` resolves to a real source (knowledge base entry
     or live URL/DOI). Flag any fabricated citation; downgrade confidence to low.
   - Confirm `roadmap` items are sorted by `impact × effort` descending.
4. **Devil's-advocate attacks.** Generate ≥3 specific attacks on the strongest scores
   and ≥3 on the weakest; for each, either rebut with cited evidence or revise the score
   and roadmap.
5. **Gate certification.** Run the harness-level Quality Gates checklist; record pass/fail
   per item. If any gate fails, revise and re-run (max 2 revisions before failing the run).
6. **Emit the final payload.** Include `revisions` log and the certified gate checklist.

## Output Schema (JSON; gate fails if any required key is missing)
```json
{
  "schema_version": "1.0",
  "stage": "sub-quality-reviewer",
  "inherited_from": "sub-scoring-engine",
  "revisions": [
    {"target":"score:regulatory_compliance|composite_index|roadmap[0]|...","change":"string","reason":"string"}
  ],
  "attacks": [
    {"attack":"string","target":"string","resolution":"rebutted|revised","evidence":"string|null"}
  ],
  "gate_checklist": {
    "framework_selection_justified":"pass|fail",
    "every_score_cited":"pass|fail",
    "roadmap_has_effort_impact_rationale":"pass|fail",
    "assumptions_confidence_limitations_stated":"pass|fail",
    "devils_advocate_completed":"pass|fail"
  },
  "final_scores": [
    {"dimension":"string","score":"0-100","justification":"string","citation":"string","confidence":"high|medium|low"}
  ],
  "final_composite_index": "number (1 dp)",
  "final_roadmap": [
    {"action":"string","dimension":"string","effort":"1-5","impact":"1-5","owner":"string","expected_effect":"string","rationale":"string"}
  ],
  "evidence_sources": [{"id":"string","title":"string","doi_or_url":"string","tier":"string"}],
  "assumptions": ["string"],
  "confidence": "high | medium | low",
  "limitations": ["string"]
}
```

## Quality Gate (certifies the whole harness)
- [ ] `gate_checklist` all items `pass`.
- [ ] ≥3 attacks generated and resolved (rebutted with evidence or revised).
- [ ] `final_composite_index` recomputed and matches to within 0.1.
- [ ] No fabricated citations (every citation resolves to a real source).
- [ ] If participation <50%, Communication & Evacuation-effectiveness capped below 70
  unless explicitly justified (recorded in `revisions`).
- [ ] `assumptions`, `confidence`, `limitations` stated.

## Tools
- `Read` — all prior payloads + `SECOND-KNOWLEDGE-BRAIN.md`.
- `WebSearch`/`WebFetch` — optional verification of citations.
- `Write` — optional artifact persistence.

## Hand-off
Emit the final payload. The harness main flow renders the user-facing artifact
(Summary, Scorecard, Detailed Analysis, Roadmap, Assumptions/Confidence/Limitations,
Sources) directly from this payload.
