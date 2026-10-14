import React, { useState } from 'react';
import { SupportedLanguage, ExecutionResponse } from './types/execution';
import { Question } from './types/question';
import { DEFAULT_SNIPPETS } from './utils/defaultSnippets';
import { Header } from './components/Header';
import { CodeEditor } from './components/CodeEditor';
import { StdinPanel } from './components/StdinPanel';
import { OutputPanel } from './components/OutputPanel';
import { HintPanel } from './components/HintPanel';
import { QuestionSidebar } from './components/QuestionSidebar';
import { executeCodeApi } from './api/client';

export const App: React.FC = () => {
  const [language, setLanguage] = useState<SupportedLanguage>('python');
  const [code, setCode] = useState<string>(DEFAULT_SNIPPETS.python);
  const [stdin, setStdin] = useState<string>('');
  const [result, setResult] = useState<ExecutionResponse | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [activeQuestion, setActiveQuestion] = useState<Question | null>(null);

  const handleLanguageChange = (newLang: SupportedLanguage) => {
    setLanguage(newLang);
    setCode(DEFAULT_SNIPPETS[newLang]);
    setResult(null);
  };

  const handleClear = () => {
    setCode(DEFAULT_SNIPPETS[language]);
    setStdin('');
    setResult(null);
  };

  const handleRun = async () => {
    setIsRunning(true);
    setResult(null);
    try {
      const response = await executeCodeApi({
        language,
        code,
        stdin,
      });
      setResult(response);
    } catch (error) {
      console.error('Execution request error:', error);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="app-container">
      <Header
        language={language}
        onLanguageChange={handleLanguageChange}
        onRun={handleRun}
        onClear={handleClear}
        isRunning={isRunning}
      />

      <div className="workspace">
        {/* Collapsible question sidebar */}
        <QuestionSidebar
          activeQuestion={activeQuestion}
          onSelectQuestion={setActiveQuestion}
        />

        {/* Main split view */}
        <main className="main-content">
          <div className="left-pane">
            <CodeEditor
              language={language}
              code={code}
              onChange={setCode}
            />
            <StdinPanel
              stdin={stdin}
              onChange={setStdin}
              disabled={isRunning}
            />
          </div>

          <div className="right-pane">
            <OutputPanel result={result} isRunning={isRunning} />
            <HintPanel
              language={language}
              sourceCode={code}
              errorOutput={result?.stderr ?? ''}
              problemStatement={activeQuestion?.aiContext ?? ''}
            />
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
