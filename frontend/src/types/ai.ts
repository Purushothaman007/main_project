export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface AIChatRequest {
  question_id: string;
  message: string;
  language: string;
  code?: string;
  execution_output?: string;
  history?: ChatMessage[];
}

export interface AIChatResponse {
  response: string;
  is_refusal: boolean;
  action_type?: string;
}
