{{ config(materialized='table') }}

select

    l_orderkey        as order_key,
    l_partkey         as part_key,
    l_suppkey         as supplier_key,
    l_linenumber      as line_number,

    l_quantity        as quantity,
    l_extendedprice   as extended_price,
    l_discount        as discount,
    l_tax             as tax,

    cast(l_shipdate as date) as ship_date

from {{ source('tpch', 'lineitem') }}