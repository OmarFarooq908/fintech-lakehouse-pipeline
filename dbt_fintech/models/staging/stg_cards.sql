with source_rows as (
    select *
    from {{ source('raw', 'cards_raw') }}
    where coalesce(is_malformed, false) = false
      and upper(coalesce(load_status, 'LOADED')) = 'LOADED'
),

parsed as (
    select
        json_extract_string(raw_payload, '$.card_id') as card_id,
        json_extract_string(raw_payload, '$.account_id') as account_id,
        json_extract_string(raw_payload, '$.card_brand') as card_brand,
        json_extract_string(raw_payload, '$.card_type') as card_type,
        json_extract_string(raw_payload, '$.card_status') as card_status,
        try_cast(json_extract_string(raw_payload, '$.issued_at') as timestamp) as issued_at,
        coalesce(try_cast(json_extract_string(raw_payload, '$.updated_at') as timestamp), event_ts) as updated_at,
        ingestion_batch_id,
        source_endpoint,
        event_ts,
        arrived_at,
        payload_hash,
        file_name,
        loaded_at
    from source_rows
),

deduped as (
    select *
    from parsed
    where card_id is not null
    qualify row_number() over (
        partition by card_id
        order by updated_at desc nulls last, event_ts desc nulls last, arrived_at desc nulls last, loaded_at desc nulls last
    ) = 1
)

select *
from deduped
