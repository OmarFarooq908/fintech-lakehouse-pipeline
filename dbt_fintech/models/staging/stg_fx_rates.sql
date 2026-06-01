with source_rows as (
    select *
    from {{ source('raw', 'fx_rates_raw') }}
    where coalesce(is_malformed, false) = false
      and upper(coalesce(load_status, 'LOADED')) = 'LOADED'
),

parsed as (
    select
        json_extract_string(raw_payload, '$.fx_rate_id') as fx_rate_id,
        json_extract_string(raw_payload, '$.base_currency') as base_currency,
        json_extract_string(raw_payload, '$.quote_currency') as quote_currency,
        try_cast(json_extract_string(raw_payload, '$.rate_date') as date) as rate_date,
        try_cast(json_extract_string(raw_payload, '$.conversion_rate') as numeric(18, 6)) as conversion_rate,
        coalesce(try_cast(json_extract_string(raw_payload, '$.event_ts') as timestamp), event_ts) as event_ts,
        ingestion_batch_id,
        source_endpoint,
        arrived_at,
        payload_hash,
        file_name,
        loaded_at
    from source_rows
),

deduped as (
    select *
    from parsed
    where fx_rate_id is not null
    qualify row_number() over (
        partition by fx_rate_id
        order by event_ts desc nulls last, arrived_at desc nulls last, loaded_at desc nulls last
    ) = 1
)

select *
from deduped
