with int_movements as (
    select * from {{ ref('int_movements_joined_with_dims') }}
)
select
    {{ dbt_utils.generate_surrogate_key(['movement_id']) }} as movement_sk,
    customer_id,
    previous_product_id,
    new_product_id,
    conversion_campaign_id,
    cast(date_id as date) as date_id,
    movement_type,
    previous_value,
    new_value,
    applied_discount
from int_movements