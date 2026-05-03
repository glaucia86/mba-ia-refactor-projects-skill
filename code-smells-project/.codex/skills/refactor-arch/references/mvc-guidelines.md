# MVC Architecture Guidelines

Use MVC as the target architecture, adapting names to the framework.

## Layer Responsibilities

| Layer | API project interpretation | Must contain | Must not contain |
|---|---|---|---|
| Entry point / composition root | App factory or server bootstrap | App creation, middleware registration, route registration, config loading | Business rules, SQL, request validation details |
| Config | Settings module | Environment reads, defaults, constants, safe debug settings | Secrets committed in code |
| Models / Repositories | Data access and persistence mapping | ORM models, SQL queries, serialization helpers, repository methods | HTTP response objects, route decorators |
| Views / Routes | HTTP route declarations | URL mapping, request extraction, response mapping | Business workflows, database loops, payment or notification logic |
| Controllers / Services | Application orchestration | Validation calls, use-case flow, transaction coordination, domain calculations | Framework bootstrapping, raw global config |
| Middlewares / Error handlers | Cross-cutting HTTP behavior | Error-to-response mapping, CORS/security middleware, request logging | Domain-specific decisions |

## Python/Flask Target

Prefer:

```text
config/
  settings.py
models/
  <domain>_model.py
controllers/
  <domain>_controller.py
routes/
  <domain>_routes.py
middlewares/
  error_handler.py
app.py
```

For Flask APIs, `routes/` is the MVC View layer.

## Node.js/Express Target

Prefer:

```text
src/
  config/
    settings.js
  database/
    connection.js
  models/
    <domain>Model.js
  controllers/
    <domain>Controller.js
  routes/
    <domain>Routes.js
  middlewares/
    errorHandler.js
  app.js
```

For Express APIs, `routes/` is the MVC View layer.

## Refactoring Constraints

- Preserve documented routes and response shape unless fixing a security leak requires removing sensitive fields.
- Keep database choice and seed behavior unless the user asks for migration.
- Prefer small, reviewable moves over a full rewrite.
- Leave compatibility adapters when request field names are legacy but public API examples depend on them.
- Centralize constants only when duplication is meaningful.
- Do not hide validation failures; report exact commands and remaining failures.
