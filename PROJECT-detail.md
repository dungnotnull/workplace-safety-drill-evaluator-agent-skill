# PROJECT-detail.md — Workplace Safety & Fire Drill Scenario Evaluator

## Executive Summary
`workplace-safety-drill-evaluator` is a Claude Skill that turns Claude into **an occupational health & safety auditor who evaluates drill scenarios against OSHA/NFPA and ISO 45001**. It ingests domain inputs, screens for safety/compliance where required, selects a world-renowned evaluation framework, gathers fresh evidence, scores the subject across 5 dimensions, and outputs a prioritized improvement roadmap. It is part of the **Business Operations & Strategy** cluster.

## Problem Statement
Employers run safety and fire drills but rarely evaluate them rigorously for compliance, response time, and effectiveness, leaving gaps that surface only in real emergencies.

Domain context: practitioners need reproducible, evidence-graded evaluation rather than ad-hoc opinion. This skill enforces a research-first harness with explicit quality gates and a self-improving knowledge base.

## Target Users & Use Cases
- Primary: practitioners, learners, and decision-makers in this domain.
- Trigger examples:
1. **Office tower fire drill** — 12-floor building, 6-min evacuation. Expect NFPA/OSHA scoring and bottleneck roadmap.
2. **Factory chemical-spill drill** — Hazmat scenario. Expect OSHA HAZWOPER alignment and ERT role review.
3. **Healthcare facility evacuation** — Non-ambulatory patients. Expect defend-in-place vs evacuate analysis and staffing gaps.
4. **Drill with poor turnout** — Low participation. Expect quality-reviewer to flag realism and propose fixes.
5. **ISO 45001 audit prep** — Company wants certification readiness. Expect management-system gap assessment.

## Harness Architecture
```
/workplace-safety-drill-evaluator  (main.md)
   |
   v
[1] sub-stakeholder-mapper        -> structured intake
   |
   v
[2] framework selection  -> choose named framework
   |
   v
[3] research (WebSearch/WebFetch)        -> evidence (graceful deg: SECOND-KNOWLEDGE-BRAIN.md)
   |
   v
[4] scoring engine                       -> 0-100 multi-dimensional score
   |
   v
[5] improvement roadmap                  -> effort x impact prioritized actions
   |
   v
[6] quality-gate / devil's advocate      -> final professional artifact
```

## Full Sub-Skill Catalog
#### `sub-stakeholder-mapper`
- **Purpose:** Map roles (wardens, first-aiders, evacuees, ERT) and responsibilities in the drill.
- **Inputs:** structured outputs from prior stage + user-supplied data
- **Outputs:** validated, structured payload for the next stage
- **Tools:** Read, Write
- **Quality gate:** output schema validated before proceeding

#### `sub-requirements-gatherer`
- **Purpose:** Capture facility type, hazards, regulatory jurisdiction, and drill objectives.
- **Inputs:** structured outputs from prior stage + user-supplied data
- **Outputs:** validated, structured payload for the next stage
- **Tools:** Read, Write
- **Quality gate:** output schema validated before proceeding

#### `sub-scoring-engine`
- **Purpose:** Score compliance, response time, communication, and evacuation effectiveness against OSHA/NFPA/ISO 45001.
- **Inputs:** structured outputs from prior stage + user-supplied data
- **Outputs:** validated, structured payload for the next stage
- **Tools:** Read, Write, WebSearch/WebFetch
- **Quality gate:** output schema validated before proceeding

#### `sub-quality-reviewer`
- **Purpose:** Devil's-advocate review of drill realism and gap closure before final report.
- **Inputs:** structured outputs from prior stage + user-supplied data
- **Outputs:** validated, structured payload for the next stage
- **Tools:** Read, Write
- **Quality gate:** output schema validated before proceeding


## Evaluation Frameworks (world-renowned, citable)
- OSHA 1910.38/.157 (emergency action & fire)
- NFPA 101 Life Safety Code & NFPA 1600
- ISO 45001 OH&S management
- Emergency response time & evacuation modeling
- Root-cause / HFACS for drill failures
- PDCA continuous improvement

## Scoring Model
| Dimension | Range | Notes |
|-----------|-------|-------|
| Regulatory compliance | 0–100 | Weighted contribution to the composite index |
| Response time | 0–100 | Weighted contribution to the composite index |
| Communication | 0–100 | Weighted contribution to the composite index |
| Evacuation effectiveness | 0–100 | Weighted contribution to the composite index |
| Gap closure | 0–100 | Weighted contribution to the composite index |

Composite = weighted mean of dimensions (weights justified per case, surfaced to the user). Every dimension score must cite at least one framework criterion or evidence source.

## Skill File Format Specification
Frontmatter: `name`, `description`. Required sections in `main.md`: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates.

## E2E Execution Flow
1. Parse user request; if inputs missing, run intake questions.
2. Select framework based on subject characteristics.
3. Gather evidence (prefer Systematic Review > Meta-analysis > RCT/empirical > expert opinion).
4. Score each dimension with cited justification.
5. Build prioritized roadmap.
6. Run devil's-advocate quality gate; revise; present artifact.
- Error handling: missing data → state assumptions + confidence; tool failure → degrade to knowledge base and signal limitation.

## SECOND-KNOWLEDGE-BRAIN Integration
- Sources: OSHA standards & letters of interpretation, NFPA codes & research, ISO 45001 guidance, Safety Science (Elsevier).
- Crawl queries: evacuation drill effectiveness metrics, OSHA emergency action plan compliance, ISO 45001 audit findings, fire drill response time benchmark.
- Append format: dated entries with Title, Authors, Year, Venue, DOI/URL, key finding, relevance.

## Supporting Tools Spec — `knowledge_updater.py`
- Inputs: source list + query list (above), `--since` date.
- Outputs: appended, de-duplicated entries in `SECOND-KNOWLEDGE-BRAIN.md`.
- Schedule: weekly cron.

## Quality Gates (must be true before final output)
- [ ] Framework selection justified
- [ ] Every score cites a framework criterion or evidence source
- [ ] Roadmap items have effort + impact + owner
- [ ] Assumptions and confidence stated; limitations disclosed
- [ ] Devil's-advocate pass completed

## Test Scenarios (≥5)
1. **Office tower fire drill** — 12-floor building, 6-min evacuation. Expect NFPA/OSHA scoring and bottleneck roadmap.
2. **Factory chemical-spill drill** — Hazmat scenario. Expect OSHA HAZWOPER alignment and ERT role review.
3. **Healthcare facility evacuation** — Non-ambulatory patients. Expect defend-in-place vs evacuate analysis and staffing gaps.
4. **Drill with poor turnout** — Low participation. Expect quality-reviewer to flag realism and propose fixes.
5. **ISO 45001 audit prep** — Company wants certification readiness. Expect management-system gap assessment.

## Key Design Decisions
1. Research-first; no memory-only claims when search is possible.
2. Named frameworks only — never ad hoc criteria.
3. Framework-selector adapts to subject; no one-size scoring.
4. Multi-dimensional score + prioritized roadmap are mandatory outputs.
5. Self-improving knowledge base via weekly crawl.
