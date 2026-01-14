from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import jwt
from functools import wraps
from datetime import datetime, timedelta

# Import existing backend logic
from backend.database import (
    get_all_courses,
    get_course_by_id,
    get_lessons_by_course,
    get_lesson_by_id,
    get_quiz_id_for_lesson,
    connect_db,
    get_question_count_for_lesson,
    get_user_id_by_username,
    get_user_info_by_username,
    has_user_passed_lesson,
)
from backend.search import search_courses, search_lessons
from backend.recommendation_engine import get_student_recommendations
from backend.auth import register_user, login_user

# Configuration
SECRET_KEY = os.environ.get('ALP_SECRET', 'change_this_secret')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_HOURS = 24

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
            # normalize token type and remove accidental quoting or b'' prefixes
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            token_str = token.strip()
            # remove surrounding quotes if present
            if (token_str.startswith("\"") and token_str.endswith("\"")) or (token_str.startswith("'") and token_str.endswith("'")):
                token_str = token_str[1:-1]
            # handle accidental Python bytes repr like b'xxx'
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
        # must be authenticated and have role 'teacher'
        if not getattr(g, 'user_id', None):
            return jsonify({'message': 'Authentication required'}), 401
        if getattr(g, 'role', None) != 'teacher':
            return jsonify({'message': 'Teacher role required'}), 403
        return f(*args, **kwargs)
    return decorated


@app.route('/auth/register', methods=['POST'])
def api_register():
    """Register a new student. Teachers require admin token."""
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    requested_role = data.get('role', 'student')
    admin_token = data.get('admin_token')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'username and password required'}), 400
    
    # Only allow student registration by default; teachers need admin approval
    role = 'student'
    if requested_role == 'teacher':
        if not admin_token or admin_token != os.environ.get('ADMIN_TOKEN', 'admin_secret'):
            return jsonify({'success': False, 'message': 'Admin token required for teacher registration'}), 403
        role = 'teacher'
    
    success, msg = register_user(username, password, role)
    if success:
        return jsonify({'success': True, 'message': msg, 'role': role}), 201
    return jsonify({'success': False, 'message': msg}), 400


@app.route('/auth/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'success': False, 'message': 'username and password required'}), 400
    success, result = login_user(username, password)
    if not success:
        return jsonify({'success': False, 'message': result}), 401
    # create token including role
    user_id, role = get_user_info_by_username(username)
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXP_DELTA_HOURS)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm=JWT_ALGORITHM)
    # ensure token is a native string (PyJWT may return bytes in some environments)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return jsonify({'success': True, 'token': token, 'user_id': user_id, 'role': role})


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
    # determine locked status for this user
    user_id = g.user_id
    # get course id for lesson and check previous lesson
    course_id = lesson[1]
    lessons = get_lessons_by_course(course_id)
    locked = False
    # find index
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


@app.route('/quizzes/<int:lesson_id>', methods=['GET'])
@token_required
def api_get_quiz(lesson_id):
    # return questions but not correct answers
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT q.id, qq.id, qq.question FROM quizzes q JOIN quiz_questions qq ON q.id = qq.quiz_id WHERE q.lesson_id = ?", (lesson_id,))
    rows = cur.fetchall()
    conn.close()
    questions = [{'quiz_id': r[0], 'question_id': r[1], 'question': r[2]} for r in rows]
    return jsonify({'lesson_id': lesson_id, 'questions': questions})


