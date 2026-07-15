{{ config(materialized='table') }}

select

    c.customer_key,
    c.customer_name,
    c.market_segment,

    count(distinct s.order_key)      as total_orders,
    sum(s.quantity)                  as items_sold,
    count(*)                         as order_lines,
    sum(s.net_sales)                 as revenue,
    avg(s.net_sales)                 as average_order_line_value


from {{ ref('int_order_sales') }} s

join {{ ref('stg_customer') }} c
    on s.customer_key = c.customer_key

group by

    c.customer_key,
    c.customer_name,
    c.market_segment