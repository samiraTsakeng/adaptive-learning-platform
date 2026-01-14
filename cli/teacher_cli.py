import json
from backend.database import connect_db, get_course_by_id, get_lessons_by_course, get_quiz_id_for_lesson


def export_course_package(course_id, out_path):
    conn = connect_db()
    cur = conn.cursor()

    course = get_course_by_id(course_id)
    if not course:
        raise ValueError(f"Course id {course_id} not found")
    _, title, description = course

    lessons = get_lessons_by_course(course_id)
    lessons_out = []
    for l in lessons:
        lesson_id, lesson_title, content, difficulty = l
        # find quiz id and its questions
        quiz_id = get_quiz_id_for_lesson(lesson_id)
        questions = []
        if quiz_id:
            cur.execute("SELECT id, question, correct_answer FROM quiz_questions WHERE quiz_id = ? ORDER BY id", (quiz_id,))
            for qid, qtext, correct in cur.fetchall():
                questions.append({"question": qtext, "correct_answer": correct})

        lessons_out.append({
            "title": lesson_title,
            "content": content,
            "difficulty": difficulty,
            "quiz": questions,
        })

    package = {
        "title": title,
        "description": description,
        "lessons": lessons_out,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(package, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"Exported course {course_id} -> {out_path}")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("course_id", type=int)
    p.add_argument("out", help="output JSON file")
    args = p.parse_args()
    export_course_package(args.course_id, args.out)
