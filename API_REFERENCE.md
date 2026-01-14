"""
API Client Reference for React Frontend

This file documents the expected request/response shapes for all microservices.
Use this to generate TypeScript types and axios wrapper.

Base URLs (adjust for production):
- Auth Service:           http://localhost:5001
- Courses Service:        http://localhost:5002
- Quizzes Service:        http://localhost:5003
- Recommendations Service: http://localhost:5004
- Search Service:         http://localhost:5005
- Progress Service:       http://localhost:5006
- Teacher Service:        http://localhost:5007

All requests (except login/register) require:
  Header: Authorization: Bearer <token>
"""

# ============================================================================
# AUTH SERVICE (Port 5001)
# ============================================================================

POST /auth/register
Request:
{
  "username": "student@example.com",
  "password": "secure_password",
  "role": "student"  # or "teacher" (requires admin_token)
  "admin_token": "admin_secret"  # required only if role=="teacher"
}

Response (201):
{
  "success": true,
  "message": "✅ User registered",
  "role": "student"
}

Response (400):
{
  "success": false,
  "message": "❌ username and password required"
}


POST /auth/login
Request:
{
  "username": "student@example.com",
  "password": "secure_password"
}

Response (200):
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",  # JWT token (24hr expiry)
  "user_id": 1,
  "role": "student"
}

Response (401):
{
  "success": false,
  "message": "Invalid credentials"
}


# ============================================================================
# COURSES SERVICE (Port 5002)
# ============================================================================

GET /courses
Headers: Authorization: Bearer <token>

Response (200):
[
  {
    "id": 1,
    "title": "Introduction to Python",
    "description": "Learn Python basics"
  },
  {
    "id": 2,
    "title": "Data Structures",
    "description": "Arrays, Linked Lists, Trees"
  }
]


GET /courses/<course_id>
Headers: Authorization: Bearer <token>

Response (200):
{
  "id": 1,
  "title": "Introduction to Python",
  "description": "Learn Python basics",
  "lessons": [
    {
      "id": 10,
      "title": "Variables and Types",
      "difficulty": 1
    },
    {
      "id": 11,
      "title": "Control Flow",
      "difficulty": 2
    }
  ]
}


GET /courses/<course_id>/lessons
Headers: Authorization: Bearer <token>

Response (200):
[
  {
    "id": 10,
    "title": "Variables and Types",
    "content": "# Variables\nIn Python...",
    "difficulty": 1
  }
]


GET /lessons/<lesson_id>
Headers: Authorization: Bearer <token>

Response (200):
{
  "id": 10,
  "title": "Variables and Types",
  "content": "# Variables\nIn Python...",
  "difficulty": 1,
  "locked": false  # true if previous lesson not passed
}

Response (404):
{
  "message": "Lesson not found"
}


# ============================================================================
# QUIZZES SERVICE (Port 5003)
# ============================================================================

GET /quizzes/<lesson_id>
Headers: Authorization: Bearer <token>

Response (200):
{
  "lesson_id": 10,
  "questions": [
    {
      "quiz_id": 5,
      "question_id": 1,
      "question": "What is a variable?"
    },
    {
      "quiz_id": 5,
      "question_id": 2,
      "question": "Which is valid Python syntax?"
    }
  ]
}


POST /quizzes/<lesson_id>/submit
Headers: Authorization: Bearer <token>

Request:
{
  "answers": {
    "1": "A named container for storing data",
    "2": "x = 10"
  }
}

Response (200):
{
  "score": 2,
  "total": 2,
  "passed": true  # true if score >= total (100%)
}


# ============================================================================
# RECOMMENDATIONS SERVICE (Port 5004)
# ============================================================================

GET /recommendations/<user_id>/<course_id>
Headers: Authorization: Bearer <token>

