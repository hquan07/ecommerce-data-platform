import pytest

pytest.importorskip("pyspark")

from src.processing.batch.transform_olist import create_spark_session

def test_create_spark_session():
    spark = create_spark_session()
    assert spark is not None
    assert spark.conf.get("spark.hadoop.fs.s3a.impl") == "org.apache.hadoop.fs.s3a.S3AFileSystem"
    spark.stop()
