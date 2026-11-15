"""Serve the registered MLflow model through its native scoring application.

Use when a Windows installation cannot launch the uvicorn console entry point.
This uses the same scoring application as `mlflow models serve`.
"""
import json
import os
from pathlib import Path

import mlflow
import uvicorn
from mlflow.pyfunc.scoring_server import init

HERE = Path(__file__).resolve().parent
selection = json.loads((HERE.parent / 'Lab 6/work/selection.json').read_text(encoding='utf-8'))
mlflow.set_tracking_uri(selection.get('tracking_uri', 'sqlite:///' + (HERE.parent / 'Lab 6/work/mlflow.db').as_posix()))
uri = f"models:/{selection['registered_model']}/{selection['version']}"
print(f'Loading {uri}; serving MLflow /invocations on port 5001', flush=True)
app = init(mlflow.pyfunc.load_model(uri))
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5001)
