## Quick context for AI coding agents

This repository implements a small commercial core (products + sales) with SQLite persistence and a layered design: domain models, infra (SQL repositories), services (application logic), and a simple CLI in `main.py`.

Key responsibilities:
- Persistence and schema: `infra/forja_persistencia.py` (creates `data/mercado.sqlite3` and indexes).
- Domain: `domain/modelos.py` (dataclasses `Produto`, `Venda` with domain validations).
- Repositories: `infra/repositorios.py` (`RepositorioProdutoSQL`, `RepositorioVendaSQL`) — use parameterized SQL and store ISO datetimes in `vendas.data_venda`.
- Application: `services/servicos.py` (`OrquestradorDeFluxoComercial`) — handles transactions: adjust stock + insert sale inside `with conn:` blocks.

Practical notes for code changes
- Database file lives at `data/mercado.sqlite3` (created on first run by `ForjaDePersistencia.criar_esquema`). Use `ForjaDePersistencia.conectar()` for tests or scripts to reuse the same configuration.
- Mutating operations must run inside a transaction (`with conn:`) to preserve consistency (see `OrquestradorDeFluxoComercial.registrar_venda`).
- Dates are persisted as ISO strings and parsed with `datetime.fromisoformat(...)` in repositories.
- When adding schema changes, prefer lightweight, in-place migrations in `ForjaDePersistencia.criar_esquema()` (the project already alters `vendas` to add `preco_unitario` if missing).

Style & conventions
- Python 3.9+ typing and `from __future__ import annotations` are used across the codebase.
- Domain objects are `dataclasses` with validation in `__post_init__` — keep validations there rather than scattering checks in services when possible.
- Repositories return domain objects (not raw dicts/rows). Follow existing constructors in `infra/repositorios.py` for field conversion.

Developer workflows
- Run CLI demo: `python main.py` (creates DB and shows interactive menu).
- Optional HTTP API: install `fastapi` + `uvicorn` and run `uvicorn api.main:app --reload` (see `README.md`).
- No external dependencies are required for the core persistence module — tests and scripts can instantiate `ForjaDePersistencia` and reuse `data/mercado.sqlite3`.

Files to inspect when changing behavior
- `infra/forja_persistencia.py` — DB path, PRAGMA, DDL and simple migration code.
- `infra/repositorios.py` — SQL statements, row -> domain mappings, ordering and index usage.
- `services/servicos.py` — transaction boundaries and business error messages.
- `domain/modelos.py` — input validation rules and field names used across the app.
- `main.py` — example usage and simple CLI flows; good for writing integration tests.

Search examples to reference
- Look for `with self.conn:` to find places that require transaction-aware changes.
- Look for `.isoformat()` and `fromisoformat` to find datetime persist/parse paths.

Edge cases and safety
- Repository methods raise `ValueError` for domain errors (e.g., nonexistent product, insufficient stock). Preserve these exceptions for the CLI and API layers.
- Avoid raw string concatenation for SQL; reuse parameterized patterns shown in `infra/repositorios.py`.

If you modify schema or introduce background tasks, add corresponding updates to `ForjaDePersistencia.criar_esquema()` and include a safe migration path similar to the existing `ALTER TABLE` usage.

When in doubt, run the CLI (`python main.py`) as a smoke test after changes.

If anything above is incomplete or you need more examples, reply what area you want expanded (DB, services, tests, or API).
