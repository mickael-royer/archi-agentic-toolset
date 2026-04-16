---
id: 0001
title: archimate-timeline-dashboard-spec
stage: spec
date: 2026-04-15
surface: cli
model: big-pickle
feature: 003-archimate-timeline-dashboard
branch: 003-archimate-timeline-dashboard
user: user
command: /sp.specify
labels: [architecture, scoring, timeline, dashboard, archimate]
links:
  spec: specs/003-archimate-timeline-dashboard/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - path: specs/003-archimate-timeline-dashboard/spec.md
    action: created
  - path: specs/003-archimate-timeline-dashboard/checklists/requirements.md
    action: created
tests: []
---

## Prompt

Refactor Architectore Score service to assess Architecture Model changes based on commit history (eg. https://github.com/mickael-royer/archimate-ear/blob/main/model.archimate) to generate a dashboard with a timeline report

## Response snapshot

Created feature specification for ArchiMate Timeline Dashboard with 4 user stories:
- View Architecture Change Timeline (P1)
- Track Complexity Trends Over Time (P2)
- Generate Dashboard Report (P3)
- Compare Specific Commits (P4)

13 functional requirements covering timeline generation, trend analysis, dashboard reporting, and commit comparison.

## Outcome

- ✅ Impact: Added timeline/dashboard feature for architecture change analysis over commit history
- 🧪 Tests: N/A (spec phase)
- 📁 Files: spec.md, checklists/requirements.md created
- 🔁 Next prompts: /sp.clarify or /sp.plan
- 🧠 Reflection: Feature builds on existing FR-011 (commit SHA linking). Uses existing scoring dimensions from 001 spec.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment: N/A
