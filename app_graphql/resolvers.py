from ariadne import QueryType, MutationType
from db.connection import conn, delta_table_path
from db.utilities import load_records_into_temp_table

# Query resolvers
query = QueryType()

@query.field("getRows")
def resolve_get_rows(_, info):
    try:
        results = conn.execute(f"SELECT * FROM read_parquet('{delta_table_path}')").fetchall()
        return [{"id": row[0], "name": row[1], "value": row[2]} for row in results]
    except Exception as e:
        raise Exception(f"Query failed: {e}")

# Mutation resolvers
mutation = MutationType()
# Add other mutation resolvers here
