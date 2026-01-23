import { NavLink } from "react-router-dom";
import "../styles/sidebar.css";

const StudentSidebar = () => {
  return (
    <div className="sidebar">
      <h2>Student</h2>

      <NavLink to="/student/dashboard">Courses</NavLink>
      <NavLink to="/student/lessons">Lessons</NavLink>

      {/* Quiz is lesson-based, no global route */}
      {/* <NavLink to="/student/quiz">Quiz</NavLink> */}

      <NavLink to="/student/progress">Progress</NavLink>
      <NavLink to="/student/recommendations">Recommendations</NavLink>
    </div>
  );
};

export default StudentSidebar;
