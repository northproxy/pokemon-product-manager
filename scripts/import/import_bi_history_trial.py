#!/usr/bin/env python3
"""
Purpose: Import the reviewed Primal Clash BI CSV into the isolated catalogue copy.
Lifecycle: DEVELOPMENT
Description: Run manually from PowerShell with Python 3 and Docker Desktop. Keep
    under scripts/import/ in pokemon-product-manager if adopted; until then keep
    beside the CSV in the external migration-work folder. This trial accepts only
    the reviewed file checksum and targets pokemon_wishlist_migration_test.
Side Effects: With --apply, writes import_runs, staging_market_prices,
    import_record_outcomes and market_price_snapshots in one transaction. Does not
    change schema, catalogue identities, Wishlist, source BI, or source files.
    Retains every CSV field in staging raw_payload; only avg30/avg30_holo are
    projected to the existing price table. Failed transactions may consume sequence
    numbers. Verify success using the built-in reconciliation and committed report.
"""

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

CONTAINER = "pokemon-wishlist-postgres"
DATABASE = "pokemon_wishlist_migration_test"
SHA256 = "1b0c56a000372e95f69fe093152eed65062c4a62e6579c76eff90d05292fd8c6"
RUN_REFERENCE = "bi-history-trial-v1:" + SHA256
METRICS = ["avg", "low", "trend", "avg1", "avg7", "avg30",
           "avg_holo", "low_holo", "trend_holo", "avg1_holo", "avg7_holo", "avg30_holo"]
FIELDS = ["snapshot_date", "source_created_at", "id_product", "id_category", *METRICS, "created_at"]
PRODUCTS = set(range(273532, 273696)) | {295269, 295286, 295292, 312211, 312239, 312267, 363664, 363665, 886899}


def timestamp(value):
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("Timezone missing from source timestamp")
    return parsed.astimezone(timezone.utc)


def validate_rows(rows):
    daily_keys, observations, products, days = set(), {}, set(), set()
    for number, row in enumerate(rows, 2):
        if set(row) != set(FIELDS) or any(v is None for v in row.values()):
            raise ValueError(f"Malformed CSV row {number}")
        product = int(row["id_product"])
        if product not in PRODUCTS:
            raise ValueError(f"Out-of-scope product at CSV row {number}")
        archive_day = date.fromisoformat(row["snapshot_date"])
        observed = timestamp(row["source_created_at"])
        timestamp(row["created_at"])
        category = int(row["id_category"]) if row["id_category"] else None
        prices = []
        for field in METRICS:
            value = Decimal(row[field]) if row[field] else None
            if value is not None and (not value.is_finite() or value < 0):
                raise ValueError(f"Invalid {field} at CSV row {number}")
            if field in ("avg30", "avg30_holo") and value is not None:
                if value >= Decimal("100000000") or value != value.quantize(Decimal("0.0001")):
                    raise ValueError(f"{field} does not fit target numeric(12,4)")
            prices.append(value)
        if not row["avg30"] and not row["avg30_holo"]:
            raise ValueError("This trial requires at least one avg30 metric per row")
        daily = (product, archive_day)
        if daily in daily_keys:
            raise ValueError(f"Repeated archive-day identity at row {number}")
        daily_keys.add(daily)
        key, values = (product, observed), (category, *prices)
        if key in observations and observations[key] != values:
            raise ValueError(f"Conflicting source observation at row {number}")
        observations[key] = values
        products.add(product)
        days.add(archive_day)
    if products != PRODUCTS or len(rows) != 4844 or len(observations) != 4671 or len(days) != 28:
        raise ValueError("CSV coverage differs from the reviewed trial")
    return {"source_rows": len(rows), "products": len(products), "archive_days": len(days),
            "unique_observations": len(observations), "identical_repeats": len(rows) - len(observations),
            "first_archive_date": str(min(days)), "last_archive_date": str(max(days))}


def load_csv(path):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("File SHA256 differs from the reviewed CSV; no import attempted")
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    if reader.fieldnames != FIELDS:
        raise ValueError("Unexpected CSV header")
    rows = list(reader)
    return rows, validate_rows(rows)


