# Architecture Audit Report - Project 3 - task-manager-api

## Task Compliance Summary

This report documents the execution of the `refactor-arch` skill against `task-manager-api`, as requested for Project 3 in `doc-specs/tarefa.md`.

| Requirement | Status | Evidence |
|---|---|---|
| Phase 1 detects language, framework, domain, files, database and architecture | Done | See "Phase 1 - Project Analysis" |
| Phase 2 reports at least 5 findings | Done | 14 findings documented |
| Findings include at least 1 CRITICAL or HIGH | Done | 4 CRITICAL and 3 HIGH findings |
| Findings include at least 2 MEDIUM and 2 LOW issues | Done | 5 MEDIUM and 2 LOW findings |
| Findings have exact file/line ranges | Done | Each finding includes pre-refactor file and line range |
| Findings are ordered by severity | Done | CRITICAL -> HIGH -> MEDIUM -> LOW |
| Deprecated API detection considered | Done | SQLAlchemy `Query.get()` was found |
| Phase 2 pauses before file modification | Done | Human confirmation received: `yes` |
| Phase 3 creates MVC structure | Done | See "New Project Structure" |
| Phase 3 validates boot and endpoint behavior | Done | `compileall` plus representative endpoints checked with `Flask.test_client()` |
| Report saved to `reports/audit-project-3.md` | Done | This file |

