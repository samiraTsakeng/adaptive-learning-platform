from flask import Blueprint, request, jsonify

attempt_bp = Blueprint("attempt", __name__)

@attempt_bp.route("/quizzes/<int:quiz_id>/attempt", methods=["POST"])
def submit_attempt(quiz_id):
    data = request.json
    answers = data.get("answers")

    quiz = get_quiz_from_db(quiz_id)

    score = 0
    for i, q in enumerate(quiz["questions"]):
        if quiz["type"] == "MCQ":
            if answers[str(i)] == q["correctLetter"]:
                score += 1
        else:
            if answers[str(i)].strip().lower() == q["correctText"].strip().lower():
                score += 1

    return jsonify({
        "score": score,
        "total": len(quiz["questions"])
    })
