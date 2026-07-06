# tests/test-scenarios.md — Workplace Safety & Fire Drill Scenario Evaluator

These scenarios validate the `workplace-safety-drill-evaluator` harness end-to-end
and exercise the quality gates. Each scenario lists the input, the framework(s)
expected, the gate behaviour (including blocking/revision cases), and the pass
criteria. Programmatic checks are delegated to `tools/validate_harness.py`; the
fixtures in `tests/fixtures/` give worked examples of valid stage payloads.

Automation: run `python -m pytest tests/ tools/ -q` to execute the offline test
suite (validator schema/gate tests + crawler unit tests). No network or live model
run is required for the offline suite; live end-to-end runs require WebSearch/WebFetch
and are documented per scenario but not executed in the "prepare for real run" stage.

---

## Functional scenarios (the 5 canonical cases)

### Scenario 1 — Office tower fire drill
- **Input:** 12-floor building, ~600 occupants, 6-min evacuation, voice+horn+wardens,
  88% accountability.
- **Expected framework:** primary NFPA 101 Life Safety Code; secondary OSHA 29 CFR
  1910.38; ISO 45001 §10 for gap closure.
- **Expected behaviour:** intake asks for nothing missing; weights raised on
  Response-time (0.30) and Evacuation-effectiveness (0.25); roadmap prioritises
  stairwell-capacity / phased evacuation and HFACS gap tracking.
- **Gate behaviour:** all gates `pass`; devil's-advocate revises evacuation
  effectiveness down from a naive high (88% < 95% benchmark) and gap-closure to ~55
  (no closure cycle).
- **Pass criteria:** every score cites a framework/source; assumptions + limitations
  stated; composite recomputed and matches.
- **Fixture:** `tests/fixtures/stage{1..4}_*.json` model this scenario.

### Scenario 2 — Factory chemical-spill drill
- **Input:** hazmat release, ERT response, decon line, no HAZWOPER training records.
- **Expected framework:** primary OSHA 29 CFR 1910.120 (HAZWOPER); secondary NFPA 1600.
- **Expected behaviour:** Regulatory-compliance weight raised; scoring rubric applies
  HAZWOPER training-lapse non-conformance; roadmap adds 8-hour refresher and decon
  drill cadence.
- **Gate behaviour:** Regulatory-compliance cited to 1910.120; missing ERT roles
  surface in `missing_roles`; quality-reviewer attacks the decon time and revises if
  unsupported.
- **Pass criteria:** HAZWOPER citation present; ERT role review in roles map.

### Scenario 3 — Healthcare facility evacuation
- **Input:** non-ambulatory patients, 6-floor hospital, defend-in-place vs evacuate.
- **Expected framework:** primary NFPA 101 (defend-in-place) + NFPA 1660; secondary
  ISO 45001.
- **Expected behaviour:** defend-in-place vs total-evacuation analysis in Detailed
  Analysis; staffing-gap finding on patient-transport roles; Communication weight
  raised (vertical-warden cascade).
- **Gate behaviour:** quality-reviewer confirms defend-in-place justification cites
  NFPA 101; flags staffing gap as roadmap priority 1.
- **Pass criteria:** defend-in-place analysis cited; staffing gap in roadmap with owner.

### Scenario 4 — Drill with poor turnout
- **Input:** participation_rate_pct = 38, otherwise plausible 4-min evacuation.
- **Expected behaviour:** quality-reviewer caps Communication AND
  Evacuation-effectiveness below 70 unless explicitly justified, and records the
  cap in `revisions`. Composite drops accordingly; realism flagged in limitations.
- **Gate behaviour:** if a downstream stage leaves those two scores ≥70 without
  justification, the quality gate FAILS and forces a revision.
- **Pass criteria:** the low-participation cap rule is evident in `revisions`;
  limitations disclose low turnout.

### Scenario 5 — ISO 45001 audit prep
- **Input:** company wants certification readiness; no drill, management-system review.
- **Expected framework:** primary ISO 45001:2018; secondary NFPA 1600.
- **Expected behaviour:** Gap-closure weight raised; scoring focuses on §4–§10 clauses
  (context, leadership, planning, support, operation, performance evaluation,
  improvement); roadmap maps each non-conformance to a clause + PDCA stage.
- **Gate behaviour:** every Gap-closure citation references an ISO 45001 clause id.
- **Pass criteria:** management-system gap assessment with clause-level citations.

---

