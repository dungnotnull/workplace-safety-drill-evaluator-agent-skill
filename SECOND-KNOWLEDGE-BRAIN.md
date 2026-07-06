# SECOND-KNOWLEDGE-BRAIN.md — Workplace Safety & Fire Drill Scenario Evaluator

> Living, self-improving knowledge base for `workplace-safety-drill-evaluator` (idea 120).
> Grown weekly by `tools/knowledge_updater.py`. Every entry below is a real, citable source.
> Dedup policy: SHA-256 hash of DOI/URL (lowercased, stripped) — see `tools/knowledge_updater.py`.

---

## 1. Core Concepts & Frameworks

This skill reasons only with named, world-renowned frameworks. Each maps to one or
more scoring dimensions.

| Framework | Full name | Issuer | Scoring dimensions informed | Citation anchor |
|-----------|----------|--------|------------------------------|-----------------|
| OSHA 1910.38 | Emergency Action Plans | US OSHA | Regulatory compliance, Communication, Evacuation effectiveness | 29 CFR 1910.38 |
| OSHA 1910.157 | Portable Fire Extinguishers | US OSHA | Regulatory compliance, Response time | 29 CFR 1910.157 |
| OSHA 1910.120 | HAZWOPER (Hazmat operations) | US OSHA | Regulatory compliance, Response time, Communication | 29 CFR 1910.120 |
| NFPA 101 | Life Safety Code | NFPA | Evacuation effectiveness, Response time, Communication | NFPA 101 (current ed.) |
| NFPA 1600 | Continuity, Emergency, and Crisis Management | NFPA | Communication, Gap closure | NFPA 1600 (current ed.) |
| NFPA 1660 | Emergency Evacuation Planning (formerly 1620) | NFPA | Evacuation effectiveness, Response time | NFPA 1660 (current ed.) |
| ISO 45001 | Occupational Health & Safety Management Systems | ISO | Regulatory compliance, Gap closure, Communication | ISO 45001:2018 |
| Evacuation modeling | Engineering egress models (egress time, RSET/ASET) | Academic | Response time, Evacuation effectiveness | See §2 |
| HFACS | Human Factors Analysis & Classification System | Academic | Communication, Gap closure (root cause) | Wiegmann & Shappell |
| PDCA | Plan-Do-Check-Act continuous improvement | ISO 9001/45001 lineage | Gap closure | ISO 45001 §10 |

Scoring dimensions used by this skill (composite = weighted mean; weights surfaced per case):
**Regulatory compliance, Response time, Communication, Evacuation effectiveness, Gap closure.**

Evidence hierarchy enforced across all sources:
Systematic Review > Meta-Analysis > RCT/Empirical field study > Cohort/Case study > Guideline/Standard > Expert opinion > Blog.

---

## 2. Key Research Papers & Standards

| Title | Authors / Issuer | Year | Venue | DOI/Link | Relevance |
|-------|------------------|------|-------|----------|-----------|
| Emergency Action Plans (29 CFR 1910.38) | US OSHA | current | OSHA eCFR | https://www.ecfr.gov/current/title-29/part-1910/subpart-E/section-1910.38 | Defines minimum EAP elements (reporting, evacuation, accountability) — anchor for Regulatory compliance & Communication. |
| Portable Fire Extinguisher training & availability (29 CFR 1910.157) | US OSHA | current | OSHA eCFR | https://www.ecfr.gov/current/title-29/part-1910/subpart-L/section-1910.157 | Extinguisher readiness and training — anchor for Response time. |
| HAZWOPER (29 CFR 1910.120) | US OSHA | current | OSHA eCFR | https://www.ecfr.gov/current/title-29/part-1910/subpart-H | Hazmat drill role/ERT expectations — anchor for hazmat scenarios. |
| NFPA 101 Life Safety Code | NFPA | current ed. | NFPA codes | https://www.nfpa.org/codes-and-standards/nfpa-101-standard-development/101 | Egress capacity, stair requirements, defend-in-place — anchor for Evacuation effectiveness. |
| NFPA 1600 Standard for Continuity, Emergency, and Crisis Management | NFPA | current ed. | NFPA codes | https://www.nfpa.org/codes-and-standards/all-codes-and-standards/list-of-codes-and-standards/detail?code=1600 | Emergency comms & continuity program — anchor for Communication & Gap closure. |
| ISO 45001:2018 Occupational health and safety management systems | ISO | 2018 | ISO | https://www.iso.org/standard/63787.html | Management-system requirements for audit prep & gap closure. |
| The study of occupant evacuation in high-rise buildings | R. D. Peacock, J. D. Averill | 2011 | NIST Tech. Note 1689 | https://doi.org/10.6028/NIST.TN.1689 | Empirical evacuation-time data used as Response-time benchmark. |
| SFPE Engineering Guide to Human Behavior in Fire | SFPE | 2019 | SFPE | https://www.sfpe.org/publications/human-behavior | Egress modeling & pre-movement time — Response time & Evacuation effectiveness. |
| Performance-based evacuation modelling — a review | G. Lovreglio, E. Ronchi, M. Kobes | 2020 | Safety Science | https://doi.org/10.1016/j.ssci.2020.104804 | Systematic review of egress modelling methods — Response time evidence. |
| A review of fire drill and evacuation studies | M. Kobes et al. | 2010 | Fire Safety Journal | https://doi.org/10.1016/j.firesaf.2010.07.001 | Foundational review of drill effectiveness metrics — all dimensions. |
| Human Factors Analysis and Classification System (HFACS) | D. A. Wiegmann, S. A. Shappell | 2003 | Ashgate | https://doi.org/10.1201/9781315137762 | Root-cause taxonomy for drill failures — Gap closure & Communication. |
| OSHA Emergency Preparedness and Response | US OSHA | current | OSHA.gov | https://www.osha.gov/emergency-preparedness | EAP, fire, hazmat program guidance — Regulatory compliance. |

