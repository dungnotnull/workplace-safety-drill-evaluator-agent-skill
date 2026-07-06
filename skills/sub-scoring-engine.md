---
name: workplace-safety-drill-evaluator-sub-scoring-engine
description: Score the drill across the 5 dimensions against OSHA/NFPA/ISO 45001 with cited justifications and produce the composite index plus the prioritized improvement roadmap.
---

## Role
Stage 3 sub-skill of `workplace-safety-drill-evaluator`. Acts as the
**scoring stage**: it converts the requirements payload into a 0–100 scorecard and a
prioritized roadmap, with every score cited to a framework criterion or evidence source.

## Purpose
Score compliance, response time, communication, and evacuation effectiveness against
OSHA/NFPA/ISO 45001; emit the composite index, per-dimension justification, and the
effort × impact roadmap.

## Inputs
- The validated payload from `sub-requirements-gatherer`
  (`frameworks`, `requirements`, `scoring_weights`).
- The stakeholder map from `sub-stakeholder-mapper` (for `missing_roles`).
- Optional live evidence via `WebSearch`/`WebFetch` (degrade to knowledge base,
  record in `limitations`).

## Procedure
1. **Inherit the requirements payload.** Confirm all 5 dimensions have ≥1
   `requirements[].criterion`.
2. **Gather evidence.** For each dimension, run `WebSearch`/`WebFetch` against the
   authoritative sources in `SECOND-KNOWLEDGE-BRAIN.md` (OSHA eCFR, NFPA, ISO 45001,
   Safety Science). Prefer Systematic Review > Meta-Analysis > RCT > Cohort > Guideline
   > Expert opinion. If tools unavailable, read `SECOND-KNOWLEDGE-BRAIN.md` §2 and cite
   those entries; record the limitation.
3. **Score each dimension 0–100.** Use the rubric below. Each dimension score MUST cite
   at least one framework criterion or evidence source (URL/DOI/standard id).
4. **Composite index.** Weighted mean of the 5 dimension scores using
   `scoring_weights` from the prior stage. Round to 1 decimal.
5. **Top findings.** Extract the 3 highest-impact positive and 3 negative findings.
6. **Build the roadmap.** For each gap, propose an action with `effort` (1–5),
   `impact` (1–5), `owner` (role), and `expected_effect` (quantified where possible).
   Sort by `impact × effort` descending (impact-first), then by `effort` ascending.
7. **State assumptions, confidence, limitations.** Confidence bands:
   high (≥3 cited empirical/standard sources), medium (1–2 sources), low (opinion only).

## Dimension Rubrics (anchor points; interpolate)
### Regulatory compliance (0–100)
- 90–100: EAP, training records, extinguisher program all documented & current; full
  OSHA 1910.38 / .157 / .120 alignment.
- 70–89: minor documentation gaps; no critical non-conformances.
- 50–69: missing EAP element or expired training (e.g., accountability absent).
- <50: no EAP, required training lapsed, or HAZWOPER gap for hazmat drills.
Citation must be the specific standard id (e.g., 29 CFR 1910.38(d)).

### Response time (0–100) — use RSET/ASET
- 90–100: observed RSET < ASET with ≥30% margin; recognition + movement both within
  SFPE/Human Behavior in Fire guidance for the occupancy.
- 70–89: RSET < ASET but margin < 30%.
- 50–69: RSET ≈ ASET or one phase (e.g., pre-movement) exceeds benchmark.
- <50: RSET ≥ ASET or evacuation incomplete. Cite NIST TN 1689 or Lovreglio et al. 2020.

### Communication (0–100)
- 90–100: alarm + voice + warden cascade all present, tested, and acknowledged;
  NFPA 1600 §5 comms.
- 70–89: two channels work, one weak (e.g., no voice instruction).
- 50–69: single channel, partial coverage.
- <50: alarm-only, ambiguous signal, or warden cascade failed.

### Evacuation effectiveness (0–100)
- 90–100: ≥95% accounted at assembly within target; egress capacity per NFPA 101;
  bottlenecks identified and within design limits.
- 70–89: 85–95% accounted; minor congestion.
- 50–69: 70–85% accounted OR a single bottleneck exceeded design capacity.
- <50: <70% accounted or evacuation abandoned. Cite NFPA 101 / NFPA 1660.

### Gap closure (0–100) — PDCA / ISO 45001 §10
- 90–100: prior gaps documented, root-caused (HFACS), assigned owners, closed & verified.
- 70–89: gaps tracked but closure partial.
- 50–69: gaps logged, no closure cycle.
- <50: no gap tracking. Cite ISO 45001:2018 §9/§10 and HFACS (Wiegmann & Shappell 2003).

## Output Schema (JSON; gate fails if any required key is missing)
```json
{
  "schema_version": "1.0",
  "stage": "sub-scoring-engine",
  "inherited_from": "sub-requirements-gatherer",
  "evidence_sources": [{"id":"string","title":"string","doi_or_url":"string","tier":"systematic_review|meta_analysis|rct|cohort|guideline|expert_opinion"}],
  "scores": [
    {"dimension":"regulatory_compliance","score":"0-100","justification":"string","citation":"string","confidence":"high|medium|low"}
  ],
  "composite_index": "number (1 dp)",
  "top_findings": {"positives":["string"],"negatives":["string"]},
  "roadmap": [
    {"action":"string","dimension":"string","effort":"1-5","impact":"1-5","owner":"string","expected_effect":"string","rationale":"string"}
  ],
  "assumptions": ["string"],
  "confidence": "high | medium | low",
  "limitations": ["string"]
}
```

## Quality Gate
- [ ] Exactly 5 dimension entries in `scores`, each 0–100 with a non-empty `citation`.
- [ ] `composite_index` equals weighted mean (recompute; reject if mismatch > 0.1).
- [ ] `roadmap` non-empty; each item has `effort`, `impact`, `owner`, `expected_effect`.
- [ ] Every score cites a framework criterion or evidence source (DOI/URL/standard id).
- [ ] `evidence_sources` listed with evidence tier; tier reflects the hierarchy.
- [ ] `assumptions`, `confidence`, `limitations` stated.
- [ ] If `WebSearch`/`WebFetch` failed, `limitations` records it and `evidence_sources`
  come from `SECOND-KNOWLEDGE-BRAIN.md`.

## Tools
- `Read` — knowledge base + prior payloads.
- `WebSearch`/`WebFetch` — live evidence (graceful degradation).
- `Write` — optional artifact persistence.

## Hand-off
Emit the validated payload. The next stage (`sub-quality-reviewer`) runs the
devil's-advocate pass over `scores`, `composite_index`, and `roadmap`.
