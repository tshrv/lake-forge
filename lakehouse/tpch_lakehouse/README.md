Welcome to your new dbt project!

### Using the starter project

Try running the following commands:
- dbt run
- dbt test


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices


### Profile
```
tpch_lakehouse:
  target: dev

  outputs:
    dev:
      type: trino
      method: none
      host: localhost
      port: 8080
      user: admin
      catalog: lakeforge_main
      schema: tpch
      threads: 4
```

### Medallion architecture:

Bronze (Raw): Existing TPCH tables loaded by Spark (lakeforge_main.tpch)
Silver: Cleaned and standardized models built with dbt
Gold: Business-ready analytical models built with dbt


```
models:
  tpch_lakehouse:

    staging:
      +materialized: table

    silver:
      +materialized: table

    gold:
      +materialized: table

# equivalent to

CREATE TABLE lakeforge_main.tpch.stg_orders AS
SELECT *
FROM lakeforge_main.tpch.orders;
```

This follows dbt's conventions while still mapping nicely to a medallion architecture:

Raw/Bronze → Spark + Iceberg (your existing TPCH tables)
Staging/Silver → dbt staging/
Intermediate → reusable joins and business logic
Marts/Gold → analytics-ready fact and dimension tables

It's a structure you'll see in many production dbt projects, and it's a good one to learn.

### Commands
dbt run
dbt test
dbt docs generate
dbt docs serve --port 8081


### Best practices
1. Source models are already present, no need to create them, just know that they are there
2. But we can add tests for source models so that we can ensure the data quality for what spark loaded in the lakehouse
3. We should have tests for the models we are creating like stg_orders to ensure the data quality was maintained with the transformation

Tests running and passing => This is actually a great demonstration
Your project now proves:
- Spark can ingest 150M+ rows.
- Trino can query Iceberg.
- dbt can transform Iceberg.
- dbt can validate data quality at scale.
That combination is exactly what modern analytics engineering is about.


**Important point for production use cases**
Right now, your staging models are materialized as tables because Trino/Nessie doesn't support views.
That means:
```
raw.orders
    │
    ▼
stg_orders
```
duplicates 150 million rows.
That's acceptable for learning, but in production you often have options like `ephemeral models or different storage strategies`. For your project, tables are fine, but we can be selective about which staging models we materialize to avoid unnecessary copies.
The idea of the staging layer is:
- Remove TPCH prefixes (c_, l_, p_, ...)
- Use readable business names
- Perform simple type conversions
- No joins
- No aggregations
- One staging model per raw table

In stg_lineitem.sql, notice we don't use unique here because the primary key is actually:
(order_key, line_number)
We'll learn about composite key testing later.

Models in `models/intermediate/fct_order_items.sql` are fact models
Notice we're creating an intermediate/fact model.
Not a mart.
Not staging.
Its purpose is to join data into a reusable business fact.

naming convention:
Instead of calling the intermediate model fct_order_items, I'd call it int_order_items.
Why?
In dbt conventions:
stg_ = cleaned source table
int_ = reusable intermediate transformation
fct_ = final star-schema fact table
dim_ = final dimension table

Materialization at each layer
| Layer        | Materialization                           |
| ------------ | ----------------------------------------- |
| staging      | view (or table if views aren't supported) |
| intermediate | ephemeral                                 |
| dimensions   | incremental                               |
| facts        | incremental                               |
| marts        | table or incremental                      |

Selective runs
- dbt run --select customer_revenue
  - dbt only runs customer_revenue.
  - It assumes its dependencies (stg_orders, stg_customer, etc.) already exist in the warehouse.
  - It does not automatically rebuild them.
- dbt run --select stg_orders+
  - Rebuild stg_orders model and everything downstream.
- dbt run --select +customer_revenue
  - Include all upstream dependencies.
  - it'll build stg_customer stg_orders stg_lineitem

Staging models remain as tables (because Trino/Nessie doesn't support views).
Intermediate models are kept minimal or made ephemeral where possible.
Business marts become incremental so you don't repeatedly process hundreds of millions of rows.
During development, use model selectors (--select, +) to rebuild only the part of the DAG you're actively changing.

❌ Don't make the staging models incremental (yet).
❌ Don't make the fact model ephemeral (at least not fct_order_items).
✅ Restructure the models to avoid materializing huge intermediate datasets.
✅ Use incremental on models where it provides real value.

> making fct_order_items ephemeral?
dbt will inline the SQL as a CTE instead of creating a physical Iceberg table.
However...
There's a catch in your case
The join between:
150M orders
600M lineitem
is still enormous.
Making it ephemeral doesn't reduce the work. It simply moves the join into the downstream query.
So it won't solve your memory problem.

> Where incremental really shines
Incremental is best for large, persistent business models.
customer_revenue Imagine new orders arrive every day.
Instead of rebuilding all customer revenue, you process only the new day's orders and merge the results.
That's a meaningful use of incremental.

| Layer     | Materialization                            | Why                                       |
| --------- | ------------------------------------------ | ----------------------------------------- |
| `stg_*`   | `table`                                    | Simple, readable, persistent cleaned data |
| `int_*`   | `ephemeral` (or `table` if reused heavily) | Reusable business logic                   |
| `dim_*`   | `table`                                    | Small lookup tables                       |
| `fct_*`   | `incremental`                              | Large business facts                      |
| `marts/*` | `table` or `incremental`                   | BI-ready datasets                         |

That progression—staging → intermediate → fact → mart—is closer to how mature dbt projects are organized, and it will make your project easier to explain in interviews.

```
                 int_order_sales
                /       |        \
               /        |         \
customer_revenue   supplier_sales   daily_sales
```
Every downstream model can reuse:
- net_sales
- gross_sales
- tax_amount
- quantity

Marts to build next:
int_order_sales
       │
       ├── customer_revenue
       ├── monthly_sales
       ├── supplier_revenue
       ├── top_products
       └── sales_by_region