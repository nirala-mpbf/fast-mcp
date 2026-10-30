# """Convert a trusted Brain Service OpenAPI document to MCP tools."""
# import os
# from urllib.parse import urlsplit
#
# import httpx2
# from dotenv import load_dotenv
# from fastmcp import FastMCP
#
# load_dotenv()
#
# OPENAPI_URL = os.environ["BRAIN_OPENAPI_URL"]
# API_BASE_URL = os.environ["BRAIN_API_BASE_URL"]
# API_TOKEN = os.getenv("BRAIN_API_TOKEN", "")
#
#
# def require_http_url(value: str) -> None:
#     parsed = urlsplit(value)
#     if parsed.scheme not in ("http", "https") or not parsed.hostname:
#         raise ValueError("Expected an absolute HTTP(S) URL")
#
#
# require_http_url(OPENAPI_URL)
# require_http_url(API_BASE_URL)
# headers = {"Authorization": f"Bearer {API_TOKEN}"} if API_TOKEN else {}
#
# # Only configure trusted internal URLs. Do not allow arbitrary user-supplied URLs.
# with httpx2.Client(timeout=15.0, follow_redirects=False, headers=headers) as spec_client:
#     response = spec_client.get(OPENAPI_URL)
#     response.raise_for_status()
#     spec = response.json()
#
# if not str(spec.get("openapi", "")).startswith("3."):
#     raise ValueError("Brain must expose an OpenAPI 3.x document")
#
# api_client = httpx2.AsyncClient(
#     base_url=API_BASE_URL.rstrip("/") + "/",
#     headers=headers,
#     timeout=30.0,
#     follow_redirects=False,
# )
#
# mcp = FastMCP.from_openapi(
#     openapi_spec=spec,
#     client=api_client,
#     name="brain-tools",
# )
#
# # Uvicorn imports this ASGI application. Its lifespan manages MCP sessions.
# app = mcp.http_app(path="/mcp", transport="streamable-http")


#
# import os
# from typing import Literal
# from urllib.parse import urlsplit
# from uuid import uuid4
#
# import httpx2
# from dotenv import load_dotenv
# from fastmcp import FastMCP
#
# load_dotenv()
#
# API_BASE_URL = os.environ["BRAIN_API_BASE_URL"].rstrip("/")
# API_TOKEN = os.getenv("BRAIN_API_TOKEN", "")
#
#
# def require_http_url(value: str) -> None:
#     parsed = urlsplit(value)
#     if parsed.scheme not in ("http", "https") or not parsed.hostname:
#         raise ValueError("Expected an absolute HTTP(S) URL")
#
#
# require_http_url(API_BASE_URL)
#
# headers = (
#     {"Authorization": f"Bearer {API_TOKEN}"}
#     if API_TOKEN
#     else {}
# )
#
# api_client = httpx2.AsyncClient(
#     base_url=API_BASE_URL + "/",
#     headers=headers,
#     timeout=30.0,
#     follow_redirects=False,
# )
#
# mcp = FastMCP("brain-tools")
#
#
# @mcp.tool(
#     name="processWorkflowCommand",
#     description=(
#         "Execute an onboarding workflow command against the Brain service. "
#         "Use GET_STATE to read existing onboarding status. "
#         "Use CREATE only when a new workflow must be created. "
#         "Use SUBMIT_EVENT only after the relevant business operation succeeds. "
#         "Always use the referenceId supplied by trusted application context. "
#         "Never invent a referenceId. The requestId and payload are generated "
#         "by this tool."
#     ),
# )
# async def processWorkflowCommand(
#     operation: Literal["CREATE", "GET_STATE", "SUBMIT_EVENT"],
#     referenceId: str,
#     event: str | None = None,
#     workflowKey: str | None = None,
#     idempotencyKey: str | None = None,
# ) -> dict:
#     if not referenceId or not referenceId.strip():
#         raise ValueError("referenceId is required")
#
#     operation = operation.strip()
#
#     metadata = {
#         "operation": operation,
#         "requestId": f"mcp-{uuid4()}",
#         "referenceId": referenceId.strip(),
#     }
#
#     if operation == "GET_STATE":
#         if any(
#             value is not None
#             for value in (event, workflowKey, idempotencyKey)
#         ):
#             raise ValueError(
#                 "GET_STATE does not accept event, workflowKey, "
#                 "or idempotencyKey"
#             )
#
#     elif operation == "CREATE":
#         if event is not None:
#             raise ValueError("CREATE does not accept event")
#
#         if workflowKey:
#             metadata["workflowKey"] = workflowKey
#
#         if idempotencyKey:
#             metadata["idempotencyKey"] = idempotencyKey
#
#     elif operation == "SUBMIT_EVENT":
#         if not event or not event.strip():
#             raise ValueError("event is required for SUBMIT_EVENT")
#
#         if workflowKey is not None:
#             raise ValueError(
#                 "SUBMIT_EVENT does not accept workflowKey"
#             )
#
#         metadata["event"] = event.strip()
#
#         if idempotencyKey:
#             metadata["idempotencyKey"] = idempotencyKey
#
#     request_body = {
#         "metadata": metadata,
#         "payload": {},
#     }
#
#     response = await api_client.post(
#         "api/workflows",
#         json=request_body,
#     )
#
#     response.raise_for_status()
#     return response.json()
#
#
# app = mcp.http_app(
#     path="/mcp",
#     transport="streamable-http",
# )


