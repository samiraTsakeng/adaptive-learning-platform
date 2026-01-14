#!/bin/bash
# Start all microservices (Linux/Mac)

set -e

echo "🚀 Starting Adaptive Learning Platform Microservices..."

# Export environment variables
export ALP_SECRET="${ALP_SECRET:-change_this_secret}"
export ADMIN_TOKEN="${ADMIN_TOKEN:-admin_secret}"
export FLASK_ENV="development"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to start a service
start_service() {
    local service_name=$1
    local app_path=$2
    local port=$3
    
    echo -e "${YELLOW}Starting $service_name on port $port...${NC}"
    python -m flask run \
        --app "$app_path" \
        --port "$port" \
        --host 0.0.0.0 &
    
    echo -e "${GREEN}✓ $service_name started (PID: $!)${NC}"
}

# Start all services
start_service "Auth Service" "services/auth_service/app.py" "5001"
start_service "Courses Service" "services/courses_service/app.py" "5002"
start_service "Quizzes Service" "services/quizzes_service/app.py" "5003"
start_service "Recommendations Service" "services/recommendations_service/app.py" "5004"
start_service "Search Service" "services/search_service/app.py" "5005"
start_service "Progress Service" "services/progress_service/app.py" "5006"
start_service "Teacher Service" "services/teacher_service/app.py" "5007"

echo ""
echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo "Services available at:"
echo "  Auth Service:           http://localhost:5001"
echo "  Courses Service:        http://localhost:5002"
echo "  Quizzes Service:        http://localhost:5003"
echo "  Recommendations Service: http://localhost:5004"
echo "  Search Service:         http://localhost:5005"
echo "  Progress Service:       http://localhost:5006"
echo "  Teacher Service:        http://localhost:5007"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all background processes
wait
