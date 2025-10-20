import { format } from 'date-fns';
import { AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react';
import type { InventoryRecommendation } from '../types/inventory';

interface InventoryRecommendationsProps {
  recommendations: InventoryRecommendation[];
}

export default function InventoryRecommendations({ recommendations }: InventoryRecommendationsProps) {
  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'high':
        return <AlertTriangle size={18} className="risk-icon high" />;
      case 'medium':
        return <AlertCircle size={18} className="risk-icon medium" />;
      default:
        return <CheckCircle size={18} className="risk-icon low" />;
    }
  };

  const getRiskLabel = (risk: string) => {
    switch (risk) {
      case 'high':
        return 'High Risk';
      case 'medium':
        return 'Medium Risk';
      default:
        return 'Low Risk';
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Inventory Recommendations</h2>
        <p className="card-subtitle">Weekly inventory levels and reorder points</p>
      </div>
      <div className="card-body">
        <div className="table-container">
          <table className="recommendations-table">
            <thead>
              <tr>
                <th>Week</th>
                <th>Recommended Level</th>
                <th>Safety Stock</th>
                <th>Reorder Date</th>
                <th>Risk Status</th>
              </tr>
            </thead>
            <tbody>
              {recommendations.map((rec) => (
                <tr key={rec.week} className={`risk-${rec.risk}`}>
                  <td className="week-cell">Week {rec.week}</td>
                  <td className="value-cell">{rec.recommendedLevel} units</td>
                  <td className="value-cell">{rec.safetyStock} units</td>
                  <td className="date-cell">
                    {format(new Date(rec.reorderDate), 'MMM dd, yyyy')}
                  </td>
                  <td className="risk-cell">
                    <div className="risk-badge">
                      {getRiskIcon(rec.risk)}
                      <span>{getRiskLabel(rec.risk)}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
