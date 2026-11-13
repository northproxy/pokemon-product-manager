# Roadmap

The owner approved the revised sequence on 2026-11-13. Integration and local data checks remain pending. Existing BI acquisition continues independently; the complete local archive is retained outside Git.

| Stage | Checkpoint |
| --- | --- |
| 0. Repository foundation | Maintain English documentation, pinned source baselines, confirmed scope, and open technical decisions. |
| 1. Source audit | Record actual catalogue schema, migrations, imported sets, and counts. Audit any BI databases separately. Inventory local archives, bytes, dates, gaps, checksums, and backups. |
| 2. Local database baseline | Restore a verified catalogue backup into an isolated database. Independently replay historical migrations into an empty database. Compare schemas, keys, and data. |
| 3. Price integration trial | Agree metric, timestamp, and correction policies. Import selected Primal Clash products from representative BI archives. Verify provenance, rejected records, mapping boundaries, and repeatability. |
| 4. Selected history and export | Import several dates for selected products. Verify CSV filtering by product, period, and metrics against the source files. Preserve nulls and report gaps; approve results before expanding history coverage. |
| 5. Controlled expansion workflow | Process Karmesin & Purpur Base Set through scoped source collection, staging, validation, reviewed mappings, owner approval, and repeatable merge. Preserve existing catalogue and user data. |
| 6. Mobile vertical slice | Validate sealed identity and contents on real examples. Exercise sealed browsing, two individual purchases, a sale, and the realized result on a phone. Verify Wishlist persistence and eligible reference prices for the MVP. |
| 7. Expand coverage | Add expansions and selected histories in reviewed increments. Reconsider a separate full-history analytics database only after archive volume and query performance justify it. |

See the [migration plan](docs/MIGRATION_PLAN.md) for the rehearsal, export checks, and recovery requirements. Stages 4 and 5 validate the data workflow; they do not require a price-history UI or change the agreed collection MVP.
