# Pokémon Product Manager

A local-first, mobile-first application for managing a Pokémon TCG collection, tracking purchases and sales, and viewing reference prices.

The first release focuses on browsing sealed products and their contents, tracking individual copies, and recording the cash result of a sale. It also includes a card Wishlist and shows Cardmarket reference prices where a verified match exists.

## Project status

The repository is at the documentation stage. Start with the [MVP scope](PROJECT.md) and the [roadmap](ROADMAP.md). The [architecture](docs/ARCHITECTURE.md) and [decision log](DECISIONS.md) describe the design under review. The [migration plan](docs/MIGRATION_PLAN.md) records the source baselines and checks required before integration.

## Source projects

- [Pokémon Card Wishlist](https://github.com/northproxy/pokemon-card-wishlist) provides the canonical card catalogue, image pipeline, and PostgreSQL import and mapping model.
- [Pokémon Cardmarket BI](https://github.com/northproxy/pokemon-cardmarket-bi) provides Cardmarket acquisition, raw archives, parsers, and reference material for market analytics.

See [Contributing](CONTRIBUTING.md) for the local workflow.
