import React, { useState, useEffect } from 'react';
import { STATIC_QUESTIONS } from './data/questions';
import { QuestionList } from './components/QuestionList/QuestionList';
import { QuestionWorkspace } from './components/QuestionWorkspace/QuestionWorkspace';

export const App: React.FC = () => {
  const [currentPath, setCurrentPath] = useState<string>(window.location.pathname);

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigateTo = (path: string) => {
    window.history.pushState({}, '', path);
    setCurrentPath(path);
  };

  // Route matching: /questions/:questionId
  const match = currentPath.match(/^\/questions\/([a-zA-Z0-9_-]+)$/);
  const selectedQuestionId = match ? match[1] : null;
  const activeQuestion = STATIC_QUESTIONS.find((q) => q.id === selectedQuestionId);

  if (activeQuestion) {
    return (
      <QuestionWorkspace
        question={activeQuestion}
        onBackToList={() => navigateTo('/')}
      />
    );
  }

  return (
    <QuestionList
      questions={STATIC_QUESTIONS}
      onSelectQuestion={(id) => navigateTo(`/questions/${id}`)}
    />
  );
};

export default App;
