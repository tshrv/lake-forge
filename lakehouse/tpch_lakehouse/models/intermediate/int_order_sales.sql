{{ config(materialized='table') }}

select

    -- Order information
    o.order_key,
    o.customer_key,
    o.order_date,
    o.order_status,

    -- Order line
    l.line_number,
    l.part_key,
    l.supplier_key,

    -- Measures
    l.quantity,
    l.extended_price,
    l.discount,
    l.tax,

    -- Derived measures
    l.extended_price                           as gross_sales,

    l.extended_price * (1 - l.discount)        as net_sales,

    l.extended_price * l.tax                  as tax_amount,

    l.extended_price * (1 - l.discount)
        + (l.extended_price * l.tax)          as total_sales

from {{ ref('stg_orders') }} o

join {{ ref('stg_lineitem') }} l
    on o.order_key = l.order_key