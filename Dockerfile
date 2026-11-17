FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ELM_STORAGE_DIR=/var/lib/equipment-library

WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends mariadb-client \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock \
    && groupadd --gid 10001 equipment \
    && useradd --uid 10001 --gid equipment --no-create-home equipment \
    && mkdir -p /var/lib/equipment-library \
    && chown equipment:equipment /var/lib/equipment-library

COPY --chown=equipment:equipment app ./app
COPY --chown=equipment:equipment migrations ./migrations
COPY --chown=equipment:equipment alembic.ini ./
USER equipment
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"]
CMD ["sh", "-c", "python -m app.manage upgrade && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
