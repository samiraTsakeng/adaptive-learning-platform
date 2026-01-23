import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../../services/api";
import "../../styles/quiz.css"; // Add styling for better UI

const Quiz = () => {
  const { lessonId } = useParams();
  const navigate = useNavigate();

  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [score, setScore] = useState(null);
  const [total, setTotal] = useState(0);
  const [passed, setPassed] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchQuiz();
  }, [lessonId]);

  const fetchQuiz = async () => {
    try {
      setLoading(true);
      const res = await API.get(`/quizzes/${lessonId}`);
      
      if (res.data && res.data.questions) {
        setQuestions(res.data.questions);
        setTotal(res.data.questions.length);
        
        // Initialize answers object
        const initialAnswers = {};
        res.data.questions.forEach(q => {
          initialAnswers[q.question_id] = "";
        });
        setAnswers(initialAnswers);
      } else {
        setQuestions([]);
      }
    } catch (err) {
      console.error("Quiz fetch error:", err);
      setError("Failed to load quiz. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const submitQuiz = async () => {
    if (submitting) return;
    
    // Check if all questions are answered
    const unanswered = questions.filter(q => !answers[q.question_id]?.trim());
    if (unanswered.length > 0) {
      if (!window.confirm(`You have ${unanswered.length} unanswered questions. Submit anyway?`)) {
        return;
      }
    }
    
    try {
      setSubmitting(true);
      const res = await API.post(`/quizzes/${lessonId}/submit`, { answers });
      
      setScore(res.data.score);
      setTotal(res.data.total);
      setPassed(res.data.passed);
      
      // Show success message
      alert(`Quiz submitted! Score: ${res.data.score}/${res.data.total}`);
      
    } catch (err) {
      console.error("Submission error:", err);
      setError("Failed to submit quiz. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-content">
        <h1>Quiz</h1>
        <p>Loading quiz questions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-content">
        <h1>Quiz</h1>
        <p className="error">{error}</p>
      </div>
    );
  }

  return (
    <div className="dashboard-content">
      <h1>Quiz</h1>
      
      {questions.length === 0 ? (
        <div className="no-quiz">
          <p>No quiz questions available for this lesson.</p>
          <button onClick={() => navigate(-1)} className="btn-back">
            Go Back
          </button>
        </div>
      ) : (
        <div className="quiz-container">
          <div className="quiz-header">
            <p>Total Questions: {questions.length}</p>
            <p>Answer all questions and click Submit when done.</p>
          </div>
          
          <div className="questions-list">
            {questions.map((q, index) => (
              <div key={q.question_id} className="question-card">
                <div className="question-header">
                  <span className="question-number">Question {index + 1}</span>
                </div>
                <p className="question-text">{q.question}</p>
                
                <div className="answer-input">
                  <input
                    type="text"
                    placeholder="Type your answer here..."
                    value={answers[q.question_id] || ""}
                    onChange={e => handleAnswerChange(q.question_id, e.target.value)}
                    className="answer-field"
                  />
                </div>
              </div>
            ))}
          </div>
          
          <div className="quiz-footer">
            <button 
              onClick={submitQuiz} 
              className="btn-submit"
              disabled={submitting}
            >
              {submitting ? "Submitting..." : "Submit Quiz"}
            </button>
            
            {score !== null && (
              <div className="quiz-result">
                <h3>Quiz Result</h3>
                <p>Score: {score}/{total}</p>
                <p>Status: {passed ? "Passed ✅" : "Needs Improvement ❌"}</p>
                {passed && (
                  <button 
                    onClick={() => navigate(-1)} 
                    className="btn-back"
                  >
                    Continue Learning
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Quiz;