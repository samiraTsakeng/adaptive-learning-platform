import { useState } from "react";
import API from "../../services/api";
import "../../styles/teacher.css";

const UploadCourse = () => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [lessons, setLessons] = useState([]);

  const addLesson = () => {
    setLessons([
      ...lessons,
      { title: "", content: "", difficulty: 1, quiz: [] },
    ]);
  };

  const addQuestion = (lessonIndex) => {
    const updated = [...lessons];
    updated[lessonIndex].quiz.push({
      question: "",
      correct_answer: "",
    });
    setLessons(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await API.post("/teacher/upload", {
        title,
        description,
        lessons,
      });
      alert("Course uploaded successfully");
    } catch {
      alert("Upload failed");
    }
  };

  return (
    <div className="upload-box">
      <h2>Upload Course</h2>

      <input
        placeholder="Course Title"
        onChange={(e) => setTitle(e.target.value)}
      />

      <textarea
        placeholder="Course Description"
        onChange={(e) => setDescription(e.target.value)}
      />

      <button onClick={addLesson} className="btn">
        Add Lesson
      </button>

      {lessons.map((lesson, i) => (
        <div key={i} className="lesson-box">
          <h4>Lesson {i + 1}</h4>

          <input
            placeholder="Lesson title"
            onChange={(e) => (lesson.title = e.target.value)}
          />

          <textarea
            placeholder="Lesson content"
            onChange={(e) => (lesson.content = e.target.value)}
          />

          <button onClick={() => addQuestion(i)} className="btn secondary">
            Add Quiz Question
          </button>

          {lesson.quiz.map((q, qi) => (
            <div key={qi}>
              <input
                placeholder="Question"
                onChange={(e) => (q.question = e.target.value)}
              />
              <input
                placeholder="Correct Answer"
                onChange={(e) => (q.correct_answer = e.target.value)}
              />
            </div>
          ))}
        </div>
      ))}

      <button className="btn" onClick={handleSubmit}>
        Upload Course
      </button>
    </div>
  );
};

export default UploadCourse;
