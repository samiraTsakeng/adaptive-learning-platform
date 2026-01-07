from backend.database import (
    get_all_courses,
    get_course_by_id,
    get_lessons_by_course,
    get_lesson_by_id,
    get_question_count_for_lesson,
    get_user_id_by_username,
    has_user_passed_lesson,
)
from backend.quiz_engine import QuizEngine
from cli.quiz_cli import start_quiz_cli


def show_courses(username=None):
    courses = get_all_courses()

    if not courses:
        print("❌ No courses available.")
        input("Press Enter to return to the dashboard...")
        return

    while True:
        print("\n📚 Available Courses:")
        for course in courses:
            print(f"{course[0]}. {course[1]} — {course[2]}")

        choice = input("\nEnter course ID to view details, 's' to start a course, or press Enter to return: ")
        if choice.strip() == "":
            return
        if choice.strip().lower() == 's':
            cid = input("Enter course ID to start: ")
            if not cid.isdigit():
                print("❌ Invalid course ID")
                continue
            start_course_flow(int(cid), username)
            continue
        if not choice.isdigit():
            print("❌ Please enter a valid numeric course ID or press Enter to return.")
            continue
        course_id = int(choice)
        course = get_course_by_id(course_id)
        if not course:
            print(f"❌ No course with ID {course_id}.")
            continue

        # Show course details
        print(f"\n--- Course {course[0]} ---")
        print(f"Title: {course[1]}")
        print(f"Description: {course[2]}\n")

        # Show lessons for this course
        lessons = get_lessons_by_course(course_id)
        if not lessons:
            print("No lessons available for this course.")
            input("Press Enter to return to the course list...")
            continue

        # Determine unlocked lessons for this user: only the first lesson or lessons whose previous lesson was passed
        user_id = None
        if username:
            user_id = get_user_id_by_username(username)

        # build unlocked set
        unlocked = set()
        for idx, lesson in enumerate(lessons):
            lid = lesson[0]
            if idx == 0:
                unlocked.add(lid)
            else:
                prev_lid = lessons[idx - 1][0]
                if user_id and has_user_passed_lesson(user_id, prev_lid):
                    unlocked.add(lid)

        while True:
            print("Lessons:")
            for lesson in lessons:
                lock_mark = "" if lesson[0] in unlocked else " [Locked]"
                qcount = get_question_count_for_lesson(lesson[0])
                print(f"{lesson[0]}. {lesson[1]} (Questions: {qcount}){lock_mark}")

            lchoice = input("\nEnter lesson ID to view content, 'q' to take quiz, or press Enter to go back: ")
            if lchoice.strip() == "":
                break
            if lchoice.strip().lower() == 'q':
                lid = input("Enter lesson ID to take quiz for: ")
                if not lid.isdigit():
                    print("❌ Invalid lesson ID")
                    continue
                lid = int(lid)
                if lid not in unlocked:
                    print("❌ That lesson is locked. Pass previous lesson to unlock.")
                    continue
                start_quiz_cli(lid, username)
                continue
            if not lchoice.isdigit():
                print("❌ Please enter a valid numeric lesson ID or press Enter to go back.")
                continue
            lesson_id = int(lchoice)
            lesson = get_lesson_by_id(lesson_id)
            if not lesson or lesson[1] != course_id:
                print(f"❌ No lesson with ID {lesson_id} for this course.")
                continue

            print(f"\n--- Lesson {lesson[0]}: {lesson[2]} ---")
            print(lesson[3])
            print(f"\nDifficulty: {lesson[4]}")
            input("\nPress Enter to return to the lessons list...")


def start_course_flow(course_id, username, pass_ratio=1.0):
    """Sequentially run lessons' quizzes for a course; require pass_ratio (fraction) to advance."""
    lessons = get_lessons_by_course(course_id)
    if not lessons:
        print("❌ No lessons for this course.")
        return

    print(f"\n🚀 Starting course {course_id} - adaptive progression")
    for lesson in lessons:
        lesson_id = lesson[0]
        print(f"\n--- Lesson {lesson_id}: {lesson[1]} ---")
        print(lesson[2])
        # Repeat until user passes
        while True:
            score = start_quiz_cli(lesson_id, username)
            total_q = None
            # determine how many questions in quiz
            conn = None
            try:
                from backend.database import connect_db
                conn = connect_db()
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM quiz_questions qq JOIN quizzes q ON qq.quiz_id = q.id WHERE q.lesson_id = ?", (lesson_id,))
                total_q = cur.fetchone()[0]
            finally:
                if conn:
                    conn.close()

            if total_q is None or total_q == 0:
                print("No questions for this lesson — marking as passed.")
                break
            required = int(total_q * pass_ratio)
            # require at least required correct answers; if pass_ratio==1.0 require full marks
            if score >= required:
                print(f"✅ Passed lesson {lesson_id} ({score}/{total_q}). Moving to next lesson.")
                break
            else:
                print(f"❌ You scored {score}/{total_q}. Please repeat the lesson until you pass.")
                retry = input("Retry now? (y/n): ")
                if retry.strip().lower() != 'y':
                    print("Stopping course progression and returning to course menu.")
                    return
