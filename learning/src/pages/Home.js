import { useEffect, useState } from "react";
import API from "../services/api";
import CourseCard from "../components/CourseCard";
import "../styles/courses.css";
import "../styles/home.css"
const Home = () => {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    API.get("/courses")
      .then(res => setCourses(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="container">
      <h1>Available Courses</h1>
      <div className="course-grid">
        {courses.map(course => (
          <CourseCard key={course.id} course={course} />
        ))}
      </div>
    </div>
  );
};

export default Home;
