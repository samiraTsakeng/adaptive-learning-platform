"""
Search CLI using Trie-based search.
"""

from backend.search import search_courses, search_lessons


def search_cli():
    """Interactive search for courses and lessons."""
    while True:
        search_type = input("\nSearch (1: Courses, 2: Lessons, or press Enter to go back): ").strip()
        if search_type == "":
            return
        if search_type == "1":
            query = input("Enter course name or prefix: ")
            results = search_courses(query)
            if not results:
                print("No courses found.")
                continue
            print("\n📚 Search Results (Courses):")
            for course_id, title, description in results:
                print(f"{course_id}. {title} — {description}")
        elif search_type == "2":
            query = input("Enter lesson name or prefix: ")
            results = search_lessons(query)
            if not results:
                print("No lessons found.")
                continue
            print("\n📝 Search Results (Lessons):")
            for lesson_id, title, course_id in results:
                print(f"{lesson_id}. {title} (Course {course_id})")
        else:
            print("Invalid choice.")
