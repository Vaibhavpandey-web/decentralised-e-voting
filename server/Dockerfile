FROM python:3.11-slim-bookworm AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential cmake libopenblas-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt gunicorn==23.0.0

FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends libopenblas0 libgomp1 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
WORKDIR /app
COPY app.py gunicorn.conf.py ./
ENV PYTHONUNBUFFERED=1 DATABASE_PATH=/var/data/voters.sqlite3
RUN mkdir -p /var/data
EXPOSE 10000
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
