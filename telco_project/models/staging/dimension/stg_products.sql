with source as (
    select * from {{ ref('dim_product') }}
),
renamed as (
    select
        product_id,
        product_name,
        category as product_category,
        cast(monthly_fee as decimal(10, 2)) as monthly_fee
    from source
)
select * from renamed