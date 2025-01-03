from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app_graphql.playground_html import PLAYGROUND_HTML
from ariadne import graphql_sync
from app_graphql.generate_schema import create_schema_definition

# Generate Schema Definition
create_schema_definition()
from app_graphql.generated_schema import schema

# FastAPI application
app = FastAPI()

@app.get("/graphql", response_class=HTMLResponse)
def graphql_playground():
    return PLAYGROUND_HTML

@app.post("/graphql")
async def graphql_server(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug if hasattr(app, 'debug') else False
    )
    status_code = 200 if success else 400
    return JSONResponse(content=result, status_code=status_code)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
