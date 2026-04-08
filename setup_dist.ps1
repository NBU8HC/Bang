Write-Host "Setting up distribution folder..." -ForegroundColor Cyan

# Copy tool executables to dist folder
Write-Host "`nCopying tool executables to dist folder..." -ForegroundColor Yellow

Copy-Item ".\Split_parameter_tool\dist\split_parameter_pro.exe" -Destination ".\dist\split_parameter_pro.exe" -Force
Write-Host "  ✓ Copied split_parameter_pro.exe" -ForegroundColor Green

Copy-Item ".\update_parameter\dist\dcm_parameter_tool.exe" -Destination ".\dist\dcm_parameter_tool.exe" -Force
Write-Host "  ✓ Copied dcm_parameter_tool.exe" -ForegroundColor Green

# Show dist folder contents
Write-Host "`nDist folder contents:" -ForegroundColor Yellow
Get-ChildItem ".\dist\*.exe" | Select-Object Name,@{Name="Size (MB)";Expression={[math]::Round($_.Length/1MB,2)}},LastWriteTime | Format-Table -AutoSize

Write-Host "`nSetup complete! You can now:" -ForegroundColor Cyan
Write-Host "  1. Run main_gui.exe directly from dist folder" -ForegroundColor White
Write-Host "  2. Copy all 3 .exe files to any location and run" -ForegroundColor White
Write-Host "  3. Tools will be detected automatically when in the same folder" -ForegroundColor White

Write-Host "`nTotal package size:" -ForegroundColor Yellow
$totalSize = (Get-ChildItem ".\dist\*.exe" | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "  $([math]::Round($totalSize, 2)) MB" -ForegroundColor Green
