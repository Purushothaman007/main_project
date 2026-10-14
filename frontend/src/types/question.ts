export type Difficulty = 'Easy' | 'Medium' | 'Hard';

export interface Example {
  input: string;
  output: string;
  explanation?: string;
}

export interface Question {
  id: string;
  title: string;
  difficulty: Difficulty;
  tags: string[];
  description: string;
  examples: Example[];
  constraints: string[];
  /** Flat text version sent to the AI as context */
  aiContext: string;
}
