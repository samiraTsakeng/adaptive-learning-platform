import { useEffect, useState } from "react";
import API from "../../services/api";
import StudentLayout from "../../layouts/StudentLayout";
import StudentSidebar from "../../components/StudentSidebar";

const Progress = () => {
  const [progress, setProgress] = useState([]);

  useEffect(() => {
    const userId = localStorage.getItem("userId");
    if (userId) {
      API.get(`/progress/${userId}`)
        .then(res => setProgress(res.data))
        .catch(console.error);
    }
  }, []);

  return (
    
      
      <div className="dashboard-content">
        <h1>Your Progress</h1>

        {progress.length === 0 ? (
          <p>No progress data available yet.</p>
        ) : (
          progress.map(p => (
            <div key={p.course_id} className="progress-card">
              <h3>{p.title}</h3>
              <p>Completed: {p.passed} / {p.total} lessons ({p.percent}%)</p>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${p.percent}%` }}
                ></div>
              </div>
            </div>
          ))
        )}
      </div>
   
  );
};

export default Progress;