$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
docker version
if ($LASTEXITCODE -ne 0) { throw 'Start Docker Desktop and retry.' }
docker build -t delivery-api:1.0 .
if ($LASTEXITCODE -ne 0) { throw 'Image build failed.' }
docker images delivery-api:1.0
docker build -f Dockerfile.v2 -t delivery-api:2.0 .
if ($LASTEXITCODE -ne 0) { throw 'Second image build failed.' }
docker run -d --rm --name aman-delivery-2 -p 8011:8000 delivery-api:2.0
if ($LASTEXITCODE -ne 0) { throw 'Container start failed.' }
try {
  $ready = $false
  for ($attempt = 0; $attempt -lt 30; $attempt++) {
    try { Invoke-RestMethod http://127.0.0.1:8011/health | Out-Host; $ready = $true; break }
    catch { Start-Sleep -Seconds 1 }
  }
  if (-not $ready) { throw 'Container did not become healthy.' }
  Invoke-RestMethod http://127.0.0.1:8011/predict -Method Post -ContentType application/json -Body (Get-Content request.json -Raw) | ConvertTo-Json
  docker logs aman-delivery-2
} finally { docker stop aman-delivery-2 }
