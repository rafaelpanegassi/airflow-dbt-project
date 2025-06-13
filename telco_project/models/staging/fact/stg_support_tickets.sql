with source as (
    select * from {{ ref('fact_support_tickets') }}
),
renamed as (
    select
        ticket_id,
        customer_id,
        cast(open_date_id as varchar) as open_date_id,
        support_channel,
        contact_reason,
        ticket_status
    from source
)
select * from renamed