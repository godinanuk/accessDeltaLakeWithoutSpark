import json, os
from ariadne import QueryType, MutationType, make_executable_schema

def generate_schema_from_json(json_file):
    with open(json_file, 'r') as file:
        table_structure = json.load(file)

    table_name = table_structure["table_name"]
    columns = table_structure["columns"]

    # Generate type definition for the table
    fields = []
    for col in columns:
        col_type = f"{col['type']}{'!' if col['required'] else ''}"
        fields.append(f"{col['name']}: {col_type}")
    fields_str = "\n        ".join(fields)

    type_def = f"""
    type {table_name} {{
        {fields_str}
    }}
    """

    # Generate query and mutation definitions
    query_def = f"""
    type Query {{
        get{table_name}s: [{table_name}!]!
    }}
    """

    mutation_fields = [
        f"insert{table_name}({', '.join([f'{col['name']}: {col['type']}{'!' if col['required'] else ''}' for col in columns])}): String!\n       ",
        f"update{table_name}(id: Int!, {', '.join([f'{col['name']}: {col['type']}' for col in columns if col['name'] != 'id'])}): String!\n       ",
        f"delete{table_name}(id: Int!): String!"
    ]
    mutation_def = f"""
    type Mutation {{
        {' '.join(mutation_fields)}
    }}
    """

    schema_def = type_def + query_def + mutation_def

    return schema_def


def save_schema_to_file(schema_str, file_path):
    with open(file_path, 'w') as file:
        file.write(schema_str)

def create_schema_definition():

    folder_path = os.getcwd() + "/app_graphql/"
    schema_file = folder_path + "/table_structure.json"
    output_file = folder_path + "/generated_schema.py"

    schema_str = generate_schema_from_json(schema_file)
    schema_code = f"""
from ariadne import QueryType, MutationType, make_executable_schema
from app_graphql.resolvers import query, mutation

# GraphQL schema definition
type_defs = \"\"\"{schema_str}\"\"\"

# Create the executable schema
schema = make_executable_schema(type_defs, query, mutation)
    """
    save_schema_to_file(schema_code, output_file)
    print(f"Schema saved to {output_file}")
