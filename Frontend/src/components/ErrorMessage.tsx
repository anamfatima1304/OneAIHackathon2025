import { AlertCircle, X } from 'lucide-react';

interface ErrorMessageProps {
  message: string;
  onDismiss?: () => void;
}

export default function ErrorMessage({ message, onDismiss }: ErrorMessageProps) {
  return (
    <div className="error-message">
      <div className="error-content">
        <AlertCircle size={24} />
        <div className="error-text">
          <strong>Error</strong>
          <p>{message}</p>
        </div>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="error-dismiss">
          <X size={20} />
        </button>
      )}
    </div>
  );
}
