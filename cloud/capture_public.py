import json,os,time
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright

url=os.environ['PUBLIC_SERVICE_URL'].rstrip('/')
assert url.startswith('https://')
out=Path('public-evidence');out.mkdir(exist_ok=True)
good={'distance_km':4.0,'prep_time_min':30,'traffic_level':3,'rain':1}
health=requests.get(url+'/health',timeout=120)
health.raise_for_status();assert health.json()['model_loaded']
with sync_playwright() as pw:
    browser=pw.chromium.launch()
    page=browser.new_page(viewport={'width':1200,'height':1000},device_scale_factor=1.5)
    page.goto(url+'/docs',wait_until='networkidle')
    page.get_by_role('button',name='POST /predict Predict',exact=True).click()
    page.get_by_role('button',name='Try it out',exact=True).click()
    page.screenshot(path=str(out/'lab8-public-docs.png'))
    for name,payload,expected in [('success',good,200),('rejected',{**good,'traffic_level':9},422)]:
        page.get_by_role('textbox').fill(json.dumps(payload))
        with page.expect_response(lambda r:r.url.rstrip('/')==url+'/predict' and r.request.method=='POST') as response:
            page.get_by_role('button',name='Execute',exact=True).click()
        assert response.value.status==expected
        data=response.value.json()
        if expected==200:assert abs(data['delivery_min']-56.1)<0.01
        page.get_by_role('heading',name='Curl',exact=True).scroll_into_view_if_needed()
        page.screenshot(path=str(out/f'lab8-public-{name}.png'))
        (out/f'lab8-public-{name}.json').write_text(json.dumps({'url':url+'/predict','request':payload,'status_code':expected,'response':data},indent=2))
    browser.close()
(out/'public-deployment.json').write_text(json.dumps({'public_url':url,'platform':'Vercel','verified_from':'GitHub-hosted Ubuntu runner','health':health.json()},indent=2))
print('Verified public health, HTTP 200 prediction, HTTP 422 rejection, and captured /docs.')
