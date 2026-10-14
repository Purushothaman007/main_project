// Hint Assistant types — mirrors backend app/schemas/hint.py

export type HintLevel = 1 | 2 | 3;
export type HintType = 'conceptual' | 'algorithmic' | 'targeted' | 'debugging';
export type HintProvider = 'gemini' | 'groq';

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface HintRequest {
  provider: HintProvider;
  language: string;
  source_code: string;
  hint_level: HintLevel;
  student_message: string;
  error_output?: string;
  conversation_history?: ConversationMessage[];
  problem_statement?: string;
}

export interface HintResponse {
  hint_level: HintLevel;
  hint_type: HintType;
  message: string;
  next_hint_available: boolean;
}
