with source_rows as (
    select *
    from {{ source('raw', 'chargebacks_raw') }}
    where coalesce(is_malformed, false) = false
      and upper(coalesce(load_status, 'LOADED')) = 'LOADED'
),

parsed as (
    select
        json_extract_string(raw_payload, '$.chargeback_id') as chargeback_id,
        json_extract_string(raw_payload, '$.payment_id') as payment_id,
        json_extract_string(raw_payload, '$.merchant_id') as merchant_id,
        json_extract_string(raw_payload, '$.chargeback_reason') as chargeback_reason,
        json_extract_string(raw_payload, '$.chargeback_status') as chargeback_status,
        try_cast(json_extract_string(raw_payload, '$.amount_minor') as bigint) as amount_minor,
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
    where chargeback_id is not null
    qualify row_number() over (
        partition by chargeback_id
        order by event_ts desc nulls last, arrived_at desc nulls last, loaded_at desc nulls last
    ) = 1
)

select *
from deduped
