with source_rows as (
    select *
    from {{ source('raw', 'accounts_raw') }}
    where coalesce(is_malformed, false) = false
      and upper(coalesce(load_status, 'LOADED')) = 'LOADED'
),

parsed as (
    select
        json_extract_string(raw_payload, '$.account_id') as account_id,
        json_extract_string(raw_payload, '$.customer_id') as customer_id,
        json_extract_string(raw_payload, '$.product_type') as product_type,
        json_extract_string(raw_payload, '$.account_status') as account_status,
        json_extract_string(raw_payload, '$.country_code') as country_code,
        json_extract_string(raw_payload, '$.currency_code') as currency_code,
        try_cast(json_extract_string(raw_payload, '$.opened_at') as timestamp) as opened_at,
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
    where account_id is not null
    qualify row_number() over (
        partition by account_id
        order by updated_at desc nulls last, event_ts desc nulls last, arrived_at desc nulls last, loaded_at desc nulls last
    ) = 1
)

select *
from deduped
