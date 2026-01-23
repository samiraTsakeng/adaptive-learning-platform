import { useState } from "react";
import API from "../../services/api";
import "../../styles/dashboard.css";

const TeacherDashboard = () => {
  const token = localStorage.getItem("token");

  const [course, setCourse] = useState({ title: "", description: "" });
  const [lesson, setLesson] = useState({
    title: "",
    content: "",
    difficulty: 1
  });
  const [quizType, setQuizType] = useState("MCQ");
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);

  /* =========================
     QUESTION MANAGEMENT
  ========================== */

  const addQuestion = () => {
    if (quizType === "MCQ") {
      setQuestions(prev => [
        ...prev,
        {
          question: "",
          options: { A: "", B: "", C: "", D: "" },
          correctLetter: "",
          correctText: ""
        }
      ]);
    } else {
      setQuestions(prev => [
        ...prev,
        { question: "", correctText: "" }
      ]);
    }
  };

  const updateQuestion = (index, field, value) => {
    setQuestions(prev => {
      const copy = [...prev];
      copy[index][field] = value;
      return copy;
    });
  };

  const updateOption = (index, letter, value) => {
    setQuestions(prev => {
      const copy = [...prev];
      copy[index].options[letter] = value;
      return copy;
    });
  };

  const removeQuestion = (index) => {
    setQuestions(prev => prev.filter((_, i) => i !== index));
  };

  /* =========================
     VALIDATION
  ========================== */

  const validateQuiz = () => {
    if (questions.length === 0) return "Add at least one question";

    for (const q of questions) {
      if (!q.question.trim()) return "Question text is required";

      if (quizType === "MCQ") {
        if (!q.correctLetter || !q.correctText)
          return "MCQ requires correct letter and text";

        const letter = q.correctLetter.toUpperCase();
        if (!["A", "B", "C", "D"].includes(letter))
          return "Correct letter must be A–D";

        if (q.options[letter] !== q.correctText)
          return "Correct text must match selected option";
      } else {
        if (!q.correctText.trim())
          return "Open question requires an answer";
      }
    }
    return null;
  };

  /* =========================
     SAVE EVERYTHING
  ========================== */

  const saveAll = async () => {
    if (!course.title.trim()) {
      alert("Course title required");
      return;
    }

    if (!lesson.title.trim()) {
      alert("Lesson title required");
      return;
    }

    const quizError = validateQuiz();
    if (quizError) {
      alert(quizError);
      return;
    }

    setLoading(true);

    try {
      /* 1️⃣ CREATE COURSE */
      const courseRes = await API.post(
        "/courses",
        course,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const courseId = courseRes.data.id;

      /* 2️⃣ CREATE LESSON */
      const lessonRes = await API.post(
        `/courses/${courseId}/lessons`,
        lesson,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const lessonId = lessonRes.data.id;

      /* 3️⃣ BUILD PAYLOAD */
      const payload = {
        type: quizType,
        questions: questions
      };

      /* 4️⃣ CREATE QUIZ */
      await API.post(
        `/lessons/${lessonId}/quiz`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      alert("✅ Course, lesson and quiz created successfully!");

      /* RESET */
      setCourse({ title: "", description: "" });
      setLesson({ title: "", content: "", difficulty: 1 });
      setQuestions([]);
      setQuizType("MCQ");

    } catch (err) {
      console.error(err);
      alert(err.response?.data?.message || "Server error");
    } finally {
      setLoading(false);
    }
  };

  /* =========================
     UI
  ========================== */

  return (
    <div className="teacher-dashboard">
      <h1>Teacher Dashboard</h1>

      <section className="form-section">
        <h3>📘 Course</h3>
        <input
          placeholder="Course title"
          value={course.title}
          onChange={e => setCourse({ ...course, title: e.target.value })}
        />
        <textarea
          placeholder="Course description"
          value={course.description}
          onChange={e => setCourse({ ...course, description: e.target.value })}
        />
      </section>

      <section className="form-section">
        <h3>📗 Lesson</h3>
        <input
          placeholder="Lesson title"
          value={lesson.title}
          onChange={e => setLesson({ ...lesson, title: e.target.value })}
        />
        <textarea
          placeholder="Lesson content"
          value={lesson.content}
          onChange={e => setLesson({ ...lesson, content: e.target.value })}
        />

        <select
          value={lesson.difficulty}
          onChange={e =>
            setLesson({ ...lesson, difficulty: Number(e.target.value) })
          }
        >
          <option value={1}>Beginner</option>
          <option value={2}>Intermediate</option>
          <option value={3}>Advanced</option>
        </select>
      </section>

      <section className="form-section">
        <h3>❓ Quiz</h3>

        <select
          value={quizType}
          onChange={e => setQuizType(e.target.value)}
        >
          <option value="MCQ">Multiple Choice</option>
          <option value="OPEN">Open Answer</option>
        </select>

        <button onClick={addQuestion}>➕ Add Question</button>

        {questions.map((q, i) => (
          <div key={i} className="question-box">
            <input
              placeholder={`Question ${i + 1}`}
              value={q.question}
              onChange={e => updateQuestion(i, "question", e.target.value)}
            />

            {quizType === "MCQ" ? (
              <>
                {["A", "B", "C", "D"].map(letter => (
                  <input
                    key={letter}
                    placeholder={`Option ${letter}`}
                    value={q.options[letter]}
                    onChange={e =>
                      updateOption(i, letter, e.target.value)
                    }
                  />
                ))}

                <input
                  placeholder="Correct letter (A–D)"
                  value={q.correctLetter}
                  onChange={e =>
                    updateQuestion(i, "correctLetter", e.target.value)
                  }
                />

                <input
                  placeholder="Correct answer text"
                  value={q.correctText}
                  onChange={e =>
                    updateQuestion(i, "correctText", e.target.value)
                  }
                />
              </>
            ) : (
              <input
                placeholder="Correct answer"
                value={q.correctText}
                onChange={e =>
                  updateQuestion(i, "correctText", e.target.value)
                }
              />
            )}

            <button onClick={() => removeQuestion(i)}>🗑 Remove</button>
          </div>
        ))}
      </section>

      <button onClick={saveAll} disabled={loading}>
        {loading ? "Saving..." : "💾 Save Everything"}
      </button>
    </div>
  );
};

export default TeacherDashboard;
