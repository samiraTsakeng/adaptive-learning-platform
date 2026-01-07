from backend.learning import load_lessons_for_course

def show_lessons(course_id):
    lessons = load_lessons_for_course(course_id)

    if not lessons:
        print("❌ No lessons found for this course.")
        return

    print("\n📘 Lessons:")
    for lesson in lessons:
        print(f"{lesson[0]}. {lesson[1]}")
