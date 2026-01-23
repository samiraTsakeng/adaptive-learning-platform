import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "database.db")

def connect_db():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        title TEXT NOT NULL,
        content TEXT,
        difficulty INTEGER,
        FOREIGN KEY(course_id) REFERENCES courses(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_id INTEGER,
        type TEXT,
        FOREIGN KEY(lesson_id) REFERENCES lessons(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER,
        question TEXT,
        correct_answer TEXT,
        FOREIGN KEY(quiz_id) REFERENCES quizzes(id)
    )
    """)
    # ensure we don't insert duplicate question text for the same quiz
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_quiz_question_unique ON quiz_questions(quiz_id, question)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        lesson_id INTEGER,
        score INTEGER,
        date TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(lesson_id) REFERENCES lessons(id)
    )
    """)

    

    conn.commit()
    conn.close()


def get_all_courses():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description FROM courses")
    courses = cursor.fetchall()
    conn.close()
    return courses


def get_course_by_id(course_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description FROM courses WHERE id = ?", (course_id,))
    course = cursor.fetchone()
    conn.close()
    return course


def get_lessons_by_course(course_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, content, difficulty FROM lessons WHERE course_id = ? ORDER BY id",
        (course_id,)
    )
    lessons = cursor.fetchall()
    conn.close()
    return lessons


def get_lesson_by_id(lesson_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, course_id, title, content, difficulty FROM lessons WHERE id = ?",
        (lesson_id,)
    )
    lesson = cursor.fetchone()
    conn.close()
    return lesson


def get_quiz_id_for_lesson(lesson_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM quizzes WHERE lesson_id = ?", (lesson_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def get_question_count_for_lesson(lesson_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM quiz_questions qq JOIN quizzes q ON qq.quiz_id = q.id WHERE q.lesson_id = ?", (lesson_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


def get_user_id_by_username(username):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def get_user_info_by_username(username):
    """Return (id, role) for the given username or (None, None)."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, role FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None, None
    return row[0], row[1]


def get_user_max_score_for_lesson(user_id, lesson_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT MAX(score) FROM results WHERE user_id = ? AND lesson_id = ?", (user_id, lesson_id))
    row = cur.fetchone()
    conn.close()
    return row[0] if row and row[0] is not None else None


def has_user_passed_lesson(user_id, lesson_id, pass_ratio=1.0):
    """Return True if the user's best score for the lesson meets the pass ratio (fraction)."""
    total = get_question_count_for_lesson(lesson_id)
    if total == 0:
        return True
    best = get_user_max_score_for_lesson(user_id, lesson_id)
    if best is None:
        return False
    required = int(total * pass_ratio)
    # ensure at least 1 required if pass_ratio > 0 and total>0
    if pass_ratio > 0 and required == 0:
        required = 1
    return best >= required


if __name__ == "__main__":
    create_tables()
    print("✅ Database initialized successfully")
