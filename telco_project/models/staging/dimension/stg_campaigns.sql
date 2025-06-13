with source as (
    select * from {{ ref('dim_campaign') }}
),
renamed as (
    select
        campaign_id,
        campaign_name,
        dispatch_channel,
        cast(start_date as date) as start_date,
        cast(end_date as date) as end_date
    from source
)
select * from renamed