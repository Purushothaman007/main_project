import React, { useState } from 'react';
import { Question, Difficulty } from '../types/question';
import { SAMPLE_QUESTIONS } from '../utils/sampleQuestions';

interface QuestionSidebarProps {
  activeQuestion: Question | null;
  onSelectQuestion: (q: Question) => void;
}

const DIFFICULTY_CLASS: Record<Difficulty, string> = {
  Easy:   'diff-easy',
  Medium: 'diff-medium',
  Hard:   'diff-hard',
};

export const QuestionSidebar: React.FC<QuestionSidebarProps> = ({
  activeQuestion,
  onSelectQuestion,
}) => {
  const [isOpen, setIsOpen] = useState(true);
  const [view, setView] = useState<'list' | 'detail'>('list');

  const handleSelect = (q: Question) => {
    onSelectQuestion(q);
    setView('detail');
  };

  const handleBack = () => setView('list');

  return (
    <>
      {/* Collapsed tab — always visible */}
      {!isOpen && (
        <button
          className="qs-collapsed-tab"
          onClick={() => setIsOpen(true)}
          id="qs-open-btn"
          title="Open Question Panel"
        >
          <span className="qs-tab-icon">📋</span>
          <span className="qs-tab-label">Problem</span>
        </button>
      )}

      {/* Sidebar panel */}
      <aside className={`question-sidebar glass-panel ${isOpen ? 'qs-open' : 'qs-closed'}`}>
        {/* Sidebar header */}
        <div className="qs-header">
          <div className="qs-title">
            <span className="qs-header-icon">📋</span>
            <span>Problems</span>
          </div>
          <div className="qs-header-actions">
            {view === 'detail' && (
              <button className="qs-icon-btn" onClick={handleBack} title="Back to list">
                ←
              </button>
            )}
            <button
              className="qs-icon-btn"
              onClick={() => setIsOpen(false)}
              id="qs-close-btn"
              title="Minimize panel"
            >
              ✕
            </button>
          </div>
        </div>

        {view === 'list' ? (
          /* ── Question List ── */
          <div className="qs-list">
            {activeQuestion && (
              <div className="qs-active-banner">
                <span className="qs-active-dot" />
                Active: <strong>{activeQuestion.title}</strong>
              </div>
            )}
            {SAMPLE_QUESTIONS.map((q) => (
              <button
                key={q.id}
                className={`qs-list-item ${activeQuestion?.id === q.id ? 'qs-list-item-active' : ''}`}
                onClick={() => handleSelect(q)}
              >
                <div className="qs-item-top">
                  <span className="qs-item-title">{q.title}</span>
                  <span className={`qs-diff-badge ${DIFFICULTY_CLASS[q.difficulty]}`}>
                    {q.difficulty}
                  </span>
                </div>
                <div className="qs-item-tags">
                  {q.tags.map((t) => (
                    <span key={t} className="qs-tag">{t}</span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        ) : (
          /* ── Question Detail ── */
          activeQuestion && (
            <div className="qs-detail">
              <div className="qs-detail-title-row">
                <h2 className="qs-detail-title">{activeQuestion.title}</h2>
                <span className={`qs-diff-badge ${DIFFICULTY_CLASS[activeQuestion.difficulty]}`}>
                  {activeQuestion.difficulty}
                </span>
              </div>

              <div className="qs-detail-tags">
                {activeQuestion.tags.map((t) => (
                  <span key={t} className="qs-tag">{t}</span>
                ))}
              </div>

              {/* Description */}
              <div className="qs-section">
                <p className="qs-description">{activeQuestion.description}</p>
              </div>

              {/* Examples */}
              <div className="qs-section">
                <h3 className="qs-section-title">Examples</h3>
                {activeQuestion.examples.map((ex, i) => (
                  <div key={i} className="qs-example">
                    <div className="qs-example-row">
                      <span className="qs-example-label">Input:</span>
                      <code className="qs-code">{ex.input}</code>
                    </div>
                    <div className="qs-example-row">
                      <span className="qs-example-label">Output:</span>
                      <code className="qs-code">{ex.output}</code>
                    </div>
                    {ex.explanation && (
                      <p className="qs-example-exp">💡 {ex.explanation}</p>
                    )}
                  </div>
                ))}
              </div>

              {/* Constraints */}
              <div className="qs-section">
                <h3 className="qs-section-title">Constraints</h3>
                <ul className="qs-constraints">
                  {activeQuestion.constraints.map((c, i) => (
                    <li key={i}>{c}</li>
                  ))}
                </ul>
              </div>

              {/* Action */}
              <button
                className="qs-solve-btn"
                onClick={() => onSelectQuestion(activeQuestion)}
                id="qs-load-question-btn"
              >
                ✅ Load this problem into editor
              </button>
            </div>
          )
        )}
      </aside>
    </>
  );
};
