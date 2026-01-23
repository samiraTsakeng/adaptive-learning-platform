from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import jwt
from functools import wraps
from datetime import datetime, timedelta

from backend.database import (
    connect_db,
    get_all_courses,
    get_course_by_id,
    get_lessons_by_course,
    get_lesson_by_id,
    has_user_passed_lesson,
    get_user_info_by_username
)

from backend.auth import register_user, login_user
from backend.search import search_courses, search_lessons
from backend.recommendation_engine import get_student_recommendations

SECRET_KEY = os.environ.get("ALP_SECRET", "change_this_secret")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_HOURS = 24

app = Flask(__name__)

# ✅ FIXED CORS
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

app.config["SECRET_KEY"] = SECRET_KEY

# ================= AUTH HELPERS =================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            parts = request.headers.get("Authorization").split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        if not token:
            return jsonify({"message": "Token missing"}), 401

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=[JWT_ALGORITHM])
            g.user_id = payload["user_id"]
            g.username = payload["username"]
            g.role = payload["role"]
        except Exception as e:
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated


def teacher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.role != "teacher":
            return jsonify({"message": "Teacher role required"}), 403
        return f(*args, **kwargs)
    return decorated

# ================= AUTH =================

@app.route("/auth/register", methods=["POST"])
def api_register():
    data = request.json or {}
    success, msg = register_user(
        data.get("username"),
        data.get("password"),
        data.get("role", "student")
    )
    if success:
        return jsonify({"success": True}), 201
    return jsonify({"success": False, "message": msg}), 400


@app.route("/auth/login", methods=["POST"])
def api_login():
    data = request.json or {}
    success, msg = login_user(data.get("username"), data.get("password"))
    if not success:
        return jsonify({"message": msg}), 401

    user_id, role = get_user_info_by_username(data.get("username"))
    payload = {
        "user_id": user_id,
        "username": data.get("username"),
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXP_DELTA_HOURS)
    }
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm=JWT_ALGORITHM)
    return jsonify({"token": token, "role": role})

# ================= COURSES =================

@app.route("/courses", methods=["GET"])
def api_courses():
    return jsonify([
        {"id": c[0], "title": c[1], "description": c[2]}
        for c in get_all_courses()
    ])


@app.route("/courses", methods=["POST"])
@token_required
@teacher_required
def api_create_course():
    data = request.json
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO courses (title, description) VALUES (?, ?)",
        (data["title"], data.get("description", ""))
    )
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return jsonify({"id": cid}), 201

# ================= LESSONS =================

@app.route("/courses/<int:course_id>/lessons", methods=["GET"])
@token_required
def api_get_lessons(course_id):
    lessons = get_lessons_by_course(course_id)

    result = []
    for l in lessons:
        passed = has_user_passed_lesson(g.user_id, l[0])
        result.append({
            "id": l[0],
            "title": l[1],
            "content": l[2],
            "difficulty": l[3],
            "locked": not passed
        })

    return jsonify(result)


@app.route("/courses/<int:course_id>/lessons", methods=["POST"])
@token_required
@teacher_required
def api_create_lesson(course_id):
    data = request.json
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO lessons (course_id, title, content, difficulty) VALUES (?, ?, ?, ?)",
        (course_id, data["title"], data["content"], data.get("difficulty", 1))
    )
    conn.commit()
    lid = cur.lastrowid
    conn.close()
    return jsonify({"id": lid}), 201


@app.route("/courses/<int:course_id>/lessons/<int:lesson_id>", methods=["GET"])
@token_required
def api_get_single_lesson(course_id, lesson_id):
    lesson = get_lesson_by_id(lesson_id)
    if not lesson or lesson[1] != course_id:
        return jsonify({"message": "Lesson not found"}), 404

    return jsonify({
        "id": lesson[0],
        "course_id": lesson[1],
        "title": lesson[2],
        "content": lesson[3],
        "difficulty": lesson[4]
    })

# ================= QUIZ =================

@app.route("/lessons/<int:lesson_id>/quiz", methods=["POST"])
@token_required
@teacher_required
def api_create_quiz(lesson_id):
    data = request.json
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO quizzes (lesson_id) VALUES (?)", (lesson_id,))
    quiz_id = cur.lastrowid

    for q in data["questions"]:
        correct = (
            f"{q['correctLetter']}|{q['correctText']}"
            if data["type"] == "MCQ"
            else q["correctText"]
        )
        cur.execute(
            "INSERT INTO quiz_questions (quiz_id, question, correct_answer) VALUES (?, ?, ?)",
            (quiz_id, q["question"], correct)
        )

    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/quizzes/<int:lesson_id>", methods=["GET"])
