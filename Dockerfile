FROM python:3.13-slim-trixie


RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

COPY uv.lock pyproject.toml  ./

RUN uv pip install . --system \
    && rm -rf /bin/uv/


COPY . ./


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_HOST=${DB_HOST} \
    DB_USER=${DB_USER} \
    DB_PORT=${DB_PORT} \
    DB_PASSWORD=${DB_PASSWORD} \
    DB_DATABASE=${DB_DATABASE} \
    FIREBASE_SERVICE_ACCOUNT_JSON=${FIREBASE_SERVICE_ACCOUNT_JSON} \
    FILE_SERVER_UPLOAD_URL=${FILE_SERVER_UPLOAD_URL} \
    FILE_SERVER_SECRET=${FILE_SERVER_SECRET}



RUN adduser --disabled-password --gecos '' app \
    && chown -R app:app /app
USER app

EXPOSE 8080

RUN chmod +x ./entrypoint.sh

CMD ["./entrypoint.sh"]