import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { DemandForecast } from '../types/inventory';

interface ForecastChartProps {
  forecastData: DemandForecast[];
}

export default function ForecastChart({ forecastData }: ForecastChartProps) {
  if (!forecastData || forecastData.length === 0) {
    return <p className="text-gray-500 text-center">No forecast data available.</p>;
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Demand Forecast</h2>
        <p className="card-subtitle">Predicted demand over time</p>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={forecastData} margin={{ top: 20, right: 30, left: 20, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="predicted_demand" stroke="#3b82f6" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
