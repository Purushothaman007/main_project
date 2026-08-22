import React from 'react';
import { SupportedLanguage } from '../types/execution';
import { Play, RotateCcw, Code2, Loader2 } from 'lucide-react';

interface HeaderProps {
  language: SupportedLanguage;
  onLanguageChange: (lang: SupportedLanguage) => void;
  onRun: () => void;
  onClear: () => void;
  isRunning: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  language,
  onLanguageChange,
  onRun,
  onClear,
  isRunning,
}) => {
  return (
    <header className="glass-panel header-bar">
      <div className="brand-title">
        <Code2 size={24} color="#6366f1" />
        <span>College Code IDE</span>
      </div>

      <div className="controls-group">
        <select
          id="language-select"
          className="select-dropdown"
          value={language}
          onChange={(e) => onLanguageChange(e.target.value as SupportedLanguage)}
          disabled={isRunning}
        >
          <option value="python">Python 3.11</option>
          <option value="java">Java 17</option>
          <option value="cpp">C++ (GCC)</option>
        </select>

        <button
          id="run-btn"
          className="btn btn-primary"
          onClick={onRun}
          disabled={isRunning}
        >
          {isRunning ? (
            <>
              <Loader2 size={16} className="spinner" />
              <span>Running…</span>
            </>
          ) : (
            <>
              <Play size={16} />
              <span>Run</span>
            </>
          )}
        </button>

        <button
          id="clear-btn"
          className="btn btn-secondary"
          onClick={onClear}
          disabled={isRunning}
        >
          <RotateCcw size={16} />
          <span>Clear</span>
        </button>
      </div>
    </header>
  );
};
