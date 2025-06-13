with int_billing as (
    select * from {{ ref('int_billing_joined_with_dims') }}
),
dim_date as (
    select * from {{ ref('stg_date') }}
),
final as (
    select
        int_billing.invoice_id,
        int_billing.customer_id,
        int_billing.due_date_id,
        int_billing.payment_date_id,
        int_billing.invoice_status,
        int_billing.total_amount,
        int_billing.paid_amount,
        payment_dates.date_day - due_dates.date_day as days_to_pay
    from int_billing
    left join dim_date as due_dates on int_billing.due_date_id = due_dates.date_day
    left join dim_date as payment_dates on int_billing.payment_date_id = payment_dates.date_day
)
select
    {{ dbt_utils.generate_surrogate_key(['invoice_id']) }} as invoice_sk,
    customer_id,
    due_date_id,
    payment_date_id,
    invoice_status,
    total_amount,
    paid_amount,
    days_to_pay
from final