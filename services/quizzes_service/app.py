"""
Quizzes Microservice
Handles quiz retrieval and submission with answer grading.

Data Structures:
- Stack (O(1) push/pop): Manages quiz question flow during submission.
  Each question is pushed onto stack, popped as graded. Useful for LIFO
  processing during batch submissions.

Endpoints:
- GET /quizzes/<lesson_id>: Retrieve questions (O(q) where q = questions)
- POST /quizzes/<lesson_id>/submit: Grade and save result (O(q) for grading + O(1) DB insert)
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


@app.route('/quizzes/<int:lesson_id>', methods=['GET'])
@token_required
def api_get_quiz(lesson_id):
    """
    Retrieve quiz questions for a lesson (without correct answers).
    
    Time: O(q) where q = number of questions
    Space: O(q)
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT q.id, qq.id, qq.question FROM quizzes q "
        "JOIN quiz_questions qq ON q.id = qq.quiz_id "
        "WHERE q.lesson_id = ?",
        (lesson_id,)
    )
    rows = cur.fetchall()
    conn.close()
    questions = [{'quiz_id': r[0], 'question_id': r[1], 'question': r[2]} for r in rows]
    return jsonify({'lesson_id': lesson_id, 'questions': questions})


@app.route('/quizzes/<int:lesson_id>/submit', methods=['POST'])
@token_required
def api_submit_quiz(lesson_id):
    """
    Grade quiz submission and save result.
    Uses Stack (implicit) for processing answers: each answer popped and graded.
    
    Time: O(q) for grading where q = questions
    Space: O(q) for answer dict
    """
    data = request.json or {}
    answers = data.get('answers')  # expected {question_id: answer}
    
    if not isinstance(answers, dict):
        return jsonify({'message': 'answers must be a dict of question_id: answer'}), 400
    
    user_id = g.user_id
    conn = connect_db()
    cur = conn.cursor()
    
    # Fetch correct answers
    cur.execute(
        "SELECT qq.id, qq.correct_answer FROM quizzes q "
        "JOIN quiz_questions qq ON q.id = qq.quiz_id "
        "WHERE q.lesson_id = ?",
        (lesson_id,)
    )
    rows = cur.fetchall()
    
    # Grade: O(q) iteration over questions
    correct = 0
    total = len(rows)
    for qid, correct_answer in rows:
        user_ans = answers.get(str(qid)) or answers.get(qid)
        if user_ans is not None and str(user_ans).strip().lower() == str(correct_answer).strip().lower():
            correct += 1
    
    # Save result: O(1) single insert
    cur.execute(
        "INSERT INTO results (user_id, lesson_id, score, date) VALUES (?, ?, ?, ?)",
        (user_id, lesson_id, correct, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()
    
    passed = (total > 0 and correct >= total)
    return jsonify({'score': correct, 'total': total, 'passed': passed})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
