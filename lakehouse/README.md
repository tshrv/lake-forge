# Spark
```py
spark.sql("""
SELECT COUNT(*)
FROM nessie.tpch.lineitem
""").show()


spark.sql("""
SELECT *
FROM nessie.tpch.trino_test
""").show()


spark.sql("""
DELETE FROM nessie.tpch.customer
WHERE c_custkey <= 100
""")

# time travel query
SELECT *
FROM nessie.tpch.customer VERSION AS OF <snapshot_id>;

# schema evolution
ALTER TABLE nessie.tpch.customer
ADD COLUMN source_system STRING;
# verify
DESCRIBE TABLE nessie.tpch.customer;

# Partition Evolution
ALTER TABLE orders ADD PARTITION FIELD bucket(64, customer_id);
# Old files stay valid, new files use new partition scheme and when query runs, It transparently combines the results.
# This is something traditional Hive-style tables struggle with.

# If you want old data reorganized, you explicitly rewrite it.
# In Spark:
CALL catalog.system.rewrite_data_files(table => 'db.events');
# This separation is one of Iceberg's biggest advantages over older Hive-style lake layouts.

# deletion
DELETE FROM nessie.tpch.customer
WHERE c_custkey < 1000;

# update
UPDATE nessie.tpch.customer
SET c_name = 'TEST'
WHERE c_custkey = 1001;

# inspect
SELECT *
FROM nessie.tpch.customer.snapshots;
# Understand copy-on-write behavior
```

# Nessie
```sql
CREATE BRANCH experiment IN nessie;
USE REFERENCE experiment IN nessie;

CREATE TABLE nessie.tpch.branch_test (
    id INT
)
USING iceberg;
```


# Trino
```sh
docker exec -it trino trino
```

```ini
# iceberg.properties
iceberg.nessie-catalog.ref=experiment
```

```sql
SHOW CATALOGS;
SHOW SCHEMAS FROM iceberg;
SHOW TABLES FROM iceberg.tpch;

SELECT COUNT(*)
FROM iceberg.tpch.lineitem;


CREATE TABLE iceberg.tpch.trino_test (
    id BIGINT,
    name VARCHAR
);

INSERT INTO iceberg.tpch.trino_test
VALUES
(1, 'alice'),
(2, 'bob');

SELECT * FROM iceberg.tpch."customer$snapshots";

select * from iceberg_main.tpch.customer for version as of <snapshot_id> limit 5;
```

# Iceberg
When creating the table, or afterwards, based on the access patterns, set partition spec for tables which are large.
- maybe upto 10G tables no partitioning is needed
- try hashing+bucketing on id
- day/month/nation etc
- modify partition spec (does not reorganize old data, does for new)
- reorganize table data based on new partition spec 


## Queries

Query 1
```sql
select
	l_returnflag,
	l_linestatus,
	sum(l_quantity) as sum_qty,
	sum(l_extendedprice) as sum_base_price,
	sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
	sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
	avg(l_quantity) as avg_qty,
	avg(l_extendedprice) as avg_price,
	avg(l_discount) as avg_disc,
	count(*) as count_order
from
	iceberg_main.tpch.lineitem
where
    l_shipdate <= date_add(
    'day',
    -90,
    DATE '1998-12-01'
)
group by
	l_returnflag,
	l_linestatus
order by
	l_returnflag,
	l_linestatus;
```

Query 2 - shipping priority
```sql
SELECT
    l_orderkey,
    sum(l_extendedprice * (1 - l_discount)) AS revenue,
    o_orderdate,
    o_shippriority
FROM
    iceberg_main.tpch.customer,
    iceberg_main.tpch.orders,
    iceberg_main.tpch.lineitem
WHERE
    c_mktsegment = 'BUILDING'
    AND c_custkey = o_custkey
    AND l_orderkey = o_orderkey
    AND o_orderdate < DATE '1995-03-15'
    AND l_shipdate > DATE '1995-03-15'
GROUP BY
    l_orderkey,
    o_orderdate,
    o_shippriority
ORDER BY
    revenue DESC,
    o_orderdate
LIMIT 10;
```

## Repartitioning
Check the file sizes, should be aroun 128-150 MB
If smaller, we have small file problem, file read overhead
```sql
-- check a table's file sizes
SELECT
    count(*) AS files,
    sum(record_count) AS rows,
    avg(file_size_in_bytes)/1024/1024 AS avg_mb
FROM iceberg_main.tpch."lineitem$files";

-- run repartitioning
CALL iceberg_main.system.rewrite_data_files(
    'tpch',
    'lineitem'
);
```
Also see, `compaction`

```sql
-- spark- set partition spec
ALTER TABLE nessie.tpch.lineitem
ADD PARTITION FIELD months(l_shipdate)

-- run repartitioning
CALL nessie.system.rewrite_data_files(
    table => 'tpch.lineitem'
)

```


## Partition Pruning
Partition pruning means:
Trino asks Iceberg for data, Iceberg checks table metadata and says: "Only these partitions/files can contain matching rows; ignore the rest."


# DBT

Iceberg already provides
- ACID
- snapshots
- partitions
- compaction
- schema evolution
- branching

dbt provides
- SQL transformations
- testing
- documentation
- lineage
- incremental pipelines
- dependency graph

They solve different problems.


```
dbt Models
        │
        ├── Silver
        ├── Gold
        ├── Tests
        ├── Docs
        ├── Lineage
        └── Incremental Models
```


> A compelling extension for your resume

To make the project stand out as a modern lakehouse implementation, aim for this workflow:

Spark ingests TPCH SF100 into Iceberg (raw layer).
Nessie manages catalog versioning, allowing branches for development and experimentation.
Iceberg handles storage features such as partitioning, compaction, schema evolution, and time travel.
dbt (via Trino) builds Silver and Gold models, enforces data quality tests, and generates lineage/documentation.
Trino serves fast analytical queries over both raw and transformed Iceberg tables.
A BI tool (e.g., Apache Superset, Power BI, or Tableau) connects to Trino to visualize business metrics.

That progression demonstrates an understanding of ingestion, storage, governance, transformation, serving, and analytics—the complete lifecycle expected in a modern data engineering project.