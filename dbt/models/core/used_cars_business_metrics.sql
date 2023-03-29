{{ 
    config(
        materialized='table',
        cluster_by = ["year", "make"]
    ) 
}}

select 
    year,
    make,
    cast(sum(price)/count(*) as numeric) as price_retention,
    cast(sum(miles)/count(*) as numeric) as mileage_utilization
from {{ ref('used_cars_inventory') }}
group by year, make