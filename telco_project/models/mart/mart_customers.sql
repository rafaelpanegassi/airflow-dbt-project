select
    customer_id,
    customer_name,
    customer_ssn,
    birth_date,
    extract(year from age(current_date, birth_date)) as age,
    marital_status,
    income_bracket,
    payment_method,
    acquisition_channel,
    credit_score,
    city,
    state,
    signup_date,
    cancellation_date,
    case 
        when cancellation_date is null then 'Active'
        else 'Cancelled'
    end as customer_status
from {{ ref('stg_customers') }}