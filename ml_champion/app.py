
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
async def predict(payload: dict): 

    data = payload.get('values', [])
    
    if len(data) == 0:
        raise HTTPException(
            status_code=HTTPException.NOT_FOUND,
            detail="No features provided"
        ) 

    df = pd.DataFrame(data) 
    X = df[MODEL.feature_names_in_]

    df_proba = pd.DataFrame(MODEL.predict_proba(X), columns=MODEL.classes_)
    df_proba['id'] = df['id'].copy()

    df_proba.set_index('id', inplace=True)

    final_payload = df_proba.to_dict(orient='index')

    return {"predictions": final_payload}
