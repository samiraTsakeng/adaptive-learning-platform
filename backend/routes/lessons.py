from flask import Blueprint, request, jsonify

lesson_bp = Blueprint("lesson", __name__)

@lesson_bp.route("/lessons/<int:lesson_id>", methods=["PUT"])
def update_lesson(lesson_id):
    data = request.json
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"error": "Title and content required"}), 400

    # update_lesson_in_db(lesson_id, title, content)

    return jsonify({"message": "Lesson updated"})
