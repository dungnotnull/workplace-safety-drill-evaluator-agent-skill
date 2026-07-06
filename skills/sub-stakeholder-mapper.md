---
name: workplace-safety-drill-evaluator-sub-stakeholder-mapper
description: Map roles (wardens, first-aiders, evacuees, ERT) and responsibilities in the drill, and produce the validated structured intake payload consumed by the rest of the harness.
---

## Role
Stage 1 sub-skill of `workplace-safety-drill-evaluator` (Workplace Safety & Fire Drill
Scenario Evaluator). Acts as the **intake stage**: it converts a free-form user request
into a validated, schema-complete stakeholder map and drill profile that every later
stage consumes.

## Purpose
Map every person-role and responsibility involved in the drill (floor wardens,
first-aiders, evacuees, Emergency Response Team (ERT), incident commander, external
responders) and capture who is accountable for each phase of the response.

## Inputs
- The user's free-text request (and any uploaded artifacts, photos, drill logs).
- `SECOND-KNOWLEDGE-BRAIN.md` (read-only) for canonical role definitions from
  OSHA 1910.38 and NFPA 1600.

## Procedure
1. **Parse the request.** Extract facility, occupancy, drill type, and any
   quantitative facts (floors, headcount, observed evacuation time, alarms used).
2. **Identify missing essentials.** If any field in the output schema below is absent,
   ask targeted questions (max 3 rounds) before proceeding. Never assume drill type,
   occupancy, or jurisdiction.
3. **Map roles.** Enumerate every role present and assign responsibilities using:
   - OSHA 29 CFR 1910.38(e)(3) — EAP employee accountability, evacuation wardens.
   - OSHA 29 CFR 1910.156/.157 — fire brigades / portable extinguisher users.
   - NFPA 1600 §5 — emergency operations roles (incident commander, comms lead).
   - ISO 45001 §5.3 — roles, responsibilities and authorities for OH&S.
4. **Build the accountability matrix.** For each role: Responsible | Accountable |
   Consulted | Informed (RACI) against the drill phases
   (alarm → notification → evacuation → assembly → accountability → all-clear).
5. **Flag gaps.** Note any role required by the chosen framework that was absent from
   the drill (these feed the Gap-closure dimension later).
6. **Record assumptions and confidence** (high/medium/low) for every inferred field.

## Output Schema (JSON; strictly validated — gate fails if any required key is missing)
```json
{
  "schema_version": "1.0",
  "stage": "sub-stakeholder-mapper",
  "request_summary": "string",
  "facility": {
    "type": "office | factory | healthcare | retail | warehouse | education | other",
    "floors": "integer | null",
    "occupancy": "integer | null",
    "jurisdiction": "string (e.g., US-OSHA, EU, ISO 45001)"
  },
  "drill": {
    "type": "fire-evacuation | hazmat-spill | shelter-in-place | active-threat | medical | combined",
    "objectives": ["string"],
    "observed_evacuation_time_min": "number | null",
    "alarms_used": ["string"],
    "participation_rate_pct": "number | null"
  },
  "roles": [
    {
      "name": "string",
      "role_type": "incident-commander | floor-warden | first-aider | ert-member | evacuee | external-responder | other",
      "responsibilities": ["string"],
      "raci_phases": {"alarm":"R|A|C|I", "notification":"...", "evacuation":"...", "assembly":"...", "accountability":"...", "all_clear":"..."},
      "present_in_drill": "boolean",
      "framework_ref": "string (citation)"
    }
  ],
  "missing_roles": ["string (framework-required roles absent from drill)"],
  "assumptions": ["string"],
  "confidence": "high | medium | low",
  "frameworks_applied": ["OSHA 29 CFR 1910.38", "..."]
}
```

## Quality Gate (must all be true before emitting the payload)
- [ ] Every required JSON key present and typed correctly.
- [ ] `roles` non-empty; each role carries `raci_phases` and `framework_ref`.
- [ ] Missing essentials caused targeted questions, not silent assumptions.
- [ ] `missing_roles` populated when a framework-required role was absent.
- [ ] `assumptions` + `confidence` stated.

## Tools
- `Read` — read `SECOND-KNOWLEDGE-BRAIN.md` for role taxonomy.
- `Write` — (optional) persist the payload to a working artifact path.
- No `WebSearch` at this stage — intake only.

## Hand-off
Emit the validated payload above. The next stage
(`sub-requirements-gatherer`) consumes `facility`, `drill`, and `roles` directly.
