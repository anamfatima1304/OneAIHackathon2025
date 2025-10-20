import { useState } from 'react';
import { format, addDays } from 'date-fns';
import { Play, Settings as SettingsIcon } from 'lucide-react';
import { fetchForecast, optimizeInventory } from '../services/api';
import ForecastChart from './ForecastChart';

import type {
  ForecastModel,
  OptimizationRequest,
  DemandForecast,
  InventoryRecommendation,
  CostBreakdown,
} from '../types/inventory';
import type { ForecastResponse, OptimizationResponse } from '../services/api';

interface SimulationControlsProps {
  onRunForecast: (startDate: string, endDate: string, model: string) => Promise<void> | void;
  onOptimize: () => Promise<void> | void;
  isLoading: boolean;
}

const FORECAST_MODELS: ForecastModel[] = [
  { id: 'arima', name: 'ARIMA' },
  { id: 'prophet', name: 'Prophet' },
  { id: 'lstm', name: 'LSTM' },
  { id: 'ensemble', name: 'Ensemble' },
];

export default function SimulationControls({
  onRunForecast,
  onOptimize,
  isLoading,
}: SimulationControlsProps) {
  const today = new Date();
  const defaultEndDate = addDays(today, 90);

  const [startDate, setStartDate] = useState(format(today, 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(defaultEndDate, 'yyyy-MM-dd'));
  const [selectedModel, setSelectedModel] = useState('arima');
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
  const [optimizationData, setOptimizationData] = useState<OptimizationResponse | null>(null);

  const handleRunForecast = async () => {
    try {
      console.log('Running forecast with model:', selectedModel);
      const data = await fetchForecast();
      setForecastData(data);
      console.log('Forecast result:', data);
      // Trigger parent callback too if needed
      onRunForecast(startDate, endDate, selectedModel);
    } catch (err) {
      console.error('Forecast error:', err);
      alert('Error fetching forecast data');
    }
  };

  const handleOptimize = async () => {
    try {
      const request: OptimizationRequest = {
        startDate,
        endDate,
        model: selectedModel,
        // remove constraints if not defined in type
      };
      const data = await optimizeInventory(request);
      setOptimizationData(data);
      console.log('Optimization result:', data);
      onOptimize();
    } catch (err) {
      console.error('Optimization error:', err);
      alert('Error optimizing inventory');
    }
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
          <button onClick={handleRunForecast} disabled={isLoading} className="btn btn-primary">
            <Play size={18} />
            <span>{isLoading ? 'Running...' : 'Predict'}</span>
          </button>

          <button onClick={handleOptimize} disabled={isLoading} className="btn btn-secondary">
            <SettingsIcon size={18} />
            <span>{isLoading ? 'Optimizing...' : 'Optimize Inventory'}</span>
          </button>
        </div>

        <div className="date-range-info">
          <p>
            Forecast period:{' '}
            <strong>
              {Math.ceil(
                (new Date(endDate).getTime() - new Date(startDate).getTime()) /
                  (1000 * 60 * 60 * 24)
              )}
            </strong>{' '}
            days
          </p>
        </div>

        {/* Optional: show backend response */}
        {forecastData && <ForecastChart forecastData={forecastData.forecast} />}
        {optimizationData && <pre>{JSON.stringify(optimizationData, null, 2)}</pre>}
      </div>
    </div>
  );
  
}
