import React from 'react';
import { ExecutionResponse } from '../types/execution';
import { Terminal, CheckCircle2, AlertTriangle, XCircle, Clock, Hash, Cpu } from 'lucide-react';

interface OutputPanelProps {
  result: ExecutionResponse | null;
  isRunning: boolean;
}

export const OutputPanel: React.FC<OutputPanelProps> = ({ result, isRunning }) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="status-badge status-completed">
            <CheckCircle2 size={14} /> COMPLETED
          </span>
        );
      case 'TIME_LIMIT_EXCEEDED':
      case 'MEMORY_LIMIT_EXCEEDED':
      case 'OUTPUT_LIMIT_EXCEEDED':
        return (
          <span className="status-badge status-warning">
            <AlertTriangle size={14} /> {status}
          </span>
        );
      default:
        return (
          <span className="status-badge status-error">
            <XCircle size={14} /> {status}
          </span>
        );
    }
  };

  return (
    <div className="glass-panel output-container">
      <div className="panel-header">
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Terminal size={16} /> Execution Result
        </span>

        {result && (
          <div className="output-meta">
            {getStatusBadge(result.status)}
            <span className="meta-item" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={14} /> {result.execution_time_ms} ms
            </span>
            <span className="meta-item" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Hash size={14} /> Exit {result.exit_code}
            </span>
          </div>
        )}
      </div>

      <div className="output-body">
        {isRunning ? (
          <div className="empty-state">
            <Cpu size={36} color="#6366f1" className="spinner" />
            <p>Executing program inside isolated container...</p>
          </div>
        ) : result ? (
          <>
            {result.stdout && (
              <div>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '6px', fontWeight: 600 }}>
                  STDOUT:
                </div>
                <pre className="stdout-block">{result.stdout}</pre>
              </div>
            )}

            {result.stderr && (
              <div>
                <div style={{ fontSize: '0.75rem', color: '#f87171', marginBottom: '6px', fontWeight: 600 }}>
                  STDERR:
                </div>
                <pre className="stderr-block">{result.stderr}</pre>
              </div>
            )}

            {!result.stdout && !result.stderr && (
              <div className="empty-state">
                <p>Program executed with no output.</p>
              </div>
            )}
          </>
        ) : (
          <div className="empty-state">
            <Terminal size={36} opacity={0.4} />
            <p>Click <strong>Run</strong> to execute code in a fresh Docker container.</p>
          </div>
        )}
      </div>
    </div>
  );
};