# """Dynamically expose Brain OpenAPI operations as MCP tools."""
#
# import os
# from urllib.parse import urlsplit
#
# import httpx2
# from dotenv import load_dotenv
# from fastmcp import FastMCP
#
# load_dotenv()
#
# OPENAPI_URL = os.environ["BRAIN_OPENAPI_URL"]
# API_BASE_URL = os.environ["BRAIN_API_BASE_URL"].rstrip("/")
# API_TOKEN = os.getenv("BRAIN_API_TOKEN", "")
#
#
# def require_http_url(value: str) -> None:
#     parsed = urlsplit(value)
#     if parsed.scheme not in ("http", "https") or not parsed.hostname:
#         raise ValueError("Expected an absolute HTTP(S) URL")
#
#
# require_http_url(OPENAPI_URL)
# require_http_url(API_BASE_URL)
#
# headers = (
#     {"Authorization": f"Bearer {API_TOKEN}"}
#     if API_TOKEN
#     else {}
# )
#
# # Fetch the latest OpenAPI document from the Brain service.
# with httpx2.Client(
#     timeout=60.0,
#     follow_redirects=False,
#     headers=headers,
# ) as spec_client:
#     response = spec_client.get(OPENAPI_URL)
#     response.raise_for_status()
#     spec = response.json()
#
# if not str(spec.get("openapi", "")).startswith("3."):
#     raise ValueError("Brain must expose an OpenAPI 3.x document")
#
# # The OpenAPI document defines the available operations and schemas.
# api_client = httpx2.AsyncClient(
#     base_url=API_BASE_URL + "/",
#     headers=headers,
#     timeout=60.0,
#     follow_redirects=False,
# )
#
# mcp = FastMCP.from_openapi(
#     openapi_spec=spec,
#     client=api_client,
#     name="brain-tools",
# )
#
# # MCP endpoint for Agent Gateway / AgentScope.
# app = mcp.http_app(
#     path="/mcp",
#     transport="streamable-http",
# )


