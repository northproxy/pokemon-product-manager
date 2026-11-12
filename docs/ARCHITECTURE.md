# Architecture

Status: Proposed. See the [decision log](../DECISIONS.md) for acceptance criteria.

A mobile-first web frontend would call one backend API backed by one PostgreSQL 17 database. Manual import commands would use the same Python package as the API. Raw market files would remain available for replay and reconciliation. The web client would access data through the API.

## Module responsibilities

| Module | Responsibility |
| --- | --- |
| `catalogue` | Canonical cards, expansions, sealed definitions, language and packaging versions, and evidence-backed contents. |
| `wishlist` | Wanted cards, quantities, and notes. |
| `inventory` | Physical copies and their current ownership state. |
| `transactions` | Purchases, sales, stores, costs, and financial allocations. |
| `market_data` | External market products, reviewed mappings, and observed prices. |
| `imports` | Acquisition, staging, validation, reconciliation, and import audit. |
| `analytics` | Read models for realized cash results, price history, and later valuation. |

The catalogue supplies the identity used by Wishlist and Inventory. Market Data owns the link between marketplace records and canonical entities. A purchase or sale changes transaction history and the affected copy's ownership state atomically.

## Proposed repository layout

| Path | Purpose |
| --- | --- |
| `apps/api/` | Python API, domain modules, and manual import commands. |
| `apps/web/` | Mobile-first web application. |
| `db/migrations/` | Versioned dbmate migrations. |
| `db/checks/` | Schema and data validation queries. |
| `tests/fixtures/` | Small, approved source samples. |
| `compose.yaml`, `.env.example` | Local service definitions and example settings. |

Add these paths as the corresponding work begins. The local development database and restore environment should use isolated volumes. Bind PostgreSQL to loopback and test phone access through the web application on a trusted network.
