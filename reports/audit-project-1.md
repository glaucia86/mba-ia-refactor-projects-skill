# Architecture Audit Report - Project 1 - code-smells-project

## Task Compliance Summary

This report documents the execution of the `refactor-arch` skill against `code-smells-project`, as requested for Project 1 in `doc-specs/tarefa.md`.

| Requirement | Status | Evidence |
|---|---|---|
| Phase 1 detects language, framework, domain, files, database and architecture | Done | See "Phase 1 - Project Analysis" |
| Phase 2 reports at least 5 findings | Done | 12 findings documented |
| Findings include at least 1 CRITICAL or HIGH | Done | 5 CRITICAL and 3 HIGH findings |
| Findings have exact file/line ranges | Done | Each finding includes original file and line range |
| Findings are ordered by severity | Done | CRITICAL -> HIGH -> MEDIUM -> LOW |
| Deprecated API detection considered | Done | No deprecated framework API usage was found in the audited stack |
| Phase 2 pauses before file modification | Done | Human confirmation received: `Yes` |
| Phase 3 creates MVC structure | Done | See "New Project Structure" |
| Phase 3 validates boot and endpoint behavior | Done | `compileall` plus all original routes checked with `Flask.test_client()` |
| Report saved to `reports/audit-project-1.md` | Done | Synchronized from this report |

## Phase 1 - Project Analysis

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Project:       code-smells-project
Language:      Python
Framework:     Flask
Dependencies:  flask==3.1.1, flask-cors==5.0.1
Domain:        E-commerce API with products, users, orders and sales reports
Architecture:  Partial MVC by name only; routing, HTTP handling, validation,
               persistence, business rules and serialization were mixed across
               root-level modules
