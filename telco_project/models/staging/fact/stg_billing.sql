with source as (
    select * from {{ ref('fact_billing') }}
),
renamed as (
    select
        invoice_id,
        customer_id,
        cast(due_date_id as varchar) as due_date_id,
        cast(payment_date_id as varchar) as payment_date_id,
        invoice_status,
        cast(total_amount as decimal(10, 2)) as total_amount,
        cast(paid_amount as decimal(10, 2)) as paid_amount
    from source
)
select * from renamed