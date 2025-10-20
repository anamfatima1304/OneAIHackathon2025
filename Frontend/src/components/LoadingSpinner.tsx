import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
}

export default function LoadingSpinner({ message = 'Loading...' }: LoadingSpinnerProps) {
  return (
    <div className="loading-spinner">
      <Loader2 size={48} className="spinner-icon" />
      <p>{message}</p>
    </div>
  );
}
