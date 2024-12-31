from db.connection import conn

def load_records_into_temp_table(temp_table_name, condition="TRUE"):
    try:
        conn.execute(f"""
            CREATE OR REPLACE TABLE {temp_table_name} AS
            SELECT * FROM read_parquet('{delta_table_path}')
            WHERE {condition}
        """)
        return f"Loaded records into temporary table '{temp_table_name}' successfully."
    except Exception as e:
        return f"Failed to load records into temporary table: {e}"
