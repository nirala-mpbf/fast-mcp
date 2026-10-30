# Brain FastMCP OpenAPI adapter

Automatically convert the Spring Boot Brain Service OpenAPI 3.x operations to MCP tools using standalone `fastmcp`.

## Requirements
- Python 3.12+
- `uv` (https://docs.astral.sh/uv/)
- Brain Service serving OpenAPI JSON at `/v3/api-docs`

## Local setup

```bash
cp .env.example .env
# Edit .env: set BRAIN_OPENAPI_URL and BRAIN_API_BASE_URL
uv sync
uv run uvicorn brain_fastmcp.server:app --host 0.0.0.0 --port 8000
```

MCP endpoint: `http://localhost:8000/mcp`. The endpoint uses MCP Streamable HTTP; it is not a conventional REST endpoint.

## Docker

```bash
docker build -t brain-fastmcp .
docker run --rm --env-file .env -p 8000:8000 brain-fastmcp
```

When Brain runs on your host and FastMCP runs in Docker, use `host.docker.internal` where supported (on Linux add `--add-host=host.docker.internal:host-gateway`). When both are in the same Docker Compose network, use the Brain service name, e.g. `http://brain-service:8080`.

## Inspect tools

```bash
uv run python -c 'import asyncio; from fastmcp import Client; async_code = "async def main():\n async with Client(\"http://localhost:8000/mcp\") as c:\n  print([t.name for t in await c.list_tools()])"; exec(async_code); asyncio.run(main())'
```

Connect Agent Gateway to `http://brain-fastmcp:8000/mcp` on the shared Docker network, using Streamable HTTP.

## Design notes
- Tool definitions are loaded **at startup**. Restart after changing the Brain Swagger document. Hot reload requires an additional refresh mechanism.
- Set stable unique `operationId` and helpful `summary`/`description` values on Spring Boot operations.
- The adapter supports the OpenAPI shapes that FastMCP supports; validate multipart uploads and complex schemas separately.
- Only expose an explicit allowlist of business-safe operations to the LLM. Protect MCP access and Brain APIs with appropriate authentication and authorization; do not share a privileged bearer token across users.
- Set trusted, static Brain URLs; this service is not intended to fetch arbitrary user-provided URLs.
- Pin resolved dependency versions (`uv.lock`) and scan images before production deployment.
