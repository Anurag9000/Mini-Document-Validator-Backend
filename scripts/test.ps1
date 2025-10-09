if (-not (Test-Path .\.venv\Scripts\python.exe)) {
  Write-Host "Creating virtualenv (.venv)"
  py -3.11 -m venv .venv
}

./.venv/Scripts/pip.exe install -U pip | Out-Null
./.venv/Scripts/pip.exe install -e ".[dev]" | Out-Null
./.venv/Scripts/pytest.exe -q

