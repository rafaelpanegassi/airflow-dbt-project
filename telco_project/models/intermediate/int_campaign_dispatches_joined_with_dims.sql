select
    disp.dispatch_id,
    disp.customer_id,
    disp.campaign_id,
    cast(disp.date_id as date) as date_id,
    disp.has_clicked_link,
    camp.campaign_name,
    camp.dispatch_channel,
    cust.customer_name
from {{ ref('stg_campaign_dispatches') }} as disp
left join {{ ref('stg_campaigns') }} as camp on disp.campaign_id = camp.campaign_id
left join {{ ref('stg_customers') }} as cust on disp.customer_id = cust.customer_id