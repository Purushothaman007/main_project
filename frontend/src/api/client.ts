import axios from 'axios';
import { ExecutionRequest, ExecutionResponse } from '../types/execution';
import { HintRequest, HintResponse } from '../types/hint';

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds HTTP timeout to accommodate compilation + execution
});

export const executeCodeApi = async (req: ExecutionRequest): Promise<ExecutionResponse> => {
  try {
    const response = await api.post<ExecutionResponse>('/api/v1/execute', req);
    return response.data;
  } catch (error: any) {
    let errorMessage = 'Network error or server unreachable.';
    if (error.response && error.response.data && error.response.data.stderr) {
      errorMessage = error.response.data.stderr;
    } else if (error.message) {
      errorMessage = error.message;
    }

    return {
      success: false,
      language: req.language,
      stdout: '',
      stderr: errorMessage,
      exit_code: -1,
      execution_time_ms: 0,
      status: 'SYSTEM_ERROR',
      execution_id: 'exec_net_error',
    };
  }
};

/**
 * Request a progressive hint from the Gemini-powered hint assistant.
 * Throws an error string on failure so the UI can display it directly.
 */
export const getHintApi = async (req: HintRequest): Promise<HintResponse> => {
  try {
    const response = await api.post<HintResponse>('/api/ai/hints', req);
    return response.data;
  } catch (error: any) {
    let msg = 'Could not reach the hint service.';
    if (error.response?.data?.detail) {
      msg = error.response.data.detail;
    } else if (error.message) {
      msg = error.message;
    }
    throw new Error(msg);
  }
};
