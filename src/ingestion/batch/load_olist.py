import os
import glob
import logging
import boto3
from botocore.exceptions import NoCredentialsError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MinIO Configuration from Environment Variables
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000') # using docker internal host
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
BUCKET_NAME = 'ecommerce-data'

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=f"http://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name='us-east-1'
    )

def ensure_bucket_exists(s3_client):
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
    except Exception as e:
        logger.info(f"Bucket {BUCKET_NAME} does not exist. Creating...")
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        logger.info(f"Bucket {BUCKET_NAME} created successfully.")

def upload_olist_data():
    s3_client = get_s3_client()
    ensure_bucket_exists(s3_client)
    
    raw_data_path = 'data/raw/olist/'
    csv_files = glob.glob(os.path.join(raw_data_path, '*.csv'))
    
    if not csv_files:
        logger.warning(f"No CSV files found in {raw_data_path}. Please download the Olist dataset.")
        return

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        dataset_name = filename.replace('olist_', '').replace('_dataset.csv', '').replace('.csv', '')
        s3_key = f"bronze/olist/{dataset_name}/{filename}"
        
        logger.info(f"Uploading {filename} to {s3_key}...")
        try:
            s3_client.upload_file(file_path, BUCKET_NAME, s3_key)
            logger.info(f"Successfully uploaded {filename}")
        except NoCredentialsError:
            logger.error("Credentials not available for MinIO")
            break
        except Exception as e:
            logger.error(f"Failed to upload {filename}: {str(e)}")

if __name__ == "__main__":
    upload_olist_data()
