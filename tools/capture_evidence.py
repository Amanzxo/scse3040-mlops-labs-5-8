"""Capture actual Linux PTY sessions with ttyd and actual API browser pages.

This script runs on the GitHub-hosted runner, after the notebooks. Screenshots
are browser captures of real terminals and live UIs, never synthesized images.
"""
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / 'evidence'
EV.mkdir(exist_ok=True)
PY = sys.executable
selection = json.loads((ROOT / 'Lab 6/work/selection.json').read_text())
environment = {**os.environ, 'MLFLOW_TRACKING_URI': selection['tracking_uri']}
children = []

def start(args, cwd, name):
    log = open(EV / f'{name}.log', 'w', encoding='utf-8')
    p = subprocess.Popen(args, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, env=environment)
    children.append(p)
    return p

def ready(url, seconds=180):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return r
        except requests.RequestException:
            pass
        time.sleep(1)
    raise RuntimeError(f'Service did not become ready: {url}')

def terminal(browser, port, cwd):
    start(['ttyd', '-i', '127.0.0.1', '-p', str(port), '-t', 'fontSize=18', '-W', 'bash', '--noprofile', '--norc'], cwd, f'terminal-{port}')
    ready(f'http://127.0.0.1:{port}')
    page = browser.new_page(viewport={'width': 1200, 'height': 1200})
    page.goto(f'http://127.0.0.1:{port}')
    page.locator('.xterm-helper-textarea').wait_for(state='attached')
    page.locator('.xterm-helper-textarea').focus()
    return page

def enter(page, command):
    page.keyboard.type(command, delay=4)
    page.keyboard.press('Enter')

def api_capture(browser, base, prefix):
    base = base.rstrip('/')
    ready(base + '/health', seconds=300)
    page = browser.new_page(viewport={'width': 1440, 'height': 1080})
    page.goto(base + '/docs')
    page.get_by_role('button', name='POST /predict Predict', exact=True).click()
    page.get_by_role('button', name='Try it out', exact=True).click()
    page.screenshot(path=str(EV / f'{prefix}-docs.png'), full_page=False)
    good = {'distance_km': 4.0, 'prep_time_min': 30, 'traffic_level': 3, 'rain': 1}
    for suffix, payload, expected in [('success', good, 200), ('rejected', {**good, 'traffic_level': 9}, 422)]:
        page.get_by_role('textbox').fill(json.dumps(payload))
        with page.expect_response(lambda r: r.url.rstrip('/') == base + '/predict' and r.request.method == 'POST') as result:
            page.get_by_role('button', name='Execute', exact=True).click()
        assert result.value.status == expected
        page.get_by_role('heading', name='Curl', exact=True).scroll_into_view_if_needed()
        page.screenshot(path=str(EV / f'{prefix}-{suffix}.png'), full_page=False)
        response = result.value.json()
        (EV / f'{prefix}-{suffix}.json').write_text(json.dumps({'url': base + '/predict', 'request': payload,
            'status_code': expected, 'response': response}, indent=2))
    page.close()

