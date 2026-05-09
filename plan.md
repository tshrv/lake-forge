# LakeForge — Jira Hierarchy (Detailed Execution Plan)

Use this structure directly in Jira.

Recommended hierarchy:

```text id="yxyqk0"
Epic
  → Story
      → Subtask
```

Recommended sprint duration:

* 1 week
* 3–5 stories per sprint maximum

---

# EPIC 1 — Foundation

## Goal

Generate benchmark datasets and validate them locally.

## Story 1.1 — Generate TPC-H Parquet Datasets

### Description

Generate reproducible TPC-H datasets and store them as parquet files.

### Subtasks

* Setup TPC generator tooling
* Generate SF1 customer dataset
* Generate SF1 orders dataset
* Generate SF1 lineitem dataset
* Validate row counts
* Create parquet conversion scripts
* Validate schema consistency
* Validate parquet readability
* Create raw dataset layout
* Create scale-factor folders
* Add dataset metadata

### Acceptance Criteria

* parquet datasets generated successfully
* reproducible generation steps documented
* datasets organized consistently

### Definition of Done

* datasets committed/generated
* README updated
* commands documented
* parquet files queryable

## Story 1.2 — DuckDB Dataset Profiling

### Description

Validate and profile parquet datasets using DuckDB.

### Subtasks

* Install DuckDB
* Configure notebooks/scripts
* Validate parquet connectivity
* Create row count profiling queries
* Create null analysis queries
* Create distribution check queries
* Create schema validation queries
* Run simple scan benchmark
* Run aggregation benchmark
* Run join benchmark

### Acceptance Criteria

* profiling scripts execute successfully
* benchmark outputs generated

### Definition of Done

* notebooks/scripts committed
* profiling reports saved
* benchmark results documented

---

# EPIC 2 — Lakehouse Core

## Goal

Build the core open lakehouse infrastructure.

## Story 2.1 — Configure MinIO Object Storage

### Description

Setup S3-compatible object storage for lakehouse datasets.

### Subtasks

* Add MinIO docker compose service
* Configure credentials
* Configure ports
* Create raw bucket
* Create staging bucket
* Create marts bucket
* Create upload script
* Validate uploads
* Validate permissions

### Acceptance Criteria

* datasets accessible through MinIO
* upload automation works

### Definition of Done

* MinIO operational
* buckets documented
* upload scripts committed

## Story 2.2 — Configure Iceberg Tables

### Description

Create Iceberg tables over parquet datasets.

### Subtasks

* Configure connectors
* Validate storage access
* Validate metadata location
* Create customer Iceberg table
* Create orders Iceberg table
* Create lineitem Iceberg table
* Insert test records
* Validate snapshots
* Validate schema evolution

### Acceptance Criteria

* Iceberg tables operational
* snapshots visible

### Definition of Done

* tables queryable
* metadata validated
* schema evolution tested

## Story 2.3 — Configure Nessie Catalog

### Description

Setup Nessie as Iceberg catalog layer.

### Subtasks

* Configure Nessie docker service
* Configure persistence
* Validate Nessie connectivity
* Configure catalog URI
* Validate branch access
* Validate namespace creation
* Create test branches
* Validate snapshot history
* Validate time travel

### Acceptance Criteria

* Nessie catalog operational
* versioning works

### Definition of Done

* branches functional
* documentation updated
* integration validated

## Story 2.4 — Configure Trino Query Engine

### Description

Enable distributed SQL querying over Iceberg tables.

### Subtasks

* Add Trino docker compose service
* Configure coordinator
* Validate Trino startup
* Configure Nessie connector
* Configure S3 access
* Configure warehouse path
* Run aggregation queries
* Run join queries
* Validate partition pruning

### Acceptance Criteria

* Trino queries execute successfully

### Definition of Done

* query examples documented
* benchmark queries saved
* connectivity validated

---

# EPIC 3 — Analytics Engineering

## Goal

Build transformation layers and marts using dbt.

## Story 3.1 — Setup dbt Project

### Description

Initialize dbt project and connect to Trino.

### Subtasks

* Create dbt project
* Configure profiles
* Configure environments
* Define staging models structure
* Define intermediate models structure
* Define marts structure
* Add schema tests
* Add source tests
* Configure documentation generation

### Acceptance Criteria

* dbt runs successfully

### Definition of Done

* dbt project operational
* tests executable
* docs generated

## Story 3.2 — Create Staging Models

### Description

Build standardized staging layer.

### Subtasks

* Create stg_customer model
* Create stg_orders model
* Create stg_lineitem model
* Rename fields to standard names
* Standardize datatypes
* Remove invalid records

### Acceptance Criteria

* staging models materialize successfully

### Definition of Done

* models documented
* tests passing
* lineage visible

## Story 3.3 — Create Intermediate Models

### Description

Build reusable analytical transformations.

### Subtasks

* Build order aggregation model
* Build revenue aggregation model
* Build customer segmentation model
* Build shipping metrics model
* Build fulfillment metrics model
* Build discount metrics model

### Acceptance Criteria

* intermediate models reusable and validated

### Definition of Done

* metrics validated
* incremental models tested

## Story 3.4 — Create Business Marts

### Description

Expose analytics-ready marts.

### Subtasks

* Create regional revenue mart
* Create monthly revenue mart
* Create product revenue mart
* Create customer lifetime value mart
* Create order frequency mart
* Create retention metrics mart

### Acceptance Criteria

* marts queryable through Trino

### Definition of Done

* marts documented
* dashboards ready
* tests passing

---

# EPIC 4 — Orchestration

## Goal

