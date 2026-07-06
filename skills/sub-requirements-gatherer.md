---
name: workplace-safety-drill-evaluator-sub-requirements-gatherer
description: Capture facility hazards, regulatory jurisdiction, drill objectives, and the evaluation framework(s); produce the validated requirements payload that frames the scoring.
---

## Role
Stage 2 sub-skill of `workplace-safety-drill-evaluator`. Acts as the
**framework-selection stage**: it turns the stakeholder map into an explicit,
justified evaluation framework choice plus the requirement set scored later.

## Purpose
Capture facility type, hazards, regulatory jurisdiction, drill objectives, and
select the named world-renowned framework(s) used for scoring.

## Inputs
- The validated payload from `sub-stakeholder-mapper` (facility, drill, roles).
- `SECOND-KNOWLEDGE-BRAIN.md` for framework definitions.
- Optional live evidence via `WebSearch`/`WebFetch` (degrade to knowledge base if
  unavailable and record the limitation).

## Procedure
1. **Inherit the stakeholder payload** and confirm `facility`, `drill.type`,
   `drill.objectives` are non-empty.
2. **Enumerate hazards.** Derive hazard classes from facility type + drill type:
   - office/high-rise → smoke, egress congestion, stairwell capacity.
   - factory/hazmat → chemical release, HAZWOPER exposure, decon.
   - healthcare → non-ambulatory patients, defend-in-place vs evacuate.
3. **Select the evaluation framework(s)** using the decision rule below. Always
   cite the framework by canonical identifier.
4. **Define measurable requirements.** Translate each chosen framework into concrete
   pass/fail or benchmark criteria (e.g., NFPA 101 egress capacity, OSHA 1910.38
   accountability, RSET < ASET).
5. **Set scoring weights.** Justify dimension weights for this case (default equal,
   but raise Response-time weight for high-rise evacuations, Regulatory-compliance
   weight for hazmat). Weights must sum to 1.0 and be surfaced to the user.
6. **Record assumptions and confidence.**

## Framework Selection Decision Rule
| Drill type | Primary framework | Secondary framework |
|------------|-------------------|---------------------|
| fire-evacuation | NFPA 101 Life Safety Code | OSHA 29 CFR 1910.38 |
| hazmat-spill | OSHA 29 CFR 1910.120 (HAZWOPER) | NFPA 1600 |
| shelter-in-place | NFPA 101 (defend-in-place) | OSHA 1910.38 |
| active-threat | NFPA 1600 / FEMA Active Shooter | ISO 45001 |
| medical | ISO 45001 / NFPA 1600 | OSHA 1910.38 |
| combined | ISO 45001 (program) + NFPA 101 (egress) | OSHA 1910.38/.120 |
| certification prep (any) | ISO 45001:2018 | NFPA 1600 |

Every framework must be cited by canonical identifier; never use an ad-hoc rubric.

## Output Schema (JSON; gate fails if any required key is missing)
```json
{
  "schema_version": "1.0",
  "stage": "sub-requirements-gatherer",
  "inherited_from": "sub-stakeholder-mapper",
  "hazards": [{"class":"string","description":"string","severity":"low|med|high|severe"}],
  "jurisdiction": "string",
  "frameworks": [
    {"name":"string (canonical id)","role":"primary|secondary","justification":"string","citation":"string"}
  ],
  "requirements": [
    {"id":"R1","dimension":"regulatory_compliance|response_time|communication|evacuation_effectiveness|gap_closure","criterion":"string","framework_ref":"string","pass_condition":"string","benchmark":"number|null"}
  ],
  "scoring_weights": {
    "regulatory_compliance":"0-1",
    "response_time":"0-1",
    "communication":"0-1",
    "evacuation_effectiveness":"0-1",
    "gap_closure":"0-1"
  },
  "assumptions": ["string"],
  "confidence": "high | medium | low",
  "limitations": ["string (e.g., WebSearch unavailable, used knowledge base)"]
}
```

## Quality Gate
- [ ] `frameworks` non-empty; each carries `justification` + `citation`.
- [ ] `requirements` cover all 5 scoring dimensions with at least one criterion each.
- [ ] `scoring_weights` sum to 1.0 (validate to within ±0.001).
- [ ] Hazards derived from facility + drill type, not invented.
- [ ] `assumptions`, `confidence`, `limitations` stated.
- [ ] If `WebSearch`/`WebFetch` failed, `limitations` records it and evidence was
  drawn from `SECOND-KNOWLEDGE-BRAIN.md`.

## Tools
- `Read` — `SECOND-KNOWLEDGE-BRAIN.md`, prior payload.
- `WebSearch`/`WebFetch` — optional live evidence (graceful degradation enforced).
- `Write` — optional artifact persistence.

## Hand-off
Emit the validated payload. The next stage (`sub-scoring-engine`) consumes
`frameworks`, `requirements`, and `scoring_weights`.
