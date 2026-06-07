from http import HTTPStatus
from typing import Optional

import dotenv
import mlflow
import pandas as pd
import sqlalchemy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

dotenv.load_dotenv()

MLFLOW_URI = "http://mlflow:5000"

import os
if os.getenv("MLFLOW_URI"):
    MLFLOW_URI = os.getenv("MLFLOW_URI")

mlflow.set_tracking_uri(MLFLOW_URI)

DB_FETURE_STORE = os.getenv(
    "DB_FETURE_STORE",
    "postgresql+psycopg://admin:minhasenha@meu_postgres:5432/feature_stores",
)
engine = sqlalchemy.create_engine(DB_FETURE_STORE, pool_pre_ping=True)


def _load_model():
    """Load the latest version of the f1_driver_champion model from MLflow.

    Uses a two-step approach to avoid path resolution bugs in some mlflow versions:
      1) Find the latest version via the registry
      2) Resolve the model artifact to a local directory and load it from there
    """
    try:
        client = mlflow.tracking.MlflowClient()
        try:
            versions = client.get_latest_versions("f1_driver_champion", stages=["None"])
        except Exception:
            versions = client.search_model_versions("name='f1_driver_champion'")
        if not versions:
            raise RuntimeError("No registered model 'f1_driver_champion' found in MLflow")

        latest = max(int(v.version) for v in versions)
        print(f"[INFO] Loading f1_driver_champion version {latest}")
        model_uri = f"models:/f1_driver_champion/{latest}"

        try:
            return mlflow.sklearn.load_model(model_uri)
        except Exception as e_uri:
            print(f"[WARN] models:/ load failed ({e_uri}); falling back to artifact download")
            local_dir = mlflow.artifacts.download_artifacts(model_uri)
            return mlflow.sklearn.load_model(local_dir)
    except Exception as e:
        print(f"[WARN] Could not load champion model from MLflow: {e}")
        return None


MODEL = _load_model()
MODEL_FEATURES = list(MODEL.feature_names_in_) if MODEL is not None else []


def _format_driver_name(driverid: str) -> str:
    if not driverid:
        return ""
    cleaned = driverid.replace("_", " ").strip()
    return " ".join(part.capitalize() for part in cleaned.split())


app = FastAPI(title="F1 Smart Predict API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health_check")
async def health_check():
    return {
        "status": "ok",
        "model_loaded": MODEL is not None,
        "mlflow_uri": MLFLOW_URI,
    }


