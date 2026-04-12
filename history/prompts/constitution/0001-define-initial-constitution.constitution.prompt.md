---
id: 0001
title: Define initial constitution
stage: constitution
date: 2026-04-12
surface: agent
model: opencode/big-pickle
feature: none
branch: main
user: system
command: constitution-update
labels: [governance, principles, initial-setup]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - history/prompts/constitution/0001-define-initial-constitution.constitution.prompt.md
tests: []
---

## Prompt

Constitution template update request (no user input provided - inferred from project context).

## Response snapshot

Created initial ArchiToolset constitution with 6 core principles:
- I. Library-First Architecture
- II. CLI-First Interface  
- III. Test-First Development (NON-NEGOTIABLE)
- IV. Contract Testing Mandate
- V. Observability by Default
- VI. Semantic Versioning

Plus sections for Quality Assurance, Development Workflow, and Governance with amendment procedures.

## Outcome

- ✅ Impact: Established foundational governance document for Spec-Driven Development workflow
- 🧪 Tests: None (constitutional governance document)
- 📁 Files: Created/updated constitution.md, created PHR
- 🔁 Next prompts: Use /sp.feature to create first feature, or /sp.plan for architecture work
- 🧠 Reflection: Constitution designed to align with opencode.md guidance and template structures

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
