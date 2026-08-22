import React from 'react';
import { Terminal } from 'lucide-react';

interface StdinPanelProps {
  stdin: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export const StdinPanel: React.FC<StdinPanelProps> = ({
  stdin,
  onChange,
  disabled = false,
}) => {
  return (
    <div className="glass-panel stdin-container">
      <div className="panel-header">
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Terminal size={16} /> Input (stdin)
        </span>
      </div>
      <textarea
        id="stdin-input"
        className="stdin-textarea"
        placeholder="Enter standard input here..."
        value={stdin}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      />
    </div>
  );
};
