import { useState } from 'react';
import { format, addDays } from 'date-fns';
import { Play, Settings as SettingsIcon } from 'lucide-react';
import type { ForecastModel } from '../types/inventory';

interface SimulationControlsProps {
  onRunForecast: (startDate: string, endDate: string, model: string) => void;
  onOptimize: () => void;
  isLoading: boolean;
}

const FORECAST_MODELS: ForecastModel[] = [
  { id: 'arima', name: 'ARIMA' },
  { id: 'prophet', name: 'Prophet' },
  { id: 'lstm', name: 'LSTM' },
  { id: 'ensemble', name: 'Ensemble' },
];

export default function SimulationControls({ onRunForecast, onOptimize, isLoading }: SimulationControlsProps) {
  const today = new Date();
  const defaultEndDate = addDays(today, 90);

  const [startDate, setStartDate] = useState(format(today, 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(defaultEndDate, 'yyyy-MM-dd'));
  const [selectedModel, setSelectedModel] = useState('arima');

  const handleRunForecast = () => {
    onRunForecast(startDate, endDate, selectedModel);
  };

  return (
    <div className="card simulation-controls">
      <div className="card-header">
        <h2>Simulation Controls</h2>
        <p className="card-subtitle">Configure and run forecasting models</p>
      </div>
      <div className="card-body">
        <div className="controls-grid">
          <div className="control-group">
            <label htmlFor="start-date">Start Date</label>
            <input
              id="start-date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="date-input"
            />
          </div>

          <div className="control-group">
            <label htmlFor="end-date">End Date</label>
            <input
              id="end-date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="date-input"
            />
          </div>

          <div className="control-group full-width">
            <label htmlFor="model-select">Forecasting Model</label>
            <select
              id="model-select"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="model-select"
            >
              {FORECAST_MODELS.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="button-group">
          <button
            onClick={handleRunForecast}
            disabled={isLoading}
            className="btn btn-primary"
          >
            <Play size={18} />
            <span>{isLoading ? 'Running...' : 'Run Forecast'}</span>
          </button>
          <button
            onClick={onOptimize}
            disabled={isLoading}
            className="btn btn-secondary"
          >
            <SettingsIcon size={18} />
            <span>{isLoading ? 'Optimizing...' : 'Optimize Inventory'}</span>
          </button>
        </div>

        <div className="date-range-info">
          <p>
            Forecast period: <strong>{Math.ceil((new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24))}</strong> days
          </p>
        </div>
      </div>
    </div>
  );
}
