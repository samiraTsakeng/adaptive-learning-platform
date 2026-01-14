import React, { useEffect, useState } from 'react';
import axios from 'axios';

function CourseList() {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    // Fetch courses from the backend API
    axios.get('http://127.0.0.1:5000/courses')
      .then(response => {
        setCourses(response.data);
      })
      .catch(error => {
        console.error(error);
      });
  }, []);

  return (
    <div>
      <h1>Course List</h1>
      <ul>
        {courses.map(course => (
          <li key={course.id}>{course.name}</li>
        ))}
      </ul>
    </div>
  );
}

export default CourseList;