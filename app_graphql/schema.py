from ariadne import QueryType, MutationType, make_executable_schema
from app_graphql.resolvers import query, mutation

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

# Create the executable schema
schema = make_executable_schema(type_defs, query, mutation)