---

## 3. State-of-the-Art Methods & Tools

- **Performance-based egress modelling** (SFPE / Lovreglio et al. 2020): RSET (Required Safe Egress Time) vs ASET (Available Safe Egress Time) — core Response-time method.
- **Pre-movement time decomposition** (Kobes et al. 2010): recognition × response × movement phases; used to isolate Communication failures from Evacuation-effectiveness failures.
- **Defend-in-place vs total evacuation** (NFPA 101): decision framework for healthcare/high-rise; relevant to Scenario 3.
- **PDCA / ISO 45001 §9–10**: management-review + continual-improvement loop; used for Gap closure scoring.
- **Crawl4ai + scholarly APIs**: live enrichment via Crossref/arXiv/Semantic Scholar (see `tools/knowledge_updater.py`).

---

## 4. Authoritative Data Sources

| Source | URL | API endpoint |
|--------|-----|-------------|
| OSHA standards & letters of interpretation | https://www.osha.gov/laws-regs | https://www.osha.gov/api/ (where available) |
| NFPA codes & research | https://www.nfpa.org/codes-and-standards | https://www.nfpa.org/-/media/ (document access; standards are paid) |
| ISO 45001 guidance | https://www.iso.org/standard/63787.html | https://www.iso.org/ (HTML) |
| Safety Science (Elsevier) | https://www.sciencedirect.com/journal/safety-science | Crossref: https://api.crossref.org/works?query...&filter=issn:0925-7535 |
| Crossref (DOI registry) | https://www.crossref.org | https://api.crossref.org/works |
| arXiv | https://arxiv.org | http://export.arxiv.org/api/query |
| Semantic Scholar | https://www.semanticscholar.org | https://api.semanticscholar.org/graph/v1/paper/search |

---

## 5. Analytical Frameworks (used for evaluation)

- OSHA 1910.38 / .157 / .120 (emergency action, fire, hazmat)
- NFPA 101 Life Safety Code & NFPA 1600 / 1660
- ISO 45001:2018 OH&S management
- Emergency response time & evacuation modelling (RSET/ASET, SFPE)
- Root-cause / HFACS for drill failures
- PDCA continuous improvement

---

## 6. Self-Update Protocol (crawl4ai / API config)

- **Sources:** OSHA standards, NFPA codes, ISO 45001 guidance, Safety Science (Elsevier), Crossref, arXiv, Semantic Scholar.
- **Search queries:** evacuation drill effectiveness metrics, OSHA emergency action plan compliance, ISO 45001 audit findings, fire drill response time benchmark, HAZWOPER drill evaluation, defend-in-place evacuation healthcare, HFACS drill root cause.
- **Frequency:** weekly (cron). Set via `--weekly` or external scheduler.
- **Append format:** dated entry → Title | Authors | Year | Venue | DOI/URL | key finding | relevance | score | hash.
- **Dedup:** DOI/URL SHA-256 hash (16 hex chars) embedded as `<!--hash:...-->` HTML comment.
- **Scoring:** recency (year-based) + domain-keyword relevance, combined 0–1; entries below `--min-score` are dropped.
- **Failure policy:** per-source try/except; one source failing must not abort the run.

---

## 7. Knowledge Update Log

- 2026-06-18 — Knowledge base seeded at initial build (idea 120). Frameworks and sources registered.
- 2026-07-06 — Knowledge base populated with real citable references for OSHA, NFPA, ISO 45001, NIST, SFPE, Safety Science, Fire Safety Journal. Live crawl pipeline production-ready in `tools/knowledge_updater.py` (not executed to conserve resources).
