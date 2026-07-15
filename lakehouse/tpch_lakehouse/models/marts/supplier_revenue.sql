-- {{ config(materialized='table') }}

-- select

--     s.supplier_key,

--     s.supplier_name,

--     count(distinct i.order_key) as total_orders,

--     sum(i.quantity) as items_supplied,

--     sum(i.net_sales) as revenue

-- from {{ ref('int_order_sales') }} i

-- join {{ ref('stg_supplier') }} s
--     on i.supplier_key = s.supplier_key

-- group by

--     s.supplier_key,
--     s.supplier_name



-- {{ config(materialized='table') }}

-- with supplier_agg as (

--     select
--         supplier_key,
--         count(distinct order_key) as total_orders,
--         sum(quantity) as items_supplied,
--         sum(net_sales) as revenue
--     from {{ ref('int_order_sales') }}
--     group by supplier_key

-- )

-- select
--     s.supplier_key,
--     s.supplier_name,
--     a.total_orders,
--     a.items_supplied,
--     a.revenue
-- from supplier_agg a
-- join {{ ref('stg_supplier') }} s
--     on a.supplier_key = s.supplier_key

{{ config(materialized='table') }}

with dedup as (

    select
        supplier_key,
        order_key,
        sum(quantity) as quantity,
        sum(net_sales) as net_sales
    from {{ ref('int_order_sales') }}
    group by supplier_key, order_key

),

supplier_agg as (

    select
        supplier_key,
        count(*) as total_orders,
        sum(quantity) as items_supplied,
        sum(net_sales) as revenue
    from dedup
    group by supplier_key

)

select
    s.supplier_key,
    s.supplier_name,
    a.total_orders,
    a.items_supplied,
    a.revenue
from supplier_agg a
join {{ ref('stg_supplier') }} s
    on a.supplier_key = s.supplier_key