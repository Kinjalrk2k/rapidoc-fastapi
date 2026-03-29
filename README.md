# fastapi-rapidoc-router

Simple reusable RapiDoc router for FastAPI projects.

## Install

```bash
pip install .
```

Or from a Git repository:

```bash
pip install git+https://github.com/<your-org>/<your-repo>.git
```

## Usage

```python
from fastapi import FastAPI
from rapidoc_fastapi import mount_rapidoc

app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

mount_rapidoc(app, docs_path="/docs", title="My API Docs")
```

## Router API

```python
from rapidoc_fastapi import create_rapidoc_router

router = create_rapidoc_router(
    docs_path="/docs",
    openapi_url="/openapi.json",
    title="My API Docs",
)

app.include_router(router)
```

## Notes

- `docs_path` controls where RapiDoc UI is served.
- `openapi_url` defaults to the app OpenAPI endpoint.
- This package uses the official RapiDoc script from CDN by default.
