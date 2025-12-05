# Run All Three Use Cases Simultaneously
# Opens each application in a new PowerShell window

Write-Host "================================================" -ForegroundColor Green
Write-Host "  Starting All Industrial Use Cases" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

$scriptDir = $PSScriptRoot

# Check if subdirectories exist
$dirs = @("vehicle_telemetry", "digital_twin", "resource_allocation")
foreach ($dir in $dirs) {
    if (!(Test-Path (Join-Path $scriptDir $dir))) {
        Write-Host "✗ Directory not found: $dir" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Starting all three systems in separate windows..." -ForegroundColor Yellow
Write-Host ""

# Start Vehicle Telemetry
Write-Host "1. Starting Vehicle Telemetry (Port 5001)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-File", (Join-Path $scriptDir "vehicle_telemetry\run.ps1")
Start-Sleep -Seconds 2

# Start Digital Twin
Write-Host "2. Starting Digital Twin Simulation (Port 5002)..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit", "-File", (Join-Path $scriptDir "digital_twin\run.ps1")
Start-Sleep -Seconds 2

# Start Resource Allocation
Write-Host "3. Starting Resource Allocation (Port 5003)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", (Join-Path $scriptDir "resource_allocation\run.ps1")

Write-Host ""
Write-Host "✓ All systems started in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "Access dashboards at:" -ForegroundColor White
Write-Host "  • Vehicle Telemetry:    http://localhost:5001" -ForegroundColor Cyan
Write-Host "  • Digital Twin:         http://localhost:5002" -ForegroundColor Magenta
Write-Host "  • Resource Allocation:  http://localhost:5003" -ForegroundColor Yellow
Write-Host ""
Write-Host "Close each PowerShell window to stop the respective server." -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
