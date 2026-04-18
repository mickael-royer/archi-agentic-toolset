---
id: "0001"
title: "c4-scoring-engine-spec"
stage: "spec"
date: "2026-04-18"
surface: "cli"
model: "big-pickle"
feature: "006-c4-scoring-engine"
branch: "006-c4-scoring-engine"
user: "royerm"
command: "/sp.specify"
labels: [archi-toolset, c4, scoring, architecture]
links:
  spec: "specs/006-c4-scoring-engine/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  created:
    - "specs/006-c4-scoring-engine/spec.md"
    - "specs/006-c4-scoring-engine/checklists/requirements.md"
  modified: []
  deleted: []
tests: []
---

## Prompt

Refactor model loader to convert Archimate element to C4 entities and scoring engine to relies on resulting C4 model (Software System, Container, Component). Architecture score defined at Container level and consolidated at Software System level. Complexity assessment based on afferent/efferent coupling with distinct weight between sync and async relation. Async is less complex (lower coupling). Keep scoring evolution (track) based on commit history for timeline review. Dashboard access scoring result by API. Update dashboard export for timeline, trends and recommendation. Add detailled architecture score report by container/component with treemap representation.

## Response snapshot

Created feature branch 006-c4-scoring-engine, wrote comprehensive spec covering:
- 6 user stories with priorities (P1-P3)
- 8 functional requirements
- 6 success criteria metrics
- Key entities: Software System, Container, Component, Flow/Trigger relations, Score Snapshot
- Edge cases: empty containers, orphaned components, missing relations
- Scoring algorithm: sync (Flow)=1.0 weight, async (Trigger)=0.5 weight

## Outcome

- ✅ Impact: Spec complete with C4 model conversion, container-level scoring, weighted coupling, timeline tracking, API access, export, treemap
- 🧪 Tests: None (spec phase)
- 📁 Files: 2 created (spec.md, checklists/requirements.md)
- 🔁 Next prompts: /sp.clarify or /sp.plan
- 🧠 Reflection: Validated all checklist items pass, no implementation details leaked, all requirements testable

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS (all checklist items)
- Prompt variant (if applicable): N/A
- Next experiment: N/A