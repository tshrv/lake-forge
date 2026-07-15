{{ config(materialized='table') }}

select

    p.part_key,

    p.part_name,

    p.brand,

    sum(i.quantity) as quantity_sold,

    sum(i.net_sales) as revenue

from {{ ref('int_order_sales') }} i

join {{ ref('stg_part') }} p
    on i.part_key = p.part_key

group by

    p.part_key,
    p.part_name,
    p.brand

order by revenue desc