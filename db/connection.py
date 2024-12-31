import duckdb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get cloud provider from environment variables
cloud_provider = os.getenv("CLOUD_PROVIDER", "azure").lower()

# Initialize DuckDB connection
conn = duckdb.connect()

# Configuration for different cloud providers
if cloud_provider == "azure":
    azure_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    azure_connection_string = os.getenv("AZURE_CONNECTION_STRING")
    fs_url = f"azure://{azure_account_name}.dfs.core.windows.net"

    conn.execute("INSTALL azure; LOAD azure;")
    conn.execute(f"SET azure_storage_connection_string = '{azure_connection_string}';")

elif cloud_provider == "aws":
    aws_s3_bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    fs_url = f"s3://{aws_s3_bucket_name}"

    conn.execute("INSTALL httpfs; LOAD httpfs;")
    conn.execute(f"SET s3_access_key_id = '{aws_access_key_id}';")
    conn.execute(f"SET s3_secret_access_key = '{aws_secret_access_key}';")

elif cloud_provider == "gcp":
    gcp_bucket_name = os.getenv("GCP_BUCKET_NAME")
    gcp_credentials_json = os.getenv("GCP_CREDENTIALS_JSON")  # Path to GCP JSON credentials
    fs_url = f"gs://{gcp_bucket_name}"

    conn.execute("INSTALL gcs; LOAD gcs;")
    conn.execute(f"SET google_application_credentials = '{gcp_credentials_json}';")

else:
    raise ValueError("Unsupported cloud provider. Please set CLOUD_PROVIDER to 'azure', 'aws', or 'gcp'.")

# Common configuration for Delta and Parquet handling
conn.execute("INSTALL delta; LOAD delta;")

# Example Delta table path
delta_table_path = f"{fs_url}/nonsparkaccess/my/delta/duckdb/dec2024/part*/*.parquet"
