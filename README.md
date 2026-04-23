# System Metrics Service

A lightweight FastAPI service that queries Prometheus and exposes various metrics and usage endpoints for easy consumption by dashboards or other services.

## Features

- Exposes metrics and aggregated usage values (CPU, GPU, NPU, Disk, Memory)
- Queries observability backends (Prometheus, Telegraf) and integrates with OpenTelemetry (OTel)
- Optional NVIDIA GPU support via `docker-compose.nvidia.yml`

## Prerequisites

- Python 3.12+
- Docker and docker-compose

## Quickstart - Docker

### 1. Get the image:

Build the image:

```bash
docker build -t system-metrics-service:latest .
```

...or pull it:

```bash
docker pull ghcr.io/ksavav/system-metrics-service:latest
```


### 2. Start the full stack (Prometheus, OpenTelemetry collector, Telegraf, service).

Note: the service's endpoints query Prometheus/Telegraf/OTel for metrics — for a local deployment the other containers must be running for meaningful responses.

```bash
docker-compose up -d --build
```

### 3. For systems with NVIDIA GPUs, use the NVIDIA compose overrides:

```bash
docker-compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d --build
```

## Quickstart - Local

### 1. Sync dependencies and install using `uv`. If you don't have `uv` installed, follow the official installation instructions:

>https://astral.sh/uv

Then install project dependencies and lockfile:

```bash
uv sync --locked
```

### 2. Run the app with `uv`:

```bash
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000`.

## Configuration

Environment variables are loaded from `.env` by default. See the example `.env` in the repository for defaults. Important variables:

- `PROMETHEUS_URL` — URL of the Prometheus server (default: `http://localhost:9090`)
- `PROMETHEUS_PORT` — Prometheus port (default: `9090`)
- `SYSTEM_METRICS_SERVICE_PORT` — Service port (default: `8000`)
- `OTEL_COLLECTOR_PORT` / `OTEL_COLLECTOR_API_PORT` — OpenTelemetry collector ports

## API Endpoints

Metric and usage endpoints are registered under `/api`:

- `GET /api/metrics/cpu` — Prometheus CPU metrics
- `GET /api/usage/cpu` — Aggregated CPU usage
- `GET /api/metrics/gpu/utilization` — GPU utilization metrics
- `GET /api/metrics/gpu/temperature` — GPU temperature metrics
- `GET /api/metrics/gpu/memory` — Per-GPU memory metrics
- `GET /usage/gpu` — Aggregated GPU usage
- `GET /api/usage/gpu/memory` — Aggregated GPU memory usage
- `GET /api/metrics/gpu/memory` — Per-GPU memory metrics
- `GET /api/usage/gpu` — Aggregated GPU usage
- `GET /api/usage/gpu/memory` — Aggregated GPU memory usage

## Troubleshooting

- If metrics return empty, verify `PROMETHEUS_URL` and that Prometheus is scraping the exporter/targets used for metrics.
- For GPU metrics, ensure system exporters (nvidia-smi or device exporters) are present and Prometheus scrapes them. Use the NVIDIA compose file to expose required devices into containers.
 - For local deployments, ensure Prometheus, Telegraf and the OpenTelemetry collector containers are up - the service depends on those to provide metrics.
