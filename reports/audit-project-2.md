# Architecture Audit Report - Project 2 - ecommerce-api-legacy

Relatorio gerado para o Projeto 2 do desafio `refactor-arch`: `ecommerce-api-legacy/` (Node.js/Express).

## Phase 1 - Project Analysis

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Project:       ecommerce-api-legacy / desafio-arquitetura-ia-boilerplate
Language:      JavaScript / Node.js
Framework:     Express 4.x
Dependencies:  express ^4.18.2, sqlite3 ^5.1.6
Domain:        LMS API com fluxo de checkout, cursos, matriculas, pagamentos e relatorio financeiro
Architecture:  Monolito em uma classe central. AppManager misturava banco, seed, rotas, regras de negocio e respostas HTTP.
Source files:  3 source files analyzed before refactoring | approx 180 LOC
Database:      SQLite em memoria; tables users, courses, enrollments, payments, audit_logs
Entry point:   ecommerce-api-legacy/src/app.js | npm start
Endpoints:     3 endpoints: POST /api/checkout, GET /api/admin/financial-report, DELETE /api/users/:id
Validation:    npm start; request examples in ecommerce-api-legacy/api.http; node --check
================================
```

## Phase 2 - Audit Summary

- Stack: Node.js + Express + SQLite
- Files analyzed: 3 source files before refactoring
- Approx LOC: 180
- CRITICAL: 3
- HIGH: 3
- MEDIUM: 4
- LOW: 2
- Total findings: 12
- Deprecated API detection: checked; no framework deprecated API usage was identified in this project.

## Phase 2 - Findings

### [CRITICAL] Hardcoded secrets and production-like configuration

- File: `ecommerce-api-legacy/src/utils.js:1-7`
- Description: Database credentials, payment gateway key, SMTP user, and port were hardcoded in source code.
- Evidence: `dbPass`, `paymentGatewayKey`, `smtpUser`, and `port` were literal values.
- Impact: Secrets could be committed, leaked in reviews/logs, and reused across environments.
- Recommendation: Move configuration to an environment-driven settings module and keep secrets out of source code.
- Resolution in Phase 3: `src/utils.js` was removed; configuration now lives in `ecommerce-api-legacy/src/config/settings.js`.

### [CRITICAL] Sensitive payment data and gateway key logged

- File: `ecommerce-api-legacy/src/AppManager.js:45`
- Description: Checkout logged the full card value and payment gateway key.
- Evidence: `console.log` interpolated `cc` and `config.paymentGatewayKey`.
- Impact: Financial data and credentials could leak through stdout, container logs, or observability tools.
- Recommendation: Never log PAN/card data or secrets; log only safe metadata.
- Resolution in Phase 3: Payment flow was moved to services and no card number or gateway key is logged.

### [CRITICAL] Weak password storage and fake hashing

- File: `ecommerce-api-legacy/src/utils.js:17-23`, `ecommerce-api-legacy/src/AppManager.js:18`, `ecommerce-api-legacy/src/AppManager.js:68-69`
- Description: Seed users stored plaintext passwords and new users used a weak base64-based fake hash.
- Evidence: `badCrypto` repeated and truncated base64 fragments; seed password was `123`.
- Impact: User credentials would be easy to recover if database contents leaked.
- Recommendation: Use a real one-way password hashing mechanism with a per-user salt.
- Resolution in Phase 3: `ecommerce-api-legacy/src/services/passwordService.js` uses Node `crypto.scryptSync` with salt, without adding a dependency.

### [HIGH] God class owns all application responsibilities

- File: `ecommerce-api-legacy/src/AppManager.js:4-139`
- Description: `AppManager` initialized the database, seeded data, registered routes, executed checkout, built reports, deleted users, and formatted responses.
- Evidence: One class mixed persistence, routing, use cases, validation, logging, and HTTP response handling.
- Impact: Low cohesion, poor testability, and high change risk.
- Recommendation: Split into database, models/repositories, services/controllers, routes, config, and middlewares.
- Resolution in Phase 3: `AppManager.js` was removed and replaced by an MVC-style structure.

### [HIGH] Missing authorization on admin and destructive endpoints

- File: `ecommerce-api-legacy/src/AppManager.js:80-137`
- Description: Financial report and user deletion endpoints were exposed without authentication or authorization.
- Evidence: `GET /api/admin/financial-report` and `DELETE /api/users/:id` had no guard.
- Impact: Any client could read financial data or delete users.
- Recommendation: Add an authorization boundary for administrative/destructive routes.
- Resolution in Phase 3: `ecommerce-api-legacy/src/middlewares/adminAuth.js` enforces `x-admin-token` when `ADMIN_TOKEN` is configured.

### [HIGH] Fat route with checkout orchestration inside HTTP handler

- File: `ecommerce-api-legacy/src/AppManager.js:28-78`
- Description: The checkout route performed request parsing, validation, course lookup, user creation, payment simulation, enrollment creation, payment creation, audit logging, cache updates, and response formatting.
- Evidence: The entire use case lived inside the route callback.
- Impact: Business logic was hard to test without HTTP and SQLite callbacks.
- Recommendation: Keep routes thin and move orchestration to controller/service layers.
- Resolution in Phase 3: Route, controller, and service were separated into `checkoutRoutes.js`, `checkoutController.js`, and `checkoutService.js`.

### [MEDIUM] N+1 queries in financial report

- File: `ecommerce-api-legacy/src/AppManager.js:89-127`
- Description: The report queried enrollments per course, then users and payments per enrollment.
- Evidence: `db.all` and `db.get` ran inside nested loops.
- Impact: Runtime and callback complexity grow with the number of courses/enrollments.
- Recommendation: Use joins or batched model methods.
- Resolution in Phase 3: `ecommerce-api-legacy/src/models/financialReportModel.js` uses one `LEFT JOIN` query and groups rows in memory.

### [MEDIUM] Weak and inconsistent request validation

- File: `ecommerce-api-legacy/src/AppManager.js:29-35`
- Description: Legacy fields were read directly and only minimally validated.
- Evidence: `usr`, `eml`, `pwd`, `c_id`, and `card` were used directly in business flow.
- Impact: The external legacy request shape leaked into business logic.
- Recommendation: Add a compatibility adapter and validate normalized fields centrally.
- Resolution in Phase 3: `CheckoutService.normalizeInput` preserves legacy fields while mapping to descriptive internal names.

### [MEDIUM] Generic error handling and ignored database errors

- File: `ecommerce-api-legacy/src/AppManager.js:37-137`
- Description: Errors were handled with scattered string responses, and some callback errors were ignored.
- Evidence: Multiple callbacks returned generic strings such as `Erro DB`; delete always sent success text.
- Impact: Operational failures could be hidden or inconsistently reported.
- Recommendation: Centralize HTTP error handling and convert SQLite callbacks to predictable async flows.
- Resolution in Phase 3: SQLite calls are Promise-based; `AppError`, `asyncHandler`, and `errorHandler` centralize failures.

### [MEDIUM] User deletion leaves orphan records

- File: `ecommerce-api-legacy/src/AppManager.js:131-136`
- Description: User deletion did not handle enrollments or payments.
- Evidence: The response explicitly said related records stayed dirty.
- Impact: Reports and persistence state could become inconsistent.
- Recommendation: Enforce foreign keys, transactions, or explicit cleanup.
- Resolution in Phase 3: Schema enables `PRAGMA foreign_keys = ON` and uses `ON DELETE CASCADE` for related records.

### [LOW] Cryptic public request field names leak into business code

- File: `ecommerce-api-legacy/src/AppManager.js:29-33`
- Description: Checkout used abbreviated fields such as `usr`, `eml`, `pwd`, and `c_id` without a DTO boundary.
- Evidence: Route handler read those fields directly.
- Impact: The API contract was harder to understand and internal code used unclear names.
- Recommendation: Preserve backward compatibility but translate to descriptive internal fields.
- Resolution in Phase 3: Legacy fields remain supported, but normalized service input uses `name`, `email`, `password`, `courseId`, and `cardNumber`.

### [LOW] Global mutable state and unused revenue state

- File: `ecommerce-api-legacy/src/utils.js:9-25`
- Description: `globalCache` was process-wide mutable state and `totalRevenue` was exported/imported but unused.
- Evidence: `logAndCache` mutated a module-level object; `totalRevenue` had no meaningful use.
- Impact: Tests and runtime behavior become less predictable; unused code adds maintenance noise.
- Recommendation: Remove unused state and encapsulate cache behavior if still needed.
- Resolution in Phase 3: `utils.js` was removed; cache behavior is isolated in `ecommerce-api-legacy/src/services/cacheService.js`.

## Confirmation Checkpoint

The skill paused after Phase 2 and asked for explicit confirmation before changing files:

```text
Phase 2 complete. Proceed with MVC refactoring (Phase 3)? Reply with explicit confirmation before I modify files.
```

Confirmation received: `yes`.

## Phase 3 - Refactoring Complete

### New Project Structure

```text
ecommerce-api-legacy/
  src/
    app.js
    config/
      settings.js
    controllers/
      adminController.js
      checkoutController.js
      userController.js
    database/
      connection.js
    errors/
      AppError.js
    middlewares/
      adminAuth.js
      asyncHandler.js
      errorHandler.js
    models/
      auditLogModel.js
      courseModel.js
      enrollmentModel.js
      financialReportModel.js
      paymentModel.js
      userModel.js
    routes/
      adminRoutes.js
      checkoutRoutes.js
      userRoutes.js
    services/
      cacheService.js
      checkoutService.js
      financialReportService.js
      passwordService.js
      paymentService.js
      userService.js
