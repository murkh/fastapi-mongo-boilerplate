# File Explorer Backend

## Overview

This project is a backend service for a file explorer web application, designed to provide seamless access to both cloud (AWS S3) and local storage providers. It is built using **FastAPI** for high performance and easy API development, and includes monitoring with **Prometheus** and **Grafana**.

## Features

- **Unified API**: Access and manage files on AWS S3 or local storage through a single RESTful API.
- **Directory Listing**: List files and directories for both AWS S3 and local storage.
- **File Download**: Download files from either storage provider.
- **Directory Tree**: Recursively fetch a nested directory structure up to a configurable depth.
- **Error Handling**: Consistent and descriptive error responses for invalid requests or server errors.
- **Observability**: Integrated Prometheus metrics and Grafana dashboards for monitoring.
- **Dockerized**: Easily run the backend and monitoring stack using Docker Compose.
- **Kubernetes Ready**: Includes a Helm chart for easy deployment to Kubernetes clusters.

## Project Structure

```
├── src/
│   └── app/
│       ├── api/           # API routers (v1, AWS, local)
│       ├── core/          # Core config, exceptions, setup
│       ├── services/      # Storage service implementations
│       └── main.py        # FastAPI app entrypoint
├── grafana_data/          # Grafana persistent data
├── prometheus_data/       # Prometheus config/data
├── helm/                  # Helm chart for Kubernetes
├── Dockerfile             # Docker build for backend
├── docker-compose.yml     # Multi-service orchestration
├── pyproject.toml         # Python dependencies
├── uv.lock                # Dependency lock file
├── .env-example           # Example environment variables
└── README.md              # Project documentation
```

## API Endpoints

### Local Storage
- `GET /api/v1/local/list?path=...` — List files/directories at a path
- `GET /api/v1/local/download?path=...` — Download a file
- `GET /api/v1/local/tree?path=...&max_depth=5` — Get nested directory tree

### AWS S3
- `GET /api/v1/aws/list?prefix=...` — List S3 objects at a prefix
- `GET /api/v1/aws/download?path=...` — Download a file from S3
- `GET /api/v1/aws/tree?prefix=...&max_depth=5` — Get nested S3 object tree

## Configuration

Copy `.env-example` to `.env` and fill in the required values:

```
ENVIRONMENT=local
APP_NAME=File Explorer API
APP_DESCRIPTION=Backend for file explorer
APP_VERSION=1.0
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=your-bucket
LOCAL_STORAGE_PATH=/tmp
```

## Running Locally

### Prerequisites
- Docker & Docker Compose

### Start the stack

```sh
docker-compose up --build
```

The FastAPI backend will be available at [http://localhost:8002/docs](http://localhost:8002/docs) (Swagger UI).

Prometheus: [http://localhost:9090](http://localhost:9090)

Grafana: [http://localhost:3000](http://localhost:3000)

## Kubernetes Deployment

Use the Helm chart in `helm/fastapi-chart` to deploy to a Kubernetes cluster:

```sh
cd helm/fastapi-chart
helm install file-explorer-backend .
```

Edit `values.yaml` to configure image, service, and ingress settings as needed.

## Development

### Python Environment
This project uses Python 3.12. Dependencies are managed with [uv](https://github.com/astral-sh/uv):

```sh
uv sync
```

### Debugging
VS Code launch configuration is provided for debugging with FastAPI and Uvicorn.

## Monitoring

- **Prometheus** scrapes metrics from the FastAPI app.
- **Grafana** provides dashboards for metrics visualization.

## License

MIT License. See individual plugin folders for their respective licenses.

---

**Author:** Gaurav Panchal
