from data_structures.graph import Graph
from backend.database import connect_db

learning_graph = Graph()

def load_lessons_for_course(course_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title
        FROM lessons
        WHERE course_id = ?
        ORDER BY difficulty
    """, (course_id,))

    lessons = cursor.fetchall()
    conn.close()

    # Build graph (linear progression for now)
    previous_lesson = None
    for lesson_id, title in lessons:
        learning_graph.add_node((lesson_id, title))
        if previous_lesson:
            learning_graph.add_edge(previous_lesson, (lesson_id, title))
        previous_lesson = (lesson_id, title)

    return lessons
