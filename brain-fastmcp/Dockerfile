FROM python:3.12-slim
ENV UV_HTTP_TIMEOUT=300
ENV UV_HTTP_RETRIES=10
ENV PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN uv sync --no-dev
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "brain_fastmcp.server:app", "--host", "0.0.0.0", "--port", "8082"]
