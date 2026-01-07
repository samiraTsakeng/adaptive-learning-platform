"""
Recommendations CLI using Priority Queue ranking.
"""

from backend.recommendation_engine import get_student_recommendations
from backend.database import get_all_courses, get_user_id_by_username


def show_recommendations_cli(username):
    """Display adaptive recommendations for the student across courses."""
    user_id = get_user_id_by_username(username)
    if not user_id:
        print("❌ User not found")
        return

    courses = get_all_courses()
    print(f"\n⭐ Recommended Lessons for {username}\n")

    for course_id, course_title, _ in courses:
        print(f"📚 {course_title}:")
        recommendations = get_student_recommendations(user_id, course_id)

        if not recommendations:
            print("  No lessons yet.")
            continue

        for i, (lesson_id, lesson_title, score, total_q) in enumerate(recommendations[:3], 1):
            if score == 0:
                status = "Not Started"
            else:
                pct = int(100 * score / total_q) if total_q > 0 else 0
                status = f"Incomplete ({score}/{total_q}, {pct}%)"
            print(f"  {i}. {lesson_title} — {status}")
        print()

    input("Press Enter to return to dashboard...")
