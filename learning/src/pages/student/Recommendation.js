import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API from "../../services/api";
import StudentLayout from "../../layouts/StudentLayout";
import StudentSidebar from "../../components/StudentSidebar";

const Recommendations = () => {
  const { courseId } = useParams();
  const [recs, setRecs] = useState([]);

  useEffect(() => {
    const userId = localStorage.getItem("userId");
    if (userId && courseId) {
      API.get(`/recommendations/${userId}/${courseId}`)
        .then(res => setRecs(res.data))
        .catch(console.error);
    }
  }, [courseId]);

  return (
    

      <div className="dashboard-content">
        <h1>Recommended for You</h1>

        {recs.length === 0 ? (
          <p>No recommendations available yet.</p>
        ) : (
          recs.map(r => (
            <div key={r.lesson_id} className="recommendation-card">
              <h3>{r.title}</h3>
              <p>Best Score: {r.best_score} / {r.total_q}</p>
            </div>
          ))
        )}
      </div>
   
  );
};

export default Recommendations;