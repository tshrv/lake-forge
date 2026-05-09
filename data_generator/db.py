import contextlib
import os

import duckdb
from loguru import logger

from utils import timeit


@contextlib.contextmanager
def get_db_connection(db_name: str = "lake-forge.duckdb"):
    """
    Get a connection to the duckdb database.
    """
    logger.info(f"Connecting to database: {db_name}")
    con = duckdb.connect(database=db_name, read_only=False)
    try:
        logger.info(f"Connected to database: {db_name}")
        yield con
    finally:
        logger.info(f"Closing database connection: {db_name}")
        con.close()
        logger.info(f"Closed database connection: {db_name}")


@timeit("Loading data into database")
def load_into_db(data_dir_path: str) -> dict[str, str]:
    """
    Load all the generated Parquet files into duckdb.
    """
    logger.info(f"Loading data into database from directory: {data_dir_path}")
    all_files = get_entity_path_map(data_dir_path)

    with get_db_connection() as con:
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
def validate_data(table_map: dict[str, str]):
    """
    Validate that the data has been loaded correctly by running some sample queries.
    """
    with get_db_connection() as con:
        for table_name in table_map.keys():
            count_rows(con, table_name)


def count_rows(con: duckdb.DuckDBPyConnection, table_name: str):
    """
    Count the number of rows in a given table.
    """
    result = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    if result is None:
        logger.error(f"Table '{table_name}' is empty or does not exist.")
    else:
        logger.info(f"Table: '{table_name}', rows: {result[0]}")