Source files:  4 original Python files analyzed
Database:      SQLite | produtos, usuarios, pedidos, itens_pedido
Entry point:   app.py | python app.py
Endpoints:     19 original routes, including /produtos, /usuarios, /login,
               /pedidos, /relatorios/vendas, /health and /admin/*
Validation:    README commands plus runtime checks with Flask.test_client()
================================
```

### Original Source Inventory

| File | Role before refactoring | Main issue |
|---|---|---|
| `app.py` | Flask app bootstrap, route registration and admin route handlers | Composition root mixed with route logic and unsafe admin behavior |
| `controllers.py` | HTTP handlers for products, users, orders, reports and health | Fat controllers with validation, response mapping and side effects |
| `models.py` | SQLite queries, business workflows, DTO serialization and report calculations | Repository, domain logic and serialization collapsed into one module |
| `database.py` | SQLite connection, schema creation and seed data | Global mutable connection and hardcoded database path |

### Original Endpoint Inventory

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | API index |
| GET | `/health` | Health and database status |
| GET | `/produtos` | List products |
| GET | `/produtos/busca` | Search products |
| GET | `/produtos/<id>` | Get product by id |
| POST | `/produtos` | Create product |
| PUT | `/produtos/<id>` | Update product |
| DELETE | `/produtos/<id>` | Delete product |
| GET | `/usuarios` | List users |
| GET | `/usuarios/<id>` | Get user by id |
| POST | `/usuarios` | Create user |
| POST | `/login` | Authenticate user |
| GET | `/pedidos` | List all orders |
| POST | `/pedidos` | Create order |
| GET | `/pedidos/usuario/<usuario_id>` | List orders by user |
| PUT | `/pedidos/<pedido_id>/status` | Update order status |
| GET | `/relatorios/vendas` | Sales report |
| POST | `/admin/reset-db` | Reset database |
| POST | `/admin/query` | Execute arbitrary SQL |

## Phase 2 - Architecture Audit Report

### Summary

- Stack: Python + Flask + SQLite
- Original files analyzed: 4
- CRITICAL: 5
- HIGH: 3
- MEDIUM: 3
- LOW: 1
- Total findings: 12
- Deprecated API usage: none found in the audited Flask/sqlite3 code

## Findings

### [CRITICAL] Arbitrary SQL Execution Endpoint

- File: `code-smells-project/app.py:59-78`
- Description: The `/admin/query` endpoint executed SQL received directly from the request body.
- Evidence: `cursor.execute(query)` used request-controlled input without allowlist, authorization or parameter binding.
- Impact: Any caller could read, modify or delete arbitrary database data.
- Recommendation: Disable the endpoint unless a real authenticated administrative boundary exists. Never expose arbitrary SQL execution through the public API.
- Phase 3 result: route preserved for compatibility, but now returns `403` with `{"erro": "Endpoint administrativo desabilitado", "sucesso": false}`.

### [CRITICAL] SQL Injection Through String Concatenation

- File: `code-smells-project/models.py:28-299`
- Description: Multiple SQL queries were built by concatenating request-controlled values.
- Evidence: vulnerable patterns existed in product lookup/create/update/delete, login, user creation, order creation, order listing, status update and product search.
- Impact: Attackers could alter SQL behavior, bypass authentication, read sensitive data or corrupt records.
- Recommendation: Replace all dynamic SQL concatenation with SQLite parameterized queries using `?` placeholders.
- Phase 3 result: data access was moved to domain model modules and external inputs are passed via query parameters.

### [CRITICAL] Plaintext Password Storage and Password Exposure

- File: `code-smells-project/database.py:75-83`, `code-smells-project/models.py:72-103`, `code-smells-project/models.py:122-129`
- Description: Seed users and newly created users stored plaintext passwords, and user list/detail responses returned the `senha` field.
- Evidence: seed values included `admin123`, `123456` and `senha123`; serializers exposed `"senha": row["senha"]`.
- Impact: Any user-listing response leaked credentials and database compromise exposed reusable passwords.
- Recommendation: Store passwords with a one-way password hashing function and never include password material in API responses.
- Phase 3 result: new passwords use Werkzeug hashing, legacy plaintext passwords are upgraded after a successful login, and user serializers omit `senha`.

### [CRITICAL] Hardcoded Secret, Debug Mode and Internal Configuration Leak

- File: `code-smells-project/app.py:7-8`, `code-smells-project/app.py:88`, `code-smells-project/controllers.py:276-290`
- Description: Flask secret key and debug mode were hardcoded, and `/health` returned internal configuration details.
- Evidence: `SECRET_KEY` used a literal value; `DEBUG` and `app.run(..., debug=True)` forced debug mode; `/health` returned `db_path`, `debug` and `secret_key`.
- Impact: Sensitive configuration could leak to clients, and debug behavior increases production risk.
- Recommendation: Move configuration to environment-backed settings and keep health responses limited to operational status.
- Phase 3 result: configuration moved to `config/settings.py`; `/health` no longer returns `secret_key`, `debug` or database path.

### [CRITICAL] Destructive Administrative Reset Without Authorization

- File: `code-smells-project/app.py:47-57`
- Description: `/admin/reset-db` deleted all data from the core tables without authentication or authorization.
- Evidence: the route executed `DELETE FROM itens_pedido`, `pedidos`, `produtos` and `usuarios` directly.
- Impact: Any caller could destroy all application data.
- Recommendation: Remove or disable the route until a real administrative authorization layer exists.
- Phase 3 result: route preserved for compatibility, but now returns `403`.

### [HIGH] Global Mutable SQLite Connection Shared Across Requests

- File: `code-smells-project/database.py:4-11`
- Description: the application stored a module-level global SQLite connection with `check_same_thread=False`.
- Evidence: `db_connection = None` and `sqlite3.connect(db_path, check_same_thread=False)`.
- Impact: request concurrency can produce inconsistent transactions and hard-to-debug state leaks.
- Recommendation: use Flask application/request context for connection lifecycle.
- Phase 3 result: `database.get_db()` now stores the connection in Flask `g`, and `teardown_appcontext` closes it.

### [HIGH] Fat Controllers Mixing HTTP, Validation, Domain Flow and Side Effects

- File: `code-smells-project/controllers.py:24-292`
- Description: controller functions parsed requests, validated payloads, orchestrated persistence, printed notifications and formatted HTTP responses.
- Evidence: `criar_pedido` validated order payloads, called persistence, printed email/SMS/push messages and returned HTTP JSON in the same function.
- Impact: low testability, high coupling to Flask and difficult evolution of business rules.
- Recommendation: keep routes thin and move validation/use-case orchestration to controllers/services with persistence isolated in models/repositories.
- Phase 3 result: HTTP routing moved to `routes/`, orchestration to `controllers/` and validation helpers to `services/validation.py`.

### [HIGH] God Model Module With Persistence, Domain Logic and Serialization

- File: `code-smells-project/models.py:4-314`
- Description: one module owned product queries, user auth, order creation, stock updates, order serialization and sales-report calculation.
- Evidence: `criar_pedido`, `relatorio_vendas`, `buscar_produtos`, `login_usuario` and serializers all lived in the same file.
- Impact: changes to one domain risk regressions in unrelated flows; behavior is difficult to test in isolation.
- Recommendation: split persistence by domain and keep business calculations close to their use case.
- Phase 3 result: split into `models/product_model.py`, `models/user_model.py` and `models/order_model.py`.

### [MEDIUM] N+1 Queries in Order Listing

- File: `code-smells-project/models.py:171-233`
- Description: order listing loaded items per order and product names per item.
- Evidence: nested `cursor2` and `cursor3` queries ran inside loops over orders and items.
- Impact: response time grows quickly as order volume increases.
- Recommendation: use JOINs or batched lookups.
- Phase 3 result: order items and product names are loaded with batched `IN (...)` queries and a `LEFT JOIN`.

### [MEDIUM] Raw Exception Details Returned to Clients

- File: `code-smells-project/controllers.py:10-292`, `code-smells-project/app.py:77-78`
- Description: route handlers returned `str(e)` to clients for server errors.
- Evidence: repeated `return jsonify({"erro": str(e)}), 500`.
- Impact: SQL errors, internal paths or implementation details could leak through API responses.
- Recommendation: centralize error handling and return generic messages for unexpected server errors.
- Phase 3 result: `middlewares/error_handler.py` centralizes HTTP and generic exception handling.

### [MEDIUM] Duplicated and Inconsistent Request Validation

- File: `code-smells-project/controllers.py:24-96`, `code-smells-project/controllers.py:146-186`, `code-smells-project/controllers.py:188-255`
- Description: validation rules were repeated manually across controller functions and did not consistently validate types.
- Evidence: product create/update duplicated required-field and range checks; price filters cast directly to `float`.
- Impact: maintenance overhead and avoidable 500 responses on malformed input.
- Recommendation: centralize validation helpers while preserving public request fields.
- Phase 3 result: validation helpers were introduced in `services/validation.py`.

### [LOW] Magic Values and Domain Constants Inline

- File: `code-smells-project/controllers.py:52-54`, `code-smells-project/controllers.py:242-243`, `code-smells-project/models.py:256-262`
- Description: valid categories, valid order statuses and discount thresholds were embedded inline.
- Evidence: literal arrays and threshold values were defined inside handlers/calculation functions.
- Impact: rules are harder to reuse and change consistently.
- Recommendation: move shared domain constants to a service/domain module.
- Phase 3 result: categories and order statuses moved to `services/validation.py`; discount logic remains encapsulated in `models/order_model.py`.

## Confirmation Checkpoint

Phase 2 completed before any project file modification. The refactoring started only after explicit human confirmation:

```text
User confirmation: Yes
```

## Phase 3 - MVC Refactoring Result

### New Project Structure

```text
code-smells-project/
├── app.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── controllers/
│   ├── __init__.py
│   ├── order_controller.py
│   ├── product_controller.py
│   ├── report_controller.py
│   ├── system_controller.py
│   └── user_controller.py
├── database.py
├── middlewares/
│   ├── __init__.py
│   └── error_handler.py
├── models/
│   ├── __init__.py
│   ├── order_model.py
│   ├── product_model.py
│   └── user_model.py
├── routes/
│   ├── __init__.py
│   ├── admin_routes.py
│   ├── order_routes.py
│   ├── product_routes.py
│   ├── report_routes.py
│   ├── system_routes.py
│   └── user_routes.py
└── services/
    ├── __init__.py
    └── validation.py
```

### MVC Responsibility Mapping

| Layer | Files | Responsibility |
|---|---|---|
| Entry point / composition root | `app.py` | Create Flask app, register middleware/routes/database and run server |
| Config | `config/settings.py` | Read environment-driven settings |
| Views / Routes | `routes/*.py` | Declare URL paths, methods, request extraction and JSON response mapping |
| Controllers | `controllers/*.py` | Coordinate use cases and return payload/status tuples |
| Models / Repositories | `models/*.py`, `database.py` | SQLite persistence, schema, seed data and safe serializers |
| Services | `services/validation.py` | Shared validation rules and domain constants |
| Middleware | `middlewares/error_handler.py` | Central error-to-response behavior |

### Changes Applied

- Converted route registration to Flask Blueprints under `routes/`.
- Converted `app.py` into a clear composition root.
- Extracted environment-backed configuration to `config/settings.py`.
- Replaced the global SQLite connection with Flask app-context connection management.
- Split the old `models.py` into product, user and order model modules.
- Parameterized SQL statements that use external input.
- Disabled unsafe administrative routes while preserving their original paths.
- Added password hashing for new users and opportunistic upgrade for legacy plaintext passwords.
- Removed password fields from user list/detail API responses.
- Sanitized `/health` by removing secret/debug/database-path fields.
- Centralized unexpected error handling.
- Replaced N+1 order item/product lookup with batched queries.
- Added project documentation and this audit report.

### Endpoint Validation

Validation used a temporary database file (`validation-temp.db`) so write operations could be tested without mutating the normal `loja.db`.

| Check | Result |
|---|---|
| `python -m compileall .` | Passed |
| `GET /` | 200 |
| `GET /health` | 200 |
| `GET /produtos` | 200 |
| `GET /produtos/1` | 200 |
| `GET /produtos/busca?q=Mouse` | 200 |
| `POST /produtos` | 201 |
| `PUT /produtos/11` | 200 |
| `DELETE /produtos/11` | 200 |
| `GET /usuarios` | 200 |
| `GET /usuarios/1` | 200 |
| `POST /usuarios` | 201 |
| `POST /login` | 200 |
| `GET /pedidos` | 200 |
| `POST /pedidos` | 201 |
| `GET /pedidos/usuario/1` | 200 |
| `PUT /pedidos/1/status` | 200 |
| `GET /relatorios/vendas` | 200 |
| `POST /admin/reset-db` | 403 |
| `POST /admin/query` | 403 |

Additional security checks:

- `/health` response does not include `secret_key`, `debug` or `db_path`.
- `/usuarios` response does not include `senha`.
- `/admin/query` does not execute submitted SQL and returns `403`.

### Checklist From `tarefa.md`

#### Phase 1 - Analysis

- [x] Linguagem detectada corretamente: Python
- [x] Framework detectado corretamente: Flask
- [x] Domínio da aplicação descrito corretamente: E-commerce API
- [x] Número de arquivos analisados condiz com a realidade: 4 original Python source files

#### Phase 2 - Audit

- [x] Relatório segue template estruturado
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade
- [x] Mínimo de 5 findings identificados
- [x] Detecção de APIs deprecated considerada
- [x] Skill pausou e pediu confirmação antes da Fase 3

#### Phase 3 - Refactoring

- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config
- [x] Models criados para abstrair dados/persistência
- [x] Views/Routes separadas para roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

## Residual Risks and Trade-offs

- The project still has no real authentication/authorization layer. For that reason, administrative routes remain disabled instead of protected.
- SQLite is preserved because it is the existing project database and is sufficient for the course exercise, but it is not a production-grade choice for high write concurrency.
- The report uses original pre-refactor file/line ranges for Phase 2 findings, because the vulnerable files were later split or removed during Phase 3.
- No automated test suite existed in the repository; validation was performed through compilation and Flask runtime endpoint checks.
