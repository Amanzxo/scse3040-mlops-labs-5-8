# Public FastAPI deployment

This service deploys Lab 8's trained linear regression model. `model.json`
stores the original model's coefficients and intercept without rounding.
The API input schema, validation, response rounding, and version are unchanged.
All 600 dataset rows were checked against `model.joblib` before deployment.
The notebook and Docker exercise retain the original scikit-learn implementation.

Vercel root directory: `cloud/vercel`. Framework preset: FastAPI.
Endpoints: `/health`, `/docs`, `/predict`.
