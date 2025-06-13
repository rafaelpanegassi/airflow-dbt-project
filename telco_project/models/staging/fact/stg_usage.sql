with source as (
    select * from {{ ref('fact_usage') }}
),
renamed as (
    select
        usage_id,
        customer_id,
        product_id,
        cast(date_ref_id as varchar) as date_ref_id,
        cast(data_usage_gb as decimal(10, 2)) as data_usage_gb,
        cast(voice_minutes as int) as voice_minutes,
        cast(sms_count as int) as sms_count
    from source
)
select * from renamed