def sql_literal(value):
    return "'" + value.replace("'", "''") + "'"


def copy_escape(value):
    return value.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def build_sql(rows, filename):
    copy_rows = []
    for ordinal, row in enumerate(rows, 1):
        payload = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        checksum = hashlib.sha256(payload.encode()).hexdigest()
        copy_rows.append(f"{ordinal}\t{copy_escape(payload)}\t{checksum}")
    return r"""
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL search_path = public, pg_catalog;
SET LOCAL timezone = 'UTC';
SET LOCAL standard_conforming_strings = on;
SET LOCAL lock_timeout = '15s';
SET LOCAL statement_timeout = '120s';
DO $$ BEGIN
  IF current_database() <> 'pokemon_wishlist_migration_test' THEN
    RAISE EXCEPTION 'Refusing non-trial database';
  END IF;
END $$;
SELECT pg_advisory_xact_lock(2026111301);
LOCK TABLE public.market_products, public.expansions IN SHARE MODE;
LOCK TABLE public.import_runs, public.staging_market_prices,
  public.import_record_outcomes, public.market_price_snapshots IN SHARE ROW EXCLUSIVE MODE;
CREATE TEMP TABLE trial_source (ordinal integer PRIMARY KEY, payload jsonb NOT NULL, checksum text NOT NULL) ON COMMIT DROP;
COPY trial_source FROM STDIN;
""" + "\n".join(copy_rows) + r"""
\.
CREATE TEMP TABLE trial_rows ON COMMIT DROP AS
SELECT s.*, m.market_product_id,
  payload->>'id_product' AS source_product_id,
  (payload->>'snapshot_date')::date AS archive_day,
  (payload->>'source_created_at')::timestamptz AS observed_at,
  NULLIF(payload->>'avg30','')::numeric AS avg30,
  NULLIF(payload->>'avg30_holo','')::numeric AS avg30_holo,
  'bi:' || (payload->>'snapshot_date') || ':' || (payload->>'id_product') AS source_reference,
  row_number() OVER (PARTITION BY m.market_product_id, (payload->>'source_created_at')::timestamptz
    ORDER BY (payload->>'snapshot_date')::date, ordinal) AS observation_rank
FROM trial_source s
JOIN public.market_products m ON m.source_system = 'cardmarket'
  AND m.source_product_id = payload->>'id_product' AND m.is_active
JOIN public.expansions e ON e.expansion_id = m.expansion_id
  AND e.expansion_key = 'primal_clash' AND e.is_active;
DO $$ BEGIN
  IF (SELECT count(*) FROM trial_rows) <> 4844 OR
     (SELECT count(DISTINCT market_product_id) FROM trial_rows) <> 173 OR
     (SELECT count(*) FROM trial_rows WHERE observation_rank = 1) <> 4671 THEN
    RAISE EXCEPTION 'Target catalogue does not contain the reviewed active product selection';
  END IF;
  IF EXISTS (
    SELECT 1 FROM trial_rows r JOIN public.market_price_snapshots p
      ON p.market_product_id = r.market_product_id AND p.source_snapshot_at = r.observed_at
    WHERE p.currency_code IS DISTINCT FROM 'EUR'
      OR p.avg30 IS DISTINCT FROM r.avg30 OR p.avg30_holo IS DISTINCT FROM r.avg30_holo
  ) THEN RAISE EXCEPTION 'Existing price conflicts with CSV: entire import rolled back; no overwrite'; END IF;
END $$;
""" + fr"""
SELECT EXISTS (SELECT 1 FROM public.import_runs WHERE run_reference = {sql_literal(RUN_REFERENCE)}) AS already_imported \gset
\if :already_imported
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM public.import_runs
    WHERE run_reference = {sql_literal(RUN_REFERENCE)} AND status = 'succeeded'
      AND source_artifact_checksum = '{SHA256}' AND total_source_records = 4844)
  THEN RAISE EXCEPTION 'Existing run is incomplete or inconsistent'; END IF;
END $$;
\else
INSERT INTO public.import_runs (
  run_reference, run_kind, source_system, source_entity_type,
  source_artifact_reference, source_artifact_checksum, scope_type, scope_reference,
  is_authoritative, importer_version, status
) VALUES ({sql_literal(RUN_REFERENCE)}, 'market_prices', 'cardmarket', 'market_price',
  {sql_literal(filename)}, '{SHA256}', 'selected_records',
  'primal_clash:173-products:2026-06-29/2026-08-22', false, 'bi-history-trial/1', 'created');
\endif
SELECT import_run_id AS trial_run_id FROM public.import_runs
  WHERE run_reference = {sql_literal(RUN_REFERENCE)} \gset
""" + r"""
\if :already_imported
\echo This exact CSV was already imported; verifying retained data without new writes.
\else
INSERT INTO public.staging_market_prices (
  import_run_id, source_record_reference, source_system, source_product_id,
  source_snapshot_at, currency_code, avg30_raw, avg30, avg30_holo_raw, avg30_holo,
  raw_payload, record_checksum, normalization_status, validation_status, validation_completed_at
)
SELECT :trial_run_id, source_reference, 'cardmarket', source_product_id,
  observed_at, 'EUR', NULLIF(payload->>'avg30',''), avg30,
  NULLIF(payload->>'avg30_holo',''), avg30_holo,
  payload, checksum, 'normalized', 'valid', CURRENT_TIMESTAMP
FROM trial_rows ORDER BY ordinal;
UPDATE public.import_runs SET status = 'validated',
  staging_loaded_at = CURRENT_TIMESTAMP, validated_at = CURRENT_TIMESTAMP,
  total_source_records = 4844, valid_source_records = 4844, rejected_records = 0
WHERE import_run_id = :trial_run_id;
UPDATE public.import_runs SET status = 'merge_started', merge_started_at = CURRENT_TIMESTAMP
WHERE import_run_id = :trial_run_id;
CREATE TEMP TABLE trial_inserted ON COMMIT DROP AS
WITH inserted AS (
  INSERT INTO public.market_price_snapshots (
    market_product_id, import_run_id, source_snapshot_at, currency_code,
    avg30, avg30_holo, source_record_reference, record_checksum
  )
  SELECT r.market_product_id, :trial_run_id, r.observed_at, 'EUR',
    r.avg30, r.avg30_holo, r.source_reference, r.checksum
  FROM trial_rows r WHERE observation_rank = 1 AND NOT EXISTS (
    SELECT 1 FROM public.market_price_snapshots p
    WHERE p.market_product_id = r.market_product_id AND p.source_snapshot_at = r.observed_at
  ) ORDER BY r.market_product_id, r.observed_at
  RETURNING market_price_snapshot_id
) SELECT * FROM inserted;
INSERT INTO public.import_record_outcomes (
  import_run_id, entity_type, source_system, source_entity_id, source_record_reference,
  production_entity_id, outcome_type, reason_code, change_summary
)
SELECT :trial_run_id, 'market_price_snapshot', 'cardmarket', r.source_product_id,
  r.source_reference, p.market_price_snapshot_id,
  CASE WHEN i.market_price_snapshot_id IS NOT NULL AND observation_rank = 1 THEN 'inserted' ELSE 'unchanged' END,
  CASE WHEN observation_rank > 1 THEN 'identical_source_observation'
       WHEN i.market_price_snapshot_id IS NULL THEN 'existing_matching_observation' ELSE NULL END,
  jsonb_build_object('staging_market_price_id', s.staging_market_price_id,
    'archive_date', r.archive_day, 'source_database', 'cardmarket_restore_test',
    'source_created_at', r.observed_at, 'source_database_created_at', r.payload->>'created_at',
    'metric_projection', 'avg30,avg30_holo; all CSV fields retained in staging raw_payload')
FROM trial_rows r
JOIN public.market_price_snapshots p ON p.market_product_id = r.market_product_id AND p.source_snapshot_at = r.observed_at
JOIN public.staging_market_prices s ON s.import_run_id = :trial_run_id AND s.source_record_reference = r.source_reference
LEFT JOIN trial_inserted i USING (market_price_snapshot_id);
UPDATE public.import_runs SET status = 'succeeded', completed_at = CURRENT_TIMESTAMP,
  inserted_records = (SELECT count(*) FROM trial_inserted), updated_records = 0,
  unchanged_records = 4844 - (SELECT count(*) FROM trial_inserted),
  missing_records = 0, retired_records = 0
WHERE import_run_id = :trial_run_id;
\endif
""" + fr"""
DO $$ DECLARE run_id bigint; BEGIN
  SELECT import_run_id INTO STRICT run_id FROM public.import_runs WHERE run_reference = {sql_literal(RUN_REFERENCE)};
  IF (SELECT count(*) FROM public.staging_market_prices WHERE import_run_id = run_id) <> 4844
     OR (SELECT count(*) FROM public.import_record_outcomes WHERE import_run_id = run_id) <> 4844
  THEN RAISE EXCEPTION 'Staging/outcome reconciliation failed'; END IF;
  IF EXISTS (
    SELECT 1 FROM trial_rows r LEFT JOIN public.staging_market_prices s
      ON s.import_run_id = run_id AND s.source_record_reference = r.source_reference
    WHERE s.staging_market_price_id IS NULL OR s.raw_payload IS DISTINCT FROM r.payload
      OR s.record_checksum IS DISTINCT FROM r.checksum OR s.validation_status <> 'valid'
      OR s.source_product_id IS DISTINCT FROM r.source_product_id
      OR s.source_snapshot_at IS DISTINCT FROM r.observed_at
      OR s.avg30 IS DISTINCT FROM r.avg30 OR s.avg30_holo IS DISTINCT FROM r.avg30_holo
  ) THEN RAISE EXCEPTION 'Raw or normalized source data was not retained exactly'; END IF;
  IF EXISTS (
    SELECT 1 FROM trial_rows r LEFT JOIN public.market_price_snapshots p
      ON p.market_product_id = r.market_product_id AND p.source_snapshot_at = r.observed_at
    WHERE p.market_price_snapshot_id IS NULL OR p.currency_code IS DISTINCT FROM 'EUR'
      OR p.avg30 IS DISTINCT FROM r.avg30 OR p.avg30_holo IS DISTINCT FROM r.avg30_holo
  ) THEN RAISE EXCEPTION 'Price reconciliation failed'; END IF;
END $$;
SELECT import_run_id, status, total_source_records AS retained_source_rows,
  inserted_records AS inserted_on_first_import, unchanged_records AS unchanged_source_rows
FROM public.import_runs WHERE import_run_id = :trial_run_id;
SELECT count(*) AS unique_observations, count(DISTINCT market_product_id) AS products
FROM trial_rows WHERE observation_rank = 1;
COMMIT;
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Import into the fixed isolated database; otherwise validate CSV only")
    args = parser.parse_args()
    rows, summary = load_csv(args.csv)
    print(json.dumps(summary, indent=2), flush=True)
    print("SHA256: " + SHA256, flush=True)
    if not args.apply:
        print("CSV validation passed. No database connection or changes. Use --apply for the isolated trial.")
        return 0
    sql = build_sql(rows, args.csv.name)
    print("Target: " + DATABASE + "; all changes are transactional.", flush=True)
    result = subprocess.run([
        "docker", "exec", "-i", CONTAINER, "psql", "-X", "-v", "ON_ERROR_STOP=1",
        "-P", "pager=off", "-U", "pokemon_app", "-d", DATABASE,
    ], input=sql.encode("utf-8"))
    if result.returncode != 0:
        print("Import did not report success. SQL errors roll back the transaction. If the connection was lost, rerun this same command to reconcile safely.", file=sys.stderr)
        return 1
    print("Trial import committed and reconciled. Repeating this exact file adds no rows.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, InvalidOperation) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        raise SystemExit(1)
