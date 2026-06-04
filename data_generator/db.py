import contextlib
import os

import duckdb
from loguru import logger

from utils import timeit

# Profiling configurations
BREAKDOWNS = {
    "customer": ["c_nationkey", "c_mktsegment"],
    "orders": ["o_orderdate", "o_orderstatus"],
    "lineitem": ["l_shipdate", "l_returnflag"],
}

EXPECTED_SCHEMAS = {
    "customer": {
        "c_custkey": "BIGINT",
        "c_name": "VARCHAR",
        "c_address": "VARCHAR",
        "c_nationkey": "BIGINT",
        "c_phone": "VARCHAR",
        "c_acctbal": "DECIMAL(15,2)",
        "c_mktsegment": "VARCHAR",
        "c_comment": "VARCHAR",
    },
    "orders": {
        "o_orderkey": "BIGINT",
        "o_custkey": "BIGINT",
        "o_orderstatus": "VARCHAR",
        "o_totalprice": "DECIMAL(15,2)",
        "o_orderdate": "DATE",
        "o_orderpriority": "VARCHAR",
        "o_clerk": "VARCHAR",
        "o_shippriority": "BIGINT",
        "o_comment": "VARCHAR",
    },
    "lineitem": {
        "l_orderkey": "BIGINT",
        "l_partkey": "BIGINT",
        "l_suppkey": "BIGINT",
        "l_linenumber": "BIGINT",
        "l_quantity": "DECIMAL(15,2)",
        "l_extendedprice": "DECIMAL(15,2)",
        "l_discount": "DECIMAL(15,2)",
        "l_tax": "DECIMAL(15,2)",
        "l_returnflag": "VARCHAR",
        "l_linestatus": "VARCHAR",
        "l_shipdate": "DATE",
        "l_commitdate": "DATE",
        "l_receiptdate": "DATE",
        "l_shipinstruct": "VARCHAR",
        "l_shipmode": "VARCHAR",
        "l_comment": "VARCHAR",
    },
    # Add other tables if needed
}


@contextlib.contextmanager
def get_db_connection(db_name: str = "lake-forge.duckdb"):
    """
    Get a connection to the duckdb database.
    """
    logger.info(f"Connecting to database: {db_name}")
    con = duckdb.connect(database=db_name, read_only=False)
    con.execute("SET memory_limit='6GB'")
    con.execute("SET threads=6")
    con.execute("SET temp_directory='/mnt/c/temp/duckdb_temp'")
    try:
        logger.info(f"Connected to database: {db_name}")
        yield con
    finally:
        logger.info(f"Closing database connection: {db_name}")
        con.close()
        logger.info(f"Closed database connection: {db_name}")


@timeit("Loading data into database")
def load_into_db(data_dir_path: str, db_name: str) -> dict[str, str]:
    """
    Load all the generated Parquet files into duckdb.
    """
    logger.info(
        f"Loading data into database: {db_name} from directory: {data_dir_path}"
    )
    all_files = get_entity_path_map(data_dir_path)

    with get_db_connection(db_name=db_name) as con:
        for table_name, file_path in all_files.items():
            create_table_from_parquet(con, table_name, file_path)

    logger.info("Finished loading data")
    return all_files


def get_entity_path_map(data_dir_path: str) -> dict[str, str]:
    """
    Get a mapping of entity names to their corresponding Parquet file paths.
    Like, {"nation": "/path/to/nation.parquet", ...}
    """
    all_files = {}
    for root, _, filenames in os.walk(data_dir_path):
        for filename in filenames:
            table_name = filename.split(".")[0]
            file_path = os.path.join(root, filename)
            all_files[table_name] = file_path
    return all_files


def create_table_from_parquet(
    con: duckdb.DuckDBPyConnection, table_name: str, file_path: str
):
    """
    Create a table in duckdb from a Parquet file.
    """
    logger.info(f"Creating table '{table_name}' from file: {file_path}")
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM '{file_path}'")


@timeit("Data validation")
def validate_data(table_map: dict[str, str], db_name: str):
    """
    Validate that the data has been loaded correctly by running some sample queries.
    """
    with get_db_connection(db_name=db_name) as con:
        for table_name in table_map.keys():
            profile_rows(con, table_name)


def count_rows(con: duckdb.DuckDBPyConnection, table_name: str):
    """
    Count the number of rows in a given table.
    """
    result = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    if result is None:
        logger.error(f"Table '{table_name}' is empty or does not exist.")
    else:
        logger.info(f"Table: '{table_name}', rows: {result[0]}")


def profile_rows(con: duckdb.DuckDBPyConnection, table_name: str):
    """
    Profile row counts with breakdowns for a given table.
    """
    # Total count
    result = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    total = result[0] if result else 0
    logger.info(f"Table '{table_name}': total rows {total}")

    # Breakdowns
    group_by_columns = BREAKDOWNS.get(table_name, [])
    for col in group_by_columns:
        query = (
            f"SELECT {col}, COUNT(*) FROM {table_name} "
            f"GROUP BY {col} ORDER BY COUNT(*) DESC LIMIT 10"
        )
        results = con.execute(query).fetchall()
        logger.info(f"Table '{table_name}': top 10 {col} counts: {results}")


