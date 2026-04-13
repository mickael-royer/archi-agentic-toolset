---
id: 0002
title: Add 10 new architecture principles
stage: constitution
date: 2026-04-13
surface: agent
model: opencode/big-pickle
feature: none
branch: main
user: system
command: constitution-update
labels: [governance, principles, DDD, microservices, Dapr, Azure, Podman]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - history/prompts/constitution/0002-add-10-new-architecture-principles.constitution.prompt.md
tests: []
---

## Prompt

add principles # Domain Driven Design # Microservice Architecture and patterns # Distributed Application based on Dapr # Event Driven Architecture principles # Object-oriented programming based on SOLID, DRY and KISS principles # AI component will be defined as Agent based on LangChain and LangGraph # Infrastructure as Code process with declarative approach # Cloud deployement based on Azure Services # Local deployment based on Podman # Distroless Container images for security purpose

## Response snapshot

Added 10 new principles (IX-XVIII):
- IX. Object-Oriented Design
- X. Domain-Driven Design
- XI. Microservice Architecture
- XII. Distributed Applications with Dapr
- XIII. Event-Driven Architecture
- XIV. AI Agents with LangChain/LangGraph
- XV. Infrastructure as Code
- XVI. Cloud Deployment (Azure)
- XVII. Local Deployment (Podman)
- XVIII. Distroless Container Security

Also reorganized existing principles: OOP moved to IX, Python Standards to VII, Code Quality to VIII.

Updated Quality Assurance and Development Workflow sections to reflect new infrastructure/container requirements.

## Outcome

- ✅ Impact: Constitution expanded from 8 to 18 principles covering architecture, deployment, and security
- 🧪 Tests: None (constitutional governance document)
- 📁 Files: Updated constitution.md, created PHR
- 🔁 Next prompts: Existing feature plans should verify alignment with new principles
- 🧠 Reflection: User requested comprehensive set of modern architecture principles; reorganized for logical grouping

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