@app.route('/quizzes/<int:lesson_id>/submit', methods=['POST'])
@token_required
def api_submit_quiz(lesson_id):
    data = request.json or {}
    answers = data.get('answers')  # expected {question_id: answer}
    if not isinstance(answers, dict):
        return jsonify({'message': 'answers must be a dict of question_id: answer'}), 400
    user_id = g.user_id
    # grade
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT qq.id, qq.correct_answer FROM quizzes q JOIN quiz_questions qq ON q.id = qq.quiz_id WHERE q.lesson_id = ?", (lesson_id,))
    rows = cur.fetchall()
    correct = 0
    total = len(rows)
    for qid, correct_answer in rows:
        user_ans = answers.get(str(qid)) or answers.get(qid)
        if user_ans is not None and str(user_ans).strip().lower() == str(correct_answer).strip().lower():
            correct += 1
    # save result
    from datetime import datetime
    cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    # insert into results
    cur.execute("INSERT INTO results (user_id, lesson_id, score, date) VALUES (?, ?, ?, ?)", (user_id, lesson_id, correct, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    passed = (total > 0 and correct >= total)
    return jsonify({'score': correct, 'total': total, 'passed': passed})


@app.route('/results/<int:user_id>', methods=['GET'])
def api_results(user_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT lesson_id, score, date FROM results WHERE user_id = ? ORDER BY date DESC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    data = []
    for lesson_id, score, date in rows:
        data.append({'lesson_id': lesson_id, 'score': score, 'date': date})
    return jsonify(data)


@app.route('/search', methods=['GET'])
def api_search():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'courses': [], 'lessons': []})
    c = search_courses(q)
    l = search_lessons(q)
    # Build course entries and include their lessons
    courses_out = []
    for course_id, title, description in c:
        lessons = get_lessons_by_course(course_id)
        lessons_data = [{'id': lm[0], 'title': lm[1], 'content': lm[2], 'difficulty': lm[3]} for lm in lessons]
        courses_out.append({'id': course_id, 'title': title, 'description': description, 'lessons': lessons_data})

    lessons_out = [{'id': x[0], 'title': x[1], 'course_id': x[2]} for x in l]
    return jsonify({'courses': courses_out, 'lessons': lessons_out})


@app.route('/recommendations/<int:user_id>/<int:course_id>', methods=['GET'])
def api_recommendations(user_id, course_id):
    recs = get_student_recommendations(user_id, course_id)
    # recs are tuples (lesson_id, lesson_title, best_score, total_q)
    return jsonify([{'lesson_id': r[0], 'title': r[1], 'best_score': r[2], 'total_q': r[3]} for r in recs])


@app.route('/progress/<int:user_id>', methods=['GET'])
def api_progress(user_id):
    courses = get_all_courses()
    report = []
    for course_id, title, _ in courses:
        lessons = get_lessons_by_course(course_id)
        total = len(lessons)
        passed = 0
        for lesson in lessons:
            if has_user_passed_lesson(user_id, lesson[0]):
                passed += 1
        pct = int(100 * passed / total) if total else 0
        report.append({'course_id': course_id, 'title': title, 'passed': passed, 'total': total, 'percent': pct})
    return jsonify(report)


@app.route('/teacher/upload', methods=['POST'])
@token_required
@teacher_required
def api_teacher_upload():
    """Accept a course package JSON and insert into DB.

    Expected JSON shape:
    {
      "title": "Course title",
      "description": "...",
      "lessons": [
         {"title": "Lesson 1", "content": "...", "difficulty": 1, "quiz": [{"question": "...", "correct_answer": "..."}, ...]},
         ...
      ]
    }
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
        # insert course
        cur.execute("INSERT INTO courses (title, description) VALUES (?, ?)", (title, description))
        course_id = cur.lastrowid

        for lesson in lessons:
            l_title = lesson.get('title')
            content = lesson.get('content', '')
            difficulty = lesson.get('difficulty', 1)
            cur.execute("INSERT INTO lessons (course_id, title, content, difficulty) VALUES (?, ?, ?, ?)", (course_id, l_title, content, difficulty))
            lesson_id = cur.lastrowid

            # create quiz for lesson
            cur.execute("INSERT INTO quizzes (lesson_id) VALUES (?)", (lesson_id,))
            quiz_id = cur.lastrowid

            for q in lesson.get('quiz', []):
                qtext = q.get('question')
                correct = q.get('correct_answer', '')
                if qtext:
                    cur.execute("INSERT INTO quiz_questions (quiz_id, question, correct_answer) VALUES (?, ?, ?)", (quiz_id, qtext, correct))

        conn.commit()
        return jsonify({'success': True, 'course_id': course_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()


@app.route('/teacher/courses', methods=['GET'])
@token_required
@teacher_required
def api_teacher_courses():
    """List all courses created by the logged-in teacher.
    
    Time: O(c) where c = number of courses
    Space: O(c)
    """
    conn = connect_db()
    cur = conn.cursor()
    # For now, return all courses (in future, add teacher_id column to track ownership)
    cur.execute("SELECT id, title, description FROM courses")
    courses = cur.fetchall()
    conn.close()
    data = [{'id': c[0], 'title': c[1], 'description': c[2]} for c in courses]
    return jsonify(data)


@app.route('/teacher/courses/<int:course_id>/results', methods=['GET'])
@token_required
@teacher_required
def api_teacher_results(course_id):
    """Get student results for a specific course.
    
    Time: O(s * l) where s = students, l = lessons in course
    Space: O(r) where r = results
    """
    conn = connect_db()
    cur = conn.cursor()
    
    # Get all lessons in the course
    cur.execute("SELECT id FROM lessons WHERE course_id = ? ORDER BY id", (course_id,))
    lesson_ids = [row[0] for row in cur.fetchall()]
    
    if not lesson_ids:
        conn.close()
        return jsonify([])
    
    # Get all results for these lessons
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
    
    # Format results grouped by student
    student_results = {}
    for username, lesson_id, score, date in results:
        if username not in student_results:
            student_results[username] = []
        student_results[username].append({'lesson_id': lesson_id, 'score': score, 'date': date})
    
    # Convert to array of objects
    data = [{'student': username, 'results': res} for username, res in student_results.items()]
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
