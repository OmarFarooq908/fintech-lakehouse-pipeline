with source_rows as (
    select *
    from {{ source('raw', 'risk_events_raw') }}
    where coalesce(is_malformed, false) = false
      and upper(coalesce(load_status, 'LOADED')) = 'LOADED'
),

parsed as (
    select
        json_extract_string(raw_payload, '$.risk_event_id') as risk_event_id,
        json_extract_string(raw_payload, '$.payment_id') as payment_id,
        json_extract_string(raw_payload, '$.device_id') as device_id,
        json_extract_string(raw_payload, '$.risk_reason') as risk_reason,
        try_cast(json_extract_string(raw_payload, '$.risk_score') as numeric(10, 4)) as risk_score,
        json_extract_string(raw_payload, '$.decision') as decision,
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
    where risk_event_id is not null
    qualify row_number() over (
        partition by risk_event_id
        order by event_ts desc nulls last, arrived_at desc nulls last, loaded_at desc nulls last
    ) = 1
)

select *
from deduped
