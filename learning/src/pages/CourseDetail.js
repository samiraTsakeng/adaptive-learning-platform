import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import API from "../services/api";
import "../styles/courses.css";

const CourseDetail = () => {
  const { id } = useParams();
  const [course, setCourse] = useState(null);

  useEffect(() => {
    API.get(`/courses/${id}`)
      .then(res => setCourse(res.data))
      .catch(err => console.error(err));
  }, [id]);

  if (!course) return <p className="container">Loading...</p>;

  return (
    <div className="container">
      <h1>{course.title}</h1>
      <p>{course.description}</p>

      <h3>Lessons</h3>
      {course.lessons.map(lesson => (
        <div key={lesson.id} className="lesson-card">
          <h4>{lesson.title}</h4>
          <p>Difficulty: {lesson.difficulty}</p>
          <Link className="btn" to={`/lesson/${lesson.id}`}>
            Open Lesson
          </Link>
        </div>
      ))}
    </div>
  );
};

export default CourseDetail;
