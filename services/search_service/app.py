"""
Search Microservice
Full-text search across courses and lessons using Trie data structure.

Data Structures:
- Trie (O(m) search where m = query length): Efficiently finds courses/lessons
  by prefix matching. Supports fast auto-complete and partial matching.

Endpoints:
- GET /search?q=<query>: Search courses and lessons (O(m + n) where n = results)
"""
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import jwt
from functools import wraps

from backend.database import (
    connect_db,
    get_lessons_by_course,
)
from backend.search import search_courses, search_lessons

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


@app.route('/search', methods=['GET'])
def api_search():
    """
    Search for courses and lessons by query string.
    Uses Trie for efficient prefix matching.
    
    Algorithm:
    1. Parse query: O(1)
    2. Search courses (Trie): O(m) where m = query length
    3. Search lessons (Trie): O(m)
    4. For each course, fetch lessons: O(c * l) where c = courses, l = avg lessons
    
    Time: O(m + c*l + results_lessons) ≈ O(m + n) where n = result set
    Space: O(n)
    """
    q = request.args.get('q', '').strip()
    
    if not q:
        return jsonify({'courses': [], 'lessons': []})
    
    # Trie-based search (backend.search uses character-by-character matching)
    courses = search_courses(q)  # O(m)
    lessons = search_lessons(q)  # O(m)
    
    # Build course entries with lessons: O(c * l)
    courses_out = []
    for course_id, title, description in courses:
        lessons_data = get_lessons_by_course(course_id)
        lessons_list = [{'id': lm[0], 'title': lm[1], 'content': lm[2], 'difficulty': lm[3]} for lm in lessons_data]
        courses_out.append({
            'id': course_id,
            'title': title,
            'description': description,
            'lessons': lessons_list
        })
    
    # Format lessons: O(r) where r = result lessons
    lessons_out = [{'id': x[0], 'title': x[1], 'course_id': x[2]} for x in lessons]
    
    return jsonify({'courses': courses_out, 'lessons': lessons_out})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
