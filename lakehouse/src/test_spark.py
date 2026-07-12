from spark_session import spark

print(spark.range(10).count())


spark.sql("CREATE NAMESPACE IF NOT EXISTS nessie.tpch")

spark.sql("SHOW NAMESPACES IN nessie").show()

print("creating iceberg table")
spark.sql("""
CREATE TABLE if not exists nessie.tpch.test_table (
    id BIGINT,
    name STRING
)
USING iceberg
""")

print("inserting data into test_table")
spark.sql("""
INSERT INTO nessie.tpch.test_table
VALUES
(1, 'a'),
(2, 'b')
""")

print("fetching data from test_table")
spark.sql("""
SELECT *
FROM nessie.tpch.test_table
""").show()
