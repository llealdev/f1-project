#!/bin/sh
set -e

echo "[entrypoint] Starting MLflow server..."
mlflow server --host 0.0.0.0 --port 5000 \
  --backend-store-uri "$MLFLOW_BACKEND_STORE_URI" \
  --default-artifact-root "$MLFLOW_DEFAULT_ARTIFACT_ROOT" &

MLFLOW_PID=$!

echo "[entrypoint] Waiting for MLflow to be reachable..."
for i in $(seq 1 60); do
  if curl -fsS http://localhost:5000/ >/dev/null 2>&1; then
    echo "[entrypoint] MLflow is up after ${i}s"
    break
  fi
  sleep 1
done

echo "[entrypoint] Running bootstrap (registering model if missing)..."
python /app/bootstrap.py || echo "[entrypoint] Bootstrap warning (continuing)"

echo "[entrypoint] Tailing MLflow process..."
wait $MLFLOW_PID