try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pytest_page = terminal(browser, 7685, ROOT / 'Lab 5/work')
        marker = EV / 'pytest-exit-code.txt'
        marker.unlink(missing_ok=True)
        enter(pytest_page, f'{shlex.quote(PY)} -m pytest -v; echo $? > {shlex.quote(str(marker))}')
        deadline = time.monotonic() + 120
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(1)
        assert marker.read_text().strip() == '0'
        pytest_page.screenshot(path=str(EV / 'pytest-terminal.png'))

        serve_page = terminal(browser, 7687, ROOT / 'Lab 7')
        serve_command = (f'{shlex.quote(PY)} -m mlflow models serve -m '
            f'models:/{selection["registered_model"]}/{selection["version"]} '
            '--env-manager local --host 127.0.0.1 --port 5001')
        enter(serve_page, serve_command)
        ready('http://127.0.0.1:5001/ping')
        serve_page.screenshot(path=str(EV / 'mlflow-serve-terminal.png'))

        payload = {'dataframe_split': {'columns': ['distance_km', 'prep_time_min', 'traffic_level', 'rain'], 'data': [[5.0, 20, 2, 0]]}}
        (EV / 'mlflow-request.json').write_text(json.dumps(payload, indent=2))
        invoke_page = terminal(browser, 7686, EV)
        curl = 'curl -sS http://127.0.0.1:5001/invocations -H "Content-Type: application/json" --data-binary @mlflow-request.json'
        enter(invoke_page, curl)
        r = requests.post('http://127.0.0.1:5001/invocations', json=payload, timeout=20)
        r.raise_for_status()
        assert len(r.json()['predictions']) == 1
        (EV / 'mlflow-response.json').write_text(json.dumps(r.json(), indent=2))
        invoke_page.wait_for_timeout(1500)
        invoke_page.screenshot(path=str(EV / 'mlflow-request-terminal.png'))

        image_page = terminal(browser, 7688, ROOT / 'Lab 8/work')
        enter(image_page, 'docker images delivery-api:1.0')
        image_page.wait_for_timeout(1500)
        image_page.screenshot(path=str(EV / 'docker-images-terminal.png'))
        images = subprocess.check_output(['docker', 'images', '--format', '{{json .}}', 'delivery-api:1.0'], text=True)
        assert images.strip()
        (EV / 'docker-images.jsonl').write_text(images)

        start([PY, '-m', 'mlflow', 'ui', '--backend-store-uri', selection['tracking_uri'],
            '--host', '127.0.0.1', '--port', '5000'], ROOT / 'Lab 6', 'mlflow-ui-ci')
        ready('http://127.0.0.1:5000')
        experiment_page = browser.new_page(viewport={'width': 1680, 'height': 1000})
        experiment_page.goto('http://127.0.0.1:5000/#/experiments/1/runs?workflowType=machine_learning&startTime=ALL')
        experiment_page.get_by_role('link', name='linear-baseline', exact=True).wait_for()
        close = experiment_page.get_by_role('button', name='Close', exact=True)
        if close.count():
            close.first.click()
        experiment_page.get_by_role('button', name='Columns', exact=True).click()
        for label in ['mae_minutes', 'max_depth', 'model_type', 'n_estimators', 'Dataset', 'Source', 'Models']:
            experiment_page.get_by_text(label, exact=True).last.click()
        experiment_page.get_by_role('heading', name='Runs', exact=True).click()
        experiment_page.screenshot(path=str(EV / 'mlflow-runs.jpg'))
        experiment_page.get_by_role('link', name=selection['name'], exact=True).click()
        experiment_page.get_by_text(selection['run_id'], exact=True).wait_for()
        experiment_page.screenshot(path=str(EV / 'mlflow-best-run.jpg'))
        experiment_page.get_by_role('link', name=selection['registered_model'], exact=True).first.click()
        experiment_page.get_by_text('Production', exact=False).wait_for()
        experiment_page.screenshot(path=str(EV / 'mlflow-registry.jpg'))

        start([PY, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8000'], ROOT / 'Lab 7/work', 'lab7-api-ci')
        api_capture(browser, 'http://127.0.0.1:8000', 'lab7-ci')

        start([PY, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8008'], ROOT / 'Lab 8/work', 'lab8-api-ci')
        api_capture(browser, 'http://127.0.0.1:8008', 'lab8-local-ci')
        public_url = os.environ.get('PUBLIC_SERVICE_URL', '').strip()
        if public_url:
            assert public_url.startswith('https://'), 'Public deployment must use HTTPS'
            api_capture(browser, public_url, 'lab8-public')
            (EV / 'public-deployment.json').write_text(json.dumps({'public_url': public_url, 'verified_from': 'GitHub-hosted Ubuntu runner'}, indent=2))
        browser.close()
finally:
    for process in reversed(children):
        if process.poll() is None:
            process.terminate()
    for process in children:
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
