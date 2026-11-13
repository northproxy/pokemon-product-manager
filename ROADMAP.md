# Roadmap

Updated 2026-11-14. Existing BI acquisition continues independently and the full available archive remains local. The isolated history trial is complete within its stated scope; this is not a production migration.

| Stage | Status | Checkpoint / remaining work |
| --- | --- | --- |
| 0. Repository foundation | In place | Design documents and trial import/export utilities. Full application/bootstrap tooling remains planned. |
| 1. Source audit | Database audit complete; archive inventory partial | Catalogue: 3 sets, 411 cards, 17 migrations. BI restore: 76,584 products and 2,162,804 price rows. Full raw-archive coverage and transport inventory remain open. |
| 2. Local database baseline | Verified by owner | Fresh catalogue backup restored with matching schema/data; 17 migrations independently reproduced the restored schema. |
| 3. Price integration trial | Scoped trial verified | 173 Primal Clash products; 4,844 source rows retained and 4,671 observations inserted. No schema changes. Wider metric/correction policies remain open. |
| 4. Selected history and export | Single-product scenario verified | Weedle export contains all 27 BI observations plus one pre-existing catalogue observation. Python export wrapper packaged; first owner-side wrapper run pending. No history UI or all-metric export yet. |
| 5. Controlled expansion workflow | Next | Define source coverage and batch scope for Karmesin & Purpur Base Set, then stage, review, and import without changing existing catalogue/user records. |
| 6. Mobile vertical slice | Planned | Validate sealed identity/contents and exercise purchases, a sale, Wishlist, and eligible reference prices on a phone. |
| 7. Expand coverage | Planned | Add reviewed expansions and selected histories. Revisit separate analytics storage only when volume or performance justifies it. |

See the [trial report](docs/import/primal-clash-history-trial.md) for evidence and limits, and the [migration plan](docs/MIGRATION_PLAN.md) for the remaining integration steps. No full-archive backfill or production cutover has been authorized by completion of this trial.
