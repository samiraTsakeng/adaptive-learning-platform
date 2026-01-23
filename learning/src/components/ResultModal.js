import "./ResultModal.css";

const ResultModal = ({ passed, onNextLesson, onRetry, onViewProgress }) => {
  return (
    <div className="modal-backdrop">
      <div className="modal-box">
        <h2>{passed ? "🎉 Success!" : "❌ Try Again"}</h2>

        {passed ? (
          <>
            <p>You passed the quiz</p>
            <button onClick={onViewProgress}>See Progress</button>
            <button onClick={onNextLesson}>Next Lesson</button>
          </>
        ) : (
          <button onClick={onRetry}>Repeat Quiz</button>
        )}
      </div>
    </div>
  );
};

export default ResultModal;
