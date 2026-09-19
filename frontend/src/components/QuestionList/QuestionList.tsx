import React from 'react';
import { Question } from '../../types/question';
import { ArrowRight, Tag, BookMarked } from 'lucide-react';


interface QuestionListProps {
  questions: Question[];
  onSelectQuestion: (questionId: string) => void;
}

export const QuestionList: React.FC<QuestionListProps> = ({
  questions,
  onSelectQuestion,
}) => {
  const getDifficultyClass = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'badge-easy';
      case 'medium':
        return 'badge-medium';
      case 'hard':
        return 'badge-hard';
      default:
        return '';
    }
  };

  return (
    <div className="question-list-container">
      {/* Page Header */}
      <header className="question-list-header glass-panel">
        <div>
          <h1 className="list-title">
            <BookMarked className="title-icon" size={24} /> College Assessment Problems
          </h1>
          <p className="list-subtitle">
            Select a problem below to open your workspace with the Monaco Code Editor and Gemini AI Educational Tutor.
          </p>
        </div>
      </header>

      {/* Questions Grid */}
      <div className="questions-grid">
        {questions.map((q, index) => (
          <div key={q.id} className="glass-panel question-card">
            <div className="card-top">
              <span className="question-number">#{index + 1}</span>
              <div className="card-badges">
                <span className={`difficulty-badge ${getDifficultyClass(q.difficulty)}`}>
                  {q.difficulty}
                </span>
                <span className="topic-badge">
                  <Tag size={12} /> {q.topic}
                </span>
              </div>
            </div>

            <h2 className="question-card-title">{q.title}</h2>
            <p className="question-card-desc">{q.shortDescription}</p>

            <div className="card-bottom">
              <button
                className="btn btn-primary solve-btn"
                onClick={() => onSelectQuestion(q.id)}
              >
                Solve <ArrowRight size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
