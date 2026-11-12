# Migration plan

Status: Proposed. Execute the first rehearsal against isolated local copies.

## Pinned source baselines

| Source | GitHub baseline | Evidence and verification gaps |
| --- | --- | --- |
| Pokémon Card Wishlist | [`3de6388bf2af7862e0a090dad673423e7d49a37e`](https://github.com/northproxy/pokemon-card-wishlist/commit/3de6388bf2af7862e0a090dad673423e7d49a37e) | The 17 migration files define 21 application tables. The checked-in `db/schema.sql` contains only `schema_migrations`. The roadmap documents a complete Primal Clash slice and 30 canonical `me55c` cards. Verify the owner-reported third expansion in the running database. |
| Pokémon Cardmarket BI | [`a86f689aee836078a28912f6190925f79f105f83`](https://github.com/northproxy/pokemon-cardmarket-bi/commit/a86f689aee836078a28912f6190925f79f105f83) | The price and product download workflows are configured for archiving. Determine actual archive coverage and the contents of any legacy databases during the audit. |

## Code reuse candidates

- Wishlist. Preserve the 17 historical `db/migrations/*.sql` files verbatim once the database baseline is reconciled. Evaluate `scripts/database/validate_schema.sql`, `scripts/database/validate_primal_clash_from_prices.sql`, approved Primal Clash fixtures, and the catalogue and image import scripts with their dependencies. Keep the original Compose, NocoDB setup, and local gallery in the source project.
- BI. Evaluate `src/transform/price_guide.py`, `src/transform/product_catalogs.py`, their tests, and the required download and archive helpers. Keep the existing Actions, loaders, schema, legacy stores, and collection and watchlist data at source during the trial. Adapt the database write path to the Wishlist staging and audit model.
- For each reused asset, record its source path, commit, and applicable attribution. Confirm redistribution rights before copying source data or images.

## Local rehearsal

1. Audit the running Wishlist database with read-only queries. Record the PostgreSQL version, applied migrations, schema, imported expansions, and counts for cards, market products, mappings, snapshots, Wishlist, and audit data. List relevant BI archives with file checksums, source timestamps, and coverage gaps.
2. Take a Wishlist backup and restore it to an isolated database. Independently replay the existing migration chain on an empty database and compare its schema with the restored copy. Compare source and restored data, including internal IDs, foreign keys, and user-owned Wishlist records. Run the existing schema and Primal Clash checks.
3. Reconcile one BI product and one price archive. Resolve the product using `(source_system, source_product_id)` and retain the internal `market_product_id`. BI upserts by `(snapshot_date, id_product)`; Wishlist records observations by `(market_product_id, source_snapshot_at)` with import provenance. Retain the BI archive date separately from the actual source timestamp.
4. Compare source and imported values, record the file checksum and import run, and report rows that are missing, ambiguous, invalid, or conflicting. Replay the same file and verify stable accepted observations, no duplicate snapshots, and unchanged catalogue and Wishlist data. Exercise a corrected input after the correction policy is agreed.
5. Use the trial results to review the schema and approve any additive SQL migrations. Review real EN/DE packaging and contents evidence for an ETB, tin, and Poké Ball before designing sealed tables. Review and approve the import results before any historical backfill.

## Recovery

Retain the source backup and the raw input. On a failed trial, capture the validation report, restore the last verified checkpoint into the isolated environment, and replay the sample after correcting the cause. Reconcile the restored baseline again before retrying.
