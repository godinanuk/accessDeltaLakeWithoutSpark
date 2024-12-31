from flask import Flask, request, jsonify
from app_graphql.playground_html import PLAYGROUND_HTML
from ariadne import graphql_sync
from app_graphql.generate_schema import create_schema_definition

# Generate Schema Definition
create_schema_definition()
from app_graphql.generated_schema import schema

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
