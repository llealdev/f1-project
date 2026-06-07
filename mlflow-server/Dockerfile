FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir mlflow==2.22.2 scikit-learn==1.5.2 cloudpickle feature-engine

COPY bootstrap.py /app/bootstrap.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV MLFLOW_BACKEND_STORE_URI=sqlite:////app/mlflow/mlflow.db
ENV MLFLOW_DEFAULT_ARTIFACT_ROOT=/app/mlflow/mlartifacts
ENV MLFLOW_URI=http://localhost:5000
ENV MODEL_ARTIFACT_DIR=/app/mlflow/mlartifacts/1/models

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=10 \
  CMD curl -fsS http://localhost:5000/ || exit 1

CMD ["/app/entrypoint.sh"]
