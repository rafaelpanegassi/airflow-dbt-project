with source as (
    select * from {{ ref('fact_campaign_dispatch') }}
),
renamed as (
    select
        dispatch_id,
        customer_id,
        campaign_id,
        cast(date_id as varchar) as date_id,
        cast(clicked_link as boolean) as has_clicked_link
    from source
)
select * from renamed