create table if not exists observability.ingest_batch_manifest (
  ingestion_batch_id varchar,
  source_endpoint varchar,
  scale_tier varchar,
  requested_rows bigint,
  delivered_rows bigint,
  duplicate_rows bigint,
  late_rows bigint,
  malformed_rows bigint,
  file_name varchar,
  payload_hash varchar,
  batch_started_at timestamp,
  batch_finished_at timestamp,
  status varchar,
  inserted_at timestamp default current_timestamp
);

alter table observability.ingest_batch_manifest add column if not exists storage_path varchar;
alter table observability.ingest_batch_manifest add column if not exists manifest_path varchar;
alter table observability.ingest_batch_manifest add column if not exists file_count bigint;
alter table observability.ingest_batch_manifest add column if not exists chunk_rows bigint;

create table if not exists observability.ingest_run_audit (
  audit_id bigint,
  dag_id varchar,
  task_id varchar,
  run_id varchar,
  ingestion_batch_id varchar,
  source_endpoint varchar,
  started_at timestamp,
  finished_at timestamp,
  status varchar,
  row_count bigint,
  error_message varchar,
  inserted_at timestamp default current_timestamp
);

create table if not exists observability.quarantine_payloads (
  quarantine_id bigint,
  ingestion_batch_id varchar,
  source_endpoint varchar,
  error_code varchar,
  error_message varchar,
  raw_payload json,
  payload_hash varchar,
  quarantined_at timestamp default current_timestamp,
  replay_status varchar default 'PENDING'
);

create table if not exists observability.replay_queue (
  replay_id bigint,
  ingestion_batch_id varchar,
  source_endpoint varchar,
  requested_at timestamp default current_timestamp,
  requested_by varchar default 'airflow',
  replay_reason varchar,
  replay_status varchar default 'QUEUED',
  replay_completed_at timestamp
);
