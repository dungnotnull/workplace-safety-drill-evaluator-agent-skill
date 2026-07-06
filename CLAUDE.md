# CLAUDE.md — Workplace Safety & Fire Drill Scenario Evaluator (idea 120)

## Skill Identity
- **Name / slug:** `workplace-safety-drill-evaluator`
- **Tagline:** Workplace Safety & Fire Drill Scenario Evaluator
- **Source idea:** #120 (`ideas.md`)
- **Cluster:** Business Operations & Strategy (`business-operations`)
- **Current phase:** All phases (0–5) complete — production-grade, ready for real run.

## Problem This Skill Solves
Employers run safety and fire drills but rarely evaluate them rigorously for
compliance, response time, and effectiveness, leaving gaps that surface only in real
emergencies.

This skill becomes **an occupational health & safety auditor who evaluates drill
scenarios against OSHA/NFPA and ISO 45001**. It is research-first, grounds every
score in named world-renowned frameworks, challenges its own assumptions before
concluding, and produces a professional artifact: a 5-dimension 0–100 score plus a
prioritized improvement roadmap.

## Harness Flow Summary
1. **Intake** → `sub-stakeholder-mapper` gathers structured inputs (RACI roles, missing roles).
2. **Framework** → `sub-requirements-gatherer` selects named framework(s), defines requirements, sets weights (sum=1.0).
3. **Evidence + scoring** → `sub-scoring-engine` gathers evidence (WebSearch/WebFetch, graceful degradation to `SECOND-KNOWLEDGE-BRAIN.md`), scores 0–100 across 5 dimensions, builds the effort × impact roadmap.
4. **Quality gate** → `sub-quality-reviewer` devil's-advocates, recomputes composite, caps Communication/Evacuation-effectiveness <70 when participation <50%, certifies the gate checklist.
5. **Artifact** → Summary, Scorecard, Detailed Analysis, Roadmap, Assumptions/Confidence/Limitations, Sources.

_No hard safety/compliance gate; standard quality gates apply._

## Sub-skills
- `skills/sub-stakeholder-mapper.md` — Map roles (wardens, first-aiders, evacuees, ERT) and responsibilities in the drill.
- `skills/sub-requirements-gatherer.md` — Capture facility type, hazards, regulatory jurisdiction, drill objectives; select framework(s); set weights.
- `skills/sub-scoring-engine.md` — Score 5 dimensions against OSHA/NFPA/ISO 45001 with cited justifications; emit composite + roadmap.
- `skills/sub-quality-reviewer.md` — Devil's-advocate review; recompute composite; certify gates.

## Evaluation Frameworks
OSHA 29 CFR 1910.38/.157/.120, NFPA 101 / 1600 / 1660, ISO 45001:2018, evacuation
modelling (RSET/ASET, SFPE, NIST TN 1689), HFACS, PDCA.

## Scoring Model
Composite = Σ(scoreᵢ × weightᵢ) over Regulatory compliance (0.20), Response time
(0.25), Communication (0.20), Evacuation effectiveness (0.25), Gap closure (0.10);
weights tuned per case and surfaced to the user. Every score cites ≥1 framework
criterion or evidence source.

## Tools Required
- `WebSearch`, `WebFetch` — live evidence gathering (graceful degradation enforced).
- `Read`, `Write` — artifact production.
- `Bash`/`python` — `tools/knowledge_updater.py` and `tools/validate_harness.py`.

## Supporting Tools
- `tools/knowledge_updater.py` — async Crossref/arXiv/Semantic Scholar pipeline (+ optional crawl4ai) that grows `SECOND-KNOWLEDGE-BRAIN.md` (weekly cron recommended). Config: `tools/knowledge_updater.toml`.
- `tools/validate_harness.py` — schema + quality-gate validator for stage payloads (cluster-wide validation hook).
- `tools/tests/`, `tests/` — offline test suites + fixtures.

## Knowledge Sources (crawl targets)
OSHA standards & letters of interpretation, NFPA codes & research, ISO 45001 guidance,
Safety Science (Elsevier), Crossref, arXiv, Semantic Scholar.

## Active Development Tasks
- [x] Scaffold all required deliverables
- [x] Author main harness + 4 differentiated sub-skills with JSON schemas + rubrics
- [x] Define scoring dimensions with citable anchors
- [x] Production-grade `knowledge_updater.py` (real APIs) + config + tests + README
- [x] `validate_harness.py` + fixtures + offline test suite
- [x] Seed `SECOND-KNOWLEDGE-BRAIN.md` with real citable references
- [x] 14 test scenarios (5 canonical + 9 gate/edge), with blocking cases
- [x] Cross-skill wiring (`CROSS-SKILL-INTERFACE.md` + main.md section)
- [ ] First live crawl (deferred to production run to conserve resources)
- [ ] Live end-to-end WebSearch/WebFetch runs (deferred to production run)

## Related Root Docs
- `PROJECT-detail.md` — full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap (all phases DONE)
- `SECOND-KNOWLEDGE-BRAIN.md` — living knowledge base (seeded with real references)
- `CROSS-SKILL-INTERFACE.md` — cluster reuse contract
