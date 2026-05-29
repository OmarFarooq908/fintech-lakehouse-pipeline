# Fintech Lakehouse Pipeline

End-to-end synthetic fintech data platform: **Airflow** orchestration, partitioned **Parquet** raw lake, **DuckDB** analytics, and **dbt** dimensional models (payments, settlements, chargebacks, fraud).

Designed as a portfolio case study for scale-minded ingestion, idempotent batches, and warehouse portability (e.g. Snowflake).

## Stack

Airflow · dbt · DuckDB · Parquet · Docker · Python

## What it demonstrates

- Ingestion patterns that scale from millions to billions of records
- Partitioned Parquet raw lake with DuckDB + dbt on top
- Dimensional modeling for payments, settlements, chargebacks, and risk
- Idempotent batch processing with replay and quarantine patterns
- Portable SQL patterns for moving from local DuckDB to a cloud warehouse

## Architecture

```text
Synthetic generator -> Airflow partition orchestration -> Parquet RAW lake
                    -> DuckDB raw views -> dbt STAGE/CURATED -> analytics and risk marts
                    -> audit, replay, and partition manifests
```

## Project layout

| Path | Purpose |
|------|---------|
| `simulator/` | Synthetic fintech API and volume generators |
| `airflow/` | DAGs and orchestration |
| `duckdb/sql/` | DuckDB bootstrap and audit DDL |
| `data_lake/` | Runtime Parquet partitions and manifests (gitignored) |
| `dbt_fintech/` | dbt staging, intermediate, marts, snapshots, tests |
| `docs/` | Case study narrative, optimization notes, benchmarks |

## Domain model

Synthetic events include customers and KYC, accounts and cards, merchants, payment authorization/capture/settlement, refunds and chargebacks, device sessions and risk events, and FX rates.

## Scale tiers

| Tier | Use |
|------|-----|
| `dev` | 1M–10M rows — functional validation |
| `perf` | 100M+ rows — optimization work |
| `stress` | Architecture aimed at 1B+ when budget allows |

## Reliability patterns

- Immutable raw Parquet partitions
- Batch manifests with row counts and latency
- `payload_hash` deduplication
- Malformed payload quarantine
- Replay queue for failed or delayed batches
- dbt freshness checks and business-rule tests
- Snapshots for mutable dimensions

## Quick start

**Prerequisites:** Docker, Docker Compose

1. Copy `.env.example` to `.env` and adjust paths or `PARQUET_CHUNK_ROWS` if needed.
2. Start services:

   ```bash
   docker compose up airflow-init airflow-webserver airflow-scheduler simulator
   ```

3. Open Airflow at [http://localhost:8080](http://localhost:8080).
4. Trigger the `fintech_ingest_and_transform` DAG.
5. Run dbt from `dbt_fintech/` using the DuckDB profile.

### DAG run parameters

From the Airflow UI you can set:

- `scale_tier` — `dev`, `perf`, or `stress`
- `rows_per_endpoint` — optional row override
- `duplicate_pct`, `late_pct`, `malformed_pct`
- `chunk_rows` — Parquet write batch size

Example trigger config:

```json
{
  "scale_tier": "perf"
}
```

## Key outputs

- Curated dimensions: customers, accounts, cards, merchants
- Facts: payment events, settlements, chargebacks
- `mart_daily_portfolio` — executive rollups
- `mart_fraud_features` — risk analytics
- Observability marts for latency, duplicates, and replay volume

## Documentation

See [`docs/case_study.md`](docs/case_study.md) for the full narrative, benchmark tiers, and portfolio framing.

## License

[MIT](LICENSE)