```

### Changes Applied

- `ecommerce-api-legacy/src/app.js` now only composes Express, middleware, routes, database initialization, and server startup.
- `AppManager.js` was removed because its responsibilities were split across MVC layers.
- `utils.js` was removed because it contained hardcoded secrets, weak crypto, mutable global state, and unused exports.
- Configuration is environment-driven through `src/config/settings.js`.
- SQLite connection, schema, seeds, and helper methods live in `src/database/connection.js`.
- SQL access is isolated in `src/models/*`.
- Business flows live in `src/services/*`.
- HTTP translation lives in `src/controllers/*`.
- Express routes live in `src/routes/*`.
- Error handling is centralized in `src/middlewares/errorHandler.js`.
- Admin/destructive routes can be protected with `ADMIN_TOKEN`.
- Checkout uses a database transaction to avoid partial writes.
- Public endpoint paths and documented request/response behavior were preserved.

### Validation

- [x] Syntax check passed:

```powershell
Get-ChildItem ecommerce-api-legacy/src -Recurse -Filter *.js | ForEach-Object { node --check $_.FullName }
```

- [x] Application boot passed:

```powershell
$env:PORT='3100'; node ecommerce-api-legacy/src/app.js
```

Observed startup message:

```text
LMS API rodando na porta 3100...
```

- [x] Endpoint checks passed:

| Check | Result |
|---|---|
| `POST /api/checkout` with card starting with `4` | HTTP 200, `{"msg":"Sucesso","enrollment_id":2}` |
| `POST /api/checkout` with card not starting with `4` | HTTP 400 |
| `GET /api/admin/financial-report` | Returned course revenue and students |
| `DELETE /api/users/1` | Returned success text and cascaded related rows |
| `GET /api/admin/financial-report` with `ADMIN_TOKEN` set and no header | HTTP 403 |
| `GET /api/admin/financial-report` with `x-admin-token` | HTTP 200 |

## Checklist Against `doc-specs/tarefa.md`

### Phase 1 - Analysis

- [x] Language detected correctly: JavaScript/Node.js
- [x] Framework detected correctly: Express
- [x] Domain described correctly: LMS API with checkout flow
- [x] Source file count stated for the legacy project before refactoring

### Phase 2 - Audit

- [x] Report follows the skill audit structure: summary, findings, severity, impact, recommendation
- [x] Each finding includes file and exact line range
- [x] Findings are ordered from CRITICAL to LOW
- [x] At least 5 findings identified: 12 findings
- [x] At least 1 CRITICAL or HIGH finding included
- [x] At least 2 MEDIUM findings included
- [x] At least 2 LOW findings included
- [x] Deprecated API detection included: checked, not applicable
- [x] Skill paused and requested confirmation before Phase 3

### Phase 3 - Refactoring

- [x] Directory structure follows MVC responsibilities for an Express API
- [x] Configuration extracted to a config module without hardcoded secrets
- [x] Models created to abstract persistence
- [x] Views/Routes separated for HTTP routing
- [x] Controllers separated for request/response orchestration
- [x] Services separated for business flows
- [x] Error handling centralized
- [x] Entry point is clear
- [x] Application starts without errors
- [x] Original endpoints respond correctly

## Residual Risks

- `ADMIN_TOKEN` is optional to preserve local development compatibility. Production should set it or replace it with a real authentication/authorization layer.
- `npm install` reported 9 dependency vulnerabilities in the existing dependency tree. `npm audit fix --force` was not executed because it may introduce breaking dependency upgrades.
- Payment processing remains a deterministic simulation based on card prefix; it is not a real payment gateway integration.

## Course Deliverable Status

This file satisfies the Project 2 report requirement from `doc-specs/tarefa.md`: `reports/audit-project-2.md`.
