from loguru import logger
from spark_session import spark


def check():
    # test spark <-> minio
    # spark.range(1).write.mode("overwrite").parquet("s3a://warehouse/test")
    logger.info(
        f"Spark driver memory: {spark.sparkContext.getConf().get('spark.driver.memory')}"
    )


def load_table(table_name: str, dir_path: str, i: int):
    logger.info(f"#{i} Loading {table_name} data from parquet file")
    path = f"{dir_path}/{table_name}.parquet"
    df = spark.read.parquet(path)
    logger.info(f"{table_name} data count: {df.count()}")

    logger.info(f"{table_name} data:")
    df.show(5)
    df.printSchema()

    # create iceberg table
    df.writeTo(f"nessie.tpch.{table_name}").using("iceberg").create()

    # verify customer data is in iceberg table
    spark.sql(f"""
        SELECT COUNT(*)
        FROM nessie.tpch.{table_name}
    """).show()
    logger.info(f"Finished loading {table_name} data into iceberg table")


def setup_namespace():
    logger.info("Setting up Nessie namespace")
    spark.sql("""
        CREATE NAMESPACE IF NOT EXISTS nessie.tpch
    """)
    spark.sql("""
        SHOW NAMESPACES IN nessie
    """).show(truncate=False)
    logger.info("Finished setting up Nessie namespace")


def main():
    dir_path = "/home/tushar/lake-forge/data_generator/data/data_sf_10"
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
    setup_namespace()
    for i, table_name in enumerate(table_names):
        load_table(table_name, dir_path, i)
    logger.info("Finished loading all tables into iceberg tables")


if __name__ == "__main__":
    main()