@token_required
def api_get_quiz(lesson_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT id FROM quizzes WHERE lesson_id = ?", (lesson_id,))
    quiz = cur.fetchone()
    
    if not quiz:
        cur.execute("INSERT INTO quizzes (lesson_id) VALUES (?)", (lesson_id,))
        conn.commit()
        quiz_id = cur.lastrowid
    else:
        quiz_id = quiz[0]

    cur.execute("""
        SELECT id, question
        FROM quiz_questions 
        WHERE quiz_id = ?
    """, (quiz_id,))

    questions = [{"question_id": row[0], "question": row[1]}
                  for row in cur.fetchall()]
    conn.close()
    return jsonify({"questions": questions})


@app.route("/quizzes/<int:lesson_id>/submit", methods=["POST"])
@token_required
def api_submit_quiz(lesson_id):
    answers = request.json["answers"]
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT qq.id, qq.correct_answer
        FROM quizzes q
        JOIN quiz_questions qq ON q.id = qq.quiz_id
        WHERE q.lesson_id = ?
    """, (lesson_id,))
    rows = cur.fetchall()

    if not rows:
        return jsonify({"message": "Quiz not found"}), 404

    score = 0
    for qid, correct in rows:
        user_ans = answers.get(str(qid), "")
        if "|" in correct:
            l, t = correct.split("|", 1)
            if user_ans.upper() == l or user_ans.lower() == t.lower():
                score += 1
        else:
            if user_ans.lower() == correct.lower():
                score += 1

    cur.execute(
        "INSERT INTO results (user_id, lesson_id, score, date) VALUES (?, ?, ?, ?)",
        (g.user_id, lesson_id, score, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()
    return jsonify({"score": score, "total": len(rows), "passed": score == len(rows)})

# ================= PROGRESS =================

@app.route("/progress", methods=["GET"])
@token_required
def api_progress():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.title,
               COUNT(l.id) as total,
               SUM(
                 CASE WHEN r.score IS NOT NULL THEN 1 ELSE 0 END
               ) as passed
        FROM courses c
        LEFT JOIN lessons l ON l.course_id = c.id
        LEFT JOIN results r ON r.lesson_id = l.id AND r.user_id = ?
        GROUP BY c.id
    """, (g.user_id,))

    data = []
    for row in cur.fetchall():
        percent = int((row[3] / row[2]) * 100) if row[2] else 0
        data.append({
            "course_id": row[0],
            "title": row[1],
            "total": row[2],
            "passed": row[3] or 0,
            "percent": percent
        })

    conn.close()
    return jsonify(data)

# Add this route after the existing routes in app.py

@app.route("/teacher/upload", methods=["POST"])
@token_required
@teacher_required
def api_upload_course():
    """
    Upload a course with lessons and quizzes
    Expected JSON structure:
    {
        "title": "Course title",
        "description": "Course description",
        "lessons": [
            {
                "title": "Lesson title",
                "content": "Lesson content",
                "difficulty": 1,
                "quiz": [
                    {
                        "question": "Question text",
                        "correct_answer": "Correct answer"
                    }
                ]
            }
        ]
    }
    """
    data = request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400
    
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        # Create course
        cur.execute(
            "INSERT INTO courses (title, description) VALUES (?, ?)",
            (data["title"], data.get("description", ""))
        )
        course_id = cur.lastrowid
        
        # Create lessons with quizzes
        for lesson_data in data.get("lessons", []):
            cur.execute(
                """INSERT INTO lessons 
                (course_id, title, content, difficulty) 
                VALUES (?, ?, ?, ?)""",
                (course_id, lesson_data["title"], 
                 lesson_data["content"], lesson_data.get("difficulty", 1))
            )
            lesson_id = cur.lastrowid
            
            # Create quiz for this lesson if questions exist
            quiz_questions = lesson_data.get("quiz", [])
            if quiz_questions:
                cur.execute(
                    "INSERT INTO quizzes (lesson_id) VALUES (?)",
                    (lesson_id,)
                )
                quiz_id = cur.lastrowid
                
                for question_data in quiz_questions:
                    cur.execute(
                        """INSERT INTO quiz_questions 
                        (quiz_id, question, correct_answer) 
                        VALUES (?, ?, ?)""",
                        (quiz_id, question_data["question"], 
                         question_data["correct_answer"])
                    )
        
        conn.commit()
        return jsonify({
            "success": True,
            "course_id": course_id,
            "message": "Course uploaded successfully"
        }), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            "success": False,
            "message": f"Upload failed: {str(e)}"
        }), 500
        
    finally:
        conn.close()

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True, port=5000)