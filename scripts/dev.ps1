Param(
    [string]$Host = $env:APP_HOST
    ,[string]$Port = $env:APP_PORT
)

if (-not $Host) { $Host = "127.0.0.1" }
if (-not $Port) { $Port = "8000" }

if (-not (Test-Path .\.venv\Scripts\python.exe)) {
  Write-Host "Creating virtualenv (.venv)"
  py -3.11 -m venv .venv
}

Write-Host "Installing dependencies (editable + dev)"
./.venv/Scripts/pip.exe install -U pip | Out-Null
./.venv/Scripts/pip.exe install -e ".[dev]" | Out-Null

Write-Host "Starting server on $Host:$Port"
./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host $Host --port $Port

