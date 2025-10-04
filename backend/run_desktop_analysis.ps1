Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Desktop Screen Analysis Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This tool will capture your ENTIRE desktop screen" -ForegroundColor Yellow
Write-Host "and provide AI-powered analysis of what you see." -ForegroundColor Yellow
Write-Host ""
Write-Host "Instructions:" -ForegroundColor Green
Write-Host "1. Open any application you want to analyze" -ForegroundColor White
Write-Host "2. Press Enter to start the analysis" -ForegroundColor White
Write-Host "3. The AI will analyze your entire desktop" -ForegroundColor White
Write-Host ""
Write-Host "Note: This captures your full desktop, not just the terminal" -ForegroundColor Magenta
Write-Host ""
Read-Host "Press Enter to start analysis"
Write-Host ""
Write-Host "Starting analysis..." -ForegroundColor Green
python screen_analysis_desktop.py
Write-Host ""
Write-Host "Analysis complete. Press any key to exit." -ForegroundColor Green
Read-Host
