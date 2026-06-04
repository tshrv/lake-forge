from loguru import logger
from spark_session import spark


def verify_records(tables: list[str], data_dir_path: str):
    total_data_size_bytes = 0
    for i, table in enumerate(tables, start=1):
        logger.info(f"#{i}/{len(tables)} {table} table")

        src_count = spark.read.parquet(f"{data_dir_path}/{table}.parquet").count()
        logger.info(f"Records count in source parquet file: {src_count}")

        iceberg_count = spark.sql(
            f"select count(*) from nessie.tpch.{table}"
        ).collect()[0][0]
        logger.info(f"Records count in iceberg table: {iceberg_count}")

        size_bytes = spark.sql(f"""
            SELECT SUM(file_size_in_bytes)
            FROM nessie.tpch.{table}.files
        """).collect()[0][0]
        total_data_size_bytes += size_bytes
        logger.info(
            f"Size in iceberg: {size_bytes / 1024 / 1024:.2f} MB ({size_bytes} bytes)"
        )
        logger.info("-" * 50)

    logger.info(
        f"Total data size in iceberg for all tables: {total_data_size_bytes / 1024 / 1024:.2f} MB ({total_data_size_bytes} bytes)"
    )


def main():
    dir_path = "/home/tushar/lake-forge/data_generator/data/data_sf_100"
    table_names = [
        "customer",
        "lineitem",
        "nation",
        "orders",
        "part",
        "partsupp",
        "region",
        "supplier",
    ]
    verify_records(table_names, dir_path)
    logger.info(f"Finished verifying iceberg tables: {', '.join(table_names)}")


if __name__ == "__main__":
    main()