# """Dynamically expose Brain OpenAPI operations as MCP tools."""
#
# import logging
# import os
# from urllib.parse import urlsplit
#
# import httpx2
# from dotenv import load_dotenv
# from fastmcp import FastMCP
#
# load_dotenv()
#
# logging.basicConfig(
#     level=os.getenv("LOG_LEVEL", "INFO"),
#     format="%(asctime)s %(levelname)s %(name)s - %(message)s",
# )
# logger = logging.getLogger("brain-mcp")
#
# OPENAPI_URL = os.environ["BRAIN_OPENAPI_URL"].strip()
# API_BASE_URL = os.environ["BRAIN_API_BASE_URL"].strip().rstrip("/")
# API_TOKEN = os.getenv("BRAIN_API_TOKEN", "").strip()
#
#
# def require_http_url(value: str, name: str) -> None:
#     parsed = urlsplit(value)
#
#     if (
#         parsed.scheme not in ("http", "https")
#         or not parsed.hostname
#     ):
#         raise ValueError(
#             f"{name} must be an absolute HTTP(S) URL: {value}"
#         )
#
#
# require_http_url(OPENAPI_URL, "BRAIN_OPENAPI_URL")
# require_http_url(API_BASE_URL, "BRAIN_API_BASE_URL")
#
# headers = (
#     {"Authorization": f"Bearer {API_TOKEN}"}
#     if API_TOKEN
#     else {}
# )
#
#
# # Log outgoing Brain requests without logging credentials or payloads.
# async def log_request(request):
#     logger.info(
#         "BRAIN HTTP REQUEST method=%s url=%s",
#         request.method,
#         request.url,
#     )
#
#
# async def log_response(response):
#     logger.info(
#         "BRAIN HTTP RESPONSE status=%s method=%s url=%s",
#         response.status_code,
#         response.request.method,
#         response.request.url,
#     )
#
#
# async def log_request_error(request):
#     logger.exception(
#         "BRAIN HTTP REQUEST FAILED method=%s url=%s",
#         request.method,
#         request.url,
#     )
#
#
# # 1. Load the live OpenAPI document.
# with httpx2.Client(
#     timeout=30.0,
#     follow_redirects=False,
#     headers=headers,
# ) as spec_client:
#     logger.info("Fetching Brain OpenAPI: %s", OPENAPI_URL)
#
#     response = spec_client.get(OPENAPI_URL)
#     response.raise_for_status()
#     spec = response.json()
#
# if not str(spec.get("openapi", "")).startswith("3."):
#     raise ValueError("Brain must expose an OpenAPI 3.x document")
#
# # Print the operations discovered from the specification.
# operation_count = 0
#
# for path, path_item in spec.get("paths", {}).items():
#     if not isinstance(path_item, dict):
#         continue
#
#     for method, operation in path_item.items():
#         if method.lower() not in {
#             "get", "post", "put", "patch", "delete",
#             "options", "head", "trace",
#         }:
#             continue
#
#         if not isinstance(operation, dict):
#             continue
#
#         operation_count += 1
#
#         logger.info(
#             "OPENAPI OPERATION method=%s path=%s operationId=%s",
#             method.upper(),
#             path,
#             operation.get("operationId", "<generated>"),
#         )
#
# if operation_count == 0:
#     raise ValueError(
#         "No HTTP operations found in the Brain OpenAPI document"
#     )
#
# logger.info(
#     "Loaded OpenAPI version=%s operations=%d",
#     spec["openapi"],
#     operation_count,
# )
#
# # 2. Configure the HTTP client used by generated MCP tools.
# #
# # BRAIN_API_BASE_URL must be the API origin/base matching the
# # paths in the OpenAPI document. For example, if the spec declares
# # /api/workflows, use http://brain-service:8081 as the base URL.
# api_client = httpx2.AsyncClient(
#     base_url=API_BASE_URL + "/",
#     headers=headers,
#     timeout=60.0,
#     follow_redirects=False,
#     event_hooks={
#         "request": [log_request],
#         "response": [log_response],
#     },
# )
#
# # 3. Dynamically create tools from the OpenAPI document.
# mcp = FastMCP.from_openapi(
#     openapi_spec=spec,
#     client=api_client,
#     name="brain-tools",
# )
#
# logger.info("Brain OpenAPI operations registered dynamically")
#
# # 4. Expose the MCP endpoint for Agent Gateway.
# app = mcp.http_app(
#     path="/mcp",
#     transport="streamable-http",
# )


"""Dynamically expose Brain OpenAPI operations as MCP tools."""

import json
import logging
import os
import uuid
from urllib.parse import urlsplit

import httpx2
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger("brain-mcp")

OPENAPI_URL = os.environ["BRAIN_OPENAPI_URL"].strip()
API_BASE_URL = os.environ["BRAIN_API_BASE_URL"].strip().rstrip("/")
API_TOKEN = os.getenv("BRAIN_API_TOKEN", "").strip()

# Testing only. In production, resolve this from authenticated
# application/user context rather than a global reference ID.
TRUSTED_REFERENCE_ID = os.getenv("TRUSTED_REFERENCE_ID", "").strip()


def require_http_url(value: str, name: str) -> None:
    parsed = urlsplit(value)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError(
            f"{name} must be an absolute HTTP(S) URL: {value}"
        )


require_http_url(OPENAPI_URL, "BRAIN_OPENAPI_URL")
require_http_url(API_BASE_URL, "BRAIN_API_BASE_URL")

headers = (
    {"Authorization": f"Bearer {API_TOKEN}"}
    if API_TOKEN
    else {}
)


def rewrite_get_state_body(body):
    """Rewrite trusted fields for GET_STATE only.

    Supports:
        {"metadata": {...}, "payload": {}}

    and:
        {"body": {"metadata": {...}, "payload": {}}}
    """
    if not isinstance(body, dict):
        return body, False

    command = body.get("body", body)

    if not isinstance(command, dict):
        return body, False

    metadata = command.get("metadata")

    if not isinstance(metadata, dict):
        return body, False

    operation = str(metadata.get("operation", "")).upper()

    if operation != "GET_STATE":
        return body, False

    if not TRUSTED_REFERENCE_ID:
        raise RuntimeError(
            "TRUSTED_REFERENCE_ID must be configured for GET_STATE"
        )

    # Never trust the LLM-supplied IDs for GET_STATE.
    metadata["referenceId"] = TRUSTED_REFERENCE_ID
    metadata["requestId"] = str(uuid.uuid4())

    # GET_STATE requires an empty payload.
    command["payload"] = {}

    return body, True


