---
id: 0003
title: Add FastAPI principle
stage: constitution
date: 2026-04-13
surface: agent
model: opencode/big-pickle
feature: none
branch: main
user: system
command: constitution-update
labels: [governance, principles, FastAPI, API]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - history/prompts/constitution/0003-add-fastapi-principle.constitution.prompt.md
tests: []
---

## Prompt

add Principles API must be defined based on FastAPI

## Response snapshot

Added principle XIX: FastAPI-First API Design
- All HTTP APIs MUST use FastAPI
- Pydantic models for validation
- Auto-generated OpenAPI schemas
- /docs endpoint for documentation

## Outcome

- ✅ Impact: Added FastAPI principle for consistent API design
- 🧪 Tests: None (constitutional governance document)
- 📁 Files: Updated constitution.md
- 🔁 Next prompts: None
- 🧠 Reflection: Simple principle addition to standardize API development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
