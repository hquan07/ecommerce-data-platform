# Business rules for Data Quality

RULES = [
    {
        "table": "dw.dim_customer",
        "checks": [
            {
                "type": "not_null",
                "column": "customer_unique_id",
                "description": "Customer unique ID must not be null"
            },
            {
                "type": "not_null",
                "column": "customer_id",
                "description": "Customer ID must not be null"
            }
        ]
    }
]
