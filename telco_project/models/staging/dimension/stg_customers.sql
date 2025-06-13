with source as (
    select * from {{ ref('dim_customer') }}
),
renamed as (
    select
        customer_id,
        ssn as customer_ssn,
        name as customer_name,
        marital_status,
        income_bracket,
        payment_method,
        acquisition_channel,
        credit_score,
        city,
        state,
        cast(birth_date as date) as birth_date,
        cast(signup_date as date) as signup_date,
        cast(cancellation_date as date) as cancellation_date

    from source
)
select * from renamed