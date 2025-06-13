select
    bil.invoice_id,
    bil.customer_id,
    cast(bil.due_date_id as date) as due_date_id,
    cast(bil.payment_date_id as date) as payment_date_id,
    bil.invoice_status,
    bil.total_amount,
    bil.paid_amount,
    cust.payment_method,
    cust.credit_score
from {{ ref('stg_billing') }} as bil
left join {{ ref('stg_customers') }} as cust on bil.customer_id = cust.customer_id