# CROSS-SKILL-INTERFACE.md — Business Operations & Strategy cluster

> Shared interface contract so sibling skills in the **Business Operations &
> Strategy** cluster can reuse the sub-skills of `workplace-safety-drill-evaluator`
> (and vice-versa) without divergence. This is the Phase 5 cross-skill wiring
> document.

## 1. Cluster
`business-operations` — skills that evaluate operational subjects against named
world-renowned frameworks and emit a multi-dimensional 0–100 score + prioritized
roadmap.

## 2. Shared sub-skill catalogue (reusable across the cluster)
All four sub-skills are written generically enough to be reused. Sibling skills
reference them by canonical `name` frontmatter and reuse `schema_version: "1.0"` so
artifacts stay comparable.

| Canonical name | Role | Reusable as | Schema anchor |
|----------------|------|-------------|---------------|
| `workplace-safety-drill-evaluator-sub-stakeholder-mapper` | generic role/RACI intake | intake stage | `stage = "sub-stakeholder-mapper"` |
| `workplace-safety-drill-evaluator-sub-requirements-gatherer` | generic framework-selection intake | framework stage | `stage = "sub-requirements-gatherer"` |
| `workplace-safety-drill-evaluator-sub-scoring-engine` | generic 0–100 weighted-composite scorer + roadmap | scoring stage | `stage = "sub-scoring-engine"` |
| `workplace-safety-drill-evaluator-sub-quality-reviewer` | generic devil's-advocate gate | quality gate stage | `stage = "sub-quality-reviewer"` |

Sibling skills that only need a subset (e.g., reuse just the scoring engine) SHOULD
override the per-dimension rubrics and frameworks while keeping the JSON schema and
the 0–100 / weighted-composite convention intact.

## 3. Aligned scoring scale (cluster-wide contract)
- **Range:** every dimension 0–100; composite = Σ(scoreᵢ × weightᵢ), weights ≥0,
  sum = 1.0 (validated to ±0.001 by `tools/validate_harness.py`).
- **Confidence bands:** high (≥3 cited empirical/standard sources), medium (1–2),
  low (opinion only).
- **Evidence hierarchy:** Systematic Review > Meta-Analysis > RCT/Empirical >
  Cohort/Case > Guideline/Standard > Expert opinion > Blog.
- **Output sections (cluster-wide):** Summary, Scorecard, Detailed Analysis,
  Improvement Roadmap, Assumptions/Confidence/Limitations, Sources.
- **Quality gates (cluster-wide):** framework justified; every score cited;
  roadmap has effort+impact+owner+rationale; assumptions/confidence/limitations
  stated; devil's-advocate completed; composite recomputed.

## 4. Reuse rules for sibling skills
1. Reference the sub-skill by its canonical `name` (do not copy-prose-duplicate).
2. Keep `schema_version: "1.0"` payloads; the validator enforces the contract.
3. Replace the framework list and rubric anchors to fit the sibling domain, but
   keep the 5-dimension / weighted-composite / 0–100 shape (or extend with new
   dimensions using the same conventions, recording the change in this file).
4. Route payloads through `tools/validate_harness.py` in the sibling's CI.
5. Share the knowledge-base convention (`SECOND-KNOWLEDGE-BRAIN.md` shape) but keep
   each skill's knowledge base file distinct.

## 5. Known divergences from siblings (to be reconciled)
- None at this build. Sibling skills adopting the 0–100 / weighted-composite
  convention should record any deviation (e.g., different default weights) here.

## 6. Validation
Reuse `tools/validate_harness.py` for any cluster skill whose payloads follow
`schema_version: "1.0"` and the stages above. Run:
```
python tools/validate_harness.py path/to/*.json
```
