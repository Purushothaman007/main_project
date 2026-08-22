import axios from 'axios';
import { ExecutionRequest, ExecutionResponse } from '../types/execution';

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
