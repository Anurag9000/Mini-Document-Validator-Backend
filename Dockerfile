# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE.txt ./
COPY src ./src

RUN pip install --upgrade pip \
    && pip install --prefix=/install .


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY --from=builder /install /usr/local
WORKDIR /app
# Source is already in /usr/local/lib/python3.11/site-packages if installed as package,
# but for FastAPI 'app.main:app' to work easily, we can keep one source of truth.
COPY src ./src

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
