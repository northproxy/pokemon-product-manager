# Decision log

## Confirmed project direction

| ID | Decision |
| --- | --- |
| PPM-001 | Use `northproxy/pokemon-product-manager` for the integrated product. The existing repositories are preserved as source projects. |
| PPM-002 | Develop locally. Changes to either source repository or database require separate authorization. Rehearse migrations on isolated copies. |
| PPM-003 | Include Wishlist as a module of the integrated product. Show Cardmarket reference prices where a verified match exists. |
| PPM-004 | Track one record per owned physical copy. Use the sealed purchase-to-sale workflow and mobile access as MVP acceptance criteria. |

Approved by the owner on 2026-11-13:

| ID | Decision |
| --- | --- |
| PPM-005 | Keep daily BI acquisition independent of catalogue imports. Retain the full available archive locally outside Git; audit actual coverage and backups. |
| PPM-006 | Initially import only selected product histories into the application database. Defer a separate full-history analytics database until volume and performance evidence justify it. |
| PPM-007 | Populate the catalogue through reviewed expansion batches. Market acquisition must not automatically create approved canonical records. Preserve existing catalogue and user-owned data. |
| PPM-008 | Validate Primal Clash integration, then selected history and CSV export, then the Karmesin & Purpur Base Set workflow before continuing the mobile collection scenario. |

Approved naming clarification on 2026-11-13:

| ID | Decision |
| --- | --- |
| PPM-009 | Use `pokemon-product-catalogue` for the catalogue project and planned source-repository name, and `pokemon_product_catalogue` for the eventual PostgreSQL database. Existing source URLs and runtime names remain until explicitly renamed. |

## Trial evidence, 2026-11-13/14

The owner verified catalogue backup/restore, 17-migration schema replay, the selected BI history import, and the Weedle CSV export. The trial used existing snapshot columns and retained all source metrics in staging JSON. This is evidence for ADR-001/003, not automatic acceptance of the complete proposed architecture. See the [trial report](docs/import/primal-clash-history-trial.md).

## Proposed architecture decisions

| ID | Proposal | Evidence needed for acceptance |
| --- | --- | --- |
| ADR-001 | Use a modular monolith with one application PostgreSQL 17 database containing selected market histories, Docker Compose for local development, and dbmate for migrations. | Reproduce the historical schema and restore a Wishlist backup with verified key and data parity. |
| ADR-002 | Use Python and FastAPI for the backend, and React, TypeScript, and Vite for a mobile-first web app with a path to PWA installation. | Validate a small API contract and a representative flow on a physical phone. |
| ADR-003 | Use the Wishlist canonical catalogue as the identity foundation. Treat Cardmarket IDs as external identifiers and replay BI archives through an audited importer. | Demonstrate timestamp and metric parity and repeatable behavior on a representative archive file. |

## Open decisions

- Determine the Wishlist release gate, including CSV export and delivery order relative to the sealed workflow.
- Establish what identifies a sealed version and when a packaging variation requires a separate contents configuration.
- Compare a shared physical-item identity with separate card and sealed inventory tables.
- Before generalizing the trial importer, decide how to store queryable additional BI metrics and how to handle corrected snapshots, missing source timestamps, missing market products, and observations without `avg30` or `avg30_holo`. The scoped trial retains extra metrics in staging JSON and rejects conflicts.
- Define how to allocate cost and proceeds for multi-item transactions and how to handle multiple currencies.
- Decide local phone access and PWA installation requirements after the prototype.

Historical decisions remain documented in the [Wishlist decision log](https://github.com/northproxy/pokemon-card-wishlist/blob/3de6388bf2af7862e0a090dad673423e7d49a37e/DECISIONS.md). This project tracks its own decisions.
