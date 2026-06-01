with source_rows as (
    select *
    from {{ source('raw', 'payment_events_raw') }}
    where coalesce(is_malformed, false) = false
      and upper(coalesce(load_status, 'LOADED')) = 'LOADED'
),

parsed as (
    select
        json_extract_string(raw_payload, '$.payment_event_id') as payment_event_id,
        json_extract_string(raw_payload, '$.payment_id') as payment_id,
        json_extract_string(raw_payload, '$.customer_id') as customer_id,
        json_extract_string(raw_payload, '$.account_id') as account_id,
        json_extract_string(raw_payload, '$.card_id') as card_id,
        json_extract_string(raw_payload, '$.merchant_id') as merchant_id,
        json_extract_string(raw_payload, '$.payment_status') as payment_status,
        json_extract_string(raw_payload, '$.country_code') as country_code,
        json_extract_string(raw_payload, '$.currency_code') as currency_code,
        try_cast(json_extract_string(raw_payload, '$.amount_minor') as bigint) as amount_minor,
        try_cast(json_extract_string(raw_payload, '$.fee_minor') as bigint) as fee_minor,
        coalesce(try_cast(json_extract_string(raw_payload, '$.event_ts') as timestamp), event_ts) as event_ts,
        try_cast(json_extract_string(raw_payload, '$.ingested_at') as timestamp) as ingested_at,
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
    where payment_event_id is not null
    qualify row_number() over (
        partition by payment_event_id
        order by event_ts desc nulls last, arrived_at desc nulls last, loaded_at desc nulls last
    ) = 1
)

select *
from deduped
