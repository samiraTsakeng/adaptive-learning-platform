import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import API from "../services/api";

const Lesson = () => {
  const { id } = useParams();
  const [lesson, setLesson] = useState(null);

  useEffect(() => {
    API.get(`/lessons/${id}`)
      .then(res => setLesson(res.data))
      .catch(err => console.error(err));
  }, [id]);

  if (!lesson) return <p className="container">Loading...</p>;

  if (lesson.locked) {
    return (
      <div className="container">
        <h2>This lesson is locked 🔒</h2>
        <p>You must complete the previous lesson.</p>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>{lesson.title}</h1>
      <p>{lesson.content}</p>
      <Link className="btn" to={`/quiz/${lesson.id}`}>
        Take Quiz
      </Link>
    </div>
  );
};

export default Lesson;
