{{ config(materialized='table') }}

select

    r.region_name,

    count(distinct i.order_key) as total_orders,

    sum(i.quantity) as quantity,

    sum(i.net_sales) as revenue

from {{ ref('int_order_sales') }} i

join {{ ref('stg_customer') }} c
    on i.customer_key = c.customer_key

join {{ ref('stg_nation') }} n
    on c.nation_key = n.nation_key

join {{ ref('stg_region') }} r
    on n.region_key = r.region_key

group by

    r.region_name

order by revenue desc