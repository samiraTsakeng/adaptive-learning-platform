"""
Recommendations Microservice
Generates personalized learning recommendations for students.

Data Structures:
- PriorityQueue (O(n) push, O(log n) pop ideal): Prioritizes lessons by
  student's best scores and difficulty. Current impl uses manual sort O(n),
  could upgrade to heap-based O(log n) extraction.

Endpoints:
- GET /recommendations/<user_id>/<course_id>: Get recommended lessons (O(n log n))
"""
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import jwt
from functools import wraps

from backend.database import connect_db, has_user_passed_lesson

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


@app.route('/recommendations/<int:user_id>/<int:course_id>', methods=['GET'])
@token_required
def api_recommendations(user_id, course_id):
    """
    Generate recommendations for a student in a course.
    Uses PriorityQueue logic: sort lessons by score (priority).
    
    Algorithm:
    1. Fetch all lessons in course: O(l) where l = lessons
    2. For each lesson, get best score: O(l * q) where q = results per lesson
    3. Sort by score descending: O(l log l) [PriorityQueue heap insert O(l log l)]
    
    Time: O(l * q + l log l) ≈ O(l log l) for typical q
    Space: O(l)
    """
    conn = connect_db()
    cur = conn.cursor()
    
    # Get all lessons in course
    cur.execute("SELECT id, title FROM lessons WHERE course_id = ?", (course_id,))
    lessons = cur.fetchall()
    
    recommendations = []
    for lesson_id, lesson_title in lessons:
        # Check if already passed
        if has_user_passed_lesson(user_id, lesson_id):
            continue
        
        # Get best score for this lesson
        cur.execute(
            "SELECT MAX(score) as best_score, COUNT(*) as attempts "
            "FROM results WHERE user_id = ? AND lesson_id = ?",
            (user_id, lesson_id)
        )
        row = cur.fetchone()
        best_score = row[0] if row[0] is not None else 0
        attempts = row[1] if row[1] is not None else 0
        
        # Get total questions
        cur.execute(
            "SELECT COUNT(*) FROM quiz_questions WHERE quiz_id = "
            "(SELECT id FROM quizzes WHERE lesson_id = ?)",
            (lesson_id,)
        )
        total_q = cur.fetchone()[0]
        
        # Priority: higher score = higher priority (recommend next step or retry)
        recommendations.append({
            'lesson_id': lesson_id,
            'title': lesson_title,
            'best_score': best_score,
            'total_q': total_q,
            'attempts': attempts,
            'priority': best_score  # used for sorting
        })
    
    conn.close()
    
    # Sort by priority descending (PriorityQueue pop-max): O(l log l)
    recommendations.sort(key=lambda x: x['priority'], reverse=True)
    
    # Return without priority field (internal only)
    return jsonify([
        {'lesson_id': r['lesson_id'], 'title': r['title'], 'best_score': r['best_score'], 'total_q': r['total_q'], 'attempts': r['attempts']}
        for r in recommendations
    ])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
