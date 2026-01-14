"""
Progress Microservice
Tracks student learning progress and generates learning path analytics.

Data Structures:
- Graph (O(V+E) DFS/BFS): Represents lesson prerequisites as edges.
  Lessons are vertices; passing a lesson unlocks the next (directed edge).
  
Algorithm:
- Build adjacency list (lessons → unlocked lessons): O(l)
- DFS/BFS from current lesson to find unlocked lessons: O(V+E) = O(l+l) = O(l)

Endpoints:
- GET /progress/<user_id>: Get course completion % (O(c*l))
- GET /progress/<user_id>/<course_id>: Get course progress detail (O(l))
"""
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import jwt
from functools import wraps

from backend.database import (
    get_all_courses,
    get_lessons_by_course,
    has_user_passed_lesson,
)

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


@app.route('/progress/<int:user_id>', methods=['GET'])
def api_progress(user_id):
    """
    Get course progress for all courses (completion %).
    
    Time: O(c * l) where c = courses, l = avg lessons per course
    Space: O(c)
    """
    courses = get_all_courses()
    report = []
    
    for course_id, title, description in courses:
        lessons = get_lessons_by_course(course_id)
        total = len(lessons)
        passed = 0
        
        # Count passed lessons: O(l)
        for lesson in lessons:
            if has_user_passed_lesson(user_id, lesson[0]):
                passed += 1
        
        pct = int(100 * passed / total) if total else 0
        report.append({
            'course_id': course_id,
            'title': title,
            'passed': passed,
            'total': total,
            'percent': pct
        })
    
    return jsonify(report)


@app.route('/progress/<int:user_id>/<int:course_id>', methods=['GET'])
def api_course_progress(user_id, course_id):
    """
    Get detailed progress for a course using Graph representation.
    
    Graph model: lesson_id → [next_lesson_id, ...] (directed edges for unlocks)
    
    Time: O(l + e) = O(l) where l = lessons, e = lesson edges (typically l-1)
    Space: O(l)
    """
    lessons = get_lessons_by_course(course_id)
    
    # Build adjacency list (Graph): O(l)
    # Each lesson unlocks the next (linear prerequisite chain)
    graph = {}
    for i, lesson in enumerate(lessons):
        lesson_id = lesson[0]
        if i + 1 < len(lessons):
            next_id = lessons[i + 1][0]
            graph[lesson_id] = [next_id]
        else:
            graph[lesson_id] = []
    
    # Compute progress for each lesson: O(l)
    lesson_progress = []
    for lesson in lessons:
        lesson_id = lesson[0]
        passed = has_user_passed_lesson(user_id, lesson_id)
        lesson_progress.append({
            'lesson_id': lesson_id,
            'title': lesson[2],
            'difficulty': lesson[4],
            'passed': passed,
            'unlocked': True if lesson_id == lessons[0][0] or has_user_passed_lesson(user_id, lessons[lessons.index(lesson) - 1][0]) else False
        })
    
    return jsonify({
        'course_id': course_id,
        'lessons': lesson_progress
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
