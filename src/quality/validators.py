import psycopg2
import os
import logging
from rules import RULES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_quality_checks():
    logger.info("Starting Data Quality checks...")
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "ecommerce"),
            user=os.getenv("POSTGRES_USER", "ecommerce"),
            password=os.getenv("POSTGRES_PASSWORD", "ecommerce")
        )
        cur = conn.cursor()
        
        for rule_set in RULES:
            table = rule_set['table']
            for check in rule_set['checks']:
                if check['type'] == 'not_null':
                    col = check['column']
                    query = f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL;"
                    cur.execute(query)
                    result = cur.fetchone()[0]
                    
                    if result > 0:
                        logger.error(f"FAILED: {check['description']} - Found {result} nulls in {table}.{col}")
                        raise ValueError(f"Data Quality Violation in {table}.{col}")
                    else:
                        logger.info(f"PASSED: {check['description']}")
                        
        cur.close()
        conn.close()
        logger.info("All Data Quality checks passed successfully!")
    except Exception as e:
        logger.error(f"Data Quality execution failed: {e}")
        raise e

if __name__ == "__main__":
    run_quality_checks()
