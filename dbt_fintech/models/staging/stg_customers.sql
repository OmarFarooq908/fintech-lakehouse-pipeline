with source_rows as (
    select *
    from {{ source('raw', 'customers_raw') }}
    where coalesce(is_malformed, false) = false
      and upper(coalesce(load_status, 'LOADED')) = 'LOADED'
),

parsed as (
    select
        json_extract_string(raw_payload, '$.customer_id') as customer_id,
        json_extract_string(raw_payload, '$.customer_segment') as customer_segment,
        json_extract_string(raw_payload, '$.country_code') as country_code,
        json_extract_string(raw_payload, '$.preferred_currency') as preferred_currency,
        json_extract_string(raw_payload, '$.kyc_status') as kyc_status,
        json_extract_string(raw_payload, '$.risk_band') as risk_band,
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
    where customer_id is not null
    qualify row_number() over (
        partition by customer_id
        order by updated_at desc nulls last, event_ts desc nulls last, arrived_at desc nulls last, loaded_at desc nulls last
    ) = 1
)

select *
from deduped
