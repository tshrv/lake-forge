from pyspark.sql import SparkSession


def create_spark():
    return (
        SparkSession.builder.appName("lakehouse-v2")
        # .master("local[*]")
        .master("local[4]")
        .config("spark.driver.memory", "6g")
        .config("spark.sql.shuffle.partitions", "16")
        .config(
            "spark.jars.packages",
            ",".join(
                [
                    "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.11.0",
                    "org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.106.0",
                    "org.apache.hadoop:hadoop-aws:3.3.4",
                    "software.amazon.awssdk:bundle:2.31.67",
                    "software.amazon.awssdk:url-connection-client:2.31.67",
                ]
            ),
        )
        .config(
            "spark.sql.extensions",
            ",".join(
                [
                    "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
                    "org.projectnessie.spark.extensions.NessieSparkSessionExtensions",
                ]
            ),
        )
        .config(
            "spark.sql.catalog.lakeforge.io-impl",
            "org.apache.iceberg.aws.s3.S3FileIO",
        )
        .config("spark.sql.catalog.lakeforge", "org.apache.iceberg.spark.SparkCatalog")
        .config(
            "spark.sql.catalog.lakeforge.catalog-impl",
            "org.apache.iceberg.nessie.NessieCatalog",
        )
        .config("spark.sql.catalog.lakeforge.uri", "http://localhost:19120/api/v1")
        .config("spark.sql.catalog.lakeforge.ref", "main")
        .config("spark.sql.catalog.lakeforge.warehouse", "s3://warehouse/")
        .config("spark.sql.catalog.lakeforge.s3.endpoint", "http://localhost:9000")
        .config("spark.sql.catalog.lakeforge.s3.path-style-access", "true")
        .config("spark.sql.catalog.lakeforge.s3.access-key-id", "admin")
        .config("spark.sql.catalog.lakeforge.s3.secret-access-key", "password123")
        .config(
            "spark.hadoop.fs.s3a.endpoint",
            "http://localhost:9000",
        )
        .config(
            "spark.hadoop.fs.s3a.access.key",
            "admin",
        )
        .config(
            "spark.hadoop.fs.s3a.secret.key",
            "password123",
        )
        .config(
            "spark.hadoop.fs.s3a.path.style.access",
            "true",
        )
        .config(
            "spark.hadoop.fs.s3a.impl",
            "org.apache.hadoop.fs.s3a.S3AFileSystem",
        )
        .config(
            "spark.sql.catalog.lakeforge.s3.region",
            "us-east-1",
        )
        .config(
            "spark.hadoop.fs.s3a.endpoint.region",
            "us-east-1",
        )
        .config(
            "spark.driver.extraJavaOptions",
            "-Daws.region=us-east-1",
        )
        .config(
            "spark.executor.extraJavaOptions",
            "-Daws.region=us-east-1",
        )
        .getOrCreate()
    )


spark = create_spark()
