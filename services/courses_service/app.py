from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import jwt
from functools import wraps

from backend.database import (
    get_all_courses,
    get_course_by_id,
    get_lessons_by_course,
    get_lesson_by_id,
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


@app.route('/courses', methods=['GET'])
def api_courses():
    courses = get_all_courses()
    data = [{'id': c[0], 'title': c[1], 'description': c[2]} for c in courses]
    return jsonify(data)


@app.route('/courses/<int:course_id>', methods=['GET'])
def api_course_detail(course_id):
    course = get_course_by_id(course_id)
    if not course:
        return jsonify({'message': 'Course not found'}), 404
    lessons = get_lessons_by_course(course_id)
    lessons_data = [{'id': l[0], 'title': l[1], 'difficulty': l[3]} for l in lessons]
    return jsonify({'id': course[0], 'title': course[1], 'description': course[2], 'lessons': lessons_data})


@app.route('/courses/<int:course_id>/lessons', methods=['GET'])
def api_course_lessons(course_id):
    lessons = get_lessons_by_course(course_id)
    data = [{'id': l[0], 'title': l[1], 'content': l[2], 'difficulty': l[4] if len(l) > 4 else None} for l in lessons]
    return jsonify(data)


@app.route('/lessons/<int:lesson_id>', methods=['GET'])
@token_required
def api_lesson_detail(lesson_id):
    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        return jsonify({'message': 'Lesson not found'}), 404
    user_id = g.user_id
    course_id = lesson[1]
    lessons = get_lessons_by_course(course_id)
    locked = False
    ids = [l[0] for l in lessons]
    try:
        idx = ids.index(lesson_id)
        if idx > 0:
            prev_id = ids[idx - 1]
            if not has_user_passed_lesson(user_id, prev_id):
                locked = True
    except ValueError:
        pass
    return jsonify({'id': lesson[0], 'title': lesson[2], 'content': lesson[3], 'difficulty': lesson[4], 'locked': locked})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
