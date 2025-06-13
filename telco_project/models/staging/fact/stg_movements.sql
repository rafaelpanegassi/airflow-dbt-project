with source as (
    select * from {{ ref('fact_movement') }}
),
renamed as (
    select
        movement_id,
        customer_id,
        previous_product_id,
        new_product_id,
        conversion_campaign_id,
        cast(date_id as varchar) as date_id,
        movement_type,
        cast(previous_value as decimal(10, 2)) as previous_value,
        cast(new_value as decimal(10, 2)) as new_value,
        cast(applied_discount as decimal(10, 2)) as applied_discount
    from source
)
select * from renamed