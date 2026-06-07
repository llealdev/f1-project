#!/usr/bin/env python3
"""
Bootstrap script: registers the champion F1 model in MLflow
from a local artifact directory (model.pkl + MLmodel) if no
registered model is found yet.
"""
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import mlflow
import mlflow.sklearn

MLFLOW_URI = os.getenv("MLFLOW_URI", "http://mlflow:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "f1_driver_champion")
SOURCE_DIR = Path(os.getenv("MODEL_ARTIFACT_DIR", "/app/mlflow/mlartifacts/1/models"))


def find_latest_model_artifact() -> Path:
    """Find the most recent model artifact.

    Supports both layouts:
      models/<m-id>/model.pkl               (older mlflow)
      models/<m-id>/artifacts/model.pkl     (newer mlflow)
    """
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"Model source dir not found: {SOURCE_DIR}")

    candidates = sorted(
        [p for p in SOURCE_DIR.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"No model artifacts found in {SOURCE_DIR}")

    for c in candidates:
        if (c / "model.pkl").exists():
            return c
        nested = c / "artifacts"
        if nested.is_dir() and (nested / "model.pkl").exists():
            return nested
    raise FileNotFoundError(f"No model.pkl found under {SOURCE_DIR}")


def wait_for_mlflow(max_wait_s: int = 120):
    import urllib.request
    import urllib.error

    deadline = time.time() + max_wait_s
    last_err = None
    while time.time() < deadline:
        try:
            urllib.request.urlopen(MLFLOW_URI, timeout=3)
            print(f"[bootstrap] MLflow is reachable at {MLFLOW_URI}")
            return
        except Exception as e:
            last_err = e
            time.sleep(2)
    raise RuntimeError(f"MLflow not reachable after {max_wait_s}s: {last_err}")


def main():
    print(f"[bootstrap] Connecting to MLflow at {MLFLOW_URI}")
    mlflow.set_tracking_uri(MLFLOW_URI)
    wait_for_mlflow()

    try:
        existing = mlflow.search_registered_models(filter_string=f"name='{MODEL_NAME}'")
        if existing:
            print(f"[bootstrap] Model '{MODEL_NAME}' already registered; skipping.")
            return
    except Exception as e:
        print(f"[bootstrap] search_registered_models note: {e}")

    latest = find_latest_model_artifact()
    print(f"[bootstrap] Using local model artifact: {latest}")

    pkl_path = latest / "model.pkl"
    if not pkl_path.exists():
        raise FileNotFoundError(f"model.pkl not found in {latest}")
    print(f"[bootstrap] Loading sklearn model from {pkl_path} ...")
    sk_model = mlflow.sklearn.load_model(f"file://{latest.absolute()}")
    print(f"[bootstrap] Model loaded. Class: {type(sk_model).__name__}")

    mlflow.set_experiment("f1_driver_champion_bootstrap")
    with mlflow.start_run(run_name="bootstrap_from_local_artifact") as run:
        mlflow.sklearn.log_model(
            sk_model=sk_model,
            artifact_path="model",
            registered_model_name=MODEL_NAME,
            await_registration_for=60,
        )
        client = mlflow.tracking.MlflowClient()
        versions = client.get_latest_versions(MODEL_NAME, stages=["None", "Production", "Staging"])
        print(f"[bootstrap] Registered versions: {[(v.version, v.current_stage) for v in versions]}")

    print(f"[bootstrap] Done. Model '{MODEL_NAME}' is now registered.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[bootstrap] FAILED: {e}", file=sys.stderr)
        sys.exit(1)