## Phase 1 - Project Analysis

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Project:       task-manager-api
Language:      Python 3.13.11
Framework:     Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Dependencies:  flask, flask-sqlalchemy, flask-cors, marshmallow, requests, python-dotenv
Domain:        Task manager API with users, tasks, categories and reports
Architecture:  Partial MVC: folders existed, but routes owned validation, business logic, persistence and response formatting
Source files:  15 Python files analyzed | approx 969 LOC
Database:      SQLite via SQLAlchemy | users, tasks, categories
Entry point:   app.py | python app.py; seed: python seed.py
Endpoints:     22 endpoints, including /tasks, /users, /login, /reports/* and /categories
Validation:    README commands plus runtime checks with Flask.test_client()
================================
```

### Original Endpoint Inventory

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | API index |
| GET | `/health` | Health check |
| GET | `/tasks` | List tasks |
| GET | `/tasks/<task_id>` | Get task by id |
| POST | `/tasks` | Create task |
| PUT | `/tasks/<task_id>` | Update task |
| DELETE | `/tasks/<task_id>` | Delete task |
| GET | `/tasks/search` | Search tasks |
| GET | `/tasks/stats` | Task statistics |
| GET | `/users` | List users |
| GET | `/users/<user_id>` | Get user by id |
| POST | `/users` | Create user |
| PUT | `/users/<user_id>` | Update user |
| DELETE | `/users/<user_id>` | Delete user |
| GET | `/users/<user_id>/tasks` | List tasks for user |
| POST | `/login` | Login |
| GET | `/reports/summary` | Summary report |
| GET | `/reports/user/<user_id>` | User report |
| GET | `/categories` | List categories |
| POST | `/categories` | Create category |
| PUT | `/categories/<cat_id>` | Update category |
| DELETE | `/categories/<cat_id>` | Delete category |

## Phase 2 - Architecture Audit Report

### Summary

- Stack: Python + Flask + Flask-SQLAlchemy + SQLite
- Files analyzed: 15
- Approx LOC: 969
- CRITICAL: 4
- HIGH: 3
- MEDIUM: 5
- LOW: 2
- Total findings: 14

## Findings

### [CRITICAL] Hardcoded secrets and sensitive configuration

- File: `task-manager-api/app.py:11-13`, `task-manager-api/app.py:34`, `task-manager-api/services/notification_service.py:7-10`
- Description: Database URI, secret key, debug mode, public host and SMTP credentials were hardcoded.
- Evidence: literal `SQLALCHEMY_DATABASE_URI`, `SECRET_KEY`, `debug=True`, `smtp.gmail.com`, user and password.
- Impact: unsafe production defaults and credential leakage risk.
- Recommendation: move configuration to environment-backed settings.
- Phase 3 result: configuration now lives in `task-manager-api/config/settings.py`; SMTP settings are read from environment.

### [CRITICAL] Weak MD5 password hashing

- File: `task-manager-api/models/user.py:27-32`
- Description: Passwords were stored and checked with MD5.
- Evidence: `hashlib.md5(pwd.encode()).hexdigest()`.
- Impact: MD5 is unsuitable for password storage.
- Recommendation: use Werkzeug password hashing.
- Phase 3 result: new passwords use Werkzeug hashing; legacy MD5 checks remain compatible for existing seeded databases.

### [CRITICAL] Password hash exposed in API responses

- File: `task-manager-api/models/user.py:16-25`, `task-manager-api/routes/user_routes.py:207-210`
- Description: `User.to_dict()` returned the `password` field and login returned `user.to_dict()`.
- Evidence: response DTO included password material.
- Impact: credential hashes could leak to clients.
- Recommendation: remove password from public serializers.
- Phase 3 result: `User.to_dict()` no longer includes password.

### [CRITICAL] Fake predictable login token

- File: `task-manager-api/routes/user_routes.py:207-210`
- Description: login returned `fake-jwt-token-<user_id>`.
- Evidence: token was deterministic and not cryptographically signed.
- Impact: misleading and guessable authentication token.
- Recommendation: remove the fake token or generate a signed token.
- Phase 3 result: login preserves the `token` response field but uses `itsdangerous.URLSafeTimedSerializer`.

### [HIGH] Destructive endpoints without authorization

- File: `task-manager-api/routes/task_routes.py:156-238`, `task-manager-api/routes/user_routes.py:92-151`, `task-manager-api/routes/report_routes.py:167-223`
- Description: update/delete operations for tasks, users and categories had no auth or role checks.
- Evidence: public PUT/DELETE handlers mutate data directly.
- Impact: any client can alter or delete data.
- Recommendation: add a real auth/authorization boundary before production.
- Phase 3 result: mutation behavior was preserved for compatibility; this remains a residual product/security risk.

### [HIGH] Fat route handlers

- File: `task-manager-api/routes/task_routes.py:85-299`, `task-manager-api/routes/user_routes.py:42-211`, `task-manager-api/routes/report_routes.py:12-223`
- Description: route functions performed validation, persistence, calculations and response formatting.
- Evidence: route modules contained direct ORM queries, business rules and commit/rollback blocks.
- Impact: low testability and high coupling between HTTP and domain logic.
- Recommendation: move orchestration to controllers/services and keep routes thin.
- Phase 3 result: use-case flow moved to `task-manager-api/controllers/`; routes now only extract requests and map JSON responses.

### [HIGH] Stateful notification service with hardcoded external provider

- File: `task-manager-api/services/notification_service.py:4-47`
- Description: notifications were stored in process memory and SMTP credentials were embedded in code.
- Evidence: `self.notifications = []` and direct SMTP login with hardcoded values.
- Impact: state is lost across restarts and credentials are unsafe.
- Recommendation: read provider settings from environment and avoid assuming durable in-memory state.
- Phase 3 result: SMTP config now comes from environment; sending fails closed when SMTP is not configured.

### [MEDIUM] N+1 queries and query-in-loop patterns

- File: `task-manager-api/routes/task_routes.py:14-57`, `task-manager-api/routes/report_routes.py:53-68`, `task-manager-api/routes/report_routes.py:157-165`
- Description: related users/categories/tasks were queried inside loops.
- Evidence: `User.query.get(...)`, `Category.query.get(...)` and `Task.query.filter_by(...)` inside loops.
- Impact: list/report endpoints degrade as data grows.
- Recommendation: use relationships, eager loading, grouped counts or batched queries.
- Phase 3 result: task listing uses eager loading, category counts use grouped query, report user stats use in-memory grouping after one task load.

### [MEDIUM] Deprecated SQLAlchemy `Query.get()`

- File: `task-manager-api/routes/task_routes.py:67`, `task-manager-api/routes/user_routes.py:29`, `task-manager-api/routes/report_routes.py:105`
- Description: code used legacy SQLAlchemy 2.x lookup style.
- Evidence: `Task.query.get(...)`, `User.query.get(...)`, `Category.query.get(...)`.
- Impact: deprecation warnings and future upgrade risk.
- Recommendation: use `db.session.get(Model, id)`.
- Phase 3 result: lookups now use `db.session.get(...)`.

### [MEDIUM] Generic exception handling

- File: `task-manager-api/routes/task_routes.py:62-63`, `task-manager-api/routes/user_routes.py:130-132`, `task-manager-api/routes/report_routes.py:186-188`
- Description: bare `except:` blocks returned inconsistent generic messages.
- Evidence: repeated `except:` without typed exception handling or centralized logging.
- Impact: harder diagnosis and inconsistent rollback behavior.
- Recommendation: centralize error handling and catch database errors predictably.
- Phase 3 result: `task-manager-api/middlewares/error_handler.py` centralizes SQLAlchemy and unexpected exceptions.

### [MEDIUM] Weak and duplicated request validation

- File: `task-manager-api/routes/task_routes.py:110-114`, `task-manager-api/routes/user_routes.py:61-72`, `task-manager-api/routes/report_routes.py:196-202`
- Description: validation rules were repeated and some casts could raise 500 on bad input.
- Evidence: direct `int(...)` casts and repeated status/role arrays.
- Impact: inconsistent 400 responses and duplicated maintenance.
- Recommendation: share validation helpers and constants.
- Phase 3 result: shared constants/helpers are used by controllers; invalid search casts now return 400.

### [MEDIUM] Date and overdue logic duplicated

- File: `task-manager-api/routes/task_routes.py:30-39`, `task-manager-api/routes/user_routes.py:171-180`, `task-manager-api/routes/report_routes.py:33-43`
- Description: overdue calculation was repeated in several endpoints.
- Evidence: nested due-date/status checks duplicated `Task.is_overdue()`.
- Impact: domain rule can drift across routes.
- Recommendation: reuse a single domain helper.
- Phase 3 result: controllers now call `Task.is_overdue()`.

### [LOW] Duplicated magic values

- File: `task-manager-api/routes/task_routes.py:110`, `task-manager-api/routes/user_routes.py:71`, `task-manager-api/utils/helpers.py:110-116`
- Description: statuses, roles, limits and defaults appeared in multiple places.
- Evidence: repeated lists and numeric constraints.
- Impact: rules can diverge over time.
- Recommendation: keep shared constants in one module.
- Phase 3 result: controllers use constants from `task-manager-api/utils/helpers.py`.

### [LOW] Dead imports and noisy modules

- File: `task-manager-api/app.py:7`, `task-manager-api/routes/task_routes.py:7`, `task-manager-api/routes/user_routes.py:6`, `task-manager-api/utils/helpers.py:2-7`
- Description: unused imports were present across the project.
- Evidence: `os`, `sys`, `json`, `hashlib`, `math` and others were unused in several files.
- Impact: lower readability and maintainability.
- Recommendation: remove unused imports while refactoring.
- Phase 3 result: route and app imports were simplified; remaining imports are intentional.

## Confirmation Checkpoint

Phase 2 completed before any project file modification. The refactoring started only after explicit human confirmation:

```text
User confirmation: yes
```

## Phase 3 - MVC Refactoring Result

### New Project Structure

```text
task-manager-api/
├── app.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── controllers/
│   ├── __init__.py
│   ├── category_controller.py
│   ├── report_controller.py
│   ├── task_controller.py
│   └── user_controller.py
├── database.py
├── middlewares/
│   ├── __init__.py
│   └── error_handler.py
├── models/
│   ├── __init__.py
│   ├── category.py
│   ├── task.py
│   └── user.py
├── routes/
│   ├── __init__.py
│   ├── report_routes.py
│   ├── task_routes.py
│   └── user_routes.py
├── services/
│   ├── __init__.py
│   └── notification_service.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

### MVC Responsibility Mapping

| Layer | Files | Responsibility |
|---|---|---|
| Entry point / composition root | `task-manager-api/app.py` | Create Flask app, register CORS, database, error handlers and blueprints |
| Config | `task-manager-api/config/settings.py` | Environment-driven settings and safe defaults |
| Views / Routes | `task-manager-api/routes/*.py` | Declare endpoints, extract request data and serialize controller results |
| Controllers | `task-manager-api/controllers/*.py` | Coordinate validation, persistence calls, domain calculations and response payloads |
| Models | `task-manager-api/models/*.py` | SQLAlchemy mappings, safe serializers and small domain helpers |
| Services | `task-manager-api/services/notification_service.py` | External notification integration boundary |
| Middleware | `task-manager-api/middlewares/error_handler.py` | Central error-to-response mapping |

### Changes Applied

- Converted `task-manager-api/app.py` into an app factory and composition root.
- Added environment-backed configuration in `task-manager-api/config/settings.py`.
- Added central error handling in `task-manager-api/middlewares/error_handler.py`.
- Moved task, user, report and category use-case logic into controllers.
- Replaced route business logic with thin route functions.
- Replaced `Model.query.get(...)` with `db.session.get(...)`.
- Removed password material from user serializers.
- Replaced MD5 password creation with Werkzeug hashing while keeping legacy MD5 verification compatibility.
- Replaced fake login token with a signed token generated by `itsdangerous`.
- Reduced N+1 patterns in task listing and category/report aggregation.
- Moved SMTP configuration to environment variables and fail-closed behavior.

### Validation

Validation avoided mutating the local `tasks.db` by setting `DATABASE_URI=sqlite:///:memory:` and using `Flask.test_client()`.

| Check | Result |
|---|---|
| `python -m compileall .` from `task-manager-api/` | Passed |
| `GET /` | 200 |
| `GET /health` | 200 |
| `POST /users` | 201 |
| `POST /login` | 200 |
| `POST /categories` | 201 |
| `POST /tasks` | 201 |
| `GET /tasks` | 200 |
| `GET /tasks/stats` | 200 |
| `GET /reports/summary` | 200 |
| login user payload includes password | False |
| login response includes token | True |

### Checklist From `doc-specs/tarefa.md`

#### Phase 1 - Analysis

- [x] Linguagem detectada corretamente: Python
- [x] Framework detectado corretamente: Flask
- [x] Domínio da aplicação descrito corretamente: Task Manager API
- [x] Número de arquivos analisados condiz com a realidade: 15 Python files

#### Phase 2 - Audit

- [x] Relatório segue template estruturado
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade
- [x] Mínimo de 5 findings identificados
- [x] Detecção de APIs deprecated incluída
- [x] Skill pausou e pediu confirmação antes da Fase 3

#### Phase 3 - Refactoring

- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

## Residual Risks and Trade-offs

- The API still has no real authorization layer. Destructive endpoints are preserved for compatibility but should not be exposed publicly without auth/role checks.
- The default `SECRET_KEY` is development-only. Production must set `SECRET_KEY` in the environment.
- Legacy MD5 password verification is retained only for compatibility with existing seeded databases; new passwords use Werkzeug hashing.
- There was no automated test suite in the repository; validation used compilation and representative Flask endpoint checks.