def analyze_nulls(con: duckdb.DuckDBPyConnection, table_name: str):
    """
    Analyze null counts per column for a given table.
    """
    columns = con.execute(f"DESCRIBE {table_name}").fetchall()
    for row in columns:
        col_name = row[0]
        result = con.execute(
            f"SELECT COUNT(*) - COUNT({col_name}) FROM {table_name}"
        ).fetchone()
        if result is not None:
            null_count = result[0]
            logger.info(
                f"Table '{table_name}', column '{col_name}': nulls {null_count}"
            )
        else:
            logger.error(f"Table '{table_name}', column '{col_name}': no records found")


def check_distributions(con: duckdb.DuckDBPyConnection, table_name: str):
    """
    Check value distributions for columns in a given table.
    """
    columns = con.execute(f"DESCRIBE {table_name}").fetchall()
    for row in columns:
        col_name, col_type = row[0], row[1]
        if "VARCHAR" in col_type or "CHAR" in col_type:
            # Categorical
            results = con.execute(
                f"SELECT {col_name}, COUNT(*) FROM {table_name} "
                f"GROUP BY {col_name} ORDER BY COUNT(*) DESC LIMIT 10"
            ).fetchall()
            logger.info(
                f"Table '{table_name}', column '{col_name}': top values {results}"
            )
        elif "DECIMAL" in col_type or "INTEGER" in col_type or "BIGINT" in col_type:
            # Numeric
            stats = con.execute(
                f"SELECT MIN({col_name}), MAX({col_name}), AVG({col_name}), "
                f"STDDEV({col_name}) FROM {table_name}"
            ).fetchone()
            if stats is not None:
                logger.info(
                    f"Table '{table_name}', column '{col_name}': min={stats[0]}, "
                    f"max={stats[1]}, avg={stats[2]}, stddev={stats[3]}"
                )
            else:
                logger.error(
                    f"Table '{table_name}', column '{col_name}': "
                    "no data to compute stats"
                )
        # Skip other types like DATE


def validate_schemas(con: duckdb.DuckDBPyConnection, table_name: str):
    """
    Validate schema for a given table against expected schema.
    """
    actual_schema = con.execute(f"DESCRIBE {table_name}").fetchall()
    expected = EXPECTED_SCHEMAS.get(table_name, {})
    logger.info(f"Table '{table_name}' actual schema: {actual_schema}")
    if expected:
        mismatches = []
        for row in actual_schema:
            col_name, col_type = row[0], row[1]
            if col_name in expected and expected[col_name] != col_type:
                mismatches.append(
                    f"{col_name}: expected {expected[col_name]}, got {col_type}"
                )
        if mismatches:
            logger.warning(f"Table '{table_name}' schema mismatches: {mismatches}")
        else:
            logger.info(f"Table '{table_name}' schema matches expected.")
    else:
        logger.error(f"Table '{table_name}' no expected schema defined.")


@timeit("Scan benchmark")
def benchmark_scan(con: duckdb.DuckDBPyConnection, table_name: str):
    """
    Run simple scan benchmark on a table.
    """
    result = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    if result is not None:
        logger.info(f"Scan benchmark '{table_name}': count {result[0]}")
    else:
        logger.error(f"Scan benchmark '{table_name}': no data found")


@timeit("Aggregation benchmark")
def benchmark_aggregation(con: duckdb.DuckDBPyConnection, table_name: str):
    """
    Run aggregation benchmark on a table.
    """
    if table_name == "orders":
        result = con.execute(
            "SELECT o_orderdate, SUM(o_totalprice), COUNT(*) FROM orders "
            "GROUP BY o_orderdate ORDER BY o_orderdate DESC LIMIT 10"
        ).fetchall()
        logger.info(f"Aggregation benchmark 'orders': top dates {result}")
    elif table_name == "lineitem":
        result = con.execute(
            "SELECT l_shipdate, SUM(l_extendedprice), COUNT(*) FROM lineitem "
            "GROUP BY l_shipdate ORDER BY l_shipdate DESC LIMIT 10"
        ).fetchall()
        logger.info(f"Aggregation benchmark 'lineitem': top dates {result}")
    else:
        logger.info(
            f"Aggregation benchmark '{table_name}': skipped (no aggregation defined)"
        )


@timeit("Join benchmark")
def benchmark_join(con: duckdb.DuckDBPyConnection):
    """
    Run join benchmark across tables.
    """
    result = con.execute("""
        SELECT COUNT(*)
        FROM customer c
        JOIN orders o ON c.c_custkey = o.o_custkey
        JOIN lineitem l ON o.o_orderkey = l.l_orderkey
    """).fetchone()
    if result is not None:
        logger.info(f"Join benchmark: count {result[0]}")
    else:
        logger.error("Join benchmark: no data found")


@timeit("Dataset profiling")
def profile_data(table_map: dict[str, str], db_name: str):
    """
    Run full profiling suite on loaded tables.
    """
    with get_db_connection(db_name=db_name) as con:
        for table_name in table_map.keys():
            logger.info(f"Profiling table: {table_name}")
            profile_rows(con, table_name)
            analyze_nulls(con, table_name)
            check_distributions(con, table_name)
            validate_schemas(con, table_name)
            benchmark_scan(con, table_name)
            benchmark_aggregation(con, table_name)
        # Join benchmark once
        benchmark_join(con)
