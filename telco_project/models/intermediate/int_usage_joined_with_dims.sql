select
    usg.usage_id,
    usg.customer_id,
    usg.product_id,
    cast(usg.date_ref_id as date) as date_ref_id,
    cast(usg.data_usage_gb as int) as data_usage_gb,
    cast(usg.voice_minutes as int) as voice_minutes,
    cast(usg.sms_count as int) as sms_count,
    prod.product_name,
    prod.product_category
from {{ ref('stg_usage') }} as usg
left join {{ ref('stg_products') }} as prod on usg.product_id = prod.product_id