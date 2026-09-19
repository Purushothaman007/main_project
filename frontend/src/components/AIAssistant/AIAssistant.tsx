import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, Sparkles, HelpCircle, Bug, BookOpen, Clock, Loader2 } from 'lucide-react';

import { ChatMessage, AIChatRequest } from '../../types/ai';
import { sendAIChatApi } from '../../api/client';

interface AIAssistantProps {
  questionId: string;
  language: string;
  code: string;
  executionOutput?: string;
}

export const AIAssistant: React.FC<AIAssistantProps> = ({
  questionId,
  language,
  code,
  executionOutput = '',
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (messageText?: string) => {
    const textToSend = (messageText || inputMessage).trim();
    if (!textToSend || isLoading) return;

    const userMsg: ChatMessage = { role: 'user', content: textToSend };
    const updatedHistory = [...messages, userMsg];
    setMessages(updatedHistory);
    if (!messageText) setInputMessage('');
    setIsLoading(true);

    const payload: AIChatRequest = {
      question_id: questionId,
      message: textToSend,
      language: language,
      code: code,
      execution_output: executionOutput,
      history: messages,
    };

    const result = await sendAIChatApi(payload);

    const assistantMsg: ChatMessage = {
      role: 'assistant',
      content: result.response,
    };

    setMessages((prev) => [...prev, assistantMsg]);
    setIsLoading(false);
  };

  const handleQuickAction = (actionPrompt: string) => {
    handleSend(actionPrompt);
  };

  return (
    <div className="glass-panel ai-panel">
      {/* Panel Header */}
      <div className="panel-header ai-header">
        <span className="ai-title">
          <Bot className="ai-icon" size={18} /> AI Educational Tutor
        </span>
        <span className="ai-badge">Gemini 3.6 Flash</span>
      </div>

      {/* Main Chat Body */}
      <div className="ai-chat-body">
        {/* Tutor Greeting & Quick Actions */}
        <div className="ai-greeting-card">
          <div className="greeting-header">
            <Sparkles size={16} className="sparkle-icon" />
            <span>Hi! I can help you understand the problem without giving you the complete solution.</span>
          </div>

          <div className="quick-actions-grid">
            <button
              className="quick-btn"
              onClick={() => handleQuickAction('Can you give me a conceptual hint to help me get started?')}
              disabled={isLoading}
            >
              <HelpCircle size={14} /> Give me a Hint
            </button>
            <button
              className="quick-btn"
              onClick={() =>
                handleQuickAction(
                  'Please look at my code and current execution output. Identify any conceptual or runtime mistakes without rewriting the full solution.'
                )
              }
              disabled={isLoading}
            >
              <Bug size={14} /> Debug My Code
            </button>
            <button
              className="quick-btn"
              onClick={() => handleQuickAction('Can you explain the core programming concept required for this problem?')}
              disabled={isLoading}
            >
              <BookOpen size={14} /> Explain Concept
            </button>
            <button
              className="quick-btn"
              onClick={() => handleQuickAction('What is the target Time and Space complexity for an optimal solution?')}
              disabled={isLoading}
            >
              <Clock size={14} /> Time / Space Complexity
            </button>
          </div>
        </div>

        {/* Message Stream */}
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-bubble-wrapper ${msg.role === 'user' ? 'user-wrapper' : 'assistant-wrapper'}`}
          >
            <div className={`chat-bubble ${msg.role === 'user' ? 'user-bubble' : 'assistant-bubble'}`}>
              {msg.role === 'assistant' && (
                <div className="assistant-role-label">
                  <Bot size={14} /> AI Tutor
                </div>
              )}
              <div className="chat-text">{msg.content}</div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="chat-bubble-wrapper assistant-wrapper">
            <div className="chat-bubble assistant-bubble loading-bubble">
              <Loader2 className="spinner" size={16} /> Thinking & analyzing code...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="ai-input-wrapper">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="ai-input-form"
        >
          <input
            type="text"
            className="ai-input"
            placeholder="Ask a question..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" className="btn btn-primary ai-send-btn" disabled={isLoading || !inputMessage.trim()}>
            <Send size={15} />
          </button>
        </form>
      </div>
    </div>
  );
};