## Gate-firing / blocking & edge scenarios (regression)

### Scenario 6 — Missing essentials block intake
- **Input:** "evaluate our drill" (no facility, drill type, occupancy, jurisdiction).
- **Expected behaviour:** `sub-stakeholder-mapper` asks targeted questions (max 3
  rounds); it must NOT fabricate facility/drill type.
- **Gate behaviour:** intake quality gate fails until required fields are supplied.
- **Pass criteria:** no silent assumption of facility type or jurisdiction.

### Scenario 7 — WebSearch/WebFetch unavailable (graceful degradation)
- **Input:** Scenario 1 inputs but with tools unavailable.
- **Expected behaviour:** `sub-scoring-engine` reads `SECOND-KNOWLEDGE-BRAIN.md` §2,
  cites those entries, and records the limitation in `limitations[]`; confidence set
  to medium/low.
- **Gate behaviour:** artifact still ships; limitation disclosed to the user.
- **Pass criteria:** `limitations` mentions the fallback; every citation resolves
  to a knowledge-base entry.

### Scenario 8 — Fabricated citation caught
- **Input:** a downstream attempt to cite a non-existent DOI.
- **Expected behaviour:** `sub-quality-reviewer` flags the citation as unresolved,
  downgrades confidence to low, and revises the score (records in `revisions`).
- **Gate behaviour:** gate `every_score_cited` would fail only if the citation is
  removed entirely; here it triggers a revision instead.
- **Pass criteria:** confidence downgraded; revision logged.

### Scenario 9 — Composite mismatch rejected
- **Input:** scoring payload where `composite_index` ≠ weighted mean of scores.
- **Expected behaviour:** `sub-quality-reviewer` recomputes and corrects; if the
  mismatch persists after 2 revisions, the run fails the gate.
- **Pass criteria:** final composite matches recomputed value to within 0.1.

### Scenario 10 — Weights do not sum to 1.0
- **Input:** requirements payload with weights summing to 0.9.
- **Expected behaviour:** `validate_harness.py` (and the documented gate) reject;
  `sub-requirements-gatherer` must normalise or refuse.
- **Pass criteria:** validator returns non-zero with "sum to" message
  (covered by `test_weights_must_sum_to_one`).

### Scenario 11 — Score out of range
- **Input:** a dimension score of 120.
- **Expected behaviour:** validator rejects ("out of 0-100").
- **Pass criteria:** covered by `test_score_out_of_range_fails`.

### Scenario 12 — Fewer than 3 devil's-advocate attacks
- **Input:** quality-reviewer payload with only 1 attack.
- **Expected behaviour:** validator rejects ("must produce >=3 attacks").
- **Pass criteria:** validator returns non-zero.

### Scenario 13 — Combined drill (fire + hazmat)
- **Input:** office + chemical storage; both evacuation and hazmat response.
- **Expected framework:** ISO 45001 (program) + NFPA 101 (egress) + OSHA 1910.38/.120.
- **Expected behaviour:** weights split across Regulatory-compliance and
  Evacuation-effectiveness; roadmap covers both egress and HAZWOPER gaps.
- **Pass criteria:** both OSHA 1910.120 and NFPA 101 cited.

### Scenario 14 — Unknown jurisdiction (non-US)
- **Input:** EU facility, ISO 45001 only.
- **Expected behaviour:** framework selection drops OSHA, keeps ISO 45001 + local
  equivalents; limitations note jurisdictional variance.
- **Pass criteria:** jurisdiction recorded; OSHA not cited for non-US subject.

---

## Regression Checklist (run after any edit)
- [ ] `python -m pytest tests/ tools/ -q` passes (offline suite).
- [ ] Framework selection always justified (gate `framework_selection_justified`).
- [ ] Scorecard includes all 5 dimensions exactly once.
- [ ] Every score carries a citation that resolves to a real source.
- [ ] Roadmap items carry effort + impact + owner + expected_effect + rationale.
- [ ] Weights sum to 1.0 (validated to ±0.001).
- [ ] Low-participation (<50%) caps Communication & Evacuation-effectiveness <70
      unless justified (recorded in `revisions`).
- [ ] Graceful degradation recorded in `limitations` when tools unavailable.
- [ ] Sources section lists every citation with DOI/URL and evidence tier.
- [ ] Composite recomputed and matches to within 0.1.
- [ ] Cross-skill references valid (see `CROSS-SKILL-INTERFACE.md`).
