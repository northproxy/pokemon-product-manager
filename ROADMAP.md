# Roadmap

| Stage | Checkpoint |
| --- | --- |
| 0. Repository foundation | English project documents are committed. The source commits, requirements, and open decisions are recorded. |
| 1. Source audit | Record the actual Wishlist schema, migration status, imported sets, and baseline counts. Inventory the BI archives and identify representative input files. |
| 2. Local database baseline | Start isolated PostgreSQL and dbmate using Docker Compose. Apply the source migrations to an empty database and independently restore a verified Wishlist backup into a test database. Compare schemas, keys, and data. |
| 3. Price integration trial | Replay one archived BI file against the isolated database. Verify identities, source timestamps, metrics, rejected records, and the outcome of a repeat run. |
| 4. Mobile vertical slice | Validate sealed identity and contents on real examples. Exercise sealed browsing, two individual purchases, a sale, and the realized result on a phone. Verify Wishlist persistence and eligible reference prices for the MVP. |
| 5. Expand coverage | Extend import coverage and add later capabilities in separately reviewed increments. |

See the [migration plan](docs/MIGRATION_PLAN.md) for the evidence required before moving from a trial to a historical backfill.
