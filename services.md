# Microservices Architecture

This project uses a **7-microservice architecture** for scalability and separation of concerns. Each service handles a specific domain and uses dedicated data structures for optimal performance.

## Services Overview

| Service | Port | Purpose | Data Structure | Complexity |
|---------|------|---------|-----------------|-----------|
| **Auth Service** | 5001 | User registration, login, JWT tokens | HashTable (auth cache) | O(1) avg |
| **Courses Service** | 5002 | Browse courses, lessons, unlock logic | — | O(l) lesson fetch |
| **Quizzes Service** | 5003 | Quiz retrieval, grading, results | Stack | O(q) grading |
| **Recommendations Service** | 5004 | Personalized lesson recommendations | PriorityQueue | O(l log l) sort |
| **Search Service** | 5005 | Full-text search on courses/lessons | Trie | O(m) prefix search |
| **Progress Service** | 5006 | Learning progress tracking, analytics | Graph | O(V+E) = O(l) |
| **Teacher Service** | 5007 | Course authoring, uploads, analytics | HashTable | O(c) + O(s*l) results |

## Running Services

### Option 1: Docker Compose (Recommended)
```bash
docker-compose up -d
```

All services will start on their respective ports and connect via `alp_network`.

### Option 2: Manual (Development)
Start each service in a separate terminal:

```bash
# Auth Service (port 5001)
python -m flask run --app services/auth_service/app.py --port 5001

# Courses Service (port 5002)
python -m flask run --app services/courses_service/app.py --port 5002

# Quizzes Service (port 5003)
python -m flask run --app services/quizzes_service/app.py --port 5003

# Recommendations Service (port 5004)
python -m flask run --app services/recommendations_service/app.py --port 5004

# Search Service (port 5005)
python -m flask run --app services/search_service/app.py --port 5005

# Progress Service (port 5006)
python -m flask run --app services/progress_service/app.py --port 5006

# Teacher Service (port 5007)
python -m flask run --app services/teacher_service/app.py --port 5007
```

Set environment variables before running:
```bash
export ALP_SECRET="your-secret-key"
export ADMIN_TOKEN="your-admin-token"
```

## API Gateway (Future)

Add an API Gateway (e.g., Kong, Nginx) as a reverse proxy to:
- Route requests to appropriate services
- Handle rate limiting
- Implement caching
- Load balance across service replicas

Gateway would expose:
```
http://api.example.com/auth/*         → Auth Service (5001)
http://api.example.com/courses/*      → Courses Service (5002)
http://api.example.com/quizzes/*      → Quizzes Service (5003)
http://api.example.com/recommendations/* → Recommendations Service (5004)
http://api.example.com/search/*       → Search Service (5005)
http://api.example.com/progress/*     → Progress Service (5006)
http://api.example.com/teacher/*      → Teacher Service (5007)
```

## Data Structures & Complexity

### Auth Service
- **HashTable** (O(1) avg): Caches user credentials for fast login lookup
  - Load on startup: O(u) where u = users
  - Lookup/Insert: O(1) avg

### Quizzes Service
- **Stack** (O(1) push/pop): Manages quiz question flow
  - Each question pushed → answered → graded: O(1) per question
  - Total grading: O(q) where q = questions

### Recommendations Service
- **PriorityQueue** (O(l log l) for sorting): Prioritizes lessons by student score
  - Current: Sort-based O(l log l)
  - Ideal: Heap-based extraction O(log l) per pop

### Search Service
- **Trie** (O(m) search): Prefix-based full-text search
  - Each character match: O(1)
  - Total search: O(m) where m = query length
  - No dependency on corpus size!

### Progress Service
- **Graph** (O(V+E) traversal): Lesson prerequisites as directed edges
  - Adjacency list: O(l) to build
  - DFS/BFS: O(V+E) = O(l + l-1) = O(l)

### Teacher Service
- **HashTable** (O(1) ideal): Cache teacher → courses mapping
  - Course list: O(1) with cache vs O(c) without

## Future Enhancements

1. **Service Mesh** (Istio): Automatic request routing, circuit breakers, retries
2. **Cache Layer** (Redis): Shared cache across services (student results, recommendations)
3. **Message Queue** (RabbitMQ): Async operations (quiz grading notifications, analytics)
4. **Monitoring** (Prometheus + Grafana): Track service health and performance
5. **Load Balancing**: Multiple replicas per service with horizontal scaling

## Testing

Run integration tests:
```bash
python -m pytest tests/
```

Test inter-service communication:
```bash
# Get token from Auth Service
TOKEN=$(curl -X POST http://localhost:5001/auth/login -H "Content-Type: application/json" -d '{"username":"student","password":"pass"}' | jq -r '.token')

# Use token in Courses Service
curl -H "Authorization: Bearer $TOKEN" http://localhost:5002/courses
```

## Security Notes

- **JWT tokens** shared across services (SECRET_KEY must match)
- **ADMIN_TOKEN** required for teacher registration (stored as env var)
- **CORS enabled** on all services for web frontend cross-origin requests
- **Each service** validates JWT independently (no single point of failure)
