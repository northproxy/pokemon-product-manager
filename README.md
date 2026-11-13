# Pokémon Product Manager

A local-first, mobile-first application for managing a Pokémon TCG collection, tracking purchases and sales, and viewing reference prices.

The first release focuses on browsing sealed products and their contents, tracking individual copies, and recording the cash result of a sale. It also includes a card Wishlist and shows Cardmarket reference prices where a verified match exists.

## Project status

The repository contains the design documents and isolated migration-trial utilities. The owner validated catalogue backup/restore, replay of 17 source migrations, a Primal Clash history import on PostgreSQL 17.10, and a selected CSV export on 2026-11-13/14. See the [trial report](docs/import/primal-clash-history-trial.md), [roadmap](ROADMAP.md), and [migration plan](docs/MIGRATION_PLAN.md).

The application, general importer, and final database deployment are not implemented here. The trial utilities use the existing source-project Docker environment; this repository does not yet bootstrap that environment. The [MVP scope](PROJECT.md), [architecture](docs/ARCHITECTURE.md), and [decision log](DECISIONS.md) retain the agreed scope and open decisions.

## Source projects

- [Pokémon Product Catalogue (formerly Card Wishlist)](https://github.com/northproxy/pokemon-card-wishlist) provides the canonical card catalogue, image pipeline, and PostgreSQL import and mapping model.
- [Pokémon Cardmarket BI](https://github.com/northproxy/pokemon-cardmarket-bi) provides Cardmarket acquisition, raw archives, parsers, and reference material for market analytics.

## Trial commands

Requires Python 3, Docker Desktop, the running `pokemon-wishlist-postgres` container, and the prepared `pokemon_wishlist_migration_test` database. No Python packages or credentials are needed by these commands. Run from this repository's root.

Import the already reviewed CSV (omit `--apply` for file-only validation):

```powershell
py .\scripts\import\import_bi_history_trial.py --csv "R:\_dev\Cardmarket Product Catalogue\migration-work\primal_clash_price_history_20261113_204934.csv" --apply
```

The importer is unchanged from the successful trial. Repeating this exact file reconciles the existing import without adding rows. Do not re-import solely to install these files.

Export one or more selected Cardmarket product IDs and an inclusive UTC date range:

```powershell
py .\scripts\export\export_price_history.py --product-id 273532 --from-date 2026-06-29 --to-date 2026-08-22 --metrics avg30 avg30_holo --output "R:\_dev\Cardmarket Product Catalogue\migration-work\weedle_history.csv"
```

The exporter queries the test catalogue in a read-only transaction and creates a new UTF-8 CSV. It refuses an existing output path. Supply additional IDs after `--product-id`, or select just one of the two supported metrics. All-null cells remain empty; missing days are not filled. Other BI metrics remain in import staging JSON and are not exported by this utility.

The equivalent single-product SQL export was verified on the owner's database. The packaged Python export wrapper has local validation; its first owner-side run remains pending.

Keep raw CSVs, database dumps, and generated exports outside Git. The eventual database name is `pokemon_product_catalogue`; these commands do not rename or target it.

See [Contributing](CONTRIBUTING.md) for the local workflow.