@app.get("/drivers")
async def list_drivers(year: Optional[int] = None):
    """Lista os pilotos com dados na feature store. Filtra por ano se enviado."""
    try:
        if year is not None:
            query = f"""
                SELECT DISTINCT driverid
                FROM fs_f1_all
                WHERE EXTRACT(YEAR FROM TO_DATE(dt_ref, 'YYYY-MM-DD')) = {int(year)}
                ORDER BY driverid
            """
        else:
            query = "SELECT DISTINCT driverid FROM fs_f1_all ORDER BY driverid"
        df = pd.read_sql(query, engine)
        drivers = [
            {"driverid": row["driverid"], "fullname": _format_driver_name(row["driverid"])}
            for _, row in df.iterrows()
        ]
        return {"drivers": drivers, "count": len(drivers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


@app.get("/years")
async def list_years():
    """Lista os anos disponíveis na feature store."""
    try:
        query = """
            SELECT DISTINCT EXTRACT(YEAR FROM TO_DATE(dt_ref, 'YYYY-MM-DD'))::int AS year
            FROM fs_f1_all
            ORDER BY year DESC
        """
        df = pd.read_sql(query, engine)
        return {"years": [int(y) for y in df["year"].tolist()]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


@app.get("/drivers/{driver_id}/history")
async def driver_history(driver_id: str):
    """Retorna o histórico de um piloto na feature store (todas as datas)."""
    try:
        safe_id = driver_id.replace("'", "")
        query = f"""
            SELECT *
            FROM fs_f1_all
            WHERE driverid = '{safe_id}'
            ORDER BY TO_DATE(dt_ref, 'YYYY-MM-DD') ASC
        """
        df = pd.read_sql(query, engine)
        if df.empty:
            return {"driverid": driver_id, "rows": [], "count": 0}

        df["dt_ref_dt"] = pd.to_datetime(df["dt_ref"], errors="coerce")
        df["year"] = df["dt_ref_dt"].dt.year
        records = df.where(pd.notnull(df), None).to_dict(orient="records")
        for r in records:
            if r.get("dt_ref_dt") is not None:
                r["dt_ref_dt"] = r["dt_ref_dt"].isoformat()
            else:
                r.pop("dt_ref_dt", None)
        return {
            "driverid": driver_id,
            "fullname": _format_driver_name(driver_id),
            "rows": records,
            "count": len(records),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


@app.get("/top-predictions")
async def top_predictions(year: Optional[int] = None, top_k: int = 5):
    """
    Carrega o snapshot mais recente de cada piloto da feature store,
    roda o modelo e retorna os top_k pilotos com maior probabilidade
    de serem campeões.
    """
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Check MLflow and model registry.")

    try:
        if year is None:
            latest_date_query = "SELECT MAX(TO_DATE(dt_ref, 'YYYY-MM-DD')) AS max_dt FROM fs_f1_all"
            latest = pd.read_sql(latest_date_query, engine)["max_dt"].iloc[0]
            if latest is None or pd.isna(latest):
                raise HTTPException(status_code=404, detail="Feature store is empty")
            latest_str = pd.to_datetime(latest).strftime("%Y-%m-%d")
            base_query = f"SELECT * FROM fs_f1_all WHERE dt_ref = '{latest_str}'"
        else:
            base_query = f"""
                SELECT *
                FROM fs_f1_all
                WHERE EXTRACT(YEAR FROM TO_DATE(dt_ref, 'YYYY-MM-DD')) = {int(year)}
                  AND TO_DATE(dt_ref, 'YYYY-MM-DD') = (
                      SELECT MAX(TO_DATE(dt_ref, 'YYYY-MM-DD'))
                      FROM fs_f1_all AS t
                      WHERE t.driverid = fs_f1_all.driverid
                        AND EXTRACT(YEAR FROM TO_DATE(t.dt_ref, 'YYYY-MM-DD')) = {int(year)}
                  )
            """

        df = pd.read_sql(base_query, engine)
        if df.empty:
            return {"predictions": [], "count": 0}

        missing = [c for c in MODEL_FEATURES if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Feature store is missing required columns: {missing[:5]}...",
            )

        X = df[MODEL_FEATURES]
        proba = MODEL.predict_proba(X)[:, 1]
        df["prob_win"] = proba
        df = df.sort_values("prob_win", ascending=False).head(int(top_k))
        df["fullname"] = df["driverid"].apply(_format_driver_name)

        result = [
            {
                "driverid": r["driverid"],
                "fullname": r["fullname"],
                "dt_ref": r["dt_ref"],
                "prob_win": float(r["prob_win"]),
            }
            for _, r in df.iterrows()
        ]
        return {"predictions": result, "count": len(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/predict/")
async def predict(payload: dict):
    """
    Recebe um payload no formato:
    {
      "values": [
         {"id": "2025-12-07_max_verstappen", "driverid": "max_verstappen", ...features...},
         ...
      ]
    }
    Retorna probabilidades de vitória por id.
    """
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    data = payload.get("values", [])
    if len(data) == 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No features provided",
        )

    try:
        df = pd.DataFrame(data)
        X = df[MODEL_FEATURES]
        proba = MODEL.predict_proba(X)
        df_proba = pd.DataFrame(proba, columns=MODEL.classes_, index=df["id"].values)
        final_payload = df_proba.to_dict(orient="index")
        return {"predictions": final_payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
