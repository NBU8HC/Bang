$python = "d:\Python\Tool parameter\.venv\Scripts\python.exe"

Write-Host "Building all tools to standalone executables..." -ForegroundColor Cyan

# Build Add New Parameter Tool
Write-Host "`n[1/4] Building Add New Parameter Tool..." -ForegroundColor Yellow
Set-Location "Add_new_parameter"
& $python -m PyInstaller --onefile --windowed --name add_new_parameter add_new_parameter.py
Set-Location ..

# Build Split Parameter Tool
Write-Host "`n[2/4] Building Split Parameter Tool..." -ForegroundColor Yellow
Set-Location "Split_parameter_tool"
& $python -m PyInstaller --onefile --windowed --name split_parameter_pro split_parameter_pro.py
Set-Location ..

# Build Update Parameter Tool
Write-Host "`n[3/4] Building Update Parameter Tool..." -ForegroundColor Yellow
Set-Location "update_parameter"
& $python -m PyInstaller --onefile --windowed --name dcm_parameter_tool dcm_parameter_tool.py
Set-Location ..

# Build Main GUI with all 3 tools embedded
Write-Host "`n[4/4] Building Main GUI with all tools..." -ForegroundColor Yellow
& $python -m PyInstaller --onefile --noconsole --add-data "Drift.gif;." --add-data "Nuclearbomb.gif;." --add-data "Add_new_parameter/dist/add_new_parameter.exe;Add_new_parameter" --add-data "Split_parameter_tool/dist/split_parameter_pro.exe;Split_parameter_tool" --add-data "update_parameter/dist/dcm_parameter_tool.exe;update_parameter" --name main_gui --clean main_gui.py

Write-Host "`nDone! Main executable: dist\main_gui.exe" -ForegroundColor Green
