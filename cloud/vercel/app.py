"""FastAPI deployment of the trained linear delivery-time model.

The coefficients are exported without rounding from Lab 8's model.joblib.
This keeps the cloud inference package small while preserving its predictions.
"""
import json
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel, Field

model = json.loads((Path(__file__).parent / 'model.json').read_text())
FEATURES = model['features']
app = FastAPI(title='Delivery Time Predictor', version='1.0.0')

class Order(BaseModel):
    distance_km: float = Field(..., gt=0, le=50)
    prep_time_min: int = Field(..., ge=0, le=120)
    traffic_level: int = Field(..., ge=1, le=3)
    rain: int = Field(..., ge=0, le=1)

@app.get('/health')
def health():
    return {'status': 'ok', 'model_loaded': True}

@app.post('/predict')
def predict(order: Order):
    row = order.model_dump()
    value = model['intercept'] + sum(weight * row[feature] for weight, feature in zip(model['coefficients'], FEATURES))
    return {'delivery_min': round(float(value), 1), 'model_version': app.version}
