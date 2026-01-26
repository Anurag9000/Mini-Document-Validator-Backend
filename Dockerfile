# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE.txt ./
COPY src ./src

RUN pip install --upgrade pip \
    && pip install --prefix=/install . || (echo "Failed to install dependencies" && exit 1)


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Add metadata labels
LABEL maintainer="Genoshi Contributors" \
    version="0.1.0" \
    description="FastAPI service for insurance document validation"

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

COPY --from=builder /install /usr/local
# Copy source again to ensure 'app.main:app' import works correctly.
# While the package is installed in site-packages, having source in /app/src
# provides a consistent PYTHONPATH and makes debugging easier.
COPY --chown=appuser:appuser src ./src

# Switch to non-root user
USER appuser

EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
