import { Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { format } from 'date-fns';
import type { DemandForecast as DemandForecastType } from '../types/inventory';

interface DemandForecastProps {
  data: DemandForecastType[];
}

export default function DemandForecast({ data }: DemandForecastProps) {
  const chartData = data.map(item => ({
    date: format(new Date(item.date), 'MMM dd'),
    fullDate: item.date,
    predicted: item.predicted,
    upperBound: item.upperBound,
    lowerBound: item.lowerBound,
    uncertainty: [item.lowerBound, item.upperBound],
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="tooltip-date">{format(new Date(data.fullDate), 'MMM dd, yyyy')}</p>
          <p className="tooltip-value">Predicted: <strong>{data.predicted.toFixed(0)}</strong> units</p>
          <p className="tooltip-range">
            Range: {data.lowerBound.toFixed(0)} - {data.upperBound.toFixed(0)} units
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Demand Forecast - Component X</h2>
        <p className="card-subtitle">90-day prediction with confidence intervals</p>
      </div>
      <div className="card-body">
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="uncertaintyGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
            />
            <YAxis
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
              label={{ value: 'Units', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area
              type="monotone"
              dataKey="upperBound"
              stroke="none"
              fill="url(#uncertaintyGradient)"
              name="Confidence Interval"
            />
            <Area
              type="monotone"
              dataKey="lowerBound"
              stroke="none"
              fill="#ffffff"
            />
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={false}
              name="Predicted Demand"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
