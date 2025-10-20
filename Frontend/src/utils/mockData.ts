import { addDays, format } from 'date-fns';
import type { DemandForecast, InventoryRecommendation, CostBreakdown } from '../types/inventory';

export function generateMockForecast(days: number = 90): DemandForecast[] {
  const forecast: DemandForecast[] = [];
  const today = new Date();

  for (let i = 0; i < days; i++) {
    const date = addDays(today, i);
    const baseValue = 1000 + Math.sin(i / 7) * 200 + Math.random() * 100;
    const uncertainty = 150 + Math.random() * 50;

    forecast.push({
      date: format(date, 'yyyy-MM-dd'),
      predicted: Math.round(baseValue),
      upperBound: Math.round(baseValue + uncertainty),
      lowerBound: Math.round(Math.max(0, baseValue - uncertainty)),
    });
  }

  return forecast;
}

export function generateMockRecommendations(): InventoryRecommendation[] {
  const recommendations: InventoryRecommendation[] = [];
  const today = new Date();
  const risks: ('low' | 'medium' | 'high')[] = ['low', 'low', 'medium', 'low', 'high', 'medium', 'low', 'low', 'medium', 'low', 'high', 'low'];

  for (let i = 0; i < 12; i++) {
    const reorderDate = addDays(today, i * 7 + 3);
    recommendations.push({
      week: i + 1,
      recommendedLevel: 5000 + Math.floor(Math.random() * 2000),
      reorderDate: format(reorderDate, 'yyyy-MM-dd'),
      safetyStock: 800 + Math.floor(Math.random() * 400),
      risk: risks[i],
    });
  }

  return recommendations;
}

export function generateMockCostBreakdown(): CostBreakdown {
  return {
    orderingCost: 12500,
    holdingCost: 8300,
    stockoutCost: 4200,
  };
}