Response (200):
[
  {
    "lesson_id": 12,
    "title": "Functions",
    "best_score": 1,
    "total_q": 3,
    "attempts": 2
  },
  {
    "lesson_id": 13,
    "title": "Error Handling",
    "best_score": 0,
    "total_q": 2,
    "attempts": 1
  }
]


# ============================================================================
# SEARCH SERVICE (Port 5005)
# ============================================================================

GET /search?q=python
Headers: Authorization: Bearer <token>

Response (200):
{
  "courses": [
    {
      "id": 1,
      "title": "Introduction to Python",
      "description": "Learn Python basics",
      "lessons": [
        {
          "id": 10,
          "title": "Variables and Types",
          "content": "...",
          "difficulty": 1
        }
      ]
    }
  ],
  "lessons": [
    {
      "id": 10,
      "title": "Variables and Types",
      "course_id": 1
    }
  ]
}


# ============================================================================
# PROGRESS SERVICE (Port 5006)
# ============================================================================

GET /progress/<user_id>
Headers: Authorization: Bearer <token>

Response (200):
[
  {
    "course_id": 1,
    "title": "Introduction to Python",
    "passed": 5,
    "total": 10,
    "percent": 50
  },
  {
    "course_id": 2,
    "title": "Data Structures",
    "passed": 0,
    "total": 8,
    "percent": 0
  }
]


GET /progress/<user_id>/<course_id>
Headers: Authorization: Bearer <token>

Response (200):
{
  "course_id": 1,
  "lessons": [
    {
      "lesson_id": 10,
      "title": "Variables and Types",
      "difficulty": 1,
      "passed": true,
      "unlocked": true
    },
    {
      "lesson_id": 11,
      "title": "Control Flow",
      "difficulty": 2,
      "passed": false,
      "unlocked": true
    },
    {
      "lesson_id": 12,
      "title": "Functions",
      "difficulty": 3,
      "passed": false,
      "unlocked": false  # locked because lesson 11 not passed
    }
  ]
}


# ============================================================================
# TEACHER SERVICE (Port 5007)
# ============================================================================

POST /teacher/upload
Headers: 
  Authorization: Bearer <token>
  Content-Type: application/json

Request:
{
  "title": "Web Development Basics",
  "description": "Learn HTML, CSS, JavaScript",
  "lessons": [
    {
      "title": "HTML Introduction",
      "content": "# HTML\nHTML is...",
      "difficulty": 1,
      "quiz": [
        {
          "question": "What does HTML stand for?",
          "correct_answer": "HyperText Markup Language"
        },
        {
          "question": "Which is a valid HTML tag?",
          "correct_answer": "<div>"
        }
      ]
    },
    {
      "title": "CSS Basics",
      "content": "# CSS\nCSS is...",
      "difficulty": 2,
      "quiz": [
        {
          "question": "What is CSS used for?",
          "correct_answer": "Styling HTML elements"
        }
      ]
    }
  ]
}

Response (201):
{
  "success": true,
  "course_id": 5
}

Response (400):
{
  "success": false,
  "message": "Invalid package format"
}


GET /teacher/courses
Headers: Authorization: Bearer <token>

Response (200):
[
  {
    "id": 1,
    "title": "Introduction to Python",
    "description": "Learn Python basics"
  },
  {
    "id": 5,
    "title": "Web Development Basics",
    "description": "Learn HTML, CSS, JavaScript"
  }
]


GET /teacher/courses/<course_id>/results
Headers: Authorization: Bearer <token>

Response (200):
[
  {
    "student": "alice@example.com",
    "results": [
      {
        "lesson_id": 10,
        "score": 2,
        "date": "2026-01-10 14:30:00"
      },
      {
        "lesson_id": 11,
        "score": 1,
        "date": "2026-01-10 15:00:00"
      }
    ]
  },
  {
    "student": "bob@example.com",
    "results": [
      {
        "lesson_id": 10,
        "score": 2,
        "date": "2026-01-10 16:00:00"
      }
    ]
  }
]
