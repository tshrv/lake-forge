# LakeForge
An end-to-end open data platform supporting batch ETL, streaming CDC, Iceberg lakehouse storage, and analytics engineering workflows.

> Iceberg + Nessie + MinIO + Spark + Trino Lab

## Architecture

```
Spark/Trino
     ↓
  Iceberg
   ↙   ↘
Nessie MinIO
```

- Nessie stores:
```
Namespaces
Tables
Branches
Tags
Snapshot references
```
- MinIO stores:
```
Parquet data files
metadata.json
manifest files
manifest lists
Iceberg
```
- Iceberg knows:
```
Which metadata file is current
Which snapshots exist
Which parquet files belong to a snapshot
```

### Components

| Component | Purpose                             |
| --------- | ----------------------------------- |
| MinIO     | S3-compatible object storage        |
| Nessie    | Catalog + Git-like branching        |
| Iceberg   | Table format and metadata layer     |
| Spark     | Data ingestion and table management |
| Trino     | Interactive SQL query engine        |


### Important point to note
#### Architecture

```text
          Spark                    Trino
            │                        │
            ▼                        ▼
      Iceberg Library        Iceberg Connector
            │                        │
            └────────┬───────────────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
          Nessie         MinIO
         (Catalog)     (Storage)
```

##### Key Concept

Iceberg is **not a server**. Spark and Trino each contain their own Iceberg implementation.

When querying a table:

1. The engine (Spark/Trino) asks Nessie for table metadata and the current snapshot.
2. The engine reads Iceberg metadata files from MinIO.
3. The engine reads the underlying Parquet data files from MinIO.

Nessie stores catalog metadata (namespaces, tables, branches, snapshots), while MinIO stores the actual Iceberg metadata files and Parquet data files.

---

## Versions

| Component | Version |
| --------- | ------- |
| PySpark   | 3.5.6   |
| Iceberg   | 1.11.0  |
| Nessie    | 0.107.6 |
| Trino     | 477     |
| Java      | 17      |

---

## Startup

Start infrastructure:

```bash
docker compose up -d
```

Services:

| Service       | URL                                  |
| ------------- | ------------------------------------ |
| MinIO Console | http://localhost:9001                |
| Nessie API    | http://localhost:19120/api/v2/config |
| Trino UI      | http://localhost:8080                |

MinIO credentials:

```text
user: admin
password: password123
```

Create bucket:

```text
warehouse
```

---

## Spark Catalog Configuration

Catalog:

```text
nessie
```

Namespace:

```text
tpch
```

Warehouse:

```text
s3a://warehouse/
```

---

## Data Flow

Source:

```text
TPCH Parquet Files
```

Load:

```python
spark.read.parquet(...)
    .writeTo("nessie.tpch.<table>")
    .using("iceberg")
    .createOrReplace()
```

Result:

```text
Parquet
  -> Iceberg Data Files
  -> Metadata Files
  -> Nessie Catalog Entries
```

---

## Useful Spark Commands

Create namespace:

```sql
CREATE NAMESPACE IF NOT EXISTS nessie.tpch;
```

Show tables:

```sql
SHOW TABLES IN nessie.tpch;
```

Row count:

```sql
SELECT COUNT(*)
FROM nessie.tpch.lineitem;
```

Metadata:

```sql
SELECT * FROM nessie.tpch.customer.snapshots;

SELECT * FROM nessie.tpch.customer.history;

SELECT * FROM nessie.tpch.customer.files;
```

---

## Nessie Branching

Create branch:

```sql
CREATE BRANCH experiment IN nessie;
```

Switch branch:

```sql
USE REFERENCE experiment IN nessie;
```

Show current branch:

```sql
SHOW CURRENT REFERENCE IN nessie;
```

Switch back:

```sql
USE REFERENCE main IN nessie;
```

---

## Trino Catalogs

Configured catalogs:

```text
iceberg_main
iceberg_experiment
```

Each catalog maps to a Nessie branch:

```text
iceberg_main       -> main
iceberg_experiment -> experiment
```

Show catalogs:

```sql
SHOW CATALOGS;
```

Show tables:

```sql
SHOW TABLES FROM iceberg_main.tpch;

SHOW TABLES FROM iceberg_experiment.tpch;
```

Query:

```sql
SELECT COUNT(*)
FROM iceberg_main.tpch.lineitem;
```

---

## Validation Performed

* Loaded all TPCH tables into Iceberg
* Verified row counts between source Parquet and Iceberg
* Verified Iceberg metadata tables
* Verified Spark read/write
* Verified Trino read
* Verified Nessie branching
* Verified branch visibility through multiple Trino catalogs

---

## Key Learning

Iceberg is the table layer.

```text
Spark  ─┐
        ├─> Iceberg
Trino ──┘
```

Multiple engines can read and write the same tables through a common catalog and storage layer.
