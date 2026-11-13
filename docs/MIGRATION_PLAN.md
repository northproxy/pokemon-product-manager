# Migration plan

Status: Revised sequence approved on 2026-11-13. Catalogue restore/schema replay and the scoped Primal Clash history trial were verified on the owner's isolated PostgreSQL 17.10 environment on 2026-11-13/14. See the [trial report](import/primal-clash-history-trial.md). Production migration and complete archive inventory remain pending.

## Integration boundary

Integrate the canonical catalogue with locally archived market data; do not blindly combine all source tables or load the entire price archive. Keep the existing daily acquisition independent and unchanged. Retain original archives outside Git, and initially load only explicitly selected product histories into the application database. A separate full-history analytics database is deferred.

`pokemon-product-catalogue` is the current project name; the source repository below still uses the historical `pokemon-card-wishlist` name. Existing data remains intact, including previously imported expansions.

## Pinned source baselines

| Source | GitHub baseline | Evidence and verification gaps |
| --- | --- | --- |
| Pokémon Card Wishlist | [`3de6388bf2af7862e0a090dad673423e7d49a37e`](https://github.com/northproxy/pokemon-card-wishlist/commit/3de6388bf2af7862e0a090dad673423e7d49a37e) | The 17 migration files define 21 application tables. The checked-in `db/schema.sql` contains only `schema_migrations`. The owner verified 3 expansions: Primal Clash (164 cards), Lost Origin (217), and 30th Celebration: Classic Collection (30). All 17 migration versions matched; a fresh restore matched schema/data and an independent migration replay reproduced the schema. |
| Pokémon Cardmarket BI | [`a86f689aee836078a28912f6190925f79f105f83`](https://github.com/northproxy/pokemon-cardmarket-bi/commit/a86f689aee836078a28912f6190925f79f105f83) | The price and product download workflows are configured for archiving. The restored 2026-08-23 prod dump contains 76,584 products and 2,162,804 price rows across 28 archive dates. Full raw-archive coverage still requires inventory. |

## Code reuse candidates

- Wishlist. Preserve the 17 historical `db/migrations/*.sql` files verbatim once the database baseline is reconciled. Evaluate `scripts/database/validate_schema.sql`, `scripts/database/validate_primal_clash_from_prices.sql`, approved Primal Clash fixtures, and the catalogue and image import scripts with their dependencies. Keep the original Compose, NocoDB setup, and local gallery in the source project.
- BI. Evaluate `src/transform/price_guide.py`, `src/transform/product_catalogs.py`, their tests, and the required download and archive helpers. Keep the existing Actions, loaders, schema, legacy stores, and collection and watchlist data at source during the trial. Adapt the database write path to the Wishlist staging and audit model.
- For each reused asset, record its source path, commit, and applicable attribution. Confirm redistribution rights before copying source data or images.

## Completed scoped rehearsal

- Backup restore and migration replay succeeded; preserve the original 17 migration files.
- The actual trial input was a selected CSV export from the restored BI database, not a replay of original daily JSON files. Do not claim JSON acquisition-to-import validation.
- All rows in this selection have a source timestamp and at least one avg30 metric. Existing columns suffice: avg30/avg30_holo go to price snapshots, all 12 original metrics and both date concepts remain in staging raw_payload.
- Duplicate source observations are consolidated with per-input audit outcomes. Conflicting existing projected prices abort the transaction; there is no overwrite or correction policy.
- The owner confirmed the first import and a one-product SQL export. Replay/conflict behavior was tested locally with PGlite; a second owner-side import was not requested.
- No additional schema migrations were needed. The original catalogue and BI data were not targeted by import writes.
- The next data expansion is Karmesin & Purpur Base Set, after agreeing its sources and coverage. General handling of missing products, missing timestamps, absent avg30 metrics, and corrected files remains open.

## Rehearsal procedure and remaining gates

1. Audit the running Wishlist database with read-only queries. Record the PostgreSQL version, applied migrations, schema, imported expansions, and counts for cards, market products, mappings, snapshots, Wishlist, and audit data. Audit any existing local BI databases separately from the archive. Inventory local price and product archives: paths, file counts, total bytes, date coverage, checksums, source timestamps, invalid files, gaps, and backup availability. Record the transport from GitHub acquisition to the local archive without assuming it is automated.
2. Take a Wishlist backup and restore it to an isolated database. Independently replay the existing migration chain on an empty database and compare its schema with the restored copy. Compare source and restored data, including internal IDs, foreign keys, and user-owned Wishlist records. Run the existing schema and Primal Clash checks.
3. Before writing an importer, agree the metric schema and policies for corrected snapshots, missing source timestamps, and records without either avg30 metric. Preserve the original files and all their metrics. Reconcile selected Primal Clash products from a BI product catalogue and one price archive. Resolve the product using `(source_system, source_product_id)` and retain the internal `market_product_id`. BI upserts by `(snapshot_date, id_product)`; Wishlist records observations by `(market_product_id, source_snapshot_at)` with import provenance. Retain the BI archive date separately from the actual source timestamp.
4. Compare source and imported values, record the file checksum and import run, and report rows that are missing, ambiguous, invalid, or conflicting. Replay the same file and verify stable accepted observations, no duplicate snapshots, and unchanged catalogue and Wishlist data. Exercise a corrected input after the correction policy is agreed.
5. Use the trial results to review and approve any additive SQL migrations before applying them. Extend the trial to several available source dates for explicitly selected products. Verify a CSV export filtered by product IDs, date range, and metrics against the source files. Include source observation timestamps, archive dates, currency, and provenance; report gaps and preserve nulls. Re-import the selection and verify stable counts and values. A successful price-only record is not proof of a canonical mapping.
6. Review and approve the trial report before expanding historical imports. Limit the next import to the agreed selection; full-archive backfill is not required for integration.
7. Exercise the controlled catalogue workflow on Karmesin & Purpur Base Set. Define scope and languages, verify source coverage, stage records, report conflicts, review mappings, and approve the change report before merging. Check expected counts, exclusions, repeat imports, and unchanged existing catalogue and user records. Unknown mappings remain explicitly unresolved.
8. Review real EN/DE packaging and contents evidence for an ETB, tin, and Poké Ball before designing sealed tables. Record mixed-expansion contents without forcing a single-expansion identity. Continue to the mobile purchase-to-sale scenario after the integration and new-expansion workflow are validated.

## Recovery

Retain the source backup and the raw input. On a failed trial, capture the validation report, restore the last verified checkpoint into the isolated environment, and replay the sample after correcting the cause. Reconcile the restored baseline again before retrying.
