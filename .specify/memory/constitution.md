<!-- Sync Impact Report
Version change: 1.2.0 → 1.3.0
Added principles:
  - XIX. FastAPI-First API Design
Removed sections: None
Templates requiring updates: ✅ No template changes needed (constitution check sections auto-generate)
Follow-up TODOs: None
-->

# ArchiToolset Constitution

## Core Principles

### I. Domain-Driven Design

Complex business domains MUST be modeled using Domain-Driven Design (DDD). Ubiquitous Language MUST be established between domain experts and developers. Bounded Contexts MUST define clear boundaries where specific domain models apply. Aggregates, Entities, Value Objects, Domain Events, and Services MUST be used appropriately to represent domain concepts.

**Rationale**: DDD aligns software models with business reality, enabling maintainable evolution as domain complexity grows.

### II. Object-Oriented Design

Architecture and code MUST be designed using Object-Oriented Programming principles. Core OOP concepts MUST be applied: encapsulation (hide internal state), inheritance (model "is-a" relationships), polymorphism (interchangeable interfaces), and abstraction (model essential features). Classes MUST have single responsibility and collaborate through well-defined interfaces.

**Rationale**: OOP provides proven patterns for modeling complex domains, managing complexity, and enabling extensibility through composition rather than modification.

### III. Code Quality

All code MUST adhere to essential principles: SOLID, DRY, and KISS. Implementations MUST prioritize clean, readable design optimizing for learning and teaching value rather than excessive cleverness. Error handling MUST be explicit, logging failures rather than silencing them (e.g., avoid bare `except:` or silent `pass`).

**Rationale**: Readability and comprehensibility ensure maintainability and team velocity over long term, while explicit error handling prevents cryptic bugs.


### IV. Microservice Architecture

Distributed systems MUST be decomposed into microservices based on business capabilities. Each service MUST own its data store and expose a well-defined API. Services MUST communicate through lightweight protocols (REST, gRPC, or messaging). Service boundaries MUST align with bounded contexts from DDD.

**Rationale**: Microservices enable independent deployment, scaling, and technology choice per service while reducing blast radius of failures.

### V. Distributed Applications with Dapr

Distributed applications MUST use Dapr (Distributed Application Runtime) for cross-cutting concerns. Dapr building blocks MUST be used for: service invocation, state management, publish/subscribe messaging, resource bindings, and secrets management. Applications MUST remain portable across hosting environments by leveraging Dapr's abstraction layer.

**Rationale**: Dapr simplifies distributed system development by providing battle-tested building blocks while avoiding vendor lock-in.

### VI. Event-Driven Architecture

Asynchronous communication between services MUST follow Event-Driven Architecture (EDA) principles. Events MUST be immutable facts about something that happened. Event schemas MUST be versioned and validated. Publishers and consumers MUST be loosely coupled through an event broker. Event processing MUST be idempotent where possible.

**Rationale**: EDA enables temporal decoupling, scalability, and resilience by separating producers from consumers through an event log.

### VII. Library-First Architecture

Every feature MUST be implemented as a standalone library. Libraries MUST be self-contained, independently testable, and documented with a clear purpose. No organizational-only libraries that exist merely to group code without a distinct responsibility.

**Rationale**: Library boundaries enforce clear contracts and prevent coupling. Independent testability enables confident refactoring.

### VIII. CLI-First Interface

Every library MUST expose a command-line interface using a text in/out protocol: stdin/args → stdout, errors → stderr. Output MUST support both JSON (for machine consumption) and human-readable formats (for debugging).

**Rationale**: CLI-first ensures composability, debuggability, and enables scriptable automation without dependency on GUI toolkits.

### IX. Test-First Development (NON-NEGOTIABLE)

Red-Green-Refactor cycle MUST be strictly enforced using the `pytest` framework. Tests MUST be written before implementation, verified to fail, then implementation follows. All public contracts require contract tests. Integration tests are mandatory for inter-service communication and shared schemas.

**Rationale**: Test-first catches design flaws early, provides executable documentation, and enables confident continuous delivery.

### X. Contract Testing Mandate

Contract tests are REQUIRED for: new library APIs, breaking changes to existing APIs, inter-service communication protocols, and shared schema definitions. Contract tests MUST be versioned alongside the contracts they verify.

**Rationale**: Contract tests prevent integration failures by validating interface compatibility independently of implementation.

### XI. Observability by Default

All operations MUST produce structured logs with: timestamp, operation type, inputs (sanitized), outputs, and error details. Text I/O protocols MUST ensure debuggability without specialized tooling.

**Rationale**: Observable systems enable rapid diagnosis in production and reduce mean time to resolution.

### XII. Semantic Versioning

