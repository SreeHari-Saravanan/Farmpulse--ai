# FarmPulse AI - Start Development Servers
# This script starts both backend and frontend servers

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Starting FarmPulse AI Development Servers" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend Server in new window
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\sharavana Kumar\OneDrive\Desktop\FarmPulse\backend'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start Frontend Server in new window
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\sharavana Kumar\OneDrive\Desktop\FarmPulse\frontend'; npm start"

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Servers Starting..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Credentials:" -ForegroundColor Yellow
Write-Host "  Farmer: farmer@test.com / farmer123" -ForegroundColor White
Write-Host "  Vet:    vet@test.com / vet123" -ForegroundColor White
Write-Host "  Admin:  admin@test.com / admin123" -ForegroundColor White
Write-Host ""
