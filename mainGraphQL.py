from flask import Flask, request, jsonify
from ariadne import QueryType, MutationType, make_executable_schema, graphql_sync
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

# GraphQL schema definition
type_defs = """
    type Row {
        id: Int!
        name: String!
        value: Float!
    }

    type Query {
        getRows: [Row!]!
    }

    type Mutation {
        insertRow(id: Int!, name: String!, value: Float!): String!
        updateRow(id: Int!, value: Float!): String!
        deleteRow(id: Int!): String!
    }
"""

# Query resolvers
query = QueryType()

@query.field("getRows")
def resolve_get_rows(_, info):
    try:
        results = conn.execute(f"SELECT * FROM read_parquet('{delta_table_path}')").fetchall()
        return [{"id": row[0], "name": row[1], "value": row[2]} for row in results]
    except duckdb.Error as e:
        raise Exception(f"Query failed: {e}")

# Mutation resolvers
mutation = MutationType()

def load_records_into_temp_table(temp_table_name, condition="TRUE"):
    try:
        conn.execute(f"""
            CREATE OR REPLACE TABLE {temp_table_name} AS
            SELECT * FROM read_parquet('{delta_table_path}')
            WHERE {condition}
        """)
        return f"Loaded records into temporary table '{temp_table_name}' successfully."
    except duckdb.Error as e:
        return f"Failed to load records into temporary table: {e}"

# Create the executable schema
schema = make_executable_schema(type_defs, query, mutation)

# Custom GraphQL Playground HTML
PLAYGROUND_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset=utf-8/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GraphQL Playground</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/graphql-playground-react@1.7.20/build/static/css/index.css"/>
  <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react@1.7.20/build/static/js/middleware.js"></script>
</head>
<body>
  <div id="root">
    <style>
      body {
        background-color: rgb(23, 42, 58);
        font-family: Open Sans, sans-serif;
        height: 90vh;
      }

      #root {
        height: 100%;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .loading {
        font-size: 1.5em;
        color: rgba(255, 255, 255, 0.6);
        font-family: Open Sans, sans-serif;
      }
    </style>
    <div class="loading">Loading GraphQL Playground...</div>
  </div>
  <script>
    window.addEventListener('load', function (event) {
      GraphQLPlayground.init(document.getElementById('root'), { endpoint: '/graphql' })
    })
  </script>
</body>
</html>
"""

# Flask application
app = Flask(__name__)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True)
