{{ 
    config(
        materialized='table',
        cluster_by = ["year", "make"]
    ) 
}}

with can_data as (
    select *, 
        'CAN' as country_code
    from {{ ref('stg-used_cars_can') }}
), 

us_data as (
    select *, 
        'US' as country_code
    from {{ ref('stg-used_cars_usa') }}
), 

inventory_unioned as (
    select * from can_data
    union all
    select * from us_data
)

select 
    inventory_unioned.id,
    inventory_unioned.VIN,
    inventory_unioned.price,
    inventory_unioned.miles,
    inventory_unioned.year,
    inventory_unioned.make,
    inventory_unioned.model,
    inventory_unioned.trim,
    inventory_unioned.body_type,
    inventory_unioned.vehicle_type,
    inventory_unioned.drivetrain,
    inventory_unioned.transmission,
    inventory_unioned.fuel_type,
    inventory_unioned.engine_size,
    inventory_unioned.engine_block,
    inventory_unioned.seller_name,
    inventory_unioned.street,
    inventory_unioned.city,
    inventory_unioned.state,
    inventory_unioned.zip,
    inventory_unioned.country_code
from inventory_unioned