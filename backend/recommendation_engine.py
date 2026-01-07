"""
Recommendation engine using Priority Queue.

Time Complexity:
  - get_student_recommendations(user_id, course_id): O(m log m) where m = lessons in course
  
Uses Priority Queue to rank lessons by (score / max_score) ratio.
"""

from data_structures.priority_queue import PriorityQueue
from backend.database import (
    connect_db,
    get_lessons_by_course,
    get_user_max_score_for_lesson,
    get_question_count_for_lesson,
)


def get_student_recommendations(user_id, course_id):
    """
    Get recommended lessons for a student in a course, ranked by performance.
    
    Lessons with lower scores are recommended (need more practice).
    Returns list of (lesson_id, lesson_title, current_score, max_questions).
    
    Time: O(m log m) where m = lessons in course (due to PQ operations)
    Space: O(m)
    """
    lessons = get_lessons_by_course(course_id)
    pq = PriorityQueue()

    for lesson in lessons:
        lesson_id = lesson[0]
        lesson_title = lesson[1]
        max_q = get_question_count_for_lesson(lesson_id)
        best_score = get_user_max_score_for_lesson(user_id, lesson_id)

        # If no score yet, prioritize (score 0)
        if best_score is None:
            best_score = 0

        # Priority = negative score (so low scores come first)
        # This makes lessons with lower scores higher priority
        priority = best_score if best_score > 0 else -1  # -1 for untouched lessons
        pq.push((lesson_id, lesson_title, best_score, max_q), priority)

    recommendations = []
    while not pq.is_empty():
        recommendations.append(pq.pop())

    return recommendations
