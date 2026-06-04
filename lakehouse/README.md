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
PARTITIONED BY (days(order_date))
ALTER TABLE ...
# Old files stay valid
# New files use new partition scheme
# This is something traditional Hive-style tables struggle with.

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
```