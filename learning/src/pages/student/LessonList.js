import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../../services/api";
import StudentLayout from "../../layouts/StudentLayout";
import StudentSidebar from "../../components/StudentSidebar";
//import "../../styles/lesson.css";

const LessonList = () => {
  const { courseId } = useParams();
  const [lessons, setLessons] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    API.get(`/courses/${courseId}/lessons`)
      .then(res => setLessons(res.data))
      .catch(console.error);
  }, [courseId]);

  return (
    
      
      <div className="dashboard-content">
        <h1>Lessons</h1>

        {lessons.map(lesson => (
          <div
            key={lesson.id}
            className={`lesson-card ${lesson.locked ? "locked" : ""}`}
            onClick={() =>
              !lesson.locked && navigate(`/student/lessons/${courseId}/${lesson.id}`)
            }
          >
            <h3>
              {lesson.title}
              {lesson.edited && <span className="edited-dot">🔵</span>}
            </h3>

            {lesson.locked && <p>🔒 Locked</p>}
          </div>
        ))}
      </div>
    
  );
};

export default LessonList;