from __future__ import annotations

from html import escape

from fastapi import APIRouter, FastAPI
from fastapi.responses import HTMLResponse

RAPIDOC_JS_CDN = "https://unpkg.com/rapidoc/dist/rapidoc-min.js"
DEFAULT_FAVICON = "https://ui-avatars.com/api/?name=RapiDoc&rounded=true"


def _normalize_docs_path(docs_path: str) -> str:
    if not docs_path:
        raise ValueError("docs_path must be a non-empty string")

    normalized = docs_path if docs_path.startswith("/") else f"/{docs_path}"
    if normalized != "/":
        normalized = normalized.rstrip("/")

    return normalized


def _render_rapidoc_html(
    *,
    title: str,
    openapi_url: str,
    rapidoc_js_url: str,
    favicon_url: str,
) -> str:
    safe_title = escape(title)
    safe_openapi_url = escape(openapi_url)
    safe_rapidoc_js_url = escape(rapidoc_js_url)
    safe_favicon = escape(favicon_url)

    return f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <script type=\"module\" src=\"{safe_rapidoc_js_url}\"></script>
    <link rel=\"icon\" type=\"image/png\" href=\"{safe_favicon}\" />
    <title>{safe_title}</title>
    <style>
      html,
      body {{
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
      }}

      rapi-doc {{
        height: 100%;
        width: 100%;
      }}
    </style>
  </head>
  <body>
    <rapi-doc
      spec-url=\"{safe_openapi_url}\"
      render-style=\"view\"
      show-components=\"true\"
      layout=\"row\"
      allow-spec-url-load=\"false\"
      allow-spec-file-load=\"false\"
      default-schema-tab=\"schema\"
      persist-auth=\"true\"
      theme=\"dark\"
      bg-color=\"#14191f\"
      text-color=\"#aec2e0\"
    ></rapi-doc>
  </body>
</html>
"""


def create_rapidoc_router(
    *,
    docs_path: str = "/docs",
    openapi_url: str = "/openapi.json",
    title: str = "API Documentation",
    rapidoc_js_url: str = RAPIDOC_JS_CDN,
    favicon_url: str = DEFAULT_FAVICON,
) -> APIRouter:
    """Create an APIRouter exposing a RapiDoc UI page."""
    normalized_docs_path = _normalize_docs_path(docs_path)
    router = APIRouter(tags=["docs"])

    async def rapidoc_ui() -> HTMLResponse:
        html = _render_rapidoc_html(
            title=title,
            openapi_url=openapi_url,
            rapidoc_js_url=rapidoc_js_url,
            favicon_url=favicon_url,
        )
        return HTMLResponse(content=html)

    router.add_api_route(
        path=normalized_docs_path,
        endpoint=rapidoc_ui,
        methods=["GET"],
        include_in_schema=False,
    )

    # Support both /docs and /docs/ URLs.
    if normalized_docs_path != "/":
        router.add_api_route(
            path=f"{normalized_docs_path}/",
            endpoint=rapidoc_ui,
            methods=["GET"],
            include_in_schema=False,
        )

    return router


def mount_rapidoc(
    app: FastAPI,
    *,
    docs_path: str = "/docs",
    openapi_url: str | None = None,
    title: str = "API Documentation",
    rapidoc_js_url: str = RAPIDOC_JS_CDN,
    favicon_url: str = DEFAULT_FAVICON,
) -> None:
    """Attach a RapiDoc route to an existing FastAPI app."""
    resolved_openapi_url = openapi_url or app.openapi_url or "/openapi.json"

    app.include_router(
        create_rapidoc_router(
            docs_path=docs_path,
            openapi_url=resolved_openapi_url,
            title=title,
            rapidoc_js_url=rapidoc_js_url,
            favicon_url=favicon_url,
        )
    )
