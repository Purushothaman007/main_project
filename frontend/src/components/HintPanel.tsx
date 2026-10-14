import React, { useState, useRef, useEffect } from 'react';
import { ConversationMessage, HintLevel, HintProvider, HintResponse } from '../types/hint';
import { getHintApi } from '../api/client';

interface HintPanelProps {
  language: string;
  sourceCode: string;
  errorOutput?: string;
  problemStatement?: string;
}

interface ChatEntry {
  role: 'user' | 'assistant';
  content: string;
  hintLevel?: HintLevel;
  hintType?: string;
  isError?: boolean;
}

const LEVEL_LABELS: Record<HintLevel, string> = {
  1: 'Conceptual',
  2: 'Algorithmic',
  3: 'Targeted',
};

const LEVEL_COLORS: Record<HintLevel, string> = {
  1: 'hint-level-conceptual',
  2: 'hint-level-algorithmic',
  3: 'hint-level-targeted',
};

export const HintPanel: React.FC<HintPanelProps> = ({
  language,
  sourceCode,
  errorOutput,
  problemStatement,
}) => {
  const [messages, setMessages] = useState<ChatEntry[]>([]);
  const [inputText, setInputText] = useState('');
  const [hintProvider, setHintProvider] = useState<HintProvider>('gemini');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const buildHistory = (): ConversationMessage[] =>
    messages.map((m) => ({ role: m.role, content: m.content }));

  const sendMessage = async () => {
    const text = inputText.trim();
    if (!text || isLoading) return;

    const userEntry: ChatEntry = { role: 'user', content: text };
    setMessages((prev) => [...prev, userEntry]);
    setInputText('');
    setIsLoading(true);

    try {
      const res: HintResponse = await getHintApi({
        provider: hintProvider,
        language,
        source_code: sourceCode,
        hint_level: 1,
        student_message: text,
        error_output: errorOutput ?? '',
        conversation_history: buildHistory(),
        problem_statement: problemStatement ?? '',
      });

      const assistantEntry: ChatEntry = {
        role: 'assistant',
        content: res.message,
        hintLevel: res.hint_level as HintLevel,
        hintType: res.hint_type,
      };
      setMessages((prev) => [...prev, assistantEntry]);

    } catch (err: any) {
      const errorEntry: ChatEntry = {
        role: 'assistant',
        content: err.message || 'An unexpected error occurred.',
        isError: true,
      };
      setMessages((prev) => [...prev, errorEntry]);
    } finally {
      setIsLoading(false);
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setInputText('');
  };

  return (
    <div className="hint-panel glass-panel">
      {/* Panel Header */}
      <div className="panel-header hint-panel-header">
        <div className="hint-title">
          <span className="hint-icon">✨</span>
          <span>AI Hint Assistant</span>
          <span className="hint-badge">{hintProvider === 'gemini' ? 'Gemini' : 'Groq'}</span>
        </div>
        {messages.length > 0 && (
          <button className="btn-ghost hint-clear-btn" onClick={clearChat} title="Clear conversation">
            ↺ Clear
          </button>
        )}
      </div>

      {/* Model Selector */}
      <div className="hint-level-bar">
        <label className="hint-model-selector" htmlFor="hint-model-select">
          <span>Model</span>
          <select
            id="hint-model-select"
            className="hint-model-select"
            value={hintProvider}
            onChange={(event) => setHintProvider(event.target.value as HintProvider)}
            disabled={isLoading}
          >
            <option value="gemini">Gemini · 3.8 Flash</option>
            <option value="groq">Groq · Llama 3.3 70B</option>
          </select>
        </label>
      </div>

      {/* Active problem banner */}
      {problemStatement ? (
        <div className="hint-problem-banner">
          <span className="hint-problem-icon">📋</span>
          <span className="hint-problem-label">Context loaded — AI knows your problem</span>
        </div>
      ) : (
        <div className="hint-problem-banner hint-problem-banner-empty">
          <span className="hint-problem-icon">⚠️</span>
          <span className="hint-problem-label">No problem selected — open the Problem panel to load one</span>
        </div>
      )}

      {/* Chat Messages */}
      <div className="hint-chat-body">
        {messages.length === 0 && !isLoading && (
          <div className="hint-empty-state">
            <div className="hint-empty-icon">🤖</div>
            <p className="hint-empty-title">Ask your AI tutor</p>
            <p className="hint-empty-sub">
              Type a question about your code and get a progressive hint.
              <br />
              Ask about the problem or your code to get a focused hint.
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`hint-message hint-message-${msg.role} ${msg.isError ? 'hint-message-error' : ''}`}
          >
            {msg.role === 'assistant' && (
              <div className="hint-message-meta">
                <span className="hint-bot-icon">✨</span>
                {msg.hintType && (
                  <span className={`hint-type-badge ${LEVEL_COLORS[msg.hintLevel ?? 1]}`}>
                    {LEVEL_LABELS[msg.hintLevel ?? 1]} hint
                  </span>
                )}
                {msg.isError && <span className="hint-error-badge">Error</span>}
              </div>
            )}
            <div className="hint-message-bubble">
              <pre className="hint-message-text">{msg.content}</pre>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="hint-message hint-message-assistant">
            <div className="hint-message-meta">
              <span className="hint-bot-icon">✨</span>
            </div>
            <div className="hint-message-bubble hint-typing-bubble">
              <span className="hint-dot" />
              <span className="hint-dot" />
              <span className="hint-dot" />
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="hint-input-area">
        <textarea
          ref={textareaRef}
          className="hint-textarea"
          placeholder="Ask a question about your code… (Enter to send)"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          rows={2}
          id="hint-input"
        />
        <button
          className={`btn btn-hint-send ${isLoading ? 'loading' : ''}`}
          onClick={sendMessage}
          disabled={isLoading || !inputText.trim()}
          id="hint-send-btn"
          title="Send (Enter)"
        >
          {isLoading ? (
            <span className="spinner">⟳</span>
          ) : (
            '→'
          )}
        </button>
      </div>
    </div>
  );
};
