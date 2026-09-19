import { SupportedLanguage } from './execution';

export interface QuestionExample {
  input: string;
  output: string;
  explanation?: string;
}

export interface Question {
  id: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  topic: string;
  shortDescription: string;
  description: string;
  inputFormat: string;
  outputFormat: string;
  examples: QuestionExample[];
  constraints: string[];
  starterCode: Record<SupportedLanguage, string>;
}
