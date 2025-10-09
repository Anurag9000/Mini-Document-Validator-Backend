Write-Host "Setting up local dev environment"
py -3.11 -m venv .venv
./.venv/Scripts/pip.exe install -U pip
./.venv/Scripts/pip.exe install -e ".[dev]"
Write-Host "Done. Activate with: .\\.venv\\Scripts\\Activate.ps1"

