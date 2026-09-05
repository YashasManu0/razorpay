# 1-Click Startup Script for AI Agent Negotiator
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  STARTING AI AGENT NEGOTIATOR (DEV STACK)       " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Check if database exists, if not seed it
if (-not (Test-Path "negotiator.db")) {
    Write-Host "[1/3] Seeding initial merchant & product database..." -ForegroundColor Yellow
    & ".venv\Scripts\python.exe" "scripts\seed_data.py"
}

# 2. Launch Backend (FastAPI on Port 8000)
Write-Host "[2/3] Launching FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".venv\Scripts\uvicorn.exe" app.main:app --app-dir backend --port 8000 --host 127.0.0.1
}

# Wait for backend to spin up
Start-Sleep -Seconds 2

# 3. Launch Frontend (Vite on Port 5173)
Write-Host "[3/3] Launching React Frontend on http://localhost:5173 ..." -ForegroundColor Green
Set-Location frontend
& npm run dev
