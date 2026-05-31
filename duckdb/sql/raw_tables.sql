create or replace view raw.customers_raw as
select
  cast(null as varchar) as ingestion_batch_id,
  cast(null as varchar) as source_endpoint,
  cast(null as timestamp) as event_ts,
  cast(null as timestamp) as arrived_at,
  cast(null as varchar) as payload_hash,
  cast(null as varchar) as load_status,
  cast(null as boolean) as is_malformed,
  cast(null as json) as raw_payload,
  cast(null as varchar) as file_name,
  cast(null as timestamp) as loaded_at
where false;

create or replace view raw.accounts_raw as
select
  cast(null as varchar) as ingestion_batch_id,
  cast(null as varchar) as source_endpoint,
  cast(null as timestamp) as event_ts,
  cast(null as timestamp) as arrived_at,
  cast(null as varchar) as payload_hash,
  cast(null as varchar) as load_status,
  cast(null as boolean) as is_malformed,
  cast(null as json) as raw_payload,
  cast(null as varchar) as file_name,
  cast(null as timestamp) as loaded_at
where false;

create or replace view raw.cards_raw as
select
  cast(null as varchar) as ingestion_batch_id,
  cast(null as varchar) as source_endpoint,
  cast(null as timestamp) as event_ts,
  cast(null as timestamp) as arrived_at,
  cast(null as varchar) as payload_hash,
  cast(null as varchar) as load_status,
  cast(null as boolean) as is_malformed,
  cast(null as json) as raw_payload,
  cast(null as varchar) as file_name,
  cast(null as timestamp) as loaded_at
where false;

create or replace view raw.merchants_raw as
select
  cast(null as varchar) as ingestion_batch_id,
  cast(null as varchar) as source_endpoint,
  cast(null as timestamp) as event_ts,
  cast(null as timestamp) as arrived_at,
  cast(null as varchar) as payload_hash,
  cast(null as varchar) as load_status,
  cast(null as boolean) as is_malformed,
  cast(null as json) as raw_payload,
  cast(null as varchar) as file_name,
  cast(null as timestamp) as loaded_at
where false;

create or replace view raw.payment_events_raw as
select
  cast(null as varchar) as ingestion_batch_id,
  cast(null as varchar) as source_endpoint,
  cast(null as timestamp) as event_ts,
  cast(null as timestamp) as arrived_at,
  cast(null as varchar) as payload_hash,
  cast(null as varchar) as load_status,
  cast(null as boolean) as is_malformed,
  cast(null as json) as raw_payload,
  cast(null as varchar) as file_name,
  cast(null as timestamp) as loaded_at
where false;

create or replace view raw.chargebacks_raw as
select
  cast(null as varchar) as ingestion_batch_id,
  cast(null as varchar) as source_endpoint,
  cast(null as timestamp) as event_ts,
  cast(null as timestamp) as arrived_at,
  cast(null as varchar) as payload_hash,
  cast(null as varchar) as load_status,
  cast(null as boolean) as is_malformed,
  cast(null as json) as raw_payload,
  cast(null as varchar) as file_name,
  cast(null as timestamp) as loaded_at
where false;

create or replace view raw.risk_events_raw as
select
  cast(null as varchar) as ingestion_batch_id,
  cast(null as varchar) as source_endpoint,
  cast(null as timestamp) as event_ts,
  cast(null as timestamp) as arrived_at,
  cast(null as varchar) as payload_hash,
  cast(null as varchar) as load_status,
  cast(null as boolean) as is_malformed,
  cast(null as json) as raw_payload,
  cast(null as varchar) as file_name,
  cast(null as timestamp) as loaded_at
where false;

create or replace view raw.fx_rates_raw as
select
  cast(null as varchar) as ingestion_batch_id,
  cast(null as varchar) as source_endpoint,
  cast(null as timestamp) as event_ts,
  cast(null as timestamp) as arrived_at,
  cast(null as varchar) as payload_hash,
  cast(null as varchar) as load_status,
  cast(null as boolean) as is_malformed,
  cast(null as json) as raw_payload,
  cast(null as varchar) as file_name,
  cast(null as timestamp) as loaded_at
where false;
