---
name: refactor-arch
description: Audit and refactor backend projects to an MVC architecture. Use when Codex needs to analyze a codebase, detect language/framework/database and current architecture, classify architecture/security/code-quality anti-patterns with exact file lines, generate an audit report, pause for human confirmation, refactor to Model-View-Controller, and validate boot plus endpoint behavior. Applies to Python/Flask, Node.js/Express, and similar API projects.
---

# Refactor Arch

Use this skill to run a three-phase architecture audit and MVC refactoring on a backend project. Keep the workflow technology-agnostic: infer the stack from the repository, preserve public API behavior, and adapt the target MVC structure to the language and framework already present.

## Required Workflow

### Phase 1 - Project Analysis

Read the project before changing anything.

1. Inspect the directory tree, README, dependency manifests, entry points, route files, database files, and test or request examples.
2. Detect language, framework, package manager, database, source files, domain concepts, current architecture, and validation commands.
3. Map routes/endpoints and persistence boundaries.
4. Print a concise summary using the format from `references/audit-report-template.md`.

Read `references/project-analysis.md` for stack detection and architecture mapping heuristics.

### Phase 2 - Architecture Audit

Audit the code without modifying files.

1. Cross-check source files against `references/antipattern-catalog.md`.
2. Record each finding with exact file and line range.
3. Classify severities as CRITICAL, HIGH, MEDIUM, or LOW.
4. Include deprecated API usage when present.
5. Generate the report using `references/audit-report-template.md`.
6. Save the report when the user or task requests an output path.
7. Stop and ask for explicit confirmation before Phase 3.

Do not edit project files during Phase 2. The confirmation checkpoint is mandatory.

### Phase 3 - MVC Refactoring

Proceed only after explicit confirmation.

1. Create or improve an MVC structure using `references/mvc-guidelines.md`.
2. Apply the transformations from `references/refactoring-playbook.md`.
3. Preserve endpoint paths, HTTP methods, request/response shapes, seed data behavior, and documented run commands unless the user approves a breaking change.
4. Extract configuration and secrets to environment-driven settings.
5. Parameterize database queries and remove unsafe dynamic execution.
6. Move business flow to controllers/services, persistence to models/repositories, and routing to views/routes.
7. Add centralized error handling where the framework supports it.
8. Validate the result: application boot plus representative endpoint checks from README, `api.http`, tests, or discovered routes.

If validation cannot run because dependencies or runtime tools are missing, report the exact blocker and provide the manual command sequence.

## Output Requirements

For every run, produce:

- Phase 1 summary with detected stack and architecture.
- Phase 2 audit report ordered CRITICAL -> HIGH -> MEDIUM -> LOW.
- A confirmation prompt before any file modification.
- Phase 3 summary with changed structure, anti-patterns fixed, validation commands, and residual risks.

For course-style deliverables, also create `reports/audit-project-N.md` and update the repository README with manual analysis, skill construction notes, results, and execution instructions.

## Reference Files

- `references/project-analysis.md`: language/framework/database and architecture detection.
- `references/antipattern-catalog.md`: severity scale and anti-pattern detection signals.
- `references/audit-report-template.md`: required Phase 1, Phase 2, and Phase 3 report formats.
- `references/mvc-guidelines.md`: target MVC responsibilities and directory conventions.
- `references/refactoring-playbook.md`: concrete before/after transformations.
