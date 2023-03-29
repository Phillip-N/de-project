{{ config(materialized="view") }}

select
    id,
    vin as VIN,
    cast(price as numeric) as price,
    cast(miles as numeric) as miles,
    year,
    make,
    model,
    trim,
    body_type,
    vehicle_type,
    drivetrain,
    transmission,
    fuel_type,
    cast(engine_size as numeric) as engine_size,
    engine_block,
    seller_name,
    street,
    city,
    state,
    zip

from {{ source("staging", "usa_used_cars") }}
where
    id is not null
    and VIN is not null
    and price is not null
    and miles is not null
    and year is not null
    and model is not null
    and trim is not null
    and body_type is not null
    and vehicle_type is not null
    and drivetrain is not null
    and transmission is not null
    and fuel_type is not null
    and engine_size is not null
    and engine_block is not null
    and seller_name is not null
    and street is not null
    and city is not null
    and state is not null
    and zip is not null

{% if var("is_test_run", default=false) %} limit 100 {% endif %}
