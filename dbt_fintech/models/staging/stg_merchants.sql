with source_rows as (
    select *
    from {{ source('raw', 'merchants_raw') }}
    where coalesce(is_malformed, false) = false
      and upper(coalesce(load_status, 'LOADED')) = 'LOADED'
),

parsed as (
    select
        json_extract_string(raw_payload, '$.merchant_id') as merchant_id,
        json_extract_string(raw_payload, '$.merchant_name') as merchant_name,
        json_extract_string(raw_payload, '$.merchant_country') as merchant_country,
        json_extract_string(raw_payload, '$.merchant_category_code') as merchant_category_code,
        json_extract_string(raw_payload, '$.pricing_tier') as pricing_tier,
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
    where merchant_id is not null
    qualify row_number() over (
        partition by merchant_id
        order by updated_at desc nulls last, event_ts desc nulls last, arrived_at desc nulls last, loaded_at desc nulls last
    ) = 1
)

select *
from deduped
