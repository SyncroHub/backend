FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/backend \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

WORKDIR /app/backend

RUN groupadd --system syncrohub \
    && useradd --system --gid syncrohub --home-dir /app --no-create-home syncrohub

COPY backend/requirements.txt ./
RUN pip install --requirement requirements.txt
RUN chown syncrohub:syncrohub /app/backend


FROM base AS test

COPY backend/requirements-dev.txt ./
RUN pip install --requirement requirements-dev.txt

COPY backend/app ./app
COPY backend/tests ./tests
COPY app-cnsonlineprd /app/app-cnsonlineprd

USER syncrohub

CMD ["pytest", "-q"]


FROM base AS runtime

COPY backend/app ./app
COPY app-cnsonlineprd /app/app-cnsonlineprd

USER syncrohub

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.environ['APP_PORT']}/api/health\", timeout=3)"]

CMD ["sh", "-c", "exec uvicorn app.main:app --host \"${APP_HOST}\" --port \"${APP_PORT}\""]
