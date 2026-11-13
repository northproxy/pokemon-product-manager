# Architecture

Status: Application stack proposed; archive and selective-import direction approved by the owner on 2026-11-13. See the [decision log](../DECISIONS.md) for acceptance criteria.

A mobile-first web frontend would call one backend API backed by one PostgreSQL 17 database. Manual import commands would use the same Python package as the API. The full locally retained market archive remains independent of the application database. Only selected product histories are imported initially; a separate full-history analytics database is deferred pending volume and performance evidence. The web client would access data through the API.

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

## Archive and catalogue boundaries

The existing BI GitHub Action downloads daily Cardmarket price snapshots. The owner retains the archive locally. The BI restore and catalogue backup have been audited for the scoped trial. Complete local raw-archive coverage and transport still require inventory; scheduled acquisition does not prove database loading or uninterrupted coverage.

- Keep acquisition running independently of catalogue expansion. Do not change source Actions during the integration trial.
- Retain original price and product files outside Git with checksums, source timestamps, and acquisition dates. An archive is replayable input, not a query database.
- Import history for an explicit product selection and date range through staging, validation, reconciliation, and an audit record.
- Preserve internal catalogue IDs and resolve external products by `(source_system, source_product_id)`. Unreviewed market products must not create approved canonical cards or sealed definitions.
- Preserve all source metrics in the archive. Decide the queryable metric schema before implementation; the catalogue's existing `avg30` and `avg30_holo` columns cannot represent all BI metrics.
- Export selected histories with product identity, source observation timestamp, archive date, currency, metric names, and values. Keep gaps and unavailable values visible; do not interpolate missing days.
- Keep catalogue imports separate from Wishlist, inventory, and transaction records.

## Controlled catalogue expansion

Use one expansion as an import batch, initially Karmesin & Purpur Base Set after the Primal Clash integration trial. Distinguish era/series, expansion, canonical card, and sealed product. A sealed contents configuration may reference multiple expansions.

For each batch: define languages and coverage; verify structured card-source coverage against official checklists; retain source URLs, retrieval dates, and files; stage and validate records; review conflicts and Cardmarket mappings; approve the change report; merge transactionally; verify repeatability and user-data preservation. Establish sealed identity and contents from official descriptions and packaging evidence, recording uncertain contents explicitly.

The specific sources and acceptance counts must be checked for each expansion. Do not infer language/finish variants or exact-language prices from aggregate Cardmarket data.

## Current trial implementation

Two manual development utilities live in `scripts/import/` and `scripts/export/`. They use Python's standard library and Docker/psql against the existing isolated catalogue copy. This is an interim trial implementation, not the proposed shared API package.

The verified import projects avg30/avg30_holo into existing price snapshots and retains the full CSV rows, including other metrics and archive dates, in `staging_market_prices.raw_payload`. Keep that staging evidence. The initial export supports only the two projected metrics and source observation time; archive-date/provenance export is still future work. No canonical identities or schema definitions change.

The eventual catalogue database name is `pokemon_product_catalogue`. Existing `pokemon_wishlist*` names and source containers are retained during the rehearsal. See the [trial report](import/primal-clash-history-trial.md).

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
