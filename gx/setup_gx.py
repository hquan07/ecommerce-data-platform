import os
import great_expectations as gx
from great_expectations.expectations.core import (
    ExpectColumnValuesToNotBeNull,
    ExpectColumnValuesToBeUnique,
    ExpectColumnValuesToBeBetween
)
from great_expectations.checkpoint.actions import UpdateDataDocsAction

def setup_gx():
    print("Initializing Great Expectations Context...")
    context = gx.get_context(mode="file")

    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = os.getenv("POSTGRES_PORT", "5433")
    pg_user = os.getenv("POSTGRES_USER", "ecommerce")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "ecommerce")
    pg_db = os.getenv("POSTGRES_DB", "ecommerce")
    
    connection_string = f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    datasource_name = "ecommerce_postgres"
    
    print(f"Connecting to Postgres: {datasource_name}")
    try:
        datasource = context.data_sources.add_postgres(
            name=datasource_name,
            connection_string=connection_string
        )
    except Exception as e:
        print(f"Datasource exists, getting it... {e}")
        datasource = context.data_sources.get(datasource_name)

    # Asset 1: dim_customer
    asset_customer_name = "dim_customer_asset"
    try:
        asset_customer = datasource.add_table_asset(name=asset_customer_name, table_name="dim_customer", schema_name="dw")
    except Exception:
        asset_customer = datasource.get_asset(asset_customer_name)

    # Asset 2: fact_orders
    asset_orders_name = "fact_orders_asset"
    try:
        asset_orders = datasource.add_table_asset(name=asset_orders_name, table_name="fact_orders", schema_name="dw")
    except Exception:
        asset_orders = datasource.get_asset(asset_orders_name)

    # Suite 1: dim_customer_suite
    suite_customer_name = "dim_customer_suite"
    try:
        suite_customer = gx.ExpectationSuite(name=suite_customer_name)
        suite_customer.add_expectation(ExpectColumnValuesToNotBeNull(column="customer_id"))
        suite_customer.add_expectation(ExpectColumnValuesToBeUnique(column="customer_id"))
        suite_customer.add_expectation(ExpectColumnValuesToNotBeNull(column="customer_city"))
        context.suites.add(suite_customer)
    except Exception:
        suite_customer = context.suites.get(suite_customer_name)

    # Suite 2: fact_orders_suite
    suite_orders_name = "fact_orders_suite"
    try:
        suite_orders = gx.ExpectationSuite(name=suite_orders_name)
        suite_orders.add_expectation(ExpectColumnValuesToNotBeNull(column="order_id"))
        suite_orders.add_expectation(ExpectColumnValuesToBeUnique(column="order_id"))
        suite_orders.add_expectation(ExpectColumnValuesToNotBeNull(column="customer_id"))
        context.suites.add(suite_orders)
    except Exception:
        suite_orders = context.suites.get(suite_orders_name)

    # Validation Definitions
    batch_def_customer_name = "whole_table_customer"
    try:
        batch_def_customer = asset_customer.add_batch_definition_whole_table(batch_def_customer_name)
    except Exception:
        batch_def_customer = asset_customer.get_batch_definition(batch_def_customer_name)

    try:
        val_def_customer = gx.ValidationDefinition(name="val_def_customer", data=batch_def_customer, suite=suite_customer)
        context.validation_definitions.add(val_def_customer)
    except Exception:
        val_def_customer = context.validation_definitions.get("val_def_customer")

    batch_def_orders_name = "whole_table_orders"
    try:
        batch_def_orders = asset_orders.add_batch_definition_whole_table(batch_def_orders_name)
    except Exception:
        batch_def_orders = asset_orders.get_batch_definition(batch_def_orders_name)

    try:
        val_def_orders = gx.ValidationDefinition(name="val_def_orders", data=batch_def_orders, suite=suite_orders)
        context.validation_definitions.add(val_def_orders)
    except Exception:
        val_def_orders = context.validation_definitions.get("val_def_orders")

    # Checkpoint
    checkpoint_name = "ecommerce_daily_checkpoint"
    try:
        checkpoint = gx.Checkpoint(
            name=checkpoint_name,
            validation_definitions=[val_def_customer, val_def_orders],
            actions=[UpdateDataDocsAction(name="update_data_docs")]
        )
        context.checkpoints.add(checkpoint)
    except Exception:
        checkpoint = context.checkpoints.get(checkpoint_name)

    print("Running Checkpoint to validate data...")
    results = checkpoint.run()
    
    print(f"Validation successful: {results.success}")
    print("Data Docs generated. Setup complete.")

if __name__ == "__main__":
    setup_gx()
