export type SupportedLanguage = 'python' | 'java' | 'cpp';

export type ExecutionStatus =
  | 'COMPLETED'
  | 'COMPILATION_ERROR'
  | 'RUNTIME_ERROR'
  | 'TIME_LIMIT_EXCEEDED'
  | 'MEMORY_LIMIT_EXCEEDED'
  | 'OUTPUT_LIMIT_EXCEEDED'
  | 'SYSTEM_ERROR';

export interface ExecutionRequest {
  language: SupportedLanguage;
  code: string;
  stdin?: string;
}

export interface ExecutionResponse {
  success: boolean;
  language: string;
  stdout: string;
  stderr: string;
  exit_code: number;
  execution_time_ms: number;
  status: ExecutionStatus;
  execution_id: string;
}
