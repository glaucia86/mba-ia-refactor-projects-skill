# Project Analysis Heuristics

Use these heuristics in Phase 1 before auditing or refactoring.

## Stack Detection

| Signal | Interpretation |
|---|---|
| `requirements.txt`, `.py`, `Flask(...)`, `Blueprint` | Python/Flask API |
| `flask_sqlalchemy`, `SQLAlchemy()` | Flask with SQLAlchemy ORM |
| `sqlite3.connect`, `.db` file, SQL strings | SQLite persistence |
| `package.json`, `express`, `app.listen` | Node.js/Express API |
| `sqlite3.Database` | Node.js with SQLite |
| `api.http`, `README`, route decorators, `app.get/post/put/delete` | Endpoint inventory source |

## Architecture Mapping

Classify the current shape:

- Monolith: one or two large files own routing, business logic, persistence, and config.
- Layered partial MVC: folders such as `models/`, `routes/`, `services/`, `utils/` exist, but responsibilities leak across layers.
- MVC-ready: entry point composes config, routes, controllers, models/repositories, and error handlers without business logic in route declarations.

## Phase 1 Inventory

Collect:

- Project name and domain from README, route names, entities, seed data, and table names.
- Entry point and boot command.
- Dependencies and versions from manifest files.
- Route list: method, path, handler, expected request body if obvious.
- Database tables/models and relationships.
- Source file count and approximate line count, excluding generated folders and dependency directories.
- Validation commands: package scripts, Python run commands, request examples, test commands.

## Agnostic Rules

- Do not assume MVC folder names are identical across frameworks; adapt names to local conventions.
- Treat HTTP route modules as MVC Views when the project is an API and has no rendered templates.
- Prefer the existing language, package manager, database, and framework.
- Avoid adding dependencies unless a security or validation requirement cannot be met with standard libraries or existing packages.
