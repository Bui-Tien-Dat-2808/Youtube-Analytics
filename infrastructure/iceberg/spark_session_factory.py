from __future__ import annotations

from pyspark.sql import SparkSession

from shared.config.settings import Settings


def build_spark_session(settings: Settings, app_name: str) -> SparkSession:
    builder = (
        SparkSession.builder.appName(app_name)
        .config("spark.master", settings.spark_master_url)
        .config(
            f"spark.sql.catalog.{settings.iceberg_catalog_name}",
            "org.apache.iceberg.spark.SparkCatalog",
        )
        .config(
            f"spark.sql.catalog.{settings.iceberg_catalog_name}.type",
            settings.iceberg_catalog_type,
        )
        .config(
            f"spark.sql.catalog.{settings.iceberg_catalog_name}.warehouse",
            settings.iceberg_warehouse_path,
        )
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.defaultCatalog", settings.iceberg_catalog_name)
        .config("spark.sql.session.timeZone", "UTC")
    )
    if settings.spark_jars_packages:
        builder = builder.config("spark.jars.packages", settings.spark_jars_packages)

    return builder.getOrCreate()
