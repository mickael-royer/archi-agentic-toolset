<!-- Sync Impact Report
Version change: 1.0.0 → 1.1.0
Modified principles: Principle III updated for pytest requirement
Added sections:
  - Principle VII: Code Quality & Object-Oriented Design
  - Principle VIII: Python Standards & Tooling
  - QA rule: 80% test coverage
  - Dev Workflow: Keep all project files in git
Removed sections: None
Templates requiring updates: None
Follow-up TODOs: None
-->

# ArchiToolset Constitution

## Core Principles

### I. Library-First Architecture

Every feature MUST be implemented as a standalone library. Libraries MUST be self-contained, independently testable, and documented with a clear purpose. No organizational-only libraries that exist merely to group code without a distinct responsibility.

**Rationale**: Library boundaries enforce clear contracts and prevent coupling. Independent testability enables confident refactoring.

### II. CLI-First Interface

Every library MUST expose a command-line interface using a text in/out protocol: stdin/args → stdout, errors → stderr. Output MUST support both JSON (for machine consumption) and human-readable formats (for debugging).

**Rationale**: CLI-first ensures composability, debuggability, and enables scriptable automation without dependency on GUI toolkits.

### III. Test-First Development (NON-NEGOTIABLE)

Red-Green-Refactor cycle MUST be strictly enforced using the `pytest` framework. Tests MUST be written before implementation, verified to fail, then implementation follows. All public contracts require contract tests. Integration tests are mandatory for inter-service communication and shared schemas.

**Rationale**: Test-first catches design flaws early, provides executable documentation, and enables confident continuous delivery.

### IV. Contract Testing Mandate

Contract tests are REQUIRED for: new library APIs, breaking changes to existing APIs, inter-service communication protocols, and shared schema definitions. Contract tests MUST be versioned alongside the contracts they verify.

**Rationale**: Contract tests prevent integration failures by validating interface compatibility independently of implementation.

### V. Observability by Default

All operations MUST produce structured logs with: timestamp, operation type, inputs (sanitized), outputs, and error details. Text I/O protocols MUST ensure debuggability without specialized tooling.

**Rationale**: Observable systems enable rapid diagnosis in production and reduce mean time to resolution.

### VI. Semantic Versioning

All libraries MUST follow Semantic Versioning (MAJOR.MINOR.PATCH). Breaking changes require MAJOR version bump with migration documentation. Deprecations MUST be announced in MINOR releases before removal in MAJOR.

**Rationale**: Predictable versioning enables consumers to assess upgrade impact without diving into changelogs.

### VII. Code Quality & Object-Oriented Design

All code MUST adhere to essential OOP principles: SOLID, DRY, and KISS. Implementations MUST prioritize clean, readable design optimizing for learning and teaching value rather than excessive cleverness. Error handling MUST be explicit, logging failures rather than silencing them (e.g., avoid bare `except:` or silent `pass`).

**Rationale**: Readability and comprehensibility ensure maintainability and team velocity over long term, while explicit error handling prevents cryptic bugs.

### VIII. Python Standards & Tooling

Projects MUST be created using Python 3.12+ and manage dependencies using the `uv` package manager. 
The following Python-specific standards MUST be strictly followed:
- **Type Hints:** Comprehensive type hints are mandatory everywhere.
- **Docstrings:** All public functions, classes, and methods MUST have detailed docstrings with a clear focus on the "why" and "how" to support teaching and learning.
- **Data Structures:** Immutable or structured data MUST use `dataclasses`.

**Rationale**: Strong typing and thorough documentation eliminate ambiguity and streamline new developer onboarding, while modern tooling like UV ensures swift dependency resolution.

## Quality Assurance

- All PRs MUST pass contract and integration tests before merge
- Test coverage MUST meet a minimum of 80%
- Code review MUST verify principle compliance
- Complexity MUST be justified in architecture decision records
- No hardcoded secrets or tokens; use `.env` and environment variables

## Development Workflow

- Keep all project files in git version control
- Feature branches follow pattern: `###-feature-name`
- Specs stored in `specs/[feature]/` with: spec.md, plan.md, tasks.md
- Use `/sp.plan`, `/sp.tasks`, `/sp.red`, `/sp.green` commands for iterative development
- Prompt History Records (PHRs) created for every user interaction
- Architecture Decision Records (ADRs) suggested for significant decisions

## Governance

This constitution supersedes all other development practices. Amendments MUST follow this procedure:

1. Propose change with rationale and impact analysis
2. Document in a draft ADR with migration plan
3. Obtain user consent before applying
4. Update constitution version per semantic versioning rules:
   - MAJOR: Backward-incompatible principle removals or redefinitions
   - MINOR: New principles or materially expanded guidance
   - PATCH: Clarifications, wording, typo fixes

All reviews MUST verify compliance with these principles. Runtime guidance is provided in `opencode.md`.

**Version**: 1.1.0 | **Ratified**: 2026-04-12 | **Last Amended**: 2026-04-12
