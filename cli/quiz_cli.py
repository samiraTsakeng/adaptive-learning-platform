from backend.quiz_engine import QuizEngine
from backend.database import get_lesson_by_id, connect_db

def start_quiz_cli(lesson_id, username):
    lesson = get_lesson_by_id(int(lesson_id))
    if not lesson:
        print("❌ Lesson not found")
        return 0

    print(f"\n📝 Starting quiz for lesson: {lesson[2]}\n")

    quiz = QuizEngine(lesson_id)

    while quiz.has_next():
        current = quiz.get_next_question()
        print(f"Question: {current['question']}")
        answer = input("Your answer: ")
        quiz.answer_current(answer)
        print()

    score = quiz.calculate_score()
    print(f"✅ Quiz finished! Your score: {score}")

    # Save result to database
    save_result(username, lesson_id, score)
    return score

def save_result(username, lesson_id, score):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        print("❌ Cannot save result: user not found")
        conn.close()
        return
    user_id = row[0]

    from datetime import datetime
    cursor.execute("""
        INSERT INTO results (user_id, lesson_id, score, date)
        VALUES (?, ?, ?, ?)
    """, (user_id, lesson_id, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    print("✅ Result saved successfully!")
