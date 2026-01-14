from cli.lessons_cli import show_lessons

try:
    from cli.menus import main_menu, student_menu
    from cli.courses_cli import show_courses
    from backend.auth import (
        load_users_into_hash_table,
        register_user,
        login_user
    )
except ModuleNotFoundError:
    import sys, os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from cli.menus import main_menu, student_menu
    from backend.auth import (
        load_users_into_hash_table,
        register_user,
        login_user
    )

# Global to store current teacher token
TEACHER_TOKEN = None


def start_cli():
    load_users_into_hash_table()

    while True:
        choice = main_menu()

        if choice == "1":
            username = input("Username: ")
            password = input("Password: ")

            success, result = login_user(username, password)
            if success:
                print("✅ Login successful")
                # determine role and route accordingly
                from backend.database import get_user_info_by_username
                uid, role = get_user_info_by_username(username)
                
                # Get JWT token for teachers to use with upload
                if role == 'teacher':
                    import json
                    import urllib.request
                    try:
                        data = json.dumps({"username": username, "password": password}).encode('utf-8')
                        req = urllib.request.Request('http://127.0.0.1:5000/auth/login', data=data, method='POST')
                        req.add_header('Content-Type', 'application/json')
                        with urllib.request.urlopen(req, timeout=5) as resp:
                            result = json.loads(resp.read().decode('utf-8'))
                            global TEACHER_TOKEN
                            TEACHER_TOKEN = result.get('token')
                            if TEACHER_TOKEN:
                                print(f"✅ Token obtained for upload")
                    except Exception as e:
                        print(f"⚠️  Could not fetch token: {e}")
                
                if role == 'teacher':
                    from cli.teacher_author_cli import run_interactive as teacher_dashboard
                    teacher_dashboard(TEACHER_TOKEN)
                else:
                    student_dashboard(username)
            else:
                print(f"❌ {result}")

        elif choice == "2":
            username = input("Choose username: ")
            password = input("Choose password: ")
            role_q = input("Are you registering as a teacher? (y/N): ")
            role = 'teacher' if role_q.lower() == 'y' else 'student'

            success, message = register_user(username, password, role)
            print(message)

        elif choice == "3":
            print("Goodbye 👋")
            break

        else:
            print("❌ Invalid choice")


def student_dashboard(username):
    while True:
        choice = student_menu()

        if choice == "1":
            show_courses(username)

        elif choice == "2":
            from cli.search_cli import search_cli
            search_cli()

        elif choice == "3":
            lesson_id = input("Enter lesson ID to take quiz: ")
            from cli.quiz_cli import start_quiz_cli
            start_quiz_cli(lesson_id, username)

        elif choice == "4":
            from cli.recommendation_cli import show_recommendations_cli
            show_recommendations_cli(username)

        elif choice == "5":
            from cli.progress_cli import view_progress_cli
            view_progress_cli(username)

        elif choice == "6":
            print("Logging out...")
            break

        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    start_cli()
