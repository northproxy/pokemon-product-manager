# Project scope

Pokémon Product Manager brings catalogue, Wishlist, inventory, transactions, and market data into one application. An owned item represents a single physical copy. Several copies can reference the same catalogue version while retaining independent purchase and sale histories.

## MVP acceptance criteria

| Capability | Acceptance criterion |
| --- | --- |
| Sealed catalogue | Browse sealed products on a phone and distinguish English and German versions. |
| Contents | Show the number and set of each known booster. Display evidence-backed configurations and make uncertain or unknown contents visible. |
| Purchases | Record the date, store, amount and currency, and notes for a purchase. Track each physical copy separately. |
| Sales | Record the sale date, gross proceeds, fees, and seller-paid shipping or other sale costs for a specific copy. Keep its purchase and sale in history. |
| Cash result | For a simple single-currency sale, show gross proceeds minus selling costs and acquisition cost. |
| Wishlist | Add and remove a wanted card, save its quantity and notes, and verify persistence after refresh. The full release criteria for Wishlist, including CSV export, are tracked in the [decision log](DECISIONS.md). |
| Cardmarket reference prices | Show the source, observation date, and metric when a reviewed mapping supports the price. Show an unavailable state when a mapping or observation is missing. |

## First end-to-end scenario

From a phone, find a German Elite Trainer Box, inspect its contents, and record two copies acquired separately. Sell the copy purchased for €44.99 for €60.00 and record a €3.00 marketplace fee and €5.00 in seller-paid shipping. Verify a realized cash gain of €7.01, retained history for the sold copy, and an owned state for the second copy.

## Later scope

Release calendars, Vienna shop and supply intelligence, openings and pull rates, an opening-value index, gifts, trades, and expanded valuation and analytics are future work. Cloud hosting is deferred.
