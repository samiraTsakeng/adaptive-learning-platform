import json
import urllib.request


def input_multiline(prompt):
    print(prompt + " (end with a blank line)")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)


def create_course_interactive():
    title = input("Course title: ")
    description = input("Course description: ")
    lessons = []
    while True:
        add = input("Add a lesson? (y/N): ")
        if add.lower() != 'y':
            break
        ltitle = input(" Lesson title: ")
        content = input_multiline(" Lesson content (markdown/plain text)")
        difficulty = input(" Lesson difficulty (1-5, default 1): ") or "1"
        try:
            difficulty = int(difficulty)
        except ValueError:
            difficulty = 1
        quiz = []
        addq = input(" Add quiz for this lesson? (y/N): ")
        if addq.lower() == 'y':
            while True:
                q = input("  Question text (empty to stop): ")
                if not q:
                    break
                ans = input("  Correct answer: ")
                choices = []
                mcq = input("  Is this multiple-choice? (y/N): ")
                if mcq.lower() == 'y':
                    while True:
                        c = input("   Choice (empty to stop): ")
                        if not c:
                            break
                        choices.append(c)
                quiz.append({"question": q, "correct_answer": ans, "choices": choices})
        lessons.append({"title": ltitle, "content": content, "difficulty": difficulty, "quiz": quiz})

    package = {"title": title, "description": description, "lessons": lessons}
    return package


def export_package(package, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(package, f, ensure_ascii=False, indent=2)
    print(f"Saved package to {out_path}")


def upload_package(package, url='http://127.0.0.1:5000/teacher/upload', token=None):
    """Upload course package to server with better error handling."""
    if not token:
        print('❌ Token required. Please login first and paste your teacher token.')
        return
    
    data = json.dumps(package).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            result = json.loads(body)
            if result.get('success'):
                print(f'✅ Upload successful! Course ID: {result.get("course_id")}')
            else:
                print(f'❌ Upload failed: {result.get("message")}')
    except urllib.error.URLError as e:
        print(f'❌ Connection failed: {e.reason}')
        print('   Make sure server is running: python -m backend.app')
        print('   and accessible at http://127.0.0.1:5000')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f'❌ Server error ({e.code}): {body}')
    except json.JSONDecodeError:
        print('❌ Invalid response from server')
    except Exception as e:
        print(f'❌ Upload failed: {e}')



def run_interactive(token=None):
    print('✏️  Teacher Course Authoring — create and upload courses offline')
    pkg = create_course_interactive()
    
    if not token:
        print("⚠️  No token available. You won't be able to upload.")
    
    while True:
        opt = input('Options: (s)ave, (u)pload, (q)uit: ')
        if opt.lower() == 's':
            out = input('Output filename (course.json): ') or 'course.json'
            export_package(pkg, out)
        elif opt.lower() == 'u':
            if not token:
                t = input('No token from login. Paste your teacher JWT token here (or empty to skip): ')
                if not t:
                    print('⚠️  Upload cancelled')
                    continue
                upload_package(pkg, token=t)
            else:
                upload_package(pkg, token=token)
        elif opt.lower() == 'q':
            break
        else:
            print('Unknown option')


if __name__ == '__main__':
    run_interactive()
