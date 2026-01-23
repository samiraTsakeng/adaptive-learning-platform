from flask import Blueprint, request, jsonify

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/lessons/<int:lesson_id>/quiz", methods=["POST"])
def create_quiz(lesson_id):
    data = request.json
    quiz_type = data.get("type")
    questions = data.get("questions")

    if quiz_type not in ["MCQ", "OPEN"]:
        return jsonify({"error": "Invalid quiz type"}), 400

    if not questions or len(questions) == 0:
        return jsonify({"error": "Quiz must contain questions"}), 400

    for q in questions:
        if not q.get("question"):
            return jsonify({"error": "Question text missing"}), 400

        if quiz_type == "MCQ":
            if not q.get("options") or len(q["options"]) != 4:
                return jsonify({"error": "MCQ must have 4 options"}), 400

            if q.get("correctLetter") not in ["A", "B", "C", "D"]:
                return jsonify({"error": "Invalid correct letter"}), 400

            if not q.get("correctText"):
                return jsonify({"error": "Correct answer text missing"}), 400

        if quiz_type == "OPEN":
            if not q.get("correctText"):
                return jsonify({"error": "Correct answer required"}), 400

    # SAVE TO DB HERE
    # save_quiz(lesson_id, quiz_type, questions)

    return jsonify({"message": "Quiz saved successfully"})
