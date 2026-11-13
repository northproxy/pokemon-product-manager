# Primal Clash history trial — 2026-11-13/14

Status: scoped owner-side trial succeeded on PostgreSQL 17.10. No production
cutover, database rename, or full-archive migration was performed.

## Catalogue baseline and recovery

| Baseline | Owner-confirmed value |
| --- | --- |
| Source database | `pokemon_wishlist` |
| Isolated restore / import target | `pokemon_wishlist_migration_test` |
| Independent schema replay | `pokemon_wishlist_schema_replay` |
| Container | `pokemon-wishlist-postgres` |
| Expansions / cards | 3 / 411: Primal Clash 164, Lost Origin 217, 30th Celebration: Classic Collection 30 |
| Market products / mappings / snapshots | 173 / 165 / 173 |
| Wishlist records / migrations | 1 / 17 |

The owner restored the fresh custom-format dump, confirmed the baseline counts,
and compared schema-only and data-only SQL dumps. Schema/data comparisons matched
after excluding generated pg_dump restrict keys. An independent replay of the
17 source migrations produced a matching schema. This is logical SQL comparison,
not a byte-level comparison of database storage.

Backup: `pokemon_wishlist_before_integration_20261113_200844.dump`, 558,970 bytes,
stored outside Git in the owner's local backups folder. SHA256:

```text
521F81BFCAB6D172DD88C9B86C1A325378FF60B752CA7A083A8093015A27C932
```

## BI findings

The restored `cardmarket_restore_test` database has 76,584 products and 2,162,804
price rows on 28 archive dates between 2026-06-29 and 2026-08-22. This is not
continuous daily coverage and does not establish the complete raw-archive inventory.

| Finding | Count |
| --- | --- |
| Priced product IDs / IDs absent from products | 78,218 / 1,634 |
| Price rows for absent products | 21,661 |
| Missing source timestamps | 0 |
| Rows without either avg30 metric, but with another metric | 240,042 |
| Rows with all 12 metrics null | 140,205 |
| Repeated product/source-time groups | 77,802; each has two identical rows |
| Conflicting values within those repeated groups | 0 |

The source permits prices without a product foreign key. Preserve this source
evidence; do not infer zero prices from nulls or automatically manufacture approved
catalogue entries for missing products.

## Selected import

Input: `primal_clash_price_history_20261113_204934.csv`, exported from BI for the
catalogue's 173 Primal Clash market products. SHA256:

```text
1b0c56a000372e95f69fe093152eed65062c4a62e6579c76eff90d05292fd8c6
```

The owner ran [import_bi_history_trial.py](../../scripts/import/import_bi_history_trial.py).
Run ID 18 ended with `succeeded` and `COMMIT`:

| Outcome | Count |
| --- | --- |
| Retained original rows / archive dates | 4,844 / 28 |
| Products / distinct product-source-time observations | 173 / 4,671 |
| Newly inserted snapshots | 4,671 |
| Identical repeated input rows recorded as unchanged | 173 |

No incoming snapshot key overlapped an existing key in this owner's trial. The
previous 173 snapshots remained, giving an expected target total of 4,844 price
rows; this total is derived from the baseline and committed insert count.

All selected rows have source timestamps and at least one avg30 metric. The
importer uses existing schema: avg30/avg30_holo go to `market_price_snapshots`;
all CSV fields remain in `staging_market_prices.raw_payload`, with a per-source-row
audit outcome. Source values in raw JSON remain strings. Repeated observations
retain both archive-date references. Currency EUR follows the existing Cardmarket
contract. A BI CSV export checksum is not an original daily JSON checksum.

The importer refuses an unreviewed file checksum, a different target database,
missing/inactive selected products, invalid values, or conflicting target prices.
Writes are transactional; sequence numbers can advance after rollback. Matching
existing prices are not overwritten. Identical replay/conflict behavior was tested
locally with PGlite 0.5.16 (PostgreSQL 18.6 engine), including preservation of
pre-existing snapshots. The owner-side PostgreSQL 17 run confirmed the first import;
a second owner-side run was not requested. Keep staging evidence after the trial.

## Selected export

Owner-generated file: `price_history_273532_20261114_004646.csv`. SHA256:

```text
f107585b070423c78012d3b2aced28823bfa1f455dfee83eec7b3c53741ca674
```

Weedle [Multiply], Cardmarket ID 273532, 2026-06-29 through 2026-08-22:
28 distinct source-time observations. All 27 unique BI observations are present
with matching avg30/avg30_holo; the additional 2026-07-26 observation is outside
the BI input and is consistent with retained pre-existing catalogue history.
The export has six columns: identity, name, UTC source time, currency, and two
metrics. Archive-date/provenance columns and other metrics are not exported yet.

[export_price_history.py](../../scripts/export/export_price_history.py) packages
this query with validated product/date/metric options and an exclusive output
file create. It uses a read-only database transaction, keeps nulls empty, and does
not fill missing dates. Its query and wrapper were checked locally; the owner's
successful export used the equivalent PowerShell/psql command, not this new wrapper.
Usage for both utilities is in the [README](../../README.md).

## Remaining work and provenance

Next: define the sources and scope for the Karmesin & Purpur Base Set import.
General importer policies, all-metric query/export support, full raw-file inventory,
original daily-file replay, and deployment of `pokemon_product_catalogue` remain open.
The historical migration chain has not yet been copied into this repository.

Contracts inspected in `northproxy/pokemon-card-wishlist` at
`3de6388bf2af7862e0a090dad673423e7d49a37e`: the six migrations for catalogue
foundation, market products, import runs, price staging, record outcomes and
price snapshots; `scripts/import/import_primal_clash_market_prices.py` and
`scripts/import/merge_primal_clash_market_prices.py`. The trial script is a separately
written CSV adapter; no source database files or card images are redistributed.
BI baseline: `northproxy/pokemon-cardmarket-bi` at
`a86f689aee836078a28912f6190925f79f105f83`. Raw input and output CSVs remain outside Git.
