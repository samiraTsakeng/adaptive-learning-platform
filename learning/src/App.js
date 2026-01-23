import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext"; 
import Navbar from "./components/Navbar";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";

import StudentDashboard from "./pages/student/Dashboard";
import LessonList from "./pages/student/LessonList";
import LessonView from "./pages/student/LessonView";
import Quiz from "./pages/student/Quiz";
import Progress from "./pages/student/Progress";
import TeacherDashboard from "./pages/Teacher/Dashboard";
import UploadCourse from "./pages/Teacher/UploadCourse";
//import StudentLayout from "./layouts/StudentLayout";
function App() {
  return (
    <AuthProvider>
    <Router>
      <Navbar />

     <Routes>
  {/* Public */}
  <Route path="/" element={<Home />} />
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />

  {/* Student */}
  <Route path="/student/dashboard" element={<StudentDashboard />} />
  <Route path="/student/lessons/:courseId" element={<LessonList />} />
  <Route path="/student/lessons/:courseId/:lessonId" element={<LessonView />} />
  <Route path="/student/quiz/:lessonId" element={<Quiz />} />
  <Route path="/student/progress" element={<Progress />} />

  {/* Teacher */}
  <Route path="/teacher/dashboard" element={<TeacherDashboard />} />
  <Route path="/teacher/upload" element={<UploadCourse />} />
</Routes>




    </Router>
    </AuthProvider>
  );
}

export default App;