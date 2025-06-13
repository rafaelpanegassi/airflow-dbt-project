-- This model joins the movements table with all its relevant dimensions 
-- to create a complete view of each event.

select 
    mov.movement_id,
    mov.customer_id,
    cast(mov.date_id as date) as date_id,
    mov.previous_product_id,
    mov.new_product_id,
    mov.conversion_campaign_id,
    mov.movement_type,
    mov.previous_value,
    mov.new_value,
    mov.applied_discount,
    cust.acquisition_channel,
    cust.city,
    cust.state,
    prev_prod.product_name as previous_product_name,
    prev_prod.product_category as previous_product_category,
    new_prod.product_name as new_product_name,
    new_prod.product_category as new_product_category,
    camp.campaign_name
from {{ ref('stg_movements') }} as mov
left join {{ ref('stg_customers') }} as cust on mov.customer_id = cust.customer_id
left join {{ ref('stg_products') }} as prev_prod on mov.previous_product_id = prev_prod.product_id
left join {{ ref('stg_products') }} as new_prod on mov.new_product_id = new_prod.product_id
left join {{ ref('stg_campaigns') }} as camp on mov.conversion_campaign_id = camp.campaign_id