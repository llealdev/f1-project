
from http import HTTPStatus
from fastapi import FastAPI, HTTPException
import mlflow 
import pandas as pd
import os 
import dotenv # Adicione o import

dotenv.load_dotenv() 

MLFLOW_URI = os.getenv("MLFLOW_URI")
mlflow.set_tracking_uri(MLFLOW_URI)

models = mlflow.search_registered_models(filter_string="name='f1_driver_champion'")
latest = max([i.version for i in models[0].latest_versions])
MODEL = mlflow.sklearn.load_model(f"models:/f1_driver_champion/{latest}")

app = FastAPI()

@app.get("/health_check")
async def health_check():
    return {"message": "Ok"}

@app.post("/predict/")
async def predict(data: dict): 
    
    if len(data) == 0:
        raise HTTPException(
            status_code=HTTPException.NOT_FOUND,
            detail="No features provided"
        ) 

    df = pd.DataFrame(data["data"]) 
    X = df[MODEL.feature_names_in_]

    proba = MODEL.predict_proba(X)[:, 1]

    payload_df = pd.DataFrame({
        "id": df["id"],
        "proba": proba
    })

    payload = payload_df.to_dict(orient='records')

    return {"predictions": payload}
