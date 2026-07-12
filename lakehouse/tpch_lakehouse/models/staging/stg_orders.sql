{{ config(materialized='table') }}

select
    o_orderkey      as order_key,
    o_custkey       as customer_key,
    o_orderstatus   as order_status,
    cast(o_orderdate as date) as order_date,
    o_totalprice    as total_price,
    o_orderpriority as order_priority,
    o_clerk         as clerk,
    o_shippriority  as ship_priority

from {{ source('tpch','orders') }}