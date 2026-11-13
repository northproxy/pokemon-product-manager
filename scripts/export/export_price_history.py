#!/usr/bin/env python3
"""
Purpose: Export selected Cardmarket price histories from the catalogue trial.
Lifecycle: DEVELOPMENT
Description: Run manually from the pokemon-product-manager repository with
    Python 3 and Docker Desktop. Lives in scripts/export/. Select one or more
    product IDs, an inclusive UTC date range, and avg30/avg30_holo metrics.
Side Effects: Reads pokemon_wishlist_migration_test in a read-only transaction
    and writes one new UTF-8 CSV at --output. Never overwrites an existing file.
    Does not modify the database, schema, source archives, or Docker settings.
    Verify the printed row count and date bounds; missing days are not invented.
"""

import argparse
import csv
import io
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

CONTAINER = "pokemon-wishlist-postgres"
DATABASE = "pokemon_wishlist_migration_test"
METRICS = ("avg30", "avg30_holo")


def product_id(value):
    try:
        result = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Product IDs must be integers") from exc
    if result < 1 or result > 9223372036854775807:
        raise argparse.ArgumentTypeError("Product ID is outside the positive bigint range")
    return result


def iso_date(value):
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use an ISO date: YYYY-MM-DD") from exc


def build_query(product_ids, start, end, metrics):
    if start > end or end == date.max:
        raise ValueError("Invalid date interval")
    if not metrics or len(set(metrics)) != len(metrics) or any(m not in METRICS for m in metrics):
        raise ValueError("Choose distinct metrics from avg30, avg30_holo")
    # Validate independently of argparse because this function can be imported.
    ids = sorted({product_id(str(x)) for x in product_ids})
    if not ids:
        raise ValueError("Select at least one product")
    upper = end + timedelta(days=1)
    return f"""SELECT mp.source_product_id AS cardmarket_id,
       mp.raw_name AS product_name,
       p.source_snapshot_at AT TIME ZONE 'UTC' AS observed_at_utc,
       p.currency_code AS currency, {', '.join('p.' + m for m in metrics)}
FROM public.market_price_snapshots p
JOIN public.market_products mp ON mp.market_product_id = p.market_product_id
WHERE mp.source_system = 'cardmarket'
  AND mp.source_product_id IN ({', '.join(chr(39) + str(x) + chr(39) for x in ids)})
  AND p.source_snapshot_at >= TIMESTAMPTZ '{start.isoformat()} 00:00:00+00'
  AND p.source_snapshot_at < TIMESTAMPTZ '{upper.isoformat()} 00:00:00+00'
ORDER BY mp.source_product_id, p.source_snapshot_at"""


def write_csv(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create also prevents replacement if a file appears after preflight.
    with path.open("xb") as output:
        try:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        except BaseException:
            output.close()
            path.unlink(missing_ok=True)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--product-id", type=product_id, nargs="+", required=True)
    parser.add_argument("--from-date", type=iso_date, required=True)
    parser.add_argument("--to-date", type=iso_date, required=True)
    parser.add_argument("--metrics", choices=METRICS, nargs="+", default=list(METRICS))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output already exists; choose a new filename")
    query = build_query(args.product_id, args.from_date, args.to_date, args.metrics)
    sql = ("BEGIN READ ONLY; SET LOCAL statement_timeout = '120s';\n"
           f"COPY ({query}) TO STDOUT WITH (FORMAT CSV, HEADER true, ENCODING 'UTF8');\nCOMMIT;")
    result = subprocess.run([
        "docker", "exec", "-i", CONTAINER, "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1",
        "-P", "pager=off", "-U", "pokemon_app", "-d", DATABASE,
    ], input=sql.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        print(result.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
        raise ValueError("Database export failed; no output file written")
    reader = csv.DictReader(io.StringIO(result.stdout.decode("utf-8"), newline=""))
    expected = ["cardmarket_id", "product_name", "observed_at_utc", "currency", *args.metrics]
    if reader.fieldnames != expected:
        raise ValueError("Unexpected CSV response; no output file written")
    rows = list(reader)
    if not rows:
        raise ValueError("No observations in the selected period; no output file written")
    found = {int(row["cardmarket_id"]) for row in rows}
    missing = sorted(set(args.product_id) - found)
    write_csv(args.output, result.stdout)
    print(f"Export saved: {args.output.resolve()}")
    print(f"Rows: {len(rows)}; products with observations: {len(found)}")
    dates = [row["observed_at_utc"] for row in rows]
    print(f"Observed UTC range: {min(dates)} / {max(dates)}")
    print("Metrics: " + ", ".join(args.metrics))
    print("Missing days are not filled; empty price cells remain null.")
    if missing:
        print("Selected IDs without observations in this period: " + ", ".join(map(str, missing)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, argparse.ArgumentTypeError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        raise SystemExit(1)
