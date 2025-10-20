import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import type { CostBreakdown as CostBreakdownType } from '../types/inventory';

interface CostBreakdownProps {
  costs: CostBreakdownType;
  chartType?: 'pie' | 'bar';
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b'];

export default function CostBreakdown({ costs, chartType = 'pie' }: CostBreakdownProps) {
  const chartData = [
    { name: 'Ordering Cost', value: costs.orderingCost, color: COLORS[0] },
    { name: 'Holding Cost', value: costs.holdingCost, color: COLORS[1] },
    { name: 'Stockout Cost', value: costs.stockoutCost, color: COLORS[2] },
  ];

  const totalCost = costs.orderingCost + costs.holdingCost + costs.stockoutCost;

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const percentage = ((data.value / totalCost) * 100).toFixed(1);
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{data.name}</p>
          <p className="tooltip-value">
            <strong>${data.value.toLocaleString()}</strong>
          </p>
          <p className="tooltip-percent">{percentage}% of total</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Cost Breakdown Summary</h2>
        <p className="card-subtitle">Total: ${totalCost.toLocaleString()}</p>
      </div>
      <div className="card-body">
        <div className="cost-summary">
          {chartData.map((item) => (
            <div key={item.name} className="cost-item">
              <div className="cost-label">
                <div className="color-dot" style={{ backgroundColor: item.color }} />
                <span>{item.name}</span>
              </div>
              <div className="cost-value">${item.value.toLocaleString()}</div>
            </div>
          ))}
        </div>

        <div className="chart-container">
          {chartType === 'pie' ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry: any) => `${((entry.value / totalCost) * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" stroke="#6b7280" tick={{ fontSize: 12 }} />
                <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="chart-toggle">
          <button className="toggle-btn">
            Switch to {chartType === 'pie' ? 'Bar' : 'Pie'} Chart
          </button>
        </div>
      </div>
    </div>
  );
}
