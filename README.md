# Workplace Safety & Fire Drill Scenario Evaluator

> A Claude Skill that turns Claude into an occupational health & safety auditor
> who evaluates workplace and fire drill scenarios against OSHA, NFPA, and
> ISO 45001, then outputs a multi-dimensional score plus a prioritized
> improvement roadmap. Research-first, evidence-graded, self-challenging,
> and self-improving.

[![Tests](https://img.shields.io/badge/tests-22%20passing-brightgreen)](#testing)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](#requirements)
[![License](https://img.shields.io/badge/license-MIT-green)](#license)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)](#status)

---

## Table of Contents

1. [What this skill does](#what-this-skill-does)
2. [Why it exists](#why-it-exists)
3. [Architecture](#architecture)
4. [The harness flow](#the-harness-flow)
5. [Sub-skills](#sub-skills)
6. [Evaluation frameworks](#evaluation-frameworks)
7. [Scoring model](#scoring-model)
8. [Quality gates](#quality-gates)
9. [Knowledge base and self-improvement](#knowledge-base-and-self-improvement)
10. [Cross-skill integration](#cross-skill-integration)
11. [Project layout](#project-layout)
12. [Requirements](#requirements)
13. [Install](#install)
14. [Usage](#usage)
15. [Testing](#testing)
16. [Test scenarios](#test-scenarios)
17. [Configuration](#configuration)
18. [Error handling and graceful degradation](#error-handling-and-graceful-degradation)
19. [Status](#status)
20. [Roadmap](#roadmap)
21. [Contributing](#contributing)
22. [License](#license)

---

## What this skill does

This repository is a **Claude Skill** (a markdown-defined capability plus supporting
tooling) that evaluates workplace and fire drill scenarios the way a real
occupational health & safety auditor would:

- Ingests a free-form drill description.
- Selects the right named, world-renowned evaluation framework for the subject.
- Gathers evidence from authoritative sources (live when possible, from the
  bundled knowledge base when not).
- Scores the drill across five dimensions on a 0 to 100 scale, each score cited
  to a framework criterion or evidence source.
- Produces a prioritized improvement roadmap (effort x impact, with owners and
  expected effects).
- Runs a devil's-advocate pass that attacks its own scores before anything ships.

The output is a professional artifact: Summary, Scorecard, Detailed Analysis,
Improvement Roadmap, Assumptions / Confidence / Limitations, and Sources.

## Why it exists

Employers run safety and fire drills but rarely evaluate them rigorously for
compliance, response time, and effectiveness. Gaps surface only in real
emergencies. Practitioners need reproducible, evidence-graded evaluation rather
than ad-hoc opinion, so this skill enforces:

- A research-first harness (no memory-only claims when search is possible).
- Named frameworks only, never ad-hoc criteria.
- A framework selector that adapts to the subject.
- A mandatory multi-dimensional score plus prioritized roadmap.
- A self-improving knowledge base via a weekly scholarly crawl.

## Architecture

```
User request
   |
   v
[1] sub-stakeholder-mapper        -> structured intake (RACI roles, missing roles)
   |
   v
[2] sub-requirements-gatherer     -> framework selection + requirements + weights
   |
   v
[3] sub-scoring-engine            -> evidence + 5-dimension scorecard + roadmap
   |
   v
[4] sub-quality-reviewer          -> devil's-advocate + gate certification
   |
   v
Final artifact (Summary, Scorecard, Analysis, Roadmap, Limitations, Sources)
```

Each stage emits a validated JSON payload (`schema_version: "1.0"`) that the next
stage consumes. If a stage's quality gate fails, the harness halts and fixes before
continuing.

## The harness flow

1. **Intake.** Parse the request. If essentials are missing (facility type, drill
   type, occupancy, jurisdiction, observed evacuation time), ask targeted
   questions (max 3 rounds). Never fabricate missing fields.
2. **Framework selection.** Enumerate hazards, choose named framework(s) using a
   decision rule, define measurable requirements per dimension, set scoring weights
   (sum to 1.0, surfaced to the user).
3. **Evidence and scoring.** Run WebSearch / WebFetch against authoritative sources.
   If tools are unavailable, read the bundled knowledge base and clearly record the
   limitation. Score 0 to 100 across the five dimensions, each cited. Compute the
   weighted composite. Build the effort x impact roadmap.
4. **Quality gate.** Devil's-advocate the scores, recompute the composite, verify
   every citation, cap Communication and Evacuation effectiveness below 70 when
   participation is below 50% unless justified, certify the gate checklist.
5. **Artifact.** Render the user-facing report from the final payload.

## Sub-skills

| Sub-skill | Stage | Purpose |
|-----------|-------|---------|
| `sub-stakeholder-mapper` | Intake | Map roles (wardens, first-aiders, evacuees, ERT) and responsibilities; build RACI; flag missing roles. |
| `sub-requirements-gatherer` | Framework | Enumerate hazards; select framework(s); define requirements; set scoring weights. |
| `sub-scoring-engine` | Scoring | Gather evidence; score 5 dimensions; compute composite; build roadmap. |
| `sub-quality-reviewer` | Quality gate | Devil's-advocate; recompute composite; certify gates; emit final payload. |

Each sub-skill file in `skills/` documents its role, purpose, inputs, procedure,
output schema, quality gate, tools, and hand-off.

## Evaluation frameworks

Only named, world-renowned, citable frameworks are used. Never ad-hoc criteria.

| Framework | Full name | Issuer |
|-----------|----------|--------|
| OSHA 1910.38 | Emergency Action Plans | US OSHA |
| OSHA 1910.157 | Portable Fire Extinguishers | US OSHA |
| OSHA 1910.120 | HAZWOPER (Hazmat operations) | US OSHA |
| NFPA 101 | Life Safety Code | NFPA |
| NFPA 1600 | Continuity, Emergency, and Crisis Management | NFPA |
| NFPA 1660 | Emergency Evacuation Planning | NFPA |
| ISO 45001:2018 | Occupational Health & Safety Management Systems | ISO |
| Evacuation modelling | RSET vs ASET, SFPE guidance, NIST TN 1689 | Academic |
| HFACS | Human Factors Analysis and Classification System | Academic |
| PDCA | Plan-Do-Check-Act continuous improvement | ISO lineage |

## Scoring model

| Dimension | Range | Default weight | Anchor |
|-----------|-------|----------------|--------|
| Regulatory compliance | 0 to 100 | 0.20 | OSHA 1910.38 / .157 / .120 |
| Response time | 0 to 100 | 0.25 | RSET vs ASET, SFPE, NIST TN 1689 |
| Communication | 0 to 100 | 0.20 | NFPA 1600, OSHA 1910.38(d) |
| Evacuation effectiveness | 0 to 100 | 0.25 | NFPA 101, NFPA 1660 |
| Gap closure | 0 to 100 | 0.10 | ISO 45001, HFACS, PDCA |

The composite is the weighted mean. Weights are tuned per case (for example,
Response time is raised for high-rise evacuations; Regulatory compliance is raised
for hazmat drills), justified, and surfaced to the user. Every dimension score must
cite at least one framework criterion or evidence source.

Confidence bands:
- **High** - at least 3 cited empirical or standard sources.
- **Medium** - 1 to 2 cited sources.
- **Low** - expert opinion only.

Evidence hierarchy enforced across all sources:
Systematic Review > Meta-Analysis > RCT / Empirical field study > Cohort / Case study
> Guideline / Standard > Expert opinion > Blog.

## Quality gates

All must be true before the artifact is emitted:

- Framework selection justified to the user.
- Every dimension score cites a framework criterion or evidence source.
- Roadmap items have effort + impact + owner + expected effect + rationale.
- Assumptions, confidence, and limitations stated.
- Devil's-advocate review completed with at least 3 attacks resolved.
- Composite recomputed and matches to within 0.1.
- Graceful degradation recorded when tools were unavailable.

## Knowledge base and self-improvement

`SECOND-KNOWLEDGE-BRAIN.md` is a living knowledge base seeded with real, citable
references (OSHA eCFR, NFPA, ISO 45001, NIST TN 1689, SFPE, Safety Science, Fire
Safety Journal). It is grown weekly by `tools/knowledge_updater.py`, a
production-grade async pipeline over real structured scholarly APIs:

- **Crossref** - DOI registry, filtered to Safety Science ISSN.
- **arXiv** - preprints API.
- **Semantic Scholar** - graph API.
- Optional **crawl4ai** - HTML crawl of OSHA / NFPA pages (extra dependency,
  gracefully skipped if not installed).

Pipeline: fetch, normalize, score (recency + relevance), dedup (SHA-256 / 16 of
DOI/URL), append dated markdown block. Per-source fault isolation means one source
failing never aborts the run. Appends are idempotent.

## Cross-skill integration

This skill is part of the **Business Operations & Strategy** cluster. Its four
sub-skills are written generically enough to be reused by sibling skills without
divergence. `CROSS-SKILL-INTERFACE.md` defines the shared sub-skill catalogue, the
aligned 0 to 100 weighted-composite convention, reuse rules, and the cluster
validation hook (`tools/validate_harness.py`).

## Project layout

```
.
+-- skills/
|   +-- main.md                       # harness definition
|   +-- sub-stakeholder-mapper.md      # stage 1
|   +-- sub-requirements-gatherer.md  # stage 2
|   +-- sub-scoring-engine.md         # stage 3
|   +-- sub-quality-reviewer.md        # stage 4
+-- tools/
|   +-- knowledge_updater.py          # async scholarly crawler + scorer + appender
|   +-- knowledge_updater.toml        # config (queries, keywords, limits)
|   +-- validate_harness.py           # payload schema + gate validator
|   +-- requirements.txt
|   +-- README.md
|   +-- tests/
|       +-- test_knowledge_updater.py # 16 offline unit tests
|       +-- run.py
+-- tests/
|   +-- test-scenarios.md             # 14 scenarios (5 canonical + 9 gate/edge)
|   +-- test_validate_harness.py      # 6 validator tests
|   +-- fixtures/
|       +-- stage1_stakeholder_mapper.json
|       +-- stage2_requirements_gatherer.json
|       +-- stage3_scoring_engine.json
|       +-- stage4_quality_reviewer.json
+-- SECOND-KNOWLEDGE-BRAIN.md         # living knowledge base (real references)
+-- CROSS-SKILL-INTERFACE.md          # cluster reuse contract
+-- PROJECT-detail.md                 # full technical spec
+-- PROJECT-DEVELOPMENT-PHASE-TRACKING.md
+-- CLAUDE.md                         # skill identity + agent guidance
+-- README.md                         # this file
```

## Requirements

- Python 3.11 or newer (uses `tomllib` in the standard library).
- `httpx` for the async crawler (pinned in `tools/requirements.txt`).
- `pytest` and `pytest-asyncio` for the test suite.
- Optional: `crawl4ai` for HTML crawling of OSHA / NFPA pages.

The skill markdown files themselves have no runtime dependency; they are consumed
by a Claude agent with the tools listed in each file (Read, Write, WebSearch,
WebFetch, Bash).

## Install

```bash
git clone https://github.com/dungnotnull/workplace-safety-drill-evaluator-agent-skill.git
cd workplace-safety-drill-evaluator-agent-skill
pip install -r tools/requirements.txt
```

Optional, for HTML crawling of OSHA / NFPA pages:

```bash
pip install "crawl4ai>=0.4.0"
```

## Usage

### Running the skill

Use this skill inside a Claude session (or any agent runtime that supports the
Skill format). Point the agent at `skills/main.md`. Example trigger:

> Evaluate our 12-floor office tower fire evacuation drill. About 600 occupants,
> 6 minutes to evacuate, voice plus horn plus floor wardens, 88% accounted at the
> assembly point.

The agent will run the harness, ask for any missing essentials, select the
framework, gather evidence, score, roadmap, devil's-advocate, and render the
report.

### Refreshing the knowledge base

```bash
# Dry run: print scored candidate entries without writing
python tools/knowledge_updater.py --dry-run

# Real run: append dated, deduplicated entries to SECOND-KNOWLEDGE-BRAIN.md
python tools/knowledge_updater.py --since 2024-01-01 --min-score 0.40

# Weekly tick (cron-friendly log line; scheduling is the operator's job)
python tools/knowledge_updater.py --weekly
```

### Validating harness payloads

```bash
python tools/validate_harness.py tests/fixtures/stage1_stakeholder_mapper.json \
  tests/fixtures/stage2_requirements_gatherer.json \
  tests/fixtures/stage3_scoring_engine.json \
  tests/fixtures/stage4_quality_reviewer.json

# Or via stdin
cat payload.json | python tools/validate_harness.py -
```

## Testing

The offline suite needs no network and no live model run.

```bash
python -m pytest tests/ tools/ -q
```

Expected: 22 passed.

- `tools/tests/test_knowledge_updater.py` - 16 tests covering hashing, scoring,
  dedup, idempotent appends, min-score, max-per-source, and the three API parsers
  (Crossref, arXiv, Semantic Scholar).
- `tests/test_validate_harness.py` - 6 tests covering valid fixtures, missing
  dimension, weights not summing to 1, gate failure, score out of range, and
  unknown stage.

Run a single suite:

```bash
python tools/tests/run.py          # crawler tests
python -m pytest tests/test_validate_harness.py -q
```

## Test scenarios

`tests/test-scenarios.md` documents 14 scenarios:

**Canonical (5):**
1. Office tower fire drill (NFPA 101 + OSHA 1910.38; modeled by the fixtures).
2. Factory chemical-spill drill (OSHA 1910.120 HAZWOPER + NFPA 1600).
3. Healthcare facility evacuation (defend-in-place vs evacuate; NFPA 101 / 1660).
4. Drill with poor turnout (Communication and Evacuation effectiveness capped
   below 70 when participation is below 50%).
5. ISO 45001 audit prep (clause-level gap assessment).

**Gate-firing and edge (9):**
6. Missing essentials block intake (targeted questions, no fabrication).
7. WebSearch / WebFetch unavailable (graceful degradation to knowledge base).
8. Fabricated citation caught (confidence downgraded, revision logged).
9. Composite mismatch rejected (recompute to within 0.1).
10. Weights do not sum to 1.0 (validator rejects).
11. Score out of range (validator rejects).
12. Fewer than 3 devil's-advocate attacks (validator rejects).
13. Combined drill (fire + hazmat; ISO 45001 + NFPA 101 + OSHA 1910.38 / .120).
14. Unknown jurisdiction (non-US; ISO 45001 only, OSHA dropped).

Each scenario lists the input, expected framework(s), gate behavior, and pass
criteria.

## Configuration

`tools/knowledge_updater.toml` controls the crawler. Edit it to change queries,
domain keywords, per-source limits, politeness email, and score thresholds. CLI
flags override config values.

Key options:

| Option | Default | Purpose |
|--------|---------|---------|
| `since` | 1970-01-01 | Keep entries dated on or after this date. |
| `min_score` | 0.30 | Drop entries below this combined score. |
| `max_per_source` | 25 | Cap results kept per source API per run. |
| `timeout_seconds` | 30 | Per-request HTTP timeout. |
| `concurrency` | 4 | Max concurrent API requests. |
| `user_agent` | workplace-safety-drill-evaluator/1.0 | Polite UA string. |
| `crossref.mailto` | knowledge-updater@example.org | Crossref polite-pool email. |
| `crossref.issn_filter` | 0925-7535 | Restrict to Safety Science. |

## Error handling and graceful degradation

- **Missing data:** state the assumption, set confidence to medium or low, never
  block silently. Ask targeted questions at intake (max 3 rounds).
- **Tool failure:** read `SECOND-KNOWLEDGE-BRAIN.md`, cite those entries, and
  record the limitation in the payload `limitations` list.
- **Citation verification failure:** the quality reviewer downgrades confidence to
  low and revises the score.
- **Gate failure:** halt, revise (max 2 revisions per stage), then re-certify.
- **Low participation (below 50%):** cap Communication and Evacuation
  effectiveness below 70 unless explicitly justified (recorded in `revisions`).

## Status

All development phases (0 through 5) are complete and verified offline. See
`PROJECT-DEVELOPMENT-PHASE-TRACKING.md`. The repository is production-grade and
ready for open source. The only intentionally deferred items are the first live
crawl and live end-to-end WebSearch / WebFetch runs, which require runtime
tooling rather than code changes and were deferred to conserve resources.

## Roadmap

- First live crawl against Crossref, arXiv, and Semantic Scholar.
- Live end-to-end WebSearch / WebFetch run through the full harness.
- Optional GitHub Actions workflow to run the weekly crawl on a schedule.
- Optional `pyproject.toml` packaging for the tools as an installable package.

## Contributing

Contributions are welcome. Please:

1. Run the offline suite before opening a pull request:
   `python -m pytest tests/ tools/ -q`.
2. Validate any new or changed stage payloads with `tools/validate_harness.py`.
3. Keep sub-skill JSON schemas at `schema_version: "1.0"` unless you bump the
   version intentionally and update the validator and fixtures together.
4. Add or update test scenarios in `tests/test-scenarios.md` for new behavior.
5. Prefer ASCII-friendly punctuation in markdown to avoid encoding artifacts.

## License

MIT. See `LICENSE` for the full text if present; otherwise this project is
released under the MIT License.
