# Anti-Pattern Catalog

Use this catalog in Phase 2. Findings must include exact file and line range, severity, description, impact, and recommendation.

## Severity Scale

- CRITICAL: Security flaws, unsafe external execution, sensitive data exposure, or complete responsibility collapse that can break correctness.
- HIGH: Strong MVC/SOLID violations that make the system hard to test, maintain, or evolve.
- MEDIUM: Validation, performance, consistency, or reliability problems with moderate impact.
- LOW: Readability, naming, duplication, magic values, or cleanup issues.

## Required Anti-Patterns

| Anti-pattern | Severity | Detection signals | Recommendation |
|---|---:|---|---|
| Hardcoded secrets/config | CRITICAL | Secret keys, passwords, API keys, debug flags, DB paths, or gateway keys committed in source | Move to env-driven config and never return secrets in responses |
| SQL injection / unsafe dynamic query | CRITICAL | SQL built by concatenating request data or endpoint executing arbitrary SQL | Use parameterized queries or ORM filters with typed inputs |
| God class / god module | CRITICAL/HIGH | One class/file owns routing, database, business flow, validation, logging, and formatting | Split into routes/views, controllers/services, models/repositories |
| Sensitive data in API response or logs | CRITICAL/HIGH | Password hashes, secret keys, card numbers, raw exception messages, or internal DB path exposed | Sanitize serializers, use safe logs, return generic errors |
| Weak password storage / crypto | CRITICAL/HIGH | Plaintext passwords, MD5, base64 loops, fake hashing, short hardcoded tokens | Use framework password hashing or a strong one-way KDF already available |
| Fat controller / route business logic | HIGH | Route functions perform validation, persistence, calculations, notifications, and response formatting | Move orchestration to controllers/services and keep routes thin |
| Global mutable state / unsafe shared connection | HIGH | Module-level cache, revenue counters, global DB connection shared across requests, `check_same_thread=False` | Encapsulate state and manage connection lifecycle |
| Missing authorization for admin/destructive endpoints | HIGH | Admin reset, arbitrary query, financial report, delete user exposed without auth/role checks | Add auth/authorization boundary or remove unsafe endpoint |
| N+1 queries / query in loop | MEDIUM | Database calls inside loops, nested callbacks per row/entity | Use joins/eager loading/batched queries |
| Validation duplication or weak validation | MEDIUM | Repeated manual field checks, untyped casts, missing range/date/email validation | Centralize request validation helpers/schemas |
| Deprecated API usage | MEDIUM | Framework APIs marked legacy, e.g. SQLAlchemy `Model.query.get(...)` in SQLAlchemy 2.x | Replace with modern API such as `db.session.get(Model, id)` |
| Generic error handling | MEDIUM | Bare `except`, `catch` returning strings, raw `str(e)` to clients | Centralize error handling and return consistent JSON |
| Magic values and duplicated constants | LOW | Repeated status arrays, thresholds, ports, category lists, messages | Extract constants near domain/service layer |
| Poor naming / unclear DTO fields | LOW | Cryptic request fields like `usr`, `eml`, `pwd`, `c_id` without translation boundary | Normalize request DTOs while preserving backward compatibility |
| Dead or unused imports/exports | LOW | Imported modules, variables, or functions never used | Remove or use intentionally |

## Sorting Rule

Sort findings by severity first, then by file path and line. Include at least five findings per target project when present.
