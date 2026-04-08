$python = "d:\Python\Tool parameter\.venv\Scripts\python.exe"

Write-Host "Building all tools to standalone executables..." -ForegroundColor Cyan

# Build Split Parameter Tool
Write-Host "`n[1/3] Building Split Parameter Tool..." -ForegroundColor Yellow
Set-Location "Split_parameter_tool"
& $python -m PyInstaller --onefile --windowed --name split_parameter_pro split_parameter_pro.py
Set-Location ..

# Build Update Parameter Tool
Write-Host "`n[2/3] Building Update Parameter Tool..." -ForegroundColor Yellow
Set-Location "update_parameter"
& $python -m PyInstaller --onefile --windowed --name dcm_parameter_tool dcm_parameter_tool.py
Set-Location ..

# Build Main GUI (standalone - no embedded tools)
Write-Host "`n[3/3] Building Main GUI (standalone)..." -ForegroundColor Yellow
& $python -m PyInstaller --onefile --noconsole --add-data "Drift.gif;." --add-data "Nuclearbomb.gif;." --name main_gui --clean main_gui.py

# Setup distribution folder
Write-Host "`n[4/4] Setting up distribution folder..." -ForegroundColor Yellow
Copy-Item ".\Split_parameter_tool\dist\split_parameter_pro.exe" -Destination ".\dist\split_parameter_pro.exe" -Force
Write-Host "  ✓ Copied split_parameter_pro.exe" -ForegroundColor Green

Copy-Item ".\update_parameter\dist\dcm_parameter_tool.exe" -Destination ".\dist\dcm_parameter_tool.exe" -Force
Write-Host "  ✓ Copied dcm_parameter_tool.exe" -ForegroundColor Green

# Show results
Write-Host "`nBuild complete! Distribution folder contents:" -ForegroundColor Green
Get-ChildItem ".\dist\*.exe" | Select-Object Name,@{Name="Size (MB)";Expression={[math]::Round($_.Length/1MB,2)}} | Format-Table -AutoSize

$totalSize = (Get-ChildItem ".\dist\*.exe" | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Total package size: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Cyan
Write-Host "`n✓ Ready to use! Copy all files from 'dist' folder to any location." -ForegroundColor Green
