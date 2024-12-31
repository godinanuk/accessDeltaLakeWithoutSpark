import duckdb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

azure_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
azure_connection_string = os.getenv("AZURE_CONNECTION_STRING")

# Initialize DuckDB connection and Azure configurations
fs_url = f"azure://{azure_account_name}.dfs.core.windows.net"
conn = duckdb.connect()
conn.execute("INSTALL delta; LOAD delta;")
conn.execute("INSTALL azure; LOAD azure;")
conn.execute(f"SET azure_storage_connection_string = '{azure_connection_string}';")

# Example Delta table path
delta_table_path = f"{fs_url}/nonsparkaccess/my/delta/duckdb/dec2024/part*/*.parquet"
