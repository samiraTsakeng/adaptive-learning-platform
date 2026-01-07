from backend.database import connect_db, get_lesson_by_id

def view_results_cli(username):
    """Display all previous quiz results for the logged-in student."""
    conn = connect_db()
    cursor = conn.cursor()

    # get user id
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        print("❌ User not found.")
        conn.close()
        return
    user_id = row[0]

    # fetch results
    cursor.execute("""
        SELECT lesson_id, score, date
        FROM results
        WHERE user_id = ?
        ORDER BY date DESC
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()

    if not results:
        print("ℹ  No quiz results found yet.")
        return

    print("\n Your Quiz Results:")
    for lesson_id, score, date in results:
        lesson = get_lesson_by_id(lesson_id)
        lesson_title = lesson[2] if lesson else "Unknown Lesson"
        print(f"- {lesson_title}: {score} points on {date}")
