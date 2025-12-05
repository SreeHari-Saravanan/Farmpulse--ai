# FarmPulse AI - Quick Setup Script
# This script helps set up the development environment quickly

Write-Host "==================================================================" -ForegroundColor Green
Write-Host "FarmPulse AI - Quick Setup Script" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js installed: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

# Check MongoDB
Write-Host ""
Write-Host "Checking MongoDB..." -ForegroundColor Yellow
try {
    $mongoCheck = mongo --eval "db.adminCommand('ping')" 2>&1
    Write-Host "✓ MongoDB is running" -ForegroundColor Green
} catch {
    Write-Host "⚠ MongoDB not detected. Please start MongoDB or use Docker:" -ForegroundColor Yellow
    Write-Host "  docker run -d -p 27017:27017 --name mongodb mongo:latest" -ForegroundColor Cyan
}

# Check Redis
Write-Host ""
Write-Host "Checking Redis..." -ForegroundColor Yellow
try {
    $redisCheck = redis-cli ping 2>&1
    if ($redisCheck -eq "PONG") {
        Write-Host "✓ Redis is running" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Redis not detected. Please start Redis or use Docker:" -ForegroundColor Yellow
    Write-Host "  docker run -d -p 6379:6379 --name redis redis:latest" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "Setting up Backend..." -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green

Set-Location backend

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Setup environment file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ Please edit backend/.env with your configuration" -ForegroundColor Cyan
}

# Seed database
Write-Host ""
$seedDb = Read-Host "Do you want to seed the database with test data? (y/n)"
if ($seedDb -eq "y") {
    Write-Host "Seeding database..." -ForegroundColor Yellow
    python scripts\seed_db.py
}

Set-Location ..

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "Setting up Frontend..." -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green

Set-Location frontend

# Install dependencies
Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
npm install

# Setup environment file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ Please edit frontend/.env with your configuration" -ForegroundColor Cyan
}

Set-Location ..

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Backend:" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "2. Start Frontend (in new terminal):" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm start" -ForegroundColor White
Write-Host ""
Write-Host "3. Access the application:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "4. Test credentials:" -ForegroundColor Yellow
Write-Host "   Farmer: farmer@test.com / farmer123" -ForegroundColor White
Write-Host "   Vet: vet@test.com / vet123" -ForegroundColor White
Write-Host "   Admin: admin@test.com / admin123" -ForegroundColor White
Write-Host ""
Write-Host "For detailed documentation, see:" -ForegroundColor Cyan
Write-Host "   - README.md" -ForegroundColor White
Write-Host "   - docs/IMPLEMENTATION_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
