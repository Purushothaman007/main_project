import React, { useState } from 'react';
import { Question } from '../../types/question';
import { SupportedLanguage, ExecutionResponse } from '../../types/execution';
import { Header } from '../Header';
import { CodeEditor } from '../CodeEditor';
import { StdinPanel } from '../StdinPanel';
import { OutputPanel } from '../OutputPanel';
import { AIAssistant } from '../AIAssistant/AIAssistant';
import { executeCodeApi } from '../../api/client';
import { ArrowLeft, BookOpen } from 'lucide-react';


interface QuestionWorkspaceProps {
  question: Question;
  onBackToList: () => void;
}

export const QuestionWorkspace: React.FC<QuestionWorkspaceProps> = ({
  question,
  onBackToList,
}) => {
  const [language, setLanguage] = useState<SupportedLanguage>('python');
  const [code, setCode] = useState<string>(question.starterCode.python);
  const [stdin, setStdin] = useState<string>('');
  const [result, setResult] = useState<ExecutionResponse | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  const handleLanguageChange = (newLang: SupportedLanguage) => {
    setLanguage(newLang);
    setCode(question.starterCode[newLang] || '');
    setResult(null);
  };

  const handleClear = () => {
    setCode(question.starterCode[language] || '');
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

  const getExecutionOutputText = (): string => {
    if (!result) return '';
    let out = `Status: ${result.status}\nExit Code: ${result.exit_code}\n`;
    if (result.stdout) out += `STDOUT:\n${result.stdout}\n`;
    if (result.stderr) out += `STDERR:\n${result.stderr}\n`;
    return out;
  };

  return (
    <div className="workspace-container">
      {/* Workspace Top Header */}
      <div className="workspace-header glass-panel">
        <button className="btn btn-secondary back-btn" onClick={onBackToList}>
          <ArrowLeft size={16} /> All Questions
        </button>

        <div className="workspace-title-area">
          <span className="workspace-question-title">{question.title}</span>
          <span className="difficulty-badge badge-easy">{question.difficulty}</span>
        </div>

        <Header
          language={language}
          onLanguageChange={handleLanguageChange}
          onRun={handleRun}
          onClear={handleClear}
          isRunning={isRunning}
        />
      </div>

      {/* Main 3-Column Workspace */}
      <div className="workspace-layout">
        {/* Left Column — Problem Statement */}
        <div className="glass-panel problem-panel">
          <div className="panel-header">
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <BookOpen size={16} /> Problem Description
            </span>
          </div>

          <div className="problem-body">
            <h2 className="problem-title">{question.title}</h2>
            <div className="problem-meta-tags">
              <span className="meta-tag">{question.topic}</span>
            </div>

            <section className="problem-section">
              <p className="description-text">{question.description}</p>
            </section>

            <section className="problem-section">
              <h3 className="section-subtitle">Input Format</h3>
              <div className="code-inline">{question.inputFormat}</div>
            </section>

            <section className="problem-section">
              <h3 className="section-subtitle">Expected Output</h3>
              <div className="code-inline">{question.outputFormat}</div>
            </section>

            <section className="problem-section">
              <h3 className="section-subtitle">Examples</h3>
              {question.examples.map((ex, i) => (
                <div key={i} className="example-box">
                  <div className="example-label">Example {i + 1}:</div>
                  <div className="example-row">
                    <strong>Input:</strong> <code>{ex.input}</code>
                  </div>
                  <div className="example-row">
                    <strong>Output:</strong> <code>{ex.output}</code>
                  </div>
                  {ex.explanation && (
                    <div className="example-row explanation">
                      <strong>Explanation:</strong> {ex.explanation}
                    </div>
                  )}
                </div>
              ))}
            </section>

            <section className="problem-section">
              <h3 className="section-subtitle">Constraints</h3>
              <ul className="constraints-list">
                {question.constraints.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </section>
          </div>
        </div>

        {/* Middle Column — Monaco Editor & Stdin/Output */}
        <div className="editor-output-column">
          <CodeEditor language={language} code={code} onChange={setCode} />
          <StdinPanel stdin={stdin} onChange={setStdin} disabled={isRunning} />
          <OutputPanel result={result} isRunning={isRunning} />
        </div>

        {/* Right Column — AI Assistant */}
        <div className="ai-column">
          <AIAssistant
            questionId={question.id}
            language={language}
            code={code}
            executionOutput={getExecutionOutputText()}
          />
        </div>
      </div>
    </div>
  );
};
