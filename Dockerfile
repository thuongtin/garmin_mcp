# linux/arm64 image for MikroTik RouterOS containers (RB5009).
# Keep the unpacked image small: RB5009 flash is 1GiB and Oura already lives here.
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    GARMINTOKENS=/data \
    GARMIN_MCP_TRANSPORT=streamable-http \
    GARMIN_MCP_HOST=0.0.0.0 \
    GARMIN_MCP_PORT=8000

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN uv pip install --no-cache -e . \
    && rm -f /usr/local/bin/uv \
    && useradd --system --uid 1001 --create-home garmin \
    && mkdir -p /data \
    && chown garmin:garmin /data \
    && find /usr/local -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod 755 /app/docker-entrypoint.sh

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=4)"

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["garmin-mcp"]
