import { useEffect, useState } from "react";
import API from "../../services/api";
import { useNavigate } from "react-router-dom";
//import StudentSidebar from "../../components/StudentSidebar";
import CourseCard from "../../components/CourseCard";
import StudentLayout from "../../layouts/StudentLayout";
import "../../styles/dashboard.css";

const StudentDashboard = () => {
  const [courses, setCourses] = useState([]);
  //const [selectedCourse, setSelectedCourse] = useState(null);
  //const navigate = useNavigate();

  useEffect(() => {
    API.get("/courses")
      .then((res) => setCourses(res.data))
      .catch(() => alert("Failed to load courses"));
  }, []);

  return (
    

      <div className="dashboard">
        <h2>Available Courses</h2>

        {courses.length === 0 ? (
          <p>No courses available yet. Please come back later</p>
        ) : (
          <div className="course-grid">
            {courses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        )}

        {/* MODAL */}
        {/*{selectedCourse && (
          <div className="modal">
            <div className="modal-box">
              <h3>{selectedCourse.title}</h3>
              <p>{selectedCourse.description}</p>

              <button
                className="btn"
                onClick={() =>
                  navigate(`/student/lessons/${selectedCourse.id}`)
                }
              >
                View Lessons
              </button>

              <button
                className="btn secondary"
                onClick={() => setSelectedCourse(null)}
              >
                Close
              </button>
            </div>
          </div>
        )}*/}
      </div>
  
  );
};

export default StudentDashboard;

