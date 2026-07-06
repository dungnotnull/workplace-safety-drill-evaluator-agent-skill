# tools/ — supporting tooling for `workplace-safety-drill-evaluator`

Production-grade utilities that back the skill. Both are runnable today without a
live model run (per the project's "prepare for real run, save resources" policy).

## `knowledge_updater.py`
Async scholarly-enrichment pipeline that grows `../SECOND-KNOWLEDGE-BRAIN.md`.

- **Sources (structured APIs):** Crossref, arXiv, Semantic Scholar. Optional HTML
  crawl of OSHA/NFPA pages via `crawl4ai` (install `pip install -e .[crawl]`; skipped
  silently if absent).
- **Pipeline:** fetch → normalize (`Entry`) → score (recency + relevance) → dedup
  (SHA-256/16 of DOI/URL) → append dated markdown block.
- **Config:** `knowledge_updater.toml` (queries, keywords, per-source limits, politeness
  email). CLI flags override config.
- **Safety:** per-source try/except (one failure never aborts the run); idempotent
  appends; deterministic output ordering.

### Install & run
```
pip install -r tools/requirements.txt
python tools/knowledge_updater.py --dry-run            # print scored JSON, no writes
python tools/knowledge_updater.py --since 2024-01-01 --min-score 0.40
```
Weekly scheduling is the operator's responsibility (cron / systemd timer / GitHub
Actions). The `--weekly` flag emits a dated log line for that purpose.

### Tests (no network)
```
python -m pytest tools/tests/test_knowledge_updater.py -q
```

## `validate_harness.py`
Schema + quality-gate validator for the JSON payloads emitted by each harness stage
(`sub-stakeholder-mapper`, `sub-requirements-gatherer`, `sub-scoring-engine`,
`sub-quality-reviewer`). Used by CI to detect regressions in skill output.

```
python tools/validate_harness.py tests/fixtures/stage1_stakeholder_mapper.json ...
cat payload.json | python tools/validate_harness.py -
```
Checks include: required keys & types, all 5 dimensions present, scoring weights
sum to 1.0, scores in 0–100 with citations, roadmap completeness, gate checklist
all `pass`, ≥3 devil's-advocate attacks resolved. Exit 0 valid / 1 invalid.

### Tests (no network)
```
python -m pytest tests/test_validate_harness.py -q
```

## Repo layout
```
tools/
  knowledge_updater.py        # async crawler + scorer + appender
  knowledge_updater.toml      # config (queries, keywords, limits)
  validate_harness.py         # payload schema + gate validator
  requirements.txt
  README.md                   # this file
  tests/
    __init__.py
    test_knowledge_updater.py
    run.py
```
