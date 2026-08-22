import React from 'react';
import Editor from '@monaco-editor/react';
import { SupportedLanguage } from '../types/execution';
import { FileCode } from 'lucide-react';

interface CodeEditorProps {
  language: SupportedLanguage;
  code: string;
  onChange: (value: string) => void;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  language,
  code,
  onChange,
}) => {
  const getMonacoLanguage = (lang: SupportedLanguage): string => {
    switch (lang) {
      case 'python':
        return 'python';
      case 'java':
        return 'java';
      case 'cpp':
        return 'cpp';
      default:
        return 'plaintext';
    }
  };

  return (
    <div className="glass-panel editor-wrapper">
      <div className="panel-header">
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <FileCode size={16} /> Source Code ({language.toUpperCase()})
        </span>
      </div>
      <div className="monaco-container">
        <Editor
          height="100%"
          language={getMonacoLanguage(language)}
          theme="vs-dark"
          value={code}
          onChange={(val) => onChange(val || '')}
          options={{
            fontSize: 14,
            fontFamily: "'Fira Code', monospace",
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            padding: { top: 12 },
          }}
        />
      </div>
    </div>
  );
};
