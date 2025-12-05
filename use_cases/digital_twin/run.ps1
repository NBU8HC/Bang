# Digital Twin Assembly-Line Simulation - Quick Start Script
Write-Host "================================================" -ForegroundColor Magenta
Write-Host "  Digital Twin Assembly-Line Simulation" -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Magenta
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "app.py")) {
    Write-Host "Error: app.py not found. Please run this script from use_cases\digital_twin\" -ForegroundColor Red
    exit 1
}

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Install dependencies if needed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$requirementsPath = "..\requirements.txt"
if (Test-Path $requirementsPath) {
    pip install -q -r $requirementsPath
    Write-Host "✓ Dependencies checked" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Digital Twin Simulation..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Dashboard will be available at:" -ForegroundColor Magenta
Write-Host "  http://localhost:5002" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the application
python app.py
