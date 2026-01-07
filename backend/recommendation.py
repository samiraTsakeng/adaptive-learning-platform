from backend.database import connect_db, get_lessons_by_course
from data_structures.priority_queue import PriorityQueue

def get_recommendations(username):
    """Recommend lessons with lowest quiz scores first"""
    conn = connect_db()
    cursor = conn.cursor()

    # get user id
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return []
    user_id = row[0]

    # get all lessons and previous scores
    cursor.execute("""
        SELECT l.id, l.title, IFNULL(r.score, 0)
        FROM lessons l
        LEFT JOIN results r ON l.id = r.lesson_id AND r.user_id = ?
    """, (user_id,))
    lessons = cursor.fetchall()
    conn.close()

    # push lessons into priority queue based on score (lower score = higher priority)
    pq = PriorityQueue()
    for lesson_id, title, score in lessons:
        pq.push({"lesson_id": lesson_id, "title": title, "score": score}, priority=-score)

    recommendations = []
    while not pq.is_empty():
        recommendations.append(pq.pop())
    return recommendations
