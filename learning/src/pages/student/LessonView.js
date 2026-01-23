import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../../services/api";
import StudentSidebar from "../../components/StudentSidebar";

const LessonView = () => {
  const { courseId, lessonId } = useParams();
  const [lesson, setLesson] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    API.get(`/courses/${courseId}/lessons/${lessonId}`)
      .then(res => setLesson(res.data))
      .catch(console.error);
  }, [courseId, lessonId]);

  if (!lesson) return <p>Loading...</p>;

  return (
    <div className="dashboard-layout">
      <StudentSidebar />

      <div className="dashboard-content">
        <h1>{lesson.title}</h1>
        <p>{lesson.content}</p>

        <button onClick={() => navigate(`/student/quiz/${lessonId}`)}>
          Take Quiz
        </button>
      </div>
    </div>
  );
};

export default LessonView;