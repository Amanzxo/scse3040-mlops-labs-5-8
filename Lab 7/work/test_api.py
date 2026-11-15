from fastapi.testclient import TestClient
from app import app

client = TestClient(app)
GOOD = {"distance_km": 5.0, "prep_time_min": 20, "traffic_level": 2, "rain": 0}

def test_health_and_openapi():
    assert client.get('/health').json() == {'status': 'ok', 'model_loaded': True}
    assert '/predict' in client.get('/openapi.json').json()['paths']

def test_prediction_and_rain_behavior():
    dry = client.post('/predict', json=GOOD)
    wet = client.post('/predict', json={**GOOD, 'rain': 1})
    assert dry.status_code == wet.status_code == 200
    assert 20 < dry.json()['delivery_min'] < 70
    assert wet.json()['delivery_min'] > dry.json()['delivery_min']

def test_bad_inputs_are_rejected():
    for update in [{'distance_km': -1}, {'traffic_level': 9}, {'rain': 2}, {'prep_time_min': -1}]:
        assert client.post('/predict', json={**GOOD, **update}).status_code == 422
    assert client.post('/predict', json={'distance_km': 5}).status_code == 422
