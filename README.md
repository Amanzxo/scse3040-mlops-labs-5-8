# SCSE3040 MLOps Practicals 05-08

Student: Aman Singh | Roll number: S24CSEU2579 | Batch: 58

Completed and verified: 15 November 2026. Original laboratory attendance dates
were not recorded; the completion date is identified separately in the reports.

Repository: https://github.com/Amanzxo/scse3040-mlops-labs-5-8

Public API: https://aman-delivery-api.vercel.app
Interactive documentation: https://aman-delivery-api.vercel.app/docs
Hosting platform: Vercel Hobby.

## Verified results

All four notebooks were executed from the first cell on a GitHub-hosted Ubuntu
runner using Python 3.12 and a real Docker engine. Self-checks: P05 9/9,
P06 8/8, P07 9/9, P08 9/9. Terminal and MLflow screenshots are actual captures.
The public deployment was independently checked from a separate GitHub runner:
health succeeds, valid input returns HTTP 200, invalid input returns HTTP 422.

Each Lab folder contains its executed notebook, PDF report, and supporting files.
The evidence folder contains execution logs, screenshots, and HTTP results.
The exact observed LMS states are recorded in lms-submissions.json.

## Cloud implementation

The original Lab 8 notebook and Docker service use scikit-learn. The deployed
FastAPI service in cloud/vercel uses the same linear model's full-precision
coefficients to reduce the deployment package size. Predictions were checked on
all 600 dataset rows and match the original model after response rounding.

## Reproducing the labs

Use Python 3.12 and install requirements-lock.txt in a virtual environment.
Run each notebook from its own Lab folder, keeping the shared data folder in
place. Re-run P06 before using the registry on another machine: MLflow artifact
paths in the saved tracking stores refer to the runner that executed them.
P08 requires a working Docker engine for its container checks.

GitHub workflows verify the notebooks and Docker execution, capture real screen
evidence, and check a supplied public API URL. Verification runs:
https://github.com/Amanzxo/scse3040-mlops-labs-5-8/actions

## AI use disclosure

OpenAI Codex assisted with reviewing and correcting code, execution, deployment,
reports, and submission. Review and understand the work before presenting it.
