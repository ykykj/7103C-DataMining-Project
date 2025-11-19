#!/usr/bin/env pwsh
# Personal Assistant Agent - Quick Start Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Personal Assistant Agent - Starting" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file with your API keys." -ForegroundColor Yellow
    Write-Host "Example:" -ForegroundColor Yellow
    Write-Host "DEEPSEEK_API_KEY=sk-your-key-here" -ForegroundColor Gray
    Write-Host "GOOGLE_CLOUD_AUTH_EMAIL=your-email@gmail.com" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the application
Write-Host "Starting application..." -ForegroundColor Green
python src\Main.py

Read-Host "Press Enter to exit"

