"""
Progress CLI - show course completion and lesson pass status.
"""

from backend.database import (
    get_all_courses,
    get_lessons_by_course,
    get_user_id_by_username,
    has_user_passed_lesson,
)


def view_progress_cli(username):
    """Display student progress across all courses."""
    user_id = get_user_id_by_username(username)
    if not user_id:
        print("❌ User not found")
        return

    courses = get_all_courses()
    print(f"\n📊 Progress Report for {username}\n")

    for course_id, course_title, course_desc in courses:
        lessons = get_lessons_by_course(course_id)
        passed = 0
        for lesson in lessons:
            lid = lesson[0]
            if has_user_passed_lesson(user_id, lid):
                passed += 1

        total = len(lessons)
        pct = int(100 * passed / total) if total > 0 else 0
        bar = "█" * (passed * 10 // total) + "░" * ((total - passed) * 10 // total)
        print(f"{course_id}. {course_title}")
        print(f"   Progress: [{bar}] {passed}/{total} ({pct}%)")
        print()

    input("Press Enter to return to dashboard...")
