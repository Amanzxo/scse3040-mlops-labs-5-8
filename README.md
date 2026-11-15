# SCSE3040 Practicals 05-08

Student: Aman Singh  
Roll number: S24CSEU2579 (from the supplied filenames)  
Batch: 58  
Executed and prepared: 9 November 2026

## Files

Each `Lab N` folder contains the executed notebook, the correctly named PDF report, and the supporting `work/` files. The common dataset is in `data/`. The MLflow database, runs, model artifacts, and registry are in `Lab 6/`. Actual UI captures and command/HTTP logs are in `evidence/`.

The supplied originals in Downloads were not modified.

## Verified results

| Practical | Notebook self-check | Additional verification |
|---|---|---|
| P05 | 9/9 passed | 10 pytest tests passed; full-dataset MAE before and after refactor is 1.924653079833835 minutes |
| P06 | 8/8 passed | 11 tracked runs, selected linear-baseline, model artifact saved and registered |
| P07 | 9/9 passed | 3 API tests passed; real HTTP prediction and validation checked; registry version 1 is Production |
| P08 | 8/9 passed | 3 direct API tests passed; real local HTTP 200 and 422; container execution awaits Docker |

Best run ID: `2c5677703a95494593ed1e858f16a96a`  
Best MAE: `1.924653079833835` minutes  
Registered model: `aman-delivery-time-model`, version `1`, stage `Production`, alias `champion`.

The P06 walkthrough registers a random-forest champion first. The final selection includes the linear baseline and correctly selects it over the forests. The separate registry name above identifies that overall winner.

## Requirements before LMS submission

The screenshots from LMS require more than just finished notebook code. The reports explicitly distinguish verified local work from missing submission evidence:

- Supply the actual lab session dates. The preparation date is recorded; it is not represented as an attendance date.
- Add the student's personal repository URL to P05, P06, and P08. The course source URL is included as a reference, not as a claim that the student owns that repository.
- Capture P05's required native terminal pytest screenshot. The exact real stdout is included. The UI tool blocked launching PowerShell, so no terminal screenshot was fabricated.
- For P07, capture the prescribed terminal screenshots if the instructor requires that exact format. The Windows launcher for `mlflow models serve` was blocked by Application Control. `serve_registered.py` runs the same native MLflow scoring application through Python, and the successful `/invocations` request is recorded. The original launcher error is retained in `evidence/mlflow-serve.log`.
- Install/start Docker Desktop, run P08 end to end, and capture the image size and container prediction. No Docker engine was installed on this computer during preparation.
- Deploy P08 to a cloud account, record the real public service URL and cloud platform, and replace the clearly labelled local screenshots with public URL evidence. No deployment, public URL, account, or image-size evidence is invented.
- Sign in to Bennett LMS and upload each PDF to its corresponding practical. No upload or submission has occurred.

## Run locally

Use Python 3.12. From this folder:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-lock.txt
.venv\Scripts\python -m pip install jupyterlab
.venv\Scripts\python -m jupyter lab
```

Open one notebook, select the Python environment above, and run all cells from the top. Each notebook must run with its `Lab N` folder as its working directory, as Jupyter normally does when opening it from the file browser. The `data/` folder must stay alongside the four lab folders.

P06's saved tracking store contains absolute artifact paths from the machine where it was executed. If moving this package elsewhere, re-run P06 before using its saved registry/model URIs. Its experiment results and PDF remain readable without re-execution. The notebook preserves history by creating a fresh tracking database when one already exists; the latest selection stores the database URI for the serving helper.

### Tests

```powershell
cd 'Lab 5/work'
..\..\.venv\Scripts\python -m pytest -v
```

For the API tests, use the same command from `Lab 7/work` or `Lab 8/work`.

### FastAPI

From `Lab 7/work` or `Lab 8/work`:

```powershell
..\..\.venv\Scripts\python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`. Stop with Ctrl+C. Do not start both applications on the same port simultaneously.

### MLflow

After executing P06, start its UI from `Lab 6`:

```powershell
..\.venv\Scripts\python -m mlflow ui --backend-store-uri "sqlite:///<absolute-path-to-the-current-mlflow.db>" --port 5000
```

The actual current URI is printed by P06 and stored in `Lab 6/work/selection.json`. The initial database supplied with this package is `Lab 6/work/mlflow.db`.

From `Lab 7`, start the scoring helper:

```powershell
..\.venv\Scripts\python serve_registered.py
```

It serves `/invocations` on port 5001. The request format is in `evidence/mlflow-request.json`. Standard command on a system whose console launcher is allowed:

```powershell
python -m mlflow models serve -m models:/aman-delivery-time-model/1 --env-manager local --host 127.0.0.1 --port 5001
```

Set `MLFLOW_TRACKING_URI` to the current store before that standard command.

### Docker and cloud

`Lab 8/work/run-docker.ps1` builds both lab images, checks readiness, sends the rainy-order request, shows logs, and stops its container in a finally block. Run it only after Docker Desktop is ready.

`Lab 8/work/render.yaml` and the Dockerfile form a prepared Render deployment configuration. Publish that work folder to a repository you control and create a Docker web service from it in your own cloud account. Use the actual assigned URL in the report and verify `/health`, `/docs`, valid `/predict`, and invalid `/predict` responses from outside the local machine. No cloud fees or subscriptions were initiated.

## Remote completion workflow

The repository now includes `.github/workflows/verify-labs.yml` and portable `requirements-ci.txt`. On a GitHub-hosted Ubuntu runner, this workflow executes all four notebooks with a real Docker engine, requires every self-check to pass, and captures actual terminal sessions for pytest, MLflow serving, curl, and Docker image size. It saves the executed notebooks, model registry files, and screenshots as a downloadable workflow artifact.

The root `render.yaml` deploys `Lab 8/work` as a free-plan Docker web service. After deployment, dispatch the workflow again with the real public service URL to capture successful and rejected requests against the public service from outside the local network.

These workflow and deployment files are prepared and syntax-checked. They have not yet been run on GitHub or deployed to Render; account connections are pending.

## AI disclosure

OpenAI Codex assisted with code review, corrections, execution, testing, and report preparation. The same disclosure is included in all four notebooks and PDF reports. Review the code and be able to explain and modify it for the viva.

Course source: https://github.com/Bennett-MLOps-Lab/SCSE3040-Lab
