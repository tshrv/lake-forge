{{ config(materialized='table') }}

select

    date_trunc('month', order_date) as sales_month,

    count(distinct order_key) as total_orders,

    sum(quantity) as total_quantity,

    sum(net_sales) as revenue,

    avg(net_sales) as average_order_line_value

from {{ ref('int_order_sales') }}

group by 1

order by 1