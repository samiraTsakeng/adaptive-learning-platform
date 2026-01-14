# Start all microservices (Windows PowerShell)

Write-Host "🚀 Starting Adaptive Learning Platform Microservices..." -ForegroundColor Green

# Set environment variables
$env:ALP_SECRET = $env:ALP_SECRET ? $env:ALP_SECRET : "change_this_secret"
$env:ADMIN_TOKEN = $env:ADMIN_TOKEN ? $env:ADMIN_TOKEN : "admin_secret"
$env:FLASK_ENV = "development"

# Function to start a service
function Start-Service {
    param(
        [string]$ServiceName,
        [string]$AppPath,
        [string]$Port
    )
    
    Write-Host "Starting $ServiceName on port $Port..." -ForegroundColor Yellow
    Start-Process -NoNewWindow -FilePath python -ArgumentList @(
        "-m", "flask", "run",
        "--app", $AppPath,
        "--port", $Port,
        "--host", "0.0.0.0"
    )
    Write-Host "✓ $ServiceName started" -ForegroundColor Green
}

# Start all services
Start-Service "Auth Service" "services/auth_service/app.py" "5001"
Start-Service "Courses Service" "services/courses_service/app.py" "5002"
Start-Service "Quizzes Service" "services/quizzes_service/app.py" "5003"
Start-Service "Recommendations Service" "services/recommendations_service/app.py" "5004"
Start-Service "Search Service" "services/search_service/app.py" "5005"
Start-Service "Progress Service" "services/progress_service/app.py" "5006"
Start-Service "Teacher Service" "services/teacher_service/app.py" "5007"

Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Services available at:"
Write-Host "  Auth Service:            http://localhost:5001"
Write-Host "  Courses Service:         http://localhost:5002"
Write-Host "  Quizzes Service:         http://localhost:5003"
Write-Host "  Recommendations Service: http://localhost:5004"
Write-Host "  Search Service:          http://localhost:5005"
Write-Host "  Progress Service:        http://localhost:5006"
Write-Host "  Teacher Service:         http://localhost:5007"
Write-Host ""
Write-Host "Press Ctrl+C to stop services"

# Keep window open
Read-Host "Press Enter to exit"