class BrainRequestRewriteTransport(httpx2.AsyncBaseTransport):
    """Rewrite GET_STATE requests before sending them to Brain."""

    def __init__(self):
        self._transport = httpx2.AsyncHTTPTransport()

    async def handle_async_request(self, request):
        if request.method.upper() != "POST":
            return await self._transport.handle_async_request(request)

        content_type = request.headers.get("content-type", "")

        if "application/json" not in content_type.lower():
            return await self._transport.handle_async_request(request)

        try:
            original_body = await request.aread()
            parsed_body = json.loads(original_body)
        except (ValueError, UnicodeDecodeError):
            # Leave non-JSON requests unchanged.
            return await self._transport.handle_async_request(request)

        rewritten_body, changed = rewrite_get_state_body(parsed_body)

        if not changed:
            return await self._transport.handle_async_request(request)

        content = json.dumps(rewritten_body).encode("utf-8")

        # Build a fresh request with the rewritten body.
        rewritten_request = httpx2.Request(
            method=request.method,
            url=request.url,
            headers=request.headers,
            content=content,
            extensions=request.extensions,
        )

        rewritten_request.headers["content-length"] = str(len(content))

        logger.info(
            "Rewrote GET_STATE request using trusted referenceId=%s",
            TRUSTED_REFERENCE_ID,
        )

        return await self._transport.handle_async_request(
            rewritten_request
        )

    async def aclose(self):
        await self._transport.aclose()


async def log_request(request):
    logger.info(
        "BRAIN HTTP REQUEST method=%s url=%s",
        request.method,
        request.url,
    )


async def log_response(response):
    logger.info(
        "BRAIN HTTP RESPONSE status=%s method=%s url=%s",
        response.status_code,
        response.request.method,
        response.request.url,
    )


async def log_request_error(request):
    logger.error(
        "BRAIN HTTP REQUEST FAILED method=%s url=%s",
        request.method,
        request.url,
    )


# 1. Fetch the live Brain OpenAPI specification.
with httpx2.Client(
    timeout=30.0,
    follow_redirects=False,
    headers=headers,
) as spec_client:
    logger.info("Fetching Brain OpenAPI: %s", OPENAPI_URL)

    response = spec_client.get(OPENAPI_URL)
    response.raise_for_status()
    spec = response.json()

if not str(spec.get("openapi", "")).startswith("3."):
    raise ValueError("Brain must expose an OpenAPI 3.x document")


# 2. Log the HTTP operations discovered in OpenAPI.
operation_count = 0

for path, path_item in spec.get("paths", {}).items():
    if not isinstance(path_item, dict):
        continue

    for method, operation in path_item.items():
        if method.lower() not in {
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "options",
            "head",
            "trace",
        }:
            continue

        if not isinstance(operation, dict):
            continue

        operation_count += 1

        logger.info(
            "OPENAPI OPERATION method=%s path=%s operationId=%s",
            method.upper(),
            path,
            operation.get("operationId", "<generated>"),
        )

if operation_count == 0:
    raise ValueError(
        "No HTTP operations found in the Brain OpenAPI document"
    )

logger.info(
    "Loaded OpenAPI version=%s operations=%d",
    spec["openapi"],
    operation_count,
)


# 3. Create the HTTP client used by generated MCP tools.
# The custom transport enforces the GET_STATE request fields.
api_client = httpx2.AsyncClient(
    base_url=API_BASE_URL + "/",
    headers=headers,
    timeout=60.0,
    follow_redirects=False,
    transport=BrainRequestRewriteTransport(),
    event_hooks={
        "request": [log_request],
        "response": [log_response],
    },
)


# 4. Dynamically expose Brain OpenAPI operations as MCP tools.
mcp = FastMCP.from_openapi(
    openapi_spec=spec,
    client=api_client,
    name="brain-tools",
)

logger.info(
    "Brain OpenAPI operations registered dynamically; "
    "trusted GET_STATE reference configured=%s",
    bool(TRUSTED_REFERENCE_ID),
)


# 5. Expose the MCP endpoint for Agent Gateway.
app = mcp.http_app(
    path="/mcp",
    transport="streamable-http",
)

