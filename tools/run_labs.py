"""Execute each submitted notebook against the runner's actual Docker engine."""
import json
import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MLFLOW_DISABLE_AGENT_HINT', '1')
summary = {}

for lab in [5, 6, 7, 8]:
    path = ROOT / f'Lab {lab}' / f'P{lab:02d}_S24CSEU2579.ipynb'
    notebook = nbformat.read(path, as_version=4)
    print(f'Executing {path.name}', flush=True)
    client = NotebookClient(notebook, timeout=1200, kernel_name='python3',
        resources={'metadata': {'path': str(path.parent)}})
    try:
        client.execute()
    finally:
        nbformat.write(notebook, path)
    outputs = [o.text for c in notebook.cells for o in c.get('outputs', [])
        if o.output_type == 'stream' and 'SELF-CHECK' in o.text]
    assert len(outputs) == 1, f'Lab {lab}: missing self-check output'
    print(outputs[0], flush=True)
    passed, failed = outputs[0].count('[PASS]'), outputs[0].count('[FAIL]')
    summary[str(lab)] = {'passed': passed, 'failed': failed}
    (ROOT / 'verification-ci.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    assert failed == 0, f'Lab {lab}: {failed} self-checks failed'
print('All four notebook self-checks passed against real execution.', flush=True)
