# rebuild.ps1
# Nuke and rebuild DynamoDB tables, then reload data

Set-Location $PSScriptRoot

# Load .env into the current session
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    Write-Host "Loaded credentials from .env" -ForegroundColor DarkGray
} else {
    Write-Host "Warning: .env not found" -ForegroundColor Red
}

Write-Host "Initializing Terraform..." -ForegroundColor Yellow
Set-Location terraform
terraform init
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Destroying existing tables..." -ForegroundColor Yellow
terraform destroy -auto-approve
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Recreating tables..." -ForegroundColor Yellow
terraform apply -auto-approve
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Set-Location ..

Write-Host "Reloading data..." -ForegroundColor Yellow
python add_zip_and_readings.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Done." -ForegroundColor Green