All libraries MUST follow Semantic Versioning (MAJOR.MINOR.PATCH). Breaking changes require MAJOR version bump with migration documentation. Deprecations MUST be announced in MINOR releases before removal in MAJOR.

**Rationale**: Predictable versioning enables consumers to assess upgrade impact without diving into changelogs.

### XIII. Python Standards & Tooling

Projects MUST be created using Python 3.12+ and manage dependencies using the `uv` package manager. The following Python-specific standards MUST be strictly followed:
- **Type Hints:** Comprehensive type hints are mandatory everywhere.
- **Docstrings:** All public functions, classes, and methods MUST have detailed docstrings with a clear focus on the "why" and "how" to support teaching and learning.
- **Data Structures:** Immutable or structured data MUST use `dataclasses`.

**Rationale**: Strong typing and thorough documentation eliminate ambiguity and streamline new developer onboarding, while modern tooling like UV ensures swift dependency resolution.

### XIV. FastAPI-First API Design

All HTTP APIs MUST be defined using FastAPI. API routes MUST be defined using Pydantic models for request validation and response serialization. OpenAPI schemas MUST be auto-generated and versioned with the API. API documentation MUST be accessible via `/docs` endpoint. Background tasks and WebSocket support MUST be used where appropriate.

**Rationale**: FastAPI provides automatic validation, OpenAPI generation, and async support while maintaining type safety through Pydantic. This reduces boilerplate and ensures consistent API contracts.

### XV. AI Agents with LangChain/LangGraph

AI-powered components MUST be implemented as Agents using LangChain and LangGraph. Agents MUST define clear tools, prompts, and state machines. Tool calling MUST have explicit schemas and error handling. Agent workflows MUST be represented as directed graphs with defined nodes and edges. Memory and context management MUST be explicit and configurable.

**Rationale**: LangChain/LangGraph provide structured frameworks for building reliable AI agents with observable, testable behavior.

### XVI. Infrastructure as Code

All infrastructure MUST be provisioned and managed using Infrastructure as Code (IaC). Declarative configuration MUST define desired state, and tooling MUST reconcile actual state. Infrastructure code MUST be version-controlled, reviewed, and tested. Drift detection MUST be enabled to detect unauthorized changes.

**Rationale**: IaC enables reproducible environments, version control for infrastructure changes, and consistent deployment across environments.

### XVII. Cloud Deployment (Azure)

Cloud-native applications MUST be deployed to Azure Services. Service deployment MUST use Azure Container Apps, Azure Kubernetes Service, or Azure App Service as appropriate. Managed services MUST be preferred over self-managed infrastructure. Bicep MUST be used for IaC.

**Rationale**: Azure provides enterprise-grade infrastructure with global availability, security compliance, and managed services that reduce operational burden.

### XVIII. Local Deployment (Podman)

Development and testing MUST use Podman for container orchestration. Podfiles or container definitions MUST be committed to the repository. Local development environments MUST be reproducible using `podman-compose up`. Container images MUST be tested locally before CI/CD deployment.

**Rationale**: Podman provides rootless containers that mirror Docker behavior while enhancing security. Consistent local environments reduce "works on my machine" issues.

### XIX. Distroless Container Security

All container images MUST use Distroless base images. Images MUST contain only application code and runtime dependencies. Shell access MUST NOT be available in production containers. Image scanning for vulnerabilities MUST be integrated into CI/CD pipelines. Container images MUST be signed and verified before deployment.

**Rationale**: Distroless images minimize attack surface by excluding unnecessary binaries and shells, reducing vulnerability exposure.

## Quality Assurance

- All PRs MUST pass contract and integration tests before merge
- Test coverage MUST meet a minimum of 80%
- Code review MUST verify principle compliance
- Complexity MUST be justified in architecture decision records
- No hardcoded secrets or tokens; use `.env` and environment variables
- Container images MUST be scanned for vulnerabilities before deployment
- IaC configurations MUST be validated with `terraform validate` or equivalent

## Development Workflow

- Keep all project files in git version control
- Feature branches follow pattern: `###-feature-name`
- Specs stored in `specs/[feature]/` with: spec.md, plan.md, tasks.md
- Use `/sp.plan`, `/sp.tasks`, `/sp.red`, `/sp.green` commands for iterative development
- Prompt History Records (PHRs) created for every user interaction
- Architecture Decision Records (ADRs) suggested for significant decisions
- Dapr building blocks used for distributed system patterns
- Azure services used for cloud deployment
- Podman used for local container development
- Distroless images used for all container deployments
- FastAPI used for all HTTP API definitions

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

**Version**: 1.3.0 | **Ratified**: 2026-04-12 | **Last Amended**: 2026-04-13
