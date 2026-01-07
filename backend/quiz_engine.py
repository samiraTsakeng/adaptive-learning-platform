from data_structures.stack import Stack
from backend.database import connect_db

class QuizEngine:
    def __init__(self, lesson_id):
        self.lesson_id = lesson_id
        self.questions_stack = Stack()
        self.load_questions()
        self.answers = {}  # user answers keyed by question_id
        self.score = 0

    def load_questions(self):
        """Load questions from the database and push onto stack"""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT qq.id, qq.question, qq.correct_answer
            FROM quizzes q
            JOIN quiz_questions qq ON q.id = qq.quiz_id
            WHERE q.lesson_id = ?
        """, (self.lesson_id,))
        questions = cursor.fetchall()
        conn.close()

        for q in reversed(questions):
            # push in reverse order so the first question is on top
            self.questions_stack.push({
                "id": q[0],
                "question": q[1],
                "correct_answer": q[2]
            })

    def has_next(self):
        return not self.questions_stack.is_empty()

    def get_next_question(self):
        if self.has_next():
            return self.questions_stack.peek()
        return None

    def answer_current(self, answer):
        """Record answer and pop question"""
        current = self.questions_stack.pop()
        if not current:
            return
        self.answers[current["id"]] = answer
        if answer.strip().lower() == current["correct_answer"].strip().lower():
            self.score += 1

    def calculate_score(self):
        return self.score
