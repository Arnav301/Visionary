@echo off
title Desktop Screen Analysis
echo.
echo ========================================
echo    Desktop Screen Analysis Tool
echo ========================================
echo.
echo This tool will capture your ENTIRE desktop screen
echo and provide AI-powered analysis of what you see.
echo.
echo Instructions:
echo 1. Open any application you want to analyze
echo 2. Press Enter to start the analysis
echo 3. The AI will analyze your entire desktop
echo.
echo Note: This captures your full desktop, not just the terminal
echo.
pause
echo.
echo Starting analysis...
python screen_analysis_desktop.py
echo.
echo Analysis complete. Press any key to exit.
pause >nul
