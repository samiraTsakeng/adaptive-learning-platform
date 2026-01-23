import { Link } from "react-router-dom";
import "../styles/courses.css";

const CourseCard = ({ course }) => {
  return (
    <div className="course-card">
      <h3>{course.title}</h3>
      <p>{course.description}</p>
    <Link to={`/student/lessons/${course.id}`} className="btn">
  View Lessons
</Link>

    </div>
  );
};

export default CourseCard;