Automate workflows using Airflow.

## Story 4.1 — Setup Airflow

### Description

Deploy and configure Airflow for pipeline orchestration.

### Subtasks

* Setup Airflow scheduler
* Setup Airflow webserver
* Configure metadata DB
* Validate DAG execution

## Story 4.2 — Create Ingestion DAG

### Description

Build Airflow DAGs for data ingestion automation.

### Subtasks

* Create parquet upload DAG
* Create Iceberg refresh DAG
* Configure retry policies
* Configure notifications

## Story 4.3 — Create Transformation DAG

### Description

Build Airflow DAGs for dbt transformation orchestration.

### Subtasks

* Create dbt execution DAG
* Create testing DAG
* Configure dependency orchestration

---

# EPIC 5 — Data Quality

## Goal

Validate platform reliability and trust.

## Story 5.1 — Setup Great Expectations

### Description

Configure Great Expectations for data quality validation.

### Subtasks

* Configure Great Expectations
* Create expectation suites
* Configure validations

## Story 5.2 — Add Freshness Checks

### Description

Add data freshness monitoring and SLA validation.

### Subtasks

* Implement source freshness checks
* Implement SLA validation
* Configure stale data alerts

## Story 5.3 — Add Integrity Validation

### Description

Add data integrity checks for uniqueness, FK constraints, nulls, and distributions.

### Subtasks

* Implement uniqueness checks
* Implement FK validation
* Implement null checks
* Implement distribution checks

---

# EPIC 6 — Streaming Platform

## Goal

Introduce real-time ingestion and CDC.

## Story 6.1 — Setup Kafka/Redpanda

### Description

Setup streaming broker infrastructure.

### Subtasks

* Setup brokers
* Configure topics
* Validate producers/consumers

## Story 6.2 — Create Event Producers

### Description

Create Kafka event producers for business events.

### Subtasks

* Build orders producer
* Build payments producer
* Build shipment producer

## Story 6.3 — Configure Debezium CDC

### Description

Configure Debezium for Change Data Capture from Postgres.

### Subtasks

* Setup Postgres source
* Configure Debezium connectors
* Validate CDC events

## Story 6.4 — Stream Events into Iceberg

### Description

Ingest streaming events into Iceberg tables with deduplication.

### Subtasks

* Implement streaming ingestion
* Implement incremental merges
* Implement deduplication

---

# EPIC 7 — Observability

## Goal

Monitor platform health and performance.

## Story 7.1 — Setup Prometheus

### Description

Configure Prometheus for metrics collection.

### Subtasks

* Configure metrics scraping
* Configure service discovery
* Configure exporter

## Story 7.2 — Setup Grafana

### Description

Configure Grafana dashboards for platform observability.

### Subtasks

* Create query metrics dashboard
* Create ingestion metrics dashboard
* Create system health dashboard

## Story 7.3 — Setup Loki

### Description

Configure Loki for centralized log aggregation.

### Subtasks

* Configure centralized log collection
* Configure pipeline log streams
* Configure query log streams

---

# EPIC 8 — BI & Consumption

## Goal

Expose analytics visually.

## Story 8.1 — Setup Superset

### Description

Configure Apache Superset for BI and data visualization.

### Subtasks

* Configure Trino datasource
* Connect Superset to Trino
* Validate connectivity

## Story 8.2 — Build Dashboards

### Description

Build business intelligence dashboards in Superset.

### Subtasks

* Build revenue dashboard
* Build customer dashboard
* Build operational metrics dashboard

---

# EPIC 9 — Benchmarking

## Goal

Benchmark platform performance.

## Story 9.1 — Benchmark DuckDB

### Description

Benchmark DuckDB performance on parquet datasets.

### Subtasks

* Run parquet scan benchmarks
* Run aggregation benchmarks
* Run join benchmarks

## Story 9.2 — Benchmark Trino

### Description

Benchmark Trino performance on Iceberg datasets.

### Subtasks

* Run Iceberg query benchmarks
* Run distributed join benchmarks
* Validate partition pruning performance

## Story 9.3 — Engine Comparison

### Description

Compare query engine performance across key dimensions.

### Subtasks

* Compile latency comparison
* Compile throughput comparison
* Compile storage efficiency comparison

---

# EPIC 10 — Advanced Platform Engineering (Optional)

## Story 10.1 — Spark Integration

### Description

Integrate Apache Spark with the Iceberg lakehouse.

### Subtasks

* Configure Spark Iceberg connector
* Run distributed benchmarks
* Compile ETL comparison

## Story 10.2 — ClickHouse Integration

### Description

Integrate ClickHouse for OLAP benchmarking comparison.

### Subtasks

* Run ingestion comparison
* Run OLAP benchmarking
* Compile query latency comparison

## Story 10.3 — Kubernetes Deployment

### Description

Deploy LakeForge platform on Kubernetes.

### Subtasks

* Create Helm charts
* Create Kubernetes manifests
* Validate scaling

---

# Global Definition of Done

Every story must satisfy:

```text id="7klm3z"
- implementation complete
- docker compose works
- validation queries pass
- documentation updated
- screenshots/logs attached
- reproducible steps documented
- no critical unresolved issues
```

---

# Recommended Jira Labels

| Label         | Purpose        |
| ------------- | -------------- |
| infra         | infrastructure |
| analytics     | dbt/marts      |
| streaming     | Kafka/CDC      |
| benchmark     | performance    |
| quality       | validation     |
| ops           | observability  |
| docs          | documentation  |
| orchestration | Airflow        |
| lakehouse     | Iceberg/Nessie |
| storage       | MinIO/parquet  |
