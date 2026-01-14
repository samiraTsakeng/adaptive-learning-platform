"""
Teacher Service
Handles course authoring, uploading, and student result analytics.

Data Structures:
- HashTable (O(1) avg lookup): Caches teacher info and their courses.
  On teacher login, store teacher_id → [courses] in HashTable for fast access.

Endpoints:
- POST /teacher/upload: Upload new course (O(l*q) inserts)
- GET /teacher/courses: List teacher's courses (O(c) with HashTable cache O(1) ideal)
- GET /teacher/courses/<id>/results: Get student results (O(s*l) where s=students, l=lessons)
"""
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import jwt
from functools import wraps
from datetime import datetime

from backend.database import connect_db

SECRET_KEY = os.environ.get('ALP_SECRET', 'change_this_secret')
JWT_ALGORITHM = 'HS256'

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = SECRET_KEY


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth = request.headers.get('Authorization')
            parts = auth.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            token_str = token.strip()
            if (token_str.startswith('"') and token_str.endswith('"')) or (token_str.startswith("'") and token_str.endswith("'")):
                token_str = token_str[1:-1]
            if token_str.startswith("b'") and token_str.endswith("'"):
                token_str = token_str[2:-1]
            if token_str.startswith('b"') and token_str.endswith('"'):
                token_str = token_str[2:-1]
            payload = jwt.decode(token_str, app.config['SECRET_KEY'], algorithms=[JWT_ALGORITHM])
            g.user_id = payload.get('user_id')
            g.username = payload.get('username')
            g.role = payload.get('role')
        except Exception as e:
            return jsonify({'message': 'Token is invalid', 'error': str(e)}), 401
        return f(*args, **kwargs)
    return decorated


def teacher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not getattr(g, 'user_id', None):
            return jsonify({'message': 'Authentication required'}), 401
        if getattr(g, 'role', None) != 'teacher':
            return jsonify({'message': 'Teacher role required'}), 403
        return f(*args, **kwargs)
    return decorated


@app.route('/teacher/upload', methods=['POST'])
@token_required
@teacher_required
def api_teacher_upload():
    """
    Upload and insert a new course package.
    
    Expected JSON:
    {
      "title": "Course title",
      "description": "...",
      "lessons": [
         {"title": "Lesson 1", "content": "...", "difficulty": 1,
          "quiz": [{"question": "...", "correct_answer": "..."}, ...]},
         ...
      ]
    }
    
    Time: O(l*q) where l = lessons, q = avg questions per lesson
    Space: O(1) (streaming inserts, no in-memory accumulation)
    """
    data = request.json or {}
    title = data.get('title')
    description = data.get('description', '')
    lessons = data.get('lessons', [])
    
    if not title or not isinstance(lessons, list):
        return jsonify({'success': False, 'message': 'Invalid package format'}), 400
    
    conn = connect_db()
    cur = conn.cursor()
    try:
        # Insert course: O(1)
        cur.execute(
            "INSERT INTO courses (title, description) VALUES (?, ?)",
            (title, description)
        )
        course_id = cur.lastrowid
        
        # Insert lessons and quizzes: O(l*q)
        for lesson in lessons:
            l_title = lesson.get('title')
            content = lesson.get('content', '')
            difficulty = lesson.get('difficulty', 1)
            
            cur.execute(
                "INSERT INTO lessons (course_id, title, content, difficulty) VALUES (?, ?, ?, ?)",
                (course_id, l_title, content, difficulty)
            )
            lesson_id = cur.lastrowid
            
            # Create quiz for lesson: O(1)
            cur.execute("INSERT INTO quizzes (lesson_id) VALUES (?)", (lesson_id,))
            quiz_id = cur.lastrowid
            
            # Insert questions: O(q)
            for q in lesson.get('quiz', []):
                qtext = q.get('question')
                correct = q.get('correct_answer', '')
                if qtext:
                    cur.execute(
                        "INSERT INTO quiz_questions (quiz_id, question, correct_answer) VALUES (?, ?, ?)",
                        (quiz_id, qtext, correct)
                    )
        
        conn.commit()
        return jsonify({'success': True, 'course_id': course_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()


@app.route('/teacher/courses', methods=['GET'])
@token_required
@teacher_required
def api_teacher_courses():
    """
    List all courses (currently all courses; can be extended with teacher_id tracking).
    
    Time: O(c) where c = total courses
    Space: O(c)
    
    With HashTable cache: O(1) ideal if teacher courses cached
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description FROM courses")
    courses = cur.fetchall()
    conn.close()
    
    data = [{'id': c[0], 'title': c[1], 'description': c[2]} for c in courses]
    return jsonify(data)


@app.route('/teacher/courses/<int:course_id>/results', methods=['GET'])
@token_required
@teacher_required
def api_teacher_results(course_id):
    """
    Get student results for a course, grouped by student.
    
    Time: O(s * l) where s = students, l = lessons in course
           Breakdown: O(l) lessons fetch + O(r) results fetch + O(s log s) grouping sort
    Space: O(r) where r = total results
    """
    conn = connect_db()
    cur = conn.cursor()
    
    # Get all lessons in course: O(l)
    cur.execute("SELECT id FROM lessons WHERE course_id = ? ORDER BY id", (course_id,))
    lesson_ids = [row[0] for row in cur.fetchall()]
    
    if not lesson_ids:
        conn.close()
        return jsonify([])
    
    # Get all results for these lessons: O(r)
    placeholders = ','.join('?' * len(lesson_ids))
    cur.execute(
        f"SELECT u.username, r.lesson_id, r.score, r.date FROM results r "
        f"JOIN users u ON r.user_id = u.id "
        f"WHERE r.lesson_id IN ({placeholders}) "
        f"ORDER BY u.username, r.lesson_id, r.date DESC",
        lesson_ids
    )
    
    results = cur.fetchall()
    conn.close()
    
    # Group by student: O(s log s) for sort, O(r) for iteration
    student_results = {}
    for username, lesson_id, score, date in results:
        if username not in student_results:
            student_results[username] = []
        student_results[username].append({
            'lesson_id': lesson_id,
            'score': score,
            'date': date
        })
    
    data = [{'student': username, 'results': res} for username, res in student_results.items()]
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)
