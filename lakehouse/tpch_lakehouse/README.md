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
