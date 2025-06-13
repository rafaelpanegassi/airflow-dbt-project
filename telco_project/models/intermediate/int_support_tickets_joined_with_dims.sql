select
    sup.ticket_id,
    sup.customer_id,
    cast(sup.open_date_id as date) as open_date_id,
    sup.support_channel,
    sup.contact_reason,
    sup.ticket_status,
    cust.customer_name
from {{ ref('stg_support_tickets') }} as sup
left join {{ ref('stg_customers') }} as cust on sup.customer_id = cust.customer_id